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
    "source": {"type": "telemetry", "detectorConfidence": 0.94},
    "severity": "high",
    "subject": "Reward curve diverging on walk-gait run, loss spiking at step 41k",
    "description": "training run unstable; reward crashed and loss diverging on the H100 instance",
    "safetyZone": "long-running",
}

LOW_RISK = {
    "incidentId": "IR-TEST-LOW",
    "source": {"type": "manual", "detectorConfidence": 0.99},
    "severity": "low",
    "subject": "Routine training note",
    "description": "minor logging verbosity note, no impact on the run",
    "safetyZone": "none",
}


def test_high_risk_routes_to_hitl():
    disp, _ = analyze(HIGH_RISK)
    assert disp["category"] == "LOSS_DIVERGENCE"
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

    # Every processed event leaves an immutable audit trail.
    audit = store.read_audit()

    assert any(e["stage"] == "INTAKE" for e in audit)
    assert any(e["stage"] == "ANALYSIS" for e in audit)
    assert any(e["stage"] == "GATEWAY" for e in audit)
    assert any(e["stage"] == "ACTION" for e in audit)


# -- EDGE-CASE TESTS (Issue #3) ---------------------------------------------

def test_low_confidence_triggers_hitl():
    """Detector confidence < 0.8 adds +0.15 risk AND offline confidence=0.65 (<0.70),
    so hitlRequired must be True even for a low-severity anomaly."""
    low_conf_incident = {
        "incidentId": "IR-TEST-LOWCONF",
        "source": {"type": "monitor", "detectorConfidence": 0.55},
        "severity": "low",
        "subject": "Routine check with an unreliable monitor reading",
        "description": "monitor confidence below acceptable threshold during the run",
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
    """An event with only incidentId must produce a schema-valid output without raising."""
    minimal_incident = {"incidentId": "IR-TEST-MINIMAL"}
    disp, _provider = analyze(minimal_incident)

    for key in ("category", "riskScore", "confidence", "hitlRequired", "suggestedAction"):
        assert key in disp, f"Missing required key: {key}"
    assert isinstance(disp["hitlRequired"], bool)
    assert 0.0 <= disp["riskScore"] <= 1.0
    assert 0.0 <= disp["confidence"] <= 1.0
    assert disp["category"] in ("GRADIENT_COLLAPSE", "LOSS_DIVERGENCE", "HARDWARE_FAULT", "RESOURCE_RISK")
    assert disp["suggestedAction"] in ("RESTART", "TERMINATE", "INSPECT", "HOLD", "PROCEED")


def test_unmatched_class_defaults_to_resource_risk():
    """A description with no gradient/divergence/hardware keywords falls into RESOURCE_RISK."""
    unclassified_incident = {
        "incidentId": "IR-TEST-UNCLASS",
        "source": {"type": "manual", "detectorConfidence": 0.95},
        "severity": "low",
        "subject": "Config version mismatch notification",
        "description": "trainer config v2.1 does not match the fleet baseline v2.3",
        "safetyZone": "none",
    }
    disp, _ = analyze(unclassified_incident)
    assert disp["category"] == "RESOURCE_RISK"
    assert disp["suggestedAction"] in ("RESTART", "TERMINATE", "INSPECT", "HOLD", "PROCEED")
    # Low severity + high confidence + no critical zone -> not HITL
    assert disp["hitlRequired"] is False


def test_critical_severity_in_critical_zone_maxes_risk():
    """Critical severity + low detectorConfidence + high-cost-gpu: risk clamped to 1.0, must HITL."""
    critical_incident = {
        "incidentId": "IR-TEST-CRITICAL",
        "source": {"type": "telemetry", "detectorConfidence": 0.60},
        "severity": "critical",
        "subject": "Gradient collapse with NaN loss on an H100",
        "description": "gradients vanished and NaN loss appeared on the high-cost GPU pool",
        "safetyZone": "high-cost-gpu",
    }
    disp, _ = analyze(critical_incident)
    assert disp["riskScore"] == 1.0, f"Expected riskScore=1.0 (clamped), got {disp['riskScore']}"
    assert disp["hitlRequired"] is True
    assert disp["category"] == "GRADIENT_COLLAPSE"


if __name__ == "__main__":
    test_high_risk_routes_to_hitl()
    test_low_risk_is_fast_tracked()
    test_gateway_is_authoritative_over_model_output()
    test_pipeline_end_to_end_and_audit_trail()
    test_low_confidence_triggers_hitl()
    test_missing_fields_do_not_crash()
    test_unmatched_class_defaults_to_resource_risk()
    test_critical_severity_in_critical_zone_maxes_risk()
    print("all tests passed")
