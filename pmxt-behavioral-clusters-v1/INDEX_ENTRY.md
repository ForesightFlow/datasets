# Index Entry for ForesightFlow/datasets top-level README

Add this row to the datasets index table:

```markdown
| [pmxt-behavioral-clusters-v1](pmxt-behavioral-clusters-v1/) | Fill-side behavioral clusters, feature tiers, and per-market microstructure signatures from 13.4M `OrderFilled` events on Polymarket CTFExchange (43,116 markets, 77,203 addresses, 2026-04-21 to 2026-04-27). k-means k=5 archetypes, 6 reviewer-defensible feature tiers, Spearman bilateral analysis with BH-FDR correction. Companion to Nechepurenko (2026) Paper 4. | CC-BY 4.0 | 17.8 MB | `pmxt-behavioral-clusters-v1` |
```

Update the PMXT Bundle Family section:

```markdown
| Bundle 3 | [`pmxt-behavioral-clusters-v1/`](./pmxt-behavioral-clusters-v1) | [10.5281/zenodo.XXXXXXXX](https://doi.org/10.5281/zenodo.XXXXXXXX) | Released |
```

Add to the citations section:

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
