from src.object_tracking import Track
from src.vision_geometry import GeometryEstimator


def tr(i,x,y):
    return Track(i,1,"object",0.9,(x,y,x+10,y+10))


def test_geometry_uses_normalized_image_plane_proxies():
    est=GeometryEstimator(object_track_id=1,target_track_id=2,gripper_track_id=3)
    first=est.estimate([tr(1,100,100),tr(2,300,100),tr(3,90,100)],400,300)
    second=est.estimate([tr(1,150,50),tr(2,300,100),tr(3,140,50)],400,300)
    assert first.object_displacement == 0.0
    assert second.object_displacement > 0
    assert second.object_height > 0
    assert second.gripper_object_distance is not None
    assert second.object_target_distance is not None


def test_missing_object_returns_unknown_geometry():
    g=GeometryEstimator(object_track_id=99).estimate([tr(1,0,0)],100,100)
    assert g.object_displacement is None
    assert g.object_target_distance is None
