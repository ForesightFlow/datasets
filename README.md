# ForesightFlow Datasets

Public datasets released alongside ForesightFlow research.

## Index

| Dataset | Description | License | Size | Tag |
|---|---|---|---|---|
| [coordination-traces-100](coordination-traces-100/) | 500 LLM reasoning traces (100 markets × 5 coordination configs) from the Phase 0.5 shakedown of "Coordination as an Architectural Layer for LLM-Based Multi-Agent Systems" | CC-BY 4.0 | 8.8 MB | `coordination-traces-100-v1` |
| [ffic-inventory](ffic-inventory/) | 8 publicly documented Polymarket insider-trading cases mapped to 24 on-chain market identifiers, released alongside the paper "ForesightFlow: Real-Time Detection of Informed Trading in Decentralized Prediction Markets"| CC-BY 4.0 | 21 KB | `ffic-inventory-v1` |
| [polymarket-deadline-ils](polymarket-deadline-ils/) | Population-scale Deadline-ILS (ILS^dl) scores for 88 Polymarket markets across military/geopolitical, regulatory, and corporate categories. Includes LLM-recovered event dates (T_event), bootstrap CIs, and full 2,375-market attrition chain. Snapshot: 2020–2026. | CC-BY 4.0 | 311 KB | `polymarket-deadline-ils-v2` |
| [polymarket-resolution-typology](polymarket-resolution-typology/) | Three-class classification of 911,237 Polymarket markets by resolution mechanism (deadline_resolved / event_resolved / unclassifiable), with category labels and volume metadata. Snapshot: 2020–2026-04-27. | CC-BY 4.0 | 242 MB (LFS) | `polymarket-resolution-typology-v1` |

## Adding a new dataset

Create a subdirectory under the repo root. Each dataset directory must contain:
- `README.md` — description, schema, quick-start
- `DATASHEET.md` — Gebru et al. (2021) datasheet
- `CITATION.cff` — citation metadata
- `LICENSE` — dataset license (CC-BY 4.0 recommended)
- `data/` — data files

Update this top-level README index, then tag as `<dataset-name>-v1`.

---

## Cite this work

If you use these datasets, please cite the papers they accompany:

### Information Leakage at Population Scale

```bibtex
@misc{nechepurenko2026population-leakage,
  title  = {Information Leakage at Population Scale: An Evaluation of the Polymarket Insider-Relevant Subpopulation},
  author = {Nechepurenko, Maksym},
  year   = {2026},
  url    = {http://ssrn.com/abstract=6686819},
  note   = {SSRN Working Paper 6686819}
}
```

Full preprint: <https://foresightflow.org/publications/information-leakage-population-scale>.

### Empirical Evaluation of Deadline-Resolved Information Leakage on Documented Polymarket Insider Cases

```bibtex
@misc{nechepurenko2026deadline-leakage,
  title  = {Empirical Evaluation of Deadline-Resolved Information Leakage on Documented Polymarket Insider Cases},
  author = {Nechepurenko, Maksym},
  year   = {2026},
  url    = {https://papers.ssrn.com/abstract=6687398},
  note   = {SSRN Working Paper 6687398}
}
```

Full preprint: <https://foresightflow.org/publications/deadline-resolved-information-leakage>.

### Coordination as an Architectural Layer for LLM-Based Multi-Agent Systems

```bibtex
@misc{nechepurenko2026coordination,
  title  = {Coordination as an Architectural Layer for LLM-Based Multi-Agent Systems: An Information-Controlled Empirical Study on Prediction Markets},
  author = {Nechepurenko, Maksym and Shuvalov, Pavel},
  year   = {2026},
  url    = {https://papers.ssrn.com/abstract=6687518},
  note   = {SSRN Working Paper 6687518}
}
```

Full preprint: <https://foresightflow.org/publications/coordination-architectural-layer>.
