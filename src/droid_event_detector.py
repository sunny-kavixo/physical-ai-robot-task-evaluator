"""Automatic telemetry event detection for DROID manipulation episodes.

This module converts real robot proprioception into reproducible grasp, lift,
transport, and release evidence. It intentionally does not claim that
approach/place are proven from telemetry alone; those stages require
object-relative visual evidence.
"""
from dataclasses import dataclass
from math import dist
from typing import Sequence

from src.droid_adapter import DroidStep


@dataclass(frozen=True)
class DroidTelemetryEvents:
    grasp_frame: int | None
    pickup_low_frame: int | None
    lift_frame: int | None
    release_frame: int | None
    pickup_z: float | None
    lift_rise_m: float | None
    transport_distance_m: float | None


def detect_telemetry_events(
    steps: Sequence[DroidStep],
    *,
    gripper_threshold: float = 0.5,
    lift_threshold_m: float = 0.05,
    pickup_search_before: int = 15,
    pickup_search_after: int = 10,
) -> DroidTelemetryEvents:
    """Detect ordered manipulation events without hard-coded episode frames."""
    if not steps:
        return DroidTelemetryEvents(None, None, None, None, None, None, None)

    gripper = [float(s.gripper_position) for s in steps]
    grasp_frame = None
    release_frame = None
    state_high = gripper[0] >= gripper_threshold

    for i in range(1, len(steps)):
        new_high = gripper[i] >= gripper_threshold
        if new_high != state_high:
            if new_high and grasp_frame is None:
                grasp_frame = i
            elif not new_high and grasp_frame is not None:
                release_frame = i
                break
            state_high = new_high

    if grasp_frame is None:
        return DroidTelemetryEvents(None, None, None, release_frame, None, None, None)

    start = max(0, grasp_frame - pickup_search_before)
    end = min(len(steps), grasp_frame + pickup_search_after)
    pickup_low_frame = min(
        range(start, end),
        key=lambda i: steps[i].cartesian_position[2],
    )
    pickup_z = float(steps[pickup_low_frame].cartesian_position[2])

    lift_limit = release_frame if release_frame is not None else len(steps)
    lift_frame = None
    for i in range(grasp_frame, lift_limit):
        if float(steps[i].cartesian_position[2]) - pickup_z >= lift_threshold_m:
            lift_frame = i
            break

    lift_rise = (
        float(steps[lift_frame].cartesian_position[2]) - pickup_z
        if lift_frame is not None else None
    )

    transport_distance = None
    if release_frame is not None:
        transport_distance = dist(
            steps[grasp_frame].cartesian_position[:3],
            steps[release_frame].cartesian_position[:3],
        )

    return DroidTelemetryEvents(
        grasp_frame=grasp_frame,
        pickup_low_frame=pickup_low_frame,
        lift_frame=lift_frame,
        release_frame=release_frame,
        pickup_z=pickup_z,
        lift_rise_m=lift_rise,
        transport_distance_m=transport_distance,
    )
