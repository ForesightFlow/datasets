# PMXT Behavioral Clusters v1

**Bundle 3 of the PMXT family** | CC-BY-4.0 | DOI: 10.5281/zenodo.XXXXXXXX (forthcoming)

Companion dataset to **Paper 4 of the Event-Linked Perpetuals research programme**:  
*"Fill-Side Non-Retail Trading on Polymarket: An Empirical Study of Behavioral Tiers and Microstructure Signatures Under Quote-Attribution Constraints"*  
Nechepurenko M., 2026.

---

## What's in this bundle

Per-cluster and per-tier aggregate behavioral statistics from 13,356,931 `OrderFilled` events on Polymarket CTFExchange (Polygon mainnet), 2026-04-21 to 2026-04-27, together with per-market microstructure metrics and resolution-anchored informed liquidity scores.

**43,116 markets · 77,203 addresses (aggregate only) · k-means k=5 · 6 feature tiers**

| File | Description |
|------|-------------|
| `data/per_cluster_summary.json` | k-means cluster centroids + 95% CI + archetype labels |
| `data/per_cluster_aggregates.parquet` | cluster-level totals and summary statistics |
| `data/per_address_tiers.parquet` | address-level tier + cluster assignments *(pseudonymous addresses)* |
| `data/tier_kmeans_crosstab.json` | 6 tiers × 5 k-means clusters cross-tabulation |
| `data/tier_sensitivity.json` | Tier populations at P90/P95/P99 threshold variants |
| `data/per_market_microstructure.parquet` | 43,116 markets × 28 metrics (PR, TS, OI, VPIN, SCI, Kyle's λ) |
| `data/per_market_ils.parquet` | ILS at 4 resolution anchor offsets (6,406 / 43,116 scope_pass) |
| `data/per_market_archetype_share.parquet` | per (market, archetype) volume fraction |
| `data/cluster_microstructure_bilateral_real.json` | Spearman ρ + BH-FDR + Mann-Whitney + BCa CI |
| `data/manipulation_patterns.json` | Wash-volume candidates + book-depth swings |
| `data/gate_report.json` | Three-gate empirical verdict (G-FILL/G-QUOTE-LIFE/G-BOOK) |
| `data/paper1_feedback.json` | Paper 1 feedback test results |
| `manifests/` | Reproducibility manifests (source hash, code commit, parameters) |
| `docs/SCHEMA.md` | Column-by-column documentation |
| `docs/METHODOLOGY.md` | Full methodology description |
| `docs/KNOWN_LIMITATIONS.md` | All known limitations (10 items) |
| `DATASHEET.md` | Datasheets for Datasets (Gebru et al. 2018) format |
| `CITATION.cff` | Citation metadata |

---

## Key findings

### Three-gate verdict

| Gate | Result |
|------|--------|
| G-FILL | ✅ PASS — 13.36M fills attributed via eth_getLogs |
| G-QUOTE-LIFE | ❌ FAIL universal — off-chain CLOB; no quote lifecycle data |
| G-BOOK | ⚠️ PASS partial — market-level best_bid/best_ask only |

### Feature-tier distribution (primary result)

| Tier | Addresses | % of Total | Notional | % of Total |
|------|-----------|-----------|----------|-----------|
| whale-tier (notional ≥ $1M) | 68 | 0.1% | $184M | 28.0% |
| high-frequency-operator | 2,952 | 3.8% | $155M | 23.5% |
| power-trader | 6,738 | 8.7% | $197M | 29.9% |
| active-retail | 2,062 | 2.7% | $70M | 10.6% |
| high-breadth-operator | 2,025 | 2.6% | $7M | 1.1% |
| episodic-retail | 63,358 | 82.1% | $45M | 6.8% |

**Top 3 tiers (12.6% of addresses) control 81.4% of notional volume.**

### k-means k=5 exploratory partition

| Cluster | Archetype | N | Notional share |
|---------|-----------|---|----------------|
| C1 | fill-MM | 16,786 | 46.0% |
| C2 | fill-LP | 13,626 | 45.1% |
| C0 | SPECIALIST | 13,775 | 7.5% |
| C3 | RETAIL | 20,033 | 0.8% |
| C4 | RETAIL | 14,733 | 0.6% |

Note: DBSCAN yielded 1 cluster (unimodal data); k-means k=5 is exploratory fallback (silhouette = 0.227). Feature-tier classification is the recommended primary stratification.

---

## Related datasets (PMXT family)

| Bundle | DOI | Contents |
|--------|-----|---------|
| Bundle 1: pmxt-stylized-facts-v1 | 10.5281/zenodo.20107449 | 13,314 markets, SF1–SF14, PMXT v2 archive |
| Bundle 2: pmxt-counterfactual-replay-v1 | 10.5281/zenodo.20108387 | E2/E3 resolution-zone counterfactuals |
| Bundle 3: pmxt-behavioral-clusters-v1 | 10.5281/zenodo.XXXXXXXX | **This dataset** |

---

## Citation

```bibtex
@dataset{nechepurenko2026pmxt_clusters,
  author    = {Nechepurenko, Maksym},
  title     = {PMXT Behavioral Clusters v1 — Non-Retail Polymarket Microstructure Dataset},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.XXXXXXXX},
  license   = {CC-BY-4.0}
}
```

---

## Reproduce from source

```bash
git clone https://github.com/ForesightFlow/event-linked-perps
cd event-linked-perps
pip install -r requirements.txt

# Phase 1b: collect fills (requires Polygon archive RPC, ~60 min)
python -m evaluation.paper4.collect_orderfilled_events \
    --start-date 2026-04-21 --end-date 2026-04-27

# Phase 2-5: features, clustering, archetypes, manipulation
python -m evaluation.paper4.compute_features
python -m evaluation.paper4.run_clustering  
python -m evaluation.paper4.per_cluster_microstructure
python -m evaluation.paper4.manipulation_detection

# Phase 6: microstructure metrics, ILS, bilateral
python -m evaluation.paper4.compute_microstructure_metrics
python -m evaluation.paper4.compute_ils
python -m evaluation.paper4.compute_per_market_address   # CC-015 A1
python -m evaluation.paper4.cluster_microstructure_bilateral

# CC-015: feature tiers, dataset bundle
python -m evaluation.paper4.compute_feature_tiers
python -m evaluation.paper4.build_dataset_bundle
```

See `manifests/parameters_locked.json` for all locked seeds and thresholds.
