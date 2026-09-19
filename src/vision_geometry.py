"""Estimate normalized 2D object geometry from detector/tracker outputs.

This module intentionally reports image-plane proxies, not metric 3D geometry.
Distances are normalized by image diagonal so thresholds are resolution-robust.
"""
from dataclasses import dataclass
import math
from src.object_tracking import Track
from src.droid_vision_fusion import VisionGeometry


def _center(box):
    x1,y1,x2,y2=box
    return ((x1+x2)/2.0,(y1+y2)/2.0)


def _norm_distance(a,b,width,height):
    diagonal=math.hypot(width,height)
    if diagonal <= 0:
        raise ValueError("frame dimensions must be positive")
    return math.dist(a,b)/diagonal


@dataclass
class GeometryEstimator:
    object_track_id: int
    target_track_id: int | None = None
    gripper_track_id: int | None = None
    initial_object_center: tuple[float,float] | None = None

    def estimate(self, tracks: list[Track], width: int, height: int) -> VisionGeometry:
        by_id={t.track_id:t for t in tracks if t.missed_frames == 0}
        obj=by_id.get(self.object_track_id)
        if obj is None:
            return VisionGeometry()
        object_center=obj.center
        if self.initial_object_center is None:
            self.initial_object_center=object_center

        displacement=_norm_distance(object_center,self.initial_object_center,width,height)
        # Image y grows downward. Upward motion is a useful 2D lift proxy only.
        lift_proxy=max(0.0,(self.initial_object_center[1]-object_center[1])/height)

        gripper_distance=None
        if self.gripper_track_id in by_id:
            gripper_distance=_norm_distance(object_center,by_id[self.gripper_track_id].center,width,height)

        target_distance=None
        if self.target_track_id in by_id:
            target_distance=_norm_distance(object_center,by_id[self.target_track_id].center,width,height)

        return VisionGeometry(
            gripper_object_distance=gripper_distance,
            object_height=lift_proxy,
            object_displacement=displacement,
            object_target_distance=target_distance,
        )
