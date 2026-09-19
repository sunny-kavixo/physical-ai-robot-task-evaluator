from src.object_tracking import Track
from src.role_identifier import TrackRoleIdentifier


def tr(i,name,x,y):
    return Track(i,i,name,0.9,(x,y,x+10,y+10))


def test_identifies_roles_with_gripper_hint():
    history=[]
    # gripper 1 and object 2 travel together; target 3 stays near final object.
    for k in range(5):
        history.append([tr(1,"end_effector",k*20,0),tr(2,"cup",k*20+8,4),tr(3,"bowl",90,5),tr(4,"book",300,200)])
    r=TrackRoleIdentifier().identify(history,gripper_hint=1)
    assert r.gripper_track_id==1
    assert r.object_track_id==2
    assert r.target_track_id==3


def test_returns_low_confidence_without_robot_semantic_track():
    history=[[tr(2,"cup",x,0),tr(3,"bowl",100,0)] for x in (0,10,20,30)]
    r=TrackRoleIdentifier().identify(history)
    assert r.gripper_track_id is None
    assert r.confidence < 1.0
