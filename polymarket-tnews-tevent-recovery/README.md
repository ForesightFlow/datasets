# Polymarket T_news / T_event Recovery Dataset (v1)

A curated dataset of public-event and news-arrival timestamps for 2,052 resolved
Polymarket markets, recovered across three methodological tiers: UMA Oracle proposer
evidence (Tier 1), GDELT-based proxy matching (Tier 2), and LLM-assisted multi-source
verification (Tier 3). Released alongside the **ForesightFlow** programme of papers on
informed-trading detection in decentralized prediction markets.

This dataset closes a gap in the public-data record for prediction-market research:
event timestamps for resolved Polymarket markets are not currently available in any
standard form. Event studies, information-leakage analyses, and price-discovery
research on Polymarket all require some recovered event anchor, and prior researchers
have largely re-derived these from scratch. We release the consolidated recovery
record so that downstream work can either reuse our anchors directly or use them as
a benchmark for alternative recovery methods.

## Quick stats

| Field | Value |
|---|---:|
| Total records | 2,052 |
| Tier 1 (UMA proposer evidence) | 12 (gold standard, confidence 0.95) |
| Tier 2 (GDELT proxy / resolved-at offset) | 1,993 (confidence 0.60) |
| Tier 3 (LLM-assisted, multi-source verified) | 47 (confidence 0.80--0.90) |
| Snapshot date | 2026-04-30 |
| Distinct categories covered | military_geopolitics, regulatory_decision, corporate_disclosure, esports, other |
| Date range covered (resolution dates) | 2022-12 -- 2026-04 |
| License | CC-BY 4.0 |

## Schema

Each record is a JSON object with the following fields:

| Field | Type | Description |
|---|---|---|
| `market_id` | string | Polymarket condition ID (bytes32 hex), e.g. `0xbfa45527...3f1d` |
| `question` | string | Market question text, as displayed on Polymarket |
| `tier` | string | One of `tier1_uma`, `tier2_gdelt_proxy`, `tier3_llm` |
| `recovered_timestamp` | string (ISO 8601 UTC) | Recovered event or news timestamp |
| `timestamp_type` | string | One of `T_event` (Tier 1, Tier 3), `T_news_proxy` (Tier 2) |
| `confidence` | float | Confidence in `[0, 1]`; see methodology |
| `recovery_method` | string | Concrete method label (e.g. `uma_proposer_evidence`, `gdelt_keyword_match`, `claude-haiku-4-5+web_search_20250305`) |
| `sources` | array | Source records (URL, publication, date_first_reported) — Tier 1 and Tier 3 only |
| `verification_notes` | string | Brief human-readable note on verification |
| `fflow_category` | string | Category label from the ForesightFlow taxonomy (post-correction v1.1) |
| `resolution_type` | string | `event_resolved`, `deadline_resolved`, or `unclassifiable` |
| `resolution_outcome` | float | `0.0` (NO) or `1.0` (YES); `null` if unresolved |

## Methodology

### Tier 1 — UMA Oracle proposer evidence

The UMA Optimistic Oracle requires market proposers to attach evidence URLs supporting
their claimed resolution outcome. For markets where UMA proposer evidence is publicly
queryable, the URL of the cited news article gives a Tier-1 timestamp anchor. This is
the highest-confidence source (confidence = 0.95) because the proposer's evidence is
the canonical resolution-justifying reference.

Coverage is small (12 of 2,052) because UMA evidence URLs are not present for all
resolved markets and not consistently queryable through public APIs.

### Tier 2 — GDELT / resolved-at proxy

For the bulk of markets (1,993), the recovered timestamp is the offset
`resolved_at - 24h`, validated against GDELT (Global Database of Events, Language, and
Tone) keyword matches. This is a structural proxy rather than a true public-event
recovery: it captures the typical lag between event occurrence and Polymarket
resolution. Confidence is set to 0.60 to reflect this proxy character.

Tier 2 anchors are appropriate for population-level analyses but should NOT be used
as the sole anchor for individual-market case studies where the precise event time
matters.

### Tier 3 — LLM-assisted multi-source verification

For 47 high-stakes markets (mostly in `military_geopolitics`), an LLM (Claude
Haiku 4.5) was prompted with a web search tool to recover the public-event timestamp
from multiple independent news sources. Each Tier-3 recovery:

1. Cites at least three independent news sources (typically 5--8)
2. Resolves source-date disagreements through cross-verification
3. Returns confidence in `[0.80, 0.90]` depending on inter-source agreement

Tier-3 records include the cited source URLs and publication dates, enabling
downstream verification.

## Quick-start

```python
import json

# Load full dataset
with open("data/tnews_tevent_recovery_v1.jsonl") as f:
    records = [json.loads(line) for line in f]

# Filter to high-confidence Tier 3 (LLM-verified) only
tier3 = [r for r in records if r["tier"] == "tier3_llm"]
print(f"Tier 3 markets: {len(tier3)}")

# Per-category breakdown
from collections import Counter
print(Counter(r["fflow_category"] for r in records))
```

```python
# Pandas / CSV variant
import pandas as pd
df = pd.read_csv("data/tnews_tevent_recovery_v1.csv")
print(df.groupby(["tier", "fflow_category"]).size().unstack(fill_value=0))
```

## Files

| File | Description | Size (approx) |
|---|---|---:|
| `data/tnews_tevent_recovery_v1.jsonl` | Full dataset, one record per line | ~5 MB |
| `data/tnews_tevent_recovery_v1.csv` | Same data, CSV format (sources column flattened) | ~3 MB |
| `data/tier1_uma_subset.jsonl` | Tier-1 (UMA) subset only, gold standard | <10 KB |
| `data/tier3_llm_subset.jsonl` | Tier-3 (LLM) subset only, with full source URLs | ~200 KB |
| `MANIFEST.json` | SHA-256 hashes of all data files | <1 KB |

## Versioning

- **v1** (2026-05-13) — Initial release. 2,052 records across three tiers. Snapshot
  cut at 2026-04-30. Category labels reflect the v1.1 taxonomy correction (esports
  reclassified out of `military_geopolitics`).

## Citation

If you use this dataset, please cite the paper it accompanies:

```bibtex
@misc{nechepurenko2026deadline-leakage,
  title  = {Empirical Evaluation of Deadline-Resolved Information Leakage on Documented Polymarket Insider Cases},
  author = {Nechepurenko, Maksym},
  year   = {2026},
  doi    = {10.48550/arXiv.2605.02286},
  url    = {https://arxiv.org/abs/2605.02286},
  note   = {SSRN Working Paper 6687398}
}
```

See [`CITATION.cff`](CITATION.cff) for additional citation formats.

## Related datasets

- [`polymarket-deadline-ils`](../polymarket-deadline-ils) — Population Deadline-ILS scores
  (88 markets with bootstrap CIs) that consume the T_event anchors in this dataset.
- [`polymarket-hazard-rates`](../polymarket-hazard-rates) — Per-category exponential
  hazard fits used in the deadline-ILS framework.
- [`ffic-inventory`](../ffic-inventory) — 32 publicly documented Polymarket insider-trading
  markets across 8 cases.

## License

CC-BY 4.0 — see [`LICENSE`](LICENSE).

## Limitations

1. **Tier-2 proxy is structural, not factual.** For 1,993 of 2,052 markets, the
   recovered timestamp is `resolved_at - 24h`, validated against keyword presence in
   GDELT. This is a structural proxy and may differ from the true public-event time
   by hours to days, especially for slow-news events.

2. **Tier-3 LLM provenance.** Tier-3 recoveries depend on LLM web-search calls.
   Sources cited are stored in the record, but the LLM's interpretation of which
   article was "first" or "definitive" is a methodological choice that may differ
   from human expert judgement on edge cases.

3. **Coverage skew.** Of the 2,052 records, 119 esports markets retain residual
   Tier-2 proxy records from before the v1.1 taxonomy correction; these are flagged
   via `fflow_category = "esports"` and should typically be excluded for
   geopolitical-event-focused analyses (event-end and resolution coincide for esports).

4. **Snapshot date.** Data reflect the database as of 2026-04-30. Markets resolved
   after this date are not in v1.
