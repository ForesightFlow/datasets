# Datasheet: polymarket-deadline-ils

## Purpose and Scope

This dataset supports the empirical measurement of informed trading on Polymarket prediction markets using the Deadline-ILS (ILS^dl) metric introduced in ForesightFlow Paper 3a. ILS^dl quantifies what fraction of total price movement occurred before the underlying real-world event, operationalising the concept of information leakage in binary prediction markets.

## Contents

The dataset contains one row per Polymarket market, covering three categories (military_geopolitics, regulatory_decision, corporate_disclosure) with trading volume ≥ $50,000 USDC.

**Columns:**

| Column | Type | Description |
|---|---|---|
| market_id | str | Polymarket condition ID (0x hex) |
| question | str | Market question text |
| category | str | ForesightFlow category label |
| subcategory | str | Regulatory sub-type (for regulatory_decision) |
| resolution_type | str | `event_resolved` or `deadline_resolved` |
| period | str | `pre_2024` or `post_2024` |
| T_open | ISO datetime | Market creation timestamp (UTC) |
| T_event | ISO datetime | Recovered event timestamp (UTC); null if not recovered |
| T_event_confidence | float | LLM confidence in T_event date (0.0–1.0) |
| T_event_sources | int | Number of independent sources used |
| T_resolve | ISO datetime | Market resolution timestamp (UTC) |
| tau_days | float | Days between T_open and T_event |
| volume_usdc | float | Total trading volume in USDC |
| p_open | float | YES price at T_open (first trade within 24h) |
| p_event | float | YES price just before T_event |
| p_resolve | float | Resolution outcome (1.0 = YES, 0.0 = NO) |
| ils_dl | float | Deadline-ILS score; null if not computable |
| ils_dl_ci_low | float | Bootstrap CI lower bound (2.5th pct, B=500) |
| ils_dl_ci_high | float | Bootstrap CI upper bound (97.5th pct, B=500) |
| ils_dl_30min | float | ILS^dl using price 30 min before T_event |
| ils_dl_2h | float | ILS^dl using price 2 h before T_event |
| ils_dl_6h | float | ILS^dl using price 6 h before T_event |
| ils_dl_24h | float | ILS^dl using price 24 h before T_event |
| in_scope | bool | True if market met all quality filters |
| exclusion_reason | str | Reason for exclusion; empty if in_scope |
| expected_decay_price | float | Hazard-adjusted expected price at T_event under exponential decay (B2); null if not computed |
| ils_dl_adj | float | Hazard-adjusted ILS^dl (B2); null if not computed |
| b2_method | str | `exponential_decay` for markets with computed il_dl_adj; null otherwise |

## Composition

**Total rows**: 2,375  
**Markets with ILS^dl**: 88  
**Markets with T_event**: 442

### Attrition chain

| Stage | Remaining | Dropped | Reason |
|---|---|---|---|
| Initial (cat+vol≥50K) | 12,708 | — | — |
| Drop unclassifiable resolution | 2,375 | 10,333 | Unclassifiable markets |
| Deadline-NO out of scope | 1,151 | 1,224 | deadline_resolved + NO outcome |
| T_event confidence ≥ 0.7 | 442 | 709 | LLM could not recover event date |
| CLOB/trade price coverage | 358 | 84 | No historical price data |
| ILS^dl computed | 88 | 270 | Price gaps at T_event or T_open, edge effects (|p_open−0.5| ≥ 0.4), negative τ |

### Category breakdown (88 markets with ILS^dl)

| Category | n |
|---|---|
| regulatory_decision | 55 |
| military_geopolitics | 22 |
| corporate_disclosure | 11 |

### Period breakdown

| Period | n |
|---|---|
| post_2024 | 55 |
| pre_2024 | 33 |

## Data Collection and Processing

**T_event recovery pipeline**:
- Stage 1: Claude Haiku (claude-haiku-4-5-20251001), training knowledge only, ~$0.0005/market
- Stage 2: Claude Haiku + web_search tool, for Stage-1 nulls, ~$0.03/market
- Stage 3 (paper3a_phase1.py): Claude Sonnet 4.6 + web_search, for remaining nulls, ~$0.16/market
- Total T_event recovery cost: ~$49 USD for 3,027 recoveries

**Price data sources**:
- Primary: Polymarket CLOB API (1-minute OHLCV)
- Fallback: 1-minute VWAP synthesized from Polymarket subgraph trades (YES outcome, outcome_index=1)
- Markets from 2020–2021 largely lack CLOB coverage; subgraph trades used as fallback

**ILS^dl computation**:
- p_open: first price within 24h of T_open (forward window)
- p_event: nearest price within ±5 minutes of T_event
- Bootstrap CI: B=500 resamplings of the [T_open, T_event] trade window

## Data Quality

**Known issues:**
1. **Low coverage (3.7%)**: Only 88/2,375 markets have ILS^dl. The primary bottleneck is CLOB price data: pre-2022 markets lack API coverage, and 2022-2024 markets have sparse trade histories that do not always cover T_open or T_event windows. All 230 `ils_compute_error` markets fail with `PriceLookupError` (price gap at T_event or T_open window).
2. **LLM-recovered T_event dates**: T_event dates were recovered by Claude models and may contain errors. Confidence scores are provided; markets with confidence < 0.7 are excluded. Known failure modes: ambiguous "did-not-happen" markets, highly niche corporate events, and future-dated questions.
3. **Synthesized prices**: For markets without CLOB data, minute-level VWAP from subgraph trades is used as `mid_price`. This may differ from the true bid-ask midpoint, potentially biasing ILS^dl estimates.
4. **Category labels**: Assigned by rule-based classifier; no independently labelled held-out test set.
5. **Negative ILS^dl values**: The large negative mean (−0.515) and outliers (min −7.750) are consistent with markets where price moved away from the true outcome before the event. Some may reflect data quality issues rather than true informed trading in the wrong direction.
6. **FFIC localization gap**: Of 32 canonical informed-trading cases in the FFIC inventory, only 1 market (Bitcoin ETF approval, ILS^dl=0.012) has a computed score. The primary barrier is `resolution_type=unclassifiable` assigned by the typology classifier to key military/geopolitical markets (Iran Oct2024 strike, Maduro capture, Venezuela operations cluster). These markets are excluded before reaching the ILS^dl computation step. Improved typology classification is required before FFIC concordance testing is meaningful.
7. **Low anchor robustness**: Only 9–17% of ILS^dl scores are anchor-robust (sign-consistent and spread < 0.3 across pre-event window variants). Spearman correlation between the primary ILS^dl and the 24h-window variant ranges from 0.10 (corporate) to 0.36 (regulatory). This reflects genuine metric sensitivity to T_event precision and volatile pre-event price paths rather than a computation error.
8. **T_event second-pass validation (B1)**: A stratified second-pass re-recovery on 50 markets (12 regulatory_announcement, 18 regulatory_formal, 20 other) using Haiku+web_search yielded 57.8% exact date match and 68.9% within-24h agreement vs. pass-1 dates. The `regulatory_formal` sub-bucket showed the lowest agreement (35.7% exact), consistent with ambiguity between announcement date and effective/published date. Source URL overlap was 0% across passes, reflecting non-deterministic web search results rather than a systematic error.

## Limitations

- **Not a representative sample**: Only markets above $50K volume in three specific categories. Results cannot be generalised to the full Polymarket population.
- **Survivorship bias**: Analysis restricted to YES-resolved markets. NO-resolved markets may have different informed trading patterns.
- **Single methodology**: ILS^dl requires both a recoverable T_event and adequate price history. Markets failing either condition are excluded.
- **No ground-truth labels**: There is no independently verified ground truth for whether any specific market involved informed trading.

## Intended Use

- Empirical analysis of information leakage in prediction markets
- Calibration and validation of the ILS^dl metric against known cases
- Cross-category comparison of informed trading intensity

## Restrictions

This dataset must not be used:
- As sole evidence for legal or regulatory action against specific traders
- To identify or dox market participants (market_id refers to a contract, not a trader)
- As training data for models where ILS^dl is treated as a ground-truth label for "is informed trading"

## Accessibility and Licensing

**License**: CC-BY 4.0 (Creative Commons Attribution 4.0 International)  
**Repository**: https://github.com/ForesightFlow/datasets  
**Contact**: maksym@devnull.ae
