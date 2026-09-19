# Real DROID validation

This project has been exercised against the official 100-episode DROID RLDS debugging sample on macOS.

## Episode 0 validation

Instruction: `Put the marker in the pot`

Observed episode length: 166 steps.

The RLDS decoder successfully exposed robot Cartesian position, gripper position, wrist RGB, and two exterior RGB camera views. The validation run also exported real frames, built an episode video, ran the generic YOLO/tracking baseline, and inspected robot telemetry.

### Automatically recovered telemetry events

Using a 0.5 gripper-state threshold and a 0.05 m lift threshold:

- pickup low point: frame 62, z about 0.142 m
- gripper HIGH transition / grasp candidate: frame 66, value 0.559
- lift threshold reached: frame 80, z about 0.199 m
- measured lift rise at threshold: about 0.057 m
- gripper LOW transition / release candidate: frame 139, value 0.432
- end-effector displacement from grasp to release: about 0.175 m

These events are now represented by `src/droid_event_detector.py`; the detector does not hard-code Episode 0 frame numbers.

### Vision finding

The generic COCO YOLO baseline was not reliable for the marker or robot gripper. A long-lived detection around the pot area was observed, but semantic class labels such as bowl/person/cup were not trusted as robot-task roles.

Therefore the repository does **not** claim that all six stages are automatically proven from raw video yet.

### Human-validated Episode 0 result

Manual inspection of targeted wrist-camera frames together with the robot telemetry supported the six-stage sequence:

`approach -> grasp -> lift -> transport -> place -> release`

The resulting Episode 0 validation was SUCCESS (6/6), but its validation mode is explicitly:

`real DROID + robot telemetry + human visual evidence`

It is **not** reported as a fully automatic benchmark result.

## Remaining validation work

1. Connect automatic telemetry events to the main evaluator.
2. Improve object/gripper role localization without trusting generic COCO labels.
3. Automatically establish approach and place from object-relative evidence.
4. Evaluate multiple episodes, including incomplete/failure cases.
5. Run the full test suite and report only measured results.
