# uipath-maestro-ecm — Agentic Robotic Lawn-Mower Fleet Ops on UiPath Maestro

> [!IMPORTANT]
> ### 🏆 GRAND PRIZE POOL: $48,000 USD!
> **Grand Prize:** $8,000 USD Cash + Global UiPath Recognition! Let's automate the enterprise with fütüristik AI Orchestration! 🤖💼


[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)

> An open-source framework for running **robotic lawn-mower fleet incident triage & remediation** as an **agentic, human-in-the-loop (HITL) orchestration** on **UiPath Maestro BPMN** — combining UiPath's two signature strengths: **agentic AI** (Agent Builder decisioning) and **RPA** (robots that execute into the fleet's legacy/back-office systems).

When an autonomous robotic mower flags a fault in the field — a blade strike on a roadside verge, a stall on a steep slope, a boundary/geofence breach toward water, an anti-theft move — it must be triaged in seconds and remediated systematically. This project orchestrates that whole lifecycle, from the moment a mower (or its fleet platform) raises an incident to the compliance-audited dispatch of a repair, as a **BPMN process where AI agents do the analysis and humans approve the critical safety and cost gates.**

## Where this fits — the robotic-mower stack

| Stage | Project | Role |
|---|---|---|
| **Deploy** | [`gcp`](https://github.com/Forenly/gcp) | Pick the right mower for a yard + plan the install |
| **Operate** | [`gemini-xprize`](https://github.com/Forenly/gemini-xprize) — FleetMind | Run the autonomous day-to-day ops loop |
| **Govern** | **`uipath-maestro` (this repo)** | **Triage incidents + run human-approved remediation** (the governance / HITL layer) |
| **Respond** | [`protocol-sift-dfir`](https://github.com/Forenly/protocol-sift-dfir) | Forensics when a unit is compromised |

Reference platform across all four: **Segway Navimow X3-class** ROS 2 mower fleet.

## The two UiPath pillars (what we lean on)

- **Agentic** — the decisioning runs as **UiPath Agent Builder** agents: a **Fleet AI Analyst** (classify + Safety Risk score), an **Impact Agent** (economic + organizational impact → routing), and a compliance-summary agent. They reason over each incident and decide *fast-track vs human review*.
- **RPA** — once an action is approved, a **UiPath RPA robot** executes it into systems that have **no clean API**: the dealer/warranty portal, the parts ERP, and the legacy fleet CMMS — driven through their UI when needed, plus API Workflows where an API exists.

## What it does

- **8 process containers** modeling the full fleet incident lifecycle (incident trigger → fault analysis → safety/impact routing → approved remediation & audit) as Maestro BPMN subprocesses.
- **9 roles** as BPMN swimlanes — some realized as autonomous LLM agents (Fleet AI Analyst, Safety Risk Agent), others as human-in-the-loop review boards via UiPath Action Center.
- **An agentic "Fast Track" gateway** — the Safety Risk Agent scores each incident and bypasses the full review board for low-risk, contained faults (auto-remediate).
- **Vendor-agnostic triggers** — onboard vision, onboard sensors (IMU/lidar), fleet telemetry, or a field-operator handheld all normalize to one canonical `IncidentReport`.
- **Audit-grade traceability** — immutable log entries at every gateway and task node.

## The 8 fleet containers

```
Process 1 · Incident Intake
  1. Incident Report       Mower/telemetry → Fleet AI Analyst → Fleet Inspector HITL → disposition
  2. Manual Intervention   Field operator handheld or fixed sensor flags a fault + feedback loop

Process 2 · Analysis & Safety Routing
  3. Risk & Safety Analysis Fault → Safety Risk Agent → Fast Track OR Fleet Review Board (HITL)
  4. Impact Analysis        Economic + organizational impact (unit cost / downtime / liability / fleet reach)

Process 3 · Action & Compliance
  5. Remediation Plan      Analyst Agent + Maintenance Specialist draft a service playbook → Ops HITL
  6. Dispatch Remediation  Send a field technician or repair action; pause/recall the unit if unsafe
  7. Legacy Write-back     **RPA robot** writes to dealer/warranty portal, parts ERP, legacy fleet CMMS
  8. Quality Assurance     Compliance-summary agent + immutable audit log + supervisor sign-off
```

## How it's built

| Layer | Choice |
| --- | --- |
| **Orchestration** | UiPath Automation Cloud + Maestro BPMN |
| **UiPath components** | **Agent Builder** (agentic) · Maestro BPMN · Action Center (HITL) · **RPA Robot** + API Workflows (execution) |
| **External agent framework** | LangChain (Analyst, Risk, Impact, audit-summary agents) |
| **LLM** | Claude (primary) + Gemini (fallback) |
| **Trigger demo source** | Onboard vision / IMU sensor / fleet telemetry / operator handheld — interchangeable |
| **Execution targets (mocked)** | API-driven repair dispatch + **RPA-driven legacy fleet CMMS** |

Full architecture: [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md).

## Getting started

The orchestration core runs on **UiPath Automation Cloud** (Maestro BPMN is the mandatory core). External frameworks (LangChain, custom Python agents) run **as task nodes invoked from the BPMN flow**.

You can validate the canonical fleet data model locally without any UiPath access:

```bash
python -m venv .venv && source .venv/bin/activate
pip install jsonschema
python - <<'PY'
import json, glob
from jsonschema import Draft202012Validator
schema = json.load(open('samples/triggers/incident_report.schema.json'))
v = Draft202012Validator(schema)
for f in glob.glob('samples/triggers/*.json'):
    if 'schema' in f: continue
    v.validate(json.load(open(f)))
    print('OK', f)
PY
```

See [`samples/triggers/`](./samples/triggers/) for the `IncidentReport` schema + 8 mower incident samples (blade strike / slope stall / boundary breach / charging / theft / operator + vision + sensor) that replay the flow without external systems.

### Run the orchestration end-to-end

The same stages the Maestro BPMN models also run as plain Python task nodes, so the flow is runnable and testable with **zero external dependencies** — the LLM and enterprise systems degrade to local fallbacks when no keys are set:

```bash
python run_pipeline.py            # trigger -> analyst agent -> gateway -> action -> audit
python -m pytest -q               # offline end-to-end tests
```

Each incident is classified by the **Fleet AI Analyst** agent ([`agents/`](./agents/)), scored by the Safety Risk gateway, routed to the **Action Center (HITL)** or the autonomous **Fast Track**, then ticketed against the **mock enterprise API** ([`mocks/`](./mocks/)) with an immutable audit entry at every stage.

- **LLM task node** — set `ANTHROPIC_API_KEY` (Claude, primary) or `GEMINI_API_KEY` (fallback) and `pip install -r requirements.txt`. With no key, a deterministic rule layer mirrors the BPMN gateway math so the pipeline still runs.
- **Mock enterprise API** — `uvicorn mocks.enterprise_api:app --port 8099` for live HTTP endpoints (QA tickets / CRM / audit log).
- **Live UiPath queue** — see [`docs/UIPATH-SETUP.md`](./docs/UIPATH-SETUP.md) to push incidents into a real `IncidentReports` queue on Orchestrator.
- **Deploy to Maestro Cloud (submission-critical)** — [`docs/DEPLOY-MAESTRO.md`](./docs/DEPLOY-MAESTRO.md) is the step-by-step runbook to make the BPMN actually *run on UiPath Automation Cloud* (the AgentHack requirement) + a done-checklist.

## Community

Building this in the open — join the team chat on Discord: https://discord.gg/ntXbNbvN95

## Contributing

Contributions are welcome — see [`CONTRIBUTING.md`](./CONTRIBUTING.md). Day-to-day discussion happens on the project **Discord**.

## License

[Apache License 2.0](./LICENSE)
