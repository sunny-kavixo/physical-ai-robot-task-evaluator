# Real DROID Demo — Episode 0

## Task

**Instruction:** `Put the marker in the pot`

This demo uses a real episode from the official DROID 100-episode RLDS debugging sample. The episode contains 166 robot steps and synchronized robot state plus wrist/exterior RGB observations.

## Before → manipulation → after

| Before pickup | Grasp / lift | Place / release | After |
|---|---|---|---|
| ![Before pickup](assets/episode0_before.jpg) | ![Grasp and lift](assets/episode0_grasp.jpg) | ![Place and release](assets/episode0_place.jpg) | ![After release](assets/episode0_after.jpg) |
| Marker is still at the pickup area; robot approaches. | Telemetry changes to the holding state and the end effector rises. | Robot reaches the pot area and the gripper transitions toward release. | Gripper withdraws after the placement sequence. |

> These are real DROID frames selected from the locally validated Episode 0. The images are evidence examples, not model-generated illustrations.

## How the evaluator works

```text
DROID episode
     │
     ├── Robot telemetry
     │      ├── gripper position
     │      └── Cartesian end-effector pose
     │
     ├── RGB observations
     │      ├── wrist camera
     │      └── exterior cameras
     │
     ▼
Automatic telemetry event detector
     │
     ├── Grasp
     ├── Lift
     ├── Transport
     └── Release
     │
     ▼
Visual object/target reasoning
     │
     ├── Approach
     └── Place
     │
     ▼
Six-stage task evaluator
     │
     ├── Approach
     ├── Grasp
     ├── Lift
     ├── Transport
     ├── Place
     └── Release
     │
     ▼
SUCCESS / FAILURE / INCOMPLETE
     │
     ├── JSON report
     └── HTML evidence report
```

## Measured Episode 0 telemetry

| Event | Automatically detected evidence |
|---|---:|
| Pickup low point | frame 62 |
| Grasp candidate | frame 66 |
| Lift threshold reached | frame 80 |
| Release candidate | frame 139 |
| Lift rise at threshold | ~0.057 m |
| Grasp-to-release EE displacement | ~0.175 m |

The telemetry detector calculates these events from the episode. It does not hard-code the frame numbers above.

## Six-stage validation result

Targeted human inspection of the real wrist-camera frames plus decoded robot telemetry supported this Episode 0 sequence:

| Stage | Episode 0 validation | Evidence source |
|---|---|---|
| Approach | PASS | visual evidence |
| Grasp | PASS | automatic telemetry + visual check |
| Lift | PASS | automatic telemetry + visual check |
| Transport | PASS | automatic telemetry + visual check |
| Place | PASS | visual evidence |
| Release | PASS | automatic telemetry + visual check |

**Human-validated result: SUCCESS — 6/6 stages.**

This result must not be confused with a fully automatic benchmark result. The current automatic telemetry path can establish Grasp, Lift, Transport, and Release. Approach and Place remain unknown until trustworthy object-relative visual evidence is available.

## Why generic YOLO is not treated as ground truth

During real-data validation, a generic COCO YOLO model produced labels such as `bowl`, `cup`, `person`, `oven`, and `motorcycle` for parts of the DROID scene. Those labels are not reliable robot-task semantics. The project therefore does not force a marker/gripper identity from a wrong class label.

This limitation is deliberate: an evaluator that reports `UNKNOWN` when evidence is insufficient is more useful than one that manufactures a confident success.

## Reports

The evaluator writes both:

- **JSON** — machine-readable stage results, event frames, provenance, and limitations.
- **HTML** — a human-readable evidence report for review or portfolio demonstration.

The final demo will include generated report examples after multi-episode validation is complete.
