"""Load a local DROID RLDS episode and emit adapter observations."""
import argparse, json
from src.droid_adapter import load_episode_from_tfds_directory, proprioceptive_observations
from src.action_stage_detector import ActionStageDetector
from src.task_evaluator import RobotTaskEvaluator


def main():
    p=argparse.ArgumentParser()
    p.add_argument("dataset_dir")
    p.add_argument("--episode",type=int,default=0)
    args=p.parse_args()
    instruction,steps=load_episode_from_tfds_directory(args.dataset_dir,args.episode)
    observations=proprioceptive_observations(steps)
    evidence=ActionStageDetector().detect(observations)
    # Unknown object geometry means several stages cannot be established from
    # proprioception alone; this output is diagnostic, not a benchmark result.
    report=RobotTaskEvaluator().evaluate(
        f"droid-{args.episode}", instruction or "DROID manipulation episode",
        {e.stage:(True if e.achieved else None) for e in evidence},
    )
    print(json.dumps({
        "instruction":instruction,
        "steps":len(steps),
        "stage_evidence":[e.__dict__ for e in evidence],
        "evaluation":report.to_dict(),
        "note":"Object-relative stages require vision geometry fusion."
    },indent=2))


if __name__=="__main__": main()
