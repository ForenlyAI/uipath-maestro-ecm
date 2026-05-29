# uipath-maestro-ecm — Agentic Physical AI & Robotics Field Inspection on UiPath Maestro

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)

> An open-source framework for running **Physical AI & Autonomous Robotics Field Inspection** as an **agentic, human-in-the-loop (HITL) orchestration** on **UiPath Maestro BPMN**.

In industrial fields (aerospace, manufacturing, energy, construction), physical defects and equipment anomalies must be detected in seconds and remediated systematically. This project orchestrates the full inspection and remediation lifecycle — from the moment a mobile patrol robot flags an anomaly to the compliance-audited release of repair actions — as a BPMN process where AI agents perform pre-analysis and humans approve critical safety and cost gates.

## What it does

- **8 process containers** modeling the full field-inspection and remediation lifecycle (inspection trigger → anomaly analysis → planning → automated execution & auditing) as Maestro BPMN subprocesses.
- **9 roles** structured as BPMN swimlanes — some realized as autonomous LLM agents (e.g., the Vision AI Analyst, Safety Risk Agent), others as human-in-the-loop review boards via UiPath Action Center.
- **An agentic "Fast Track" gateway** — a Safety Risk Agent automatically scores incoming anomalies and bypasses the full operations board for low-risk, minor repairs.
- **Vendor-agnostic triggers** — mobile patrol robots, fixed sensor feeds, handheld operator portals, or camera feeds all normalize to one canonical `IncidentReport` shape.
- **Audit-grade traceability** — immutable log entries at every gateway and task node for regulatory compliance.

## Architecture at a glance

### Core Orchestration: UiPath Maestro BPMN
* **8 Robotics Process Containers** modeled as BPMN subprocesses.
* **9 Roles as Swimlanes / Agents** (such as Vision AI Analyst, Safety Risk Agent).
* **Action Center HITL** for critical human-in-the-loop approvals.
* **Agentic Fast Track Gateway** for automated, low-risk routing.
* **Immutable Audit Compliance Log** for complete regulatory traceability.

### Swappable Task Nodes Integration

| Trigger Source (Swappable) | LLM Agents (Swappable) | Enterprise / Maintenance (Swappable) | Execution Systems (Swappable) |
| :--- | :--- | :--- | :--- |
| • Mobile Patrol Robot<br>• Fixed Sensor Feeds<br>• Operator Handheld App<br>• Camera Feeds | • Claude via LangChain<br>• Gemini via LangChain | • Mock Asset Database<br>(Maximo/ServiceNow-shaped API) | • Repair Robot (API)<br>• RPA-driven Legacy UI |


Full architecture: [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md).

## The 8 Robotics Containers

```
Process 1 · Inspection & Defect Intake
  1. Anomaly Report        Mobile Robot → Vision AI Analyst → Inspector HITL → disposition (5-way)
  2. Manual Intervention   Field operator or fixed sensor flags deviation + Inspector feedback loop

Process 2 · Analysis & Safety Routing
  3. Risk & Safety Analysis Defect Request → Safety Risk Agent → Fast Track OR CAB (Change Advisory Board) HITL
  4. Site Impact Analysis   Operations Board analyzes cost / downtime / labor hours / effectivity of repair

Process 3 · Action & Compliance
  5. Remediation Plan      Analyst Agent + Maintenance Specialist draft Playbook → CIB (CISO/Operations) HITL
  6. Release Repair Action Product/Asset data released; dispatch mobile repair robot or field engineer
  7. Legacy Configuration  RPA Security Robot / API Workflows write to subcontractor or legacy CMMS systems
  8. Quality Assurance     Compliance-summary agent + immutable audit log + supervisor signature
```

## How it's built

| Layer | Choice |
| --- | --- |
| **Orchestration** | UiPath Automation Cloud + Maestro BPMN |
| **UiPath components** | Agent Builder · Maestro BPMN · API Workflows · Action Center · RPA Robot |
| **External agent framework** | LangChain (Analyst agent, Risk Agent, audit-summary agent) |
| **LLM** | Claude (primary) + Gemini (fallback) |
| **Trigger demo source** | Mobile patrol robot & vision system; interchangeable |
| **Asset CMMS target (mocked)**| Open-source Asset Management mock service (Maximo/ServiceNow–shaped API) |
| **Execution targets (mocked)** | Two mock endpoints — one API-driven (repair robot), one RPA-driven (legacy database) |

## Getting started

The orchestration core runs on **UiPath Automation Cloud** (Maestro BPMN is the mandatory core). External frameworks (LangChain, custom Python agents) are welcome **as task nodes invoked from the BPMN flow**.

You can explore and validate the canonical robotics data model locally without any UiPath access:

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

See [`samples/triggers/`](./samples/triggers/) for the `IncidentReport` schema + 4 robotics source samples (vision / ERP / manual / supplier) that let you replay the flow without external systems.

## Community

Building this in the open — join the team chat on Discord: https://discord.gg/ntXbNbvN95

## Contributing

Contributions are welcome — see [`CONTRIBUTING.md`](./CONTRIBUTING.md). Day-to-day discussion happens on the project **Discord**.

## License

[Apache License 2.0](./LICENSE)
