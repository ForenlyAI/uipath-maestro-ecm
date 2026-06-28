"""In-memory cloud-ops systems store — standard library only.

This is the swappable run-ticket / cloud-provider registry / audit task node behind
the BPMN action stage. Keeping it dependency-free means `run_pipeline.py` runs
end-to-end with the stdlib alone; `enterprise_api.py` puts a FastAPI/HTTP face on the
same functions for a live demo. In production these calls go to the cloud providers'
billing/quota APIs, a model registry, and a compliance audit service through UiPath
connectors.
"""

_TICKETS: list[dict] = []
_AUDIT: list[dict] = []
# Cloud-provider accounts (the "suppliers" of GPU capacity). tier = priority/discount
# tier; openIssues = open quota/billing/reliability issues on that account.
_SUPPLIERS = {
    "aws-us-east-1":   {"supplierId": "aws-us-east-1",   "name": "AWS Spot (us-east-1, H100)",        "tier": "A", "openIssues": 2},
    "gcp-us-central1": {"supplierId": "gcp-us-central1", "name": "GCP (us-central1, A100/L4)",         "tier": "B", "openIssues": 1},
    "amd-devcloud":    {"supplierId": "amd-devcloud",    "name": "AMD Developer Cloud (MI300X)",       "tier": "A", "openIssues": 0},
    "azure-ncv3":      {"supplierId": "azure-ncv3",      "name": "Azure NCv3 (V100)",                  "tier": "C", "openIssues": 4},
}


def get_supplier(supplier_id):
    return _SUPPLIERS.get(supplier_id)


def open_ticket(incident_id, category, suggested_action, risk_score, assigned_to="run-queue",
                supplier_context=None):
    record = {
        "ticketId": f"QA-{len(_TICKETS) + 1:05d}",
        "incidentId": incident_id,
        "category": category,
        "suggestedAction": suggested_action,
        "riskScore": risk_score,
        "assignedTo": assigned_to,
        "status": "OPEN",
        "supplierContext": supplier_context or {},
    }
    _TICKETS.append(record)
    return record


def append_audit(incident_id, stage, actor, detail):
    record = {
        "seq": len(_AUDIT) + 1,
        "incidentId": incident_id,
        "stage": stage,
        "actor": actor,
        "detail": detail,
    }
    _AUDIT.append(record)
    return record


def read_audit():
    return list(_AUDIT)
