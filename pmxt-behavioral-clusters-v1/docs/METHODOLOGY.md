# Methodology — PMXT Behavioral Clusters v1

This document describes the methodology used to produce the `pmxt-behavioral-clusters-v1` dataset. For full details, see Paper 4 of the Event-Linked Perpetuals research programme (Nechepurenko 2026).

---

## 1. Data Collection

**Source:** Polymarket CTFExchange smart contract on Polygon mainnet.  
**Contract:** `0x4bfb41d5b3570defd03c39a9a4d8de6bd8b8982e`  
**Event:** `OrderFilled(bytes32 orderHash, address maker, address taker, bytes32 makerAssetId, bytes32 takerAssetId, uint256 makerAmountFilled, uint256 takerAmountFilled, bytes32 fee)`  
**Method:** `eth_getLogs` streaming, 200-block pages, Polygon archive node (drpc.org / quiknode / 1rpc.io)  
**Period:** 2026-04-21 00:00 UTC – 2026-04-27 23:59 UTC  
**Block range:** 86,008,447 – 86,107,178 (98,732 blocks)  
**Total fills:** 13,356,931

**Price computation:** For binary YES/NO markets, `price = maker_amount / taker_amount` if maker pays USDC (maker_asset_id = 0), else `price = taker_amount / maker_amount`. Clipped to [0.001, 0.999] for logit transforms.

**Taker-side convention:** Order flow imbalance, VPIN, OFI, and market volume metrics use the **taker-side (aggressor)** only. This avoids double-counting (a single fill has exactly one taker and one maker — counting both would set buy = sell for every market by construction). Maker-side data is included in the per-market-per-address table for completeness.

**Excluded addresses:**
- `0x4bfb41d5b3570defd03c39a9a4d8de6bd8b8982e` — CTFExchange contract (exchange settlement, not a trader)
- `0xe3f18acc55091e2c48d883fc8c8413319d4ab7b0` — NEGRisk adapter (0 fills in window; documented for reproducibility)

---

## 2. Feature Engineering

Features computed from per-address fill aggregates over the 7-day window:

| Feature | Formula |
|---------|---------|
| f2 — log_trade_intensity | log1p(total_fills / active_hours) |
| f3 — log_avg_notional | log10(mean_USDC_notional_per_fill) |
| f5 — directional_ratio | (buy_notional − sell_notional) / (buy_notional + sell_notional) ∈ [−1, 1] |
| f6 — market_hhi | Σ(volume_in_market_i / total_volume)² — Herfindahl concentration |
| f7 — intraday_entropy | Shannon entropy H = −Σ p_h log(p_h) over 24 hour bins |
| f9 — log_market_breadth | log(n_unique_markets + 1) |

Preprocessing: winsorize p99.5 per feature, then StandardScaler (zero mean, unit variance).

Features f1 (quote_intensity), f4 (two-sided_ratio), f8 (spread_provision) are **absent** — they require off-chain CLOB data (OrderPlaced/OrderCancelled) not available on Polygon (see KNOWN_LIMITATIONS §1).

---

## 3. Clustering

**Algorithm:** DBSCAN (primary, pre-registered) → HDBSCAN → k-means (fallback cascade).

DBSCAN with 15 configurations (ε ∈ {1.15, 1.60, 2.29, 2.98, 3.44} × MinPts ∈ {10, 20, 30}) yielded 1 cluster across all configurations (noise < 0.2%). HDBSCAN with 9 configurations (min_cluster_size ∈ {25, 40, 60} × min_samples ∈ {5, 10, 15}) produced 49–213 clusters with 80–87% noise fraction — rejected per pre-registered thresholds (>50% noise, >20 clusters). **k-means k=5** selected as fallback (silhouette = 0.227, best across k ∈ {3,4,5,6,7}).

Seeds: 20260505 (clustering), 20260505+cluster_id+1000 (bootstrap CI).

---

## 4. Feature-Tier Classification

Percentile-based tiers computed on cleaned per_address_trades (after exchange exclusion):

| Tier | Threshold | N | % Addresses | % Notional |
|------|-----------|---|-------------|------------|
| whale-tier | notional ≥ $1M | 68 | 0.1% | 28.0% |
| high-frequency-operator | f2 ≥ P95 AND f9 ≥ P75 | 2,952 | 3.8% | 23.5% |
| high-breadth-operator | f9 ≥ P95 | 2,025 | 2.6% | 1.1% |
| power-trader | f2 ≥ P75 AND notional ≥ P75 | 6,738 | 8.7% | 29.9% |
| active-retail | residual | 2,062 | 2.7% | 10.6% |
| episodic-retail | notional < $10K | 63,358 | 82.1% | 6.8% |

Primary thresholds (P95 intensity / P95 breadth for top tiers) chosen based on pre-registration. Sensitivity analysis at P90/P99 variants reported in `tier_sensitivity.json`.

**Whale-tier overlay:** `whale_tier_overlay` boolean is orthogonal — any address with notional ≥ $1M gets this flag regardless of tier. 68 addresses (0.1%) hold 28% of total notional.

---

## 5. Microstructure Metrics

All computed per market from 5-minute bins in `per_market_stats.parquet`:

**Persistence Ratio (PR):**  
`PR_w = median(|ℓ_t − ℓ_{t−w}| / Σ|Δℓ|)` over all windows, logit returns `ℓ_t = log(p_t / (1−p_t))`.

**Two-sidedness (TS):**  
`TS = 1 − |B−S| / (B+S)` where B, S are taker-side buy/sell notional.

**Order Imbalance (OI):**  
Mean `|B−S|/(B+S)` over bins of width 5 min, 15 min, 1 hour.

**VPIN:**  
Time-bucket approximation with N=50 buckets: `VPIN = mean(|B_i − S_i|) / (B_i + S_i)`.

**Kyle's λ:**  
Coefficient from rolling OLS: `ΔP_t = λ · (B_t − S_t) / (B_t + S_t) + ε_t`, 60-min rolling window. Winsorized at [p01, p99] for analysis (496 thin-market outliers flagged).

**SCI (Structured Complexity Index):**  
`SCI = PR · (1 − TS) · (1 − HHI^flow)` in 3 weight schemes × 2 windows.

**ILS (Informed Liquidity Score):**  
`ILS_Δ = (p_anchor − p_open) / (p_res − p_open)`, clipped [−0.5, 1.5].  
Anchor = last price in 5-min bins before T_res − Δ. Δ ∈ {1h, 6h, 12h, 24h}.  
join path: token_id (decimal) → condition_id (archive scan) → PMXT v2 resolution.

---

## 6. Bilateral Analysis

Spearman ρ between per-market archetype volume share and per-market microstructure metrics. BH-FDR correction at α = 0.05. Mann-Whitney U test (markets with above-median vs. below-median archetype share). BCa 95% CI (B = 2,000 bootstrap resamples).

88 tests = 4 archetypes × 22 metrics. Real cluster shares computed from per-market-per-address attribution (CC-015 A1).

---

## 7. Reproducibility

All parameters locked:
- Clustering seed: 20260505
- Bootstrap seed: 20260505 + cluster_id + 1000
- BCa seed: 20260505
- Winsorize: p99.5 per feature
- ILS scope: |p_res − p_open| > 0.05
- VPIN buckets: 50
- Kyle λ rolling window: 60 min

Code: `evaluation/paper4/` in [github.com/ForesightFlow/event-linked-perps](https://github.com/ForesightFlow/event-linked-perps)  
Commit hash: see `manifests/code_manifest.json`
