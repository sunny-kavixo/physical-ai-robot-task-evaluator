"""Project a robot end-effector point into a calibrated camera image.

Transforms are explicit 4x4 homogeneous matrices. No DROID calibration field
names are assumed here; the dataset adapter must map actual metadata into this
API after validating frame conventions.
"""
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class PinholeCamera:
    intrinsic: np.ndarray          # 3x3 K
    camera_from_robot: np.ndarray  # 4x4 transform: robot/base -> camera

    def __post_init__(self):
        if self.intrinsic.shape != (3,3):
            raise ValueError("intrinsic must be 3x3")
        if self.camera_from_robot.shape != (4,4):
            raise ValueError("camera_from_robot must be 4x4")


@dataclass(frozen=True)
class Projection:
    u: float
    v: float
    depth: float
    visible: bool


def project_robot_point(point_xyz, camera: PinholeCamera, width: int, height: int) -> Projection:
    p=np.asarray([*point_xyz,1.0],dtype=float)
    pc=camera.camera_from_robot @ p
    z=float(pc[2])
    if z <= 0:
        return Projection(float("nan"),float("nan"),z,False)
    uvw=camera.intrinsic @ pc[:3]
    u=float(uvw[0]/uvw[2]); v=float(uvw[1]/uvw[2])
    return Projection(u,v,z,0 <= u < width and 0 <= v < height)
