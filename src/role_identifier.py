"""Heuristic role identification for gripper, manipulated object, and target.

Uses temporal track evidence rather than pretending a generic detector knows
robot-task semantics. Scores are inspectable and confidence is reported.
"""
from dataclasses import dataclass
import math
from collections import defaultdict
from src.object_tracking import Track


@dataclass(frozen=True)
class RoleAssignment:
    gripper_track_id: int | None
    object_track_id: int | None
    target_track_id: int | None
    confidence: float
    evidence: dict


class TrackRoleIdentifier:
    def __init__(self, min_frames: int = 3):
        self.min_frames=min_frames

    @staticmethod
    def _dist(a,b): return math.dist(a,b)

    def identify(self, history: list[list[Track]], gripper_hint: int | None = None) -> RoleAssignment:
        positions=defaultdict(list)
        classes={}
        for frame_i,tracks in enumerate(history):
            for t in tracks:
                if t.missed_frames==0:
                    positions[t.track_id].append((frame_i,t.center))
                    classes[t.track_id]=t.class_name
        eligible={i:p for i,p in positions.items() if len(p)>=self.min_frames}
        if not eligible:
            return RoleAssignment(None,None,None,0.0,{"reason":"insufficient track history"})

        def motion(seq):
            return sum(self._dist(seq[i-1][1],seq[i][1]) for i in range(1,len(seq)))

        motions={i:motion(p) for i,p in eligible.items()}
        # A gripper detector/keypoint model is preferred. Without one, a supplied
        # hint is required; generic COCO YOLO normally has no gripper class.
        gripper=gripper_hint if gripper_hint in eligible else None
        if gripper is None:
            candidates=[i for i in eligible if any(k in classes[i].lower() for k in ("gripper","robot hand","end effector"))]
            gripper=max(candidates,key=lambda i:motions[i],default=None)

        object_id=None
        proximity_scores={}
        if gripper is not None:
            gp=dict(eligible[gripper])
            for i,seq in eligible.items():
                if i==gripper: continue
                shared=[self._dist(pos,gp[f]) for f,pos in seq if f in gp]
                if shared:
                    proximity_scores[i]=sum(shared)/len(shared)
            # Manipulated objects should both move and spend time near gripper.
            if proximity_scores:
                max_motion=max(motions.values()) or 1.0
                max_prox=max(proximity_scores.values()) or 1.0
                scores={i:(motions[i]/max_motion) + (1.0-proximity_scores[i]/max_prox) for i in proximity_scores}
                object_id=max(scores,key=scores.get)

        target=None
        target_scores={}
        if object_id is not None:
            final_obj=eligible[object_id][-1][1]
            for i,seq in eligible.items():
                if i in (gripper,object_id): continue
                # Target is expected to be relatively stationary and near final object.
                target_scores[i]=self._dist(final_obj,seq[-1][1]) + motions[i]
            target=min(target_scores,key=target_scores.get,default=None)

        assigned=sum(x is not None for x in (gripper,object_id,target))
        confidence=assigned/3.0
        return RoleAssignment(gripper,object_id,target,confidence,{
            "classes":classes,"motion_pixels":motions,
            "mean_gripper_proximity_pixels":proximity_scores,
            "target_score":target_scores,
            "method":"temporal heuristic baseline"
        })
