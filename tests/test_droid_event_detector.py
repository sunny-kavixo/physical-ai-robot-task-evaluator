from src.droid_adapter import DroidStep
from src.droid_event_detector import detect_telemetry_events


def step(i, z, grip, x=0.0, y=0.0):
    return DroidStep(i, (x, y, z, 0.0, 0.0, 0.0), grip)


def test_detects_ordered_telemetry_events():
    steps = [
        step(0, .20, 0.0),
        step(1, .10, 0.2),
        step(2, .10, 0.6),
        step(3, .13, 0.8, .03),
        step(4, .16, 0.8, .08),
        step(5, .16, 0.4, .12),
    ]
    e = detect_telemetry_events(
        steps,
        lift_threshold_m=.05,
        pickup_search_before=2,
        pickup_search_after=1,
    )
    assert e.grasp_frame == 2
    assert e.pickup_low_frame == 1
    assert e.lift_frame == 4
    assert e.release_frame == 5
    assert round(e.lift_rise_m, 2) == .06
    assert e.transport_distance_m is not None


def test_empty_episode_is_unknown():
    e = detect_telemetry_events([])
    assert e.grasp_frame is None
    assert e.lift_frame is None
    assert e.release_frame is None
