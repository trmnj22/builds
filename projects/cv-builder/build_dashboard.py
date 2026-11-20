#!/usr/bin/env python3
"""Build the one-page dashboard CV (HTML, PDF, preview PNG) from a dashboard note.

Usage:
    python3 build_dashboard.py "<path to dashboard .md or .json>" [--paper A4|Letter] [--rules rules.json]

The source is either a .json file or a Markdown note holding a single ```json block (see
examples/alex-morgan-dashboard.md). Content changes per application, the design lives here:
slate page, light header band, green accent, number tiles, world map with pins.

Spec keys (all optional except name):
    name, headline, contact [..], photo (path to an image, relative to the source file)
    tiles      [{value, unit, label}]                 3 or 4 big numbers
    cards      {title, subtitle, items: [{title, text}]}   current-role cards, 2 by 2
    fit        {title, items: [{need, proof, level 1-5}]}   JD needs mapped to proof
    timeline   {title, from, to, items: [{start, end, role, org, note}]}
    map        {title, pins: [{label, lat, lon, kind: lived|clients}],
                shade: {lived: [..], clients: [..]} (Natural Earth country names), key, legend}
    bars       {title, items: [{label, value 0-1, text}]}
    chips      {title, items: [..]}
    education  [{what, where, when}]
    listblock  {title, items: [{what, where, when}]}
    footer     {title, items: [..]}                    e.g. how I would start

With --rules, a ruled organisation in the timeline must carry its phrase in that item's note.
"""
import argparse, base64, html, json, os, re, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_cv import render_pdf, render_previews, names_org, org_pattern, load_rules, CHROME  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SLATE, BAND, INK, GREEN, PALE, MUTED = "#2f4a5a", "#86a9b5", "#24394a", "#8dc63f", "#dfe7ea", "#a9bcc6"

def esc(s):
    s = html.escape(str(s))
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)

def load_spec(path):
    text = open(path, encoding="utf-8").read()
    if path.lower().endswith(".json"):
        return json.loads(text)
    m = re.search(r"```json\s*\n(.*?)\n```", text, re.S)
    if not m:
        sys.exit("No ```json block found in " + path)
    return json.loads(m.group(1))

def descriptor_problems(sp, rules):
    """A ruled organisation goes in the timeline with its phrase in that item's note. Empty when it complies."""
    problems = []
    text = json.dumps(sp, ensure_ascii=False)
    for rule in rules:
        org, phrase = rule["org"], rule["phrase"].lower()
        hits = [it for it in (sp.get("timeline") or {}).get("items", []) if names_org(str(it.get("org", "")), org)]
        if hits:
            if not any(phrase in str(it.get("note", "")).lower() for it in hits):
                problems.append(f'no {org} timeline note says "{rule["phrase"]}"')
        elif re.search(org_pattern(org), text, re.I) and phrase not in text.lower():
            problems.append(f'the dashboard mentions {org} but never as "{rule["phrase"]}"')
    return problems

MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}

def header(sp, base_dir):
    photo = ""
    if isinstance(sp.get("photo"), str):
        p = os.path.join(base_dir, sp["photo"])
        if os.path.exists(p):
            mime = MIME.get(os.path.splitext(p)[1].lower(), "image/jpeg")
            b64 = base64.b64encode(open(p, "rb").read()).decode()
            photo = f'<div class="photo" style="background-image:url(data:{mime};base64,{b64})"></div>'
        else:
            print(f"photo: {p} not found, built without a photo", file=sys.stderr)
    contact = '<span class="dot">·</span>'.join(esc(c) for c in sp.get("contact", []))
    return (f'<header>{photo}<h1>{esc(sp["name"])}</h1>'
            f'<div class="headline">{esc(sp.get("headline", ""))}</div>'
            f'<div class="contact">{contact}</div></header>')

def tiles(sp):
    t = sp.get("tiles") or []
    if not t:
        return ""
    cells = "".join(f'<div class="tile"><div class="num">{esc(x["value"])}<span>{esc(x.get("unit", ""))}</span></div>'
                    f'<div class="lab">{esc(x["label"])}</div></div>' for x in t)
    return f'<section class="tiles" style="grid-template-columns:repeat({len(t)},1fr)">{cells}</section>'

def h2(t):
    return f"<h2>{esc(t)}</h2>"

def fit(sp):
    f = sp.get("fit")
    if not f:
        return ""
    rows = []
    for it in f["items"]:
        lvl = int(it.get("level", 5))
        dots = "".join(f'<i class="{"on" if i < lvl else ""}"></i>' for i in range(5))
        rows.append(f'<div class="fit"><div class="need">{esc(it["need"])}<span class="dots">{dots}</span></div>'
                    f'<div class="proof">{esc(it["proof"])}</div></div>')
    return h2(f.get("title", "What the role asks for")) + "".join(rows)

def cards(sp):
    c = sp.get("cards")
    if not c:
        return ""
    items = "".join(f'<div class="card"><div class="ctitle">{esc(i["title"])}</div><div class="ctext">{esc(i["text"])}</div></div>'
                    for i in c["items"])
    sub = f'<div class="csub">{esc(c["subtitle"])}</div>' if c.get("subtitle") else ""
    return h2(c.get("title", "Now")) + sub + f'<div class="cards">{items}</div>'

def timeline(sp):
    t = sp.get("timeline")
    if not t:
        return ""
    lo, hi = t.get("from", 2010), t.get("to", 2027)
    span = hi - lo
    ticks = "".join(f'<span style="left:{(y - lo) / span * 100:.2f}%">{y}</span>'
                    for y in range(lo, hi + 1, t.get("tick", 5)))
    rows = []
    for it in t["items"]:
        l = (it["start"] - lo) / span * 100
        w = max((it["end"] - it["start"]) / span * 100, 1.5)
        note = f'<div class="tnote">{esc(it["note"])}</div>' if it.get("note") else ""
        rows.append(f'<div class="trow"><div class="tlab"><b>{esc(it["org"])}</b> {esc(it["role"])}{note}</div>'
                    f'<div class="ttrack"><div class="tbar" style="left:{l:.2f}%;width:{w:.2f}%"></div></div></div>')
    return h2(t.get("title", "Career at a glance")) + "".join(rows) + f'<div class="tticks">{ticks}</div>'

def world(sp):
    m = sp.get("map")
    if not m:
        return ""
    W, H = 600, 230
    CLIENT = "#5f9fc0"  # shaded client countries: blue, clearly apart from pale land and green
    pts = [((p["lon"] + 180) / 360 * W, (80 - p["lat"]) / 138 * H, p) for p in m.get("pins", [])]
    shade = m.get("shade")
    if shade:
        # one path per country (Natural Earth names), same projection as the pins
        shapes = json.load(open(os.path.join(HERE, "assets", "world-countries-110m.json")))
        lived, clients = set(shade.get("lived", [])), set(shade.get("clients", []))
        missing = sorted((lived | clients) - set(shapes))
        if missing:
            print("map: no outline for", ", ".join(missing), "(too small at this scale)", file=sys.stderr)
        layers = {"land": [], "client": [], "lived": []}
        for name, d in shapes.items():
            k = "lived" if name in lived else "client" if name in clients else "land"
            layers[k].append(d)
        fills = {"land": PALE, "client": CLIENT, "lived": GREEN}
        base = "".join(f'<path fill="{fills[k]}" stroke="{SLATE}" stroke-width="0.35" d="{"".join(layers[k])}"/>'
                       for k in ("land", "client", "lived"))
        x0, x1, y0, y1 = m.get("crop", [0, W, 8, 216])
    else:
        d = open(os.path.join(HERE, "assets", "world-land-path.txt")).read().strip()
        base = f'<path fill="{PALE}" opacity="0.92" d="{d}"/>'
        # crop to the pins with a margin, so the map fills its column
        x0 = max(0, min(x for x, _, _ in pts) - 45) if pts else 0
        x1 = min(W, max(x for x, _, _ in pts) + 25) if pts else W
        y0 = max(0, min(y for _, y, _ in pts) - 40) if pts else 0
        y1 = min(H, max(y for _, y, _ in pts) + 40) if pts else H
    pins = []
    for x, y, p in pts:
        lived_pin = p.get("kind", "lived") == "lived"
        col = GREEN if lived_pin else "#ffffff"
        dy = p.get("dy", 22)
        anchor = p.get("anchor", "middle")
        ly = y + dy
        lx = x + p.get("dx", 0)
        pins.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{ly - (13 if dy > 0 else -4):.1f}" stroke="#fff" stroke-width="1.2"/>'
                    f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{5 if lived_pin else 4}" fill="{col}" stroke="#fff" stroke-width="1.4"/>'
                    f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}">{esc(p["label"])}</text>')
    svg = (f'<svg viewBox="{x0:.0f} {y0:.0f} {x1 - x0:.0f} {y1 - y0:.0f}" class="map">{base}'
           + "".join(pins) + "</svg>")
    leg = ""
    key = m.get("key")
    if key:
        # key = [lived label, clients label], drawn as the map draws them
        sw = f'<svg width="9" height="9" viewBox="0 0 12 12"><circle cx="6" cy="6" r="5" fill="{GREEN}" stroke="#fff" stroke-width="1.4"/></svg>'
        sc = f'<svg width="11" height="8" viewBox="0 0 14 10"><rect width="14" height="10" rx="1.5" fill="{CLIENT}"/></svg>'
        leg = f'<div class="mapkey"><span>{sw} {esc(key[0])}</span><span>{sc} {esc(key[1])}</span></div>'
    legend = m.get("legend", "")
    leg += f'<div class="legend">{esc(legend)}</div>' if legend else ""
    return h2(m.get("title", "International experience")) + svg + leg

def bars(sp):
    b = sp.get("bars")
    if not b:
        return ""
    rows = "".join(f'<div class="bar"><div class="track"><div class="fill" style="width:{float(i["value"]) * 100:.0f}%"></div></div>'
                   f'<div class="blab">{esc(i["label"])}<span>{esc(i.get("text", ""))}</span></div></div>' for i in b["items"])
    return h2(b.get("title", "Strengths")) + rows

def chips(sp):
    c = sp.get("chips")
    if not c:
        return ""
    return h2(c.get("title", "Toolkit")) + '<div class="chips">' + "".join(f"<span>{esc(i)}</span>" for i in c["items"]) + "</div>"

def education(sp):
    e = sp.get("education")
    if not e:
        return ""
    rows = "".join(f'<div class="edu"><div><b>{esc(i["what"])}</b><br><span>{esc(i["where"])}</span></div><div class="when">{esc(i.get("when", ""))}</div></div>' for i in e)
    return h2("Education") + rows

def listblock(sp):
    # optional titled list, same look as education: {"title": ..., "items": [{what, where, when}]}
    e = sp.get("listblock")
    if not e:
        return ""
    rows = "".join(f'<div class="edu"><div><b>{esc(i["what"])}</b><br><span>{esc(i["where"])}</span></div><div class="when">{esc(i.get("when", ""))}</div></div>' for i in e["items"])
    return h2(e.get("title", "")) + rows

def footer(sp):
    f = sp.get("footer")
    if not f:
        return ""
    items = "".join(f'<div class="step"><div class="n">{n}</div><div>{esc(t)}</div></div>' for n, t in enumerate(f["items"], 1))
    return f'<section class="foot"><h2>{esc(f.get("title", "How I would start"))}</h2><div class="steps">{items}</div></section>'

CSS = """
@page { size: %(paper)s; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; color: #fff; font-size: 9pt; line-height: 1.36;
  -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: %(w)s; min-height: %(h)s; background: SLATE; display: flex; flex-direction: column; }
header { background: BAND; color: INK; padding: 9mm 12mm 6mm 12mm; position: relative; min-height: 38mm; }
header h1 { font-family: Georgia, "Times New Roman", serif; font-weight: 400; font-size: 31pt; margin: 0; letter-spacing: .3pt; line-height: 1.05; }
.headline { font-family: Georgia, serif; font-weight: 700; font-size: 12pt; margin-top: 2.5mm; max-width: 140mm; }
.contact { font-size: 8.4pt; margin-top: 2.5mm; color: #1d2f3c; }
.contact .dot { padding: 0 5pt; opacity: .6; }
.photo { position: absolute; right: 12mm; top: 5mm; width: 36mm; height: 36mm; border-radius: 50%%; background-size: cover;
  background-position: center 18%%; border: 1.2mm solid SLATE; }
.tiles { display: grid; gap: 3mm; padding: 5mm 12mm 1mm 12mm; }
.tile { border: 0.3mm solid rgba(255,255,255,.22); border-radius: 2mm; padding: 2.6mm 3mm; }
.tile .num { font-family: Georgia, serif; font-size: 21pt; font-weight: 700; color: GREEN; line-height: 1; }
.tile .num span { font-size: 9.5pt; margin-left: 2pt; color: GREEN; font-family: "Helvetica Neue", sans-serif; font-weight: 600; }
.tile .lab { font-size: 7.8pt; color: #e6eef1; margin-top: 1.4mm; line-height: 1.25; }
main { display: grid; grid-template-columns: 1.18fr 1fr; gap: 7mm; padding: 1mm 12mm 0 12mm; flex: 1; }
h2 { font-family: Georgia, serif; font-weight: 400; font-size: 11pt; text-transform: uppercase; letter-spacing: .6pt;
  border-bottom: 0.3mm solid rgba(255,255,255,.55); padding-bottom: 1.2mm; margin: 5.5mm 0 2.8mm 0; color: #fff; }
.csub { font-size: 8.3pt; color: MUTED; margin: -1.4mm 0 2.4mm 0; }
.cards { display: grid; grid-template-columns: 1fr 1fr; gap: 2.6mm; }
.card { border-left: 0.8mm solid GREEN; background: rgba(255,255,255,.06); padding: 2.2mm 2.6mm; border-radius: 0 1.5mm 1.5mm 0; }
.ctitle { font-weight: 700; font-size: 8.9pt; color: #fff; margin-bottom: .8mm; line-height: 1.2; }
.ctext { font-size: 8.1pt; color: #dbe5ea; line-height: 1.3; }
.fit { margin-bottom: 3mm; }
.need { font-weight: 700; font-size: 9.1pt; display: flex; justify-content: space-between; gap: 3mm; color: #fff; }
.dots { flex: 0 0 auto; white-space: nowrap; }
.dots i { display: inline-block; width: 2.3mm; height: 2.3mm; border-radius: 50%%; background: rgba(255,255,255,.22); margin-left: 0.9mm; }
.dots i.on { background: GREEN; }
.proof { color: #dbe5ea; font-size: 8.5pt; margin-top: .6mm; }
.trow { display: grid; grid-template-columns: 1fr 38mm; gap: 2.5mm; align-items: center; margin-bottom: 2mm; }
.tlab { font-size: 8.5pt; color: #e8eff2; line-height: 1.2; }
.tlab b { color: #fff; }
.tnote { color: MUTED; font-size: 7.4pt; }
.ttrack { position: relative; height: 2.2mm; background: rgba(255,255,255,.13); border-radius: 1mm; }
.tbar { position: absolute; top: 0; bottom: 0; background: GREEN; border-radius: 1mm; }
.tticks { position: relative; height: 3.5mm; margin-left: calc(100%% - 38mm); width: 38mm; }
.tticks span { position: absolute; transform: translateX(-50%%); font-size: 6.3pt; color: MUTED; }
svg.map { width: 100%%; display: block; margin-top: 1mm; }
svg.map text { font-size: 16px; fill: #fff; font-family: "Helvetica Neue", sans-serif; font-weight: 600; paint-order: stroke; stroke: SLATE; stroke-width: 4px; stroke-linejoin: round; }
.legend { font-size: 7.2pt; color: MUTED; margin-top: .5mm; }
.mapkey { display: flex; gap: 5mm; font-size: 7.8pt; color: #fff; margin-top: .8mm; }
.mapkey svg { vertical-align: -1px; }
.bar { display: grid; grid-template-columns: 38%% 1fr; gap: 2.5mm; align-items: center; margin-bottom: 1.5mm; }
.track { height: 3.2mm; background: rgba(255,255,255,.18); }
.fill { height: 100%%; background: GREEN; }
.blab { font-size: 8pt; color: #fff; display: flex; justify-content: space-between; gap: 2mm; }
.blab span { color: MUTED; white-space: nowrap; }
.chips { display: flex; flex-wrap: wrap; gap: 1.4mm; }
.chips span { border: 0.3mm solid GREEN; color: #fff; border-radius: 3mm; padding: .9mm 2.4mm; font-size: 8pt; }
.edu { display: flex; justify-content: space-between; gap: 3mm; margin-bottom: 2.4mm; font-size: 8.6pt; }
.edu span { color: #dbe5ea; }
.edu .when { color: MUTED; white-space: nowrap; }
.foot { margin: 2mm 12mm 6mm 12mm; border-top: 0.3mm solid rgba(255,255,255,.55); }
.foot h2 { border: 0; margin: 3mm 0 2mm 0; }
.steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 4mm; }
.step { display: flex; gap: 2.2mm; font-size: 8pt; color: #e6eef1; }
.step .n { flex: 0 0 5.5mm; height: 5.5mm; border-radius: 50%%; background: GREEN; color: SLATE; font-weight: 700;
  display: flex; align-items: center; justify-content: center; font-size: 8.5pt; }
"""

def page(sp, paper, base_dir="."):
    w, h = ("210mm", "297mm") if paper == "A4" else ("8.5in", "11in")
    css = CSS % {"paper": paper, "w": w, "h": h}
    for k, v in {"SLATE": SLATE, "BAND": BAND, "INK": INK, "GREEN": GREEN, "MUTED": MUTED}.items():
        css = css.replace(k, v)
    left = cards(sp) + fit(sp) + timeline(sp)
    right = world(sp) + listblock(sp) + bars(sp) + chips(sp) + education(sp)
    return ("<!doctype html><html><head><meta charset='utf-8'>"
            f"<title>{esc(sp['name'])} dashboard CV</title><style>{css}</style></head><body><div class='page'>"
            + header(sp, base_dir) + tiles(sp) + f"<main><div>{left}</div><div>{right}</div></main>" + footer(sp)
            + "</div></body></html>")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--paper", default="A4", choices=["A4", "Letter"])
    ap.add_argument("--rules", default=None, help="JSON file of required descriptors (see build_cv.load_rules)")
    a = ap.parse_args()
    # Stop before building rather than skip a check: Chrome renders, pdfinfo counts pages, pdftoppm makes the preview.
    if not os.path.exists(CHROME):
        sys.exit(f"FAILED: Google Chrome not found at {CHROME}. It renders the PDF. Set CHROME_PATH to point at it.")
    missing = [t for t in ("pdfinfo", "pdftoppm") if shutil.which(t) is None]
    if missing:
        sys.exit(f"FAILED: {' and '.join(missing)} not found (poppler), so the page count or the preview cannot be made. brew install poppler.")
    sp = load_spec(a.source)
    bad = descriptor_problems(sp, load_rules(a.rules))
    if bad:
        print(f"REFUSED: a required descriptor is missing: {'; '.join(bad)}.", file=sys.stderr)
        sys.exit(5)
    base = os.path.splitext(a.source)[0]
    open(base + ".html", "w", encoding="utf-8").write(page(sp, a.paper, os.path.dirname(os.path.abspath(a.source))))
    try:
        n = render_pdf(base + ".html", base + ".pdf")
    except Exception as e:  # a failed or hung Chrome render
        sys.exit(f"FAILED: Chrome could not render the PDF ({e.__class__.__name__}). Try again.")
    if not n:
        sys.exit("FAILED: no PDF was rendered (Chrome missing?).")
    print(f"html: {base}.html")
    print(f"pdf:  {base}.pdf  ({n} page{'s' if n != 1 else ''})")
    for p in render_previews(base + ".pdf", base):
        print("preview:", p)
    if n > 1:
        print("FAILED: more than one page. Cut items or shorten text.", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
