# Known Limitations — PMXT Behavioral Clusters v1

This document discloses all known data quality, methodological, and scope limitations of the `pmxt-behavioral-clusters-v1` dataset. Users of this dataset should read this document before drawing conclusions.

---

## 1. G-QUOTE-LIFE Universal Fail (Permanent)

**What this means:** OrderPlaced and OrderCancelled events are off-chain CLOB events on Polymarket's internal order book. They are not recorded on the Polygon blockchain, not in PMXT v2, and not available via any public subgraph for the observation window.

**Consequences:**
- Features f1 (quote intensity), f4 (two-sided ratio), f8 (spread provision at address level) are absent from the behavioral clustering vector.
- Address-level market-maker and liquidity-provider characterization via quote lifecycle is **not possible** from on-chain data alone.
- The archetype labels `fill-MM` and `fill-LP` are **fill-side proxies only** — they reflect fill-side behavioral patterns (trade frequency, market breadth, notional size) but do not confirm that an address posted or cancelled quotes.
- Spoof detection (post-without-fill) is withdrawn.
- This failure is permanent for the empirical window; it is not a contingent execution constraint that could be resolved with additional data collection.

---

## 2. DBSCAN Unimodality — k-means k=5 is Exploratory Fallback

**What this means:** The pre-registered primary clustering algorithm (DBSCAN) yielded a single density cluster across all 15 sensitivity configurations (ε ∈ [1.15, 3.44], MinPts ∈ {10, 20, 30}). HDBSCAN produced 49–213 clusters with 80–87% noise fraction and was rejected per the pre-registered noise threshold (>50% noise) and cluster-count cap (>20 clusters).

**Fallback:** k-means k=5 was selected as the pre-registered fallback (silhouette = 0.227 — weak partition by Rousseeuw convention).

**Consequences for this dataset:**
- The k-means k=5 partition is **exploratory and descriptive**, not a statistically validated archetype assignment.
- Silhouette = 0.227 indicates weak cluster separation; many addresses near cluster boundaries could plausibly belong to adjacent clusters.
- **The recommended primary participant stratification is the feature-tier classification** (`per_address_tiers.parquet`), which uses pre-registered percentile thresholds independent of clustering outcomes.
- The k-means partition and feature-tier classification are cross-tabulated in `tier_kmeans_crosstab.json` for comparison.

---

## 3. ILS Scope Coverage 14.9%

**What this means:** The resolution-anchored ILS (Informed Liquidity Score) requires (a) a market where the initial price and final resolution price differ by >5% (`|p_res − p_open| > 0.05`) and (b) a resolution outcome in PMXT v2.

**Coverage:** 6,406 / 43,116 markets (14.9%) pass both conditions. The remaining 85.1% either:
- Are not yet resolved as of the PMXT v2 snapshot used (most common — the 7-day window captures many markets that resolved after the collection date), or
- Were priced at extremes throughout the window (no meaningful price movement), or
- Are not present in PMXT v2 (some token_ids may correspond to ancillary positions).

**Consequence:** ILS statistics in `per_market_ils.parquet` apply only to the 6,406 scope-pass markets. Median ILS ≈ 0 across these markets reflects efficient pricing for the typical market; the mean (≈ 0.14) reflects a right-skewed distribution with a minority of markets exhibiting strong pre-resolution price informativeness.

---

## 4. Single-Week Scope

The empirical window is **2026-04-21 to 2026-04-27** (7 days). Results may not generalize to other periods. In particular:
- Market composition (sports vs. politics vs. crypto) varies week to week.
- Trading activity levels vary with news cycles and major events.
- No seasonality or week-of-month effects are controlled for.

---

## 5. Sports-Dominant Composition

The empirical window inherits the market composition documented in Paper 1 (CC-007 stylized facts): approximately **77.9% of active markets are sports prediction markets** (soccer, basketball, tennis, MMA). Non-sports categories (politics, crypto, culture) represent ~22.1%.

**Consequence:** Microstructure metrics (PR, TS, OI, VPIN, ILS) are dominated by sports market dynamics (short event lifecycles, binary resolution, binary pricing). Results should be interpreted in this context.

---

## 6. Address-Level Data Not Published (Privacy-by-Design)

Per-address behavioral data (`per_address_trades.parquet`, `cluster_labels.parquet` at address granularity) is **not included in this deposit**. This is an intentional privacy-by-design decision.

Addresses on Polymarket CTFExchange are pseudonymous (Polygon wallet addresses), but linking them to behavioral patterns could enable de-anonymization. The deposit contains only:
- Per-cluster aggregate statistics (centroids, CIs, notional shares)
- Per-tier aggregate statistics
- Per-market metrics (markets are public on Polymarket)
- Cross-tabulation of tiers vs. k-means clusters (counts only, no addresses)

---

## 7. CTFExchange Contract Excluded

The address `0x4bfb41d5b3570defd03c39a9a4d8de6bd8b8982e` (the CTFExchange smart contract itself) appears in the raw fill log with 4.57M fills and ~$200M notional — it is the exchange settlement contract, not a trader. This address is **explicitly excluded** from all behavioral analyses in this dataset.

The NEGRisk adapter (`0xe3f18acc55091e2c48d883fc8c8413319d4ab7b0`) was not active in the 2026-04-21 to 2026-04-27 window (0 fills). It is included in the exclusion list for code reproducibility.

---

## 8. `fill-MM` and `fill-LP` Labels are Fill-Side Proxies

The archetype labels applied to k-means clusters via the heuristic in `per_cluster_summary.json` are fill-side proxies derived from feature centroids:
- `fill-MM`: high intraday entropy (>2.5), very high market breadth (>4.0), symmetric direction — reflects MM-like fill behavior, not confirmed market-making.
- `fill-LP`: moderate-high per-fill notional, moderate breadth, symmetric — reflects LP-like fill behavior, not confirmed quote posting.
- `SPECIALIST`: very low intraday entropy (<1.0) — time-concentrated, single-market focus.
- `RETAIL`: low notional, directional.

Confirmed MM/LP identification requires OrderPlaced/OrderCancelled data (see Limitation #1).

---

## 9. Bilateral Analysis Limitation (Phase 6c)

The cluster-microstructure bilateral analysis (`cluster_microstructure_bilateral_real.json`) uses per-market archetype volume shares computed from the per-market-per-address attribution table. If the re-processing in CC-015 A1 does not complete before dataset deposit, the bilateral file from the initial run (ρ = 0 for all pairs, due to uniform approximation) is noted as a placeholder pending re-computation.

---

## 10. Kyle's λ Outliers

Raw Kyle's λ in `per_market_microstructure.parquet` has a mean of −2.04e+12 dominated by 496 markets with extreme OLS instability (thin market with few price changes but large net flow). The `kyle_lambda_winsorized` column (clipped at p01/p99) and `kyle_lambda_outlier` boolean flag are provided. Use `kyle_lambda_winsorized` (median = 0, trimmed mean = −0.001) for any distributional analysis.
