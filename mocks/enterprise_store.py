"""In-memory enterprise systems store — standard library only.

This is the swappable QA-ticket / CRM / audit task node behind the BPMN action
stage. Keeping it dependency-free means `run_pipeline.py` runs end-to-end with the
stdlib alone; `enterprise_api.py` puts a FastAPI/HTTP face on the same functions for
a live demo. In production these calls go to ServiceNow / SAP / a compliance audit
service through UiPath connectors.
"""

_TICKETS: list[dict] = []
_AUDIT: list[dict] = []
_SUPPLIERS = {
    "sup-acme-001": {"supplierId": "sup-acme-001", "name": "ACME Assemblies", "tier": "A", "openNCRs": 2},
    "sup-globex-002": {"supplierId": "sup-globex-002", "name": "Globex Components", "tier": "B", "openNCRs": 5},
    "sup-techparts-003": {"supplierId": "sup-techparts-003", "name": "TechParts Industries", "tier": "A", "openNCRs": 0},
    "sup-primecut-004": {"supplierId": "sup-primecut-004", "name": "PrimeCut Robotics", "tier": "C", "openNCRs": 12},
}


def get_supplier(supplier_id):
    return _SUPPLIERS.get(supplier_id)


def open_ticket(incident_id, category, suggested_action, risk_score, assigned_to="qa-queue",
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
