import py_compile
from pathlib import Path


def test_wrist_temporal_validation_script_compiles(tmp_path):
    script = Path(__file__).parents[1] / "validate_wrist_temporal_vision.py"

    py_compile.compile(
        script,
        cfile=tmp_path / "validate_wrist_temporal_vision.pyc",
        doraise=True,
    )
