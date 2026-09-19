"""Bridge detector/tracker observations into DROID vision fusion."""
from dataclasses import dataclass
from typing import Any

from src.droid_adapter import DroidStep
from src.droid_vision_fusion import fuse_step
from src.object_tracking import CentroidTracker, YoloObjectDetector
from src.vision_geometry import GeometryEstimator


@dataclass
class DroidVisionBridge:
    detector: YoloObjectDetector
    tracker: CentroidTracker
    geometry: GeometryEstimator

    def process_step(self, step: DroidStep, image: Any):
        if image is None:
            return fuse_step(step, None)
        height,width=image.shape[:2]
        detections=self.detector.detect(image)
        tracks=self.tracker.update(detections)
        vision=self.geometry.estimate(tracks,width,height)
        return fuse_step(step,vision)
