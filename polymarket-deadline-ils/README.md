# polymarket-deadline-ils

Population-scale Deadline-ILS (ILS^dl) dataset for Polymarket prediction markets.

## Overview

This dataset provides Deadline Information Leakage Scores (ILS^dl) for Polymarket markets in three high-information categories: military/geopolitical events, regulatory decisions, and corporate disclosures. ILS^dl measures the fraction of total price movement that occurred before the underlying real-world event — a signal for informed trading.

## Key Contents

| File | Format | Rows | Description |
|---|---|---|---|
| `data/population_ils_dl.parquet` | Parquet | 2,375 | Full population with T_event, ILS^dl, exclusion chain |
| `data/population_ils_dl.csv` | CSV | 2,375 | Same data in flat CSV format |

## Scope

- **Source markets**: 12,708 Polymarket markets (military_geopolitics + regulatory_decision + corporate_disclosure, volume ≥ $50,000 USDC)
- **After pre-filter**: 2,375 non-unclassifiable markets
- **T_event recovered**: 442 markets (via Claude Haiku + web search)
- **ILS^dl computed**: 88 markets (require both T_event ≥ 0.7 confidence and historical CLOB/trade price coverage)
- **Time period**: 2020–2026
- **ILS^dl with bootstrap CI (B=500)**: 78/88 markets

## ILS^dl Formula

```
ILS^dl(M) = (p(T_event⁻) - p_open) / (p_resolve - p_open)
```

Where `p(T_event⁻)` is the market price just before the event occurred, `p_open` is the opening price, and `p_resolve` ∈ {0, 1} is the binary resolution outcome.

- **ILS^dl ≈ 1**: price fully moved before the event → strong informed trading signal
- **ILS^dl ≈ 0**: price moved only after the event → no pre-event information leakage
- **ILS^dl < 0**: price moved in the wrong direction before the event

## Distribution (88 markets with ILS^dl)

| Metric | Value |
|---|---|
| Mean | −0.515 |
| Median | −0.395 |
| Std | 1.043 |
| Min | −7.750 |
| Max | 0.994 |

## Accessibility

**License**: CC-BY 4.0  
**Format**: Apache Parquet + CSV  
**Load (Python)**:
```python
import pandas as pd
df = pd.read_parquet("data/population_ils_dl.parquet")
ils = df[df["ils_dl"].notna()]  # 88 markets with computed ILS^dl
```

## Limitations

- CLOB price coverage is limited to markets whose historical trade data was available via the Polymarket subgraph. Markets from 2020–2021 (pre-CLOB era) have lower coverage.
- T_event dates are LLM-recovered (Claude Haiku + Sonnet) and may contain errors, especially for ambiguous or niche events.
- 88/2,375 markets (3.7%) have ILS^dl — see DATASHEET.md for the full attrition chain.
- Categories assigned by the ForesightFlow rule-based classifier (polymarket-resolution-typology dataset).
- Many canonical informed-trading cases (FFIC inventory) have `resolution_type=unclassifiable` in the typology and are therefore excluded from ILS^dl computation. See DATASHEET.md §FFIC Localization.

## Citation

See `CITATION.cff`.
