# Datasheet for Dataset: PMXT Behavioral Clusters v1

Following the Datasheets for Datasets convention (Gebru et al. 2018).  
Bundle 3 of the PMXT family. See also: Bundle 1 (pmxt-stylized-facts-v1, DOI 10.5281/zenodo.20107449) and Bundle 2 (pmxt-counterfactual-replay-v1, DOI 10.5281/zenodo.20108387).

---

## Motivation

**For what purpose was the dataset created?**  
To enable reproducibility of Paper 4 of the Event-Linked Perpetuals research programme (Nechepurenko 2026) and to provide the first public characterization of non-retail participant behavior on a decentralized prediction market platform (Polymarket). The dataset supports research on prediction market microstructure, behavioral clustering of on-chain participants, and informed liquidity scoring.

**Who created the dataset and on whose behalf?**  
Maksym Nechepurenko (Devnull Research / ForesightFlow). Independent research, no institutional funding.

**Who funded the creation of the dataset?**  
Self-funded.

---

## Composition

**What do the instances represent?**  
Two primary unit types:
1. Per-market aggregate microstructure metrics (43,116 Polymarket binary prediction markets)
2. Per-cluster and per-tier aggregate behavioral statistics (5 k-means clusters, 6 feature tiers)

No address-level data is published (privacy-by-design; see KNOWN_LIMITATIONS §6).

**How many instances?**  
- Markets: 43,116 (per_market_microstructure.parquet, per_market_ils.parquet)
- Clusters: 5 (per_cluster_summary.json, per_cluster_aggregates.parquet)
- Tiers: 6 primary + 1 whale overlay (per_address_tiers aggregated to tier level)
- Market × archetype pairs: varies (per_market_archetype_share.parquet)

**Does the dataset contain all possible instances, or is it a sample?**  
All 43,116 markets with ≥1 fills in the 2026-04-21 to 2026-04-27 window are included. 77,203 unique addresses with ≥5 fills are covered in aggregate statistics.

**Is there any information that is missing from individual instances?**  
- ILS is null for 85.1% of markets (not yet resolved or price movement < 5%; see KNOWN_LIMITATIONS §3)
- Kyle's λ is null for markets with insufficient price variation (18,338 / 43,116)
- G-QUOTE-LIFE FAIL: no quote lifecycle features (see KNOWN_LIMITATIONS §1)

**Are there recommended data splits?**  
No official train/test split. For time-series analysis, within-week splits should respect chronological order of 5-min bins.

**Are there any errors, sources of noise, or redundancies in the dataset?**  
- Kyle's λ raw values contain extreme outliers from OLS instability (496 markets); use `kyle_lambda_winsorized` 
- ILS values clipped to [−0.5, 1.5] (formulaic clipping, not winsorization)
- Archetype labels are fill-side proxies, not ground-truth market roles

**Is the dataset self-contained?**  
Yes for aggregate statistics. Reproducing from source requires Polygon archive node access and PMXT v2 archive data (see Bundles 1–2).

**Does the dataset contain data that might be considered confidential?**  
No. All market identifiers (token_id, condition_id) are public on Polymarket. All addresses are pseudonymous on-chain identifiers. Address-level data is not published.

**Does the dataset contain data that, if viewed directly, might be offensive, insulting, threatening, or might otherwise cause anxiety?**  
No.

---

## Collection Process

**How was the data collected?**  
1. `OrderFilled` events collected via `eth_getLogs` streaming on Polygon mainnet, 200-block pages, from Polygon archive nodes (polygon.drpc.org, rpc-mainnet.matic.quiknode.pro, 1rpc.io/matic)
2. 5-minute price bins reconstructed from fill event timestamps and prices
3. Resolution outcomes joined from PMXT v2 archive (`pmxt-stylized-facts-v1`)
4. Market metadata (condition_id) mapped via Polymarket archive files

**Who collected the data?**  
Automated pipeline (evaluation/paper4/ scripts in the event-linked-perps repository).

**Over what timeframe was the data collected?**  
Source data: fills from 2026-04-21 00:00 UTC to 2026-04-27 23:59 UTC (Polygon blocks 86,008,447 – 86,107,178). Pipeline run: 2026-05-11.

**Were any ethical review processes conducted?**  
No formal IRB review. Data is entirely from public on-chain transactions. No personally identifiable information is collected or published.

**Did the individuals in question consent to the collection and use of their data?**  
Polymarket users transact on a public blockchain. All transactions are publicly visible by design. Address-level data is not published in this deposit.

---

## Preprocessing, Cleaning, and Labeling

**Was any preprocessing/cleaning/labeling of the data done?**  
Yes:
- CTFExchange contract (0x4bfb…) excluded from behavioral analysis
- Addresses with <5 fills excluded from clustering
- Features winsorized at p99.5 and StandardScaled before clustering
- k-means k=5 assigned via fallback cascade (DBSCAN→HDBSCAN→k-means)
- Archetype labels assigned via heuristic on feature centroids
- Feature tiers assigned via pre-registered percentile thresholds

**Was the raw data saved in addition to the preprocessed/cleaned/labeled data?**  
Raw fills are not published (privacy and size constraints). Per-market-stats with 5-min bins are preserved in `per_market_stats.parquet` (not in this deposit due to size; available on request).

**Is the software used to preprocess/clean/label the data available?**  
Yes. Full pipeline at [github.com/ForesightFlow/event-linked-perps](https://github.com/ForesightFlow/event-linked-perps), `evaluation/paper4/`.

---

## Uses

**Has the dataset been used for any tasks already?**  
Yes — Paper 4 of the Event-Linked Perpetuals research programme.

**What (other) tasks could the dataset be used for?**  
- Comparative prediction market microstructure analysis across venues
- Behavioral segmentation of on-chain DeFi participants
- Informed trading detection in binary prediction markets
- Testing of market microstructure models on prediction market data

**Is there anything about the composition of the dataset or the way it was collected and preprocessed/cleaned/labeled that might impact future uses?**  
Yes — see KNOWN_LIMITATIONS.md. Key: sports-dominant composition (77.9% of markets), single-week scope, fill-side only data (no quote lifecycle), k-means clustering is exploratory (silhouette = 0.227).

**Are there tasks for which the dataset should not be used?**  
- Identifying specific individuals or wallet owners from address behavior (address-level data is not published; inference from aggregate data is discouraged)
- Claims about ground-truth market-making or liquidity-provision (G-QUOTE-LIFE FAIL; fill-side proxies only)

---

## Distribution

**Will the dataset be distributed to third parties?**  
Yes. Deposited on Zenodo under CC-BY-4.0. Mirrored on [github.com/ForesightFlow/datasets](https://github.com/ForesightFlow/datasets).

**How will the dataset be distributed?**  
Zenodo deposit (DOI forthcoming), GitHub mirror.

**When will the dataset be distributed?**  
Post-arXiv submission of Paper 4 r0.5.0.

**Will the dataset be distributed under a copyright or other intellectual property (IP) license?**  
CC-BY-4.0. Attribution required.

**Have any third parties imposed IP-based or other restrictions on the data?**  
No. Source data is public on-chain; PMXT v2 archive data licensed under CC-BY-4.0 (Bundle 1).

---

## Maintenance

**Who will be supporting/hosting/maintaining the dataset?**  
Maksym Nechepurenko (maksym@devnull.ae).

**How can the owner/curator be contacted?**  
maksym@devnull.ae / GitHub: @mnechepurenko

**Is there an erratum?**  
No erratum at time of deposit. See GitHub issues on event-linked-perps for post-deposit corrections.

**Will the dataset be updated?**  
The current version (v1) covers 2026-04-21 to 2026-04-27 and is a static snapshot. Future versions may cover additional windows.

**Are there applicable limits on the retention of the data?**  
No.

**Will older versions of the dataset continue to be supported/hosted/maintained?**  
Zenodo provides version persistence via DOI.

**If others want to extend/augment/build on/contribute to the dataset, is there a mechanism for them to do so?**  
GitHub issues and pull requests at [github.com/ForesightFlow/event-linked-perps](https://github.com/ForesightFlow/event-linked-perps).
