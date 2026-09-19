"""Validate temporal visual role reasoning against an existing real tracking run."""
import argparse
import json

from src.object_tracking import Track
from src.temporal_visual_roles import TemporalRoleReasoner


def load_history(path: str):
    by_frame = {}
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            frame = int(row["frame_index"])
            tracks = []
            for item in row.get("tracks", []):
                tracks.append(Track(
                    track_id=int(item["track_id"]),
                    class_id=int(item["class_id"]),
                    class_name=str(item["class_name"]),
                    confidence=float(item["confidence"]),
                    xyxy=tuple(float(v) for v in item["xyxy"]),
                    missed_frames=int(item.get("missed_frames", 0)),
                ))
            by_frame[frame] = tracks

    if not by_frame:
        return []
    last = max(by_frame)
    return [by_frame.get(i, []) for i in range(last + 1)]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("tracks_jsonl")
    p.add_argument("--grasp-frame", type=int, required=True)
    p.add_argument("--release-frame", type=int, required=True)
    p.add_argument("--gripper-track", type=int)
    args = p.parse_args()

    history = load_history(args.tracks_jsonl)
    roles = TemporalRoleReasoner().identify(
        history,
        grasp_frame=args.grasp_frame,
        release_frame=args.release_frame,
        gripper_track_id=args.gripper_track,
    )

    print("=== REAL VISUAL ROLE VALIDATION ===")
    print(f"Manipulated object track : {roles.object_track_id}")
    print(f"Target track             : {roles.target_track_id}")
    print(f"Gripper track            : {roles.gripper_track_id}")
    print(f"Object confidence        : {roles.object_confidence:.3f}")
    print(f"Target confidence        : {roles.target_confidence:.3f}")
    print()
    print("Detector labels (diagnostic only; NOT task truth):")
    classes = roles.evidence.get("classes", {})
    for label, tid in (
        ("object", roles.object_track_id),
        ("target", roles.target_track_id),
        ("gripper", roles.gripper_track_id),
    ):
        print(f"  {label:7s}: {classes.get(tid, 'UNKNOWN') if tid is not None else 'UNKNOWN'}")
    print()
    print("REAL VISUAL ROLE TEST COMPLETE")


if __name__ == "__main__":
    main()
