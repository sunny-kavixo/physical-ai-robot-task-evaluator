"""Export visual evidence crops for automatic role assignments.

This is a validation utility: it creates real-image contact sheets around the
selected object/target tracks so a role assignment can be inspected instead of
accepted from a detector label.
"""
import argparse, json
from pathlib import Path
import cv2


def load_track_boxes(path, wanted):
    boxes = {tid: [] for tid in wanted if tid is not None}
    with open(path, encoding="utf-8") as f:
        for line in f:
            row=json.loads(line); frame=int(row["frame_index"])
            for t in row.get("tracks", []):
                tid=int(t["track_id"])
                if tid in boxes:
                    boxes[tid].append((frame, tuple(map(float,t["xyxy"]))))
    return boxes


def crop(frame, box, pad=18):
    h,w=frame.shape[:2]; x1,y1,x2,y2=box
    x1=max(0,int(x1)-pad); y1=max(0,int(y1)-pad)
    x2=min(w,int(x2)+pad); y2=min(h,int(y2)+pad)
    return frame[y1:y2,x1:x2]


def nearest(seq, frame):
    return min(seq, key=lambda x: abs(x[0]-frame)) if seq else None


def main():
    p=argparse.ArgumentParser()
    p.add_argument("video"); p.add_argument("tracks_jsonl")
    p.add_argument("--object-track",type=int,required=True)
    p.add_argument("--target-track",type=int,required=True)
    p.add_argument("--frames",default="60,66,80,120,139,150")
    p.add_argument("--output-dir",default="results/role_evidence")
    a=p.parse_args()

    requested=[int(x) for x in a.frames.split(",")]
    roles={"object":a.object_track,"target":a.target_track}
    boxes=load_track_boxes(a.tracks_jsonl,roles.values())
    cap=cv2.VideoCapture(a.video)
    out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=True)

    for frame_no in requested:
        cap.set(cv2.CAP_PROP_POS_FRAMES,frame_no)
        ok,image=cap.read()
        if not ok: continue
        for role,tid in roles.items():
            hit=nearest(boxes.get(tid,[]),frame_no)
            if hit is None: continue
            observed_frame,box=hit
            piece=crop(image,box)
            if piece.size:
                cv2.imwrite(str(out/f"{role}_track{tid}_request{frame_no}_observed{observed_frame}.jpg"),piece)
    cap.release()
    print(f"ROLE EVIDENCE EXPORTED: {out.resolve()}")
    print("Inspect these real crops before accepting the role assignments.")


if __name__=="__main__": main()
