from pathlib import Path
import pytest
from src.droid_dataset import DroidDataset, official_sample_download_command


def test_download_command_targets_official_sample():
    cmd=official_sample_download_command("data")
    assert "gs://gresearch/robotics/droid_100" in cmd
    assert cmd.endswith(" data")


def test_dataset_discovers_tfrecord_shards(tmp_path: Path):
    (tmp_path/"nested").mkdir()
    (tmp_path/"nested"/"part.tfrecord-00000-of-00001").write_bytes(b"")
    ds=DroidDataset(tmp_path)
    assert len(ds.tfrecord_files()) == 1


def test_missing_dataset_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        DroidDataset(tmp_path/"missing").summary()
