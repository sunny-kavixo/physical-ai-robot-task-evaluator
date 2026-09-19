# Physical AI Robot Task Evaluator

**Real DROID robot-task evaluation prototype with automatic telemetry-stage detection and evidence-aware visual validation.**

> Validated demo task: **Put the marker in the pot** — DROID Episode 0, 166 robot steps.

## Real DROID evidence

<p align="center">
  <img src="docs/assets/episode0_before.jpg" width="24%" alt="DROID Episode 0 before pickup">
  <img src="docs/assets/episode0_grasp.jpg" width="24%" alt="DROID Episode 0 during grasp and lift">
  <img src="docs/assets/episode0_place.jpg" width="24%" alt="DROID Episode 0 near placement and release">
  <img src="docs/assets/episode0_after.jpg" width="24%" alt="DROID Episode 0 after release">
</p>

| Before | Grasp / lift | Place / release | After |
|---|---|---|---|
| Robot approaches the pickup area | Gripper closes and end effector rises | Robot reaches the pot area and release begins | Gripper withdraws |

These are **real frames from the locally validated DROID episode**, not generated illustrations.

## What the prototype evaluates

A manipulation task is represented as:

**Approach → Grasp → Lift → Transport → Place → Release**

The demo intentionally separates what is automatic from what was visually validated.

| Stage | Automatic telemetry path | Episode 0 human validation |
|---|---|---|
| Approach | UNKNOWN | PASS |
| Grasp | PASS candidate | PASS |
| Lift | PASS | PASS |
| Transport | PASS | PASS |
| Place | UNKNOWN | PASS |
| Release | PASS candidate | PASS |

The automatic evaluator therefore returns **INCOMPLETE (4/6 established)** for Episode 0. A separate targeted inspection of the real RGB evidence supports the full **human-validated 6/6 SUCCESS**. The project does not turn uncertain visual detections into automatic PASS results.

## Architecture

```text
DROID RLDS episode
       │
       ├───────────────┐
       ▼               ▼
Robot telemetry      RGB observations
gripper + EE pose    wrist + exterior
       │               │
       ▼               ▼
Telemetry events     Visual validation / experiments
       │               │
       ├─ Grasp         ├─ real evidence frames
       ├─ Lift          ├─ detector/tracker baseline
       ├─ Transport     └─ wrist temporal analysis
       └─ Release
       │
       └──────────┬──────────┘
                  ▼
          Six-stage evaluator
                  ▼
      SUCCESS / FAILURE / INCOMPLETE
                  ▼
          JSON + HTML reports
```

## Measured Episode 0 telemetry

| Measurement | Real result |
|---|---:|
| Pickup low point | frame 62 |
| Grasp transition | frame 66 |
| Lift threshold reached | frame 80 |
| Release transition | frame 139 |
| Lift rise at threshold | ~0.057 m |
| Grasp-to-release EE displacement | ~0.175 m |

These values came from the real Episode 0 run. The detector itself does not hard-code those frame numbers.

## Visual experiments and what they proved

A generic pretrained YOLO model executed successfully, but its COCO labels were not reliable task semantics for the marker and robot gripper. A telemetry-conditioned track-role experiment also confused multiple detections around the pot. A wrist-frame differencing experiment detected motion, but simple translation compensation did not isolate local object motion reliably on the moving wrist camera.

Those experiments are retained because they document an important evaluator behavior: **insufficient evidence becomes UNKNOWN, not a fabricated success.**

## Quick start

### 1. Create an environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-droid.txt
```

Install a TensorFlow build compatible with your OS/Python if it is not already available. Vision experiments additionally use:

```bash
python -m pip install -r requirements-vision.txt
```

### 2. Run tests

```bash
python -m pytest -v
```

### 3. Run the automatic DROID evaluator

```bash
python evaluate_droid_automatic.py /path/to/droid_100/1.0.0 --episode 0
```

Expected semantics:

```text
Approach   UNKNOWN
Grasp      PASS
Lift       PASS
Transport  PASS
Place      UNKNOWN
Release    PASS

Automatic status: INCOMPLETE
Established stages: 4/6
```

The command writes machine-readable JSON and a human-readable HTML report under `results/automatic/`.

## Repository guide

- `src/droid_adapter.py` — decodes DROID RLDS episodes.
- `src/droid_event_detector.py` — detects grasp/lift/release events and transport displacement.
- `src/automatic_droid_evaluator.py` — honest telemetry-only stage evaluation.
- `src/task_evaluator.py` — six-stage SUCCESS/FAILURE/INCOMPLETE core.
- `src/report_generator.py` — JSON + HTML reports with PASS/FAIL/UNKNOWN.
- `src/object_tracking.py` — optional YOLO + centroid-tracking baseline.
- `src/temporal_visual_roles.py` — experimental telemetry-conditioned role reasoning.
- `src/wrist_temporal_vision.py` — experimental wrist-camera temporal analysis.
- `docs/demo.md` — detailed Episode 0 evidence walkthrough.
- `docs/portfolio_demo.md` — step-by-step presentation script.

## Data and reproducibility

The DROID dataset, model weights, videos, and generated `results/` directories are intentionally excluded from Git because they are large/generated artifacts. The repository contains the source code, tests, documentation, and four compact real evidence images needed to understand the demo.

## Scope and limitations

This repository is a **portfolio prototype, not a benchmark claim**. It has been validated in depth on real DROID Episode 0. It does not claim measured accuracy across the full DROID dataset. Camera calibration is not assumed for the RLDS-only sample. Automatic Approach and Place remain future perception work.

## Project status

**Demo-ready portfolio prototype.**

The research implementation is frozen at an evidence-safe boundary: automatic telemetry establishes four stages, real visual evidence demonstrates the complete Episode 0 sequence, and uncertain automatic visual perception remains explicitly UNKNOWN rather than being overstated.
