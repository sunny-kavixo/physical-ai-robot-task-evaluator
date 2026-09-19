from src.droid_adapter import DroidStep, decode_rlds_step, proprioceptive_observations
from src.droid_vision_fusion import VisionGeometry, fuse_step


def test_decode_droid_schema():
    step={"observation":{"cartesian_position":[0,1,2,0,0,0],"gripper_position":[0.8],"wrist_image_left":"w","exterior_image_1_left":"e1","exterior_image_2_left":"e2"}}
    decoded=decode_rlds_step(4,step)
    assert decoded.frame_index==4
    assert decoded.cartesian_position[:3]==(0.0,1.0,2.0)
    assert decoded.gripper_position==0.8


def test_proprioception_does_not_invent_object_geometry():
    steps=[DroidStep(0,(0,0,0,0,0,0),0.1),DroidStep(1,(0.2,0,0,0,0,0),0.9)]
    obs=proprioceptive_observations(steps)
    assert obs[1].gripper_closed is True
    assert obs[1].object_displacement==0.2
    assert obs[1].object_height is None
    assert obs[1].object_target_distance is None


def test_vision_fusion_populates_object_evidence():
    step=DroidStep(7,(0,0,0,0,0,0),0.9)
    obs=fuse_step(step,VisionGeometry(0.03,0.08,0.2,0.04))
    assert obs.gripper_closed is True
    assert obs.gripper_object_distance==0.03
    assert obs.object_target_distance==0.04
