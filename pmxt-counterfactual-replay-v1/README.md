# pmxt-counterfactual-replay-v1

**Counterfactual Replay Results for Polymarket Binary Markets (Bundle 2)**

Per-(engine/mechanic, leverage, class) summary statistics from two counterfactual
simulation experiments (E2 and E3) on 13,000+ resolved Polymarket binary-event
markets. Companion dataset for Nechepurenko (2026) Paper 1.

| Field        | Value |
|---|---|
| Version      | 1.0 |
| Tag          | `pmxt-counterfactual-replay-v1` |
| Released     | 2026-05-10 |
| License      | CC-BY 4.0 |
| Markets      | E2: 13,306 · E3: 13,115 |
| Snapshot     | 2026-04-21 to 2026-04-27 |
| Companion    | [pmxt-stylized-facts-v1](../pmxt-stylized-facts-v1/) |

---

## Background

This dataset bundles the outputs of two counterfactual simulation experiments
conducted on the resolved-market subset of the `pmxt-stylized-facts-v1` corpus:

**E2 (CC-007b) — Margin formula recalibration**
Three engine variants (E0 baseline, E1 EMA-vol, E2 recalibrated) are compared
on survivability, drawdown, and trader PnL. The recalibrated E2 engine removes
the index-price multiplier from the vol margin term.

**E3 (CC-008) — Resolution-zone protocol comparison**
Four resolution-zone mechanics (R0 through R3) are compared on final-hour
liquidation rates, bad-debt frequency, and average PnL across leverages 2×–10×.
R3 (multi-stage halt with circuit-breaker) reduces final-hour liquidation by
80.4% vs the naive R0 baseline.

---

## Files

```
data/
  e2a-survivability-v1.parquet       75 rows — E2a: survivability & liquidation rate
  e2b-drawdown-v1.parquet            15 rows — E2b: total drawdown by engine × class
  e2c-pnl-distribution-v1.parquet    3 rows  — E2c: synthetic trader PnL percentiles
  e3-liquidation-rate-v1.parquet     80 rows — E3: final-hour liquidation rate
  e3-bad-debt-v1.parquet             80 rows — E3: bad-debt event frequency
  e3-pnl-v1.parquet                  80 rows — E3: average terminal PnL (USDC)
  aggregates.json                            — key summary statistics
  engine-parameters-v1.json                  — locked engine/mechanic parameters
build_manifest.json                          — SHA-256 checksums + provenance
```

---

## Engine and Mechanic Definitions

### E2 Engines (margin formula variants)

| Engine | Description |
|---|---|
| `E0` | Baseline — constant volatility estimate, no dynamic margin |
| `E1` | EMA-vol — exponential moving average vol, dynamic margin (no index scaling) |
| `E2` | Recalibrated — `M_SIGMA·σ̂ + M_JUMP·p_jump·φ + KAPPA_BOOK/depth` (CC-007b: vol term has no index multiplier) |

### E3 Resolution-Zone Mechanics

| Mechanic | Description |
|---|---|
| `R0` | Naive forced expiry — no resolution-zone rules; positions held to oracle settlement |
| `R1` | Leverage compression only — max leverage ramps linearly from L to 1× over the final Δ_R = 1 h |
| `R2` | R1 + boundary funding correction — extra `C_BOUNDARY` per-hour funding activates when `\|mid − 0.5\| > DELTA_BOUND = 0.10` |
| `R3` | Full multi-stage halt — M₁ zone compression (2Δ_R), M₂ notional taper (Δ_R/3 to Δ_R), M₃ position freeze (<Δ_R/3) + circuit-breaker on vol spike ≥ 3× EMA |

Full parameter values: `data/engine-parameters-v1.json`.

---

## Schema

### `e2a-survivability-v1.parquet`

| Column | Type | Description |
|---|---|---|
| `engine` | string | `E0` / `E1` / `E2` |
| `leverage` | int | 1 / 2 / 3 / 5 / 10 |
| `class` | string | `crypto` / `politics` / `sports` / `other` / `all` |
| `survivability_rate` | float64 | fraction of positions that reach expiry without liquidation |
| `liquidation_rate` | float64 | fraction of positions liquidated before expiry |

### `e2b-drawdown-v1.parquet`

| Column | Type | Description |
|---|---|---|
| `engine` | string | `E0` / `E1` / `E2` |
| `class` | string | `crypto` / `politics` / `sports` / `other` / `all` |
| `total_drawdown` | float64 | sum of position losses (USDC) across all markets |

### `e2c-pnl-distribution-v1.parquet`

| Column | Type | Description |
|---|---|---|
| `engine` | string | `E0` / `E1` / `E2` |
| `p10` / `p25` / `p50` / `p75` / `p90` | float64 | PnL percentiles (USDC, 1000 USDC notional) |
| `mean` | float64 | mean PnL (USDC) |

### `e3-liquidation-rate-v1.parquet`, `e3-bad-debt-v1.parquet`, `e3-pnl-v1.parquet`

| Column | Type | Description |
|---|---|---|
| `mechanic` | string | `R0` / `R1` / `R2` / `R3` |
| `leverage` | int | 2 / 3 / 5 / 10 |
| `class` | string | `crypto` / `politics` / `sports` / `other` / `all` |
| `value` | float64 | liquidation rate / bad-debt frequency / average PnL (USDC) |

---

## Key Results

### E2 Recalibration

| Metric | E2 vs E0 at L=5× |
|---|---|
| Liquidation rate reduction | -5.96% |
| Drawdown reduction | +5.14% |
| Passes pre-registered floor (≥10% liq reduction) | ❌ |

### E3 Resolution-Zone Protocol

| Mechanic | Final-hour liq rate (all, L=5×) | vs R0 |
|---|---|---|
| R0 (baseline) | 0.00107 | — |
| R1 (leverage compression) | 0.00115 | +7.5% |
| R2 (R1 + boundary funding) | 0.00115 | +7.5% |
| R3 (full halt) | 0.000209 | **−80.4%** |

Pre-registered floors:
- Floor 1 (R3 liq reduction ≥50% vs R0): **PASS** (80.4%)
- Floor 2 (R3 bad-debt reduction ≥75% vs R0): **FAIL** (−2.4%, slight increase)

---

## Quick Start

```python
import polars as pl

# E3 liquidation rates
liq = pl.read_parquet("data/e3-liquidation-rate-v1.parquet")
print(liq.filter(pl.col("class") == "all").pivot("mechanic", index="leverage", values="value"))

# E2 survivability at leverage 5×
surv = pl.read_parquet("data/e2a-survivability-v1.parquet")
print(surv.filter((pl.col("leverage") == 5) & (pl.col("class") == "all")))
```

---

## Provenance

- E2 simulation: `evaluation/counterfactual_replay.py` (CC-007b), run 2026-05-08
- E3 simulation: `evaluation/resolution_zone_test.py` (CC-008), run 2026-05-09
- Build script: `evaluation/build_bundle2.py` (CC-011), run 2026-05-10
- Source repo: `ForesightFlow/event-linked-perps` (master, post-CC-010)
- Engine parameters: `data/engine-parameters-v1.json`

---

## Citation

```bibtex
@misc{nechepurenko2026elp,
  title  = {Resolution-Aware Perpetual Futures on Binary Prediction Markets:
             An Empirical Risk-Design Framework Using Polymarket Data},
  author = {Nechepurenko, Maksym},
  year   = {2026},
  note   = {Working paper. Companion datasets: pmxt-stylized-facts-v1,
             pmxt-counterfactual-replay-v1.}
}
```

---

## License

[CC-BY 4.0](LICENSE) — Maksym Nechepurenko / Devnull FZCO, 2026.
