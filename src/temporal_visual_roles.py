"""Temporal visual role understanding for robot manipulation.

This module avoids trusting generic detector class names. It uses task timing
from robot telemetry plus track motion/proximity to score manipulated-object
and target candidates. A gripper track is optional because DROID RLDS does not
include camera calibration in its step schema.
"""
from dataclasses import dataclass
from collections import defaultdict
import math

from src.object_tracking import Track


@dataclass(frozen=True)
class VisualRoleEvidence:
    object_track_id: int | None
    target_track_id: int | None
    gripper_track_id: int | None
    object_confidence: float
    target_confidence: float
    evidence: dict


def _path_length(seq):
    return sum(math.dist(seq[i - 1][1], seq[i][1]) for i in range(1, len(seq)))


def _center_at_or_near(seq, frame):
    return min(seq, key=lambda item: abs(item[0] - frame))[1] if seq else None


class TemporalRoleReasoner:
    """Infer task roles from temporal behavior rather than COCO semantics."""

    def __init__(self, min_observations: int = 3):
        self.min_observations = min_observations

    def identify(
        self,
        history: list[list[Track]],
        *,
        grasp_frame: int | None,
        release_frame: int | None,
        gripper_track_id: int | None = None,
    ) -> VisualRoleEvidence:
        positions = defaultdict(list)
        classes = {}
        for frame_index, tracks in enumerate(history):
            for track in tracks:
                if track.missed_frames == 0:
                    positions[track.track_id].append((frame_index, track.center))
                    classes[track.track_id] = track.class_name

        eligible = {
            tid: seq for tid, seq in positions.items()
            if len(seq) >= self.min_observations
        }
        if not eligible:
            return VisualRoleEvidence(None, None, gripper_track_id, 0.0, 0.0,
                                      {"reason": "insufficient visual track history"})

        motions = {tid: _path_length(seq) for tid, seq in eligible.items()}
        object_scores = {}

        # A manipulated object should be visible around the manipulation window
        # and exhibit motion while the robot is holding something.
        if grasp_frame is not None and release_frame is not None:
            for tid, seq in eligible.items():
                if tid == gripper_track_id:
                    continue
                during = [(f, p) for f, p in seq if grasp_frame <= f <= release_frame]
                if len(during) < self.min_observations:
                    continue
                span = math.dist(during[0][1], during[-1][1])
                coverage = len(during) / max(1, release_frame - grasp_frame + 1)
                object_scores[tid] = span * (1.0 + coverage)

        object_id = max(object_scores, key=object_scores.get, default=None)

        # Target should be comparatively stationary and close to the object's
        # position around release. This is image-plane evidence only.
        target_scores = {}
        if object_id is not None and release_frame is not None:
            object_release = _center_at_or_near(eligible[object_id], release_frame)
            for tid, seq in eligible.items():
                if tid in (object_id, gripper_track_id):
                    continue
                target_release = _center_at_or_near(seq, release_frame)
                proximity = math.dist(object_release, target_release)
                target_scores[tid] = proximity + motions[tid]

        target_id = min(target_scores, key=target_scores.get, default=None)

        def confidence(scores, selected, higher=True):
            if selected is None or not scores:
                return 0.0
            vals = sorted(scores.values(), reverse=higher)
            if len(vals) == 1:
                return 0.5
            best = scores[selected]
            second = vals[1]
            denom = max(abs(best), abs(second), 1e-6)
            margin = (best - second) / denom if higher else (second - best) / denom
            return max(0.0, min(1.0, 0.5 + 0.5 * margin))

        return VisualRoleEvidence(
            object_track_id=object_id,
            target_track_id=target_id,
            gripper_track_id=gripper_track_id,
            object_confidence=confidence(object_scores, object_id, True),
            target_confidence=confidence(target_scores, target_id, False),
            evidence={
                "method": "telemetry-conditioned temporal visual reasoning",
                "detector_classes_are_not_treated_as_task_semantics": True,
                "classes": classes,
                "motion_pixels": motions,
                "object_scores": object_scores,
                "target_scores": target_scores,
            },
        )
