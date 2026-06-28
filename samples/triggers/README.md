# Trigger samples

These files demonstrate how every supported source produces the same canonical
[`IncidentReport`](./incident_report.schema.json) (a training-run anomaly event) consumed by
**Container 1 — Anomaly Intake**. The flow can be replayed end-to-end without external systems by
feeding these files into the source adapters (`python run_pipeline.py`).

## Files

| File | Source | What it simulates |
|---|---|---|
| [`gradient_collapse.json`](./gradient_collapse.json) | `telemetry` | Reward telemetry flags a reward collapse + vanished gradients on a `high-cost-gpu` run — high severity |
| [`loss_divergence.json`](./loss_divergence.json) | `telemetry` | Critic loss diverging and reward crashing on a `long-running` multi-day job — unstable training |
| [`gpu_oom_fault.json`](./gpu_oom_fault.json) | `monitor` | Hardware monitor catches a CUDA OOM crash on a `production-bound` run (model bound for the robot) |
| [`idle_spend.json`](./idle_spend.json) | `telemetry` | A spot instance left idle after the run finished — low severity, no critical zone → **autonomous fast-track** |
| [`quota_exhaustion.json`](./quota_exhaustion.json) | `monitor` | Cloud GPU quota nearly exhausted on the training project |
| [`IR-20260606-manual-console.json`](./IR-20260606-manual-console.json) | `manual` | A researcher flags a reward plateau via the console |
| [`IR-20260606-logs-trainer.json`](./IR-20260606-logs-trainer.json) | `logs` | Trainer stdout shows intermittent NaN loss (possible gradient explosion) |
| [`IR-20260606-monitor-gpu.json`](./IR-20260606-monitor-gpu.json) | `monitor` | GPU monitor reports thermal throttling / overheat on a training node |

## How adapters use these

Each source has its own raw payload format. The adapter for that source:

1. Validates the raw payload (source-specific shape).
2. Maps it to the canonical `IncidentReport` shape (`incident_report.schema.json`).
3. Preserves the raw payload under `vendor.*` so audit can reproduce the trigger.

The BPMN never sees the source-specific shape; it only sees the canonical object. Adding a new
source means writing a new adapter, not modifying the BPMN.

## How the Risk Agent reads these

The agentic Fast Track gateway in Container 3 reads `source.detectorConfidence`, `severity`,
`safetyZone`, and `affectedItems[].supplierId` to score each anomaly. Critical zones
(`high-cost-gpu`, `production-bound`, `public-benchmark`, `long-running`) bias toward the Researcher
Review Board (HITL). Low-confidence detections (`< 0.8`) add risk regardless of severity.

## Adding new samples

When a new source is integrated (another telemetry stream, a new monitor, a billing feed),
add a sample here using the same canonical shape. The source-specific raw payload goes under
`vendor.<provider>`.
