# Code: Rebuilding `pmxt-stylized-facts-v1`

This directory contains the code needed to reproduce the dataset from source data.

## Two paths

### Path A — use pre-computed CC-003.11 + CC-004 outputs (fast, ~5 min)

Requires:
- The project's Python environment (polars, httpx, pyarrow, pandas, numpy)
- Local Gamma and UMA metadata caches under `~/.cache/elp` (populated by prior CC-003 / CC-004 runs)

```bash
cd <project-root>
python datasets-staging/pmxt-stylized-facts-v1/code/build_dataset.py \
    --g5-input  evaluation/output/table_t_g5_stratified_70k.json \
    --sf-input  evaluation/output/sf_results_stratified_resume_merged.json \
    --sf9-input evaluation/output/sf9_refined.json \
    --archive-dir data/raw/primary_2026-04-21_2026-04-27 \
    --output-dir datasets-staging/pmxt-stylized-facts-v1/data
```

The script reconstructs the 13,298-market analysis sample from the aggregate cache parquet and local metadata caches (no API calls), then joins the SF per-market arrays and writes all four output files plus `build_manifest.json`.

### Path B — full rebuild from PMXT v2 archive (~15 h)

Path B requires the full PMXT v2 archive (168 × ~430 MB hourly Parquet files) and re-running the CC-003 and CC-004 pipelines from the companion repository. This dataset's `code/` does not duplicate that pipeline. See the Paper 1 reproducibility README at the companion repository root for full instructions.

## `sf9_hypothesis_tests.ipynb`

Reproduces the H1 (per-region), H2 (near-mid 50bps), and H3 (by-path-cohort) SF9 refinements from CC-006a. These results are NOT in the headline dataset; they are provided here for transparency.

Dependencies: `pandas`, `matplotlib`, `jupyter`. Source data: `evaluation/output/sf9_refined.json` (companion repository).

Run from the project root:
```bash
jupyter notebook datasets-staging/pmxt-stylized-facts-v1/code/sf9_hypothesis_tests.ipynb
```
