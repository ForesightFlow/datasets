# Polymarket ILS Corpus (v1)

Population-scale Information Leakage Score (ILS) computations for 4,801 resolved
Polymarket markets. Each record provides the ILS, multi-window pre-anchor variants,
top-wallet concentration (HHI), scope-condition flags, and an `anchor_type` column
that distinguishes the **5 genuinely event-anchored markets** from the **4,796
resolution-proxy markets** that comprise the bulk of the corpus.

> **Anchor caveat (read before use).**
> 99.9% of records use `t_news = t_resolve − 24h` as the anchor (structural proxy).
> Only 5 records have an independently recovered $T_{\text{event}}$ anchor with a
> gap materially different from 24 hours. Downstream analyses that require true
> event-anchoring should use the `event_anchored_subset.jsonl` (5 records) or the
> dedicated [`polymarket-deadline-ils-v3`](../polymarket-deadline-ils) dataset
> (88 markets, LLM-recovered T_event). See the `anchor_type` field.

## Quick stats

| Field | Value |
|---|---:|
| Total markets | 4,801 |
| `anchor_type = proxy_24h` | 4,796 (99.9%) |
| `anchor_type = event` | 5 (0.1%) |
| Markets with `scope_all_pass = true` | 2,548 (53.1%) |
| Snapshot date | 2026-04-30 |
| Taxonomy version | v1.1 (post-esports correction) |
| Anchor description | `t_resolve − 24h` proxy (4,796); recovered $T_{\text{event}}$ (5) |
| Window variants per market | 30min, 2h, 6h, 24h, 7d, full pre-news |
| License | CC-BY 4.0 |

## Category breakdown

| Category | Total | proxy_24h | event-anchored |
|---|---:|---:|---:|
| regulatory_decision | 3,443 | 3,441 | 2 |
| military_geopolitics | 902 | 899 | 3 |
| esports | 273 | 273 | 0 |
| corporate_disclosure | 183 | 183 | 0 |

## Schema

Each record is a JSON object:

| Field | Type | Description |
|---|---|---|
| `market_id` | string | Polymarket condition ID |
| `question` | string | Market question text |
| `fflow_category` | string | Category label from ForesightFlow taxonomy (v1.1) |
| `resolution_type` | string | `event_resolved`, `deadline_resolved`, or `unclassifiable` |
| `resolution_outcome` | int \| null | `0` (NO) or `1` (YES); `null` if unresolved |
| `volume_total_usdc` | float \| null | Cumulative traded volume in USDC |
| `t_open` | string (ISO 8601) | Market opening timestamp |
| `t_news` | string (ISO 8601) | Anchor timestamp: recovered T_event (5 markets) or `t_resolve − 24h` proxy (4,796) |
| `t_resolve` | string (ISO 8601) | Market resolution timestamp |
| `t_news_gap_hours` | float | `(t_resolve − t_news)` in hours; = 24.0 for proxy markets |
| `anchor_type` | string | `"event"` (gap ≠ 24h, independent T_event) or `"proxy_24h"` (gap = 24h) |
| `anchor_tier` | string \| null | Source tier: `"tier1"`, `"tier2"`, `"tier3"`, or `"proxy"` |
| `p_open` | float | Market price at `t_open` |
| `p_news` | float | Market price at `t_news` (the anchor) |
| `p_resolve` | int | Resolution outcome (0 or 1) |
| `delta_pre` | float | `p_news − p_open` |
| `delta_total` | float | `p_resolve − p_open` |
| `ils` | float | ILS anchored at `t_news`; null when `\|delta_total\|` < ε |
| `ils_30min` | float \| null | ILS in the last 30 min before `t_news` |
| `ils_2h` | float \| null | ILS in the last 2 hours before `t_news` |
| `ils_6h` | float \| null | ILS in the last 6 hours before `t_news` |
| `ils_24h` | float \| null | ILS in the last 24 hours before `t_news` |
| `ils_7d` | float \| null | ILS in the last 7 days before `t_news` |
| `volume_pre_share` | float | Fraction of total volume traded before `t_news` |
| `pre_news_max_jump` | float | Maximum price jump observed before `t_news` |
| `wallet_hhi_top10` | float \| null | HHI of top-10 wallet concentration (aggregate only; no wallet IDs) |
| `n_trades_total` | int | Total indexed trades |
| `n_trades_pre_news` | int | Trades indexed before `t_news` |
| `flags` | array of strings | Per-record flags (e.g. `window_7d_predates_topen`) |
| `price_source` | string | Price data source (`trade_vwap`) |
| `scope_pass_non_trivial_move` | bool | `\|delta_total\| ≥ ε` (non-null ILS) |
| `scope_pass_edge_effect` | bool | `\|p_open − 0.5\| ≤ 0.4` (substantive opening uncertainty) |
| `scope_all_pass` | bool | All scope conditions satisfied |
| `snapshot_date` | string | DB snapshot date |

## Quick-start

```python
import pandas as pd

# Load corpus
df = pd.read_parquet("data/ils_corpus_v1.parquet")

# Clean subset: scope conditions passed
clean = df[df["scope_all_pass"]]
print(f"Clean-scope markets: {len(clean)}")  # 2,548

# Per-category ILS distribution (proxy-anchored; 99.9% of records)
print(clean.groupby("fflow_category")["ils"].describe())

# Genuinely event-anchored records (5 markets)
event_anchored = df[df["anchor_type"] == "event"]
print(f"Event-anchored: {len(event_anchored)}")

# High-signal screening: ILS > 0.25 with elevated short-window
flagged = clean[
    (clean["ils"] > 0.25) &
    ((clean["ils_30min"] > 0.10) | (clean["ils_2h"] > 0.10))
]
print(f"Flagged for review: {len(flagged)}")
```

## Files

| File | Description | Size (approx) |
|---|---|---:|
| `data/ils_corpus_v1.parquet` | Full corpus, Parquet (Snappy compressed) | ~950 KB |
| `data/ils_corpus_v1.jsonl.gz` | Full corpus, JSONL gzipped | ~680 KB |
| `data/clean_scope_subset.jsonl` | 2,548 rows where `scope_all_pass = true` | ~2.5 MB |
| `data/event_anchored_subset.jsonl` | 5 rows where `anchor_type = "event"` | <5 KB |
| `data/scope_failure_breakdown.csv` | Per-condition failure counts | <1 KB |
| `MANIFEST.json` | SHA-256 hashes of all data files | <1 KB |

## ILS definition

For a resolved binary market with anchor timestamp $T_{\text{news}}$:

$$\text{ILS}(M) = \frac{p(T_{\text{news}}^-) - p(T_{\text{open}})}{p_{\text{resolve}} - p(T_{\text{open}})}$$

where $p(T_{\text{news}}^-)$ is the last observed price before the anchor. The score
measures the fraction of the terminal price move that occurred before the anchor.

**Proxy anchor interpretation.** For the 4,796 proxy markets, $T_{\text{news}} =
T_{\text{resolve}} - 24\text{h}$. The ILS therefore measures how much of the
resolution-day price move was visible 24 hours before settlement — a resolution-proxy
ILS, not an event-anchored ILS. Treat positive values as evidence of informed
positioning OR of price drift toward resolution, since the anchor is not the public
information event.

**Multi-window variants.** For each window $w \in \{30\text{min}, 2\text{h}, 6\text{h},
24\text{h}, 7\text{d}\}$:

$$\text{ILS}_w(M) = \frac{p(T_{\text{news}}^-) - p(T_{\text{news}} - w)}{p_{\text{resolve}} - p(T_{\text{open}})}$$

**Scope conditions.** Two operational scope conditions are evaluated per record:
1. **Non-trivial total move:** $|\Delta_{\text{total}}| \geq \varepsilon$ — denominator
   well-conditioned (non-null ILS).
2. **Edge effect:** $|p(T_{\text{open}}) - 0.5| \leq 0.4$ — substantive uncertainty
   at market opening.

Records failing any condition are retained with `scope_all_pass = false`.
The clean-scope subset (`scope_all_pass = true`, 2,548 markets) is the recommended
analysis population.

## Differentiation from related datasets

| Dataset | Anchor | N markets | Depth |
|---|---|---:|---|
| `polymarket-deadline-ils-v3` | $T_{\text{event}}$ (LLM-recovered) | 88 | Deep: bootstrap CIs, hazard-adjusted variants |
| `polymarket-ils-corpus-v1` (this) | $t_{\text{resolve}} − 24\text{h}$ proxy (99.9%) | 4,801 | Breadth: multi-window, scope flags, HHI |
| `pmxt-behavioral-clusters-v1` | $T_{\text{resolve}}$ fill-week window | ~3,864 | Resolution-anchored, behavioral clusters |

This corpus and `pmxt-behavioral-clusters-v1` have **zero market overlap**: behavioral
clusters covers fill activity during April 21–27 2026 (mostly open, unresolved markets),
while this corpus covers resolved markets across 2022–2026. The two datasets measure
ILS at orthogonal points in a market's lifecycle.

## Citation

```bibtex
@misc{nechepurenko2026population-leakage,
  title  = {Information Leakage at Population Scale: An Evaluation of the {Polymarket} Insider-Relevant Subpopulation},
  author = {Nechepurenko, Maksym},
  year   = {2026},
  doi    = {10.48550/arXiv.2605.00459},
  url    = {https://arxiv.org/abs/2605.00459},
  note   = {SSRN Working Paper 6686819}
}

@misc{nechepurenko2026ils-framework,
  title  = {{ForesightFlow}: An Information Leakage Score Framework for Prediction Markets},
  author = {Nechepurenko, Maksym},
  year   = {2026},
  doi    = {10.48550/arXiv.2605.00493},
  url    = {https://arxiv.org/abs/2605.00493},
  note   = {SSRN Working Paper 6687361}
}
```

## Related datasets

- [`polymarket-tnews-tevent-recovery`](../polymarket-tnews-tevent-recovery) —
  Source of the 5 genuinely event-anchored T_event timestamps in this corpus
  (Tier 2/3 recovery).
- [`polymarket-hazard-rates`](../polymarket-hazard-rates) — Per-category exponential
  hazard fits; not used in the proxy-anchored ILS computation but relevant context
  for interpreting the 5 event-anchored records.
- [`polymarket-deadline-ils`](../polymarket-deadline-ils) — Smaller (88-market) deeper
  companion with LLM-recovered T_event, bootstrap CIs, and hazard-adjusted columns.
- [`pmxt-behavioral-clusters`](../pmxt-behavioral-clusters) — Companion publishing
  resolution-anchored ILS variants (different market population, different anchor).
- [`ffic-inventory`](../ffic-inventory) — Documented insider-trading cases.

## Versioning

- **v1** (2026-05-13) — Initial release. 4,801 markets. Post-esports-correction
  taxonomy (v1.1). Snapshot cut 2026-04-30. Anchor type explicitly labelled
  (`anchor_type` column); ILS column is proxy-anchored for 99.9% of records.

## License

CC-BY 4.0 — see [`LICENSE`](LICENSE).

## Limitations

1. **Proxy anchor is not T_event.** For 4,796 of 4,801 records, `t_news` is set to
   `t_resolve − 24h`. Positive ILS values for these records may reflect resolution
   convergence, not genuinely informed pre-event positioning. Use the
   `event_anchored_subset.jsonl` (5 records) or `polymarket-deadline-ils-v3` for
   event-anchored analysis.

2. **Scope exclusion rate.** 46.9% of records fail the `edge_effect` scope condition
   (`|p_open − 0.5| > 0.4`). Many Polymarket markets open at high-probability prices
   (e.g., near-certain regulatory outcomes), making the edge condition restrictive.
   Researchers may apply a looser threshold for specific categories.

3. **HHI coverage gap.** `wallet_hhi_top10` is non-null for only 1,391 of 4,801
   markets (29.0%) — trade-level data must exist in the `trades` table for HHI to be
   computed.

4. **7d window gap.** `ils_7d` is non-null for only 50.7% of markets; markets with
   `t_open` within 7 days of `t_news` receive a `window_7d_predates_topen` flag and
   null `ils_7d`.

5. **Esports markets.** 273 esports markets are included with category label
   `esports`. For geopolitical-event analyses, filter to `fflow_category !=
   "esports"`.
