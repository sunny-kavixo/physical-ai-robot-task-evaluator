"""Run the calibration-free automatic evaluator on a local DROID RLDS episode."""
import argparse
import json

from src.automatic_droid_evaluator import evaluate_telemetry_episode
from src.droid_adapter import load_episode_from_tfds_directory
from src.report_generator import write_reports


def main():
    p = argparse.ArgumentParser()
    p.add_argument("dataset_dir")
    p.add_argument("--episode", type=int, default=0)
    p.add_argument("--output-dir", default="results/automatic")
    p.add_argument("--gripper-threshold", type=float, default=0.5)
    p.add_argument("--lift-threshold", type=float, default=0.05)
    p.add_argument("--transport-threshold", type=float, default=0.10)
    a = p.parse_args()

    instruction, steps = load_episode_from_tfds_directory(
        a.dataset_dir, episode_index=a.episode, split="train"
    )
    payload = evaluate_telemetry_episode(
        instruction,
        steps,
        episode_index=a.episode,
        gripper_threshold=a.gripper_threshold,
        lift_threshold_m=a.lift_threshold,
        transport_threshold_m=a.transport_threshold,
    )
    jp, hp = write_reports(payload, a.output_dir, f"droid_episode_{a.episode}_automatic")
    print(json.dumps({
        "task": instruction,
        "episode": a.episode,
        "status": payload["evaluation"]["status"],
        "completed_stages": payload["evaluation"]["completed_stages"],
        "total_stages": payload["evaluation"]["total_stages"],
        "telemetry_events": payload["telemetry_events"],
        "json_report": str(jp),
        "html_report": str(hp),
    }, indent=2))


if __name__ == "__main__":
    main()
