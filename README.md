# uipath-maestro-ecm — Training Fleet & Cloud Resource Manager on UiPath Maestro

> [!IMPORTANT]
> ### 🏆 GRAND PRIZE POOL: $48,000 USD!
> **Grand Prize:** $8,000 USD Cash + Global UiPath Recognition! Let's automate the enterprise with fütüristik AI Orchestration! 🤖💼


[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)

> An open-source framework for running a **cloud-GPU orchestrator and humanoid RL training lifecycle manager** as an **agentic, human-in-the-loop (HITL) orchestration** on **UiPath Maestro BPMN** — combining UiPath's two signature strengths: **agentic AI** (Agent Builder decisioning) and **RPA** (robots that provision cloud GPUs and execute into back-office systems).

Training neural skills (walking, running, grasping) for bipedal humanoid robots (like the Unitree G1) in reinforcement-learning simulation is compute-heavy and expensive. Teams burn thousands of dollars on cloud GPUs (AWS, GCP, AMD Developer Cloud) that sit **idle**, or on RL runs that **silently diverge or collapse** for hours before anyone notices. This project orchestrates the whole training lifecycle — from a researcher's training request, to cost-optimal GPU provisioning, to live anomaly detection that kills wasted runs, to human-approved checkpoint registration — as a **BPMN process where AI agents do the analysis and humans approve the critical cost and physics-safety gates.**

## Where this fits — the humanoid-robot stack

| Stage | Project | Role |
|---|---|---|
| **Deploy** | [`gcp`](https://github.com/Forenly/gcp) | Pick the right robot for a task + plan the install |
| **Operate** | [`gemini-xprize`](https://github.com/Forenly/gemini-xprize) — FleetMind | Run the autonomous day-to-day ops loop |
| **Govern** | **`uipath-maestro` (this repo)** | **Manage training runs + cloud GPU budget with human-approved gates** (the governance / HITL layer) |
| **Respond** | [`protocol-sift-dfir`](https://github.com/Forenly/protocol-sift-dfir) | Forensics when a unit is compromised |

Reference workload across all four: **Unitree G1-class** humanoid RL skills trained in MuJoCo.

## The two UiPath pillars (what we lean on)

- **Agentic** — the decisioning runs as **UiPath Agent Builder** agents: a **Telemetry Analyst** (classify the anomaly + Anomaly Risk score), a **Cost & Impact Agent** (cloud-GPU economic + organizational impact → routing), and a compliance-summary agent. They reason over each training-run anomaly and decide *fast-track vs human review*.
- **RPA** — once an action is approved, a **UiPath RPA robot** executes it into systems that have **no clean API**: cloud-provider consoles, the billing/quota dashboards, the model registry, and SSH-driven container control — driven through the UI when needed, plus API Workflows where an API exists.

## What it does

- **8 process containers** modeling the full training lifecycle (training request → GPU provisioning → telemetry/anomaly analysis → risk/cost routing → approved remediation & audit) as Maestro BPMN subprocesses.
- **9 roles** as BPMN swimlanes — some realized as autonomous LLM agents (Telemetry Analyst, Anomaly Risk Agent), others as human-in-the-loop review boards via UiPath Action Center.
- **An agentic "Fast Track" gateway** — the Anomaly Risk Agent scores each event and bypasses the full review board for low-risk, contained anomalies (auto-remediate, e.g. release an idle instance).
- **Vendor-agnostic sources** — live reward/loss telemetry, container logs, a hardware monitor (GPU/thermal/quota), or a researcher console all normalize to one canonical `IncidentReport` (training-run anomaly event).
- **Audit-grade traceability** — immutable log entries at every gateway and task node (GPU hours, cost, approvals).

## The 8 training-fleet containers

```
Process 1 · Anomaly & Request Intake
  1. Anomaly Report       Telemetry/logs/monitor → Telemetry Analyst → Researcher HITL → disposition
  2. Manual Intervention  Researcher console request or a fixed monitor flags an anomaly + feedback loop

Process 2 · Analysis & Risk Routing
  3. Risk & Anomaly Analysis  Anomaly → Anomaly Risk Agent → Fast Track OR Researcher Review Board (HITL)
  4. Cost & Impact Analysis   Cloud-GPU economic + organizational impact (idle spend / run loss / liability / fleet reach)

Process 3 · Action & Compliance
  5. Remediation Plan     Analyst Agent + RL Engineer draft a recovery playbook (retune/restart) → Ops HITL
  6. Execute Remediation  SSH-shutdown a diverging run, release/teardown an instance; HOLD a production-bound run
  7. Cloud/Registry Write-back  **RPA robot** writes to the cloud console, billing dashboard, model registry
  8. Quality Assurance    Compliance-summary agent + immutable audit log + researcher sign-off
```

## How it's built

| Layer | Choice |
| --- | --- |
| **Orchestration** | UiPath Automation Cloud + Maestro BPMN |
| **UiPath components** | **Agent Builder** (agentic) · Maestro BPMN · Action Center (HITL) · **RPA Robot** + API Workflows (provisioning/execution) |
| **External agent framework** | LangChain (Analyst, Risk, Impact, audit-summary agents) |
| **LLM** | Claude (primary) + Gemini (fallback) |
| **Training workload** | Docker + MuJoCo RL training containers (`g1-mujoco-rl-training`) on AWS / GCP / AMD GPUs |
| **Execution targets (mocked)** | API-driven cloud provisioning + **RPA-driven cloud console / billing / model registry** |

Full architecture: [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md).

## Getting started

The orchestration core runs on **UiPath Automation Cloud** (Maestro BPMN is the mandatory core). External frameworks (LangChain, custom Python agents) run **as task nodes invoked from the BPMN flow**.

You can validate the canonical anomaly data model locally without any UiPath access:

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

See [`samples/triggers/`](./samples/triggers/) for the `IncidentReport` schema + 8 training-anomaly samples (gradient collapse / loss divergence / GPU OOM / idle spend / quota exhaustion / researcher note + logs + monitor) that replay the flow without external systems.

### Run the orchestration end-to-end

The same stages the Maestro BPMN models also run as plain Python task nodes, so the flow is runnable and testable with **zero external dependencies** — the LLM and cloud systems degrade to local fallbacks when no keys are set:

```bash
python run_pipeline.py            # anomaly -> analyst agent -> gateway -> action -> audit
python -m pytest -q               # offline end-to-end tests
```

Each event is classified by the **Telemetry Analyst** agent ([`agents/`](./agents/)), scored by the Anomaly Risk gateway, routed to the **Action Center (HITL)** or the autonomous **Fast Track**, then ticketed against the **mock cloud-ops API** ([`mocks/`](./mocks/)) with an immutable audit entry at every stage.

- **LLM task node** — set `ANTHROPIC_API_KEY` (Claude, primary) or `GEMINI_API_KEY` (fallback) and `pip install -r requirements.txt`. With no key, a deterministic rule layer mirrors the BPMN gateway math so the pipeline still runs.
- **Mock cloud-ops API** — `uvicorn mocks.enterprise_api:app --port 8099` for live HTTP endpoints (run tickets / provider registry / audit log).
- **Live UiPath queue** — see [`docs/UIPATH-SETUP.md`](./docs/UIPATH-SETUP.md) to push anomalies into a real `IncidentReports` queue on Orchestrator.
- **Deploy to Maestro Cloud (submission-critical)** — [`docs/DEPLOY-MAESTRO.md`](./docs/DEPLOY-MAESTRO.md) is the step-by-step runbook to make the BPMN actually *run on UiPath Automation Cloud* (the AgentHack requirement) + a done-checklist.

## Community

Building this in the open — join the team chat on Discord: https://discord.gg/ntXbNbvN95

## Contributing

Contributions are welcome — see [`CONTRIBUTING.md`](./CONTRIBUTING.md). Day-to-day discussion happens on the project **Discord**.

## License

[Apache License 2.0](./LICENSE)
