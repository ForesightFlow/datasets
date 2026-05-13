# Polymarket Per-Category Exponential Hazard Rates (v1)

Per-category exponential hazard fits for the time-to-event distribution on
Polymarket deadline-resolved contracts. Used as the baseline survival function
in the deadline-Information Leakage Score (ILS-dl) framework of the ForesightFlow
programme.

For each target category, this dataset publishes the maximum-likelihood estimator
of the hazard rate $\lambda$, its 95% confidence interval, half-life,
Kolmogorov--Smirnov adequacy test p-value, sample size, and the underlying
market IDs used in the fit. Researchers building on the ILS-dl framework can use
these fits directly as the survival baseline $S(\tau) = \exp(-\lambda \tau)$
without re-fitting from scratch.

## Quick stats

| Field | Value |
|---|---:|
| Categories fit | 4--7 (military_geopolitics, corporate_disclosure, regulatory_decision and subcategories, plus optional controls) |
| Sample period | 2022-12 -- 2026-04 |
| Snapshot date | 2026-04-30 |
| Taxonomy version | v1.1 (post-esports correction) |
| License | CC-BY 4.0 |

## Headline result: military_geopolitics

| Metric | Value |
|---|---:|
| n (Tier-3 markets with τ > 0) | 18 |
| λ̂ (events / day) | **0.241** |
| 95% CI for λ̂ | **[0.143, 0.365]** |
| Half-life (days) | **2.87** |
| KS p-value | **0.425** |
| KS verdict | adequate (exponential not rejected) |

The military_geopolitics fit supersedes the preliminary estimate reported in
Nechepurenko (2026), arXiv:2605.02286 (n=9, λ=0.306, half-life 2.3d). The
preliminary value lies inside the new 95% CI; both estimates are statistically
consistent. The change is driven by sample-size expansion from a Task-03 cap of
9 markets to the full Tier-3 population of 18 markets, not by the esports
taxonomy correction (which affected zero Tier-3 sample markets).

## Schema

Each record is a JSON object:

| Field | Type | Description |
|---|---|---|
| `category` | string | Target category from the ForesightFlow taxonomy |
| `subcategory` | string \| null | Sub-category split where applicable (e.g., `regulatory_decision_announcement` vs `regulatory_decision_formal`) |
| `sample_period_start` | string (ISO 8601) | Earliest resolution date in fit sample |
| `sample_period_end` | string (ISO 8601) | Latest resolution date in fit sample |
| `n_markets_fit` | integer | Number of markets used in MLE |
| `lambda_hat` | float | MLE point estimate (events / day) |
| `lambda_ci_low` | float | Lower bound of 95% CI |
| `lambda_ci_high` | float | Upper bound of 95% CI |
| `half_life_days` | float | $\ln(2) / \lambda$ |
| `ks_pvalue` | float | Kolmogorov--Smirnov test p-value vs fitted exponential |
| `ks_verdict` | string | `adequate`, `marginal`, or `rejected` |
| `exclusions` | array of strings | Markets or sub-populations excluded from fit, with rationale |
| `notes` | string | Methodological notes specific to this fit |

A companion file `sample_market_ids.jsonl` provides the per-fit list of market IDs
for full reproducibility.

## Methodology

**Sampling.** For each target category, we draw Tier-3-recovered T_event timestamps
from the [polymarket-tnews-tevent-recovery](../polymarket-tnews-tevent-recovery)
dataset and compute the lead time $\tau = T_{\text{event}} - T_{\text{open}}$
between market opening and the public event. Markets with $\tau \leq 0$ (events
that occurred before market opening) are excluded; this is a structural exclusion
because the canonical informed-trading window does not exist for such markets.

**Estimator.** The maximum-likelihood estimator for the exponential rate parameter
is $\hat{\lambda} = 1 / \bar{\tau}$. The 95% confidence interval is constructed
via the standard chi-square quantile relation:

$$\text{CI}_{95\%} = \left[\frac{\chi^2_{0.025, 2n}}{2 n \bar{\tau}}, \frac{\chi^2_{0.975, 2n}}{2 n \bar{\tau}}\right]$$

**Goodness of fit.** The Kolmogorov--Smirnov test compares the empirical CDF of
observed $\tau$ values against the fitted exponential CDF. We report the
two-sided p-value; verdicts follow:
- `adequate` (p > 0.10): exponential model not rejected
- `marginal` (0.05 < p ≤ 0.10): borderline; use with caution
- `rejected` (p ≤ 0.05): exponential model rejected; sub-categorization or
  alternative parametric family required

## Files

| File | Description | Size (approx) |
|---|---|---:|
| `data/hazard_rates_v1.json` | Per-category fit records, JSON | <10 KB |
| `data/hazard_rates_v1.csv` | Same data, CSV format | <5 KB |
| `data/sample_market_ids.jsonl` | Per-fit list of market IDs used (for reproducibility) | <50 KB |
| `figures/hazard_fits.svg` | Visual fits per category (empirical CDF + fitted exponential) | <100 KB |
| `MANIFEST.json` | SHA-256 hashes of all data files | <1 KB |

## Quick-start

```python
import json

with open("data/hazard_rates_v1.json") as f:
    fits = json.load(f)

# Survival function for military_geopolitics
import math
mg = next(f for f in fits if f["category"] == "military_geopolitics" and f["subcategory"] is None)
lam = mg["lambda_hat"]

def S(tau_days):
    """Survival function: probability event has not occurred by tau days after market open."""
    return math.exp(-lam * tau_days)

print(f"P(event by 1 day): {1 - S(1):.3f}")
print(f"P(event by half-life {mg['half_life_days']:.1f} days): {1 - S(mg['half_life_days']):.3f}")
```

## Citation

If you use these hazard fits in derived work, please cite the methodology paper
and the empirical paper jointly:

```bibtex
@misc{nechepurenko2026ils-framework,
  title  = {{ForesightFlow}: An Information Leakage Score Framework for Prediction Markets},
  author = {Nechepurenko, Maksym},
  year   = {2026},
  doi    = {10.48550/arXiv.2605.00493},
  url    = {https://arxiv.org/abs/2605.00493},
  note   = {SSRN Working Paper 6687361}
}

@misc{nechepurenko2026deadline-leakage,
  title  = {Empirical Evaluation of Deadline-Resolved Information Leakage on Documented {Polymarket} Insider Cases},
  author = {Nechepurenko, Maksym},
  year   = {2026},
  doi    = {10.48550/arXiv.2605.02286},
  url    = {https://arxiv.org/abs/2605.02286},
  note   = {SSRN Working Paper 6687398}
}
```

## Related datasets

- [`polymarket-tnews-tevent-recovery`](../polymarket-tnews-tevent-recovery) — Source
  of the T_event timestamps used to compute the $\tau$ values in this fit.
- [`polymarket-deadline-ils`](../polymarket-deadline-ils) — Consumes these hazard
  fits to produce hazard-adjusted ILS-dl scores for 88 markets.
- [`polymarket-ils-corpus`](../polymarket-ils-corpus) — Population-scale
  ILS scores that use these fits as the survival baseline.

## Versioning

- **v1** (2026-05-13) — Initial release. Post-esports-correction taxonomy. Full
  Tier-3 population.

## Versioning relationship with submitted papers

The numerical values in this dataset (military_geopolitics: λ=0.241, half-life
2.9d, KS p=0.425) **supersede** the preliminary v1 estimates published in:

- Nechepurenko (2026), arXiv:2605.00493 (Methodology paper)
- Nechepurenko (2026), arXiv:2605.02286 (Empirical paper)
- Nechepurenko (2026), arXiv:2605.02287 (Comparison paper)
- Nechepurenko (2026), SSRN 6687441 (Real-Time Detection monolith)

The previous estimates (n=9, λ=0.306, half-life 2.3d) lie inside the v1 95% CI and
are statistically consistent. v2 revisions of the above papers will update the
numerical values to match this dataset; the substantive conclusions of the papers
do not change.

## License

CC-BY 4.0 — see [`LICENSE`](LICENSE).

## Limitations

1. **Sample sizes remain modest.** Tier-3 LLM recovery is selective; even for the
   best-covered category (military_geopolitics) n is 18. CIs are correspondingly
   wide.

2. **Exponential assumption.** Empirical fit is adequate for military_geopolitics
   and corporate_disclosure. The unrefined regulatory_decision category is
   bimodal and rejects the exponential assumption; we publish sub-categorizations
   (announcement vs formal-deliberation) where the within-subcategory fit is
   adequate, but the parent-category fit should not be used.

3. **Post-correction taxonomy.** Esports markets have been excluded from
   `military_geopolitics` per the v1.1 taxonomy correction. Researchers replicating
   our methodology should apply the same correction or accept that pre-correction
   fits will give different λ̂.
