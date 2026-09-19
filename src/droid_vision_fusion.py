"""Fuse DROID proprioception with optional vision-derived object geometry."""
from dataclasses import dataclass
from typing import Mapping

from src.action_stage_detector import ActionObservation
from src.droid_adapter import DroidStep


@dataclass(frozen=True)
class VisionGeometry:
    gripper_object_distance: float | None = None
    object_height: float | None = None
    object_displacement: float | None = None
    object_target_distance: float | None = None


def fuse_step(step: DroidStep, vision: VisionGeometry | None, closed_threshold: float = 0.65) -> ActionObservation:
    vision = vision or VisionGeometry()
    return ActionObservation(
        frame_index=step.frame_index,
        gripper_object_distance=vision.gripper_object_distance,
        gripper_closed=step.gripper_position >= closed_threshold,
        object_height=vision.object_height,
        object_displacement=vision.object_displacement,
        object_target_distance=vision.object_target_distance,
    )


def fuse_episode(steps: list[DroidStep], geometry_by_frame: Mapping[int, VisionGeometry]) -> list[ActionObservation]:
    return [fuse_step(step, geometry_by_frame.get(step.frame_index)) for step in steps]
