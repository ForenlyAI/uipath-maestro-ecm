"""Mock enterprise systems — HTTP face over `enterprise_store`.

In production these are the cloud providers' billing/quota APIs, a model registry,
and a compliance audit service reached through UiPath connectors. Here a single FastAPI app gives the BPMN action
stage real HTTP endpoints to call during a live demo. The same logic is available
dependency-free in `enterprise_store` for the local runner and tests.

Run:
    pip install -r requirements.txt
    uvicorn mocks.enterprise_api:app --reload --port 8099
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from mocks import enterprise_store as store

app = FastAPI(title="Maestro Training-Fleet Mock Cloud-Ops API", version="0.1.0")


class Ticket(BaseModel):
    incidentId: str
    category: str
    suggestedAction: str
    riskScore: float
    assignedTo: str = "qa-queue"


class AuditEntry(BaseModel):
    incidentId: str
    stage: str
    actor: str
    detail: str


@app.get("/providers/{supplier_id}")
def get_supplier(supplier_id: str):
    record = store.get_supplier(supplier_id)
    if not record:
        raise HTTPException(status_code=404, detail="supplier not found")
    return record


@app.post("/qa/tickets")
def open_ticket(ticket: Ticket):
    return store.open_ticket(
        ticket.incidentId, ticket.category, ticket.suggestedAction,
        ticket.riskScore, ticket.assignedTo,
    )


@app.post("/audit/log")
def append_audit(entry: AuditEntry):
    return store.append_audit(entry.incidentId, entry.stage, entry.actor, entry.detail)


@app.get("/audit/log")
def read_audit():
    return {"entries": store.read_audit()}
