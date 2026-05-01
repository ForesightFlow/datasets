# Polymarket Resolution Typology Dataset

A three-class classification of 911,237 Polymarket markets by resolution mechanism, released as a methodological resource for research on prediction-market structure and informed-trading detection.

**Version:** 1.0  
**Tag:** `polymarket-resolution-typology-v1`  
**License:** CC-BY 4.0  
**Companion paper:** Nechepurenko (2026), *ForesightFlow: Real-Time Detection of Informed Trading in Decentralized Prediction Markets*

---

## Why this dataset exists

Applying information-based microstructure models to prediction markets — in particular, computing the Information Leakage Score (ILS) defined in the companion paper — requires knowing how each market resolves. Markets that resolve against a deadline ("Will event X occur by date Y?") behave structurally differently from markets that resolve against a reported outcome ("Did event X happen?"). The two classes require different reference timestamps (T_event vs. T_resolve), different baseline assumptions, and different interpretations of pre-event price drift.

No public classification of Polymarket markets by resolution mechanism existed prior to this release. Every research group working with Polymarket data has had to re-derive this classification from scratch, typically using informal keyword heuristics that are neither documented nor reproducible. This dataset provides the ForesightFlow classification — a systematic, documented keyword classifier applied to the full corpus — as a shared baseline that other researchers can evaluate, correct, and build on.

Beyond ILS-based analysis, the resolution typology is useful for any study that treats deadline-resolved markets differently from event-resolved ones: studies of crowd forecasting accuracy, prediction-market calibration, deadline effects on liquidity, or market design.

---

## What the dataset contains

The dataset covers 911,237 Polymarket markets created on or before 2026-04-27, spanning the platform's history from October 2020 through April 2026. Each record captures the resolution classification alongside the market metadata needed to reproduce or extend the analysis.

### Counts by resolution type

| resolution_type | Count | Share |
|---|---|---|
| `unclassifiable` | 853,774 | 93.7% |
| `deadline_resolved` | 56,318 | 6.2% |
| `event_resolved` | 1,145 | 0.1% |

### Counts by category

| category_fflow | Count | Share |
|---|---|---|
| `other` | 771,424 | 84.7% |
| `regulatory_decision` | 71,588 | 7.9% |
| `military_geopolitics` | 47,580 | 5.2% |
| `corporate_disclosure` | 20,645 | 2.3% |

### Corpus summary

| Attribute | Value |
|---|---|
| Total records | 911,237 |
| Date range (created_at) | 2020-10-02 — 2026-04-26 |
| Total volume (all markets) | ~$59.8 B USDC |
| Snapshot cutoff | 2026-04-27T00:00:00Z |
| Formats | JSONL (gzipped), Parquet |

---

## Schema

Each record contains the following fields:

| Field | Type | Description |
|---|---|---|
| `market_id` | string | Polymarket condition ID — full lowercase hex with `0x` prefix. Primary key for all Polymarket APIs. |
| `question` | string | Market question text, as returned by the Polymarket Gamma API. |
| `description` | string \| null | Market description text, as returned by Gamma. Length varies from a single sentence to several paragraphs; some markets have no description. |
| `category_fflow` | string | ForesightFlow keyword-classifier output. Values: `military_geopolitics`, `regulatory_decision`, `corporate_disclosure`, `other`. |
| `resolution_type` | string | Resolution mechanism. Values: `event_resolved`, `deadline_resolved`, `unclassifiable`. |
| `resolution_outcome` | int8 \| null | UMA oracle resolution: `1` = YES, `0` = NO. Null for unresolved markets. |
| `volume_total_usdc` | float64 \| null | Total trading volume in USDC, as reported by the Gamma API at ingest time. Null if not reported. |
| `created_at` | string \| null | Market creation timestamp (ISO 8601 UTC, `Z` suffix). Corresponds to the on-chain market-creation block time (`T_open` in the companion paper). |
| `closed_at` | string \| null | Market trading close timestamp (ISO 8601 UTC). Null for markets with no explicit close date. |
| `resolved_at` | string \| null | UMA oracle resolution timestamp (ISO 8601 UTC). Null for unresolved markets. |
| `n_trades_in_db` | int32 | Count of individual trades stored in the ForesightFlow database for this market. `0` for markets not yet collected via the subgraph; non-zero indicates trade-level data availability. |

**Example record (JSON):**

```json
{
  "market_id": "0x6d0e09d0f04572d9b1adad84703458b0297bc5603b69dccbde93147ee4443246",
  "question": "US forces enter Iran by April 30?",
  "description": "This market resolves YES if ...",
  "category_fflow": "military_geopolitics",
  "resolution_type": "deadline_resolved",
  "resolution_outcome": 1,
  "volume_total_usdc": 825000000.0,
  "created_at": "2026-03-18T16:29:07Z",
  "closed_at": "2026-04-30T00:00:00Z",
  "resolved_at": "2026-04-09T00:28:21Z",
  "n_trades_in_db": 4000
}
```

---

## Quick start

### JSONL (streaming, no extra dependencies)

```python
import gzip, json

with gzip.open("data/typology-v1.jsonl.gz", "rt", encoding="utf-8") as f:
    records = [json.loads(line) for line in f]

# Filter to deadline-resolved military markets
deadline_mil = [
    r for r in records
    if r["resolution_type"] == "deadline_resolved"
    and r["category_fflow"] == "military_geopolitics"
]
print(len(deadline_mil))  # ~3,100 markets
```

### Parquet (fast columnar queries)

```python
import pandas as pd

df = pd.read_parquet("data/typology-v1.parquet")
print(df.shape)                          # (911237, 11)
print(df["resolution_type"].value_counts())

# High-volume deadline markets
high_vol = df[
    (df["resolution_type"] == "deadline_resolved") &
    (df["volume_total_usdc"] > 1e6)
].sort_values("volume_total_usdc", ascending=False)
```

### DuckDB (SQL, zero Python overhead)

```python
import duckdb

con = duckdb.connect()
con.execute("CREATE VIEW typology AS SELECT * FROM read_parquet('data/typology-v1.parquet')")

con.execute("""
    SELECT category_fflow, resolution_type, COUNT(*) AS n
    FROM typology
    GROUP BY 1, 2
    ORDER BY 1, 3 DESC
""").df()
```

---

## Versioning policy

This dataset is a snapshot frozen at the 2026-04-27T00:00:00Z cutoff. The classification reflects the state of the ForesightFlow keyword classifier as of Task 03 Phase 0 (April 2026). Future versions will extend the corpus to later markets and may incorporate an improved classifier; existing records will not be modified except to correct factual errors, which are documented in `CHANGELOG.md`. Each version is a distinct git tag; reproducibility-sensitive work should pin to `polymarket-resolution-typology-v1`.

---

## Citation

If you use this dataset in academic work, please cite both the dataset and the companion paper:

```bibtex
@dataset{typology2026,
  author       = {Nechepurenko, Maksym},
  title        = {{Polymarket Resolution Typology Dataset}, v1},
  year         = {2026},
  publisher    = {GitHub},
  url          = {https://github.com/ForesightFlow/datasets/tree/main/polymarket-resolution-typology},
  note         = {Tag: polymarket-resolution-typology-v1. Snapshot cutoff: 2026-04-27.}
}

@misc{nechepurenko2026foresightflow,
  author = {Nechepurenko, Maksym},
  title  = {ForesightFlow: Real-Time Detection of Informed Trading in Decentralized Prediction Markets},
  year   = {2026},
  note   = {Working draft}
}
```

A `CITATION.cff` file is included for automated citation generation.

---

## License

The dataset metadata, classification labels, and structured manifest are released under [CC-BY 4.0](LICENSE). Market questions and descriptions are sourced from the Polymarket Gamma API; Polymarket's own terms of service govern their original data. The CC-BY 4.0 grant above applies to the compiled dataset as a whole, including the classification layer and the structured format.

---

## Contact

Questions, corrections, or proposed classifier improvements: maksym@devnull.ae or via GitHub issue on this repository.
