"""DROID dataset helpers.

V1 supports discovery of locally downloaded RLDS shards and records the official
100-episode sample download command. TensorFlow parsing is kept optional so the
lightweight video pipeline can run without TensorFlow installed.
"""
from dataclasses import dataclass
from pathlib import Path

DROID_100_GCS_URI = "gs://gresearch/robotics/droid_100"


@dataclass(frozen=True)
class DroidDataset:
    root: Path

    def validate(self) -> None:
        if not self.root.exists():
            raise FileNotFoundError(self.root)
        if not self.root.is_dir():
            raise NotADirectoryError(self.root)

    def tfrecord_files(self) -> list[Path]:
        self.validate()
        return sorted(self.root.rglob("*.tfrecord*"))

    def summary(self) -> dict:
        files = self.tfrecord_files()
        return {"root": str(self.root), "tfrecord_shards": len(files)}


def official_sample_download_command(target_dir: str = "data") -> str:
    return f"gsutil -m cp -r {DROID_100_GCS_URI} {target_dir}"
