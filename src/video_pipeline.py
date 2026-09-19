"""Video inspection and deterministic frame extraction utilities."""

from dataclasses import asdict, dataclass
from pathlib import Path
import cv2


@dataclass(frozen=True)
class VideoMetadata:
    path: str
    frame_count: int
    fps: float
    width: int
    height: int
    duration_seconds: float

    def to_dict(self) -> dict:
        return asdict(self)


def inspect_video(path: str | Path) -> VideoMetadata:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {path}")
    try:
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    finally:
        cap.release()
    if fps <= 0:
        raise ValueError(f"Invalid FPS for video: {path}")
    return VideoMetadata(str(path), frame_count, fps, width, height, frame_count / fps)


def extract_frames(path: str | Path, output_dir: str | Path, every_n_frames: int = 30) -> list[Path]:
    if every_n_frames < 1:
        raise ValueError("every_n_frames must be >= 1")
    path, output_dir = Path(path), Path(output_dir)
    if not path.is_file():
        raise FileNotFoundError(path)
    output_dir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {path}")
    written, index = [], 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if index % every_n_frames == 0:
                target = output_dir / f"frame_{index:06d}.jpg"
                if not cv2.imwrite(str(target), frame):
                    raise OSError(f"Could not write frame: {target}")
                written.append(target)
            index += 1
    finally:
        cap.release()
    return written
