"""Prepare small real-image assets for the GitHub demo.

Run locally after the DROID Episode 0 key-event frames have been extracted.
This copies four already-extracted real wrist-camera JPEGs into docs/assets.
"""
from pathlib import Path
import shutil

SOURCE = Path("results/episode_0_key_events")
DEST = Path("docs/assets")

SELECTIONS = {
    "frame_040_wrist.jpg": "episode0_before.jpg",
    "frame_080_wrist.jpg": "episode0_grasp.jpg",
    "frame_140_wrist.jpg": "episode0_place.jpg",
    "frame_160_wrist.jpg": "episode0_after.jpg",
}

DEST.mkdir(parents=True, exist_ok=True)

missing = []
for src_name, dst_name in SELECTIONS.items():
    src = SOURCE / src_name
    if not src.exists():
        missing.append(str(src))
        continue
    shutil.copy2(src, DEST / dst_name)
    print(f"copied {src} -> {DEST / dst_name}")

if missing:
    raise SystemExit("Missing extracted frames:\n" + "\n".join(missing))

print("\nDEMO ASSETS READY")
