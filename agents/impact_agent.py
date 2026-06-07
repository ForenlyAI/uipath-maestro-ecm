"""Impact Analysis — the agentic economic + organizational impact task node.

Sits between root-cause analysis and the routing gateway in the Maestro BPMN.
Given a canonical IncidentReport from a robotic lawn-mower fleet plus the Fleet AI
Analyst disposition, it estimates the **economic** and **organizational** impact of
acting (or not) on a detected fault, and turns that into the routing signal: a
costly, safety-critical, or fleet-wide fault escalates to a human review board
(Action Center); a cheap, contained one is auto-resolved on the Fast Track.

Design choice: the *scoring is deterministic and auditable* (like the gateway in
`samples/simulate_gateway.py`) — an LLM may narrate the rationale, but never sets
the numbers. The dollar figures are ILLUSTRATIVE model inputs (parameters below),
not measured costs; the contribution is the model that combines them, not the
specific values.
"""
import re

# --- Illustrative model parameters (not measured costs) ---------------------
# Downtime cost per hour a mower (and its route) is offline, by asset criticality.
DOWNTIME_USD_PER_HOUR = {"critical": 1200.0, "high": 600.0, "medium": 200.0, "low": 50.0}
# Baseline direct repair/service cost by fault category.
REPAIR_BASE_USD = {
    "MOBILITY_FAULT": 600.0,
    "BLADE_FAULT": 250.0,
    "BOUNDARY_BREACH": 150.0,
    "OPERATIONAL_RISK": 100.0,
}
# Consequence cost if the fault is left unaddressed and fails in the field
# (unit loss, off-property/road liability, blade-strike injury or property damage).
FAILURE_CONSEQUENCE_USD = {
    "MOBILITY_FAULT": 15000.0,
    "BOUNDARY_BREACH": 12000.0,
    "BLADE_FAULT": 8000.0,
    "OPERATIONAL_RISK": 2000.0,
}
# Probability the fault fails / recurs in the field, by severity.
P_FAILURE = {"critical": 0.6, "high": 0.4, "medium": 0.2, "low": 0.05}
# Hours the mower is offline to remediate, by severity.
DOWNTIME_HOURS = {"critical": 16.0, "high": 8.0, "medium": 4.0, "low": 1.0}
# Lead time (days) to remediate, by severity.
LEAD_TIME_DAYS = {"critical": 5, "high": 3, "medium": 2, "low": 1}

# Economic-impact dollars that map to a normalized score of 1.0.
ECONOMIC_CAP_USD = 25000.0
# Routing thresholds.
ECONOMIC_HITL_THRESHOLD = 0.40          # economicImpactScore >= this -> HITL
FLEET_QUANTITY_THRESHOLD = 10           # affected units >= this -> fleet-wide

# Operating zones that make a fault inherently safety-critical for a mower.
SAFETY_ZONES = ("near-road", "near-water", "public-access", "steep-slope")
# Fault cues (in subject/description) that imply a safety-critical failure mode —
# someone could be hurt or the unit lost.
SAFETY_CUES = ("strike", "road", "water", "rollover", "tip", "injury", "person", "child", "pond")


def _severity(incident):
    return (incident.get("severity") or "low").lower()


def _affected_units(incident):
    return sum(int(i.get("quantity", 1)) for i in incident.get("affectedItems", []))


def _org_scope(incident):
    """SINGLE_UNIT / MULTI_TEAM / FLEET_WIDE — how wide the organizational reach is."""
    units = _affected_units(incident)
    tags = " ".join(incident.get("tags", [])).lower()
    if units >= FLEET_QUANTITY_THRESHOLD or "fleet" in tags or "recall" in tags:
        return "FLEET_WIDE"
    suppliers = {i.get("supplierId") for i in incident.get("affectedItems", []) if i.get("supplierId")}
    item_types = {i.get("itemType") for i in incident.get("affectedItems", [])}
    if len(suppliers) > 1 or len(item_types) > 1:
        return "MULTI_TEAM"
    return "SINGLE_UNIT"


def _safety_critical(incident, disposition):
    if incident.get("safetyZone", "").lower() in SAFETY_ZONES:
        return True
    if disposition.get("category") in ("MOBILITY_FAULT", "BLADE_FAULT") and _severity(incident) in ("high", "critical"):
        return True
    blob = (incident.get("subject", "") + " " + incident.get("description", "")).lower()
    # Word-boundary match so e.g. "watering" does NOT trip the "water" cue.
    tokens = set(re.findall(r"[a-z]+", blob))
    return any(cue in tokens for cue in SAFETY_CUES)


def _roles_engaged(incident, disposition, safety_critical, org_scope):
    """Which teams the fault pulls in — the organizational footprint."""
    roles = ["AI Analyst"]
    cat = disposition.get("category")
    if cat == "MOBILITY_FAULT":
        roles.append("Drivetrain Technician")
    elif cat == "BLADE_FAULT":
        roles.append("Cutting-Deck Technician")
    elif cat == "BOUNDARY_BREACH":
        roles.append("Navigation/RTK Specialist")
    roles.append("Fleet Maintenance Crew")
    if safety_critical:
        roles.append("Safety Officer")
    if org_scope in ("MULTI_TEAM", "FLEET_WIDE"):
        roles.append("Procurement")
        roles.append("Fleet Operations Manager")
    if org_scope == "FLEET_WIDE":
        roles.append("Reliability Engineering")
    return roles


def assess(incident, disposition):
    """Impact Analysis task node.

    Returns a structured impact payload that the BPMN gateway consumes:
    economicImpactScore, estimatedCostUsd, leadTimeDays, orgScope, safetyCritical,
    rolesEngaged, hitlRequired, route, hitlReason.
    """
    sev = _severity(incident)
    cat = disposition.get("category", "OPERATIONAL_RISK")

    repair = REPAIR_BASE_USD.get(cat, 100.0) * max(1, _affected_units(incident))
    downtime = DOWNTIME_USD_PER_HOUR.get(sev, 50.0) * DOWNTIME_HOURS.get(sev, 1.0)
    inaction_risk = P_FAILURE.get(sev, 0.05) * FAILURE_CONSEQUENCE_USD.get(cat, 2000.0)
    estimated_cost = round(repair + downtime + inaction_risk, 2)
    economic_score = round(min(estimated_cost / ECONOMIC_CAP_USD, 1.0), 3)

    org_scope = _org_scope(incident)
    safety_critical = _safety_critical(incident, disposition)
    roles = _roles_engaged(incident, disposition, safety_critical, org_scope)

    # Routing: HITL if the analyst already flagged it, OR economic impact is high,
    # OR it is safety-critical, OR the organizational reach is fleet-wide.
    reasons = []
    if disposition.get("hitlRequired"):
        reasons.append(f"analyst risk {disposition.get('riskScore')}/conf {disposition.get('confidence')}")
    if economic_score >= ECONOMIC_HITL_THRESHOLD:
        reasons.append(f"economic impact {economic_score} (~${estimated_cost:,.0f})")
    if safety_critical:
        reasons.append("safety-critical")
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
