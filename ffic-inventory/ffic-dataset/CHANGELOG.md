# Changelog

All notable changes to the FFIC Inventory are documented here.

The inventory follows append-only versioning: existing case records are not modified except to correct factual errors. Each version is a frozen git tag.

---

## [1.0] — 2026-04-27 (amended 2026-04-29)

### Amendment — 2026-04-29

Expanded `fficd-004` from 3 markets to 11 markets (7 YES + 4 NO) following cross-verification against the DOJ indictment of Gannon Van Dyke (April 23, 2026, U.S. vs. Van Dyke), the first insider-trading case on a prediction market involving classified U.S. military information.

The original 3-market entry was based on a preliminary cluster definition that omitted Van Dyke's other documented YES positions and included one market (`Maduro in U.S. custody by January 31`) incorrectly labeled NO (actual DB value: YES / 1.0). The corrected 11-market entry covers the full Operation Absolute Resolve cluster:

- 7 YES-resolved markets ($19.1 M combined volume), including the primary Van Dyke positions
- 4 NO-resolved markets ($69.2 M combined volume), including deadline-miss markets and one market Van Dyke reportedly traded but lost (invade Venezuela)

DOJ uses simplified naming in the indictment: "Maduro out by January 31" maps to Polymarket's "Maduro in U.S. custody by January 31?" and "US forces in Venezuela by January 31" maps to "US x Venezuela military engagement by January 31, 2026?".

Tag `ffic-inventory-v1` force-updated. No downstream consumers existed at time of correction (pre-submission).

---

## [1.0] — 2026-04-27

Initial release.

### Cases included

- `fficd-001` — 2024 U.S. presidential election (4 markets, $2.96B)
- `fficd-002` — October 2024 Iran strike on Israel (3 markets, $1.04M)
- `fficd-003` — 2026 U.S.–Iran conflict cluster (6 markets, $825.3M)
- `fficd-004` — January 2026 U.S.–Venezuela / Maduro operation cluster (11 markets, $89.2M) *(expanded in 2026-04-29 amendment)*
- `fficd-005` — Bitcoin ETF SEC approval (1 market, $12.6M)
- `fficd-006` — Google Year-in-Search rankings 2025 (3 markets, $5.3M)
- `fficd-007` — FTX / SBF case cluster (3 markets, $9.5M)
- `fficd-008` — Romanian presidential election 2024–2025 (1 market, $326M)

### Total

32 markets, approximately $4.23B in cumulative volume (after 2026-04-29 amendment to fficd-004).

### Known limitations

- Six high-volume markets exceed the public Polymarket subgraph indexer-capacity envelope; trade history requires alternative recovery paths (CLOB price-history endpoint, Dune Analytics SQL, or self-hosted subgraph).
- Public-reporting bias: cases with smaller dollar amounts, less politically salient events, or actors with effective opsec are systematically under-represented.

### Companion materials

- Companion paper: Nechepurenko (2026), *ForesightFlow*, working draft v1.0.
- Code: [github.com/ForesightFlow/platform](https://github.com/ForesightFlow/platform)
