#!/usr/bin/env python3
"""Build a two-page CV (HTML, PDF, DOCX) from a Markdown CV source.

Usage:
    python3 build_cv.py "<path to CV markdown>" [--paper A4|Letter] [--no-docx] [--no-fill] [--rules rules.json]

Needs Google Chrome (or Chromium), poppler (pdfinfo, pdftotext, pdftoppm), PyMuPDF and python-docx.
Set CHROME_PATH if Chrome is not in its usual place. The build stops with an error rather than skip
a check it cannot run.

Outputs land next to the markdown with the same base name:
    <name>.html   the designed page (open in a browser to tweak)
    <name>.pdf    rendered by headless Chrome, what you upload
    <name>.docx   editable Word copy (same content, simpler styling)
    <name>.preview-1.png ... one PNG per page, for a visual check

Spacing (both pages of a two-page CV are full, never a page and a half): by default the script
renders the CV at every step from the tight design spacing to the airiest allowed, keeps the step
whose pages all run closest to the foot without adding a page, and fails (exit 4) if a page still
stops short. --line-height or --gap fix the spacing by hand (never tighter than the design);
--no-fill keeps the tight design. Margins are 2 cm on every side and cannot be changed from the
command line.

Rules the build enforces: body text at 10 pt or more (refused below, exit 3 if Chrome shrinks it),
the page count (exit 2 over, exit 4 under), every page at least 95% full (exit 4), and, with
--rules, any required descriptor for a named organisation (refused without it, exit 5).

Markdown dialect (see examples/alex-morgan-cv.md):
    # Name                                  one H1, the candidate's name
    contact line                            first paragraph after the H1
    ## Section                              section heading
    ### Org, Location | descriptor          entry header (descriptor optional)
    **Title** · dates                       role row; last " · " segment is right-aligned
    plain line under an entry               small grey note (earlier roles, honours)
    - bullet                                bullet (supports **bold**)
    <!-- page break -->                     start a new page here, in the PDF and the Word copy
    ---                                     everything after the first rule below the
                                            front matter is ignored (held-back notes)
"""
import argparse, html, json, math, os, pathlib, platform, re, shutil, subprocess, sys, tempfile

def find_chrome():
    """CHROME_PATH wins. Otherwise the usual install place for this OS, then anything on the PATH."""
    env = os.environ.get("CHROME_PATH")
    if env:
        return env
    defaults = {
        "Darwin": ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                   "/Applications/Chromium.app/Contents/MacOS/Chromium"],
        "Windows": [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"],
    }.get(platform.system(), [])
    for p in defaults:
        if os.path.exists(p):
            return p
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"):
        found = shutil.which(name)
        if found:
            return found
    return defaults[0] if defaults else "google-chrome"

CHROME = find_chrome()

# Readability floor: body text never below 10 pt, every CV two pages.
# A CV that does not fit is cut, never shrunk.
MIN_BASE_SIZE = 10.0
MAX_BASE_SIZE = 10.5         # bigger type would pad a short CV instead of adding a true line
MAX_WORDS = 1150
PAGES = 2                    # every text CV; the one-page version is the dashboard CV

# Full pages: a two-page CV runs to the foot of page 2 as well as page 1.
# Air is added along one path, from the tight design (spread 0) to the airiest allowed (spread 1),
# and the build fails if any page stops short of FILL_MIN of its printable height.
FILL_MIN = 0.95
MARGIN_MM = 20               # every side: 2 cm all round, the common "Normal" Word margin
PAGE_BREAK = re.compile(r"^\s*<!--\s*page\s*break\s*-->\s*$", re.I)
LINE_HEIGHT = (1.25, 1.40)   # line height at spread 0 and at spread 1
GAP = (1.0, 3.0)             # gap multiplier at spread 0 and at spread 1
SPREAD_STEPS = 20
SPLIT_MIN_BULLETS = 5        # a role with at least this many bullets may break across a page between bullets

# Required descriptors (optional, --rules): some organisations must always carry a set phrase,
# for example a firm that asks to be described the same way on every CV. A rules file is JSON:
#   {"required_descriptors": [{"org": "Northwind Retail", "phrase": "a national homewares retailer"}]}
# "org" is matched case-insensitively at the start of an entry header, ignoring **bold** markers
# and spaces inside the name.

def load_rules(path):
    if not path:
        return []
    with open(path, encoding="utf-8") as f:
        rules = json.load(f).get("required_descriptors", [])
    for r in rules:
        if not r.get("org") or not r.get("phrase"):
            sys.exit(f"REFUSED: every rule in {path} needs an org and a phrase.")
    return rules

def org_pattern(org):
    """Regex for an organisation name, tolerant of spacing ("Northwind Retail", "NorthwindRetail")."""
    return r"\s*".join(re.escape(ch) for ch in org.replace(" ", ""))

def names_org(header, org):
    """True for an entry header naming org, however it is styled (**Org**), and not a longer name."""
    return re.match(r"\W*" + org_pattern(org) + r"(?![\w])", re.sub(r"[*_]", "", header), re.I) is not None

# ------------------------------------------------------------------ parsing

def strip_front_matter(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:]
    return text

def cv_body(md):
    """The CV itself: front matter dropped, and everything after the first horizontal rule (held-back notes)."""
    body = strip_front_matter(md)
    cut = re.search(r"^ {0,3}([-*_])[ \t]*(?:\1[ \t]*){2,}$", body, re.M)  # ---, ***, ___ or spaced forms
    return body[:cut.start()] if cut else body

def descriptor_problems(md, doc, rules):
    """Places where the CV names a ruled organisation without its phrase. Empty when the CV complies."""
    problems = []
    body = cv_body(md)
    for rule in rules:
        org, phrase = rule["org"], rule["phrase"].lower()
        found = False
        for sec in doc["sections"]:
            for it in sec["items"]:
                if it[0] == "entry" and names_org(it[1]["org"], org) and phrase not in it[1]["desc"].lower():
                    found = True
                    problems.append(f'the header "### {it[1]["org"]} | {it[1]["desc"]}" needs "{rule["phrase"]}"')
        if not found and re.search(org_pattern(org), body, re.I) and phrase not in body.lower():
            problems.append(f'the CV mentions {org} but never as "{rule["phrase"]}"')
    return problems

def parse(md):
    body = cv_body(md)
    doc = {"name": "", "contact": "", "sections": []}
    section = None
    entry = None
    para_buf = []

    def flush_para():
        nonlocal para_buf
        if not para_buf:
            return
        text = " ".join(s.strip() for s in para_buf).strip()
        para_buf = []
        if not text:
            return
        if not doc["name"]:
            return
        if not doc["contact"] and section is None:
            doc["contact"] = text
            return
        target = entry["items"] if entry else section["items"]
        left, right = text, ""
        if text.startswith("**") and " · " in text:
            l, r = text.rsplit(" · ", 1)
            if len(r) <= 24 and re.search(r"(19|20)\d\d|present", r):
                left, right = l, r
        if text.startswith("**") and (right or entry):
            target.append(("row", left, right))
        else:
            target.append(("note", text))

    for raw in body.splitlines():
        line = raw.rstrip()
        if PAGE_BREAK.match(line):
            flush_para()
            if section is not None:
                (entry["items"] if entry else section["items"]).append(("pagebreak",))
            continue
        if line.startswith("# "):
            flush_para(); doc["name"] = line[2:].strip(); continue
        if line.startswith("## "):
            flush_para(); entry = None
            section = {"title": line[3:].strip(), "items": []}
            doc["sections"].append(section); continue
        if line.startswith("### "):
            flush_para()
            head = line[4:].strip()
            org, desc = (head.split(" | ", 1) + [""])[:2]
            entry = {"org": org.strip(), "desc": desc.strip(), "items": []}
            section["items"].append(("entry", entry)); continue
        if line.startswith("- "):
            flush_para()
            target = entry["items"] if entry else section["items"]
            target.append(("bullet", line[2:].strip())); continue
        if not line.strip():
            flush_para(); continue
        if line.lstrip().startswith("**") or (para_buf and para_buf[0].lstrip().startswith("**")):
            flush_para()
        para_buf.append(line)
    flush_para()
    return doc

# ------------------------------------------------------------------ inline

EXAM = r"[A-Z]{2,3}-\d{3}"

def keep_codes(t):
    """Exam codes such as AZ-900 never split at the hyphen, wherever they sit (in brackets, before a comma,
    inside bold). In a list split by " · ", a short certification ending in a code, such as "Azure
    Fundamentals (AZ-900)", also stays whole on one line, and a long one keeps its last word with the
    code. t is escaped HTML with the **bold** markers still in it. A span never crosses the edge of a bold
    run, so the tags always nest."""
    runs = [m.span() for m in re.finditer(r"\*\*(.+?)\*\*", t)]
    def crosses(a, b):
        return any(s < a < e < b or a < s < b < e for s, e in runs)
    out, pos = [], 0
    for seg in t.split(" · "):
        a, b = pos, pos + len(seg)
        pos = b + len(" · ")
        m = re.search(r"([^\s*]+ )?\(" + EXAM + r"\)$", seg)
        if m and len(seg.replace("**", "")) <= 45 and not crosses(a, b):
            seg = f'<span class="nw">{seg}</span>'
        elif m and not crosses(a + m.start(), b):
            seg = seg[:m.start()] + f'<span class="nw">{m.group(0)}</span>'
        out.append(seg)
    t = " · ".join(out)
    return re.sub(r"(?<![A-Za-z0-9])(" + EXAM + r")(?![0-9])", r'<span class="nw">\1</span>', t)

def inline_html(text):
    t = keep_codes(html.escape(text, quote=False))
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<!\w)\*(.+?)\*(?!\w)", r"<i>\1</i>", t)
    return t

def inline_runs(text):
    """Yield (text, bold, italic) for python-docx."""
    pos = 0
    for m in re.finditer(r"\*\*(.+?)\*\*|(?<!\w)\*(.+?)\*(?!\w)", text):
        if m.start() > pos:
            yield text[pos:m.start()], False, False
        if m.group(1) is not None:
            yield m.group(1), True, False
        else:
            yield m.group(2), False, True
        pos = m.end()
    if pos < len(text):
        yield text[pos:], False, False

# ------------------------------------------------------------------ HTML

CSS = """
@page { size: %(paper)s; margin: %(m)smm; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: %(base)spt; line-height: %(lh)s; color: #1f2328;
  -webkit-print-color-adjust: exact; print-color-adjust: exact;
  /* no fi/fl ligatures: some parsers read them as single symbols and miss "benefits" or "workflow" */
  font-variant-ligatures: none; font-feature-settings: "liga" 0, "clig" 0;
}
.page { padding: 0; }
h2 { break-after: avoid; }
li, .row, .org, .note { break-inside: avoid; }
.entry:not(.split) { break-inside: avoid; }
.org, .entry > .row:not(:last-child), .entry > p.note:not(:last-child) { break-after: avoid; }
.row.later { break-before: avoid; }
.row + .row { margin-top: 2.2pt; }  /* stacked titles stay paired with their dates when an ATS reads the text */
.row + .row + ul { margin-top: 3pt; }
.nw { white-space: nowrap; }
.pagebreak { break-before: page; height: 0; margin: 0; }
header { border-bottom: 1.4pt solid #163a5c; padding-bottom: 4pt; margin-bottom: 4pt; }
h1 { font-family: Georgia, "Times New Roman", serif; font-weight: normal; font-size: 23pt;
  letter-spacing: 0.3pt; margin: 0 0 2pt 0; color: #163a5c; line-height: 1.1; }
.contact { font-size: 8.6pt; color: #4b5563; line-height: 1.35; }
.contact span { white-space: nowrap; }
.contact .sep { color: #9aa5b1; padding: 0 3pt; }
h2 { font-size: 8pt; letter-spacing: 0.6pt; font-kerning: none; font-feature-settings: "kern" 0, "liga" 0; text-transform: uppercase; color: #163a5c;
  font-weight: 700; margin: 7pt 0 3pt 0; padding-bottom: 1.5pt; border-bottom: 0.5pt solid #b7c3d1; }
h2:first-of-type { margin-top: 2pt; }
p { margin: 0 0 2pt 0; }
.entry { margin-top: 3.8pt; }
.entry:first-child { margin-top: 1pt; }
.org { font-weight: 700; font-size: %(org)spt; color: #111; }
.org .desc { font-weight: 400; color: #4b5563; }
.org .desc::before { content: "\\2009\\00B7\\2009"; color: #9aa5b1; }
.row { display: flex; justify-content: space-between; align-items: baseline; gap: 8pt; }
.row .left { flex: 1 1 auto; }
.row .right { flex: 0 0 auto; font-size: 8.4pt; color: #4b5563; white-space: nowrap; font-variant-numeric: tabular-nums; }
.note { font-size: 8.6pt; color: #4b5563; margin: 0.5pt 0 1.5pt 0; }
ul { margin: 1.2pt 0 0 0; padding-left: 9pt; }
li { margin: 0 0 1.2pt 0; padding-left: 1.5pt; }
li::marker { color: #163a5c; font-size: 0.85em; }
.skills p { line-height: 1.45; }
.sep { color: #9aa5b1; padding: 0 3.5pt; }
"""

def section_html(sec):
    out = [f"<h2>{inline_html(sec['title'])}</h2>"]
    cls = "skills" if "skill" in sec["title"].lower() else "sec"
    out.append(f'<div class="{cls}">')
    out.append(items_html(sec["items"], top=True))
    out.append("</div>")
    return "\n".join(out)

def items_html(items, top=False):
    out, bullets = [], []
    after_list = False  # a role row after a bullet list takes the last bullet with it, so no page opens on a stray title
    def flush():
        nonlocal bullets, after_list
        if bullets:
            out.append("<ul>" + "".join(f"<li>{inline_html(b)}</li>" for b in bullets) + "</ul>")
            bullets = []
            after_list = True
    for it in items:
        kind = it[0]
        if kind == "bullet":
            bullets.append(it[1]); continue
        flush()
        if kind == "pagebreak":
            out.append('<div class="pagebreak"></div>'); continue
        if kind == "entry":
            e = it[1]
            desc = f'<span class="desc">{inline_html(e["desc"])}</span>' if e["desc"] else ""
            long_role = sum(1 for x in e["items"] if x[0] == "bullet") >= SPLIT_MIN_BULLETS
            out.append(f'<div class="entry{" split" if long_role else ""}"><div class="org">{inline_html(e["org"])}{desc}</div>')
            out.append(items_html(e["items"]))
            out.append("</div>")
        elif kind == "row":
            later = " later" if after_list and not top else ""
            out.append(f'<div class="row{later}"><div class="left">{inline_html(it[1])}</div>'
                       f'<div class="right">{inline_html(it[2])}</div></div>')
        elif kind == "note":
            text = it[1]
            if top and " · " in text and "**" not in text:
                parts = [inline_html(p.strip()) for p in text.split(" · ")]
                # <wbr> lets a line end after a dot; without it "word·Word" cannot break and lines wrap early
                text_html = '<span class="sep">·</span><wbr>'.join(parts)
                out.append(f"<p>{text_html}</p>")
            else:
                klass = "note" if not top else ""
                out.append(f'<p class="{klass}">{inline_html(text)}</p>')
    flush()
    return "\n".join(out)

def spacing_css(gap):
    """Scale the vertical gaps between sections, entries and bullets. 1.0 keeps the default design."""
    if gap == 1.0:
        return ""
    return (f"h2 {{ margin: {7*gap:.2f}pt 0 {3*gap:.2f}pt 0; }} h2:first-of-type {{ margin-top: {2*gap:.2f}pt; }}"
            f" .entry {{ margin-top: {3.8*gap:.2f}pt; }} li {{ margin-bottom: {1.2*gap:.2f}pt; }}"
            f" header {{ padding-bottom: {4*gap:.2f}pt; margin-bottom: {4*gap:.2f}pt; }}")

def build_html(doc, paper, base, org, lh=LINE_HEIGHT[0], gap=GAP[0]):
    # <wbr> after each separator lets a long contact line wrap; without it Chrome scales the whole page down to fit
    contact = '<span class="sep">·</span><wbr>'.join(f"<span>{inline_html(p.strip())}</span>" for p in doc["contact"].split(" · "))
    paper_css = "A4" if paper == "A4" else "Letter"
    parts = [
        "<!doctype html><html><head><meta charset='utf-8'>",
        f"<title>{html.escape(doc['name'])} CV</title>",
        "<style>", CSS % {"paper": paper_css, "base": base, "org": org, "lh": lh, "m": MARGIN_MM}, spacing_css(gap), "</style></head><body><div class='page'>",
        f"<header><h1>{inline_html(doc['name'])}</h1><div class='contact'>{contact}</div></header>",
    ]
    parts += [section_html(s) for s in doc["sections"]]
    parts.append("</div></body></html>")
    return "\n".join(parts)

# ------------------------------------------------------------------ PDF

def render_pdf(html_path, pdf_path):
    """Print the HTML to PDF with headless Chrome and return the page count (0 when Chrome is missing).
    Raises subprocess.SubprocessError if Chrome fails, hangs or writes no PDF."""
    if not os.path.exists(CHROME):
        print(f"Chrome not found at {CHROME}; no PDF", file=sys.stderr); return 0
    if os.path.exists(pdf_path):
        os.remove(pdf_path)  # an old PDF must never stand in for a render that failed
    profile = tempfile.mkdtemp(prefix="cvchrome")
    try:
        # as_uri() percent-encodes the path: a raw "#" or "?" in a folder name makes Chrome load nothing
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--user-data-dir={profile}", f"--print-to-pdf={pdf_path}",
                        pathlib.Path(html_path).resolve().as_uri()],
                       check=True, capture_output=True, timeout=90)
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
        raise subprocess.SubprocessError(f"Chrome wrote no PDF for {html_path}")
    return pdf_pages(pdf_path)

def pdf_body_size(pdf_path):
    """Most common font size actually printed in the PDF (catches Chrome shrink-to-fit)."""
    try:
        import fitz, collections
    except ImportError:
        return 0
    sizes = collections.Counter()
    for page in fitz.open(pdf_path):
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    sizes[round(span["size"], 2)] += len(span["text"].strip())  # 2 decimals: a 9.84 pt shrink must not read as 10
    return sizes.most_common(1)[0][0] if sizes else 0

def pdf_words(pdf_path):
    try:
        out = subprocess.run(["pdftotext", pdf_path, "-"], capture_output=True, text=True).stdout
        return len(out.split())
    except FileNotFoundError:
        return 0

def pdf_pages(pdf_path):
    try:
        out = subprocess.run(["pdfinfo", pdf_path], capture_output=True, text=True).stdout
        m = re.search(r"Pages:\s+(\d+)", out)
        if m:
            return int(m.group(1))
    except FileNotFoundError:
        pass
    with open(pdf_path, "rb") as f:
        return len(re.findall(rb"/Type\s*/Page[^s]", f.read()))

def page_fills(pdf_path):
    """How far down each page the text reaches, as a share of the printable height between the
    2 cm margins (1.0 = the bottom margin). main() checks that PyMuPDF is installed before any build."""
    import fitz
    mm = 72 / 25.4
    fills = []
    for page in fitz.open(pdf_path):
        top, bottom = MARGIN_MM * mm, page.rect.height - MARGIN_MM * mm
        ys = [b["bbox"][3] for b in page.get_text("dict")["blocks"]
              if b.get("type") == 0 and any(s["text"].strip() for l in b["lines"] for s in l["spans"])]
        fills.append(round((max(ys) - top) / (bottom - top), 3) if ys else 0.0)
    return fills

def spread(s):
    """Line height and gap multiplier for a spread between 0 (tight design) and 1 (airiest allowed)."""
    return (round(LINE_HEIGHT[0] + (LINE_HEIGHT[1] - LINE_HEIGHT[0]) * s, 3),
            round(GAP[0] + (GAP[1] - GAP[0]) * s, 3))

def pct(f):
    """A fill as a whole percent, rounded down, so a page at 94.8% never prints as a passing 95%."""
    return f"{int(round(f * 1000)) // 10}%"

def fit_spacing(doc, a):
    """Render every spread step and keep the one whose pages are fullest without adding a page.
    Returns {s, lh, gap, pages, fills, fits, failed}. fits is False when no step gives exactly PAGES pages;
    the nearest step comes back so the preview shows the problem and the checks in main() fail it.
    failed counts steps that did not render even on a second try. Returns None when no step rendered."""
    from concurrent.futures import ThreadPoolExecutor
    work = tempfile.mkdtemp(prefix="cvfit")
    def trial(i):
        s = i / SPREAD_STEPS
        lh, gap = spread(s)
        h = os.path.join(work, f"spread{i:02d}.html")
        with open(h, "w", encoding="utf-8") as f:
            f.write(build_html(doc, a.paper, a.base_size, a.org_size, lh, gap))
        try:
            pages = render_pdf(h, h[:-5] + ".pdf")
        except (subprocess.SubprocessError, OSError):
            pages = 0  # a failed or hung render drops this one step, not the whole build
        fills = page_fills(h[:-5] + ".pdf") if pages else []
        return {"i": i, "s": s, "lh": lh, "gap": gap, "pages": pages, "fills": fills}
    try:
        with ThreadPoolExecutor(max_workers=4) as ex:
            results = list(ex.map(trial, range(SPREAD_STEPS + 1)))
            retry = [r["i"] for r in results if not r["fills"]]
            if retry:  # one more try for steps whose render failed or hung
                again = {r["i"]: r for r in ex.map(trial, retry)}
                results = [again.get(r["i"], r) for r in results]
    finally:
        shutil.rmtree(work, ignore_errors=True)
    trials = [t for t in results if t["fills"]]
    failed = len(results) - len(trials)
    if failed:
        print(f"WARNING: {failed} of {len(results)} spacing steps did not render, even on a second try, and were skipped.",
              file=sys.stderr)
    if not trials:
        return None
    fitting = [t for t in trials if t["pages"] == PAGES]
    if fitting:
        return dict(max(fitting, key=lambda t: (min(t["fills"]), -t["s"])), fits=True, failed=failed)
    # Too long even at the tight design, or too short even at the airiest: build the nearest.
    too_short = all(t["pages"] < PAGES for t in trials)
    return dict(trials[-1] if too_short else trials[0], fits=False, failed=failed)

def render_previews(pdf_path, base_path):
    if shutil.which("pdftoppm") is None:
        return []
    for old in os.listdir(os.path.dirname(base_path) or "."):
        if old.startswith(os.path.basename(base_path) + ".preview-"):
            os.remove(os.path.join(os.path.dirname(base_path) or ".", old))
    subprocess.run(["pdftoppm", "-r", "80", "-png", pdf_path, base_path + ".preview"], check=True)
    d = os.path.dirname(base_path) or "."
    return sorted(os.path.join(d, f) for f in os.listdir(d)
                  if f.startswith(os.path.basename(base_path) + ".preview-"))

# ------------------------------------------------------------------ DOCX

def build_docx(doc, path, paper):
    from docx import Document
    from docx.shared import Pt, Mm, RGBColor, Inches
    from docx.enum.text import WD_TAB_ALIGNMENT, WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    NAVY = RGBColor(0x16, 0x3A, 0x5C); GREY = RGBColor(0x4B, 0x55, 0x63)
    d = Document()
    sec = d.sections[0]
    if paper == "A4":
        sec.page_width, sec.page_height = Mm(210), Mm(297)
    else:
        sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    sec.top_margin = sec.bottom_margin = sec.left_margin = sec.right_margin = Mm(MARGIN_MM)
    text_width = sec.page_width - sec.left_margin - sec.right_margin

    normal = d.styles["Normal"]
    normal.font.name = "Calibri"; normal.font.size = Pt(10.5)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    normal.paragraph_format.space_after = Pt(1.5)
    normal.paragraph_format.line_spacing = 1.05

    def bottom_border(p, sz=4, color="163A5C", space=1):
        pPr = p._p.get_or_add_pPr()
        pbdr = OxmlElement("w:pBdr"); b = OxmlElement("w:bottom")
        for k, v in (("w:val", "single"), ("w:sz", str(sz)), ("w:space", str(space)), ("w:color", color)):
            b.set(qn(k), v)
        pbdr.append(b); pPr.append(pbdr)

    def add_runs(p, text, size=None, color=None, bold=None):
        for t, b, i in inline_runs(text):
            r = p.add_run(t); r.bold = b or bool(bold); r.italic = i
            if size: r.font.size = Pt(size)
            if color: r.font.color.rgb = color
        return p

    # header
    p = d.add_paragraph(); r = p.add_run(doc["name"])
    r.font.name = "Georgia"; r.font.size = Pt(20); r.font.color.rgb = NAVY
    p.paragraph_format.space_after = Pt(0)
    p = d.add_paragraph(); add_runs(p, doc["contact"], size=8.5, color=GREY)
    p.paragraph_format.space_after = Pt(4); bottom_border(p, sz=12, space=3)

    def heading(title):
        p = d.add_paragraph(); r = p.add_run(title.upper())
        r.bold = True; r.font.size = Pt(8); r.font.color.rgb = NAVY
        rPr = r._r.get_or_add_rPr(); sp = OxmlElement("w:spacing"); sp.set(qn("w:val"), "28"); rPr.append(sp)
        p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(2)
        bottom_border(p, sz=4, color="B7C3D1", space=1)

    def row(left, right):
        p = d.add_paragraph()
        p.paragraph_format.tab_stops.add_tab_stop(text_width, WD_TAB_ALIGNMENT.RIGHT)
        add_runs(p, left)
        if right:
            r = p.add_run("\t" + right); r.font.size = Pt(8.5); r.font.color.rgb = GREY
        p.paragraph_format.space_after = Pt(0.5)

    def bullet(text):
        p = d.add_paragraph(style="List Bullet")
        p.paragraph_format.left_indent = Mm(4); p.paragraph_format.first_line_indent = Mm(-3)
        p.paragraph_format.space_after = Pt(1)
        add_runs(p, text)

    # A page-break marker takes effect on the first paragraph added after it, wherever that is:
    # the next row or bullet, the next employer, or the next section heading.
    pending = [None]
    def mark():
        if pending[0] is not None and len(d.paragraphs) > pending[0]:
            d.paragraphs[pending[0]].paragraph_format.page_break_before = True
            pending[0] = None

    def items(its, top=False):
        for it in its:
            k = it[0]
            if k == "pagebreak":
                pending[0] = len(d.paragraphs); continue
            if k == "entry":
                e = it[1]
                p = d.add_paragraph(); p.paragraph_format.space_before = Pt(3.5); p.paragraph_format.space_after = Pt(0.5)
                r = p.add_run(e["org"]); r.bold = True; r.font.size = Pt(11)
                if e["desc"]:
                    r2 = p.add_run("  ·  " + e["desc"]); r2.font.color.rgb = GREY
                mark()
                items(e["items"])
            elif k == "row":
                row(it[1], it[2])
            elif k == "bullet":
                bullet(it[1])
            elif k == "note":
                p = d.add_paragraph()
                if top:
                    add_runs(p, it[1])
                else:
                    add_runs(p, it[1], size=8.5, color=GREY)
                p.paragraph_format.space_after = Pt(1)
            mark()

    for s in doc["sections"]:
        heading(s["title"]); mark(); items(s["items"], top=True)
    d.core_properties.title = f"{doc['name']} CV"; d.core_properties.author = doc["name"]
    d.save(path)

# ------------------------------------------------------------------ main

class Args(argparse.ArgumentParser):
    def error(self, message):
        # argparse exits 2 by default, and exit 2 here means "the CV runs over two pages"
        self.print_usage(sys.stderr)
        sys.exit(f"REFUSED: {message}")

def main():
    sys.stdout.reconfigure(line_buffering=True)  # keep progress lines and warnings in the order they happen
    ap = Args()
    ap.add_argument("markdown"); ap.add_argument("--paper", default="A4", choices=["A4", "Letter"])
    ap.add_argument("--no-docx", action="store_true")
    ap.add_argument("--base-size", type=float, default=10.0, help=f"body font size in pt (HTML/PDF), {MIN_BASE_SIZE} to {MAX_BASE_SIZE}")
    ap.add_argument("--org-size", type=float, default=11.0, help=f"employer heading size in pt, never below {MIN_BASE_SIZE}")
    ap.add_argument("--line-height", type=float, default=None,
                    help=f"fix the line height by hand ({LINE_HEIGHT[0]} to {LINE_HEIGHT[1]}); turns off the fill search")
    ap.add_argument("--gap", type=float, default=None,
                    help=f"fix the multiplier for gaps between sections, roles and bullets by hand ({GAP[0]} to {GAP[1]}); turns off the fill search")
    ap.add_argument("--no-fill", action="store_true", help="keep the tight design spacing instead of spreading it so every page is full")
    ap.add_argument("--max-pages", type=int, default=PAGES, help=f"kept for old commands; only {PAGES} is accepted")
    ap.add_argument("--rules", default=None, help="JSON file of required descriptors (see load_rules)")
    a = ap.parse_args()
    for name in ("base_size", "org_size", "line_height", "gap"):
        v = getattr(a, name)
        if v is not None and not math.isfinite(v):  # nan slips past every < and > check below
            sys.exit(f"REFUSED: --{name.replace('_', '-')} {v} is not a finite number.")
    if a.max_pages != PAGES:
        sys.exit(f"REFUSED: every text CV is {PAGES} full pages. "
                 f"The one-page version is the dashboard CV: build_dashboard.py.")
    if not MIN_BASE_SIZE <= a.base_size <= MAX_BASE_SIZE:
        sys.exit(f"REFUSED: --base-size {a.base_size} is outside {MIN_BASE_SIZE} to {MAX_BASE_SIZE} pt. "
                 "Smaller is unreadable: cut words. Bigger only pads a short CV: add a true line instead.")
    if a.org_size < MIN_BASE_SIZE:
        sys.exit(f"REFUSED: --org-size {a.org_size} is below the {MIN_BASE_SIZE} pt readability floor.")
    if a.line_height is not None and not LINE_HEIGHT[0] <= a.line_height <= LINE_HEIGHT[1]:
        sys.exit(f"REFUSED: --line-height {a.line_height} is outside {LINE_HEIGHT[0]} to {LINE_HEIGHT[1]}. "
                 "Tighter crams, looser is air. Cut words, or add a true line.")
    if a.gap is not None and not GAP[0] <= a.gap <= GAP[1]:
        sys.exit(f"REFUSED: --gap {a.gap} is outside {GAP[0]} to {GAP[1]}. "
                 "Tighter crams, looser is air. Cut words, or add a true line.")
    # Stop before building rather than skip a check: a check that switches off silently is worse than none.
    try:
        import fitz  # noqa: F401  PyMuPDF measures page fill and the printed font size
    except ImportError:
        sys.exit("FAILED: PyMuPDF is missing, so page fill and the printed font size cannot be checked. "
                 "pip install pymupdf (see requirements.txt).")
    if not a.no_docx:
        try:
            import docx  # noqa: F401
        except ImportError:
            sys.exit("FAILED: python-docx is missing, so the Word copy cannot be built. "
                     "pip install python-docx (see requirements.txt), or pass --no-docx.")
    if not os.path.exists(CHROME):
        sys.exit(f"FAILED: Google Chrome not found at {CHROME}. It renders the PDF. Set CHROME_PATH to point at it.")
    missing = [t for t in ("pdfinfo", "pdftotext", "pdftoppm") if shutil.which(t) is None]
    if missing:
        sys.exit(f"FAILED: {' and '.join(missing)} not found (poppler), so the page count, word count or preview cannot be made. brew install poppler.")
    with open(a.markdown, encoding="utf-8") as f:
        md = f.read()
    doc = parse(md)
    bad = descriptor_problems(md, doc, load_rules(a.rules))
    if bad:
        print(f"REFUSED: a required descriptor is missing. Fix {'; '.join(bad)}.", file=sys.stderr)
        sys.exit(5)
    base = os.path.splitext(a.markdown)[0]
    html_path, pdf_path, docx_path = base + ".html", base + ".pdf", base + ".docx"
    lh = a.line_height if a.line_height is not None else LINE_HEIGHT[0]
    gap = a.gap if a.gap is not None else GAP[0]
    failed = 0
    if a.line_height is None and a.gap is None and not a.no_fill:
        fit = fit_spacing(doc, a)
        if fit is None:
            sys.exit("FAILED: Chrome could not render the CV at any spacing step. Try again; if it keeps failing, check Chrome.")
        lh, gap, failed = fit["lh"], fit["gap"], fit["failed"]
        if fit["fits"] and min(fit["fills"]) >= FILL_MIN:
            print(f"spacing: line height {lh}, gaps x{gap} (spread {fit['s']:.2f} of 1, chosen so every page runs to the foot)")
        elif fit["fits"]:
            print(f"spacing: line height {lh}, gaps x{gap} (spread {fit['s']:.2f} of 1), the fullest {PAGES}-page step, "
                  "but a page still stops short. The checks below say where.")
        else:
            print(f"spacing: no step from the tight design to the airiest gives exactly {PAGES} pages, so it is built "
                  f"at line height {lh}, gaps x{gap}, the nearest. The checks below say what to cut or add.")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(build_html(doc, a.paper, a.base_size, a.org_size, lh, gap))
    try:
        pages = render_pdf(html_path, pdf_path)
    except (subprocess.SubprocessError, OSError) as e:
        sys.exit(f"FAILED: Chrome could not render the PDF ({e.__class__.__name__}). Try again.")
    if not pages:
        sys.exit("FAILED: no PDF was rendered, so nothing could be checked.")
    previews = render_previews(pdf_path, base)
    if not a.no_docx:
        build_docx(doc, docx_path, a.paper)
    print(f"html: {html_path}\npdf:  {pdf_path}  ({pages} page{'s' if pages != 1 else ''})")
    if not a.no_docx: print(f"docx: {docx_path}")
    for p in previews: print(f"preview: {p}")
    printed = pdf_body_size(pdf_path)
    print(f"body text as printed: {printed} pt")
    if printed < a.base_size - 0.02:  # Chrome scales the whole page down when something is wider than it
        print(f"FAILED: body text prints at {printed} pt, not the {a.base_size} pt asked for (something wider than the page "
              f"made Chrome shrink it). Find the long unbroken line in the preview.", file=sys.stderr)
        sys.exit(3)
    words = pdf_words(pdf_path)
    if words: print(f"words: {words} (budget {MAX_WORDS})")
    if words > MAX_WORDS:
        print(f"WARNING: {words} words, over the {MAX_WORDS} budget for a readable two-page CV. Cut bullets.", file=sys.stderr)
    fills = page_fills(pdf_path)
    print("page fill: " + " · ".join(f"page {i} {pct(f)}" for i, f in enumerate(fills, 1)) + f" (each must reach {pct(FILL_MIN)})")
    retry = (f" {failed} spacing step(s) did not render, so run it again before you change the CV." if failed else "")
    if pages > PAGES:
        print(f"FAILED: {pages} pages, over {PAGES}. Cut content; the font size stays.{retry}", file=sys.stderr)
        sys.exit(2)
    if pages < PAGES:
        print(f"FAILED: only {pages} page(s); every CV is {PAGES} full pages. Add evidence.{retry}", file=sys.stderr)
        sys.exit(4)
    short = [f"page {i} stops at {pct(f)}" for i, f in enumerate(fills, 1) if f < FILL_MIN]
    if short:
        print(f"FAILED: {', '.join(short)}. Every page runs to the foot. Look at the preview, then add "
              f"evidence or check for a short role that cannot break across the page.{retry}", file=sys.stderr)
        sys.exit(4)

if __name__ == "__main__":
    main()
