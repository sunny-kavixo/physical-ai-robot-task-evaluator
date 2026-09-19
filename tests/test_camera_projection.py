import numpy as np
from src.camera_projection import PinholeCamera, project_robot_point
from src.gripper_localization import find_gripper_track
from src.object_tracking import Track


def test_projection_hits_image_center():
    cam=PinholeCamera(np.array([[100.,0,50],[0,100.,50],[0,0,1]]),np.eye(4))
    p=project_robot_point((0,0,1),cam,100,100)
    assert p.visible
    assert p.u==50 and p.v==50


def test_point_behind_camera_is_invisible():
    cam=PinholeCamera(np.eye(3),np.eye(4))
    assert not project_robot_point((0,0,-1),cam,100,100).visible


def test_projection_selects_nearest_track():
    p=type("P",(),{"visible":True,"u":50.0,"v":50.0})()
    tracks=[Track(1,0,"x",.9,(40,40,50,50)),Track(2,0,"x",.9,(48,48,58,58))]
    assert find_gripper_track(p,tracks,80)==2
