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


if __name__ == "__main__":
    test_high_risk_routes_to_hitl()
    test_low_risk_is_fast_tracked()
    test_gateway_is_authoritative_over_model_output()
    test_pipeline_end_to_end_and_audit_trail()
    print("all tests passed")
