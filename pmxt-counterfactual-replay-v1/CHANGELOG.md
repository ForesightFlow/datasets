# Changelog — pmxt-counterfactual-replay-v1

## v1.0 — 2026-05-10

Initial release.

- 6 parquet tables from E2 (CC-007b) and E3 (CC-008) simulation experiments
- `aggregates.json` — key summary statistics for quick reference
- `engine-parameters-v1.json` — locked engine/mechanic parameter definitions
- `build_manifest.json` — SHA-256 checksums for all data files
- E2 source: `evaluation/output/e2b/results.json`, generated 2026-05-08
- E3 source: `evaluation/output/e3/results.json`, generated 2026-05-09
- Markets: E2 n=13,306, E3 n=13,115 (eligibility filter: ≥10 resolved ticks)
