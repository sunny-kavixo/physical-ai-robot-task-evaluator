# Physical AI Robot Task Evaluator

A portfolio project for evaluating robot-manipulation episodes and producing transparent task-level success/failure reports.

## Problem

Robot-learning teams need repeatable ways to inspect manipulation episodes, determine which task stages completed, identify failure points, and summarize evaluation evidence.

## V1 scope

The first version provides a reproducible evaluation core. Given stage observations for a manipulation episode, it:

- validates the expected task stages;
- calculates task completion;
- reports `SUCCESS`, `FAILURE`, or `INCOMPLETE`;
- identifies the first failed/incomplete stage;
- emits a machine-readable JSON report.

The default manipulation sequence is:

`approach -> grasp -> lift -> transport -> place -> release`

Video perception and public robotics-dataset adapters will be added in later milestones. V1 deliberately does **not** claim that success/failure can already be inferred automatically from raw video.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python demo.py
pytest
```

## Example

```python
from src.task_evaluator import RobotTaskEvaluator

evaluator = RobotTaskEvaluator()
report = evaluator.evaluate(
    task_id="pick-and-place-001",
    instruction="Pick up the object and place it in the target container.",
    stages={
        "approach": True,
        "grasp": True,
        "lift": True,
        "transport": True,
        "place": False,
        "release": False,
    },
)
print(report.to_dict())
```

## Roadmap

1. Evaluation core and tests
2. Video metadata/frame pipeline
3. DROID sample-data adapter
4. Object/robot tracking
5. Temporal action-stage detection
6. Success/failure inference with confidence
7. Metrics, visual reports, and dashboard

## Data

Large datasets and generated media are intentionally excluded from Git. Dataset download instructions and licensing notes will be documented before sample data is added.

## Status

Early development. Current outputs are rule-based evaluation results from supplied stage observations, not benchmark accuracy claims.
