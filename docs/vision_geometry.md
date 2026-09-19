# Vision geometry bridge

The V1 vision bridge converts tracked 2D bounding boxes into normalized image-plane evidence for the action-stage detector.

## What is measured

- object displacement: center movement divided by image diagonal;
- lift proxy: upward image movement divided by image height;
- gripper/object proximity: center distance divided by image diagonal;
- object/target proximity: center distance divided by image diagonal.

## Important limitation

These are **2D visual proxies**, not metric metres and not true 3D pose. Perspective, camera motion and occlusion can change them. DROID has multiple camera views; a later milestone should use camera calibration/depth or learned keypoints/segmentation to obtain stronger 3D evidence.

The object, target and gripper track IDs must currently be selected/identified before geometry estimation. A general COCO-pretrained YOLO model may not contain a class for a robot gripper or task-specific object, so this module must not be presented as fully automatic robot understanding yet.
