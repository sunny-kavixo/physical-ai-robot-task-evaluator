"""Adapt decoded DROID RLDS steps to the action-stage observation API.

DROID provides robot Cartesian pose, gripper state and three RGB views per step.
Object-relative quantities (object height/target distance) are NOT present in the
RLDS proprioceptive schema, so they remain unknown unless a vision estimator
supplies them.
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
    if hasattr(value, "numpy"):
        value = value.numpy()
    if hasattr(value, "tolist"):
        value = value.tolist()
    while isinstance(value, (list, tuple)) and len(value) == 1:
        value = value[0]
    return float(value)


def _vector(value: Any) -> tuple[float, ...]:
    if hasattr(value, "numpy"):
        value = value.numpy()
    if hasattr(value, "tolist"):
        value = value.tolist()
    return tuple(float(v) for v in value)


def decode_rlds_step(index: int, step: dict[str, Any]) -> DroidStep:
    observation = step["observation"]
    return DroidStep(
        frame_index=index,
        cartesian_position=_vector(observation["cartesian_position"]),
        gripper_position=_scalar(observation["gripper_position"]),
        wrist_image=observation.get("wrist_image_left"),
        exterior_image_1=observation.get("exterior_image_1_left"),
        exterior_image_2=observation.get("exterior_image_2_left"),
    )


def load_episode_from_tfds_directory(path: str, episode_index: int = 0) -> tuple[str, list[DroidStep]]:
    """Load one DROID episode from a downloaded TFDS/RLDS directory."""
    try:
        import tensorflow_datasets as tfds
    except ImportError as exc:
        raise RuntimeError(
            "RLDS loading requires TensorFlow Datasets. Install requirements-droid.txt"
        ) from exc

    builder = tfds.builder_from_directory(path)
    dataset = builder.as_dataset(split="all")
    for current_index, episode in enumerate(dataset):
        if current_index != episode_index:
            continue
        raw_steps = episode["steps"]
        steps = [decode_rlds_step(i, step) for i, step in enumerate(raw_steps)]
        instruction = ""
        if steps:
            # Read language directly from the first raw step; keep adapter state compact.
            first = next(iter(episode["steps"]))
            value = first.get("language_instruction", b"")
            if hasattr(value, "numpy"):
                value = value.numpy()
            if isinstance(value, bytes):
                instruction = value.decode("utf-8")
            else:
                instruction = str(value)
        return instruction, steps
    raise IndexError(f"episode_index {episode_index} not found")


def proprioceptive_observations(
    steps: Iterable[DroidStep],
    closed_threshold: float = 0.65,
) -> list[ActionObservation]:
    """Create only evidence DROID proprioception can support directly.

    DROID's platform reports gripper_position as normalized closure
    (approximately 0=open, 1=closed). Cartesian xyz supplies end-effector
    displacement. Object-relative fields stay None until vision fusion.
    """
    steps = list(steps)
    if not steps:
        return []
    origin = steps[0].cartesian_position[:3]
    result = []
    for step in steps:
        xyz = step.cartesian_position[:3]
        displacement = math.dist(origin, xyz)
        result.append(
            ActionObservation(
                frame_index=step.frame_index,
                gripper_object_distance=None,
                gripper_closed=step.gripper_position >= closed_threshold,
                object_height=None,
                object_displacement=displacement,
                object_target_distance=None,
            )
        )
    return result
