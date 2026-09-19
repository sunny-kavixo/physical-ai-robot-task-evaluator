"""Associate projected end-effector pixels with visual tracks."""
import math
from src.object_tracking import Track
from src.camera_projection import Projection


def find_gripper_track(projection: Projection, tracks: list[Track], max_pixel_distance: float = 80.0) -> int | None:
    if not projection.visible:
        return None
    candidates=[]
    for t in tracks:
        if t.missed_frames != 0:
            continue
        d=math.dist((projection.u,projection.v),t.center)
        if d <= max_pixel_distance:
            candidates.append((d,t.track_id))
    return min(candidates)[1] if candidates else None
