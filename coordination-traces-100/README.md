# coordination-traces-100

**LLM multi-agent coordination traces on 100 Polymarket binary prediction markets.**

This dataset accompanies **"Coordination as an Architectural Layer for LLM-Based
Multi-Agent Systems"** (Nechepurenko & Shuvalov, 2026). It contains the full
reasoning traces produced by five coordination configurations evaluated on 100
resolved Polymarket binary prediction markets, along with the Murphy decomposition
leaderboard from the paper.

---

## Contents

```
data/
├── markets.jsonl                   100 market definitions (question, category,
│                                   outcome, baseline price, volume)
├── traces/
│   ├── independent_ensemble.jsonl  100 predictions with full reasoning traces
│   ├── peer_critique_debate.jsonl
│   ├── orchestrator_specialist.jsonl
│   ├── sequential_pipeline.jsonl
│   └── consensus_alignment.jsonl
└── leaderboard.csv                 per-config Brier/Alpha/REL/RES (Table 1 in paper)
analysis/
└── explore_traces.ipynb            15-line notebook: load traces, compute Brier
```

Total: ~9.3 MB. 500 trace records (100 markets × 5 configurations).

---

## Quick start

```python
import json, numpy as np

# Load traces for one configuration
traces = []
with open("data/traces/sequential_pipeline.jsonl") as f:
    for line in f:
        traces.append(json.loads(line))

# Compute Brier score
brier = np.mean([(t["probability"] - t["outcome"])**2
                 for t in traces if t["outcome"] is not None])
print(f"sequential_pipeline Brier: {brier:.4f}")  # → 0.1531
```

See `analysis/explore_traces.ipynb` for a complete worked example.

---

## Schema

### `data/markets.jsonl`

Each line is one market:

| Field | Type | Description |
|---|---|---|
| `marketId` | string | Polymarket condition ID (0x…) |
| `marketIndex` | int | Row index (0–99), matches `traces/*.jsonl` |
| `question` | string | Binary resolution question |
| `description` | string | Resolution criteria |
| `category` | string | One of: crypto, politics, sports, economics, geopolitics, entertainment |
| `resolvedAt` | ISO date | Resolution timestamp |
| `resolutionOutcome` | 0 or 1 | Ground-truth outcome |
| `baselineMidPrice` | float [0,1] | Polymarket mid-price ≥24h before resolution |
| `volumeUsdc` | float | Total traded volume in USDC |

### `data/traces/*.jsonl`

Each line is one (configuration, market) prediction:

| Field | Type | Description |
|---|---|---|
| `configName` | string | Configuration identifier |
| `marketIndex` | int | Matches `markets.jsonl` |
| `question` | string | Market question (denormalised for convenience) |
| `probability` | float [0,1] | Final predicted probability |
| `baseline` | float [0,1] | Market baseline mid-price |
| `outcome` | 0 or 1 | Ground-truth outcome |
| `trace.configName` | string | Same as top-level `configName` |
| `trace.calls` | array | LLM call records (see below) |
| `trace.totalTokens` | int | Sum of input + output tokens |
| `trace.totalCostUsd` | float | Cost in USD |
| `trace.totalDurationMs` | int | Wall-clock time |
| `_failure` | string? | Present only on fallback predictions (0.5); contains error message |

Each element of `trace.calls`:

| Field | Description |
|---|---|
| `agentRole` | Role label (e.g., "researcher", "analyst", "forecaster") |
| `callIndex` | Position in the call sequence |
| `request.systemPrompt` | Full system prompt sent to the model |
| `request.userPrompt` | User-side message |
| `response.text` | Model response text |
| `response.toolCalls` | Array of tool calls made during the turn |
| `usage` | `{promptTokens, completionTokens, totalTokens}` |
| `costUsd` | Per-call cost |
| `durationMs` | Per-call wall time |

### `data/leaderboard.csv`

| Column | Description |
|---|---|
| `config` | Configuration name |
| `n` | Number of markets scored |
| `brier` | Mean Brier score (lower is better) |
| `alpha` | Alpha = Brier_market − Brier_agent (positive = beats market) |
| `alpha_sem` | Standard error of Alpha |
| `UNC` | Murphy uncertainty component |
| `REL` | Murphy reliability (calibration error; lower is better) |
| `RES` | Murphy resolution (discrimination; higher is better) |
| `tokens_per_market` | Mean tokens used per market |
| `cost_usd_per_market` | Mean cost in USD per market |

---

## Dataset statistics

- **Markets:** 100 binary Polymarket prediction markets
- **Categories:** crypto (17), politics (16), sports (17), economics (17), geopolitics (16), entertainment (17)
- **Resolution window:** 2025-08-01 to 2026-04-01 (all after model training cutoff of 2025-08-01)
- **Baseline Brier (market consensus):** 0.1525 (mean)
- **Model:** claude-opus-4-6 (Anthropic)
- **Total predictions:** 500 (100 markets × 5 configurations)
- **Failures (0.5 fallback):** 6 (transient network errors)
- **Total cost to generate:** ~$109.65 USD
- **Total tokens:** 17,095,785

---

## License

[CC-BY 4.0](LICENSE). You are free to share and adapt this dataset for any purpose,
provided appropriate credit is given.

## Citation

See [CITATION.cff](CITATION.cff) or:

```bibtex
@misc{nechepurenko2026coordination,
  author = {Nechepurenko, Maksym and Shuvalov, Pavel},
  title  = {Coordination as an Architectural Layer for {LLM}-Based
            Multi-Agent Systems},
  year   = {2026},
  note   = {Working paper — arXiv DOI to be added after submission}
}
```
