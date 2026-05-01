# ForesightFlow Insider Cases (FFIC) Inventory

A curated validation set mapping eight publicly documented episodes of suspected informed trading on Polymarket to concrete on-chain market identifiers.

**Version:** 1.0
**Tag:** `ffic-inventory-v1`
**License:** CC-BY 4.0
**Companion paper:** Nechepurenko (2026), *ForesightFlow: Real-Time Detection of Informed Trading in Decentralized Prediction Markets*

---

## Why this dataset exists

The empirical literature on informed trading in prediction markets (notably Mitts and Ofir 2026, Saguillo et al. 2025) has documented hundreds of millions of dollars in anomalous profits on Polymarket between 2024 and 2026. The cases are real and concretely attributable, but published reports typically describe events at the narrative level (which market, approximately when, approximately how much) without releasing the on-chain identifiers necessary for reproducibility. As a result, every research group studying informed flow on Polymarket has had to reconstruct the case-to-market mapping themselves, and direct comparison across methodologies is impeded.

FFIC closes this gap. For each of eight publicly reported insider-trading episodes, we provide:

- The narrative description and primary public sources
- The Polymarket condition IDs of the directly involved markets
- The resolution metadata (outcome, timestamp, oracle path)
- A structured manifest that downstream tooling can ingest directly

The inventory is intended as a community resource: future work on informed-trading detection in prediction markets can be evaluated against the same labelled cases, addressing one of the persistent reproducibility weaknesses of the on-chain forensics literature.

---

## What the dataset contains

The inventory covers eight cases spanning 2023–2026, mapped to 32 individual Polymarket markets:

| Case ID | Description | Date | Markets | Total volume |
|---|---|---|---|---|
| `fficd-001` | 2024 U.S. presidential election | Nov 2024 | 4 | $2.96 B |
| `fficd-002` | October 2024 Iran strike on Israel | Oct 2024 | 3 | $1.04 M |
| `fficd-003` | 2026 U.S.–Iran conflict cluster | Feb–Apr 2026 | 6 | $825.3 M |
| `fficd-004` | January 2026 U.S.–Venezuela / Maduro operation cluster | Jan 2026 | 11 | $89.2 M |
| `fficd-005` | Bitcoin ETF SEC approval | Jan 2024 | 1 | $12.6 M |
| `fficd-006` | Google Year-in-Search rankings 2025 | Dec 2025 | 3 | $5.3 M |
| `fficd-007` | FTX / SBF case cluster | 2024–2025 | 3 | $9.5 M |
| `fficd-008` | Romanian presidential election 2024–2025 | Dec 2024 | 1 | $326.5 M |

Total: 32 markets, approximately $4.23 billion in cumulative volume. Cases span three of the target categories used in the companion paper: military and geopolitical actions, corporate proprietary disclosures, and regulatory decisions.

For each case, we provide the public-reporting record (URLs to news outlets, court filings, or other primary sources where available), the Polymarket condition IDs, and structured metadata sufficient for programmatic ingestion.

---

## Schema

`data/ffic-v1.jsonl` is one JSON object per case, with the following shape:

```json
{
  "case_id": "fficd-002",
  "title": "October 2024 Iran strike on Israel",
  "date": "2024-10-01",
  "category": "military_geopolitics",
  "narrative": "Hours before Iran launched ballistic missiles at Israel, six newly-created Polymarket wallets purchased YES shares...",
  "primary_sources": [
    {"type": "news", "outlet": "WSJ", "url": "https://...", "date": "2024-10-15"}
  ],
  "academic_sources": [
    {"citation": "Mitts and Ofir (2026)", "section": "Section 4.1, Table 2"}
  ],
  "markets": [
    {
      "market_id": "0xc1b6d712...",
      "label": "Iran strike today",
      "condition_id_full": "0xc1b6d7128a5c7b1a7c3e9f...",
      "yes_token_decimal": "...",
      "resolution_outcome": "YES",
      "resolution_timestamp": "2024-10-01T18:30:00Z",
      "volume_total_usdc": 148732,
      "trade_count": 309
    }
  ],
  "notes": "Insider activity confirmed by post-resolution wallet-clustering analysis..."
}
```

`data/ffic-v1.csv` provides a flat per-market view with the most-used fields for spreadsheet workflows.

`sources/` contains archived public-reporting materials (where redistribution is permitted) and reference URLs.

`MANIFEST.json` provides cryptographic hashes of all data files for integrity verification.

---

## Quick start

```python
import json

with open("data/ffic-v1.jsonl") as f:
    cases = [json.loads(line) for line in f]

# Find all markets in the Iran-strike cluster
iran = next(c for c in cases if c["case_id"] == "fficd-002")
for m in iran["markets"]:
    print(m["market_id"], m["label"], m["resolution_outcome"])

# Or, flat per-market view
import pandas as pd
df = pd.read_csv("data/ffic-v1.csv")
df[df["case_id"] == "fficd-002"]
```

To ingest into a Polymarket-research pipeline, use the `condition_id_full` field as the primary key. Polymarket's gamma API (`https://gamma-api.polymarket.com/markets?condition_ids=...`) and subgraph (`https://gateway.thegraph.com/api/<key>/subgraphs/id/<id>`) both accept this identifier directly.

---

## Trade-history availability

Twenty-two of the 32 markets have full on-chain trade history recoverable through the standard Polymarket subgraph at the time of release (April 2026). Seven markets are blocked: the four 2024 U.S. presidential top-line markets (subgraph indexer capacity exceeded) and three fficd-004 markets whose trade history was not collected prior to dataset release. Three additional markets (two from fficd-003, one from fficd-006) have partial coverage recoverable via the CLOB price-history endpoint. The companion paper documents the recovery procedure; see Section 6.6 of Nechepurenko (2026).

The inventory itself is index-complete (all 32 condition IDs are documented and verified); the trade-history limitation is a property of the public infrastructure or collection status, not of the dataset.

---

## Versioning policy

The FFIC inventory is versioned and append-only. New documented cases that surface in the public-reporting record will be added in subsequent versions; existing case entries are not modified except to correct factual errors, which are tracked in `CHANGELOG.md`. Each version is a git tag and a frozen release; reproducibility-sensitive downstream work should pin to a specific tag (e.g., `ffic-inventory-v1`).

---

## Citation

If you use FFIC in academic work, please cite both the inventory and the companion paper:

```bibtex
@dataset{ffic2026,
  author       = {Nechepurenko, Maksym},
  title        = {{ForesightFlow Insider Cases (FFIC) Inventory}, v1},
  year         = {2026},
  publisher    = {GitHub},
  url          = {https://github.com/ForesightFlow/datasets/tree/main/ffic-inventory},
  note         = {Tag: ffic-inventory-v1}
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

The inventory metadata, narrative descriptions, schema, and structured manifest are released under [CC-BY 4.0](LICENSE). The original news articles and academic citations linked from this dataset retain their respective licenses; the present inventory only references and excerpts them.

---

## Contact

Questions, corrections, or proposed additions: maksym@devnull.ae or via GitHub issue on this repository.
