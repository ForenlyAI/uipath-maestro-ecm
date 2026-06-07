# Deploy runbook — run `FieldIncidentTriage` on UiPath Automation Cloud (SUBMISSION-CRITICAL)

> **Why this is the #1 task.** AgentHack requires a **new working app built in UiPath Studio
> Web that runs on UiPath Automation Cloud**, with UiPath as the execution/orchestration layer
> ([rules](https://uipath-agenthack.devpost.com/rules)). Our `run_pipeline.py` is only a local
> proof; the **judged artifact is the Maestro process actually running on the cloud.** Until the
> BPMN is deployed and a job runs end-to-end on Automation Cloud, the submission is incomplete.

> **Known constraint.** The Maestro/Solution **cannot be created programmatically** —
> `POST /Solution` returns `403` (entitlement `20041`, scope-independent; see the
> StudioWeb-S2S finding). So steps 1–7 below are done in the **browser Studio Web**, not via API.

---

## Prerequisites — already live ✅

| Item | Value |
|---|---|
| Tenant | `forenlyaiplatform` / `DefaultTenant` |
| Folder | `Shared` (id **116151**) |
| Queue | `IncidentReports` (id **16639**) — live, items present |
| BPMN | `maestro/FieldIncidentTriage/content/FieldIncidentTriage.bpmn` (well-formed, 11 nodes) |
| Agent specs | `artifacts/container1/agent_analyst.yaml`, `agents/analyst_agent.py`, `agents/impact_agent.py` |
| HITL form | `artifacts/container1/action_center_irb.json` |
| API token | GSM `uipath-client-id/-secret/-org/-tenant` (works; `OR.*` scopes) |

## Step 0 — Team & entitlements (do first)

- [ ] Register the **Devpost team** (max 4 members) at uipath-agenthack.devpost.com.
- [ ] Submit the **UiPath Labs access form** (team of ≤4 → Labs env within ~3 business days).
- [ ] Confirm the working tenant has **Maestro + Agent Builder + Action Center** entitlements.
      Our `forenlyaiplatform` tenant currently **lacks Maestro entitlement** (that is the 403).
      → Build in the **Labs environment** granted for the hackathon, or have Maestro enabled.

## Step 1 — Get the process into Studio Web

Two ways (see `maestro/README.md`):
1. **Git source control** — connect the Studio Web Maestro project to this repo, pull;
   the process appears under the project, or
2. **New process + replace** — create a new Maestro (Process Orchestration) project in Studio
   Web, then replace the generated `.bpmn` with `maestro/FieldIncidentTriage/content/FieldIncidentTriage.bpmn`.

The diagram renders and routes as-is. Steps 2–7 make it **executable**.

## Step 2 — Bind the agentic task nodes (Agent Builder)

- [ ] **`AI Triage and Risk Score`** service task → a published **Agent Builder** agent
      (the *Fleet AI Analyst*), spec = `artifacts/container1/agent_analyst.yaml`
      (categories BLADE/MOBILITY/BOUNDARY/OPERATIONAL; risk x1.5 on safety zones; HITL flag).
- [ ] **`Impact Analysis (Economic + Organizational)`** → an agent / API Workflow mirroring
      `agents/impact_agent.py` (economic score + safetyCritical + orgScope → route).

> LangChain/CrewAI wrappers are allowed, but **UiPath must be the orchestration layer** (rule).

## Step 3 — Gateway

- [ ] **`HITL Required?`** exclusive gateway → branch on the analyst/impact output
      (`Incident.hitlRequired == true` → Action Center; else Fast-Track).

## Step 4 — Action Center HITL (human gate)

- [ ] **`Escalate to Review Board (Action Center)`** → a **real Action Center action**
      (External-app task or QuickForm) using the fields in `action_center_irb.json`
      (read-only AI context + decision enum `APPROVE_SERVICE/RECALL_UNIT/INITIATE_INSPECTION/HOLD_UNIT/OVERRIDE_TO_PROCEED` + reviewerNotes + reviewerName).
- [ ] Assign to the **Fleet Review Board** queue/role.

> Gotcha: Action Center tasks need a **registered action type** — a bare
> `GenericTasks/CreateTask` won't work; model the action in the process.

## Step 5 — Queue trigger (entry point)

- [ ] Wire the **`IncidentReports`** queue (Shared / 116151, id 16639) as the process trigger
      so each new queue item starts a `FieldIncidentTriage` job. Entry point: `Event_start`
      with `Incident` input (see `entry-points.json`).

## Step 6 — RPA write-back (the RPA pillar)

- [ ] **`Fast-Track Auto-Resolve`** and the post-approval path → an **RPA Robot** / API
      Workflow that records the outcome in the (mock) fleet **CMMS / warranty portal**.
      For the demo, point at `mocks/enterprise_api.py` (`uvicorn mocks.enterprise_api:app --port 8099`)
      or a stub. This is where UiPath's **RPA** strength shows (writing into a system with no clean API).

## Step 7 — Publish & run end-to-end on the cloud

- [ ] **Publish** the Maestro process.
- [ ] Push fresh incidents: `python integrations/push_incidents.py` (env from GSM, folder 116151).
- [ ] In **Orchestrator → Jobs** (the Overview screen): confirm a `FieldIncidentTriage` **Job runs**.
- [ ] A high-risk item → an **Action Center task** appears → **approve it** → job completes.
- [ ] A low-risk item (e.g. `mower_charging_fault.json`) → **auto-resolves** (no human gate).
- [ ] Capture the **demo URL + screenshots** for Devpost.

---

## Done = these are all true (the "runs on Automation Cloud" bar)

- [ ] `FieldIncidentTriage` visible under Maestro / Solutions on `forenlyaiplatform` (or Labs tenant)
- [ ] Queue item → process job auto-starts
- [ ] HITL item creates an Action Center task; a human approves it
- [ ] Fast-track item auto-resolves with an RPA/API write-back
- [ ] Job history shows success + audit trail
- [ ] Public demo URL captured for the submission

## Maps to open GitHub issues

- **#2** Deploy BPMN to Maestro Cloud + wire live Action Center (demo URL) — steps 1–7
- **#1** Model containers 2–3 + Action Center HITL form — steps 2–4
- **#8 / #9** Dequeue `IncidentReports` + branch on `hitlRequired` + set transaction status — steps 5, 7
- **#6** Submission: Devpost draft + ~3-min demo — after step 7

## Who does what

- **Core team (≤4, tenant/Labs access):** steps 1–7 in Studio Web (browser) — this is the
  manual, entitlement-gated part.
- **Wider Discord contributors (GitHub only):** keep improving the open-source framework
  (agents, schema, BPMN definition, samples, mocks) via fork → PR — **no tenant access needed.**
