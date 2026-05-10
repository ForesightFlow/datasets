# Datasheet — pmxt-counterfactual-replay-v1

Following Gebru et al. (2021), "Datasheets for Datasets."

---

## Motivation

**For what purpose was the dataset created?**
To provide a reproducible, publicly archived summary of two counterfactual simulation experiments (E2 and E3) conducted as part of the empirical risk-design study for event-linked perpetual futures on Polymarket binary markets. The dataset enables third-party replication of the key quantitative findings reported in Nechepurenko (2026) Paper 1 without requiring access to the raw tick archive (~168 GB).

**Who created the dataset and on behalf of which entity?**
Maksym Nechepurenko, Devnull FZCO, 2026.

**Who funded the creation?**
Self-funded research.

---

## Composition

**What do the instances represent?**
Each row in the parquet files represents aggregated simulation statistics for a specific combination of: engine or mechanic variant, leverage multiplier, and market class (crypto / politics / sports / other / all-pooled).

**How many instances are there?**
- E2a survivability table: 75 rows (3 engines × 5 leverages × 5 classes)
- E2b drawdown table: 15 rows (3 engines × 5 classes)
- E2c PnL distribution table: 3 rows (3 engines)
- E3 liquidation rate, bad-debt, PnL tables: 80 rows each (4 mechanics × 4 leverages × 5 classes)

**Does the dataset contain all possible instances or a sample?**
This dataset contains aggregated summaries derived from the full eligible resolved-market population (E2: 13,306 markets; E3: 13,115 markets) meeting quality filters (≥10 resolved tick observations, non-null outcome). No sampling was applied beyond the quality filter.

**What data does each instance consist of?**
Numeric rates or amounts (float64): survivability/liquidation rates (fraction in [0,1]), drawdown totals (USDC), PnL percentiles/averages (USDC), bad-debt frequencies (fraction in [0,1]).

**Is there a label or target associated with each instance?**
No supervised labels. The grouping columns (engine/mechanic, leverage, class) serve as indices.

**Is any information missing from individual instances?**
No missing values. Classes with zero markets in a cell retain zero rates.

**Are relationships between instances made explicit?**
Yes — by the shared (engine/mechanic, leverage, class) index. The `aggregates.json` file provides cross-table summaries.

**Are there any errors, sources of noise, or redundancies?**
- Tick data sourced from Polymarket's on-chain CLOB. Price gaps at resolution boundary are treated as oracle settlement. See companion paper for discussion of bid/ask spread approximation.
- E2 and E3 use overlapping but not identical market sets (13,306 vs 13,115) due to slightly different eligibility filters.

**Is the dataset self-contained or does it rely on external resources?**
Self-contained. Raw tick data is not included (size: ~168 GB). Aggregated outputs are complete without external resources.

**Does the dataset contain data that might be considered confidential?**
No. All data is derived from public Polymarket on-chain state.

**Does the dataset contain data that might be considered offensive?**
No.

---

## Collection Process

**How was the data collected?**
Raw tick data was collected from Polymarket's Gamma API and on-chain CLOB event stream. Stylized-fact measurements (SF1–SF9) were computed on the resolved-market subset. Counterfactual simulations were run deterministically using fixed random seeds and a fixed position notional (1000 USDC).

**Who was involved in data collection and how were they compensated?**
Maksym Nechepurenko (self-funded researcher).

**Over what timeframe was the data collected?**
Market tick data: 2020–2026-04-27. Simulation experiments run 2026-05-08 (E2) and 2026-05-09 (E3).

---

## Preprocessing / Cleaning / Labeling

**Was any preprocessing done?**
Yes:
- Markets with fewer than 10 resolved tick observations excluded.
- Post-resolution ticks trimmed before E3 simulation.
- Tick-level bid/ask spread approximated as symmetric around mid-price.
- Vol EMA initialized at zero; first 200 ticks are warm-up period.

**Is the software used to preprocess/clean/label available?**
Yes — `ForesightFlow/event-linked-perps` (MIT license), specifically `evaluation/counterfactual_replay.py` (E2) and `evaluation/resolution_zone_test.py` (E3). Build script: `evaluation/build_bundle2.py`.

---

## Uses

**Has the dataset been used for any tasks?**
Yes — as the empirical basis for Paper 1 (Nechepurenko 2026), which proposes and evaluates event-linked perpetual futures on binary prediction markets.

**What other tasks could the dataset be used for?**
- Comparing margin design choices for prediction-market derivatives.
- Benchmarking resolution-zone protocols against observed market data.
- Studying leverage-dependent liquidation dynamics in binary markets.

**Are there tasks for which the dataset should not be used?**
This dataset contains aggregate statistics, not individual trader positions or PII. It should not be used to infer individual market participant behavior.

---

## Distribution

**How will the dataset be distributed?**
Via `ForesightFlow/datasets` GitHub repository under the tag `pmxt-counterfactual-replay-v1`.

**When will the dataset be distributed?**
2026-05-10.

**Under what license is it distributed?**
CC-BY 4.0. See `LICENSE`.

**Have any third parties imposed IP-based restrictions?**
No. Source data (Polymarket CLOB events) is public on-chain data.

---

## Maintenance

**Who is supporting or maintaining the dataset?**
Maksym Nechepurenko / Devnull FZCO.

**How can the owner/curator be contacted?**
Via issues on `ForesightFlow/datasets` GitHub repository.

**Will the dataset be updated?**
This is a versioned snapshot (`v1`). A `v2` would be created for any material change to the simulation methodology or source data window.

**Will older versions be retained?**
Yes, via git tags.

**If others want to extend or augment the dataset, is there a mechanism?**
Open a pull request on `ForesightFlow/datasets` following the dataset contribution guidelines in the top-level README.
