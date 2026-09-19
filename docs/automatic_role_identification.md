# Automatic task-role identification

The project now includes a temporal heuristic baseline for assigning tracked entities to three task roles: **gripper**, **manipulated object**, and **target**.

The manipulated object is scored using motion plus sustained proximity to the gripper. The target is scored using relative stationarity plus proximity to the manipulated object's final position. Scores and evidence are returned for auditing.

## Gripper limitation

A generic COCO-pretrained YOLO model normally does not provide a dedicated robot-gripper/end-effector class. Therefore the system does not silently guess that an arbitrary object is the gripper. It accepts a gripper track hint or can consume detections from a future robot-specific detector/keypoint model. This is intentional: calling the current pipeline fully automatic without a reliable gripper observation would be misleading.

## Next improvement

Use DROID robot/camera calibration or a robot-specific end-effector detector to project/locate the gripper in the image. That removes the remaining gripper hint and enables a genuinely automatic end-to-end episode evaluator.
