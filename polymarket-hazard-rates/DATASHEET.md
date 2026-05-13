# Datasheet: Polymarket Per-Category Exponential Hazard Rates (v1)

Following [Gebru et al. (2021), "Datasheets for Datasets"](https://arxiv.org/abs/1803.09010).

## Motivation

**For what purpose was the dataset created?**
The dataset publishes the per-category exponential hazard rate fits used as the
survival baseline in the deadline-Information Leakage Score (ILS-dl) framework.
Prior published work on Polymarket informed-trading detection used these fits
internally but did not release the parameter estimates, confidence intervals, or
underlying samples. Independent researchers wishing to replicate or build on the
ILS-dl methodology need these fits, and the dataset closes that gap.

**Who created the dataset and on behalf of which entity?**
Maksym Nechepurenko / Devnull FZCO.

**Who funded the creation of the dataset?**
Devnull FZCO internal research budget.

## Composition

**What do the instances that comprise the dataset represent?**
Each instance is a per-category exponential hazard fit, consisting of:
- The MLE estimate λ̂ (events per day)
- 95% CI bounds
- Half-life
- KS goodness-of-fit p-value and verdict
- Sample size, period, and exclusion criteria
- The list of market IDs used in the fit

**How many instances are there?**
Approximately 4--7 records (one per target category, with sub-categorization for
regulatory_decision). Final count documented in the data file.

**Does the dataset contain all possible instances or is it a sample?**
Each record represents a fit on a specific sample drawn from our Tier-3 T_event
recovery dataset. The fits are computed once per snapshot date; future snapshots
will produce additional records.

**What data does each instance consist of?**
Structured numerical and categorical fields (see README schema). No raw market
data, no trade data, no wallet data.

**Is there a label or target associated with each instance?**
The target is the hazard rate parameter itself; the dataset is the result of an
estimation procedure rather than a labeled training set.

**Is any information missing from individual instances?**
Sub-category fits may be marked `null` for the parent-category fit if the parent
category was rejected by the KS test and only sub-categorizations are reported.

**Are relationships between individual instances made explicit?**
Yes: sub-category fits reference the parent category via the `category` field.

**Are there recommended data splits?**
Not applicable.

**Are there any errors, sources of noise, or redundancies in the dataset?**
The estimator and CI assume the exponential family is the correct parametric form.
The KS test verifies adequacy at the 0.05 significance level. Where the KS test
rejects the exponential family, the fit is not published; sub-categorizations are
attempted instead.

**Is the dataset self-contained, or does it link to or rely on external resources?**
The fits depend on the Tier-3 T_event timestamps published in the companion
[polymarket-tnews-tevent-recovery](../polymarket-tnews-tevent-recovery) dataset.

**Does the dataset contain confidential or restricted information?**
No.

**Does the dataset contain data that might be considered sensitive in any way?**
No.

## Collection process

**How was the data associated with each instance acquired?**
- T_event timestamps drawn from the [polymarket-tnews-tevent-recovery](../polymarket-tnews-tevent-recovery)
  dataset (Tier 3 LLM-verified subset)
- Market metadata (T_open, category) drawn from the ForesightFlow platform database
- MLE and KS test computed in-process via SciPy

**What mechanisms or procedures were used to collect the data?**
Custom Python scripts implementing the MLE estimator and KS test. Code in the
ForesightFlow platform repository.

**Over what timeframe was the data collected?**
2026-04 -- 2026-05. Fits computed on the v1.1 (post-esports-correction) database
snapshot of 2026-04-30.

**Were any ethical review processes conducted?**
No human subjects involved. No formal review needed.

## Preprocessing / cleaning / labeling

**Was any preprocessing/cleaning/labeling of the data done?**
- Markets with τ ≤ 0 excluded (structural exclusion).
- Markets without Tier-3 T_event timestamps excluded.
- Esports markets excluded from military_geopolitics per v1.1 taxonomy correction.
- For regulatory_decision: parent-category fit rejected by KS test, so reported
  only as sub-categorizations.

**Was the "raw" data saved in addition to the preprocessed/cleaned/labeled data?**
The raw T_event timestamps and market metadata are in companion datasets and the
platform database.

**Is the software used to preprocess/clean/label the data available?**
Yes, in the ForesightFlow platform repository.

## Uses

**Has the dataset been used for any tasks already?**
Yes. Hazard fits are used in the deadline-ILS computations for the
[polymarket-deadline-ils](../polymarket-deadline-ils) dataset (88 markets with
hazard-adjusted scores). The fits are also cited in the methodology and empirical
papers in the ForesightFlow programme.

**What (other) tasks could the dataset be used for?**
- Survival analysis on event-time prediction-market data
- Calibration of alternative parametric families (e.g., Weibull, log-normal)
- Cross-platform comparisons (e.g., fitting analogous rates on Kalshi or PredictIt
  data, where available)

**Is there anything about the composition of the dataset or the way it was collected
and preprocessed/cleaned/labeled that might impact future uses?**
The exponential assumption is parsimonious but limits the fits to settings where it
is empirically adequate. Researchers preferring a more flexible family should
re-fit using the sample market IDs provided.

**Are there tasks for which the dataset should not be used?**
The fits should not be applied to non-Polymarket prediction markets without first
verifying that the underlying lead-time distribution is comparable.

## Distribution

**Will the dataset be distributed to third parties outside of the entity on behalf
of which the dataset was created?**
Yes. Released openly via [github.com/ForesightFlow/datasets](https://github.com/ForesightFlow/datasets).

**How will the dataset be distributed?**
Git repository, CC-BY 4.0 license. JSON and CSV formats. SHA-256 manifest.

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
Yes. As the T_event recovery corpus grows, hazard fits will be re-computed and
released as v2, v3, etc. Sample-size growth will tighten confidence intervals.

**If others want to extend/augment/build on/contribute to the dataset, is there a
mechanism for them to do so?**
Pull requests welcome at github.com/ForesightFlow/datasets.
