from src.object_tracking import CentroidTracker, Detection


def det(x, name="cup", class_id=1):
    return Detection(class_id, name, 0.9, (x, 0, x + 10, 10))


def test_tracker_preserves_id_for_nearby_same_class():
    tracker = CentroidTracker(max_distance=30)
    first = tracker.update([det(0)])[0]
    second = tracker.update([det(5)])[0]
    assert first.track_id == second.track_id


def test_tracker_creates_new_id_for_distant_detection():
    tracker = CentroidTracker(max_distance=20)
    first_id = tracker.update([det(0)])[0].track_id
    visible = tracker.update([det(100)])
    assert any(t.track_id != first_id and t.missed_frames == 0 for t in visible)


def test_tracker_does_not_match_different_classes():
    tracker = CentroidTracker(max_distance=100)
    first_id = tracker.update([det(0, "cup", 1)])[0].track_id
    tracks = tracker.update([det(1, "bottle", 2)])
    new_tracks = [t for t in tracks if t.missed_frames == 0]
    assert len(new_tracks) == 1
    assert new_tracks[0].track_id != first_id
