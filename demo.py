"""Run a small deterministic demonstration of the evaluation core."""

import json
from src.task_evaluator import RobotTaskEvaluator


def main() -> None:
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
    print(json.dumps(report.to_dict(), indent=2))


if __name__ == "__main__":
    main()
