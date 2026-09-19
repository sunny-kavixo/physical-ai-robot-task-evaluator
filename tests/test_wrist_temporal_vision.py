import numpy as np
from src.wrist_temporal_vision import visual_change, analyze_wrist_sequence, estimate_translation

def test_visual_change_finds_changed_region():
    a=np.zeros((20,20,3),dtype=np.uint8)
    b=a.copy(); b[5:10,12:18]=255
    score,center,fraction,shift=visual_change(a,b,threshold=20,compensate=False)
    assert score > 0 and center is not None and fraction > 0
    assert 12 <= center[0] <= 17
    assert 5 <= center[1] <= 9
    assert shift == (0.0,0.0)

def test_sequence_reports_requested_window():
    frames=[np.zeros((8,8,3),dtype=np.uint8) for _ in range(5)]
    frames[3][2:5,2:5]=255
    out=analyze_wrist_sequence(frames,0,2,4,compensate=False)
    assert [x.frame_index for x in out] == [2,3,4]
    assert out[1].change_score > out[0].change_score

def test_translation_compensation_reduces_global_motion():
    rng=np.random.default_rng(7)
    base=rng.integers(0,256,(64,64,3),dtype=np.uint8)
    moved=np.roll(np.roll(base,4,axis=1),-3,axis=0)
    raw=visual_change(base,moved,20,compensate=False)[0]
    corrected=visual_change(base,moved,20,compensate=True)[0]
    assert corrected < raw
