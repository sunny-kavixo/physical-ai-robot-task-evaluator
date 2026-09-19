"""Adapt decoded DROID RLDS steps to the action-stage observation API.

Verified against the official DROID RLDS schema: each episode has a steps
sequence containing language instructions, robot proprioception, and three
180x320 RGB views. Camera calibration is not part of the documented RLDS step
schema, so calibration is handled separately.
"""
from dataclasses import dataclass
from typing import Any, Iterable
import math
from src.action_stage_detector import ActionObservation

@dataclass(frozen=True)
class DroidStep:
    frame_index: int
    cartesian_position: tuple[float, ...]
    gripper_position: float
    wrist_image: Any = None
    exterior_image_1: Any = None
    exterior_image_2: Any = None

def _scalar(value: Any) -> float:
    if hasattr(value,"numpy"): value=value.numpy()
    if hasattr(value,"tolist"): value=value.tolist()
    while isinstance(value,(list,tuple)) and len(value)==1: value=value[0]
    return float(value)

def _vector(value: Any) -> tuple[float,...]:
    if hasattr(value,"numpy"): value=value.numpy()
    if hasattr(value,"tolist"): value=value.tolist()
    return tuple(float(v) for v in value)

def _text(value: Any) -> str:
    if hasattr(value,"numpy"): value=value.numpy()
    return value.decode("utf-8") if isinstance(value,bytes) else str(value)

def decode_rlds_step(index:int, step:dict[str,Any]) -> DroidStep:
    o=step["observation"]
    return DroidStep(index,_vector(o["cartesian_position"]),_scalar(o["gripper_position"]),
                     o.get("wrist_image_left"),o.get("exterior_image_1_left"),o.get("exterior_image_2_left"))

def load_episode_from_tfds_directory(path:str,episode_index:int=0,split:str="train") -> tuple[str,list[DroidStep]]:
    try:
        import tensorflow_datasets as tfds
    except ImportError as exc:
        raise RuntimeError("RLDS loading requires TensorFlow Datasets. Install requirements-droid.txt") from exc
    builder=tfds.builder_from_directory(path)
    available=set(builder.info.splits.keys())
    if split not in available:
        if len(available)==1:
            split=next(iter(available))
        else:
            raise ValueError(f"split {split!r} unavailable; available={sorted(available)}")
    dataset=builder.as_dataset(split=split)
    for current_index,episode in enumerate(dataset):
        if current_index != episode_index: continue
        raw=list(episode["steps"].as_numpy_iterator()) if hasattr(episode["steps"],"as_numpy_iterator") else list(episode["steps"])
        if not raw: return "",[]
        instruction=_text(raw[0].get("language_instruction",b""))
        return instruction,[decode_rlds_step(i,s) for i,s in enumerate(raw)]
    raise IndexError(f"episode_index {episode_index} not found")

def proprioceptive_observations(steps:Iterable[DroidStep],closed_threshold:float=.65)->list[ActionObservation]:
    steps=list(steps)
    if not steps:return []
    origin=steps[0].cartesian_position[:3]
    return [ActionObservation(s.frame_index,None,s.gripper_position>=closed_threshold,None,
            math.dist(origin,s.cartesian_position[:3]),None) for s in steps]
