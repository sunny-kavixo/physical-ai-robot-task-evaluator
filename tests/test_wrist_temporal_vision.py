import numpy as np
from src.wrist_temporal_vision import visual_change, analyze_wrist_sequence


def test_visual_change_finds_changed_region():
    a=np.zeros((20,20,3),dtype=np.uint8)
    b=a.copy(); b[5:10,12:18]=255
    score,center,fraction=visual_change(a,b,threshold=20)
    assert score > 0
    assert center is not None
    assert 12 <= center[0] <= 17
    assert 5 <= center[1] <= 9
    assert fraction > 0


def test_sequence_reports_requested_window():
    frames=[np.zeros((8,8,3),dtype=np.uint8) for _ in range(5)]
    frames[3][2:5,2:5]=255
    out=analyze_wrist_sequence(frames,reference_index=0,start=2,end=4)
    assert [x.frame_index for x in out] == [2,3,4]
    assert out[1].change_score > out[0].change_score
