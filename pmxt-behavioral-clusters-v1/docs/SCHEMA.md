# Data Schema — PMXT Behavioral Clusters v1

Column-by-column documentation for all parquet and JSON files in `data/`.

---

## per_cluster_summary.json

Top-level keys:
- `generated_at` — ISO 8601 UTC timestamp
- `n_clusters` — number of non-noise clusters (5 for k-means k=5)
- `total_addresses` — total addresses in clustering input
- `attribution_constraint` — CC-013 Amendment v2 constraint statement
- `clusters[]` — array of cluster objects:
  - `cluster_id` — integer 0–4 (k-means label)
  - `is_noise` — boolean (false for all in k-means)
  - `n_addresses` — count of addresses in cluster
  - `notional_share` — fraction of total taker-side notional in this cluster [0,1]
  - `archetype` — fill-side proxy label: `fill-MM`, `fill-LP`, `SPECIALIST`, `RETAIL`
  - `centroid` — dict of mean feature values (unscaled)
  - `ci_lo_95` / `ci_hi_95` — 95% bootstrap CI (B=1000) for each feature

---

## per_cluster_aggregates.parquet

| Column | Type | Description |
|--------|------|-------------|
| cluster_id | Int64 | k-means cluster label (0–4) |
| archetype | Utf8 | fill-side proxy archetype label |
| n_addresses | Int64 | addresses in cluster |
| notional_share | Float64 | fraction of total notional |
| f2_trade_intensity | Float64 | centroid: log1p(fills/active_hours) |
| f3_log_avg_notional | Float64 | centroid: log10(mean_notional_per_fill) |
| f5_directional_ratio | Float64 | centroid: (buy−sell)/(buy+sell) |
| f6_market_hhi | Float64 | centroid: Herfindahl index over token_ids |
| f7_intraday_entropy | Float64 | centroid: Shannon entropy over 24 hour bins |
| f9_log_market_breadth | Float64 | centroid: log(n_unique_markets+1) |

---

## per_address_tiers.parquet

| Column | Type | Description |
|--------|------|-------------|
| from_address | Utf8 | Polygon wallet address (pseudonymous) |
| trade_count | Int64 | total fills as taker or maker |
| total_notional | Float64 | total USDC notional traded |
| buy_notional | Float64 | taker-side buy notional |
| sell_notional | Float64 | taker-side sell notional |
| n_markets | Int64 | unique markets traded |
| f2_trade_intensity | Float64 | log1p(fills / active_hours) |
| f9_log_market_breadth | Float64 | log(n_unique_markets + 1) |
| cluster_id | Int64 | k-means cluster assignment (0–4, -99=unmatched) |
| archetype | Utf8 | k-means archetype label |
| tier | Utf8 | primary feature-tier (see below) |
| whale_tier_overlay | Boolean | total_notional >= $1M |

**Tier values (mutually exclusive, primary assignment):**
| Tier | Threshold |
|------|-----------|
| `whale-tier` | total_notional ≥ $1,000,000 |
| `high-frequency-operator` | f2 ≥ P95 AND f9 ≥ P75 (fill-MM-like) |
| `high-breadth-operator` | f9 ≥ P95 (ARB/large-LP-like) |
| `power-trader` | f2 ≥ P75 AND total_notional ≥ P75 |
| `episodic-retail` | total_notional < $10,000 |
| `active-retail` | residual |

*Note: `from_address` is pseudonymous on-chain identifier. Not linked to real-world identity.*

---

## tier_kmeans_crosstab.json

Cross-tabulation of feature tiers × k-means archetypes. Schema:
```json
{
  "generated_at": "...",
  "crosstab": {
    "<archetype>": {
      "<tier>": <count>,
      ...
    },
    ...
  }
}
```
Row = k-means archetype; column = feature tier; value = address count.

---

## per_market_microstructure.parquet

One row per market (token_id). 43,116 markets from the 2026-04-21 to 2026-04-27 window.

| Column | Type | Description |
|--------|------|-------------|
| token_id | Utf8 | ERC-1155 position token ID (decimal) |
| buy_notional | Float64 | taker-side buy USDC notional |
| sell_notional | Float64 | taker-side sell USDC notional |
| total_notional | Float64 | buy + sell notional |
| n_fills | Int64 | total fills |
| n_makers | Int64 | count of unique makers |
| n_bins_5m | Int64 | number of non-empty 5-min bins |
| OFI | Float64 | order flow imbalance = (buy−sell)/(buy+sell), taker-side |
| OI_5m_mean | Float64 | mean |B−S|/(B+S) over 5-min bins |
| OI_15m_mean | Float64 | mean |B−S|/(B+S) over 15-min bins |
| OI_1h_mean | Float64 | mean |B−S|/(B+S) over 1-hour bins |
| TS_full | Float64 | two-sidedness = 1 − |B−S|/(B+S), full window |
| TS_60m_mean | Float64 | mean TS over 60-min bins |
| PR_60m_median | Float64 | persistence ratio, 60-min window (median over bins) |
| PR_240m_median | Float64 | persistence ratio, 240-min window |
| VPIN_50 | Float64 | time-bucket VPIN approximation, N=50 buckets |
| kyle_lambda | Float64 | Kyle's λ from rolling OLS (raw, may have outliers) |
| kyle_lambda_winsorized | Float64 | kyle_lambda clipped to [p01, p99] |
| kyle_lambda_outlier | Boolean | True if outside [p01, p99] (496 markets) |
| hhi_flow_approx | Float64 | 1/n_makers (uniform flow concentration approximation) |
| SCI_balanced_60m | Float64 | SCI = PR·(1−TS)·(1−HHI), 60-min, equal weights |
| SCI_balanced_240m | Float64 | SCI, 240-min |
| SCI_persistence_60m | Float64 | SCI, persistence-weighted |
| SCI_persistence_240m | Float64 | SCI, persistence-weighted, 240-min |
| SCI_breadth_60m | Float64 | SCI, breadth-weighted |
| SCI_breadth_240m | Float64 | SCI, breadth-weighted, 240-min |

---

## per_market_ils.parquet

| Column | Type | Description |
|--------|------|-------------|
| token_id | Utf8 | ERC-1155 position token ID |
| condition_id | Utf8 | Polymarket condition ID (hex, from archive scan) |
| resolution_outcome | Int64 | 1=YES, 0=NO (from PMXT v2) |
| resolved_at_ts | Float64 | Unix timestamp of resolution |
| p_open | Float64 | first non-zero price in 5-min bins |
| p_res | Float64 | resolution price (1.0 or 0.0) |
| ILS_1h | Float64 | ILS at T_res − 1h anchor |
| ILS_6h | Float64 | ILS at T_res − 6h anchor |
| ILS_12h | Float64 | ILS at T_res − 12h anchor |
| ILS_24h | Float64 | ILS at T_res − 24h anchor |
| ILS_mean | Float64 | mean over available offsets |
| anchor_sensitivity | Float64 | max|ILS_i − ILS_j| over offset pairs |
| anchor_sensitivity_pass | Boolean | anchor_sensitivity < 0.20 |
| scope_pass | Boolean | |p_res − p_open| > 0.05 AND has resolution |

**ILS formula:** `ILS_Δ = (p_anchor(Δ) − p_open) / (p_res − p_open)`, clipped to [−0.5, 1.5].  
ILS = 1.0 means price was already at resolution level Δ before resolution. ILS = 0.0 means no pre-resolution information. ILS < 0 means price moved against final outcome.

---

## per_market_archetype_share.parquet

*(Generated after CC-015 A1 per-market-per-address re-processing)*

| Column | Type | Description |
|--------|------|-------------|
| token_id | Utf8 | market token ID |
| archetype | Utf8 | k-means archetype label |
| arch_notional | Float64 | total notional from this archetype in this market |
| arch_taker | Float64 | taker-side notional from this archetype |
| n_addresses | Int64 | unique addresses of this archetype in this market |
| volume_share | Float64 | arch_notional / market_total_notional |
| taker_share | Float64 | arch_taker / market_total_notional |

---

## cluster_microstructure_bilateral_real.json

*(Generated after Phase 6c re-run with real cluster_share from A1)*

```json
{
  "n_tests": 88,
  "n_sig_fdr": <int>,
  "archetypes": [...],
  "metrics": [...],
  "results": [
    {
      "archetype": "fill-MM",
      "metric": "PR_60m_median",
      "spearman_rho": <float>,
      "p_value": <float>,
      "bh_significant": <bool>,
      "mw_statistic": <float>,
      "mw_p_value": <float>,
      "bca_ci_lo": <float>,
      "bca_ci_hi": <float>,
      "n_markets": <int>
    },
    ...
  ]
}
```

---

## manipulation_patterns.json

| Key | Type | Description |
|-----|------|-------------|
| wash_volume_candidates | object | `count`, `status`, addresses with near-zero net position |
| book_depth_swings | object | `count`, markets with >10¢ mid-price moves |
| withdrawn_patterns | object | spoof/coordination patterns withdrawn (G-QUOTE-LIFE FAIL) |

---

## gate_report.json

Three-gate empirical verdict:
- `G-FILL`: PASS — all fills attributed via eth_getLogs
- `G-QUOTE-LIFE`: FAIL universal — off-chain CLOB
- `G-BOOK`: PASS partial — market-level best_bid/best_ask only
