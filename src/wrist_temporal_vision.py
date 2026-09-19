"""Wrist-camera temporal vision with translation motion compensation."""
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class WristChangeEvidence:
    frame_index: int
    change_score: float
    centroid: tuple[float, float] | None
    changed_fraction: float
    shift_xy: tuple[float, float] = (0.0, 0.0)

def _gray(image):
    a=np.asarray(image)
    if a.ndim == 2: return a.astype(np.float32)
    if a.ndim != 3 or a.shape[2] < 3: raise ValueError("expected HxW or HxWx3 image")
    return (0.299*a[...,0]+0.587*a[...,1]+0.114*a[...,2]).astype(np.float32)

def estimate_translation(reference,current):
    """Estimate global x/y translation using phase correlation (NumPy only)."""
    a=_gray(reference); b=_gray(current)
    if a.shape != b.shape: raise ValueError("images must have identical shape")
    a=a-a.mean(); b=b-b.mean()
    cross=np.fft.fft2(a)*np.conj(np.fft.fft2(b))
    cross/=np.maximum(np.abs(cross),1e-9)
    corr=np.abs(np.fft.ifft2(cross))
    y,x=np.unravel_index(np.argmax(corr),corr.shape)
    h,w=a.shape
    if x>w//2: x-=w
    if y>h//2: y-=h
    return float(x),float(y)

def _shift(image,dx,dy):
    return np.roll(np.roll(np.asarray(image),int(round(dy)),axis=0),int(round(dx)),axis=1)

def visual_change(reference,current,threshold: float=25.0,compensate: bool=True):
    shift=(0.0,0.0)
    aligned=current
    if compensate:
        shift=estimate_translation(reference,current)
        aligned=_shift(current,*shift)
    a,b=_gray(reference),_gray(aligned)
    diff=np.abs(b-a); mask=diff>=threshold
    score=float(diff.mean()); fraction=float(mask.mean())
    if not mask.any(): return score,None,fraction,shift
    ys,xs=np.nonzero(mask)
    return score,(float(xs.mean()),float(ys.mean())),fraction,shift

def analyze_wrist_sequence(frames,reference_index:int,start:int,end:int,threshold:float=25.0,compensate:bool=True):
    if not frames: return []
    if not 0<=reference_index<len(frames): raise IndexError("reference_index outside frame sequence")
    lo=max(0,start); hi=min(len(frames)-1,end); ref=frames[reference_index]; out=[]
    for i in range(lo,hi+1):
        score,centroid,fraction,shift=visual_change(ref,frames[i],threshold,compensate)
        out.append(WristChangeEvidence(i,score,centroid,fraction,shift))
    return out
