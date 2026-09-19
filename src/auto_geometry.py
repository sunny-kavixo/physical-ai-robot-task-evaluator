"""Configure GeometryEstimator from automatically inferred track roles."""
from src.role_identifier import TrackRoleIdentifier, RoleAssignment
from src.vision_geometry import GeometryEstimator


def build_geometry_estimator(history, gripper_hint=None) -> tuple[GeometryEstimator | None, RoleAssignment]:
    roles=TrackRoleIdentifier().identify(history,gripper_hint=gripper_hint)
    if roles.object_track_id is None:
        return None,roles
    return GeometryEstimator(
        object_track_id=roles.object_track_id,
        target_track_id=roles.target_track_id,
        gripper_track_id=roles.gripper_track_id,
    ),roles
