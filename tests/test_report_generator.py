from pathlib import Path
import json
from src.report_generator import write_reports


def test_writes_json_and_html(tmp_path: Path):
    payload={"instruction":"pick & place","stage_evidence":[{"stage":"approach","achieved":True,"frame_index":4,"reason":"near"}],"evaluation":{"status":"SUCCESS","completed_stages":1,"total_stages":1},"provenance":{"source":"test"}}
    jp,hp=write_reports(payload,str(tmp_path))
    assert json.loads(jp.read_text())["evaluation"]["status"]=="SUCCESS"
    assert "pick &amp; place" in hp.read_text()
    assert "approach" in hp.read_text()
