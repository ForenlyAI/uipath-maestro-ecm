# Trigger samples

These files demonstrate how every supported trigger source produces the same canonical
[`IncidentReport`](./incident_report.schema.json) consumed by **Container 1 — Incident Report**.
The flow can be replayed end-to-end without external systems by feeding these files into the
trigger adapters (`python run_pipeline.py`).

## Files

| File | Source | What it simulates |
|---|---|---|
| [`mower_blade_strike.json`](./mower_blade_strike.json) | `vision` | Onboard vision flags a blade strike on a foreign object on a near-road verge — high severity, safety zone `near-road` |
| [`mower_mobility_slope.json`](./mower_mobility_slope.json) | `sensor` | IMU reports the mower stalled and tilting on a `steep-slope` — drivetrain bogged, rollover risk |
| [`mower_boundary_breach.json`](./mower_boundary_breach.json) | `telemetry` | Fleet telemetry shows the unit crossed its geofence toward water — RTK drift, safety zone `near-water` |
| [`mower_charging_fault.json`](./mower_charging_fault.json) | `telemetry` | A slow overnight dock-and-charge cycle — low severity, no safety zone → **autonomous fast-track** |
| [`mower_theft_alert.json`](./mower_theft_alert.json) | `telemetry` | Anti-theft flags an off-hours off-site move in a `public-access` area |
| [`IR-20260606-manual-handheld.json`](./IR-20260606-manual-handheld.json) | `manual` | Field operator logs grass clumping + a mild blade jam via the handheld portal |
| [`IR-20260606-vision-camera.json`](./IR-20260606-vision-camera.json) | `vision` | Onboard camera detects debris lodged in the cutting deck |
| [`IR-20260606-vision-sensor.json`](./IR-20260606-vision-sensor.json) | `sensor` | Tilt sensor flags rollover risk on a steep embankment |

## How adapters use these

Each trigger source has its own raw payload format. The trigger adapter for that source:

1. Validates the raw payload (vendor-specific shape).
2. Maps it to the canonical `IncidentReport` shape (`incident_report.schema.json`).
3. Preserves the raw payload under `vendor.*` so audit can reproduce the trigger.

The BPMN never sees the vendor-specific shape; it only sees the canonical object. Adding a new
trigger source means writing a new adapter, not modifying the BPMN.

## How the Risk Agent reads these

The agentic Fast Track gateway in Container 3 reads `source.detectorConfidence`, `severity`,
`safetyZone`, and `affectedItems[].supplierId` to score each incident. Safety-critical operating
zones (`near-road`, `near-water`, `public-access`, `steep-slope`) bias toward the Fleet Review
Board (HITL). Low-confidence detections (`< 0.8`) add risk regardless of severity.

## Adding new samples

When a new trigger source is integrated (another vision system, a new sensor, a supplier feed),
add a sample here using the same canonical shape. The vendor-specific raw payload goes under
`vendor.<provider>`.
