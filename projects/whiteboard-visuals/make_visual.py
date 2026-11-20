#!/usr/bin/env python3
"""Render a social post visual in the Whiteboard design system.

    python3 make_visual.py spec.json [--out file.png] [--square] [--keep-html]

Spec types: boxes, number, ladder, compare (README.md, examples/). The design lives in tokens.json and in
this file, a spec only supplies content. check_visual.py runs first and the render refuses on errors, so an
image cannot leave the system. The hand-drawn wobble is seeded from the spec, so the same spec always
renders the same image. Chrome headless renders the SVG at 2x, then Pillow downsamples to 1200 wide.
Chrome is found from --chrome, $CHROME_PATH, PATH, then the usual macOS and Windows install paths.
"""
import argparse, hashlib, html, json, math, os, random, shutil, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_visual import check

HERE = os.path.dirname(os.path.abspath(__file__))
TOK = json.load(open(os.path.join(HERE, "tokens.json"), encoding="utf-8"))
C, S, ST, LY, F = TOK["colour"], TOK["size"], TOK["stroke"], TOK["layout"], TOK["font"]
CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
]

def find_chrome(explicit=None):
    """Return a Chrome or Chromium binary: --chrome, then $CHROME_PATH, then PATH, then the usual install paths."""
    for c in (explicit, os.environ.get("CHROME_PATH")):
        if c and os.path.exists(c): return c
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"):
        w = shutil.which(name)
        if w: return w
    for c in CHROME_CANDIDATES:
        if os.path.exists(c): return c
    return None
W = TOK["canvas"]["width"]; M = TOK["canvas"]["margin"]

# ---------- hand-drawn primitives ----------
class Hand:
    def __init__(self, seed): self.r = random.Random(seed)
    def j(self, a): return self.r.uniform(-a, a)
    def line(self, x1, y1, x2, y2, bow=None, amp=None):
        bow = ST["bow"] if bow is None else bow; amp = ST["wobble"] if amp is None else amp
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2; dx, dy = x2 - x1, y2 - y1; L = math.hypot(dx, dy) or 1; nx, ny = -dy / L, dx / L
        out = []
        for _ in range(2):
            b = self.j(bow); out.append(f"M{x1 + self.j(amp):.1f},{y1 + self.j(amp):.1f} Q{mx + nx * b:.1f},{my + ny * b:.1f} {x2 + self.j(amp):.1f},{y2 + self.j(amp):.1f}")
        return " ".join(out)
    def rect(self, x, y, w, h, rad=None):
        rad = ST["corner_radius"] if rad is None else rad
        d = [self.line(x + rad, y, x + w - rad, y), self.line(x + w, y + rad, x + w, y + h - rad), self.line(x + w - rad, y + h, x + rad, y + h), self.line(x, y + h - rad, x, y + rad)]
        for cx, cy, a0 in [(x + rad, y + rad, 180), (x + w - rad, y + rad, 270), (x + w - rad, y + h - rad, 0), (x + rad, y + h - rad, 90)]:
            p0 = (cx + rad * math.cos(math.radians(a0)), cy + rad * math.sin(math.radians(a0))); p1 = (cx + rad * math.cos(math.radians(a0 + 90)), cy + rad * math.sin(math.radians(a0 + 90)))
            d.append(f"M{p0[0]:.1f},{p0[1]:.1f} A{rad},{rad} 0 0 1 {p1[0]:.1f},{p1[1]:.1f}")
        return " ".join(d)
    def ellipse(self, cx, cy, rx, ry, n=28):
        out = []
        for _ in range(2):
            out.append(" ".join(f"{'M' if i == 0 else 'L'}{cx + rx * math.cos(2 * math.pi * i / n) + self.j(2):.1f},{cy + ry * math.sin(2 * math.pi * i / n) + self.j(2):.1f}" for i in range(n + 1)))
        return " ".join(out)
    def head(self, x2, y2, ang, size=18):
        a1, a2 = ang + math.radians(155), ang - math.radians(155)
        return f"M{x2:.1f},{y2:.1f} L{x2 + size * math.cos(a1) + self.j(1.5):.1f},{y2 + size * math.sin(a1) + self.j(1.5):.1f} M{x2:.1f},{y2:.1f} L{x2 + size * math.cos(a2) + self.j(1.5):.1f},{y2 + size * math.sin(a2) + self.j(1.5):.1f}"
    def arrow(self, x1, y1, x2, y2, curve=0):
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2; dx, dy = x2 - x1, y2 - y1; L = math.hypot(dx, dy) or 1; nx, ny = -dy / L, dx / L
        cx, cy = mx + nx * curve, my + ny * curve; ang = math.atan2(y2 - cy, x2 - cx)
        return f"M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f} " + self.head(x2, y2, ang)
    def underline(self, x1, x2, y, n=8):
        return "M%d,%d " % (x1, y) + " ".join(f"L{x1 + (x2 - x1) * i / n:.1f},{y + self.j(3):.1f}" for i in range(1, n + 1))
    def figure(self, cx, cy, scale=1.3, pose="down"):
        s = scale; hr = 22 * s; d = [self.ellipse(cx, cy, hr, hr, 20)]
        neck, hip = cy + hr, cy + hr + 70 * s; sh = cy + hr + 20 * s
        d += [self.line(cx, neck, cx, hip, 2), self.line(cx, hip, cx - 28 * s, hip + 55 * s, 2), self.line(cx, hip, cx + 28 * s, hip + 55 * s, 2)]
        arms = {"down": [(-32, 42), (32, 42)], "up": [(-34, -40), (34, -40)], "tap": [(-30, 40), (48, -12)], "walk": [(-36, 30), (30, 36)], "think": [(-30, 40), (18, -8)]}[pose]
        for ax, ay in arms: d.append(self.line(cx, sh, cx + ax * s, sh + ay * s, 2))
        return " ".join(d), hip + 55 * s

# ---------- svg helpers ----------
def esc(s): return html.escape(str(s))
def P(d, col, w, dash=None):
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{f" stroke-dasharray=\"{dash}\"" if dash else ""}/>'
def T(x, y, s, size, col, fam="hand", wt=400, anchor="start", italic=False):
    family = F["display"]["family"] if fam == "display" else F["hand"]["family"]
    return f'<text x="{x:.0f}" y="{y:.0f}" font-family="{family}, {F["fallback"]}" font-weight="{wt}" font-size="{size}" fill="{col}" text-anchor="{anchor}"{" font-style=\"italic\"" if italic else ""}>{esc(s)}</text>'
def width_of(s, size, fam="hand"): return len(str(s)) * size * (0.40 if fam == "display" else 0.52)

def person(h, spec, cx, cy):
    p = spec.get("person"); out = []
    if not p: return out
    d, foot = h.figure(cx, cy, 1.3, p.get("pose", "down")); out.append(P(d, C["matters"], ST["figure"]))
    if p.get("pose") == "tap":
        out.append(P(h.ellipse(cx + 118, cy + 36, 34, 22), C["matters"], 3)); out.append(T(cx + 118, cy + 44, "tap", 22, C["matters"], "hand", 700, "middle"))
    if p.get("label"): out.append(T(cx, foot + 56, p["label"], S["person_label"], C["matters"], "display", 700, "middle"))
    if p.get("aside"): out.append(T(cx, foot + 94, f"({p['aside']})", S["aside"], C["aside"], "hand", 300, "middle"))
    return out

def risk(h, spec, from_xy, cx, cy):
    r = spec.get("risk"); out = []
    if not r: return out
    out.append(P(h.ellipse(cx, cy, 200, 72), C["risk"], ST["risk"]))
    if r.get("head"): out.append(T(cx, cy - 8, r["head"], S["risk_head"], C["risk"], "hand", 400, "middle")); out.append(T(cx, cy + 30, r["body"], S["risk_body"], C["risk"], "display", 700, "middle"))
    else: out.append(T(cx, cy + 12, r["body"], S["risk_body"], C["risk"], "display", 700, "middle"))
    if from_xy: out.append(P(h.arrow(from_xy[0], from_xy[1], cx - 190, cy + 20, curve=-60), C["risk"], ST["risk"], ST["dash"]))
    if r.get("aside"): out.append(T(cx, cy + 112, f"({r['aside']})", S["aside"], C["aside"], "hand", 300, "middle"))
    return out

def frame(h, spec, H, body):
    out = [f'<rect width="{W}" height="{H}" fill="{C["paper"]}"/>']
    title = spec["title"]; out.append(T(M, LY["title_y"], title, S["title"], C["ink"], "display", 700))
    out.append(P(h.underline(M, M + min(width_of(title, S["title"], "display"), W - 2 * M), LY["title_y"] + 22), C["matters"], ST["underline"]))
    if spec.get("subtitle"): out.append(T(M + 2, LY["subtitle_y"], spec["subtitle"], S["subtitle"], C["aside"], "hand", 300, italic=True))
    out += body
    ty = H - LY["takeaway_bottom"] - LY["takeaway_height"]
    out.append(P(h.rect(M, ty, W - 2 * M, LY["takeaway_height"], 14), C["ink"], ST["box"]))
    out.append(T(W / 2, ty + LY["takeaway_height"] / 2 + 14, spec["takeaway"], S["takeaway"], C["ink"], "display", 700, "middle"))
    out.append(T(W - M, H - 50, spec.get("signature", TOK["grammar"]["signature_default"]), S["signature"], C["aside"], "hand", 300, "end"))
    return out

# ---------- types ----------
def r_boxes(h, spec, H):
    bx = spec["boxes"]; n = len(bx); out = []
    side = bool(spec.get("person") or spec.get("risk")); layout = spec.get("layout", "stack")
    top = LY["flow_top"]; bottom = H - LY["takeaway_bottom"] - LY["takeaway_height"] - 60
    pos = {}
    if layout == "row":
        gap = 60; bw = (W - 2 * M - gap * (n - 1)) // n; bh = 150; y = top + 80
        for i, b in enumerate(bx): pos[b["id"]] = (M + i * (bw + gap), y, bw, bh)
    else:
        bw = LY["box_width_with_margin_column"] if side else LY["box_width_full"]; bh = LY["box_height"]
        x = M if side else (W - bw) // 2; avail = bottom - top; gap = min(110, (avail - n * bh) // max(n - 1, 1))
        y0 = top + (avail - (n * bh + (n - 1) * gap)) // 2
        for i, b in enumerate(bx): pos[b["id"]] = (x, y0 + i * (bh + gap), bw, bh)
    acc_y = None
    for b in bx:
        x, y, bw, bh = pos[b["id"]]; col = C["matters"] if b.get("matters") else C["ink"]
        if b.get("matters"): acc_y = y
        out.append(P(h.rect(x, y, bw, bh), col, ST["box"])); out.append(T(x + 26, y + 52, b["label"], S["label"], col, "display", 600))
        if b.get("line"): out.append(T(x + 26, y + 92, b["line"], S["line"], C["ink"] if b.get("matters") else C["aside"], "hand", 300))
    for a in spec.get("arrows", []):
        fx, fy, fw, fh = pos[a["from"]]; tx, ty, tw, th = pos[a["to"]]; to_m = next(b for b in bx if b["id"] == a["to"]).get("matters")
        col = C["matters"] if to_m else C["ink"]
        if layout == "row": x1, y1, x2, y2 = fx + fw + 6, fy + fh / 2, tx - 8, ty + th / 2
        else: x1, y1, x2, y2 = fx + fw / 2, fy + fh + 6, tx + tw / 2, ty - 8
        out.append(P(h.arrow(x1, y1, x2, y2), col, ST["arrow"]))
        if a.get("label"):
            if layout == "row": out.append(T((x1 + x2) / 2, y1 - 24, a["label"], S["arrow_label"], C["aside"], "hand", 300, "middle"))
            else: out.append(T(x1 + 22, (y1 + y2) / 2 + 8, a["label"], S["arrow_label"], C["aside"], "hand", 300))
    if side and layout == "stack":
        rx = M + LY["box_width_with_margin_column"]; cx = rx + (W - M - rx) / 2
        if spec.get("risk"):
            fr = pos.get(spec["risk"].get("from"), None); from_xy = (fr[0] + fr[2] + 10, fr[1] + fr[3] / 2) if fr else None
            out += risk(h, spec, from_xy, cx, top + 110)
        if spec.get("person"):
            py = (acc_y - 70) if acc_y else (top + 400)
            if spec.get("risk") and py < top + 330: py = top + 330
            out += person(h, spec, cx, py)
    elif spec.get("person"):
        out += person(h, spec, W - M - 160, bottom - 330)
    for i, a in enumerate(spec.get("asides", [])): out.append(T(M + 2, bottom - 10 - i * 34, f"({a})", S["aside"], C["aside"], "hand", 300))
    return out

def r_number(h, spec, H):
    out = []; top = LY["flow_top"] + 20
    out.append(T(M, top + 270, spec["value"], S["number"], C["matters"], "display", 700))
    out.append(P(h.underline(M, M + width_of(spec["value"], S["number"], "display") * 1.05, top + 300, 6), C["matters"], 5))
    out.append(T(M + 4, top + 370, spec["unit"], S["unit"], C["ink"], "display", 600))
    if spec.get("how"):
        words = spec["how"].split(); lines, cur = [], ""
        for w in words:
            if width_of(cur + " " + w, S["how"]) > 640: lines.append(cur); cur = w
            else: cur = (cur + " " + w).strip()
        lines.append(cur)
        out.append(P(h.line(M, top + 420, M, top + 430 + 44 * len(lines), 3), C["matters"], 4))
        for i, l in enumerate(lines): out.append(T(M + 28, top + 455 + i * 44, l, S["how"], C["ink"], "hand", 300))
    if spec.get("person"): out += person(h, spec, W - M - 170, top + 120)
    out += risk(h, spec, None, W - M - 220, top + 560) if spec.get("risk") else []
    for i, a in enumerate(spec.get("asides", [])): out.append(T(M + 2, H - LY["takeaway_bottom"] - LY["takeaway_height"] - 70 - i * 34, f"({a})", S["aside"], C["aside"], "hand", 300))
    return out

def r_ladder(h, spec, H):
    st = spec["steps"]; n = len(st); out = []
    top = LY["flow_top"]; bottom = H - LY["takeaway_bottom"] - LY["takeaway_height"] - 70
    side = bool(spec.get("person")); sw = (W - 2 * M) - (260 if side else 0); indent = 70
    avail = bottom - top; sh = max(120, min(150, (avail - 60 * (n - 1)) // n)); gap = max(30, min(60, (avail - n * sh) // max(n - 1, 1)))
    y0 = top + (avail - (n * sh + (n - 1) * gap)) // 2
    acc = None
    for i, s in enumerate(reversed(st)):
        rung = n - i; y = y0 + i * (sh + gap); x = M + (n - 1 - i) * indent; w = sw - (n - 1 - i) * indent
        col = C["matters"] if s.get("matters") else C["ink"]
        if s.get("matters"): acc = (x + w, y)
        out.append(P(h.rect(x, y, w, sh), col, ST["box"])); out.append(T(x + 24, y + 48, str(rung), 26, C["aside"], "hand", 700))
        out.append(T(x + 70, y + 52, s["label"], S["step"], col, "display", 600))
        if s.get("line"): out.append(T(x + 70, y + 90, s["line"], S["step_line"], C["aside"] if not s.get("matters") else C["ink"], "hand", 300))
    if side:
        cx = W - M - 120; cy = (acc[1] - 40) if acc else top + 200; out += person(h, spec, cx, cy)
    out += risk(h, spec, None, W - M - 220, top - 20) if (spec.get("risk") and not side) else []
    for i, a in enumerate(spec.get("asides", [])): out.append(T(M + 2, bottom + 40 - i * 34, f"({a})", S["aside"], C["aside"], "hand", 300))
    return out

def r_compare(h, spec, H):
    out = []; top = LY["flow_top"]; colw = (W - 2 * M - 60) / 2
    for k, side in enumerate(("left", "right")):
        c = spec[side]; x = M + k * (colw + 60); col = C["matters"] if c.get("matters") else C["ink"]
        out.append(T(x, top + 30, c["title"], S["compare_head"], col, "display", 700))
        out.append(P(h.underline(x, x + min(width_of(c["title"], S["compare_head"], "display"), colw), top + 50), col, ST["underline"]))
        for i, it in enumerate(c["items"]):
            y = top + 120 + i * 96; out.append(P(h.line(x, y - 10, x + 22, y - 10, 1), col, 3)); out.append(T(x + 38, y, it, S["compare_item"], C["ink"], "hand", 300 if not c.get("matters") else 400))
    nmax = max(len(spec["left"]["items"]), len(spec["right"]["items"])); list_end = top + 120 + nmax * 96 - 50
    mid = W / 2; out.append(P(h.line(mid, top, mid, list_end, 6, 3), C["aside"], 2, "2 14"))
    if spec.get("person"):
        side_m = "right" if spec["right"].get("matters") else "left"; x = M + (colw + 60) * (1 if side_m == "right" else 0) + colw / 2
        out += person(h, spec, x, list_end + 70)
    for i, a in enumerate(spec.get("asides", [])): out.append(T(M + 2, H - LY["takeaway_bottom"] - LY["takeaway_height"] - 60 - i * 34, f"({a})", S["aside"], C["aside"], "hand", 300))
    return out

RENDER = {"boxes": r_boxes, "number": r_number, "ladder": r_ladder, "compare": r_compare}

def font_css():
    css = []
    for key in ("display", "hand"):
        for wt, rel in F[key]["files"].items():
            p = os.path.join(HERE, rel)
            if os.path.exists(p): css.append(f"@font-face{{font-family:'{F[key]['family']}';font-weight:{wt};src:url('{Path(p).as_uri()}') format('truetype');}}")
    return "".join(css)

def build_html(spec, H):
    seed = int(hashlib.sha1(json.dumps(spec, sort_keys=True).encode()).hexdigest()[:8], 16)
    h = Hand(seed); body = RENDER[spec["type"]](h, spec, H)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(frame(h, spec, H, body))}</svg>'
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}*{{margin:0}}body{{width:{W}px;height:{H}px;overflow:hidden;background:{C["paper"]}}}</style></head><body>{svg}</body></html>'

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("spec"); ap.add_argument("--out"); ap.add_argument("--square", action="store_true"); ap.add_argument("--keep-html", action="store_true"); ap.add_argument("--chrome", help="path to a Chrome or Chromium binary")
    a = ap.parse_args()
    try: from PIL import Image
    except ImportError: raise SystemExit("Pillow is missing: pip install -r requirements.txt")
    spec = json.load(open(a.spec, encoding="utf-8"))
    errors, warnings = check(spec)
    for w in warnings: print("warning:", w, file=sys.stderr)
    if errors:
        for e in errors: print("error:", e, file=sys.stderr)
        raise SystemExit("spec breaks the Whiteboard system; fix the spec (see check_visual.py)")
    H = TOK["canvas"]["square_height"] if a.square else TOK["canvas"]["height"]
    out = a.out or os.path.splitext(a.spec)[0] + ".png"; html_path = os.path.splitext(out)[0] + ".html"
    open(html_path, "w", encoding="utf-8").write(build_html(spec, H))
    chrome = find_chrome(a.chrome)
    if not chrome: raise SystemExit("Chrome or Chromium not found: install it, set CHROME_PATH or pass --chrome")
    profile = tempfile.mkdtemp(prefix="livis"); raw = out + ".2x.png"
    try:
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run", "--allow-file-access-from-files", f"--user-data-dir={profile}", "--force-device-scale-factor=2", f"--window-size={W},{H}", f"--screenshot={raw}", "--virtual-time-budget=3000", Path(html_path).resolve().as_uri()], check=True, capture_output=True, timeout=90)
    finally: shutil.rmtree(profile, ignore_errors=True)
    im = Image.open(raw).convert("RGB").resize((W, H), Image.LANCZOS); im.save(out, optimize=True); os.remove(raw)
    if not a.keep_html: os.remove(html_path)
    print(out)

if __name__ == "__main__": main()
