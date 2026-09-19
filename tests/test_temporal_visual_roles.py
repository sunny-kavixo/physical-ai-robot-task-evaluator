from src.object_tracking import Track
from src.temporal_visual_roles import TemporalRoleReasoner


def t(track_id, x, y, name="unknown"):
    return Track(track_id, track_id, name, .8, (x-1, y-1, x+1, y+1))


def test_temporal_reasoner_prefers_moving_object_and_stationary_target():
    history = []
    for f in range(10):
        tracks = [
            t(1, 10 + 4*f, 20),      # manipulated object moves while held
            t(2, 48, 20),            # stationary target near final object
            t(3, 100, 100),          # irrelevant stationary detection
        ]
        history.append(tracks)

    roles = TemporalRoleReasoner().identify(
        history, grasp_frame=2, release_frame=9
    )
    assert roles.object_track_id == 1
    assert roles.target_track_id == 2
    assert roles.object_confidence > 0
    assert roles.target_confidence > 0
