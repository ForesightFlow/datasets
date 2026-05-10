# Polymarket Stylized Facts Dataset

Per-market stylized-facts measurements (SF1–SF9) for 13,314 resolved Polymarket binary-event markets over the seven-day window 2026-04-21 to 2026-04-27, released as the empirical foundation for Paper 1 of the four-paper Event-Linked Perpetuals research programme.

**Version:** 1.0  
**Tag:** `pmxt-stylized-facts-v1`  
**License:** CC-BY 4.0  
**Companion paper:** Nechepurenko (2026), *Resolution-Aware Perpetual Futures on Binary Prediction Markets: An Empirical Risk-Design Framework Using Polymarket Data*

---

## Why this dataset exists

Microstructure analysis of prediction markets requires per-market measurements of properties that are not directly available in raw on-chain transaction archives: how depth distributes across the price range, how prices jump near resolution, how trade size distributes by event class, how spreads vary with the index level. Computing these quantities on the full PMXT v2 archive at scale is feasible but expensive — approximately 10 hours of wall time on the 13.7B-event seven-day archive. Each research group studying Polymarket microstructure has had to either re-derive these quantities or settle for cruder proxies.

This dataset provides nine stylized-fact measurements (SF1 through SF9) computed on a stratified sample of 13,314 Polymarket markets that resolved during 2026-04-21 to 2026-04-27. The sample is reproducible via locked seed (20260505) and a stratified-by-day rule that addresses single-day selection bias documented in the companion paper's Appendix B. The measurements are released as a shared baseline that other researchers can use directly, evaluate against alternative methodologies, or extend.

Beyond the companion paper's specific use, the dataset is useful for: comparative analysis with other prediction-market venues (Kalshi, Manifold), calibration of microstructure models adapted to bounded-event underlyings, and follow-up empirical research on Polymarket binary-event markets.

---

## What the dataset contains

The dataset covers 13,314 resolved Polymarket binary-event markets from the PMXT v2 seven-day archive (2026-04-21 to 2026-04-27). Per-market columns are provided for SF1 (boundary depth asymmetry), SF2 (terminal jump magnitude), and SF4 (half-spread by index region) — the three stylized facts for which CC-004 computed per-market arrays. SF3, SF5, SF6, SF7, SF8, SF9 are aggregate-only computations; their pooled and per-class values appear in `aggregates.json`, with SF7 (hourly activity) in `sf7-class-hour-v1.parquet` and SF9 (depth by time-to-resolution bucket) in `sf9-bucket-aggregate-v1.parquet`.

### Counts by event class

| event_class | Count | Share of total | Share of three classes |
|---|---|---|---|
| `sports` | 6,800 | 51.1% | **77.9%** |
| `other` | 4,584 | 34.4% | (excluded from three-class metric) |
| `crypto` | 1,518 | 11.4% | 17.4% |
| `politics` | 412 | 3.1% | 4.7% |
| **Total** | **13,314** | 100% | — |

The "share of three classes" column excludes `other` from the denominator and matches Paper 1's sports-dominance metric (77.9% triggered the pre-registered ≤70% threshold consequence rule on the analysis sample).

### Stylized facts headline summary

| Stylized fact | Headline value | Floor (if pre-registered) | Passed | Note |
|---|---|---|---|---|
| SF1 boundary depth asymmetry ρ (base) | 1.72 | ≥ 1.5 | ✓ | 4,030 markets, files 1–121 |
| SF1 boundary depth asymmetry ρ (resume) | 1.65 | ≥ 1.5 | ✓ | 1,648 markets, files 122–168 |
| SF2 terminal jump magnitude \|Δ\| | 0.50 | ≥ 0.10 | ✓ | identical to 4 sig figs across base and resume |
| SF3 news vs control basis | 0.0132 / 0.0367 | descriptive | — | basis smaller in news (fast-EMA adapts) |
| SF4 mid half-spread | 0.27 | descriptive | — | ~49× wider than boundary spreads |
| SF8 crypto surge factor | 24.62× | descriptive | — | extreme late-stage leverage activity |
| SF8 politics surge factor | 0.68× | descriptive | — | predictable resolution timing |
| SF9 12h-3h → 3h-1h depth ratio | 4.91 | descriptive | — | growth (not contraction) at 200bps window |

### Corpus summary

| Attribute | Value |
|---|---|
| Total markets in sample | 13,314 |
| Source archive | PMXT v2, 168 files |
| Date range (resolved_at) | 2026-04-21 to 2026-04-27 UTC |
| Sample composition | sports-dominant: 77.9% of three-class total (excluding `other`) |
| Subsample rule | stratified-by-day, seed 20260505 |
| Snapshot cutoff | 2026-04-27T23:59:59Z |
| Format | Parquet (primary), JSON (aggregates) |

---

## Schema

### Primary file: `markets-stylized-facts-v1.parquet`

One row per market. SF1, SF2, and SF4 carry per-market columns; all other stylized facts are aggregate-only (in `aggregates.json`).

| Field | Type | Source | Description |
|---|---|---|---|
| `market_id` | string | gamma | Polymarket condition ID, lowercase 0x-prefixed hex |
| `question` | string | gamma | Market question text |
| `event_class` | string | g5 sample | One of `sports`, `politics`, `crypto`, `other` |
| `tags` | list[string] | gamma | Polymarket tag names (string names, not numeric IDs) |
| `created_at` | string | gamma | ISO 8601 UTC, `Z` suffix |
| `closed_at` | string \| null | gamma | ISO 8601 UTC, `Z` suffix; null if not reported |
| `resolved_at` | string | uma | ISO 8601 UTC, `Z` suffix (UMA OO settlement) |
| `resolution_outcome` | int8 | uma | 0 (NO) or 1 (YES) |
| `volume_total_usdc` | float64 \| null | gamma | Cumulative trading volume |
| `is_negrisk_member` | bool | gamma | Whether part of a Polymarket negRisk group |
| `negrisk_group_id` | string \| null | gamma | Group identifier if applicable; else null |
| `sf_pass` | string | sf | CC-004 pass that produced SF row data: `resume` or `none` |
| `sf1_rho` | float64 \| null | sf | Boundary depth asymmetry ratio; null if no boundary obs |
| `sf2_terminal_jump_magnitude` | float64 \| null | sf | \|Δ index\| over [restime − 1h, restime]; null for 23% illiquidity cohort |
| `sf4_half_spread_boundary_low` | float64 \| null | sf | Median half-spread when index < 0.10; null in v1 (not per-market in CC-004) |
| `sf4_half_spread_low` | float64 \| null | sf | index in [0.10, 0.30) |
| `sf4_half_spread_mid` | float64 \| null | sf | index in [0.30, 0.70] |
| `sf4_half_spread_high` | float64 \| null | sf | index in (0.70, 0.90] |
| `sf4_half_spread_boundary_high` | float64 \| null | sf | Median half-spread when index > 0.90; null in v1 |

**Note:** SF3, SF5, SF6, SF7, SF8, SF9 are aggregate-only in the CC-004 source data. Per-market arrays for these SFs were not emitted by CC-004. Their pooled and per-class values are in `aggregates.json`. SF7 hourly activity is in `sf7-class-hour-v1.parquet` (per-class × hour). SF9 depth-by-bucket is in `sf9-bucket-aggregate-v1.parquet`.

**Example record (JSON):**

```json
{
  "market_id": "0x1a2b3c4d5e6f...",
  "question": "Will the 2026 NBA Finals go to a Game 7?",
  "event_class": "sports",
  "tags": ["Sports", "NBA", "Basketball"],
  "created_at": "2026-04-01T12:00:00Z",
  "closed_at": "2026-06-30T00:00:00Z",
  "resolved_at": "2026-04-23T18:45:00Z",
  "resolution_outcome": 0,
  "volume_total_usdc": 84211.5,
  "is_negrisk_member": false,
  "negrisk_group_id": null,
  "sf_pass": "resume",
  "sf1_rho": 1.84,
  "sf2_terminal_jump_magnitude": 0.50,
  "sf4_half_spread_boundary_low": null,
  "sf4_half_spread_low": 0.08,
  "sf4_half_spread_mid": 0.29,
  "sf4_half_spread_high": 0.07,
  "sf4_half_spread_boundary_high": null
}
```

---

## Quick start

### Parquet (fast columnar queries)

```python
import pandas as pd

df = pd.read_parquet("data/markets-stylized-facts-v1.parquet")

# Median terminal jump magnitude by event class (SF2)
jump_by_class = (
    df[df["sf2_terminal_jump_magnitude"].notna()]
    .groupby("event_class")["sf2_terminal_jump_magnitude"]
    .median()
    .sort_values(ascending=False)
)
print(jump_by_class)
# crypto    0.9995
# sports    0.5000
# politics  0.5000
# other     0.5000

# Median boundary depth asymmetry (SF1) by class
rho_by_class = (
    df[df["sf1_rho"].notna()]
    .groupby("event_class")["sf1_rho"]
    .median()
)
print(rho_by_class)
```

### DuckDB (SQL, zero Python overhead)

```python
import duckdb

con = duckdb.connect()

# SF9: depth growth approaching resolution
con.execute("""
    SELECT bucket, bucket_lower_h, bucket_upper_h,
           pooled_median_depth_within_200bps_usdc,
           pooled_n_market_observations
    FROM read_parquet('data/sf9-bucket-aggregate-v1.parquet')
    ORDER BY bucket_lower_h DESC
""").df()
# Shows the ~5x depth growth from 12h-3h → 3h-1h bucket
```

### Aggregates (class-level and pooled statistics)

```python
import json

agg = json.load(open("data/aggregates.json"))

# SF1 headline values
sf1 = agg["stylized_facts"]["sf1"]
print(f"SF1 ρ (base):   {sf1['pooled_median_rho_base']:.4f}  [n={sf1['n_markets_base']}]")
print(f"SF1 ρ (resume): {sf1['pooled_median_rho_resume']:.4f}  [n={sf1['n_markets_resume']}]")
print("Per-class (base):", sf1["per_class_median_rho_base"])
```

---

## Versioning policy

This dataset is a snapshot frozen at the 2026-04-27T23:59:59Z cutoff. The stylized-fact computations reflect the methodology as specified in Paper 1 Section 5 and the EVENT_CLASS_DERIVATION rule version v1. Future versions will extend the empirical window or add SF computations as the four-paper programme develops; existing records will not be modified except to correct factual errors, documented in `CHANGELOG.md`. Each version is a distinct git tag; reproducibility-sensitive work should pin to `pmxt-stylized-facts-v1`.

---

## Citation

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20107449.svg)](https://doi.org/10.5281/zenodo.20107449)

If you use this dataset, please cite:

```bibtex
@dataset{nechepurenko_pmxt_stylized_facts_v1_2026,
  author       = {Nechepurenko, Maksym},
  title        = {{pmxt-stylized-facts-v1}: Stylized Facts on
                  {Polymarket} Binary-Event Markets
                  (Empirical Week 2026-04-21 to 2026-04-27)},
  year         = {2026},
  publisher    = {Zenodo},
  version      = {1.0.0},
  doi          = {10.5281/zenodo.20107449},
  url          = {https://doi.org/10.5281/zenodo.20107449}
}
```

If you also use the companion simulation outputs, please cite Paper 1:

```bibtex
@unpublished{nechepurenko_pirap_2026,
  author = {Nechepurenko, Maksym},
  title  = {Resolution-Aware Perpetual Futures on Binary Prediction
            Markets: An Empirical Risk-Design Framework Using
            Polymarket Data},
  year   = {2026},
  note   = {Working paper. arXiv DOI to be added when assigned.}
}
```

A `CITATION.cff` file is included for automated citation generation.

---

## Companion Datasets

This dataset is part of the PMXT bundle family for the Event-Linked Perpetuals research programme:

- **Bundle 2 (`pmxt-counterfactual-replay-v1`)**: Engine and resolution-zone protocol comparison outputs from CC-007b (E2) and CC-008 (E3). DOI: [10.5281/zenodo.20108387](https://doi.org/10.5281/zenodo.20108387)
- **Bundle 3 (`pmxt-behavioral-clusters-v1`, forthcoming)**: Per-trader behavioral cluster labels from Paper 4 (release after Paper 4 empirical run).

---

## License

The dataset metadata, computed stylized-fact measurements, and structured manifest are released under [CC-BY 4.0](LICENSE). Market questions and descriptions are sourced from the Polymarket Gamma API; Polymarket's own terms of service govern their original data. The CC-BY 4.0 grant above applies to the compiled dataset as a whole, including the stylized-fact computation layer and the structured format.

---

## Contact

Questions, corrections, or proposed methodology improvements: maksym@devnull.ae or via GitHub issue on this repository.
