# Datasheet: Polymarket ILS Corpus (v1)

Following [Gebru et al. (2021), "Datasheets for Datasets"](https://arxiv.org/abs/1803.09010).

## Motivation

**For what purpose was the dataset created?**
The dataset publishes the population-scale Information Leakage Score (ILS) corpus
underlying the empirical claims in the ForesightFlow programme. Prior published work
cited individual ILS values for case-study markets but did not release the broader
corpus. Researchers wishing to evaluate scope-condition filter rates, the distribution
of ILS across categories, or alternative screening thresholds need the underlying
corpus.

This dataset differs from `polymarket-deadline-ils-v3` (88 markets, event-anchored,
bootstrap CIs) in scope and depth: it is broader (all resolved markets with sufficient
price coverage in our DB) but uses a structural resolution proxy (`t_resolve − 24h`)
as the anchor for 99.9% of records. It is appropriate for population-level screening;
for precise event-anchored analysis use `polymarket-deadline-ils-v3`.

**Who created the dataset and on behalf of which entity?**
Maksym Nechepurenko / Devnull FZCO.

**Who funded the creation of the dataset?**
Devnull FZCO internal research budget.

## Composition

**What do the instances that comprise the dataset represent?**
Each instance is one resolved Polymarket market with a computed ILS anchored at
`t_news` (= `t_resolve − 24h` for 99.9% of records; independently recovered
$T_{\text{event}}$ for 5 records). Metadata includes price trajectory at key
timestamps, multi-window ILS variants, scope-condition flags, and an aggregate
wallet concentration measure.

**How many instances are there?**
4,801 markets total.

| Anchor type | Count | Description |
|---|---:|---|
| `proxy_24h` | 4,796 | `t_news = t_resolve − 24h`; structural proxy |
| `event` | 5 | Independently recovered $T_{\text{event}}$ (gap ≠ 24h) |

**Does the dataset contain all possible instances or is it a sample?**
All markets in the ForesightFlow DB as of 2026-04-30 that satisfy:
- Resolved binary market (YES/NO outcome)
- Price data sufficient to compute ILS
- Non-null `p_open` and `p_resolve`

An additional 4,940 rows exist in `market_labels` but have `ils IS NULL` (typically
because `|delta_total| < ε`). These are excluded from v1; their exclusion is a
data quality rather than a selection criterion.

**What data does each instance consist of?**
Structured fields (see README schema): market IDs, timestamps (t_open, t_news,
t_resolve), prices at three key timestamps, ILS in six window variants, scope-
condition flags, aggregate wallet concentration measure. No raw trade data.
No wallet addresses.

**Is there a label or target associated with each instance?**
The ILS value is the primary computed quantity. No ground-truth informed-trading
label is available for individual markets.

**Is any information missing from individual instances?**
- `wallet_hhi_top10` is null for 3,410 of 4,801 markets (71.0%) — trade-level
  aggregation requires indexed trades.
- `ils_7d` is null for ~2,369 markets where `t_open` falls within 7 days of
  `t_news` (flagged `window_7d_predates_topen`).
- Short-window variants (`ils_30min`, `ils_2h`) may be null for markets with
  sparse CLOB coverage near the anchor.

**Are relationships between individual instances made explicit?**
Markets sharing the same `fflow_category` can be analyzed jointly. No explicit
cluster IDs link markets sharing underlying events.

**Are there recommended data splits?**
- Full corpus (4,801 records): population-level screening analyses.
- `clean_scope_subset.jsonl` (2,548 records, `scope_all_pass = true`):
  hypothesis tests on informed-flow signatures.
- `event_anchored_subset.jsonl` (5 records): analyses requiring true event-anchoring.

**Are there any errors, sources of noise, or redundancies in the dataset?**
- For 1,406 of 4,796 proxy markets, a GDELT article was recovered with a timestamp
  coinciding exactly with `t_resolve − 24h`. The GDELT timestamp is a real news
  article time, but it is indistinguishable from the structural proxy. The causal
  direction — whether GDELT coverage precedes or causes the 24h resolution lag —
  is not resolved.
- For the 5 event-anchored records, the anchor is independently recovered via GDELT
  (tier2) or LLM (tier3) with gaps ranging from 42h to 3,477h.
- 273 esports markets are included. For these markets, event occurrence and resolution
  coincide (match completion = resolution trigger); ILS values may reflect structural
  convergence rather than informed trading.

**Is the dataset self-contained, or does it link to or rely on external resources?**
Self-contained for analyses using the provided columns. T_event provenance for the
5 event-anchored markets is documented in `anchor_tier`; full source citations are
in the companion
[polymarket-tnews-tevent-recovery](../polymarket-tnews-tevent-recovery) dataset.

**Does the dataset contain confidential or restricted information?**
No.

**Does the dataset contain data that might be considered sensitive in any way?**
**Wallet privacy:** `wallet_hhi_top10` is an aggregate concentration measure
(sum of squared shares of top-10 wallets). Individual wallet addresses are NOT
included. Wallet prefixes are NOT included. The HHI value alone does not identify
any individual trader.

## Collection process

**How was the data associated with each instance acquired?**
- Market metadata from Polymarket subgraph (The Graph network)
- `t_news` anchor: `t_resolve − 24h` for proxy markets; GDELT (tier2) or LLM
  (tier3) recovered for 5 event-anchored markets
- Price trajectories from CLOB price reconstruction in the ForesightFlow platform
- ILS computation via the ForesightFlow scoring engine
- HHI computation on trade-window aggregations from the `trades` table

**What mechanisms or procedures were used to collect the data?**
ForesightFlow platform pipelines
([github.com/ForesightFlow/platform](https://github.com/ForesightFlow/platform)).

**Over what timeframe was the data collected?**
Data ingestion: 2024-09 — 2026-04. ILS computation pipeline: 2026-04 — 2026-05.

**Were any ethical review processes conducted?**
No human subjects. No formal review needed. All data is publicly observable
on-chain state.

## Preprocessing / cleaning / labeling

**Was any preprocessing/cleaning/labeling of the data done?**
- Timestamp normalization to UTC ISO 8601.
- Category labels via ForesightFlow taxonomy v1.1 (post-esports correction).
- `anchor_type` and `t_news_gap_hours` columns computed from `t_resolve − t_news`.
- Scope conditions evaluated per record (retained regardless of pass/fail).
- `time_to_news_top10` (per-wallet timing data) excluded from published schema for
  privacy reasons.

**Was the "raw" data saved in addition to the preprocessed/cleaned/labeled data?**
Yes, in the platform database (`market_labels`, `markets`, `news_timestamps` tables).

**Is the software used to preprocess/clean/label the data available?**
Yes, at [github.com/ForesightFlow/platform](https://github.com/ForesightFlow/platform).

## Uses

**Has the dataset been used for any tasks already?**
Used internally in the analyses underlying:
- Nechepurenko (2026), "Information Leakage at Population Scale," arXiv:2605.00459
- Nechepurenko (2026), "ForesightFlow: An ILS Framework," arXiv:2605.00493
- Nechepurenko (2026), "Per-Market ILS and Order-Flow Skill," arXiv:2605.02287

**What (other) tasks could the dataset be used for?**
- Population-level informed-trading screening on Polymarket
- Replication of scope-condition filter rates and ILS distributions
- Category-level comparison of pre-resolution drift patterns
- Cross-platform comparison (re-computing resolution-proxy ILS on other venues)
- Benchmarking alternative anchor strategies against the 5 event-anchored records

**Is there anything about the composition of the dataset or the way it was
collected and preprocessed/cleaned/labeled that might impact future uses?**
- The proxy anchor (`t_resolve − 24h`) systematically conflates pre-event
  informed trading with resolution convergence. Positive ILS values should not be
  interpreted as evidence of informed trading without corroborating evidence.
- HHI is sparse (29% coverage) and settlement-window-biased for most markets.
- Esports markets (273) have structural coincidence of event and resolution.

**Are there tasks for which the dataset should not be used?**
- Should NOT be used to make definitive claims about informed trading in individual
  markets based solely on proxy-anchored ILS — the anchor is not the public event.
- Should NOT be used to validate LLM timestamp-recovery methods (circular use of
  Tier-3 records).
- Should NOT be used to make claims about specific wallet behavior; HHI is aggregate
  only.

## Distribution

**Will the dataset be distributed to third parties outside of the entity on behalf
of which the dataset was created?**
Yes. Open release via [github.com/ForesightFlow/datasets](https://github.com/ForesightFlow/datasets).

**How will the dataset be distributed?**
Git repository. Parquet primary, JSONL gzip alternative. CC-BY 4.0.

**Will the dataset be distributed under a copyright or other intellectual property
(IP) license, and/or under applicable terms of use (ToU)?**
CC-BY 4.0.

**Have any third parties imposed IP-based or other restrictions on the data
associated with the instances?**
No.

## Maintenance

**Who will be supporting/hosting/maintaining the dataset?**
Maksym Nechepurenko / Devnull FZCO.

**How can the owner/curator/manager of the dataset be contacted?**
- Email: maksym@devnull.ae
- GitHub Issues: [github.com/ForesightFlow/datasets/issues](https://github.com/ForesightFlow/datasets/issues)

**Will the dataset be updated?**
Yes. As genuine T_event recovery expands via Tier-3 LLM recovery, v2 will increase
the event-anchored fraction. Schema revisions trigger a version bump.

**If others want to extend/augment/build on/contribute to the dataset, is there a
mechanism for them to do so?**
Pull requests welcome at [github.com/ForesightFlow/datasets](https://github.com/ForesightFlow/datasets).
