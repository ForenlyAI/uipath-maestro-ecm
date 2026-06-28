"""Telemetry Analyst — the agentic classification + risk task node.

Implements the contract declared in `artifacts/container1/agent_analyst.yaml`:
given a canonical IncidentReport (a training-run anomaly/event) from a humanoid RL
training fleet, it returns a structured disposition payload (category, riskScore,
confidence, hitlRequired, reasoning, suggestedAction).

In a UiPath deployment this runs as an **Agent Builder** agent invoked by the
Maestro BPMN gateway (the *agentic* half of the system). Here it runs as a plain
task node so the pipeline is runnable and testable locally. The Anomaly Risk math
is identical to the BPMN gateway rules (`samples/simulate_gateway.py`) regardless
of which provider answers.
"""
from agents.llm_provider import complete_json

# Training-run anomaly taxonomy.
CATEGORIES = ["GRADIENT_COLLAPSE", "LOSS_DIVERGENCE", "HARDWARE_FAULT", "RESOURCE_RISK"]
# Dispositions the agent can recommend for a run.
ACTIONS = ["RESTART", "TERMINATE", "INSPECT", "HOLD", "PROCEED"]

# HITL fires if risk crosses this OR classification confidence drops below 0.70.
RISK_HITL_THRESHOLD = 0.15
CONFIDENCE_HITL_THRESHOLD = 0.70

# Criticality zones that make any anomaly inherently high-stakes (a wrong
# autonomous call on an expensive GPU pool, a model bound for a physical robot, a
# published benchmark, or a multi-day run is costly). Read from the `safetyZone`.
SAFETY_ZONES = ("high-cost-gpu", "production-bound", "public-benchmark", "long-running")

SYSTEM_PROMPT = """You are the Telemetry Analyst, an autonomous agent inside UiPath Agent Builder.
Ingest the IncidentReport JSON (a training-run anomaly/event) from a humanoid RL
training fleet and return ONLY a JSON object with these keys:
incidentId, category, riskScore, confidence, hitlRequired, reasoning, suggestedAction.

Rules:
- category is one of GRADIENT_COLLAPSE, LOSS_DIVERGENCE, HARDWARE_FAULT, RESOURCE_RISK.
- riskScore: baseline 0.05; +0.50 critical / +0.25 high / +0.10 medium severity;
  +0.15 if detectorConfidence < 0.8; x1.5 if safetyZone is a critical zone
  (high-cost-gpu, production-bound, public-benchmark, long-running); clamp 0..1.
- confidence is your 0..1 confidence in the classification.
- hitlRequired is true if riskScore >= 0.15 OR confidence < 0.70.
- suggestedAction is one of RESTART, TERMINATE, INSPECT, HOLD, PROCEED.
- Never echo tenant URLs or credentials."""


def _score_offline(incident):
    """Deterministic mirror of the BPMN gateway — used when no LLM key is set."""
    risk = 0.05
    risk += {"critical": 0.50, "high": 0.25, "medium": 0.10}.get(
        incident.get("severity", "low").lower(), 0.0
    )
    if incident.get("source", {}).get("detectorConfidence", 1.0) < 0.8:
        risk += 0.15
    if incident.get("safetyZone", "").lower() in SAFETY_ZONES:
        risk *= 1.5
    risk = min(max(risk, 0.0), 1.0)

    blob = (incident.get("subject", "") + " " + incident.get("description", "")).lower()
    if any(w in blob for w in ("gradient", "collapse", "vanish", "nan", "flatline",
                               "plateau", "reward collapse", "no learning", "zero gradient")):
        category = "GRADIENT_COLLAPSE"
    elif any(w in blob for w in ("diverg", "loss spike", "reward crash", "unstable",
                                 "oscillat", "exploded", "exploding loss", "blew up")):
        category = "LOSS_DIVERGENCE"
    elif any(w in blob for w in ("oom", "out of memory", "cuda", "thermal", "overheat",
                                 "throttl", "ecc error", "xid", "hardware fault",
                                 "gpu fault", "instance crash", "node failure")):
        category = "HARDWARE_FAULT"
    else:
        category = "RESOURCE_RISK"

    confidence = 0.92 if incident.get("source", {}).get("detectorConfidence", 1.0) >= 0.8 else 0.65
    action = {
        "GRADIENT_COLLAPSE": "HOLD" if risk >= 0.5 else "RESTART",
        "LOSS_DIVERGENCE": "TERMINATE" if risk >= 0.5 else "RESTART",
        "HARDWARE_FAULT": "HOLD",
        "RESOURCE_RISK": "PROCEED",
    }[category]

    return {
        "incidentId": incident.get("incidentId"),
        "category": category,
        "riskScore": round(risk, 3),
        "confidence": confidence,
        "hitlRequired": risk >= RISK_HITL_THRESHOLD or confidence < CONFIDENCE_HITL_THRESHOLD,
        "reasoning": f"Rule-based disposition: {category} at risk {round(risk, 3)} "
        f"(severity={incident.get('severity')}, zone={incident.get('safetyZone', 'n/a')}).",
        "suggestedAction": action,
    }


def _validate(result, incident):
    """Coerce/guard LLM output so a downstream BPMN node always gets a clean payload."""
    result.setdefault("incidentId", incident.get("incidentId"))
    if result.get("category") not in CATEGORIES:
        result["category"] = "RESOURCE_RISK"
    if result.get("suggestedAction") not in ACTIONS:
        result["suggestedAction"] = "INSPECT"
    result["riskScore"] = min(max(float(result.get("riskScore", 0.0)), 0.0), 1.0)
    result["confidence"] = min(max(float(result.get("confidence", 0.0)), 0.0), 1.0)
    # The gateway is authoritative: recompute hitlRequired from the numbers, never trust the model.
    result["hitlRequired"] = (
        result["riskScore"] >= RISK_HITL_THRESHOLD
        or result["confidence"] < CONFIDENCE_HITL_THRESHOLD
    )
    return result


def analyze(incident):
    """Run the analyst task node. Returns (disposition_dict, provider_label)."""
    result, provider = complete_json(SYSTEM_PROMPT, incident, _score_offline)
    return _validate(result, incident), provider
