from src.action_stage_detector import ActionObservation, ActionStageDetector


def successful_sequence():
    return [
        ActionObservation(0, gripper_object_distance=0.30, gripper_closed=False, object_height=0.0, object_displacement=0.0, object_target_distance=0.5),
        ActionObservation(10, gripper_object_distance=0.05, gripper_closed=False, object_height=0.0, object_displacement=0.0, object_target_distance=0.5),
        ActionObservation(20, gripper_object_distance=0.03, gripper_closed=True, object_height=0.0, object_displacement=0.0, object_target_distance=0.5),
        ActionObservation(30, gripper_object_distance=0.03, gripper_closed=True, object_height=0.08, object_displacement=0.02, object_target_distance=0.4),
        ActionObservation(40, gripper_object_distance=0.03, gripper_closed=True, object_height=0.08, object_displacement=0.20, object_target_distance=0.2),
        ActionObservation(50, gripper_object_distance=0.03, gripper_closed=True, object_height=0.02, object_displacement=0.25, object_target_distance=0.04),
        ActionObservation(60, gripper_object_distance=0.10, gripper_closed=False, object_height=0.02, object_displacement=0.25, object_target_distance=0.04),
    ]


def test_detects_ordered_successful_stages():
    evidence=ActionStageDetector().detect(successful_sequence())
    assert [e.stage for e in evidence if e.achieved] == ["approach","grasp","lift","transport","place","release"]
    assert [e.frame_index for e in evidence] == [10,20,30,40,50,60]


def test_no_grasp_blocks_later_stages():
    obs=successful_sequence()
    obs=[ActionObservation(o.frame_index,o.gripper_object_distance,False,o.object_height,o.object_displacement,o.object_target_distance) for o in obs]
    result=ActionStageDetector().as_stage_map(obs)
    assert result["approach"] is True
    assert result["grasp"] is False
    assert result["lift"] is False
    assert result["release"] is False


def test_empty_observations_fail_all_stages():
    result=ActionStageDetector().detect([])
    assert all(not e.achieved for e in result)
