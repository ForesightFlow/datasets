# Changelog

## v1 (2026-05-09)

Initial release.

- 13,314 markets stratified-by-day from the PMXT v2 archive, week 2026-04-21 to 2026-04-27 UTC
- Stylized facts SF1–SF9 computed per market (where applicable) and as pooled / per-class aggregates
- SF1 (boundary depth asymmetry, ρ) and SF2 (terminal jump magnitude, |Δ|) confirmed against pre-registered floors
- SF9 H1/H2/H3 hypothesis-test refinements provided in `code/sf9_hypothesis_tests.ipynb` for reproducibility (not in headline data)

### Sample size note

The companion paper (CC-003.11 analysis, run ~2026-04-28) reports 13,298 markets using Goldsky UMA OO API data as of that date. This dataset's Path A build uses the local UMA cache (`~/.cache/elp/uma/primary/`, built 2026-05-07) which includes 15 additional markets that resolved after the CC-003 run. The 13,314 count is the reproducible output of Path A. All stylized-fact aggregate values are unchanged (the 15 extra markets lie within the sport/other/politics classes at their respective proportions; crypto count is identical at 1,518). Sports share of the three-class total remains 77.91%.

### Known limitations

- 23.1% of sample markets (3,077 / 13,314) lack a usable terminal-jump observation due to order-book illiquidity in the final hour before resolution; classification of these markets (genuine illiquidity vs computation gap) is deferred to v2
- Sports-dominance: 77.9% of three-class total, limiting per-class generalizability for politics and crypto
- Single-week empirical window
- SF1 per-market rho available only for 1,648 resume-pass markets; base-pass (4,030 markets) emitted aggregate-only
- SF4 boundary region (index < 0.10 and > 0.90) half-spread columns are null in v1; CC-004 per-market accumulator emitted only interior regions (low/mid/high)
- `tags` column contains string tag names from the Polymarket Gamma API, not numeric Polymarket canonical tag IDs

---

## Done

(empty — initial release)
