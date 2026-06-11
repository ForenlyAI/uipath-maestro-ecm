# Container 3 — Decision & Compliance Subprocess

This container handles the business decision-making and compliance enforcement for robotic lawn-mower fleet incidents.

It uses an autonomous **Decision Agent** to map classified incidents to operational compliance actions, and delegates high-risk or high-impact choices to human stakeholders via the **Action Center Review Board**.

## File Contents

- [decision_compliance.bpmn](./decision_compliance.bpmn): The subprocess diagram conformant to BPMN 2.0. Defines swimlanes, agent tasks, gateways, and transition flows.
- [agent_decision.yaml](./agent_decision.yaml): Configuration playbook for the Decision Agent (Agent Builder).
- [action_center_review_board.json](./action_center_review_board.json): Action Center human-review task form schema and disposition types for the compliance review board.

---

## Architectural Process Flow

```mermaid
graph TD
    Start([Subprocess Triggered]) --> Decision[Decision Agent]
    Decision -->|Compliance Action| Gateway{Is High Risk?}
    
    Gateway -->|Risk >= 0.15 OR Action != PROCEED| HITL[Action Center Review Board]
    Gateway -->|Risk < 0.15 AND Action = PROCEED| Log[Record in CMMS & Audit Log]
    
    HITL --> Log
    Log --> End([Compliance Completed])
```

---

## Key Interfaces & Data Shapes

### 1. Decision Agent (`agent_decision.yaml`)
- **Inputs**: Normalized `IncidentReport` JSON, incident category, and safety risk score.
- **Compliance Actions**:
  - `REWORK`: Salvageable physical repairs/servicing.
  - `SCRAP`: Extreme damage, component decommission.
  - `AUDIT`: Telemetry coordinates calibration/verification.
  - `HOLD`: Lockout/safety quarantine.
  - `PROCEED`: Resume automated operation.
- **Outputs**:
  - `incidentId` (string)
  - `complianceAction`: One of the 5 values above.
  - `reasoning` (string): Cognitive justification.

### 2. High-Risk Rule Criteria
The Exclusive Gateway checks if the incident meets compliance review requirements:
- **High-Risk (Requires Review Board)**: `${riskScore >= 0.15 || complianceAction != 'PROCEED'}`
- **Low-Risk (Auto-logs and completes)**: `${riskScore < 0.15 && complianceAction == 'PROCEED'}`

### 3. Human-In-The-Loop Sign-Off (`action_center_review_board.json`)
For high-risk reviews, a task is created on UiPath Action Center displaying read-only context (incident ID, category, risk score, proposed action, and AI reasoning) and requiring:
1. Final disposition (`APPROVE_REWORK`, `APPROVE_SCRAP`, `APPROVE_AUDIT`, `APPROVE_HOLD`, `APPROVE_PROCEED`, `OVERRIDE_TO_PROCEED`, `OVERRIDE_TO_HOLD`).
2. Mandatory, audit-logged text explanation (`reviewerNotes`, minimum 10 characters).
3. Authorized signature (`reviewerName`).
4. Compliance Work Order ID (`workOrderId` pattern matching `WO-YYYY-NNNN+`).
