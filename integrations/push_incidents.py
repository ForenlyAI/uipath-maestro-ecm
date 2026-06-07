#!/usr/bin/env python3
"""Push the sample IncidentReports into a live Orchestrator queue.

Each trigger is run through the Fleet AI Analyst, then enqueued with its triage
(category / riskScore / confidence / hitlRequired / route) as SpecificContent.
A Maestro/Studio process dequeues these and routes them — HITL items (high risk
or low confidence) to the Action Center, the rest to autonomous Fast Track.

    export UIPATH_ORG=... UIPATH_TENANT=DefaultTenant UIPATH_FOLDER_ID=...
    export UIPATH_CLIENT_ID=... UIPATH_CLIENT_SECRET=...
    python integrations/push_incidents.py
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.analyst_agent import analyze
from integrations.orchestrator_client import Orchestrator

QUEUE = "IncidentReports"


def main():
    orc = Orchestrator()
    orc.ensure_queue(QUEUE, "Robotic lawn-mower fleet incidents — agentic HITL triage")
    triggers = sorted(p for p in glob.glob("samples/triggers/*.json") if "schema" not in p)
    for path in triggers:
        inc = json.load(open(path))
        disp, _ = analyze(inc)
        content = {
            "incidentId": inc["incidentId"], "severity": inc.get("severity"),
            "subject": inc.get("subject"), "safetyZone": inc.get("safetyZone", "none"),
            "category": disp["category"], "riskScore": disp["riskScore"],
            "confidence": disp["confidence"], "hitlRequired": disp["hitlRequired"],
            "suggestedAction": disp["suggestedAction"],
            "route": "ACTION_CENTER" if disp["hitlRequired"] else "AUTONOMOUS",
        }
        item = orc.add_queue_item(
            QUEUE, inc["incidentId"], content,
            priority="High" if disp["hitlRequired"] else "Normal",
        )
        print(f"  + {inc['incidentId']} -> {content['category']} "
              f"risk={content['riskScore']} {content['route']} (item #{item.get('Id')})")
    print(f"pushed {len(triggers)} incident(s) to queue '{QUEUE}'")


if __name__ == "__main__":
    main()
