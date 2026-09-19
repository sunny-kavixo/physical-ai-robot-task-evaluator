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
