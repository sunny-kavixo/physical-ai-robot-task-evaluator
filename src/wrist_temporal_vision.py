"""Wrist-camera temporal change analysis for manipulation episodes."""
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class WristChangeEvidence:
    frame_index: int
    change_score: float
    centroid: tuple[float, float] | None
    changed_fraction: float

def _gray(image):
    a=np.asarray(image)
    if a.ndim == 2:
        return a.astype(np.float32)
    if a.ndim != 3 or a.shape[2] < 3:
        raise ValueError("expected HxW or HxWx3 image")
    return (0.299*a[...,0] + 0.587*a[...,1] + 0.114*a[...,2]).astype(np.float32)

def visual_change(reference, current, threshold: float = 25.0):
    a,b=_gray(reference),_gray(current)
    if a.shape != b.shape:
        raise ValueError("reference and current images must have identical shape")
    diff=np.abs(b-a)
    mask=diff >= threshold
    score=float(diff.mean())
    fraction=float(mask.mean())
    if not mask.any():
        return score,None,fraction
    ys,xs=np.nonzero(mask)
    return score,(float(xs.mean()),float(ys.mean())),fraction

def analyze_wrist_sequence(frames, reference_index: int, start: int, end: int, threshold: float = 25.0):
    if not frames:
        return []
    if not 0 <= reference_index < len(frames):
        raise IndexError("reference_index outside frame sequence")
    lo=max(0,start); hi=min(len(frames)-1,end)
    ref=frames[reference_index]
    evidence=[]
    for i in range(lo,hi+1):
        score,centroid,fraction=visual_change(ref,frames[i],threshold)
        evidence.append(WristChangeEvidence(i,score,centroid,fraction))
    return evidence
