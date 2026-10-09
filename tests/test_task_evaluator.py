import pytest

from src.task_evaluator import RobotTaskEvaluator


def test_success_when_every_stage_passes():
    evaluator = RobotTaskEvaluator()
    report = evaluator.evaluate("1", "pick and place", {stage: True for stage in evaluator.expected_stages})
    assert report.status == "SUCCESS"
    assert report.completion_ratio == 1.0
    assert report.first_problem_stage is None


def test_failure_reports_first_failed_stage():
    evaluator = RobotTaskEvaluator()
    report = evaluator.evaluate(
        "2", "pick and place",
        {"approach": True, "grasp": False, "lift": None},
    )
    assert report.status == "FAILURE"
    assert report.first_problem_stage == "grasp"
    assert report.completed_stages == 1


def test_missing_stages_are_incomplete():
    evaluator = RobotTaskEvaluator()
    report = evaluator.evaluate("3", "pick and place", {"approach": True})
    assert report.status == "INCOMPLETE"
    assert report.first_problem_stage == "grasp"


def test_empty_task_id_is_rejected():
    with pytest.raises(ValueError):
        RobotTaskEvaluator().evaluate("", "task", {})


@pytest.mark.parametrize("value", [1, 0, 2, -1, "true", "false"])
def test_non_boolean_stage_values_are_rejected(value):
    evaluator = RobotTaskEvaluator(expected_stages=("grasp",))

    with pytest.raises(TypeError, match="'grasp' must be True, False, or None"):
        evaluator.evaluate("4", "pick and place", {"grasp": value})


@pytest.mark.parametrize(
    ("value", "expected_status"),
    [(True, "SUCCESS"), (False, "FAILURE"), (None, "INCOMPLETE")],
)
def test_boolean_and_unknown_stage_values_remain_supported(value, expected_status):
    evaluator = RobotTaskEvaluator(expected_stages=("grasp",))

    report = evaluator.evaluate("5", "pick and place", {"grasp": value})

    assert report.status == expected_status
    assert report.stage_results == {"grasp": value}
