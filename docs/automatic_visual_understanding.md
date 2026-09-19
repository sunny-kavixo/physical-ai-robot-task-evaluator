# Automatic visual understanding

The visual milestone is designed around an evidence rule: **generic detector
class names are proposals, not robot-task truth**.

## Current strategy

1. Decode DROID robot telemetry and detect the grasp/release manipulation window.
2. Track visible regions across RGB frames.
3. Score manipulated-object candidates by motion and persistence specifically
   during the grasp-to-release window.
4. Score target candidates by relative stationarity and proximity to the
   manipulated object's release-time position.
5. Use gripper identity only when supported by a trustworthy hint/model.
6. Feed accepted roles into normalized 2D geometry for Approach and Place.

This improves on the earlier role baseline because the real robot telemetry
constrains *when* object motion matters. It does not pretend that a COCO label
such as bowl/person/cup is automatically the marker, pot, or gripper.

## Evidence boundary

Without calibrated camera geometry or a dedicated gripper/object model, a role
assignment can still be uncertain. Low-confidence visual roles must remain
UNKNOWN rather than being converted into a false PASS/FAIL.

## Next validation

Run the reasoner on multiple real DROID episodes and inspect its selected tracks
against real frames. Only after that validation should Approach and Place be
promoted to fully automatic stage evidence.
