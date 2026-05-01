# Changelog

All notable changes to the FFIC Inventory are documented here.

The inventory follows append-only versioning: existing case records are not modified except to correct factual errors. Each version is a frozen git tag.

---

## [1.0] — 2026-04-27

Initial release.

### Cases included

- `fficd-001` — 2024 U.S. presidential election (4 markets, $2.96B)
- `fficd-002` — October 2024 Iran strike on Israel (3 markets, $1.04M)
- `fficd-003` — 2026 U.S.–Iran conflict cluster (6 markets, $825.3M)
- `fficd-004` — Maduro / Venezuela cluster (3 markets, $70.5M)
- `fficd-005` — Bitcoin ETF SEC approval (1 market, $12.6M)
- `fficd-006` — Google Year-in-Search rankings 2025 (3 markets, $5.3M)
- `fficd-007` — FTX / SBF case cluster (3 markets, $9.5M)
- `fficd-008` — Romanian presidential election 2024–2025 (1 market, $326M)

### Total

24 markets, approximately $4.21B in cumulative volume.

### Known limitations

- Six high-volume markets exceed the public Polymarket subgraph indexer-capacity envelope; trade history requires alternative recovery paths (CLOB price-history endpoint, Dune Analytics SQL, or self-hosted subgraph).
- Public-reporting bias: cases with smaller dollar amounts, less politically salient events, or actors with effective opsec are systematically under-represented.

### Companion materials

- Companion paper: Nechepurenko (2026), *ForesightFlow*, working draft v1.0.
- Code: [github.com/ForesightFlow/platform](https://github.com/ForesightFlow/platform)
