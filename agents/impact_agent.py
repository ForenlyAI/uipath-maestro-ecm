"""Cost & Impact Analysis — the agentic economic + organizational impact task node.

Sits between root-cause analysis and the routing gateway in the Maestro BPMN.
Given a canonical IncidentReport (a training-run anomaly) from a humanoid RL
training fleet plus the Telemetry Analyst disposition, it estimates the **economic**
(cloud GPU $) and **organizational** impact of acting (or not) on a detected
anomaly, and turns that into the routing signal: a costly, production-bound, or
fleet-wide anomaly escalates to a human review board (Action Center); a cheap,
contained one is auto-resolved on the Fast Track.

Design choice: the *scoring is deterministic and auditable* (like the gateway in
`samples/simulate_gateway.py`) — an LLM may narrate the rationale, but never sets
the numbers. The dollar figures are ILLUSTRATIVE model inputs (parameters below),
not measured costs; the contribution is the model that combines them, not the
specific values.
"""
import re

# --- Illustrative model parameters (not measured costs) ---------------------
# Idle/wasted GPU cost per hour a run (and its instance) burns, by criticality.
DOWNTIME_USD_PER_HOUR = {"critical": 1200.0, "high": 600.0, "medium": 200.0, "low": 50.0}
# Baseline direct remediation cost (engineer time + relaunch) by anomaly category.
REPAIR_BASE_USD = {
    "LOSS_DIVERGENCE": 600.0,
    "GRADIENT_COLLAPSE": 250.0,
    "HARDWARE_FAULT": 150.0,
    "RESOURCE_RISK": 100.0,
}
# Consequence cost if the anomaly is left unaddressed (wasted multi-day run,
# a bad model shipped to a physical robot, blown cloud budget).
FAILURE_CONSEQUENCE_USD = {
    "LOSS_DIVERGENCE": 15000.0,
    "HARDWARE_FAULT": 12000.0,
    "GRADIENT_COLLAPSE": 8000.0,
    "RESOURCE_RISK": 2000.0,
}
# Probability the anomaly wastes the run / recurs, by severity.
P_FAILURE = {"critical": 0.6, "high": 0.4, "medium": 0.2, "low": 0.05}
# Hours of GPU time burned before remediation, by severity.
DOWNTIME_HOURS = {"critical": 16.0, "high": 8.0, "medium": 4.0, "low": 1.0}
# Lead time (days) to remediate / re-run, by severity.
LEAD_TIME_DAYS = {"critical": 5, "high": 3, "medium": 2, "low": 1}

# Economic-impact dollars that map to a normalized score of 1.0.
ECONOMIC_CAP_USD = 25000.0
# Routing thresholds.
ECONOMIC_HITL_THRESHOLD = 0.40          # economicImpactScore >= this -> HITL
FLEET_QUANTITY_THRESHOLD = 10           # affected jobs/instances >= this -> fleet-wide

# Criticality zones that make an anomaly inherently high-stakes for a run.
SAFETY_ZONES = ("high-cost-gpu", "production-bound", "public-benchmark", "long-running")
# Cues (in subject/description) that imply a high-stakes failure mode —
# expensive waste, or a model that will reach physical hardware.
SAFETY_CUES = ("oom", "thermal", "overheat", "runaway", "production", "hardware",
               "robot", "deploy", "collapse", "diverge", "nan")


def _severity(incident):
    return (incident.get("severity") or "low").lower()


def _affected_units(incident):
    return sum(int(i.get("quantity", 1)) for i in incident.get("affectedItems", []))


def _org_scope(incident):
    """SINGLE_RUN / MULTI_TEAM / FLEET_WIDE — how wide the organizational reach is."""
    units = _affected_units(incident)
    tags = " ".join(incident.get("tags", [])).lower()
    if units >= FLEET_QUANTITY_THRESHOLD or "fleet" in tags or "rollout" in tags:
        return "FLEET_WIDE"
    suppliers = {i.get("supplierId") for i in incident.get("affectedItems", []) if i.get("supplierId")}
    item_types = {i.get("itemType") for i in incident.get("affectedItems", [])}
    if len(suppliers) > 1 or len(item_types) > 1:
        return "MULTI_TEAM"
    return "SINGLE_RUN"


def _safety_critical(incident, disposition):
    if incident.get("safetyZone", "").lower() in SAFETY_ZONES:
        return True
    if disposition.get("category") in ("LOSS_DIVERGENCE", "GRADIENT_COLLAPSE") and _severity(incident) in ("high", "critical"):
        return True
    blob = (incident.get("subject", "") + " " + incident.get("description", "")).lower()
    # Word-boundary match so e.g. "deployment" does NOT trip the "deploy" cue.
    tokens = set(re.findall(r"[a-z]+", blob))
    return any(cue in tokens for cue in SAFETY_CUES)


def _roles_engaged(incident, disposition, safety_critical, org_scope):
    """Which teams the anomaly pulls in — the organizational footprint."""
    roles = ["Telemetry Analyst"]
    cat = disposition.get("category")
    if cat == "LOSS_DIVERGENCE":
        roles.append("RL Optimization Engineer")
    elif cat == "GRADIENT_COLLAPSE":
        roles.append("Reward-Shaping Engineer")
    elif cat == "HARDWARE_FAULT":
        roles.append("Cloud Infrastructure Engineer")
    roles.append("MLOps Crew")
    if safety_critical:
        roles.append("Robotics Safety Reviewer")
    if org_scope in ("MULTI_TEAM", "FLEET_WIDE"):
        roles.append("Cloud Budget Owner")
        roles.append("Training Operations Manager")
    if org_scope == "FLEET_WIDE":
        roles.append("Reliability Engineering")
    return roles


def assess(incident, disposition):
    """Cost & Impact Analysis task node.

    Returns a structured impact payload that the BPMN gateway consumes:
    economicImpactScore, estimatedCostUsd, leadTimeDays, orgScope, safetyCritical,
    rolesEngaged, hitlRequired, route, hitlReason.
    """
    sev = _severity(incident)
    cat = disposition.get("category", "RESOURCE_RISK")

    repair = REPAIR_BASE_USD.get(cat, 100.0) * max(1, _affected_units(incident))
    downtime = DOWNTIME_USD_PER_HOUR.get(sev, 50.0) * DOWNTIME_HOURS.get(sev, 1.0)
    inaction_risk = P_FAILURE.get(sev, 0.05) * FAILURE_CONSEQUENCE_USD.get(cat, 2000.0)
    estimated_cost = round(repair + downtime + inaction_risk, 2)
    economic_score = round(min(estimated_cost / ECONOMIC_CAP_USD, 1.0), 3)

    org_scope = _org_scope(incident)
    safety_critical = _safety_critical(incident, disposition)
    roles = _roles_engaged(incident, disposition, safety_critical, org_scope)

    # Routing: HITL if the analyst already flagged it, OR economic impact is high,
    # OR it is high-stakes (production-bound etc.), OR the reach is fleet-wide.
    reasons = []
    if disposition.get("hitlRequired"):
        reasons.append(f"analyst risk {disposition.get('riskScore')}/conf {disposition.get('confidence')}")
    if economic_score >= ECONOMIC_HITL_THRESHOLD:
        reasons.append(f"economic impact {economic_score} (~${estimated_cost:,.0f})")
    if safety_critical:
        reasons.append("high-stakes (production/cost critical)")
    if org_scope == "FLEET_WIDE":
        reasons.append("fleet-wide org scope")

    hitl_required = bool(reasons)
    return {
        "incidentId": incident.get("incidentId"),
        "economicImpactScore": economic_score,
        "estimatedCostUsd": estimated_cost,
        "costBreakdownUsd": {
            "repair": round(repair, 2),
            "downtime": round(downtime, 2),
            "inactionRisk": round(inaction_risk, 2),
        },
        "leadTimeDays": LEAD_TIME_DAYS.get(sev, 1),
        "orgScope": org_scope,
        "safetyCritical": safety_critical,
        "rolesEngaged": roles,
        "hitlRequired": hitl_required,
        "route": "ACTION_CENTER" if hitl_required else "AUTONOMOUS",
        "hitlReason": "; ".join(reasons) if reasons else "low economic + organizational impact",
    }
