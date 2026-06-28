# Architecture — UiPath-Core, Vendor-Agnostic Training-Fleet Orchestration

> **Design principle:** UiPath Maestro BPMN is the orchestration core for a humanoid RL
> training fleet and its cloud GPU budget. Cloud providers, telemetry/monitor sources, LLMs,
> and back-office systems are **swappable task nodes** invoked by the BPMN flow. The two
> UiPath pillars carry the work: **Agent Builder** (agentic decisioning) and the **RPA Robot**
> (provisioning GPUs and executing into systems without clean APIs).

## Why vendor-agnostic

A vendor-agnostic orchestration core is the difference between a drop-in adoption path and a
rip-and-replace pitch. A research team keeps its existing cloud accounts, training framework, and
registries; the BPMN orchestration sits on top. Each task node has a defined interface, which is
what makes exception handling, retries, and fallbacks possible (e.g. primary cloud provider out of
quota → swap to a secondary or a mock).

## The two UiPath pillars

| Pillar | UiPath component | What it does here |
|---|---|---|
| **Agentic** | **Agent Builder** | Telemetry Analyst (classify + risk), Anomaly Risk Agent (Fast-Track gateway), Cost & Impact Agent (cloud-GPU economic/org impact), compliance-summary agent — each a Maestro-callable agent that *reasons and decides*. |
| **RPA** | **RPA Robot** + API Workflows | Provisions cost-optimal GPUs (AWS/GCP/AMD), SSH-launches/kills training containers, and writes outcomes into the cloud console, billing dashboard, and model registry — through the UI where there is no API, via API Workflows where there is. |
| **Governance** | **Action Center** | Human-in-the-loop approval for cost/physics-safety gates; researcher sign-off on checkpoints. |
| **Backbone** | **Maestro BPMN** | Top-level process (BPMN 2.0): tasks, gateways, events, swimlanes; immutable audit at each node. |

## Swappable integration points

| Source (swappable) | Cloud provider (swappable) | LLM agent (swappable) | Back-office systems (swappable) |
| :--- | :--- | :--- | :--- |
| • Reward/loss telemetry<br>• Container logs<br>• Hardware monitor (GPU/thermal)<br>• Researcher console | • AWS Spot (H100)<br>• GCP (A100/L4)<br>• AMD Developer Cloud (MI300X)<br>• Mock cloud API | • Claude via LangChain<br>• Gemini via LangChain | • Cloud console / billing (**RPA**)<br>• Quota dashboard<br>• Model registry<br>• Audit log / notifications |

## Reference flow (BPMN tasks)

A training run raises an anomaly; the BPMN orchestrates triage and approved remediation:

1. **Anomaly Intake** — telemetry/logs/monitor/console raises an event (type, run, severity, evidence) → canonical `IncidentReport`.
2. **Telemetry Analyst (agent)** — categorize the anomaly (GRADIENT_COLLAPSE / LOSS_DIVERGENCE / HARDWARE_FAULT / RESOURCE_RISK).
3. **Anomaly Risk Agent (agent)** — risk score; critical zones (high-cost-gpu, production-bound, public-benchmark, long-running) bias toward HITL.
4. **Cost & Impact Agent (agent)** — cloud-GPU economic + organizational impact → Fast Track (autonomous) or Researcher Review Board.
5. **Researcher Review Board (HITL)** — Action Center approval for high-risk / high-cost actions.
6. **Execute Remediation** — SSH-shutdown a diverging run, release/teardown an instance; HOLD a production-bound run if unsafe.
7. **Cloud/Registry Write-back (RPA)** — the RPA Robot records the action in the cloud console / billing dashboard / model registry.
8. **Quality Assurance** — compliance-summary agent + immutable audit entry + researcher sign-off.

End-to-end target: seconds-to-minutes per anomaly; full audit trail; HITL only where risk warrants it.

## Swap-ability matrix

| Layer | Reference choice | Drop-in alternatives |
|---|---|---|
| Training workload | Unitree G1 MuJoCo RL skills | Any RL/IL training container, any robot embodiment |
| Source | Reward/loss telemetry + logs + monitor | Stable-Baselines3 callbacks, W&B, Prometheus, supplier feed |
| LLM | Claude (primary), Gemini (fallback) | OpenAI, local LLM through LangChain |
| Cloud / back-office | Mocked cloud / billing / registry endpoints | AWS/GCP/AMD APIs, decentralized GPU (Vast.ai/Akash), model registries via UiPath RPA/connectors |

## What this is **not**

- Not a single-vendor proof of concept.
- Not a robot demo where UiPath sits beside the workflow — UiPath *is* the orchestration (agentic + RPA).
- Not a slide deck with a happy-path diagram — the orchestration is meant to actually run (`python run_pipeline.py`).
