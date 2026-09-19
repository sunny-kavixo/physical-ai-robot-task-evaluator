# Real DROID validation

## Verified official sample

The official DROID documentation provides a **100-episode RLDS debugging sample (~2 GB)**:

```bash
gsutil -m cp -r gs://gresearch/robotics/droid_100 data/
```

The full RLDS release is about 1.7 TB, so this project targets `droid_100` for local validation.

## Verified RLDS fields used by this project

Each step documents:
- `language_instruction` (+ two alternatives)
- `observation/gripper_position` — shape 1
- `observation/cartesian_position` — shape 6
- `observation/joint_position` — shape 7
- `wrist_image_left`, `exterior_image_1_left`, `exterior_image_2_left` — RGB 180x320
- action/action_dict fields

Run `python inspect_droid_schema.py data/droid_100` after download to verify the local builder rather than assuming split names.

## Calibration finding

The official documented RLDS step schema does **not** expose camera intrinsics/extrinsics. DROID's raw release contains richer camera/calibration information, and the project homepage notes improved camera calibrations released for ~36k episodes in April 2025.

Therefore the evaluator must not pretend that the 2 GB RLDS sample alone contains everything needed for calibrated end-effector projection. Two valid validation modes are:

1. **RLDS-only:** run images + robot state, but keep calibrated gripper projection disabled/unknown.
2. **Calibration-backed:** match an episode to validated calibration metadata, verify transform convention, then enable end-effector projection.

## Acceptance rule

A real-data result is publishable in this repository only after:
- the episode loads from the actual released data;
- camera frames decode;
- role assignments are inspectable;
- stage evidence refers to real frame indices;
- calibration provenance is recorded when projection is enabled;
- failures/incomplete stages are preserved rather than edited into success.
