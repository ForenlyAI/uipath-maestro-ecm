# Architecture — UiPath-Core, Vendor-Agnostic BPMN Orchestration

> **Design principle:** UiPath Maestro BPMN is the orchestration core. Vision providers, robot
> platforms, LLMs, and enterprise systems are **swappable task nodes** invoked by the BPMN flow.
> The use case is illustrative; the orchestration layer is the product.

## Why vendor-agnostic

A vendor-agnostic orchestration core is the difference between a drop-in adoption path and a
rip-and-replace pitch. Customers keep their existing vision/robot/PLM vendors; the BPMN orchestration
sits on top. Each task node has a defined interface, which is what makes exception handling, retries,
and fallbacks possible (e.g. primary vision provider down → swap to a secondary or a mock).

## Architecture diagram

### Core Orchestration: UiPath Maestro BPMN
* **Process Orchestration** defining top-level flow (tasks, gateways, events, swimlanes).
* **Agent Builder Agents** running classification, risk scoring, and decisions.
* **Action Center (HITL)** for safety and compliance human reviews.
* **Audit & Governance Layer** providing immutable logging at each node.

### Swappable Integration Points

| Vision API (Swappable) | Robot/Sensor Platform (Swappable) | LLM Agent (Swappable) | Enterprise Systems (Swappable) |
| :--- | :--- | :--- | :--- |
| • AOI Vision System<br>• Mock Vision API | • Mobile Inspection Robot<br>• Fixed Camera Feeds | • Claude via LangChain<br>• Gemini via LangChain | • QA Ticket System<br>• CRM Database<br>• Audit Log Services<br>• Notification Services |


## UiPath components used

| Component | Role in the BPMN |
|---|---|
| **Maestro BPMN** | Top-level process definition (BPMN 2.0): tasks, gateways, events, lanes |
| **Agent Builder** | Classification Agent, Risk Agent, Decision Agent — each encapsulated as a Maestro-callable agent |
| **API Workflows** | Outbound calls to vendor task nodes (vision, robot platform, enterprise systems) |
| **Action Center** | Human-in-the-loop approval for high-risk decisions; supervisor sign-off |
| **RPA Robot** | Optional system-of-record updates that lack APIs |

## Reference demo use case (illustrative)

A reference use case grounds the demo. **The use case can change without redesigning the BPMN** —
that is the point.

**Working candidate:** field quality control on an industrial installation site (e.g. an electrical
installation). A mobile platform patrols, the vision system flags defects, and the BPMN orchestrates
remediation with HITL where needed.

Flow stages (BPMN tasks):
1. **Inspection Intake** — the vision system flags a candidate defect (type, location, severity, image).
2. **Classification Agent** — categorize the defect (product / line / severity tier).
3. **Risk Agent** — risk score; route severe cases to HITL.
4. **Decision Agent** — choose remediation: rework / scrap / alert / halt / continue.
5. **Compliance Reviewer (HITL)** — Action Center approval for high-risk decisions.
6. **Action Output** — execute the decision (notify line, ticket QA system, update CRM).
7. **Notification Agent** — supervisor notification + immutable audit-log entry.

End-to-end target: seconds-to-minutes per defect; full audit trail; HITL only where risk warrants it.

## Swap-ability matrix

| Layer | Reference choice | Drop-in alternatives |
|---|---|---|
| Vision | AOI vision system | Landing AI, MVTec, Cognex VisionPro, mock/curated dataset |
| Robot / sensor platform | Mobile inspection robot | Other mobile robots, fixed-camera setup, handheld AR tablet |
| LLM | Claude (primary), Gemini (fallback) | OpenAI, local LLM through LangChain |
| Enterprise systems | Mocked QA ticket + CRM endpoints | ServiceNow, Salesforce, Jira, SAP via UiPath connectors |

## What this is **not**

- Not a single-vendor proof of concept.
- Not a robot demo where UiPath sits beside the workflow.
- Not a slide deck with a happy-path diagram — the orchestration is meant to actually run.
