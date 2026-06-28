"""Cost & Impact Analysis node tests — economic + organizational impact -> routing.

    python -m pytest tests/ -q
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.analyst_agent import analyze
from agents.impact_agent import assess


# High-impact: a run diverging on an expensive instance, model bound for the
# physical robot — high-stakes, costly, should escalate to a human review board.
DIVERGE = {
    "incidentId": "IR-TEST-DIVERGE",
    "source": {"type": "telemetry", "name": "reward-monitor", "detectorConfidence": 0.93},
    "severity": "high",
    "subject": "Walk-gait run diverging on an H100; model is production-bound for the robot",
    "description": "reward crashed mid-training; loss diverging. run is production-bound for a hardware deploy.",
    "affectedItems": [{"itemId": "job-walk-gait-v2", "itemType": "job", "quantity": 1}],
    "safetyZone": "production-bound",
    "tags": ["divergence", "production-bound", "h100"],
}

# Low-impact: a slightly noisy reward curve within tolerance — auto-resolve, no human.
MINOR = {
    "incidentId": "IR-TEST-MINOR",
    "source": {"type": "telemetry", "name": "reward-monitor", "detectorConfidence": 0.96},
    "severity": "low",
    "subject": "Slightly noisy reward curve, within tolerance",
    "description": "minor reward variance within tolerance; the run is healthy and learning.",
    "affectedItems": [{"itemId": "job-1", "itemType": "job", "quantity": 1}],
    "safetyZone": "none",
    "tags": ["minor", "healthy"],
}


def test_high_impact_diverge_escalates_to_action_center():
    disp, _ = analyze(DIVERGE)
    imp = assess(DIVERGE, disp)
    assert imp["route"] == "ACTION_CENTER"
    assert imp["hitlRequired"] is True
    assert imp["safetyCritical"] is True
    assert imp["economicImpactScore"] >= 0.40
    assert "Robotics Safety Reviewer" in imp["rolesEngaged"]


def test_low_impact_minor_is_auto_resolved():
    disp, _ = analyze(MINOR)
    imp = assess(MINOR, disp)
    assert imp["route"] == "AUTONOMOUS"
    assert imp["hitlRequired"] is False
    assert imp["safetyCritical"] is False


def test_economic_score_is_bounded_and_breaks_down():
    disp, _ = analyze(DIVERGE)
    imp = assess(DIVERGE, disp)
    assert 0.0 <= imp["economicImpactScore"] <= 1.0
    b = imp["costBreakdownUsd"]
    assert round(b["repair"] + b["downtime"] + b["inactionRisk"], 2) == imp["estimatedCostUsd"]


def test_word_boundary_does_not_false_trip_safety_cue():
    # Word-boundary matching: "deployment" must NOT be read as the "deploy" cue.
    inc = dict(MINOR, subject="note about the deployment schedule sticker",
               description="reminder about the deployment schedule, the run is healthy")
    disp, _ = analyze(inc)
    imp = assess(inc, disp)
    assert imp["safetyCritical"] is False


if __name__ == "__main__":
    test_high_impact_diverge_escalates_to_action_center()
    test_low_impact_minor_is_auto_resolved()
    test_economic_score_is_bounded_and_breaks_down()
    test_word_boundary_does_not_false_trip_safety_cue()
    print("all impact tests passed")
