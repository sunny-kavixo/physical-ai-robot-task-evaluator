"""Temporal action-stage inference from explicit robot/object observations.

This is a transparent heuristic baseline. It does not claim learned action
recognition. Later DROID state adapters can populate the same observation API.
"""
from dataclasses import dataclass
from typing import Iterable

STAGES = ("approach", "grasp", "lift", "transport", "place", "release")


@dataclass(frozen=True)
class ActionObservation:
    frame_index: int
    gripper_object_distance: float | None = None
    gripper_closed: bool | None = None
    object_height: float | None = None
    object_displacement: float | None = None
    object_target_distance: float | None = None


@dataclass(frozen=True)
class StageEvidence:
    stage: str
    achieved: bool
    frame_index: int | None
    reason: str


class ActionStageDetector:
    def __init__(
        self,
        approach_distance: float = 0.10,
        lift_height: float = 0.05,
        transport_distance: float = 0.10,
        target_distance: float = 0.08,
    ):
        self.approach_distance = approach_distance
        self.lift_height = lift_height
        self.transport_distance = transport_distance
        self.target_distance = target_distance

    @staticmethod
    def _first(observations, predicate):
        return next((o for o in observations if predicate(o)), None)

    def detect(self, observations: Iterable[ActionObservation]) -> list[StageEvidence]:
        obs = sorted(observations, key=lambda o: o.frame_index)
        if not obs:
            return [StageEvidence(s, False, None, "no observations") for s in STAGES]

        approach = self._first(obs, lambda o: o.gripper_object_distance is not None and o.gripper_object_distance <= self.approach_distance)
        grasp = self._first(obs, lambda o: approach is not None and o.frame_index >= approach.frame_index and o.gripper_closed is True and o.gripper_object_distance is not None and o.gripper_object_distance <= self.approach_distance)
        lift = self._first(obs, lambda o: grasp is not None and o.frame_index >= grasp.frame_index and o.object_height is not None and o.object_height >= self.lift_height)
        transport = self._first(obs, lambda o: lift is not None and o.frame_index >= lift.frame_index and o.object_displacement is not None and o.object_displacement >= self.transport_distance)
        place = self._first(obs, lambda o: transport is not None and o.frame_index >= transport.frame_index and o.object_target_distance is not None and o.object_target_distance <= self.target_distance)
        release = self._first(obs, lambda o: place is not None and o.frame_index >= place.frame_index and o.gripper_closed is False)

        found = {
            "approach": (approach, "gripper entered object proximity threshold"),
            "grasp": (grasp, "gripper closed near object"),
            "lift": (lift, "object exceeded lift-height threshold"),
            "transport": (transport, "object exceeded displacement threshold"),
            "place": (place, "object entered target threshold"),
            "release": (release, "gripper opened after placement"),
        }
        return [
            StageEvidence(stage, event is not None, event.frame_index if event else None, reason if event else f"{stage} evidence not observed")
            for stage, (event, reason) in found.items()
        ]

    def as_stage_map(self, observations: Iterable[ActionObservation]) -> dict[str, bool]:
        return {e.stage: e.achieved for e in self.detect(observations)}
