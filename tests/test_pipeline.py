"""End-to-end pipeline tests — run offline (stdlib only, no API keys).

    python -m pytest tests/ -q      # or: python tests/test_pipeline.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.analyst_agent import analyze
from mocks import enterprise_store as store
import run_pipeline


HIGH_RISK = {
    "incidentId": "IR-TEST-HIGH",
    "source": {"type": "vision", "detectorConfidence": 0.94},
    "severity": "high",
    "subject": "Mower stuck on steep slope, drivetrain stalled at 41 deg tilt",
    "description": "fleet unit bogged on a wet slope; wheels slipping, drivetrain stalled",
    "safetyZone": "steep-slope",
}

LOW_RISK = {
    "incidentId": "IR-TEST-LOW",
    "source": {"type": "manual", "detectorConfidence": 0.99},
    "severity": "low",
    "subject": "Routine operational note",
    "description": "minor cosmetic scuff on the housing, no functional impact",
    "safetyZone": "none",
}


def test_high_risk_routes_to_hitl():
    disp, _ = analyze(HIGH_RISK)
    assert disp["category"] == "MOBILITY_FAULT"
    assert disp["hitlRequired"] is True
    assert 0.0 <= disp["riskScore"] <= 1.0


def test_low_risk_is_fast_tracked():
    disp, _ = analyze(LOW_RISK)
    assert disp["hitlRequired"] is False


def test_gateway_is_authoritative_over_model_output():
    # Even if a provider returned a bad hitl flag, _validate recomputes it from the math.
    disp, _ = analyze(HIGH_RISK)
    expected = disp["riskScore"] >= 0.15 or disp["confidence"] < 0.70
    assert disp["hitlRequired"] == expected


def test_pipeline_end_to_end_and_audit_trail():
    results = run_pipeline.main([])  # all sample triggers
    assert len(results) >= 1

    for r in results:
        assert r["route"] in ("ACTION_CENTER", "AUTONOMOUS")
        assert r["ticket"].startswith("QA-")

    # Every processed incident leaves an immutable audit trail.
    audit = store.read_audit()

    assert any(e["stage"] == "INTAKE" for e in audit)
    assert any(e["stage"] == "ANALYSIS" for e in audit)
    assert any(e["stage"] == "GATEWAY" for e in audit)
    assert any(e["stage"] == "ACTION" for e in audit)


# ── NEW EDGE-CASE TESTS (Issue #3) ─────────────────────────────────────────

def test_low_confidence_triggers_hitl():
    """Detector confidence < 0.8 adds +0.15 risk AND offline confidence=0.65 (<0.70),
    so hitlRequired must be True even for a low-severity incident."""
    low_conf_incident = {
        "incidentId": "IR-TEST-LOWCONF",
        "source": {"type": "sensor", "detectorConfidence": 0.55},
        "severity": "low",
        "subject": "Routine check with unreliable sensor reading",
        "description": "sensor confidence below acceptable threshold during patrol",
        "safetyZone": "none",
    }
    disp, _ = analyze(low_conf_incident)
    assert disp["hitlRequired"] is True, (
        f"Expected hitlRequired=True for low detector confidence, "
        f"got riskScore={disp['riskScore']} confidence={disp['confidence']}"
    )
    assert 0.0 <= disp["riskScore"] <= 1.0
    assert 0.0 <= disp["confidence"] <= 1.0


def test_missing_fields_do_not_crash():
    """An incident with only incidentId must produce a schema-valid output without raising."""
    minimal_incident = {"incidentId": "IR-TEST-MINIMAL"}
    disp, _provider = analyze(minimal_incident)

    for key in ("category", "riskScore", "confidence", "hitlRequired", "suggestedAction"):
        assert key in disp, f"Missing required key: {key}"
    assert isinstance(disp["hitlRequired"], bool)
    assert 0.0 <= disp["riskScore"] <= 1.0
    assert 0.0 <= disp["confidence"] <= 1.0
    assert disp["category"] in ("BLADE_FAULT", "MOBILITY_FAULT", "BOUNDARY_BREACH", "OPERATIONAL_RISK")
    assert disp["suggestedAction"] in ("SERVICE", "RECALL", "INSPECT", "HOLD", "PROCEED")


def test_non_regulated_class_defaults_to_operational_risk():
    """An incident description with no blade/mobility/boundary keywords falls into OPERATIONAL_RISK."""
    unclassified_incident = {
        "incidentId": "IR-TEST-UNCLASS",
        "source": {"type": "manual", "detectorConfidence": 0.95},
        "severity": "low",
        "subject": "Software version mismatch notification",
        "description": "firmware version v2.1 does not match fleet baseline v2.3",
        "safetyZone": "none",
    }
    disp, _ = analyze(unclassified_incident)
    assert disp["category"] == "OPERATIONAL_RISK"
    assert disp["suggestedAction"] in ("SERVICE", "RECALL", "INSPECT", "HOLD", "PROCEED")
    # Low severity + high confidence + no safety zone → not HITL
    assert disp["hitlRequired"] is False


def test_critical_severity_in_safety_zone_maxes_risk():
    """Critical severity + low detectorConfidence + near-road: risk clamped to 1.0, must HITL."""
    critical_incident = {
        "incidentId": "IR-TEST-CRITICAL",
        "source": {"type": "vision", "detectorConfidence": 0.60},
        "severity": "critical",
        "subject": "Blade jam near road with debris strike",
        "description": "blade jammed after striking debris near a public road",
        "safetyZone": "near-road",
    }
    disp, _ = analyze(critical_incident)
    assert disp["riskScore"] == 1.0, f"Expected riskScore=1.0 (clamped), got {disp['riskScore']}"
    assert disp["hitlRequired"] is True
    assert disp["category"] == "BLADE_FAULT"


if __name__ == "__main__":
    test_high_risk_routes_to_hitl()
    test_low_risk_is_fast_tracked()
    test_gateway_is_authoritative_over_model_output()
    test_pipeline_end_to_end_and_audit_trail()
    test_low_confidence_triggers_hitl()
    test_missing_fields_do_not_crash()
    test_non_regulated_class_defaults_to_operational_risk()
    test_critical_severity_in_safety_zone_maxes_risk()
    print("all tests passed")
