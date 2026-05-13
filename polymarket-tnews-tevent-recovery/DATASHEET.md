# Datasheet: Polymarket T_news / T_event Recovery Dataset (v1)

Following [Gebru et al. (2021), "Datasheets for Datasets"](https://arxiv.org/abs/1803.09010).

## Motivation

**For what purpose was the dataset created?**
The dataset was created to make public-event timestamps for resolved Polymarket
markets reusable across the research community. Event-time anchors are a prerequisite
for any information-leakage, event-study, or price-discovery analysis on prediction
markets, but no public corpus of such timestamps existed prior to this release. The
dataset was built to support the ForesightFlow programme of papers on informed-trading
detection in decentralized prediction markets.

**Who created the dataset and on behalf of which entity?**
The dataset was assembled by Maksym Nechepurenko (Devnull FZCO, Dubai, UAE) as part
of the ForesightFlow research programme. No external funding was used; the project
is internally funded.

**Who funded the creation of the dataset?**
Devnull FZCO internal research budget.

## Composition

**What do the instances that comprise the dataset represent?**
Each instance represents one resolved Polymarket market and provides:
- An identifier (Polymarket condition ID)
- The market question text
- A recovered timestamp for the public event or news arrival
- The tier and method used to recover the timestamp
- A confidence score
- Source URLs (where available)
- Category and resolution metadata

**How many instances are there?**
2,052 markets total. Tier breakdown: Tier 1 (UMA Oracle, gold standard) = 12; Tier 2
(GDELT / resolved-at proxy) = 1,993; Tier 3 (LLM-assisted multi-source verification)
= 47.

**Does the dataset contain all possible instances or is it a sample?**
The dataset is a sample drawn from the universe of resolved Polymarket markets
(911,237 markets in our internal corpus as of 2026-04-30). Tier 1 coverage is
limited to markets where UMA proposer evidence URLs are publicly queryable. Tier 2
covers markets with substantive trading history above a $50K volume threshold and
GDELT keyword matches. Tier 3 was applied selectively to high-stakes markets
relevant to the ForesightFlow Insider Cases (FFIC) inventory.

**What data does each instance consist of?**
Structured fields (see README schema): IDs, timestamps, categorical labels,
source URLs (Tier 1 and Tier 3 only). No raw market trade data, no wallet data,
no price series.

**Is there a label or target associated with each instance?**
Yes: each record's `recovered_timestamp` is the labeled anchor. Confidence scores
and tier labels indicate provenance.

**Is any information missing from individual instances?**
- Tier 2 records have no source URLs (proxy method does not require them).
- Some Tier 1 records have one source URL only (UMA proposer evidence URL).
- `verification_notes` field is sparse for Tier 2 records.

**Are relationships between individual instances made explicit?**
Markets sharing the same `fflow_category` and the same underlying event (e.g.,
multiple Iran-conflict markets resolving on related events) are not explicitly
linked, but can be grouped via the `fflow_category` field and timestamp clustering.

**Are there recommended data splits?**
No formal train/validation/test split. Recommended use:
- Tier 1 (n=12) as gold standard for evaluating timestamp-recovery methods.
- Tier 3 (n=47) for case studies where source provenance matters.
- Tier 2 (n=1,993) for population-level analyses where the structural proxy is
  adequate.

**Are there any errors, sources of noise, or redundancies in the dataset?**
- Tier 2 confidence is set to 0.60 to reflect the structural-proxy character of
  the anchor.
- 119 esports markets retain Tier-2 records from before the v1.1 taxonomy
  correction; these are flagged via `fflow_category = "esports"`.
- LLM-derived Tier 3 records may contain interpretation differences from human
  expert judgement on edge cases.

**Is the dataset self-contained, or does it link to or rely on external resources?**
Self-contained for analyses that use only the recovered timestamps and metadata.
Source URLs in Tier 1 and Tier 3 records link to external news articles whose
availability is outside our control.

**Does the dataset contain confidential or restricted information?**
No. All data is derived from publicly observable Polymarket on-chain state and
publicly accessible news articles.

**Does the dataset contain data that might be considered sensitive in any way?**
No. The dataset contains no personal data, no wallet addresses, no trade-level
data. Market questions are public-facing strings already published on Polymarket.

## Collection process

**How was the data associated with each instance acquired?**
- Tier 1: UMA Oracle proposer evidence URLs queried from the on-chain Optimistic
  Oracle state.
- Tier 2: GDELT (Global Database of Events, Language, and Tone) keyword matches
  against market questions, with the resolved-at offset (24h) used as the structural
  anchor.
- Tier 3: Claude Haiku 4.5 LLM with the `web_search_20250305` tool, prompted to
  identify the canonical public-event date with multi-source verification.

**What mechanisms or procedures were used to collect the data?**
Custom Python pipelines reading from:
- Polymarket subgraph (The Graph network) for market metadata and resolution state
- UMA Oracle on-chain queries via Polygon JSON-RPC
- GDELT BigQuery export for news event records
- Anthropic API for LLM recovery with web search

**Over what timeframe was the data collected?**
Data collection ran intermittently 2024-09 through 2026-04. Most Tier 2 records
were generated in bulk runs during 2025-Q4 and 2026-Q1. Tier 3 records were
generated on-demand for FFIC-relevant cases.

**Were any ethical review processes conducted?**
No formal IRB review was conducted. The data is entirely publicly observable
on-chain state and publicly accessible news content. No human subjects were
involved.

## Preprocessing / cleaning / labeling

**Was any preprocessing/cleaning/labeling of the data done?**
Yes:
- Timestamp normalization to UTC ISO 8601.
- Category labels assigned via the ForesightFlow taxonomy (v1.1, post-esports
  correction).
- Confidence scores assigned per-tier as documented.
- Duplicate detection and removal for markets that appeared in multiple tiers
  (no markets are in v1 at multiple tiers; the highest-tier label wins).

**Was the "raw" data saved in addition to the preprocessed/cleaned/labeled data?**
Raw Polymarket subgraph data and raw GDELT records are preserved in our internal
database. Raw LLM completions for Tier 3 are stored but not released in v1.

**Is the software used to preprocess/clean/label the data available?**
The ForesightFlow platform code that generated these labels is released at
[github.com/ForesightFlow/platform](https://github.com/ForesightFlow/platform).
The taxonomy-correction scripts are in the same repository.

## Uses

**Has the dataset been used for any tasks already?**
Yes. The dataset (or earlier internal versions) was used in:
- Nechepurenko (2026), "Empirical Evaluation of Deadline-Resolved Information
  Leakage on Documented Polymarket Insider Cases" (SSRN 6687398)
- Nechepurenko (2026), "ForesightFlow: An Information Leakage Score Framework"
  (SSRN 6687361)

**What (other) tasks could the dataset be used for?**
- Event studies on Polymarket markets
- Benchmarking alternative timestamp-recovery methods (LLM-assisted, GDELT-based,
  proposer-evidence-based)
- Information-leakage analyses requiring an event anchor
- Studies of news-to-resolution lag distributions

**Is there anything about the composition of the dataset or the way it was collected
and preprocessed/cleaned/labeled that might impact future uses?**
- Tier 2 anchors are structural proxies, not factual recoveries. Population-level
  analyses are appropriate; individual-market case studies should prefer Tier 3 or
  Tier 1 anchors.
- Tier 3 LLM provenance: while sources are cited, the LLM's interpretation of
  "first authoritative report" is a methodological choice.

**Are there tasks for which the dataset should not be used?**
- The dataset should NOT be used as ground truth for evaluating LLM web-search
  capabilities in a circular way (Tier 3 was generated by an LLM with web search).
- The dataset should NOT be used for any commercial trading application that
  treats Tier 2 proxy timestamps as factual public-event times.

## Distribution

**Will the dataset be distributed to third parties outside of the entity on behalf
of which the dataset was created?**
Yes. Released openly via [github.com/ForesightFlow/datasets](https://github.com/ForesightFlow/datasets).

**How will the dataset be distributed?**
Git repository, CC-BY 4.0 license. JSONL and CSV formats. SHA-256 manifest for
verification.

**Will the dataset be distributed under a copyright or other intellectual property
(IP) license, and/or under applicable terms of use (ToU)?**
CC-BY 4.0. See LICENSE file.

**Have any third parties imposed IP-based or other restrictions on the data
associated with the instances?**
No. All upstream sources (Polymarket public state, GDELT, news articles cited by
URL) are publicly accessible.

## Maintenance

**Who will be supporting/hosting/maintaining the dataset?**
Maksym Nechepurenko / Devnull FZCO.

**How can the owner/curator/manager of the dataset be contacted?**
- Email: maksym@devnull.ae
- GitHub Issues: [github.com/ForesightFlow/datasets/issues](https://github.com/ForesightFlow/datasets/issues)

**Will the dataset be updated?**
Periodic v2 / v3 releases as the underlying corpus grows. Major changes (schema
revisions, taxonomy corrections) trigger a version bump.

**If others want to extend/augment/build on/contribute to the dataset, is there a
mechanism for them to do so?**
Yes. Pull requests welcome at github.com/ForesightFlow/datasets.
