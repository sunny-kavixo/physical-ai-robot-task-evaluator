"""Run detection + tracking over a video and emit JSONL observations."""
import argparse
import json
import cv2

from src.object_tracking import CentroidTracker, YoloObjectDetector


def process_video(video: str, output: str, every: int, confidence: float) -> None:
    if every < 1:
        raise ValueError("--every must be >= 1")
    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video}")

    detector = YoloObjectDetector(confidence=confidence)
    tracker = CentroidTracker()
    frame_index = 0
    with open(output, "w", encoding="utf-8") as handle:
        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                if frame_index % every == 0:
                    detections = detector.detect(frame)
                    tracks = tracker.update(detections)
                    handle.write(json.dumps({
                        "frame_index": frame_index,
                        "detections": [d.to_dict() for d in detections],
                        "tracks": [t.to_dict() for t in tracks if t.missed_frames == 0],
                    }) + "\n")
                frame_index += 1
        finally:
            cap.release()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("video")
    parser.add_argument("--output", default="results/generated/tracks.jsonl")
    parser.add_argument("--every", type=int, default=5)
    parser.add_argument("--confidence", type=float, default=0.25)
    args = parser.parse_args()
    from pathlib import Path
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    process_video(args.video, args.output, args.every, args.confidence)


if __name__ == "__main__":
    main()
