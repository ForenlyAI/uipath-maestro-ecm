#!/usr/bin/env python3
import json
import glob
import os

# Criticality zones for a training run (mirror of analyst_agent).
SAFETY_ZONES = ("high-cost-gpu", "production-bound", "public-benchmark", "long-running")


def calculate_gateway(incident):
    # 1. Baseline risk score = 0.05
    risk_score = 0.05

    # 2. Add severity modifier
    severity = incident.get("severity", "low").lower()
    if severity == "critical":
        risk_score += 0.50
    elif severity == "high":
        risk_score += 0.25
    elif severity == "medium":
        risk_score += 0.10

    # 3. Add detector-uncertainty modifier if detectorConfidence < 0.8
    source = incident.get("source", {})
    detector_confidence = source.get("detectorConfidence", 1.0)
    if detector_confidence < 0.8:
        risk_score += 0.15

    # 4. Multiply by 1.5 if the run was in a critical zone
    safety_zone = incident.get("safetyZone", "").lower()
    if safety_zone in SAFETY_ZONES:
        risk_score *= 1.5

    # Clamp risk_score between 0.0 and 1.0
    risk_score = min(max(risk_score, 0.0), 1.0)

    # 5. Classify the anomaly from subject/description cues
    blob = (incident.get("subject", "") + " " + incident.get("description", "")).lower()
    category = "RESOURCE_RISK"
    if any(w in blob for w in ("gradient", "collapse", "vanish", "nan", "flatline", "plateau")):
        category = "GRADIENT_COLLAPSE"
    elif any(w in blob for w in ("diverg", "loss spike", "reward crash", "unstable", "oscillat")):
        category = "LOSS_DIVERGENCE"
    elif any(w in blob for w in ("oom", "out of memory", "cuda", "thermal", "overheat", "throttl")):
        category = "HARDWARE_FAULT"

    # Mock analyst confidence
    analyst_confidence = 0.92 if detector_confidence >= 0.8 else 0.65

    # 6. Gateway Rule: HITL required if riskScore >= 0.15 OR confidence < 0.70
    hitl_required = (risk_score >= 0.15) or (analyst_confidence < 0.70)

    return {
        "incidentId": incident.get("incidentId"),
        "category": category,
        "riskScore": round(risk_score, 2),
        "confidence": analyst_confidence,
        "hitlRequired": hitl_required,
        "severity": severity,
        "safetyZone": safety_zone or "none",
    }


def main():
    print("==========================================================================")
    print("   UiPath Agentic Gateway & Anomaly Risk Agent - Local Simulation Engine   ")
    print("==========================================================================\n")

    triggers = glob.glob("samples/triggers/*.json")
    triggers = [t for f in triggers if "schema" not in (t := os.path.basename(f))]

    if not triggers:
        print("No sample triggers found in samples/triggers/.")
        return

    print(f"Found {len(triggers)} sample triggers. Running simulation...\n")

    print(f"{'Trigger File':<34} | {'Incident ID':<16} | {'Severity':<8} | {'Zone':<16} | {'Risk':<5} | {'Conf':<5} | {'HITL?':<5}")
    print("-" * 104)

    for t_file in sorted(triggers):
        path = os.path.join("samples/triggers", t_file)
        with open(path, "r") as f:
            incident = json.load(f)

        res = calculate_gateway(incident)

        hitl_str = "YES" if res["hitlRequired"] else "NO"
        print(f"{t_file:<34} | {res['incidentId']:<16} | {res['severity']:<8} | {res['safetyZone']:<16} | {res['riskScore']:<5.2f} | {res['confidence']:<5.2f} | {hitl_str:<5}")

    print("\n" + "=" * 74)
    print("Simulation rules applied:")
    print("  - Base risk: 0.05. Add: medium (+0.10), high (+0.25), critical (+0.50).")
    print("  - Critical zone (high-cost-gpu/production-bound/public-benchmark/long-running): risk x1.5.")
    print("  - If detector confidence < 0.8: add 0.15 to risk.")
    print("  - HITL is triggered if Risk Score >= 0.15 OR Analyst Confidence < 0.70.")
    print("=" * 74)


if __name__ == "__main__":
    main()
