# Architecture — UiPath-Core, Vendor-Agnostic Fleet Orchestration

> **Design principle:** UiPath Maestro BPMN is the orchestration core for a robotic
> lawn-mower fleet. Mower platforms, vision/sensor providers, LLMs, and back-office systems
> are **swappable task nodes** invoked by the BPMN flow. The two UiPath pillars carry the
> work: **Agent Builder** (agentic decisioning) and the **RPA Robot** (executing into
> systems without clean APIs).

## Why vendor-agnostic

A vendor-agnostic orchestration core is the difference between a drop-in adoption path and a
rip-and-replace pitch. A fleet operator keeps their existing mower brand, vision stack, and
back-office systems; the BPMN orchestration sits on top. Each task node has a defined
interface, which is what makes exception handling, retries, and fallbacks possible (e.g.
primary telemetry source down → swap to a secondary or a mock).

## The two UiPath pillars

| Pillar | UiPath component | What it does here |
|---|---|---|
| **Agentic** | **Agent Builder** | Fleet AI Analyst (classify + risk), Safety Risk Agent (Fast-Track gateway), Impact Agent (economic/org impact), compliance-summary agent — each a Maestro-callable agent that *reasons and decides*. |
| **RPA** | **RPA Robot** + API Workflows | Executes approved remediation into the dealer/warranty portal, parts ERP, and legacy fleet CMMS — driven through the UI where there is no API, via API Workflows where there is. |
| **Governance** | **Action Center** | Human-in-the-loop approval for safety/cost gates; supervisor sign-off. |
| **Backbone** | **Maestro BPMN** | Top-level process (BPMN 2.0): tasks, gateways, events, swimlanes; immutable audit at each node. |

## Swappable integration points

| Trigger source (swappable) | Mower platform (swappable) | LLM agent (swappable) | Back-office systems (swappable) |
| :--- | :--- | :--- | :--- |
| • Onboard vision<br>• IMU / lidar sensor<br>• Fleet telemetry<br>• Operator handheld | • Segway Navimow X3<br>• Husqvarna<br>• Mock fleet API | • Claude via LangChain<br>• Gemini via LangChain | • Warranty/dealer portal (**RPA**)<br>• Parts ERP<br>• Fleet CMMS<br>• Audit log / notifications |

## Reference flow (BPMN tasks)

A robotic mower flags a fault; the BPMN orchestrates triage and approved remediation:

1. **Incident Intake** — onboard vision/sensor/telemetry/handheld raises a fault (type, location, severity, evidence) → canonical `IncidentReport`.
2. **Fleet AI Analyst (agent)** — categorize the fault (BLADE_FAULT / MOBILITY_FAULT / BOUNDARY_BREACH / OPERATIONAL_RISK).
3. **Safety Risk Agent (agent)** — risk score; safety-critical operating zones (near-road, near-water, public-access, steep-slope) bias toward HITL.
4. **Impact Agent (agent)** — economic + organizational impact → Fast Track (autonomous) or Fleet Review Board.
5. **Fleet Review Board (HITL)** — Action Center approval for high-risk / high-cost actions.
6. **Dispatch Remediation** — send a field technician or repair action; HOLD/RECALL the unit if unsafe.
7. **Legacy Write-back (RPA)** — the RPA Robot records the action in the warranty portal / parts ERP / fleet CMMS.
8. **Quality Assurance** — compliance-summary agent + immutable audit entry + supervisor sign-off.

End-to-end target: seconds-to-minutes per incident; full audit trail; HITL only where risk warrants it.

## Swap-ability matrix

| Layer | Reference choice | Drop-in alternatives |
|---|---|---|
| Mower platform | Segway Navimow X3-class | Husqvarna Automower, other ROS 2 fleets, mock fleet API |
| Trigger source | Onboard vision + IMU + telemetry | Lidar, bump sensors, AR handheld, supplier feed |
| LLM | Claude (primary), Gemini (fallback) | OpenAI, local LLM through LangChain |
| Back-office | Mocked CMMS / warranty / parts endpoints | ServiceNow, Salesforce, SAP, dealer portals via UiPath RPA/connectors |

## What this is **not**

- Not a single-vendor proof of concept.
- Not a robot demo where UiPath sits beside the workflow — UiPath *is* the orchestration (agentic + RPA).
- Not a slide deck with a happy-path diagram — the orchestration is meant to actually run (`python run_pipeline.py`).
