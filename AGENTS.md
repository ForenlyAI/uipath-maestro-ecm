# AGENTS.md

> Agent context file for the `uipath-maestro-ecm` repository. Coding agents (Claude Code, Cursor,
> Codex, Gemini CLI) — and UiPath for Coding Agents in particular — should read this before doing
> any work in this repo.

## Project

An open-source framework that runs a **cloud-GPU orchestrator and humanoid RL training lifecycle
manager** as an agentic, human-in-the-loop workflow on **UiPath Maestro BPMN**. The framework
defines 3 processes, 8 containers, and 9 roles. AI agents handle pre-analysis (the Telemetry Analyst
role is an LLM agent, the Fast Track decision is an autonomous Anomaly Risk Agent, board briefings are
AI-rendered); humans approve at the review-board gates via Action Center. UiPath's two pillars carry
the work: **Agent Builder** (agentic) and the **RPA Robot** (provisioning GPUs and writing into
back-office systems that lack clean APIs).

## Stack and constraints

| Layer | Choice |
|---|---|
| Orchestration core | UiPath Maestro BPMN (mandatory) |
| Agent runtime | UiPath Agent Builder (Maestro-callable); LangChain wrappers permitted for external agents called from BPMN task nodes |
| LLM | Claude (primary), Gemini (fallback) |
| Sources | Reward/loss telemetry · container logs · hardware monitor (GPU/thermal/quota) · researcher console — see `samples/triggers/` |
| Cloud-ops target (mock) | Lightweight FastAPI mock approximating cloud billing/quota + a model registry REST API |
| Execution targets (mock)| One API-driven provisioning endpoint + one **RPA-driven cloud console / billing UI** |

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
    - **incident_report.schema.json**: IncidentReport (training-run anomaly) JSON schema
    - **gradient_collapse.json**: reward-telemetry gradient-collapse sample
    - **loss_divergence.json**: telemetry loss-divergence sample
    - **gpu_oom_fault.json**: hardware-monitor CUDA-OOM sample
    - **idle_spend.json**: low-severity idle-GPU-spend sample (fast-track)
    - **quota_exhaustion.json**: cloud-quota sample
    - **IR-20260606-*.json**: researcher-console / trainer-logs / gpu-monitor samples
    - **README.md**: Overview of sources
  - **artifacts/**: Generated UiPath artifacts (created during work)
    - **container1/**: Container 1 — Anomaly Intake
      - **problem_report.bpmn**: Maestro BPMN export
      - **agent_analyst.yaml**: Agent Builder definition
      - **action_center_irb.json**: Action Center task template
      - **README.md**: Sub-container documentation

## How to work in this repo (instructions for coding agents)

1. **Read `samples/triggers/incident_report.schema.json` first.** Every source normalizes to this shape; all BPMN inputs and agent inputs consume it.
2. **Read `docs/ARCHITECTURE.md` second.** The UiPath-component breakdown (Agent Builder, Maestro, API Workflows, Action Center, RPA) is defined there. Use those components — do not substitute external tools where a UiPath component fits.
3. **Default scope:** Container 1 (Anomaly Intake) only, unless the prompt explicitly asks for a different container. Do not invent containers, roles, or dispositions beyond those defined in the architecture.
4. **Output location:** write generated UiPath artifacts under `artifacts/container1/`. Do not write to `docs/` or `samples/` unless explicitly told.
5. **Reproducibility rule:** every artifact must be deterministic from the prompt + repo content. Do not bake in secrets, hard-coded tenant URLs, or absolute file paths.
6. **Commit messages:** use the prefix `bpmn:`, `agents:`, `actioncenter:`, or `artifacts(container1):`. Reference the issue number when relevant.
7. **Confidence and HITL:** whenever an agent produces an output, include a `confidence` field. If `confidence < 0.7` the BPMN must route to Action Center HITL rather than auto-disposition.

## Glossary

| Acronym | Expansion |
|---|---|
| **Anomaly** | A training-run health/cost event (gradient collapse, loss divergence, hardware fault, resource risk) |
| **Researcher Review Board** | Human cost & physics-safety review, realized via UiPath Action Center |
| **Fast Track** | Bypassing the review board for low-risk anomalies; here an agentic Anomaly Risk Agent gateway |
| **HITL** | Human-in-the-Loop, realized via UiPath Action Center tasks |
| **RPA** | Robotic Process Automation — UiPath robot provisioning GPUs / writing into cloud & back-office systems |
| **BPMN** | Business Process Model and Notation 2.0 |
| **Criticality Zone** | Run zone (high-cost-gpu/production-bound/public-benchmark/long-running) that biases risk |

## What this file is NOT

- Not architecture (see `docs/ARCHITECTURE.md`).
- Not for human reading first — humans should start at `README.md`. This file is for coding agents to bootstrap context.
