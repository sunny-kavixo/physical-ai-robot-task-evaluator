"""Generate portable JSON and HTML evidence reports."""
import json, html
from pathlib import Path


def write_reports(payload: dict, output_dir: str, stem: str = "evaluation") -> tuple[Path,Path]:
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    jp=out/f"{stem}.json"; hp=out/f"{stem}.html"
    jp.write_text(json.dumps(payload,indent=2,default=str),encoding="utf-8")
    ev=payload.get("stage_evidence",[])
    rows="".join(
        f"<tr><td>{html.escape(str(x['stage']))}</td><td>{'PASS' if x['achieved'] else 'NOT ESTABLISHED'}</td>"
        f"<td>{html.escape(str(x.get('frame_index')))}</td><td>{html.escape(str(x.get('reason','')))}</td></tr>"
        for x in ev
    )
    evaluation=payload.get("evaluation",{})
    hp.write_text(f"""<!doctype html><html><head><meta charset="utf-8"><title>Robot Task Evaluation</title>
<style>body{{font-family:system-ui;max-width:1000px;margin:40px auto;padding:0 20px}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccc;padding:8px;text-align:left}}code{{background:#eee;padding:2px 5px}}</style></head><body>
<h1>Robot Task Evaluation</h1><p><b>Task:</b> {html.escape(str(payload.get('instruction','')))}</p>
<p><b>Status:</b> {html.escape(str(evaluation.get('status','UNKNOWN')))} &nbsp; <b>Completion:</b> {html.escape(str(evaluation.get('completed_stages','?')))}/{html.escape(str(evaluation.get('total_stages','?')))}</p>
<table><thead><tr><th>Stage</th><th>Evidence</th><th>Frame</th><th>Reason</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Provenance</h2><pre>{html.escape(json.dumps(payload.get('provenance',{}),indent=2,default=str))}</pre>
</body></html>""",encoding="utf-8")
    return jp,hp
