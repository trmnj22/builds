"""Render a demo grade dashboard from sample-grades.json.

This is a helper for the README demo only. In real use the skill's
orchestrator agent writes the dashboard itself from the two agents' JSON.

Usage: python3 examples/render_demo.py [grades.json] [out.html]
"""
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "assets" / "dashboard-template.html"


def band(pct, bands):
    for floor, name in bands:
        if pct >= floor:
            return name
    return bands[-1][1]


def esc(x):
    return html.escape(str(x))


def lens_totals(data, lens):
    got = sum(data[lens]["scores"][c["id"]]["score"] for c in data["criteria"])
    total = sum(c["max"] for c in data["criteria"])
    pct = round(100 * got / total)
    return got, total, pct, band(pct, data["bands"])


def lens_block(c, s):
    pct = round(100 * s["score"] / c["max"])
    earns = "".join(f"<li>{esc(e)}</li>" for e in s["earns"])
    if s["loses"]:
        loses = "<ul>" + "".join(f"<li>{esc(l)}</li>" for l in s["loses"]) + "</ul>"
    else:
        loses = '<p class="none">Nothing, full marks.</p>'
    return (
        f'<div class="scoreline"><span class="pts">{s["score"]}</span> / {c["max"]}</div>'
        f'<div class="bar"><i style="width:{pct}%"></i></div>'
        f'<div class="just">{esc(s["justification"])}</div>'
        f'<div class="el"><div class="box earn"><h4>What earns marks</h4><ul>{earns}</ul></div>'
        f'<div class="box lose"><h4>What loses marks</h4>{loses}</div></div>'
    )


def render(data):
    style = re.search(r"<style>.*?</style>", TEMPLATE.read_text(), re.S).group(0)
    sg, tot, sp, sb = lens_totals(data, "strict")
    lg, _, lp, lb = lens_totals(data, "lenient")
    prof = esc(data["professor"])
    cards = ""
    for c in data["criteria"]:
        cards += (
            f'<div class="crit"><div class="crit-head"><span class="name">{esc(c["name"])}</span>'
            f'<span class="max">max {c["max"]}</span></div>'
            f'<div class="v-strict">{lens_block(c, data["strict"]["scores"][c["id"]])}</div>'
            f'<div class="v-lenient">{lens_block(c, data["lenient"]["scores"][c["id"]])}</div></div>'
        )
    imps = "".join(f"<li>{esc(i['text'])} <small>({esc(i['targets'])})</small></li>" for i in data["improvements"])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(data["assignment"])} · Grade dashboard</title>
{style}
</head><body class="lens-strict"><div class="wrap">
<header><h1>{esc(data["assignment"])}</h1>
<p>Examiner <b>Prof. {prof}</b> · Scale {esc(data["scale"])} · {esc(data["date"])} · Files: {esc(", ".join(data["files"]))}</p></header>
<div class="seg" role="group" aria-label="Choose grading lens">
<button type="button" data-l="strict" aria-pressed="true" onclick="setLens('strict')">Strict professor</button>
<button type="button" data-l="lenient" aria-pressed="false" onclick="setLens('lenient')">Lenient professor</button></div>
<div class="hero">
<div class="v-strict"><div>Strict lens · independent grader</div><div class="big">{sp}%</div><div>{sg} / {tot} · {sb}</div>
<div class="compare">Lenient professor scored this <b>{lp}% ({lb})</b>. Spread between graders: {lp - sp} points.</div></div>
<div class="v-lenient"><div>Lenient lens · independent grader</div><div class="big">{lp}%</div><div>{lg} / {tot} · {lb}</div>
<div class="compare">Strict professor scored this <b>{sp}% ({sb})</b>. Spread between graders: {lp - sp} points.</div></div>
</div>
{cards}
<div class="v-strict"><div class="verdict"><h3>{sp}% · {sb}</h3><p>{esc(data["strict"]["verdict"])}</p><em>Prof. {prof}, holding the line.</em></div></div>
<div class="v-lenient"><div class="verdict"><h3>{lp}% · {lb}</h3><p>{esc(data["lenient"]["verdict"])}</p><em>Prof. {prof}, giving credit where due.</em></div></div>
<h2>How to close the gap</h2><ul>{imps}</ul>
<footer><p>{esc(data["methodology"])}</p></footer>
</div>
<script>
function setLens(l){{document.body.classList.remove('lens-strict','lens-lenient');document.body.classList.add('lens-'+l);
document.querySelectorAll('.seg button').forEach(function(b){{b.setAttribute('aria-pressed',b.dataset.l===l?'true':'false');}});}}
</script></body></html>
"""


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "sample-grades.json"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "demo-dashboard.html"
    out.write_text(render(json.loads(src.read_text())))
    print(f"Wrote {out.name}")
