# Real DROID Demo — Episode 0

## Task

**Instruction:** `Put the marker in the pot`

This demo uses a real episode from the DROID 100-episode RLDS debugging sample. Episode 0 contains 166 robot steps with synchronized robot state and wrist/exterior RGB observations.

## Before → manipulation → after

| Before pickup | Grasp / lift | Place / release | After |
|---|---|---|---|
| ![Before pickup](assets/episode0_before.jpg) | ![Grasp and lift](assets/episode0_grasp.jpg) | ![Place and release](assets/episode0_place.jpg) | ![After release](assets/episode0_after.jpg) |
| Marker remains in the pickup area while the robot approaches. | The gripper transitions to the holding state and the end effector rises. | The robot reaches the pot area and transitions toward release. | The gripper withdraws after the placement sequence. |

These are real DROID frames selected from the locally validated Episode 0.

## Evidence pipeline

```text
DROID episode
   ├── telemetry → Grasp / Lift / Transport / Release
   └── RGB frames → visual review and perception experiments
                         ↓
                 six-stage evaluator
                         ↓
             JSON + HTML evidence report
```

## Automatically measured telemetry

| Event | Episode 0 result |
|---|---:|
| Pickup low point | frame 62 |
| Grasp transition | frame 66 |
| Lift threshold reached | frame 80 |
| Release transition | frame 139 |
| Lift rise at threshold | ~0.057 m |
| Grasp-to-release EE displacement | ~0.175 m |

The detector calculates these events from telemetry; it does not hard-code these Episode 0 frame numbers.

## Automatic result versus human validation

| Stage | Automatic telemetry mode | Human Episode 0 validation |
|---|---|---|
| Approach | UNKNOWN | PASS |
| Grasp | PASS candidate | PASS |
| Lift | PASS | PASS |
| Transport | PASS | PASS |
| Place | UNKNOWN | PASS |
| Release | PASS candidate | PASS |

**Automatic status: INCOMPLETE — 4/6 stages established.**

**Human-validated Episode 0 result: SUCCESS — 6/6 stages.**

These are deliberately separate claims. The automatic path does not infer Approach or Place from telemetry alone.

## Visual-perception experiments

### Generic detector/tracker

A generic COCO YOLO model ran successfully but did not reliably identify the marker or robot gripper. Detector class names are therefore treated as diagnostic proposals, not robot-task truth.

### Telemetry-conditioned visual roles

Temporal track reasoning was tested using the grasp-to-release window. Real-image crop inspection showed ambiguous/fragmented detections around the pot, so those assignments were not promoted to stage evidence.

### Wrist temporal analysis

Raw wrist-frame differencing detected large scene changes. A simple translation-compensation experiment did not reduce global motion reliably on the real episode, so its centroids are not used as proof of Approach or Place.

## Reporting rule

The project uses three evidence states:

- **PASS** — the required evidence was established;
- **FAIL** — contradictory/failure evidence was established;
- **UNKNOWN** — available evidence is insufficient.

This prevents an experimental perception result from silently becoming a false task-success claim.

## Reports

`evaluate_droid_automatic.py` writes:
- JSON for machine-readable stage results, telemetry events, provenance, and limitations;
- HTML for human review.

See [portfolio_demo.md](portfolio_demo.md) for the final presentation walkthrough.
