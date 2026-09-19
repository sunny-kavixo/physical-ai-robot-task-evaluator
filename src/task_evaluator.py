"""Rule-based task evaluation core for robot manipulation episodes."""

from dataclasses import asdict, dataclass
from typing import Mapping, Sequence

DEFAULT_STAGES = ("approach", "grasp", "lift", "transport", "place", "release")


@dataclass(frozen=True)
class EvaluationReport:
    task_id: str
    instruction: str
    status: str
    completed_stages: int
    total_stages: int
    completion_ratio: float
    first_problem_stage: str | None
    stage_results: dict[str, bool | None]

    def to_dict(self) -> dict:
        return asdict(self)


class RobotTaskEvaluator:
    """Evaluate ordered task stages without pretending to perform perception."""

    def __init__(self, expected_stages: Sequence[str] = DEFAULT_STAGES) -> None:
        if not expected_stages:
            raise ValueError("expected_stages must not be empty")
        if len(set(expected_stages)) != len(expected_stages):
            raise ValueError("expected_stages must be unique")
        self.expected_stages = tuple(expected_stages)

    def evaluate(
        self,
        task_id: str,
        instruction: str,
        stages: Mapping[str, bool | None],
    ) -> EvaluationReport:
        if not task_id.strip():
            raise ValueError("task_id must not be empty")
        if not instruction.strip():
            raise ValueError("instruction must not be empty")

        normalized: dict[str, bool | None] = {}
        for stage in self.expected_stages:
            value = stages.get(stage)
            if value not in (True, False, None):
                raise TypeError(f"{stage!r} must be True, False, or None")
            normalized[stage] = value

        completed = sum(value is True for value in normalized.values())
        first_problem = next((name for name, value in normalized.items() if value is not True), None)

        if all(value is True for value in normalized.values()):
            status = "SUCCESS"
        elif any(value is False for value in normalized.values()):
            status = "FAILURE"
        else:
            status = "INCOMPLETE"

        return EvaluationReport(
            task_id=task_id,
            instruction=instruction,
            status=status,
            completed_stages=completed,
            total_stages=len(self.expected_stages),
            completion_ratio=completed / len(self.expected_stages),
            first_problem_stage=first_problem,
            stage_results=normalized,
        )
