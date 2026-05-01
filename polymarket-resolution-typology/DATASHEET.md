# Datasheet for the Polymarket Resolution Typology Dataset

Following the datasheet template of Gebru et al. (2021).

---

## Motivation

**For what purpose was the dataset created?**

The dataset was created to address a methodological prerequisite for applying information-based microstructure models — specifically the Information Leakage Score (ILS) — to Polymarket prediction markets. The ILS formulation in the companion paper (Nechepurenko 2026) requires distinguishing two structural types of market resolution: deadline-resolved markets ("Will event X occur by date Y?") and event-resolved markets ("Did event X happen?"). These two types require different reference timestamps, different baseline calculations, and different interpretations of pre-event price drift. Without a classification, no ILS-based analysis can proceed at scale.

A secondary motivation is to support related research on prediction-market structure more broadly: studies of crowd forecasting, calibration, liquidity dynamics, and market design all benefit from knowing which markets have hard deadline constraints and which track open-ended event outcomes.

No public classification of Polymarket markets by resolution mechanism existed prior to this release. This dataset provides that classification as a shared, documented baseline.

**Who created the dataset and on behalf of what entity?**

The dataset was produced by Maksym Nechepurenko (Devnull FZCO, Dubai, UAE) as part of the ForesightFlow research programme.

**Who funded the creation of the dataset?**

Self-funded research by Devnull FZCO.

---

## Composition

**What do the instances that comprise the dataset represent?**

Each instance is one Polymarket market, represented by its condition ID (the canonical Polymarket market identifier) and associated metadata. The dataset covers 911,237 markets created on or before 2026-04-27.

**How many instances are there?**

911,237 records, comprising:

| resolution_type | Count | Share |
|---|---|---|
| `unclassifiable` | 853,774 | 93.7% |
| `deadline_resolved` | 56,318 | 6.2% |
| `event_resolved` | 1,145 | 0.1% |

**Is there a label or target associated with each instance?**

Yes. Each record carries two classifier outputs: `resolution_type` (the primary label, three-class) and `category_fflow` (a secondary keyword-based topic label, four values). Both are derived from the market question text and description using the ForesightFlow rule-based classifier. They are not ground-truth labels; see the Limitations section below.

The `resolution_outcome` field (YES/NO) is a factual label from the UMA Optimistic Oracle, not a classifier output.

**Does the dataset contain all possible instances or is it a sample?**

The dataset is a near-complete snapshot of Polymarket markets as of the cutoff date. The population is defined as all markets collected via the Polymarket Gamma API during the ForesightFlow ingest runs, with `created_at_chain <= 2026-04-27T00:00:00Z`. Markets created after the cutoff, or markets that were not yet ingested by the Gamma collector at the time of export, are not included.

**Are there recommended data splits?**

No train/validation/test split is defined. The intended use is as a filtering layer: downstream tooling loads the typology file, filters to the markets of interest (e.g., `deadline_resolved` + `military_geopolitics`), and then fetches price or trade data for those markets from other sources. The companion paper uses the `deadline_resolved` subset as the population from which FFIC markets are drawn for ILS-dl analysis.

**Are there any errors, sources of noise, or redundancies?**

See the Limitations section below.

**Is the dataset self-contained?**

The dataset is self-contained for the metadata and classification labels it provides. It does not bundle price data or trade-level data; those require separate collection from the Polymarket CLOB API and subgraph. The `n_trades_in_db` field provides a data-availability indicator (non-zero means trade-level data exists in the ForesightFlow database), but does not redistribute the trade records themselves.

**Does the dataset contain confidential, sensitive, or otherwise restricted material?**

No. The market questions and descriptions are sourced from the public Polymarket Gamma API. All content was publicly available at the time of collection.

---

## Key Limitations

The following limitations should be understood by any consumer of this dataset.

**1. Classifier confidence varies by class.**

- *`deadline_resolved`*: High precision. The classifier uses a two-stage regex: first, it matches deadline patterns in the market question ("by [date]", "before [date]", "on [date]"); then, if the match appears only in the description (not the question), it emits a lower-confidence flag. Structural validation — the observation that 100% of deadline-classified markets in the target categories resolved NO when no event occurred, which is the only valid outcome for a deadline market that reaches expiry without resolution — provides indirect confirmation of precision. Recall is also high for the target categories; it is less certain for edge cases such as markets with unusual phrasing.

- *`event_resolved`*: High precision but conservative recall. The `event_resolved` class currently covers only the top-tier targeted markets explicitly collected under that category. A substantial portion of the actual event-resolved population is likely sitting in the `unclassifiable` bucket because the classifier's positive criteria for event-resolved markets are more restrictive than for deadline markets.

- *`unclassifiable`*: A conservative fallback that contains two structurally different groups: (i) markets that are genuinely non-classifiable by text features alone (sports outcomes, count markets, "Who will win X?"), and (ii) markets that were event-resolved or deadline-resolved but whose question phrasing did not trigger the classifier's patterns. Researchers treating `unclassifiable` as a homogeneous category, or treating the absence of a `deadline_resolved` label as evidence that a market is not deadline-resolved, will introduce errors.

**2. No external ground truth.**

The classification rests entirely on question text and description text. There is no independently labelled held-out test set against which precision and recall can be measured. The only external validation available is the structural 100% NO-rate observation noted above. Researchers requiring higher-confidence labels for a subset of markets should validate the classifier's output against the actual resolution rules documented in market descriptions.

**3. Category bias.**

The `category_fflow` labels come from a keyword classifier that was designed for the ForesightFlow target categories (military/geopolitics, regulatory decisions, corporate disclosures). The classifier is biased toward those categories; markets from other domains (sports, entertainment, science) are predominantly assigned to `other`. Within the target categories, the classifier uses keyword lists that may over-include peripherally related markets and under-include markets with unusual phrasing. Treat `category_fflow` as a filtering aid, not a definitive topic taxonomy.

**4. Snapshot date.**

The dataset is frozen at 2026-04-27T00:00:00Z. Markets created before the cutoff but not yet resolved on that date are included with null `resolution_outcome` and `resolved_at` fields. Markets that resolved between the ingest cutoff and publication may have stale null values.

**5. Description text quality varies.**

Some markets have extensive structured descriptions; others have minimal text or no description at all. Downstream NLP applications that rely on description text should handle this variance. The `description` field is null for approximately 3–5% of records (based on Gamma API response coverage).

**6. `n_trades_in_db` reflects local database coverage, not Polymarket platform coverage.**

A value of `0` means no trades were collected into the ForesightFlow database for that market. It does not imply the market had no trading activity. The subgraph and CLOB collectors were run selectively on markets of interest; the vast majority of the 911K markets have not been collected at the individual-trade level.

---

## Collection process

**How was the data acquired?**

- Market metadata (question, description, volume, resolution outcome, timestamps) was retrieved via the Polymarket Gamma API (`gamma-api.polymarket.com`) during ForesightFlow ingest runs.
- Resolution timestamps and outcomes were verified against the UMA Optimistic Oracle records retrieved via Polygon JSON-RPC.
- The `resolution_type` classification was produced by the ForesightFlow keyword classifier (`fflow/scoring/resolution_type.py`), applied in bulk to all ingested markets as part of Task 03 Phase 0 (April 2026).
- The `category_fflow` labels were produced by the ForesightFlow taxonomy classifier (`fflow/taxonomy/classifier.py`).
- Trade counts were aggregated from the ForesightFlow trade database (populated via the Polymarket subgraph and CLOB collectors).

**Over what timeframe was the data collected?**

Markets span October 2020 through April 2026. Gamma API ingest was conducted continuously during the ForesightFlow development period (January–April 2026). The `resolution_type` classification backfill was run in a single batch in April 2026, covering the full 911K-market corpus.

**What ethical review processes were conducted?**

The dataset consists of publicly available market metadata from a public prediction platform. No human subjects research was conducted, and no review-board approval was sought or required.

---

## Preprocessing, cleaning, labeling

**Was any preprocessing or cleaning done?**

- Condition IDs were canonicalized to lowercase hexadecimal with `0x` prefix.
- All timestamps were normalized to UTC and formatted as ISO 8601 with `Z` suffix.
- Volume figures are in USDC as reported by the Gamma API; no adjustment was made for currency conversion or outlier treatment.
- The `resolution_type` classifier was applied without human review of individual records. Markets flagged during the description-only deadline-match heuristic were logged internally but not removed from the dataset.

**Was the raw data saved?**

The original Gamma API JSON responses are retained in the ForesightFlow platform database (`raw_metadata` JSONB column of the `markets` table) but are not part of this dataset release. Researchers needing the full API response can re-query the live Gamma API using the `market_id` as the condition ID; responses for resolved markets are stable.

---

## Uses

**Has the dataset been used already?**

The `deadline_resolved` subset was used in Nechepurenko (2026), *ForesightFlow*, for: (i) the corpus-level typology audit (Task 03 Phase 0); (ii) hazard model calibration (exponential fit of T_event timing by category); and (iii) ILS-dl computation across the FFIC deadline-resolved cluster.

**What tasks is the dataset suitable for?**

- *Filtering for ILS scope conditions.* Load the typology, filter to `resolution_type == 'deadline_resolved'` + the relevant `category_fflow`, and proceed to price-level ILS computation on the resulting subset.
- *Training or evaluating resolution-type classifiers.* The dataset provides 911K labelled instances for training improved classifiers. Note the class-imbalance caveat above.
- *Studying the deadline structure of prediction markets.* The 56K deadline-resolved markets, their creation dates, volume distribution, and resolution outcomes constitute a large-scale corpus for studying how markets with explicit deadlines differ from open-ended markets.
- *Mapping category distributions.* The category counts by resolution type allow analysis of whether particular topic areas (military, regulatory, corporate) are more or less likely to be structured as deadline markets.

**What tasks should the dataset NOT be used for?**

- *Treating `unclassifiable` as definitively not deadline-resolved or event-resolved.* The `unclassifiable` class is a conservative fallback; it contains misclassified markets. Do not use the absence of a `deadline_resolved` label as evidence that a market is structurally event-resolved.
- *Treating `category_fflow` as a ground-truth topic taxonomy.* Category labels were produced by a keyword classifier optimised for the ForesightFlow target categories. They are suitable as filters but not as authoritative topic classifications.
- *Volume or resolution analysis without accounting for data completeness.* The `volume_total_usdc` field is null for some markets and reflects Gamma API reporting at ingest time, which may be incomplete for recently created or very low-volume markets.

---

## Distribution

**Will the dataset be distributed to third parties?**

Yes. Released publicly at [github.com/ForesightFlow/datasets](https://github.com/ForesightFlow/datasets) under CC-BY 4.0.

**How will it be distributed?**

Through the public ForesightFlow GitHub organization, as a versioned subdirectory of the `datasets` repository. Each version is a git tag.

**When was the first release?**

April 2026, concurrent with the working draft of the companion paper.

**What license applies?**

The dataset as a whole is released under [CC-BY 4.0](LICENSE). Market questions and descriptions are sourced from the Polymarket Gamma API; Polymarket's own terms govern their original content.

---

## Maintenance

**Who will be maintaining the dataset?**

Maksym Nechepurenko (Devnull FZCO). Hosted on GitHub.

**How can the maintainer be contacted?**

Email: maksym@devnull.ae. GitHub issues on the `ForesightFlow/datasets` repository are also monitored.

**Is there an erratum?**

Errata are tracked in `CHANGELOG.md`.

**Will the dataset be updated?**

Yes. Future versions will extend the corpus to markets created after the 2026-04-27 cutoff, and may incorporate improved classifier versions. Existing records are not modified except to correct factual errors.

**Will older versions continue to be available?**

Yes. Each version is a frozen git tag and remains accessible indefinitely.

---

## Reference

Gebru, Timnit, Jamie Morgenstern, Briana Vecchione, Jennifer Wortman Vaughan, Hanna Wallach, Hal Daumé III, and Kate Crawford. 2021. "Datasheets for Datasets." *Communications of the ACM* 64 (12): 86–92.
