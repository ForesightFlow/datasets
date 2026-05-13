# ForesightFlow Datasets

Public datasets released alongside ForesightFlow research.

## Index

| Dataset | Description | License | Size | Tag |
|---|---|---|---|---|
| [coordination-traces-100](coordination-traces-100/) | 500 LLM reasoning traces (100 markets × 5 coordination configs) from the Phase 0.5 shakedown of "Coordination as an Architectural Layer for LLM-Based Multi-Agent Systems" | CC-BY 4.0 | 8.8 MB | `coordination-traces-100-v1` |
| [ffic-inventory](ffic-inventory/) | 8 publicly documented Polymarket insider-trading cases mapped to 24 on-chain market identifiers, released alongside the paper "ForesightFlow: Real-Time Detection of Informed Trading in Decentralized Prediction Markets"| CC-BY 4.0 | 21 KB | `ffic-inventory-v1` |
| [polymarket-deadline-ils](polymarket-deadline-ils/) | Population-scale Deadline-ILS (ILS^dl) scores for 88 Polymarket markets across military/geopolitical, regulatory, and corporate categories. Includes LLM-recovered event dates (T_event), bootstrap CIs, and full 2,375-market attrition chain. Snapshot: 2020–2026. | CC-BY 4.0 | 311 KB | `polymarket-deadline-ils-v3` |
| [polymarket-tnews-tevent-recovery](polymarket-tnews-tevent-recovery/) | Curated public-event and news-arrival timestamps for 2,052 resolved Polymarket markets across three methodological tiers: UMA Oracle proposer evidence (Tier 1, n=12), GDELT proxy (Tier 2, n=1,993), and LLM-assisted multi-source verification (Tier 3, n=47). Snapshot: 2022-12–2026-04. | CC-BY 4.0 | ~6 MB | `polymarket-tnews-tevent-recovery-v1` |
| [polymarket-hazard-rates](polymarket-hazard-rates/) | Per-category exponential hazard fits (MLE λ̂, 95% CI, KS test) for the time-to-event distribution on Polymarket deadline-resolved contracts. Baseline survival function for the ILS-dl framework. Categories: military_geopolitics (n=18, λ=0.241, adequate), corporate_disclosure (preliminary), regulatory_decision (rejected), esports (n/a). | CC-BY 4.0 | <1 MB | `polymarket-hazard-rates-v1` |
| [polymarket-ils-corpus](polymarket-ils-corpus/) | Population-scale ILS corpus for 4,801 resolved Polymarket markets. Anchor: `t_resolve − 24h` proxy (4,796 markets, 99.9%) or recovered T_event (5 markets). Multi-window variants, scope flags, HHI. `anchor_type` column distinguishes proxy from event-anchored records. 2,548 clean-scope markets. | CC-BY 4.0 | ~4 MB | `polymarket-ils-corpus-v1` |
| [polymarket-resolution-typology](polymarket-resolution-typology/) | Three-class classification of 911,237 Polymarket markets by resolution mechanism (deadline_resolved / event_resolved / unclassifiable), with category labels and volume metadata. Snapshot: 2020–2026-04-27. | CC-BY 4.0 | 242 MB (LFS) | `polymarket-resolution-typology-v1` |
| [pmxt-stylized-facts-v1](pmxt-stylized-facts-v1/) | Per-market stylized-fact measurements (SF1–SF9) for 13,314 resolved Polymarket binary-event markets, week 2026-04-21 to 2026-04-27. Empirical foundation for Nechepurenko (2026) Paper 1 (event-linked perpetuals). | CC-BY 4.0 | 1.6 MB | `pmxt-stylized-facts-v1` |
| [pmxt-counterfactual-replay-v1](pmxt-counterfactual-replay-v1/) | Counterfactual simulation results (E2 margin recalibration + E3 resolution-zone protocol comparison) for 13,000+ resolved Polymarket binary-event markets. Per-(engine/mechanic, leverage, class) liquidation rates, bad-debt frequencies, drawdown, and PnL. Companion to pmxt-stylized-facts-v1 and Nechepurenko (2026) Paper 1. | CC-BY 4.0 | 19 KB | `pmxt-counterfactual-replay-v1` |
| [pmxt-behavioral-clusters-v1](pmxt-behavioral-clusters-v1/) | Fill-side behavioral clusters, feature tiers, and per-market microstructure signatures from 13.4M `OrderFilled` events on Polymarket CTFExchange (43,116 markets, 77,203 addresses, 2026-04-21 to 2026-04-27). k-means k=5 archetypes, 6 reviewer-defensible feature tiers, bilateral Spearman analysis with BH-FDR correction. Companion to Nechepurenko (2026) Paper 4. | CC-BY 4.0 | 17.8 MB (LFS) | `pmxt-behavioral-clusters-v1` |

---

## PMXT Bundle Family (Event-Linked Perpetuals)

Datasets released as the empirical foundation for the four-paper Event-Linked Perpetuals programme by Maksym Nechepurenko (Devnull Research). See each bundle's README for schema, methodology, and citation details.

| Bundle | Folder | DOI | Status |
|---|---|---|---|
| Bundle 1 | [`pmxt-stylized-facts-v1/`](./pmxt-stylized-facts-v1) | [10.5281/zenodo.20107449](https://doi.org/10.5281/zenodo.20107449) | Released |
| Bundle 2 | [`pmxt-counterfactual-replay-v1/`](./pmxt-counterfactual-replay-v1) | [10.5281/zenodo.20108387](https://doi.org/10.5281/zenodo.20108387) | Released |
| Bundle 3 | [`pmxt-behavioral-clusters-v1/`](./pmxt-behavioral-clusters-v1) | TBD (Zenodo forthcoming) | Released |

---

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
  title  = {Information Leakage at Population Scale: An Evaluation of the {Polymarket} Insider-Relevant Subpopulation},
  author = {Nechepurenko, Maksym},
  year   = {2026},
  doi    = {10.48550/arXiv.2605.00459},
  url    = {https://arxiv.org/abs/2605.00459},
  note   = {SSRN Working Paper 6686819}
}
```

### ForesightFlow: An Information Leakage Score Framework for Prediction Markets

```bibtex
@misc{nechepurenko2026ils-framework,
  title  = {{ForesightFlow}: An Information Leakage Score Framework for Prediction Markets},
  author = {Nechepurenko, Maksym},
  year   = {2026},
  doi    = {10.48550/arXiv.2605.00493},
  url    = {https://arxiv.org/abs/2605.00493},
  note   = {SSRN Working Paper 6687361}
}
```

### Empirical Evaluation of Deadline-Resolved Information Leakage on Documented Polymarket Insider Cases

```bibtex
@misc{nechepurenko2026deadline-leakage,
  title  = {Empirical Evaluation of Deadline-Resolved Information Leakage on Documented {Polymarket} Insider Cases},
  author = {Nechepurenko, Maksym},
  year   = {2026},
  doi    = {10.48550/arXiv.2605.02286},
  url    = {https://arxiv.org/abs/2605.02286},
  note   = {SSRN Working Paper 6687398}
}
```

### Per-Market Information Leakage and Order-Flow Skill

```bibtex
@misc{nechepurenko2026per-market-ils,
  title  = {Per-Market Information Leakage and Order-Flow Skill: Two Methodological Lenses on Informed Trading in Decentralized Prediction Markets},
  author = {Nechepurenko, Maksym},
  year   = {2026},
  doi    = {10.48550/arXiv.2605.02287},
  url    = {https://arxiv.org/abs/2605.02287},
  note   = {SSRN Working Paper 6687441}
}
```

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

### Resolution-Aware Perpetual Futures on Binary Prediction Markets

```bibtex
@misc{nechepurenko2026elp,
  title  = {Resolution-Aware Perpetual Futures on Binary Prediction Markets: An Empirical Risk-Design Framework Using Polymarket Data},
  author = {Nechepurenko, Maksym},
  year   = {2026},
  note   = {Working paper. Companion datasets: pmxt-stylized-facts-v1
            (DOI: 10.5281/zenodo.20107449), pmxt-counterfactual-replay-v1
            (DOI: 10.5281/zenodo.20108387).}
}
```

### Fill-Side Non-Retail Trading on Polymarket

```bibtex
@misc{nechepurenko2026pmxt_clusters_paper,
  title  = {Fill-Side Non-Retail Trading on Polymarket: An Empirical Study of Behavioral
            Tiers and Microstructure Signatures Under Quote-Attribution Constraints},
  author = {Nechepurenko, Maksym},
  year   = {2026},
  note   = {Working paper. Companion dataset: pmxt-behavioral-clusters-v1
            (DOI: 10.5281/zenodo.XXXXXXXX).}
}
```
