"""Calibration-free automatic DROID evaluator.

Uses robot telemetry for events that telemetry can support directly and keeps
object-relative stages UNKNOWN until trustworthy visual evidence is available.
This prevents a generic detector misclassification from becoming a fake task
success.
"""
from dataclasses import asdict

from src.droid_adapter import DroidStep
from src.droid_event_detector import detect_telemetry_events
from src.task_evaluator import RobotTaskEvaluator


def evaluate_telemetry_episode(
    instruction: str,
    steps: list[DroidStep],
    *,
    episode_index: int = 0,
    gripper_threshold: float = 0.5,
    lift_threshold_m: float = 0.05,
    transport_threshold_m: float = 0.10,
) -> dict:
    events = detect_telemetry_events(
        steps,
        gripper_threshold=gripper_threshold,
        lift_threshold_m=lift_threshold_m,
    )

    grasp = True if events.grasp_frame is not None else None
    lift = True if events.lift_frame is not None else None
    transport = (
        True
        if events.transport_distance_m is not None
        and events.transport_distance_m >= transport_threshold_m
        else None
    )
    release = (
        True
        if events.release_frame is not None
        and events.grasp_frame is not None
        and events.release_frame > events.grasp_frame
        else None
    )

    # Approach and place require object-relative evidence. Do not manufacture
    # them from end-effector motion alone.
    stage_map = {
        "approach": None,
        "grasp": grasp,
        "lift": lift,
        "transport": transport,
        "place": None,
        "release": release,
    }

    evaluation = RobotTaskEvaluator().evaluate(
        task_id=f"droid-{episode_index}",
        instruction=instruction or "DROID manipulation episode",
        stages=stage_map,
    )

    evidence = [
        {
            "stage": "approach",
            "achieved": None,
            "frame_index": None,
            "reason": "requires trustworthy object-relative visual evidence",
        },
        {
            "stage": "grasp",
            "achieved": grasp,
            "frame_index": events.grasp_frame,
            "reason": "automatic gripper LOW-to-HIGH transition",
        },
        {
            "stage": "lift",
            "achieved": lift,
            "frame_index": events.lift_frame,
            "reason": f"automatic end-effector rise >= {lift_threshold_m:.3f} m after grasp",
        },
        {
            "stage": "transport",
            "achieved": transport,
            "frame_index": events.release_frame if transport else None,
            "reason": f"grasp-to-release end-effector displacement >= {transport_threshold_m:.3f} m",
        },
        {
            "stage": "place",
            "achieved": None,
            "frame_index": None,
            "reason": "requires trustworthy object-to-target visual evidence",
        },
        {
            "stage": "release",
            "achieved": release,
            "frame_index": events.release_frame,
            "reason": "automatic gripper HIGH-to-LOW transition after grasp",
        },
    ]

    return {
        "instruction": instruction,
        "episode_index": episode_index,
        "mode": "automatic_telemetry",
        "fully_automatic": True,
        "stage_evidence": evidence,
        "telemetry_events": asdict(events),
        "evaluation": evaluation.to_dict(),
        "provenance": {
            "uses_human_visual_validation": False,
            "uses_camera_calibration": False,
            "limitations": (
                "Approach and place remain UNKNOWN without trustworthy "
                "object-relative visual evidence; telemetry alone cannot prove them."
            ),
        },
    }
