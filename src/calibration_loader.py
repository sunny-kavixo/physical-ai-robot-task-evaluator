"""Validated calibration container and JSON loader.

This intentionally uses a project-owned schema rather than guessing DROID
metadata keys or transform direction.
"""
import json
from pathlib import Path
import numpy as np
from src.camera_projection import PinholeCamera


def load_camera_calibration(path: str | Path) -> PinholeCamera:
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("transform_convention") != "camera_from_robot":
        raise ValueError("transform_convention must be 'camera_from_robot'")
    return PinholeCamera(
        intrinsic=np.asarray(data["intrinsic"],dtype=float),
        camera_from_robot=np.asarray(data["camera_from_robot"],dtype=float),
    )
