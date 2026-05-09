# Datasheet for the Polymarket Stylized Facts Dataset

Following Gebru et al. (2021), "Datasheets for Datasets." *Communications of the ACM*.

---

## 1. Motivation

**1.1 For what purpose was the dataset created?**  
To provide per-market stylized-fact measurements for Polymarket binary-event markets as a reusable building block for prediction-market microstructure research, eliminating the need for each research group to re-derive these quantities from the raw PMXT v2 archive.

**1.2 Who created the dataset and on behalf of which entity?**  
Maksym Nechepurenko, Devnull FZCO / ForesightFlow. Released alongside Paper 1 of the four-paper Event-Linked Perpetuals research programme.

**1.3 Who funded the creation of the dataset?**  
Self-funded research; no external funding.

---

## 2. Composition

**2.1 What do the instances represent?**  
Each row in the primary file represents a single Polymarket binary-event market (condition ID) that resolved during the window 2026-04-21 to 2026-04-27 UTC and passed the CC-003 usability filters (minimum lifetime, confirmed UMA OO resolution, Gamma metadata available).

**2.2 How many instances are there?**  
13,314 markets in the primary file. SF7 aggregate has 96 rows (4 classes × 24 hours). SF9 aggregate has 5 rows (one per time-to-resolution bucket).

**2.3 Does the dataset contain all possible instances or is it a sample?**  
Sample. The PMXT v2 archive for the seven-day window contains approximately 110,000+ markets. The 13,314 are a stratified-by-day subsample (seed 20260505, target 10,000 per calendar day) of the usable resolved markets.

**2.4 What data does each instance consist of?**  
Market metadata (condition ID, question text, event class, timestamps, volume, negRisk membership) plus per-market SF measurements where available. SF1 (boundary depth asymmetry ρ) and SF2 (terminal jump magnitude |Δ|) are per-market for 1,648 and 4,225 markets respectively (resume CC-004 pass only). SF4 (half-spread by region) is per-market for 4,911 markets. All other SF measurements are aggregate-only (in `aggregates.json`).

**2.5 Is there a label or target associated with each instance?**  
`resolution_outcome` (0 = NO, 1 = YES) is the UMA OO oracle resolution for each market.

**2.6 Is any information missing from individual instances?**  
- **SF2 (terminal jump):** 23.1% of markets (3,077 / 13,314) lack a usable terminal-jump observation due to order-book illiquidity in the final hour before resolution. CC-006b 50-market sanity sample confirmed these are genuine dark-book markets (50/50 dark books), not computation gaps. These markets carry `sf2_terminal_jump_magnitude = null`.
- **SF1 (boundary depth asymmetry):** 88% of markets lack boundary observations; `sf1_rho` is null for these markets. Boundary region is defined as index < 0.10 or > 0.90, which many markets never reach.
- **SF4 (half-spread):** `sf4_half_spread_boundary_low` and `sf4_half_spread_boundary_high` are null in v1; the CC-004 per-market accumulator emitted only the three interior regions (low, mid, high).
- **SF3, SF5, SF6, SF8, SF9:** No per-market columns. Aggregate-only in CC-004 source.
- **Metadata:** A small fraction of markets may have null `question`, `created_at`, or `volume_total_usdc` if the Gamma API returned incomplete records at cache time.

**2.7 Are there any errors, noise, or redundancies?**  
SF1 and SF2 have two independent coverage cohorts (base pass: files 0–120; resume pass: files 121–167). The primary parquet includes only the resume-pass per-market data (base pass emitted aggregate-only). The two cohorts are disjoint. Both pass the pre-registered floor independently.

**2.8 Is the dataset self-contained?**  
Yes for the compiled measurements. External dependencies (Polymarket Gamma API, UMA OO registry) were used at build time; the compiled parquet files are standalone.

**2.9 Does the dataset contain data that might be considered confidential?**  
No. All data derives from public blockchain events and the public Gamma API.

**2.10 Does the dataset contain data that might cause offense?**  
Market question text is sourced from the Polymarket Gamma API and may include topics related to political events, conflicts, or other sensitive subject matter. This is inherent to prediction markets as a data source.

---

## 3. Collection Process

**3.1 How was the data associated with each instance acquired?**  
Order-book tick data from the PMXT v2 event-stream archive (168 hourly Parquet files, 2026-04-21 to 2026-04-27). Market metadata (question, tags, timestamps, volume) from the Polymarket Gamma REST API. Resolution outcomes from the UMA Optimistic Oracle v3 subgraph via Goldsky (The Graph).

**3.2 What mechanisms or procedures were used to collect the data?**  
Automated pipeline: (1) archive download via CC-002; (2) G5 evaluation (CC-003.11) joining archive ticks with Gamma metadata and UMA resolutions; (3) stylized-fact computation (CC-004 base + resume passes). All code is in the companion repository.

**3.3 If the dataset is a sample, what was the sampling strategy?**  
Stratified-by-day sampling with seed 20260505 and target 10,000 markets per calendar day. The strategy addresses single-day chronological selection bias (documented in companion paper Appendix B): drawing only from one day would over-represent that day's market category composition, which varies significantly day-to-day due to sports-event scheduling.

**3.4 Who was involved in the data collection process?**  
Automated pipeline; no crowdsourcing or human annotation for the core dataset. Market question text and resolution outcomes are sourced from Polymarket and UMA respectively.

**3.5 Over what timeframe was the data collected?**  
Source archive: 2026-04-21 to 2026-04-27 UTC (seven days). Pipeline execution: 2026-05-05 to 2026-05-07. Dataset compiled: 2026-05-09.

**3.6 Were any ethical review processes conducted?**  
Not applicable. The dataset consists of public market data from a public prediction-market platform.

**3.7 Did you collect the data from the individuals in question directly?**  
Not applicable. Data is from a public blockchain and public API.

---

## 4. Preprocessing / Cleaning / Labeling

**4.1 Was any preprocessing or cleaning of the data done?**  
Yes. Usability filters applied before inclusion in the sample: minimum observed lifetime ≥ 1 hour; confirmed UMA OO resolution within the archive window; Gamma metadata available (title, event_class, timestamps). Markets failing these filters are excluded. EVENT_CLASS_RULE_VERSION v1 applied (keyword + feeType classifier). Full filter specification in companion repository at `ingest/EVENT_CLASS_DERIVATION.md`.

**4.2 Was the "raw" data saved in addition to the preprocessed data?**  
The raw PMXT v2 archive files are not distributed with this dataset (168 × ~430 MB files). The `build_manifest.json` contains SHA256 checksums of the source archive files and the pre-computed CC-003.11 / CC-004 outputs.

**4.3 Is the software that was used to preprocess/clean/label the data available?**  
Yes. The full pipeline is in the companion repository. `code/build_dataset.py` in this dataset package reproduces the parquet files from CC-003.11 + CC-004 outputs; `code/README.md` describes Path B for full rebuild from the archive.

**4.4 Is there any other information?**  
SF computations use 64-bit floating-point arithmetic throughout. Rounding in `aggregates.json` is for display only; full-precision values are in the parquet files.

---

## 5. Uses

**5.1 Has the dataset been used for any tasks already?**  
Yes. The companion paper (Nechepurenko 2026) uses this dataset as the empirical foundation for Sections 4–6: sample characterization, stylized-fact reporting, and risk-engine calibration. All nine stylized facts reported in Paper 1 are derived from this dataset.

**5.2 Is there a repository that links to any or all papers that use the dataset?**  
The ForesightFlow datasets repository (https://github.com/ForesightFlow/datasets) tracks usage. The companion paper preprint will be linked from the dataset README when published.

**5.3 What (other) tasks could the dataset be used for?**  
- Comparative microstructure analysis with other prediction-market venues (Kalshi, Manifold, PredictIt)
- Calibration of microstructure models adapted to binary bounded-event underlyings
- Event-study analysis using the SF3 (basis in news vs control windows) measurements
- Benchmarking alternative stylized-fact computation methods against this baseline

**5.4 Is there anything about the composition of the dataset that might affect future uses?**  
Sports-dominance (77.9% of three-class total) limits per-class generalizability for politics (408 markets, 3.1%) and crypto (1,518 markets, 11.4%). Single-week empirical window; seasonal and market-condition variation is not captured. SF3, SF5, SF6, SF8, SF9 are aggregate-only; per-market analysis of these SFs is not supported by this dataset version.

**5.5 Are there tasks for which the dataset should not be used?**  
- **Real-time trading or deployment:** The dataset is a static snapshot. Stylized facts reflect the 2026-04-21 to 2026-04-27 week only.
- **Cross-platform generalization:** All markets are Polymarket-specific. Claims about "prediction markets in general" based solely on this dataset are not warranted without cross-platform validation.
- **Multi-week temporal generalization:** Single-week window limits temporal extrapolation. Seasonal effects, platform-composition shifts, and macro regime changes are not captured.

---

## 6. Distribution

**6.1 Will the dataset be distributed to third parties?**  
Yes. Publicly available at https://github.com/ForesightFlow/datasets/tree/main/pmxt-stylized-facts-v1.

**6.2 How will the dataset be distributed?**  
GitHub repository, tagged at `pmxt-stylized-facts-v1`. Parquet format (primary file) and JSON (aggregates). No LFS required (~5–8 MB total).

**6.3 When will the dataset be distributed?**  
At the time of tagging `pmxt-stylized-facts-v1`.

**6.4 Will the dataset be distributed under a copyright or other IP license?**  
CC-BY 4.0. Market questions and descriptions originate from the Polymarket Gamma API; Polymarket's terms of service govern their original data.

**6.5 Have any third parties imposed IP-based or other restrictions on the data?**  
Polymarket's terms of service apply to the original market question text. The CC-BY 4.0 license applies to the compiled dataset (stylized-fact measurements, structured manifest, classification labels).

**6.6 Do any export controls or other regulatory restrictions apply?**  
Not to the authors' knowledge.

---

## 7. Maintenance

**7.1 Who will be supporting, hosting, or maintaining the dataset?**  
Maksym Nechepurenko / ForesightFlow. Contact: maksym@devnull.ae or via GitHub issue.

**7.2 How can the owner/curator/manager of the dataset be contacted?**  
GitHub issues on the ForesightFlow/datasets repository, or email at maksym@devnull.ae.

**7.3 Is there an erratum?**  
Not at initial release. Errors will be documented in `CHANGELOG.md`.

**7.4 Will the dataset be updated?**  
Future versions (v2, v3) will extend the empirical window or add per-market coverage for SF5/SF6/SF8/SF9 as the four-paper programme develops. Existing records will not be modified except to correct factual errors. Each version is a distinct git tag.

**7.5 If the dataset relates to people, are there applicable limits on the retention of the data associated with the instances?**  
Not applicable. The dataset contains no personally identifiable information. Markets are identified by on-chain condition IDs; question text is public prediction-market content.

**7.6 Will older versions of the dataset continue to be supported?**  
Yes. Each version is a distinct git tag (e.g., `pmxt-stylized-facts-v1`) and will remain accessible in perpetuity via the GitHub repository.

**7.7 If others want to extend/augment/build on the dataset, are there any requirements?**  
CC-BY 4.0 requires attribution. The `CITATION.cff` file provides the recommended citation format. Derivative datasets should note which version of this dataset they build on.
