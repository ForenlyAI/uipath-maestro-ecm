#!/usr/bin/env python3
"""End-to-end local orchestration of the field-inspection BPMN flow.

This is the runnable proof that the orchestration actually runs (see
docs/ARCHITECTURE.md — "the orchestration is meant to actually run"). It chains the
same stages the UiPath Maestro BPMN models, as plain Python task nodes:

    trigger (IncidentReport)
      -> Vision AI Analyst agent      (classify + Safety Risk score)
      -> Agentic Fast-Track gateway   (HITL required?  -> Action Center : autonomous)
      -> Action stage                 (open QA ticket via mock enterprise API)
      -> Immutable audit log

Usage:
    python run_pipeline.py                                  # run all sample triggers
    python run_pipeline.py samples/triggers/mower_blade_strike.json
"""
import glob
import json
import sys

from agents.analyst_agent import analyze
from mocks import enterprise_store as store


def _audit(incident_id, stage, actor, detail):
    store.append_audit(incident_id, stage, actor, detail)


def process(incident):
    iid = incident.get("incidentId", "UNKNOWN")
    print(f"\n=== {iid} :: {incident.get('subject', '')[:64]}")
    _audit(iid, "INTAKE", "orchestrator", f"severity={incident.get('severity')}")

    # Stage 1-3: Vision AI Analyst (classification + Safety Risk Agent)
    disp, provider = analyze(incident)
    print(f"  analyst [{provider}] -> {disp['category']} "
          f"risk={disp['riskScore']} conf={disp['confidence']} action={disp['suggestedAction']}")
    _audit(iid, "ANALYSIS", "vision-ai-analyst",
           f"{disp['category']} risk={disp['riskScore']} action={disp['suggestedAction']}")

    # Stage: Agentic Fast-Track gateway
    if disp["hitlRequired"]:
        print("  gateway -> HITL: routed to Compliance Review Board (Action Center)")
        _audit(iid, "GATEWAY", "fast-track-gateway", "HITL required -> Action Center")
        route = "ACTION_CENTER"
    else:
        print("  gateway -> FAST TRACK: autonomous remediation, no human gate")
        _audit(iid, "GATEWAY", "fast-track-gateway", "low risk -> autonomous fast track")
        route = "AUTONOMOUS"

    # Stage: Action — open a remediation ticket in the (mock) enterprise system
    ticket = store.open_ticket(
        iid, disp["category"], disp["suggestedAction"], disp["riskScore"],
        assigned_to="compliance-board" if route == "ACTION_CENTER" else "auto-remediation",
    )
    print(f"  action  -> {ticket['ticketId']} ({ticket['status']}, owner={ticket['assignedTo']})")
    _audit(iid, "ACTION", "enterprise-api", f"opened {ticket['ticketId']} -> {ticket['assignedTo']}")

    return {"incidentId": iid, "route": route, "ticket": ticket["ticketId"], **disp}


def main(paths):
    if not paths:
        paths = sorted(p for p in glob.glob("samples/triggers/*.json") if "schema" not in p)
    results = []
    for path in paths:
        with open(path) as fh:
            results.append(process(json.load(fh)))

    hitl = sum(1 for r in results if r["route"] == "ACTION_CENTER")
    print(f"\n--- processed {len(results)} incident(s): {hitl} routed to HITL, "
          f"{len(results) - hitl} autonomous fast-track ---")
    return results


if __name__ == "__main__":
    main(sys.argv[1:])
