from src.automatic_droid_evaluator import evaluate_telemetry_episode
from src.droid_adapter import DroidStep


def s(i, x, z, grip):
    return DroidStep(i, (x, 0.0, z, 0.0, 0.0, 0.0), grip)


def test_automatic_telemetry_keeps_visual_stages_unknown():
    steps = [
        s(0, 0.00, .20, 0.0),
        s(1, 0.00, .10, 0.0),
        s(2, 0.00, .10, 0.6),
        s(3, 0.04, .13, 0.8),
        s(4, 0.12, .16, 0.8),
        s(5, 0.15, .16, 0.4),
    ]
    payload = evaluate_telemetry_episode("pick and place", steps)
    stages = payload["evaluation"]["stage_results"]
    assert stages["approach"] is None
    assert stages["grasp"] is True
    assert stages["lift"] is True
    assert stages["transport"] is True
    assert stages["place"] is None
    assert stages["release"] is True
    assert payload["evaluation"]["status"] == "INCOMPLETE"
    assert payload["fully_automatic"] is True
