# Changelog

All notable changes to the Polymarket Resolution Typology Dataset are documented here.

The dataset follows append-only versioning: existing records are not modified except to correct factual errors. Each version is a frozen git tag.

---

## [1.0] — 2026-04-28

Initial release.

### Corpus

- 911,237 markets with `created_at_chain <= 2026-04-27T00:00:00Z`
- Date range: 2020-10-02 through 2026-04-26
- Total volume across corpus: approximately $59.8 B USDC

### Classification

- **Classifier version:** ForesightFlow Task 03 Phase 0 (April 2026 refinement)
- **Algorithm:** Rule-based keyword classifier in `fflow/scoring/resolution_type.py` (ForesightFlow platform repository)
- **Backfill:** Run in a single batch pass across all 911K markets, April 2026
- **Key heuristic:** Deadline pattern matching in question text ("by [date]", "before [date]", "on or before", etc.); description-only matches logged separately as lower-confidence
- **Structural validation:** 100% NO-resolution rate among deadline-classified markets in target categories at deadline expiry, consistent with correct classifier behaviour

### By resolution_type

| Type | Count |
|---|---|
| `unclassifiable` | 853,774 |
| `deadline_resolved` | 56,318 |
| `event_resolved` | 1,145 |

### Known limitations at release

- `event_resolved` recall is conservative: a substantial fraction of the actual event-resolved population is classified as `unclassifiable`.
- `unclassifiable` is a heterogeneous fallback class, not a homogeneous category.
- Category labels (`category_fflow`) reflect a keyword classifier optimised for three target categories; `other` is a residual class.
- See DATASHEET.md for full limitations documentation.

### Files

- `data/typology-v1.jsonl.gz` — 90.1 MB gzipped JSONL
- `data/typology-v1.parquet` — 152.6 MB Parquet (Snappy compression)

### Companion materials

- Companion paper: Nechepurenko (2026), *ForesightFlow*, working draft v1.0
- Platform code: [github.com/ForesightFlow/platform](https://github.com/ForesightFlow/platform)
