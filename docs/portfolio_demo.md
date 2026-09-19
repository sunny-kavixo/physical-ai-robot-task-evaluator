# Portfolio Demo Guide

## One-minute explanation

This project evaluates a real robot manipulation episode as six ordered stages:
**Approach, Grasp, Lift, Transport, Place, Release**.

The input is a real DROID RLDS episode containing robot telemetry and synchronized RGB observations. For the validated Episode 0 task, **Put the marker in the pot**, the telemetry pipeline automatically detects the gripper transition, lift, transport displacement, and release transition. Approach and Place require trustworthy object-relative vision, so the automatic evaluator leaves them UNKNOWN instead of guessing.

## Step-by-step demo

### Step 1 — Show the real images

Open the repository README and point to the four Episode 0 frames: before pickup, grasp/lift, place/release, and after release. Explain that they are real DROID observations.

### Step 2 — Show the input

The DROID adapter reads:
- language instruction;
- gripper position;
- Cartesian end-effector pose;
- wrist RGB image;
- two exterior RGB images.

The large dataset itself is intentionally not committed to Git.

### Step 3 — Run the tests

```bash
python -m pytest -v
```

Do not claim a passing test count until this command has been run on the final repository revision.

### Step 4 — Run the evaluator

```bash
python evaluate_droid_automatic.py /path/to/droid_100/1.0.0 --episode 0
```

For the validated Episode 0 run, the measured telemetry events were:
- pickup low point: frame 62;
- grasp transition: frame 66;
- lift threshold: frame 80;
- release transition: frame 139;
- lift rise: approximately 0.057 m;
- grasp-to-release end-effector displacement: approximately 0.175 m.

### Step 5 — Explain the result correctly

Automatic mode establishes Grasp, Lift, Transport, and Release. Approach and Place are UNKNOWN, so the automatic six-stage status is INCOMPLETE.

Targeted human inspection of the real visual evidence supports all six stages for Episode 0, giving a separate human-validated result of SUCCESS.

### Step 6 — Open the report

The evaluator writes JSON and HTML reports. The HTML report uses three evidence states:
**PASS**, **FAIL**, and **UNKNOWN**.

## What to say about the visual experiments

A generic YOLO detector was tested, but its labels were not trustworthy for robot-specific identities such as the marker and gripper. Temporal role reasoning also produced ambiguous pot-region tracks. Wrist-frame differencing detected large motion, but the simple translation compensation was not reliable enough to isolate the manipulated object.

These are documented experiments, not hidden failures. They justify the project's evidence rule: when the perception signal is not trustworthy, report UNKNOWN.

## Optional video

A short screen recording can make the portfolio easier to scan, but it is not required for the repository to be understandable. A useful 30–45 second video would show:

1. the four real Episode 0 images in the README;
2. the automatic evaluator command;
3. the terminal result;
4. the generated HTML report;
5. a final caption: **Automatic telemetry: 4/6 established; human-validated Episode 0: 6/6 SUCCESS.**

Keep large MP4 files outside the Git repository or host the demo video externally; the source repository intentionally ignores video files.
