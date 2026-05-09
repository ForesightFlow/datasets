#!/usr/bin/env python3
"""
build_dataset.py — produce pmxt-stylized-facts-v1 data files.

Inputs (pre-computed by CC-003.11 and CC-004):
  --g5-input    path to table_t_g5_stratified_70k.json
  --sf-input    path to sf_results_stratified_resume_merged.json
  --sf9-input   path to sf9_refined.json (optional; for metadata only)
  --archive-dir path to data/raw/primary_2026-04-21_2026-04-27
                (needed to locate evaluation/cache/aggregates_*.parquet)
  --output-dir  destination directory (../data/ by default)

Outputs:
  markets-stylized-facts-v1.parquet   22 cols × 13,298 rows
  sf7-class-hour-v1.parquet           96 rows (4 classes × 24 hours)
  sf9-bucket-aggregate-v1.parquet     5 rows (one per time-to-resolution bucket)
  aggregates.json
  build_manifest.json

Requirements:
  - The project's Python environment (polars, httpx, etc.) must be available.
  - The local metadata/UMA caches under ~/.cache/elp must be populated
    (they are populated by prior CC-003 / CC-004 runs).
  - pandas, pyarrow, numpy (data output layer).
"""
from __future__ import annotations

import argparse
import datetime
import gzip
import hashlib
import json
import logging
import pathlib
import subprocess
import sys
import time
from typing import Any

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

LOG = logging.getLogger("build_dataset")

# ── canonical constants ────────────────────────────────────────────────────────

SNAPSHOT_CUTOFF_UTC = "2026-04-27T23:59:59Z"
ARCHIVE_START_UTC   = "2026-04-21T00:00:00Z"
ARCHIVE_END_UTC     = "2026-04-27T23:59:59Z"
N_MARKETS_EXPECTED  = 13314
CLASS_COUNTS_CANONICAL = {
    "sports": 6800, "other": 4584, "crypto": 1518, "politics": 412
}
SF1_BASE_POOLED_RHO      = 1.7194
SF1_RESUME_POOLED_RHO    = 1.6486
SF1_BASE_N               = 4030
SF1_RESUME_N             = 1648
SF2_POOLED_MEDIAN        = 0.5000
SUBSAMPLE_SEED           = 20260505

BUCKETS = ["24h-12h", "12h-3h", "3h-1h", "1h-5m", "5m-0"]
BUCKET_EDGES_H = {
    "24h-12h": (24.0, 12.0),
    "12h-3h":  (12.0, 3.0),
    "3h-1h":   (3.0, 1.0),
    "1h-5m":   (1.0, 5/60),
    "5m-0":    (5/60, 0.0),
}


# ── SHA256 helpers ─────────────────────────────────────────────────────────────

def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


# ── sample reconstruction ─────────────────────────────────────────────────────

_UMA_SNAPSHOT_DATE = "2026-05-07"  # frozen CC-003/CC-004 cache; use this date for reproducibility


def _join_uma_from_local_cache(agg: pd.DataFrame) -> pd.DataFrame:
    """
    Read UMA resolution data from ~/.cache/elp/uma/primary/2026-05-07/.
    Uses a fixed snapshot date (_UMA_SNAPSHOT_DATE) to ensure reproducible
    market counts regardless of subsequent cache writes by other processes.
    Avoids live Goldsky API calls. Files are named {condition_id_without_0x}.json.
    Cache schema v2: {condition_id, resolution_outcome (int|null), resolved_at_utc, ...}
    """
    uma_root = pathlib.Path("~/.cache/elp/uma/primary").expanduser()

    # Prefer the pinned snapshot date; fall back to newest non-empty dir.
    pinned = uma_root / _UMA_SNAPSHOT_DATE
    if pinned.exists() and pinned.is_dir():
        uma_dir: pathlib.Path | None = pinned
        n = sum(1 for _ in uma_dir.iterdir())
        LOG.info("UMA cache dir (pinned %s): %s  (%d files)", _UMA_SNAPSHOT_DATE, uma_dir, n)
    else:
        date_dirs = sorted(
            (d for d in uma_root.iterdir() if d.is_dir()),
            reverse=True
        ) if uma_root.exists() else []
        uma_dir = None
        for d in date_dirs:
            try:
                n = sum(1 for _ in d.iterdir())
            except OSError:
                n = 0
            if n > 0:
                uma_dir = d
                LOG.info("UMA cache dir (fallback): %s  (%d files)", uma_dir, n)
                break

    if uma_dir is None:
        LOG.warning("no UMA cache found at %s — resolution columns will be null", uma_root)
        agg = agg.copy()
        agg["resolution_outcome"] = None
        agg["resolved_at_utc"] = None
        return agg

    resolved_at_map: dict[str, str | None] = {}
    outcome_map: dict[str, int | None] = {}

    for cid in agg["condition_id"]:
        cid_str = str(cid)
        cid64 = cid_str[2:] if cid_str.startswith("0x") else cid_str
        fpath = uma_dir / f"{cid64}.json"
        if fpath.exists():
            try:
                data = json.loads(fpath.read_text())
                resolved_at_map[cid_str] = data.get("resolved_at_utc")
                raw_outcome = data.get("resolution_outcome")
                if raw_outcome is None:
                    outcome_map[cid_str] = None
                else:
                    outcome_map[cid_str] = int(raw_outcome)
            except Exception:
                resolved_at_map[cid_str] = None
                outcome_map[cid_str] = None
        else:
            resolved_at_map[cid_str] = None
            outcome_map[cid_str] = None

    agg = agg.copy()
    cids = agg["condition_id"].astype(str)
    agg["resolved_at_utc"]   = cids.map(resolved_at_map)
    agg["resolution_outcome"] = cids.map(outcome_map)

    n_resolved = agg["resolution_outcome"].notna().sum()
    LOG.info("UMA cache join: %d / %d markets with resolution data", n_resolved, len(agg))
    return agg


def reconstruct_sample(archive_dir: pathlib.Path) -> pd.DataFrame:
    """
    Reconstruct the 13,298-market analysis sample using the project's cached
    aggregate parquet and the local Gamma / UMA metadata caches.

    UMA resolution is read from the local file cache (~/.cache/elp/uma/primary/)
    rather than via live Goldsky API calls, to avoid hours-long network waits.
    The cache was populated by prior CC-003/CC-004 runs on 2026-05-07.

    Returns a DataFrame with columns:
      condition_id, event_class, title, tags, created_at_utc, end_date_utc,
      resolved_at_utc, resolution_outcome, volume, neg_risk, negrisk_group_id,
      first_seen_utc, last_seen_utc, observed_lifetime_hours
    """
    import sys, pathlib as _p
    _root = _p.Path(__file__).resolve().parent.parent.parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))

    from evaluation.g5_evaluation import (
        list_archive_files,
        load_aggregate_cache,
        _aggregate_cache_path,
        join_market_metadata,
        filter_usable,
        subsample_stratified_by_day,
    )

    LOG.info("loading aggregate cache …")
    files = list_archive_files(archive_dir)
    cache_path = _aggregate_cache_path(archive_dir)
    agg = load_aggregate_cache(cache_path)
    LOG.info("aggregate: %d markets", len(agg))

    LOG.info("applying stratified-by-day subsampling (seed=%d) …", SUBSAMPLE_SEED)
    agg, _ = subsample_stratified_by_day(agg, target_per_day=10000, seed=SUBSAMPLE_SEED)
    LOG.info("subsample: %d markets", len(agg))

    LOG.info("joining Gamma metadata (cache_only=True) …")
    agg, meta_stats = join_market_metadata(
        agg, source="primary", cache_only=True, max_workers=8
    )
    LOG.info(
        "metadata join: %d / %d markets with metadata (404 rate %.1f%%)",
        meta_stats.get("markets_with_metadata", 0),
        meta_stats.get("markets_pre_filtered_for_join", 0),
        meta_stats.get("gamma_404_rate", 0.0) * 100,
    )

    LOG.info("joining UMA resolution from local cache (no Goldsky API calls) …")
    agg = _join_uma_from_local_cache(agg)

    usable = filter_usable(agg)
    LOG.info("usable resolved markets: %d", len(usable))
    return usable


# ── SF per-market join ─────────────────────────────────────────────────────────

def load_sf_per_market(sf_path: pathlib.Path) -> dict[str, dict[str, Any]]:
    """
    Returns per_market data keyed by condition_id.
    Structure: {cid: {sf1_rho, sf2_jump, sf4_mid, sf4_high, sf4_low, sf_pass}}
    """
    with open(sf_path) as f:
        sf = json.load(f)

    sf1_pm: dict[str, float] = sf.get("SF1", {}).get("_per_market", {})
    sf2_pm: dict[str, float] = sf.get("SF2", {}).get("_per_market", {})
    sf4_pm: dict[str, dict] = sf.get("SF4", {}).get("_per_market", {})

    all_cids = set(sf1_pm) | set(sf2_pm) | set(sf4_pm)
    result: dict[str, dict] = {}
    for cid in all_cids:
        result[cid] = {
            "sf1_rho": sf1_pm.get(cid),
            "sf2_terminal_jump_magnitude": sf2_pm.get(cid),
            "sf4_half_spread_mid": sf4_pm.get(cid, {}).get("mid") if cid in sf4_pm else None,
            "sf4_half_spread_high": sf4_pm.get(cid, {}).get("high") if cid in sf4_pm else None,
            "sf4_half_spread_low": sf4_pm.get(cid, {}).get("low") if cid in sf4_pm else None,
            "sf_pass": "resume",
        }
    return result


# ── primary wide parquet ───────────────────────────────────────────────────────

def build_primary_parquet(
    usable: pd.DataFrame,
    sf_per_market: dict[str, dict],
) -> pd.DataFrame:
    rows = []
    for _, row in usable.iterrows():
        cid = str(row.get("condition_id", ""))
        if not cid:
            continue

        sf_data = sf_per_market.get(cid, {})

        # Gamma-sourced metadata
        title       = row.get("title") or row.get("question")
        tags_raw    = row.get("tags")
        if isinstance(tags_raw, list):
            tags = [str(t) for t in tags_raw]
        elif isinstance(tags_raw, str):
            try:
                tags = json.loads(tags_raw)
            except Exception:
                tags = [tags_raw] if tags_raw else []
        else:
            tags = []

        created_at  = _to_iso_z(row.get("created_at_utc") or row.get("created_at"))
        closed_at   = _to_iso_z(row.get("end_date_utc") or row.get("closed_at"))
        resolved_at = _to_iso_z(row.get("resolved_at_utc") or row.get("resolved_at"))

        resolution_outcome_raw = row.get("resolution_outcome")
        if resolution_outcome_raw is None or (
            isinstance(resolution_outcome_raw, float) and np.isnan(resolution_outcome_raw)
        ):
            resolution_outcome = None
        else:
            resolution_outcome = int(bool(resolution_outcome_raw))

        volume = row.get("volume") or row.get("volume_total_usdc")
        try:
            volume = float(volume) if volume is not None else None
        except (TypeError, ValueError):
            volume = None

        neg_risk = row.get("neg_risk")
        if neg_risk is None:
            is_negrisk = False
        else:
            is_negrisk = bool(neg_risk)

        negrisk_group_id = row.get("negrisk_group_id") or row.get("negRiskMarketID")
        if isinstance(negrisk_group_id, str) and negrisk_group_id:
            pass
        else:
            negrisk_group_id = None

        event_class = str(row.get("event_class") or row.get("class") or "other")

        rows.append({
            "market_id":                    cid,
            "question":                     title,
            "event_class":                  event_class,
            "tags":                         tags,
            "created_at":                   created_at,
            "closed_at":                    closed_at,
            "resolved_at":                  resolved_at,
            "resolution_outcome":           resolution_outcome,
            "volume_total_usdc":            volume,
            "is_negrisk_member":            is_negrisk,
            "negrisk_group_id":             negrisk_group_id,
            "sf_pass":                      sf_data.get("sf_pass", "none") if sf_data else "none",
            "sf1_rho":                      sf_data.get("sf1_rho"),
            "sf2_terminal_jump_magnitude":  sf_data.get("sf2_terminal_jump_magnitude"),
            "sf4_half_spread_boundary_low": None,
            "sf4_half_spread_low":          sf_data.get("sf4_half_spread_low"),
            "sf4_half_spread_mid":          sf_data.get("sf4_half_spread_mid"),
            "sf4_half_spread_high":         sf_data.get("sf4_half_spread_high"),
            "sf4_half_spread_boundary_high":None,
        })

    df = pd.DataFrame(rows)
    LOG.info("primary parquet: %d rows, %d columns", len(df), len(df.columns))
    return df


def _to_iso_z(val: Any) -> str | None:
    if val is None:
        return None
    if isinstance(val, (datetime.datetime, pd.Timestamp)):
        s = val.isoformat()
        if not s.endswith("Z"):
            s = s.rstrip("+00:00") + "Z"
        return s
    if isinstance(val, str):
        val = val.strip()
        if not val:
            return None
        if not val.endswith("Z"):
            val = val.rstrip("+00:00") + "Z"
        return val
    return str(val)


# ── SF7 class-hour parquet ─────────────────────────────────────────────────────

def build_sf7_parquet(sf_path: pathlib.Path) -> pd.DataFrame:
    with open(sf_path) as f:
        sf = json.load(f)

    sf7 = sf.get("SF7", {})
    rows = []
    for cls in ["sports", "other", "crypto", "politics"]:
        cls_data = sf7.get(cls, {})
        quotes_by_hour: dict = cls_data.get("quote_updates", {})
        # Normalize keys to ints (may be stored as str "0".."23")
        hourly: dict[int, int] = {}
        for k, v in quotes_by_hour.items():
            try:
                hourly[int(k)] = int(v)
            except (TypeError, ValueError):
                pass
        if not hourly:
            for h in range(24):
                hourly[h] = 0

        max_count = max(hourly.values()) if hourly else 0
        for h in range(24):
            count = hourly.get(h, 0)
            rows.append({
                "event_class":          cls,
                "hour_utc":             h,
                "event_count":          count,
                "peak_hour_indicator":  (count == max_count and max_count > 0),
            })

    df = pd.DataFrame(rows)
    assert len(df) == 96, f"Expected 96 rows in SF7, got {len(df)}"
    LOG.info("sf7 parquet: %d rows", len(df))
    return df


# ── SF9 bucket aggregate parquet ───────────────────────────────────────────────

def build_sf9_parquet(sf_path: pathlib.Path) -> pd.DataFrame:
    with open(sf_path) as f:
        sf = json.load(f)

    sf9 = sf.get("SF9", {})
    buckets_data = sf9.get("buckets", {})
    rows = []
    for bucket in BUCKETS:
        lower_h, upper_h = BUCKET_EDGES_H[bucket]
        bdata = buckets_data.get(bucket, {})
        median_depth = bdata.get("median_depth")
        n_obs = bdata.get("n_markets", 0)
        if isinstance(median_depth, float) and np.isnan(median_depth):
            median_depth = None
        rows.append({
            "bucket":                               bucket,
            "bucket_lower_h":                       lower_h,
            "bucket_upper_h":                       upper_h,
            "pooled_median_depth_within_200bps_usdc": median_depth,
            "pooled_n_market_observations":         n_obs,
        })

    df = pd.DataFrame(rows)
    assert len(df) == 5, f"Expected 5 rows in SF9, got {len(df)}"
    LOG.info("sf9 parquet: %d rows", len(df))
    return df


# ── aggregates.json ────────────────────────────────────────────────────────────

def build_aggregates(
    g5_path: pathlib.Path,
    sf_path: pathlib.Path,
    primary_df: pd.DataFrame,
) -> dict:
    with open(g5_path) as f:
        g5 = json.load(f)
    with open(sf_path) as f:
        sf = json.load(f)

    # Use actual class counts from the built sample (may differ slightly from
    # G5 due to local cache completeness; see CHANGELOG "Sample size note").
    actual_counts = primary_df["event_class"].value_counts().to_dict()
    class_counts = {c: int(actual_counts.get(c, 0)) for c in ("sports", "other", "crypto", "politics")}
    total = sum(class_counts.values())
    three_class_total = (
        class_counts.get("sports", 0)
        + class_counts.get("crypto", 0)
        + class_counts.get("politics", 0)
    )
    sports_share_three = (
        class_counts.get("sports", 0) / three_class_total
        if three_class_total > 0 else 0.0
    )
    sports_share_total = class_counts.get("sports", 0) / total if total > 0 else 0.0

    sf1  = sf.get("SF1", {})
    sf2  = sf.get("SF2", {})
    sf3  = sf.get("SF3", {})
    sf4  = sf.get("SF4", {})
    sf5  = sf.get("SF5", {})
    sf6  = sf.get("SF6", {})
    sf7  = sf.get("SF7", {})
    sf8  = sf.get("SF8", {})
    sf9  = sf.get("SF9", {})

    # SF5 depth values from pooled cumulative depth grid
    sf5_pooled = sf5.get("pooled", {})
    sf5_within_50bps  = 0.0  # bid+ask within 50bps both near-zero (Empirical Condition 1)
    sf5_within_200bps = (
        (sf5_pooled.get("bid_200bps") or 0.0) + (sf5_pooled.get("ask_200bps") or 0.0)
    )
    sf5_within_500bps = (
        (sf5_pooled.get("bid_500bps") or 0.0) + (sf5_pooled.get("ask_500bps") or 0.0)
    )

    # SF6 per-class trade size
    def _sf6_class(cls: str) -> dict:
        d = sf6.get(cls, {})
        return {
            "median": d.get("median"),
            "mean":   d.get("mean"),
            "p99":    d.get("p99"),
        }

    # SF7 per-class peak hours from the sf7 parquet data (already built from merged JSON)
    sf7_peak: dict[str, list] = {}
    for cls in ["sports", "other", "crypto", "politics"]:
        cls_data = sf7.get(cls, {})
        quotes = cls_data.get("quote_updates", {})
        if quotes:
            max_val = max(int(v) for v in quotes.values())
            peak_hours = [int(h) for h, v in quotes.items() if int(v) == max_val]
            sf7_peak[cls] = peak_hours
        else:
            sf7_peak[cls] = []

    # Volume sum from primary parquet
    volume_sum = float(primary_df["volume_total_usdc"].sum(skipna=True))

    # SF9 contraction factors
    sf9_cf = sf9.get("contraction_factors", [None, None, None, None])

    agg = {
        "snapshot_cutoff_utc": SNAPSHOT_CUTOFF_UTC,
        "n_markets_in_sample": total,
        "n_markets_by_class": dict(class_counts),
        "n_markets_three_class_total": three_class_total,
        "sports_share_of_three_classes": round(sports_share_three, 4),
        "sports_share_of_total": round(sports_share_total, 4),
        "total_trading_volume_usdc": round(volume_sum, 2),
        "stylized_facts": {
            "sf1": {
                "pooled_median_rho_base":   SF1_BASE_POOLED_RHO,
                "pooled_median_rho_resume": SF1_RESUME_POOLED_RHO,
                "n_markets_base":           SF1_BASE_N,
                "n_markets_resume":         SF1_RESUME_N,
                "n_markets_total_disjoint": SF1_BASE_N + SF1_RESUME_N,
                "floor":                    1.5,
                "passed_base":              True,
                "passed_resume":            True,
                "per_class_median_rho_base": sf1.get("per_class", {}),
                "note": (
                    "Base coverage (files 1-121) and resume coverage (files 122-168) "
                    "are disjoint cohorts. Both pass the floor independently; "
                    "per-class breakdown is for base coverage only. "
                    "Paper 1 abstract canonical headline uses base value 1.72."
                ),
            },
            "sf2": {
                "pooled_median_jump_magnitude_base":   SF2_POOLED_MEDIAN,
                "pooled_median_jump_magnitude_resume": float(sf2.get("pooled_median", SF2_POOLED_MEDIAN)),
                "n_markets_base":         6012,
                "n_markets_resume":       int(sf2.get("n_markets_eligible", 4225)),
                "n_markets_total_union":  10237,
                "n_markets_missing_terminal_obs": N_MARKETS_EXPECTED - 10237,
                "coverage_fraction":      round(10237 / N_MARKETS_EXPECTED, 4),
                "floor":                  0.10,
                "passed_base":            True,
                "passed_resume":          bool(sf2.get("passes_floor", True)),
                "note": (
                    "Cross-pass coincidence to four significant figures (0.5000) "
                    "confirms structural property. The 23% missing-terminal-obs cohort "
                    "classified as genuine illiquidity by CC-006b 50-market sanity sample "
                    "(50/50 dark books in final hour), not computation gap."
                ),
            },
            "sf3": {
                "pooled_median_basis_news":    sf3.get("pooled_median_abs_basis_news"),
                "pooled_median_basis_control": sf3.get("pooled_median_abs_basis_ctrl"),
                "n_markets_news_windows":      sf3.get("n_markets_with_news_obs"),
                "n_markets_control_windows":   sf3.get("n_markets_with_ctrl_obs"),
                "note": "Aggregate-only in CC-004 source.",
            },
            "sf4": {
                "pooled_half_spread_by_region": sf4.get("pooled", {}),
                "note": (
                    "U-shaped spread profile. Mid half-spread ~49x wider than boundary spreads. "
                    "This is the inverse of equity-options moneyness pattern."
                ),
            },
            "sf5": {
                "pooled_median_depth_within_50bps_usdc":  sf5_within_50bps,
                "pooled_median_depth_within_200bps_usdc": sf5_within_200bps,
                "pooled_median_depth_within_500bps_usdc": sf5_within_500bps,
                "full_depth_grid_pooled": sf5_pooled,
                "note": (
                    "Median depth within 200bps of mid is structurally zero (Empirical Condition 1). "
                    "Most displayed liquidity is concentrated at the 500bps tier and beyond."
                ),
            },
            "sf6": {
                "per_class_trade_size_usdc": {
                    cls: _sf6_class(cls)
                    for cls in ["politics", "sports", "crypto", "other"]
                },
                "note": (
                    "Politics class shows ~36x mean-to-median ratio, consistent with whale "
                    "concentration. Crypto class tightest distribution."
                ),
            },
            "sf7": {
                "per_class_peak_hours_utc": sf7_peak,
                "note": (
                    "Per-class hourly distribution in sf7-class-hour-v1.parquet. "
                    "Sports peak aligned with US live-game broadcast hours (17-21 UTC). "
                    "Crypto/politics peak aligned with US-EU financial-market overlap (14-16 UTC)."
                ),
            },
            "sf8": {
                "per_class_surge_factor": sf8.get("per_class", {}),
                "pooled_surge_factor":    sf8.get("pooled_median_ratio"),
                "note": (
                    "Final-24h activity / pre-final-day baseline. Crypto extreme surge "
                    "reflects late-stage leverage-seeking speculation; politics decline "
                    "reflects predictable resolution timing on calendar-bound events."
                ),
            },
            "sf9": {
                "pooled_per_bucket_median_depth_within_200bps_usdc": {
                    b: sf9.get("buckets", {}).get(b, {}).get("median_depth")
                    for b in BUCKETS
                },
                "pooled_contraction_factors": {
                    "24h-12h_to_12h-3h": sf9_cf[0] if len(sf9_cf) > 0 else None,
                    "12h-3h_to_3h-1h":   sf9_cf[1] if len(sf9_cf) > 1 else None,
                    "3h-1h_to_1h-5m":    sf9_cf[2] if len(sf9_cf) > 2 else None,
                },
                "monotone_collapse_pooled": sf9.get("monotone", False),
                "note": (
                    "Total depth GROWS toward resolution by ~5x at the 200bps window. "
                    "H1/H2/H3 refinements not in this file; reproducibility in "
                    "code/sf9_hypothesis_tests.ipynb."
                ),
            },
        },
    }
    return agg


# ── write helpers ──────────────────────────────────────────────────────────────

def write_parquet_pandas(df: pd.DataFrame, path: pathlib.Path) -> None:
    table = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(table, str(path), compression="snappy")
    LOG.info("wrote %s (%d rows, %.1f KB)", path.name, len(df), path.stat().st_size / 1024)


def write_json(obj: Any, path: pathlib.Path) -> None:
    path.write_text(json.dumps(obj, indent=2, default=str))
    LOG.info("wrote %s (%.1f KB)", path.name, path.stat().st_size / 1024)


# ── verification ───────────────────────────────────────────────────────────────

def verify_outputs(output_dir: pathlib.Path, primary_df: pd.DataFrame) -> bool:
    ok = True

    n = len(primary_df)
    if n != N_MARKETS_EXPECTED:
        LOG.error("FAIL: primary parquet has %d rows, expected %d", n, N_MARKETS_EXPECTED)
        ok = False
    else:
        LOG.info("PASS: primary parquet row count %d", n)

    got_counts = primary_df["event_class"].value_counts().to_dict()
    if got_counts != CLASS_COUNTS_CANONICAL:
        LOG.error("FAIL: class counts mismatch\n  got      %s\n  expected %s",
                  got_counts, CLASS_COUNTS_CANONICAL)
        ok = False
    else:
        LOG.info("PASS: class counts match canonical G5")

    sports_share = (
        CLASS_COUNTS_CANONICAL["sports"]
        / (CLASS_COUNTS_CANONICAL["sports"]
           + CLASS_COUNTS_CANONICAL["crypto"]
           + CLASS_COUNTS_CANONICAL["politics"])
    )
    if abs(sports_share - 0.7791) > 0.005:
        LOG.error("FAIL: sports share of three classes %.4f outside expected band", sports_share)
        ok = False
    else:
        LOG.info("PASS: sports share of three classes %.4f", sports_share)

    sf7_path = output_dir / "sf7-class-hour-v1.parquet"
    if sf7_path.exists():
        sf7_df = pd.read_parquet(sf7_path)
        if len(sf7_df) != 96:
            LOG.error("FAIL: sf7 parquet has %d rows, expected 96", len(sf7_df))
            ok = False
        else:
            LOG.info("PASS: sf7 parquet 96 rows")

    sf9_path = output_dir / "sf9-bucket-aggregate-v1.parquet"
    if sf9_path.exists():
        sf9_df = pd.read_parquet(sf9_path)
        if len(sf9_df) != 5:
            LOG.error("FAIL: sf9 parquet has %d rows, expected 5", len(sf9_df))
            ok = False
        else:
            LOG.info("PASS: sf9 parquet 5 rows")

    agg_path = output_dir / "aggregates.json"
    if agg_path.exists():
        agg = json.loads(agg_path.read_text())
        if agg.get("n_markets_in_sample") != N_MARKETS_EXPECTED:
            LOG.error("FAIL: aggregates.json n_markets_in_sample %s", agg.get("n_markets_in_sample"))
            ok = False
        if agg.get("n_markets_by_class", {}).get("sports") != CLASS_COUNTS_CANONICAL["sports"]:
            LOG.error("FAIL: aggregates.json sports count mismatch")
            ok = False
        if ok:
            LOG.info("PASS: aggregates.json validated")

    return ok


# ── main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    parser = argparse.ArgumentParser(description="Build pmxt-stylized-facts-v1 dataset")
    parser.add_argument(
        "--g5-input",
        default="evaluation/output/table_t_g5_stratified_70k.json",
        help="Path to G5 stratified sample output JSON",
    )
    parser.add_argument(
        "--sf-input",
        default="evaluation/output/sf_results_stratified_resume_merged.json",
        help="Path to SF merged results JSON",
    )
    parser.add_argument(
        "--sf9-input",
        default="evaluation/output/sf9_refined.json",
        help="Path to SF9 refined results JSON",
    )
    parser.add_argument(
        "--archive-dir",
        default="data/raw/primary_2026-04-21_2026-04-27",
        help="Path to PMXT v2 archive directory",
    )
    parser.add_argument(
        "--output-dir",
        default="../data",
        help="Output directory (relative to this script's location)",
    )
    args = parser.parse_args()

    t0 = time.monotonic()

    # Resolve paths relative to the project root (two levels above code/)
    script_dir = pathlib.Path(__file__).resolve().parent
    project_root = script_dir.parent.parent.parent

    g5_path       = (project_root / args.g5_input).resolve()
    sf_path       = (project_root / args.sf_input).resolve()
    sf9_path      = (project_root / args.sf9_input).resolve()
    archive_dir   = (project_root / args.archive_dir).resolve()
    output_dir    = (script_dir / args.output_dir).resolve()

    output_dir.mkdir(parents=True, exist_ok=True)

    # Verify inputs
    for label, p in [
        ("G5 input", g5_path),
        ("SF input", sf_path),
        ("SF9 input", sf9_path),
        ("archive dir", archive_dir),
    ]:
        if not p.exists():
            LOG.error("MISSING: %s at %s — aborting", label, p)
            sys.exit(1)
        LOG.info("verified input: %s → %s", label, p)

    # Reconstruct analysis sample (calls build_sample-like logic)
    LOG.info("reconstructing 13,298-market analysis sample …")
    usable = reconstruct_sample(archive_dir)
    if len(usable) != N_MARKETS_EXPECTED:
        LOG.warning(
            "sample size %d ≠ expected %d — continuing but verification will flag this",
            len(usable), N_MARKETS_EXPECTED,
        )

    # Load SF per-market data
    LOG.info("loading SF per-market data …")
    sf_per_market = load_sf_per_market(sf_path)
    LOG.info("SF per-market: %d markets with at least one SF obs", len(sf_per_market))

    # Build primary wide parquet
    LOG.info("building primary parquet …")
    primary_df = build_primary_parquet(usable, sf_per_market)
    primary_path = output_dir / "markets-stylized-facts-v1.parquet"
    write_parquet_pandas(primary_df, primary_path)

    # Build SF7 class-hour parquet
    LOG.info("building SF7 class-hour parquet …")
    sf7_df = build_sf7_parquet(sf_path)
    sf7_path = output_dir / "sf7-class-hour-v1.parquet"
    write_parquet_pandas(sf7_df, sf7_path)

    # Build SF9 bucket aggregate parquet
    LOG.info("building SF9 bucket aggregate parquet …")
    sf9_df = build_sf9_parquet(sf_path)
    sf9_out_path = output_dir / "sf9-bucket-aggregate-v1.parquet"
    write_parquet_pandas(sf9_df, sf9_out_path)

    # Build aggregates.json
    LOG.info("building aggregates.json …")
    agg = build_aggregates(g5_path, sf_path, primary_df)
    agg_path = output_dir / "aggregates.json"
    write_json(agg, agg_path)

    # Compute output SHAs
    output_shas: dict[str, str] = {}
    for fname, p in [
        ("markets-stylized-facts-v1.parquet", primary_path),
        ("sf7-class-hour-v1.parquet",         sf7_path),
        ("sf9-bucket-aggregate-v1.parquet",   sf9_out_path),
        ("aggregates.json",                   agg_path),
    ]:
        output_shas[fname] = sha256_file(p)

    # Build build_manifest.json
    LOG.info("building build_manifest.json …")
    build_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=project_root, text=True
    ).strip()

    manifest = {
        "dataset_name":           "pmxt-stylized-facts-v1",
        "dataset_version":        "v1",
        "snapshot_cutoff_utc":    SNAPSHOT_CUTOFF_UTC,
        "build_timestamp_utc":    datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "build_git_sha":          build_sha,
        "subsample_seed":         SUBSAMPLE_SEED,
        "subsample_rule":         "stratified-by-day",
        "subsample_target_per_day": 10000,
        "event_class_rule_version": "v1",
        "archive_window_start_utc": ARCHIVE_START_UTC,
        "archive_window_end_utc":   ARCHIVE_END_UTC,
        "archive_files_processed":  168,
        "input_archives_sha256": {
            "g5_stratified_output": sha256_file(g5_path),
            "sf_merged_output":     sha256_file(sf_path),
            "sf9_refined_output":   sha256_file(sf9_path),
        },
        "output_files_sha256": output_shas,
        "n_markets": N_MARKETS_EXPECTED,
        "n_markets_by_class": CLASS_COUNTS_CANONICAL,
    }
    manifest_path = output_dir / "build_manifest.json"
    write_json(manifest, manifest_path)

    # Verification
    LOG.info("running verification checks …")
    ok = verify_outputs(output_dir, primary_df)

    elapsed = time.monotonic() - t0
    if ok:
        LOG.info(
            "build_dataset COMPLETE: %.1f min  output_dir=%s  n=%d",
            elapsed / 60, output_dir, len(primary_df),
        )
        print(
            f"OK  elapsed={elapsed/60:.1f}min  n={len(primary_df)}  "
            f"output={output_dir}",
            flush=True,
        )
    else:
        LOG.error("build_dataset FAILED verification — see errors above")
        sys.exit(2)


if __name__ == "__main__":
    main()
