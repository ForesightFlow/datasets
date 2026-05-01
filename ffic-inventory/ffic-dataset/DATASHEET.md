# Datasheet for the ForesightFlow Insider Cases (FFIC) Inventory

Following the datasheet template of Gebru et al. (2021).

---

## Motivation

**For what purpose was the dataset created?**
FFIC was created to provide a reproducible validation set for research on informed trading in decentralized prediction markets, with primary application to Polymarket. The empirical literature documenting insider activity on these platforms has typically described cases at the narrative level without releasing the on-chain identifiers necessary for reproduction; FFIC closes this gap by mapping eight publicly documented insider-trading episodes to concrete Polymarket condition IDs.

**Who created the dataset and on behalf of what entity?**
The dataset was assembled by Maksym Nechepurenko (Devnull FZCO, Dubai, UAE) as part of the ForesightFlow research programme.

**Who funded the creation of the dataset?**
Self-funded research by Devnull FZCO.

---

## Composition

**What do the instances that comprise the dataset represent?**
Each instance is a documented insider-trading episode, structured as one case record. Each case contains a narrative description, primary public sources, and the set of Polymarket condition IDs at which the episode is alleged to have occurred. Each market is itself a structured record with resolution metadata.

**How many instances are there?**
Eight cases, mapped to twenty-four individual Polymarket markets, representing approximately $5.26 billion in cumulative trading volume.

**Is there a label or target associated with each instance?**
The case-level labels are categorical (the case category: military / geopolitical, regulatory decision, corporate disclosure). The market-level labels are factual: resolution outcome (YES/NO), resolution timestamp, total volume, trade count. The dataset does not include any continuous-valued labels (such as ILS or detector scores); those are computed downstream by tooling that consumes the inventory.

**Does the dataset contain all possible instances or is it a sample?**
FFIC is a curated sample, not a complete population. Inclusion criteria are: (i) the episode has been publicly reported in news media or academic literature; (ii) the connection to specific Polymarket markets can be established with reasonable confidence from the public record; (iii) the markets resolved (i.e., we exclude ongoing situations). The inventory does not claim to enumerate all instances of informed trading on Polymarket; it enumerates documented instances.

**Are there recommended data splits?**
The intended use is as a validation set, not a training set. We do not propose train/validation/test splits. The companion paper uses the entire inventory as the validation reference for methodology evaluation.

**Are there any errors, sources of noise, or redundancies in the dataset?**
Two systematic limitations:

1. *Public-reporting bias.* The inventory consists of cases that surfaced through public reporting. We do not claim it is a uniform sample of insider-trading activity on Polymarket; cases involving smaller dollar amounts, less politically salient events, or actors with effective opsec are systematically under-represented.

2. *Identification uncertainty.* For some cases, the published reporting does not identify specific market IDs and we have inferred them from contextual details (event dates, market questions, volume signatures). Where this inference required judgment, the case record's `notes` field documents the reasoning. We do not anticipate identification errors of greater than approximately 1–2 markets across the inventory, but we explicitly do not guarantee zero error and welcome corrections.

**Is the dataset self-contained, or does it link to or otherwise rely on external resources?**
The inventory itself is self-contained: condition IDs, resolution metadata, and case descriptions are included directly. However, it links to two classes of external resources: (i) the original news-media reports that documented each case, retained as URLs in the `primary_sources` field, and (ii) the on-chain trade history at the listed condition IDs, which is queryable via Polymarket's public subgraph and the Polygon RPC. Both classes of external resources are governed by their own access conditions; the inventory does not redistribute either.

**Does the dataset contain confidential, sensitive, or otherwise restricted material?**
No. All material in FFIC was already public at the time of inclusion: news reports, court filings, blockchain records, and academic citations. The inventory does not de-anonymize any actor whose identity was not already disclosed in public reporting, and does not include personally identifiable information beyond what was already published in news outlets.

---

## Collection process

**How was the data acquired?**
- News-media reports were collected via standard search of the public web; URLs were captured and dated at the time of inclusion.
- Polymarket condition IDs were obtained via the Polymarket Gamma API (`gamma-api.polymarket.com`) using the case event description and date as the search anchor.
- Resolution metadata (outcome, timestamp, volume) was extracted from the same Gamma API and verified against the Polymarket subgraph.
- Trade-count fields are aggregations from the Polymarket subgraph; they reflect the indexer's coverage as of April 2026.

**Over what timeframe was the data collected?**
Cases span September 2023 through April 2026. Inventory assembly took place during March and April 2026 in connection with the companion paper.

**What ethical review processes were conducted?**
The inventory consists exclusively of publicly available information about publicly reported events; no human subjects research was conducted, and no review-board approval was sought or required. The decision to include each case was guided by a conservative threshold: at least one independent news-media or academic source must have publicly identified the episode as suspected insider trading at the time of inclusion.

---

## Preprocessing, cleaning, labeling

**Was any preprocessing/cleaning/labeling of the data done?**
The condition IDs were canonicalized to lowercase hexadecimal. Resolution timestamps were normalized to UTC. Volume figures are reported in USDC and aggregated from the gamma metadata.

**Was the "raw" data saved in addition to the preprocessed/cleaned/labeled data?**
The original `gamma-api` JSON responses for each market are retained internally but are not part of this release; researchers needing them can re-issue the same gamma queries against the live API (the responses are stable for resolved markets). Original news-media URLs are retained in the inventory.

---

## Uses

**Has the dataset been used for any tasks already?**
The inventory is the validation set used in Nechepurenko (2026), *ForesightFlow*. That paper documents the first end-to-end use: an audit of the inventory against the methodology's scope conditions, a proof-of-concept article-derived $T_{\text{news}}$ recovery on the Barak Epstein-files market, and (in the empirical-evaluation section) a deadline-ILS computation across the deadline-resolved subset of the inventory.

**What other tasks could the dataset be used for?**
The inventory is suitable as a labelled reference for any methodology evaluating informed-trading detection on Polymarket: classifier training, detector calibration, comparative evaluation across detection frameworks, ablation studies on individual feature classes (microstructure, wallet-level, price-trajectory). It is also suitable as an empirical anchor for studies of prediction-market efficiency more broadly, where insider activity is treated as one form of information asymmetry.

**Is there anything about the composition of the dataset or the way it was collected and preprocessed that might impact future uses?**
Three points warrant attention. First, the public-reporting bias noted above means the inventory is not a representative sample of insider-trading on Polymarket and should not be treated as such. Second, the inventory is dominated structurally by deadline-resolved markets ("Will event X occur by date Y?"); any methodology that is restricted to event-resolved markets will find a smaller set of FFIC cases applicable. Third, six of the highest-volume markets (the 2024 U.S. presidential top-line markets and two 2026 U.S.–Iran cluster markets) are inventory-complete but exceed the public Polymarket subgraph's indexer capacity, which means downstream tooling that depends on subgraph trade history will need an alternative recovery path for those markets.

**Are there tasks for which the dataset should not be used?**
The inventory should not be used as a training set in a way that conflates "appears in FFIC" with "is an instance of informed trading." The labels are case-level (the episode is publicly reported as suspected informed trading) and not market-level (every trade in the market was informed). Any methodology that uses FFIC for supervised learning should treat the labels as weak labels and validate accordingly.

---

## Distribution

**Will the dataset be distributed to third parties outside of the entity on behalf of which the dataset was created?**
Yes. The inventory is publicly released at [github.com/ForesightFlow/datasets](https://github.com/ForesightFlow/datasets) under CC-BY 4.0.

**How will the dataset be distributed?**
Through the public ForesightFlow GitHub organization, as a versioned subdirectory of the `datasets` repository. Each version is a git tag.

**When will the dataset be distributed?**
First public release: April 2026, concurrent with the working draft of the companion paper.

**Will the dataset be distributed under a copyright or other intellectual property license?**
The inventory metadata is released under [CC-BY 4.0](LICENSE). Linked external resources retain their own licenses.

---

## Maintenance

**Who will be supporting/hosting/maintaining the dataset?**
Maksym Nechepurenko (Devnull FZCO). Hosted on GitHub.

**How can the owner/curator/manager of the dataset be contacted?**
Email: maksym@devnull.ae. GitHub issues on the `ForesightFlow/datasets` repository are also monitored.

**Is there an erratum?**
Errata are tracked in `CHANGELOG.md` in this directory.

**Will the dataset be updated?**
Yes. New documented cases that surface in the public-reporting record will be added in subsequent versions; existing entries are not modified except to correct factual errors. Version bumps follow the convention `ffic-inventory-vN`.

**Will older versions of the dataset continue to be supported/hosted/maintained?**
Yes. Each version is a frozen git tag and remains accessible.

**If others want to extend/augment/build on/contribute to the dataset, is there a mechanism for them to do so?**
Yes. Pull requests proposing new cases, corrections, or schema extensions are welcome. Proposed new cases must include at least one independent public source identifying the episode as suspected insider trading. Schema changes are versioned.

---

## Reference

Gebru, Timnit, Jamie Morgenstern, Briana Vecchione, Jennifer Wortman Vaughan, Hanna Wallach, Hal Daumé III, and Kate Crawford. 2021. "Datasheets for Datasets." *Communications of the ACM* 64 (12): 86–92.
