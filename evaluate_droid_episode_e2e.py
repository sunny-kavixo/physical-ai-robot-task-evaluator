"""End-to-end DROID episode evaluator.

Runs on a locally downloaded RLDS episode plus validated calibration. The
pipeline refuses to invent task semantics when automatic visual roles cannot be
established.
"""
import argparse, json
from pathlib import Path
import numpy as np

from src.droid_adapter import load_episode_from_tfds_directory
from src.object_tracking import CentroidTracker, YoloObjectDetector
from src.camera_projection import project_robot_point
from src.calibration_loader import load_camera_calibration
from src.gripper_localization import find_gripper_track
from src.role_identifier import TrackRoleIdentifier
from src.vision_geometry import GeometryEstimator
from src.droid_vision_fusion import fuse_step
from src.action_stage_detector import ActionStageDetector
from src.task_evaluator import RobotTaskEvaluator
from src.report_generator import write_reports


def _image(step, view):
    value=getattr(step,view)
    if hasattr(value,"numpy"): value=value.numpy()
    return np.asarray(value) if value is not None else None


def evaluate(dataset_dir, calibration_file, episode_index=0, view="exterior_image_1", confidence=.25):
    instruction,steps=load_episode_from_tfds_directory(dataset_dir,episode_index)
    camera=load_camera_calibration(calibration_file)
    detector=YoloObjectDetector(confidence=confidence)
    tracker=CentroidTracker()
    history=[]; projected_gripper_ids=[]; frames=[]

    for step in steps:
        image=_image(step,view)
        if image is None or image.ndim < 2: continue
        h,w=image.shape[:2]
        tracks=tracker.update(detector.detect(image))
        history.append([t for t in tracks if t.missed_frames==0])
        p=project_robot_point(step.cartesian_position[:3],camera,w,h)
        gid=find_gripper_track(p,tracks)
        projected_gripper_ids.append(gid)
        frames.append((step,image,tracks))

    valid=[x for x in projected_gripper_ids if x is not None]
    gripper_hint=max(set(valid),key=valid.count) if valid else None
    roles=TrackRoleIdentifier().identify(history,gripper_hint)
    observations=[]
    if roles.object_track_id is not None:
        geometry=GeometryEstimator(roles.object_track_id,roles.target_track_id,roles.gripper_track_id)
        for step,image,tracks in frames:
            h,w=image.shape[:2]
            observations.append(fuse_step(step,geometry.estimate(tracks,w,h)))

    evidence=ActionStageDetector().detect(observations)
    stage_map={e.stage:(True if e.achieved else None) for e in evidence}
    evaluation=RobotTaskEvaluator().evaluate(
        f"droid-{episode_index}",instruction or "DROID manipulation episode",stage_map
    )
    return {
        "instruction":instruction,"episode_index":episode_index,
        "roles":roles.__dict__,"stage_evidence":[e.__dict__ for e in evidence],
        "evaluation":evaluation.to_dict(),
        "provenance":{
            "dataset_dir":str(dataset_dir),"camera_view":view,
            "calibration_file":str(calibration_file),"processed_frames":len(frames),
            "limitations":"2D geometry proxies; pretrained detector; result is not a benchmark accuracy claim."
        }
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("dataset_dir"); p.add_argument("calibration_file")
    p.add_argument("--episode",type=int,default=0)
    p.add_argument("--view",choices=["wrist_image","exterior_image_1","exterior_image_2"],default="exterior_image_1")
    p.add_argument("--output-dir",default="results/generated")
    p.add_argument("--confidence",type=float,default=.25)
    a=p.parse_args()
    payload=evaluate(a.dataset_dir,a.calibration_file,a.episode,a.view,a.confidence)
    jp,hp=write_reports(payload,a.output_dir,f"droid_episode_{a.episode}")
    print(json.dumps({"json":str(jp),"html":str(hp),"status":payload["evaluation"]["status"]},indent=2))


if __name__=="__main__": main()
