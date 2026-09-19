# End-effector projection

This layer removes a manual gripper-track hint **when valid camera calibration is available**.

1. Read the robot end-effector Cartesian XYZ in robot/base coordinates.
2. Transform XYZ with a validated `camera_from_robot` 4x4 extrinsic matrix.
3. Project the camera-space point with the 3x3 pinhole intrinsic matrix.
4. Match the projected pixel to the nearest eligible visual track.
5. Feed that track ID to automatic task-role identification.

## Calibration safety

Camera calibration conventions are easy to reverse. The implementation therefore does not guess DROID metadata field names or whether a published transform is camera-to-base versus base-to-camera. The adapter accepts a small validated JSON schema with an explicit `transform_convention: camera_from_robot` field.

This prevents a plausible-looking but geometrically wrong projection from being presented as a working DROID result. A real DROID episode calibration adapter must be verified against the exact released dataset schema and a known frame before end-to-end benchmark claims are made.
