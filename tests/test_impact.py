"""Impact Analysis node tests — economic + organizational impact -> routing.

    python -m pytest tests/ -q
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.analyst_agent import analyze
from agents.impact_agent import assess


# High-impact: a mower stalled on a steep slope beside a road — safety-critical,
# costly (unit + road liability), should escalate to a human review board.
SLOPE = {
    "incidentId": "IR-TEST-SLOPE",
    "source": {"type": "vision", "name": "onboard-cam", "detectorConfidence": 0.93},
    "severity": "high",
    "subject": "Mower stalled and tilting on steep slope next to the road",
    "description": "drivetrain stalled mid-slope; unit tilting toward the road shoulder.",
    "affectedItems": [{"itemId": "MOW-NX3-07", "itemType": "unit", "quantity": 1}],
    "safetyZone": "near-road",
    "tags": ["mobility", "slope", "near-road"],
}

# Low-impact: a shallow cosmetic scuff on the housing — auto-resolve, no human.
COSMETIC = {
    "incidentId": "IR-TEST-COSMETIC",
    "source": {"type": "vision", "name": "onboard-cam", "detectorConfidence": 0.96},
    "severity": "low",
    "subject": "Shallow cosmetic scuff on the top housing",
    "description": "Shallow cosmetic scuff on the plastic top housing. Surface finish only.",
    "affectedItems": [{"itemId": "HSG-1", "itemType": "part", "quantity": 1}],
    "safetyZone": "none",
    "tags": ["cosmetic", "scuff"],
}


def test_high_impact_slope_escalates_to_action_center():
    disp, _ = analyze(SLOPE)
    imp = assess(SLOPE, disp)
    assert imp["route"] == "ACTION_CENTER"
    assert imp["hitlRequired"] is True
    assert imp["safetyCritical"] is True
    assert imp["economicImpactScore"] >= 0.40
    assert "Safety Officer" in imp["rolesEngaged"]


def test_low_impact_cosmetic_is_auto_resolved():
    disp, _ = analyze(COSMETIC)
    imp = assess(COSMETIC, disp)
    assert imp["route"] == "AUTONOMOUS"
    assert imp["hitlRequired"] is False
    assert imp["safetyCritical"] is False


def test_economic_score_is_bounded_and_breaks_down():
    disp, _ = analyze(SLOPE)
    imp = assess(SLOPE, disp)
    assert 0.0 <= imp["economicImpactScore"] <= 1.0
    b = imp["costBreakdownUsd"]
    assert round(b["repair"] + b["downtime"] + b["inactionRisk"], 2) == imp["estimatedCostUsd"]


def test_word_boundary_does_not_false_trip_safety_cue():
    # Word-boundary matching: "watering" must NOT be read as the "water" safety cue.
    inc = dict(COSMETIC, subject="note near the watering schedule sticker",
               description="reminder about the watering schedule, no fault")
    disp, _ = analyze(inc)
    imp = assess(inc, disp)
    assert imp["safetyCritical"] is False


if __name__ == "__main__":
    test_high_impact_slope_escalates_to_action_center()
    test_low_impact_cosmetic_is_auto_resolved()
    test_economic_score_is_bounded_and_breaks_down()
    test_word_boundary_does_not_false_trip_safety_cue()
    print("all impact tests passed")
