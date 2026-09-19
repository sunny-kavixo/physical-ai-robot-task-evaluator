"""Inspect a local robot video and optionally extract sampled frames."""
import argparse, json
from src.video_pipeline import extract_frames, inspect_video


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("video")
    parser.add_argument("--frames-dir")
    parser.add_argument("--every", type=int, default=30)
    args=parser.parse_args()
    metadata=inspect_video(args.video)
    result={"video": metadata.to_dict()}
    if args.frames_dir:
        frames=extract_frames(args.video,args.frames_dir,args.every)
        result["extracted_frames"]=[str(p) for p in frames]
    print(json.dumps(result,indent=2))

if __name__=="__main__": main()
