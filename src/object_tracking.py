"""Object detection and lightweight multi-frame tracking.

Ultralytics is optional. Import happens at runtime so the rest of the project
remains usable without the detector dependency.
"""
from dataclasses import asdict, dataclass
from typing import Iterable
import math


@dataclass(frozen=True)
class Detection:
    class_id: int
    class_name: str
    confidence: float
    xyxy: tuple[float, float, float, float]

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def center(self) -> tuple[float, float]:
        x1, y1, x2, y2 = self.xyxy
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


@dataclass
class Track:
    track_id: int
    class_id: int
    class_name: str
    confidence: float
    xyxy: tuple[float, float, float, float]
    missed_frames: int = 0

    @property
    def center(self) -> tuple[float, float]:
        x1, y1, x2, y2 = self.xyxy
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

    def to_dict(self) -> dict:
        return asdict(self)


class YoloObjectDetector:
    """Pretrained general-purpose detector; no robotics accuracy is implied."""

    def __init__(self, model_name: str = "yolo11n.pt", confidence: float = 0.25):
        if not 0.0 < confidence <= 1.0:
            raise ValueError("confidence must be in (0, 1]")
        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise RuntimeError(
                "Object detection requires ultralytics. "
                "Install with: pip install -r requirements-vision.txt"
            ) from exc
        self.model = YOLO(model_name)
        self.confidence = confidence

    def detect(self, frame) -> list[Detection]:
        result = self.model.predict(frame, conf=self.confidence, verbose=False)[0]
        names = result.names
        detections: list[Detection] = []
        for box in result.boxes:
            class_id = int(box.cls[0].item())
            coords = tuple(float(v) for v in box.xyxy[0].tolist())
            detections.append(
                Detection(
                    class_id=class_id,
                    class_name=str(names[class_id]),
                    confidence=float(box.conf[0].item()),
                    xyxy=coords,
                )
            )
        return detections


class CentroidTracker:
    """Small deterministic tracker for a transparent V1 baseline."""

    def __init__(self, max_distance: float = 100.0, max_missed_frames: int = 10):
        if max_distance <= 0:
            raise ValueError("max_distance must be positive")
        self.max_distance = max_distance
        self.max_missed_frames = max_missed_frames
        self._next_id = 1
        self._tracks: dict[int, Track] = {}

    @staticmethod
    def _distance(a: tuple[float, float], b: tuple[float, float]) -> float:
        return math.dist(a, b)

    def update(self, detections: Iterable[Detection]) -> list[Track]:
        detections = list(detections)
        unmatched_tracks = set(self._tracks)
        unmatched_detections = set(range(len(detections)))
        candidates = []

        for track_id, track in self._tracks.items():
            for index, detection in enumerate(detections):
                if track.class_id != detection.class_id:
                    continue
                distance = self._distance(track.center, detection.center)
                if distance <= self.max_distance:
                    candidates.append((distance, track_id, index))

        for _, track_id, index in sorted(candidates):
            if track_id not in unmatched_tracks or index not in unmatched_detections:
                continue
            detection = detections[index]
            track = self._tracks[track_id]
            track.xyxy = detection.xyxy
            track.confidence = detection.confidence
            track.missed_frames = 0
            unmatched_tracks.remove(track_id)
            unmatched_detections.remove(index)

        for track_id in unmatched_tracks:
            self._tracks[track_id].missed_frames += 1

        for track_id in list(self._tracks):
            if self._tracks[track_id].missed_frames > self.max_missed_frames:
                del self._tracks[track_id]

        for index in sorted(unmatched_detections):
            detection = detections[index]
            self._tracks[self._next_id] = Track(
                track_id=self._next_id,
                class_id=detection.class_id,
                class_name=detection.class_name,
                confidence=detection.confidence,
                xyxy=detection.xyxy,
            )
            self._next_id += 1

        return [self._tracks[key] for key in sorted(self._tracks)]
