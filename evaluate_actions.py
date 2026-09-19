"""End-to-end baseline: action observations -> stages -> task report."""
import argparse, json
from src.action_stage_detector import ActionObservation, ActionStageDetector
from src.task_evaluator import RobotTaskEvaluator


def main():
    p=argparse.ArgumentParser()
    p.add_argument("observations", help="JSONL file containing ActionObservation fields")
    p.add_argument("--task-id", default="robot-task-001")
    p.add_argument("--instruction", default="Pick up the object and place it in the target.")
    args=p.parse_args()
    observations=[]
    with open(args.observations, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                observations.append(ActionObservation(**json.loads(line)))
    detector=ActionStageDetector()
    evidence=detector.detect(observations)
    report=RobotTaskEvaluator().evaluate(args.task_id,args.instruction,{e.stage:e.achieved for e in evidence})
    print(json.dumps({"stage_evidence":[e.__dict__ for e in evidence],"evaluation":report.to_dict()},indent=2))


if __name__=="__main__":
    main()
