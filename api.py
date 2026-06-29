import glob
import json
import os
import subprocess
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from mocks import enterprise_store as store

app = FastAPI(title="Sentinel API")

# Enable CORS for the Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/dashboard")
def get_dashboard_stats():
    # Mocking some dashboard stats
    return {
        "total_incidents": 142,
        "hitl_routed": 38,
        "autonomous_resolved": 104,
        "cloud_cost_saved": 14500,
        "avg_response_time_sec": 4.2
    }


@app.get("/api/incidents")
def get_incidents():
    incidents = []
    for path in glob.glob("samples/triggers/*.json"):
        if "schema" in path:
            continue
        try:
            with open(path) as f:
                data = json.load(f)
                incidents.append(data)
        except Exception:
            pass
    return incidents


@app.get("/api/incidents/{incident_id}")
def get_incident(incident_id: str):
    incidents = get_incidents()
    for inc in incidents:
        if inc.get("incidentId") == incident_id:
            return inc
    raise HTTPException(status_code=404, detail="Incident not found")


@app.get("/api/queue")
def get_queue():
    # Check if we should use orchestrator or mock
    try:
        if all(k in os.environ for k in ["UIPATH_ORG", "UIPATH_TENANT", "UIPATH_CLIENT_ID", "UIPATH_CLIENT_SECRET", "UIPATH_FOLDER_ID"]):
            from integrations.orchestrator_client import Orchestrator
            client = Orchestrator()
            q_def = client.ensure_queue("IncidentReports")
            items = client.list_queue_items(q_def["Id"])
            return items
    except Exception as e:
        print(f"Orchestrator integration failed, using mock queue: {e}")

    # Fallback to mock data or tickets
    return [
        {"Id": t["ticketId"], "Reference": t["incidentId"], "Status": t["status"], "Priority": "High", "CreationTime": "Just now"}
        for t in store._TICKETS
    ]


@app.get("/api/analytics")
def get_analytics():
    return {
        "risk_distribution": [
            {"name": "Low", "value": 45},
            {"name": "Medium", "value": 35},
            {"name": "High", "value": 20},
        ],
        "queue_growth": [
            {"time": "10:00", "items": 12},
            {"time": "10:05", "items": 15},
            {"time": "10:10", "items": 18},
            {"time": "10:15", "items": 25},
            {"time": "10:20", "items": 30},
        ]
    }


@app.get("/api/audit")
def get_audit():
    return store.read_audit()


@app.get("/api/pipeline/run")
def run_pipeline():
    """Runs run_pipeline.py synchronously and returns all output lines as JSON."""
    try:
        result = subprocess.run(
            [sys.executable, "-u", "run_pipeline.py"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
            timeout=60
        )
        output = result.stdout + result.stderr
        lines = [line for line in output.splitlines() if line.strip()]
        return {"lines": lines}
    except subprocess.TimeoutExpired:
        return {"lines": ["ERROR: Pipeline timed out after 60s"]}
    except Exception as e:
        return {"lines": [f"ERROR: {str(e)}"]}


@app.post("/api/pipeline/push")
def push_pipeline():
    try:
        subprocess.run([sys.executable, "integrations/push_incidents.py"], check=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        return {"status": "success"}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=str(e))
