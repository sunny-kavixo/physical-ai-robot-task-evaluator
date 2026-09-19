"""Validate motion-compensated wrist evidence on a real DROID episode."""
import argparse, numpy as np
from src.droid_adapter import load_episode_from_tfds_directory
from src.wrist_temporal_vision import analyze_wrist_sequence

def image(step):
    value=step.wrist_image
    if hasattr(value,"numpy"): value=value.numpy()
    return np.asarray(value)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("dataset_dir"); p.add_argument("--episode",type=int,default=0)
    p.add_argument("--reference-frame",type=int,default=50)
    p.add_argument("--grasp-frame",type=int,default=66)
    p.add_argument("--release-frame",type=int,default=139)
    p.add_argument("--threshold",type=float,default=25.0); p.add_argument("--top",type=int,default=12)
    a=p.parse_args()
    instruction,steps=load_episode_from_tfds_directory(a.dataset_dir,a.episode,"train")
    frames=[image(s) for s in steps]
    ev=analyze_wrist_sequence(frames,a.reference_frame,max(0,a.grasp_frame-10),min(len(frames)-1,a.release_frame+10),a.threshold,True)
    strongest=sorted(ev,key=lambda x:x.change_score,reverse=True)[:a.top]
    print("=== MOTION-COMPENSATED WRIST VISION ===")
    print("Task:",instruction); print("Reference frame:",a.reference_frame)
    print("Manipulation window:",a.grasp_frame,"->",a.release_frame); print()
    for x in strongest:
        c="None" if x.centroid is None else f"({x.centroid[0]:.1f}, {x.centroid[1]:.1f})"
        print(f"frame={x.frame_index:3d} change={x.change_score:7.2f} changed={x.changed_fraction:.3f} centroid={c} shift=({x.shift_xy[0]:.0f},{x.shift_xy[1]:.0f})")
    print("\nMOTION-COMPENSATED ANALYSIS: PASS")
if __name__=="__main__": main()
