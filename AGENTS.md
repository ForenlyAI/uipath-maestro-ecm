# AGENTS.md

> Agent context file for the `uipath-maestro-ecm` repository. Coding agents (Claude Code, Cursor,
> Codex, Gemini CLI) — and UiPath for Coding Agents in particular — should read this before doing
> any work in this repo.

## Project

An open-source framework that runs **Physical AI & Autonomous Robotics Field Inspection** as an agentic,
human-in-the-loop workflow on **UiPath Maestro BPMN**. The framework defines 3 processes,
8 containers, and 9 roles. AI agents handle pre-analysis (the Vision AI Analyst role is an LLM agent, the
Fast Track decision is an autonomous Safety Risk Agent, board briefings are AI-rendered); humans approve
at the review-board gates via Action Center.

## Stack and constraints

| Layer | Choice |
|---|---|
| Orchestration core | UiPath Maestro BPMN (mandatory) |
| Agent runtime | UiPath Agent Builder (Maestro-callable); LangChain wrappers permitted for external agents called from BPMN task nodes |
| LLM | Claude (primary), Gemini (fallback) |
| Trigger sources | Mobile patrol robot · Fixed sensors · Manual operator app · Supplier deviation feed — see `samples/triggers/` |
| CMMS target (mock) | Lightweight FastAPI mock approximating an IBM Maximo / ServiceNow–shaped REST API |
| Execution targets (mock)| One API-driven repair robot endpoint + one RPA-driven legacy maintenance UI |

## Repository layout

- **uipath-maestro-ecm/**: Root directory of the repository
  - **README.md**: Project entry (humans start here)
  - **AGENTS.md**: THIS FILE (coding-agent bootstrap)
  - **LICENSE**: Apache 2.0
  - **CONTRIBUTING.md**: Working agreement
  - **docs/**: Documentation folder
    - **README.md**: Documentation index
    - **ARCHITECTURE.md**: UiPath-core BPMN architecture
  - **samples/triggers/**: Canonical input data
    - **incident_report.schema.json**: IncidentReport JSON schema
    - **vision_aoi_defect.json**: Sample optical inspection input
    - **erp_deviation.json**: Sample ERP deviation input
    - **manual_qa_report.json**: Sample manual input
    - **supplier_deviation.json**: Sample supplier variance input
    - **README.md**: Overview of triggers
  - **artifacts/**: Generated UiPath artifacts (created during work)
    - **container1/**: Container 1 — Problem Report
      - **problem_report.bpmn**: Maestro BPMN export
      - **agent_analyst.yaml**: Agent Builder definition
      - **action_center_irb.json**: Action Center task template
      - **README.md**: Sub-container documentation

## How to work in this repo (instructions for coding agents)

1. **Read `samples/triggers/incident_report.schema.json` first.** Every trigger normalizes to this shape; all BPMN inputs and agent inputs consume it.
2. **Read `docs/ARCHITECTURE.md` second.** The UiPath-component breakdown (Agent Builder, Maestro, API Workflows, Action Center, RPA) is defined there. Use those components — do not substitute external tools where a UiPath component fits.
3. **Default scope:** Container 1 (Problem Report / Anomaly Intake) only, unless the prompt explicitly asks for a different container. Do not invent containers, roles, or dispositions beyond those defined in the architecture.
4. **Output location:** write generated UiPath artifacts under `artifacts/container1/`. Do not write to `docs/` or `samples/` unless explicitly told.
5. **Reproducibility rule:** every artifact must be deterministic from the prompt + repo content. Do not bake in secrets, hard-coded tenant URLs, or absolute file paths.
6. **Commit messages:** use the prefix `bpmn:`, `agents:`, `actioncenter:`, or `artifacts(container1):`. Reference the issue number when relevant.
7. **Confidence and HITL:** whenever an agent produces an output, include a `confidence` field. If `confidence < 0.7` the BPMN must route to Action Center HITL rather than auto-disposition.

## Glossary

| Acronym | Expansion |
|---|---|
| **CMMS** | Computerized Maintenance Management System |
| **CAB** | Change Advisory Board (Safety & Operations review) |
| **CIB** | Change Implementation Board (Executive-level director approvals) |
| **Fast Track** | Bypassing CAB for low-impact repairs; here implemented as an agentic Safety Risk Agent gateway |
| **HITL** | Human-in-the-Loop, realized via UiPath Action Center tasks |
| **BPMN** | Business Process Model and Notation 2.0 |
| **AOI** | Automated Optical Inspection (vision-based defect detection) |

## What this file is NOT

- Not architecture (see `docs/ARCHITECTURE.md`).
- Not for human reading first — humans should start at `README.md`. This file is for coding agents to bootstrap context.
