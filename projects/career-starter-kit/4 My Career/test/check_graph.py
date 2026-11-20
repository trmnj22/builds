#!/usr/bin/env python3
"""Checks a built My Career knowledge graph against the starter's rules.

Usage: python3 -I check_graph.py "<path to My Career>"

Prints PASS, FAIL or WARN per check and exits 1 if any check FAILs.
Python 3 standard library only.
"""

import html
import os
import re
import sys
from html.parser import HTMLParser

# Folders that hold notes written by the build
TYPE_FOLDERS = [
    "Sources", "Roles", "Employers", "Achievements", "Skills", "Stories",
    "Themes", "Education", "Certifications", "Recommendations", "Gaps",
]
ROOT_BUILT = ["Profile.md", "Index.md", "Build log.md"]
SKIP_DIRS = {".claude", "Inbox", "Templates", "Old builds", ".obsidian", ".git"}

COMMON = ["type", "key", "person", "sources", "checked", "built"]
REQUIRED = {
    "source": ["type", "key", "kind", "label", "checked", "built"],
    "index": ["type", "key", "person", "built"],
    "build-log": ["type", "key", "person", "built"],
}
TYPE_EXTRA = {
    "role": ["employer", "title", "start", "end", "title_disagrees", "dates_disagree"],
    "employer": ["relationship"],
    "achievement": ["role", "has_number", "my_part"],
    "skill": ["strength", "evidence"],
    "story": ["achievements", "complete"],
    "theme": ["roles"],
    "education": ["status"],
    "recommendation": ["recommender_role"],
    "gap": ["kind", "ask_priority", "status"],
}

FACT_SECTIONS = {
    "what i did", "what changed", "situation", "contact", "where i am based",
    "headline and summary", "what the role was for", "in five lines",
}
FACT_BULLETS = (
    "Title:", "Dates:", "Location:", "Reported to:", "Team:", "Budget:",
    "When:", "Qualification:", "Institution:", "Status:", "What it does:",
    "Where:", "Name:", "Issuer:", "Date issued:", "Expires:",
)

SAM_MIN = {
    "role": 5, "employer": 4, "achievement": 10, "skill": 9, "education": 2,
    "recommendation": 1, "gap": 6, "story": 3,
}
SAM_MIN_QUICK = {"achievement": 7, "story": 0}

results = []


def report(status, name, detail=""):
    results.append(status)
    line = f"{status}  {name}"
    if detail:
        line += f"\n      {detail}"
    print(line)


def check(ok, name, bad=None, warn_only=False, limit=8):
    """ok is a bool. bad is a list of example problems shown on failure."""
    if ok:
        report("PASS", name)
        return
    status = "WARN" if warn_only else "FAIL"
    detail = ""
    if bad:
        shown = bad[:limit]
        detail = "\n      ".join(str(b) for b in shown)
        if len(bad) > limit:
            detail += f"\n      ... and {len(bad) - limit} more"
    report(status, name, detail)


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def split_frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    lines = text.split("\n")
    fm = {}
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            body = "\n".join(lines[i + 1:])
            return fm, body
        m = re.match(r"^([A-Za-z_]+):\s*(.*)$", lines[i])
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return {}, text


def rel(root, path):
    return os.path.relpath(path, root).replace(os.sep, "/")


def walk_md(root, skip=SKIP_DIRS):
    for dirpath, dirnames, filenames in os.walk(root):
        top = rel(root, dirpath).split("/")[0]
        if top in skip:
            dirnames[:] = []
            continue
        for fn in filenames:
            if fn.endswith(".md"):
                yield os.path.join(dirpath, fn)


def strip_code(text):
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", text)


class TextOnly(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script", "head", "title"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("style", "script", "head", "title") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def visible_words(html_text):
    p = TextOnly()
    p.feed(html_text)
    text = html.unescape(" ".join(p.parts))
    return len(re.findall(r"\S+", text))


def main():
    if len(sys.argv) != 2:
        print('Usage: python3 -I check_graph.py "<path to My Career>"')
        sys.exit(2)
    root = os.path.abspath(sys.argv[1])
    if not os.path.isdir(root):
        print(f"Not a folder: {root}")
        sys.exit(2)
    print(f"Checking {root}\n")

    # ---------- collect built notes ----------
    notes = {}  # rel path -> (fm, body, raw)
    candidates = [os.path.join(root, f) for f in ROOT_BUILT]
    for folder in TYPE_FOLDERS:
        d = os.path.join(root, folder)
        if os.path.isdir(d):
            for dirpath, _, filenames in os.walk(d):
                for fn in filenames:
                    if fn.endswith(".md"):
                        candidates.append(os.path.join(dirpath, fn))
    for path in candidates:
        if not os.path.isfile(path):
            continue
        raw = read(path)
        fm, body = split_frontmatter(raw)
        if "type" in fm:
            notes[rel(root, path)] = (fm, body, raw)

    by_type = {}
    for r, (fm, _, _) in notes.items():
        by_type.setdefault(fm["type"], []).append(r)

    check(len(notes) > 0, "Built notes found", ["No note with type: frontmatter. Has the build run?"])
    if not notes:
        finish()

    person = notes.get("Profile.md", ({}, "", ""))[0].get("person", "")
    is_sam = "Sam Whitlock" in person
    print(f"      Person: {person or '(no Profile.md)'}")

    # ---------- counts ----------
    print("\nCounts by type:")
    for t in sorted(by_type):
        print(f"      {t}: {len(by_type[t])}")
    print()

    # ---------- frontmatter keys ----------
    bad = []
    for r, (fm, _, _) in notes.items():
        t = fm["type"]
        need = REQUIRED.get(t, COMMON) + TYPE_EXTRA.get(t, [])
        missing = [k for k in need if k not in fm]
        if missing:
            bad.append(f"{r}: missing {', '.join(missing)}")
    check(not bad, "Every built note has the front matter keys its type needs", bad)

    # ---------- checked: yes or flagged ----------
    bad = []
    for r, (fm, _, _) in notes.items():
        if fm["type"] in ("index", "build-log"):
            continue
        if fm.get("checked") not in ("yes", "flagged"):
            bad.append(f"{r}: checked: {fm.get('checked', '(missing)')}")
    check(not bad, "checked is yes or flagged on every note, never no", bad)

    # ---------- links resolve ----------
    all_files = {}
    for dirpath, dirnames, filenames in os.walk(root):
        top = rel(root, dirpath).split("/")[0]
        if top in (".git", ".obsidian"):
            dirnames[:] = []
            continue
        for fn in filenames:
            p = rel(root, os.path.join(dirpath, fn))
            all_files[p.lower()] = p
    stems = {}
    for p in all_files.values():
        base = p.split("/")[-1]
        stems.setdefault(base.lower(), p)
        if base.endswith(".md"):
            stems.setdefault(base[:-3].lower(), p)

    def resolves(target):
        t = target.strip().lower()
        if not t:
            return True
        if t in stems or t in all_files or (t + ".md") in all_files:
            return True
        return False

    link_files = list(notes.keys())
    for sub in ("Targets", "Job Scout/Shortlists"):
        d = os.path.join(root, sub)
        if os.path.isdir(d):
            for dirpath, _, filenames in os.walk(d):
                for fn in filenames:
                    if fn.endswith(".md") and not fn.startswith("About "):
                        link_files.append(rel(root, os.path.join(dirpath, fn)))
    bad = []
    for r in link_files:
        text = strip_code(read(os.path.join(root, r)))
        for m in re.finditer(r"!?\[\[([^\]]+)\]\]", text):
            target = m.group(1).split("|")[0].split("#")[0].replace("\\", "")
            if not resolves(target):
                bad.append(f"{r}: [[{m.group(1)}]]")
    check(not bad, "Every [[link]] resolves to a file in the folder", bad)

    # ---------- citations on fact lines ----------
    labels = set()
    for r in by_type.get("source", []):
        lab = notes[r][0].get("label", "").strip().strip('"').strip("'")
        if lab:
            labels.add(lab.lower())
    check(bool(labels), "Source notes carry a label", ["No label: found in any Sources note"])

    cite_end = re.compile(r"\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*\.?\s*$")
    uncited = []
    bad_labels = []

    def label_ok(group):
        parts = [p.strip() for p in group.split(",")]
        for p in parts:
            pl = p.lower()
            if not pl:
                continue
            if pl.startswith("told me"):
                continue
            if re.match(r"^[\w ()_-]+\.csv row \d+", pl):
                continue
            if re.match(r"^p\d+", pl) or re.match(r"^row \d+", pl):
                continue
            if any(pl == lab or pl.startswith(lab + " ") for lab in labels):
                continue
            return False
        return True

    for r, (fm, body, _) in notes.items():
        if fm["type"] in ("build-log",):
            continue
        section = ""
        for line in strip_code(body).split("\n"):
            s = line.strip()
            if s.startswith("#"):
                section = s.lstrip("#").strip().lower()
                continue
            if not s or s.startswith(">") or s.startswith("Sources:"):
                continue
            item = re.sub(r"^(?:[-*]|\d+\.)\s+", "", s)
            is_fact = section in FACT_SECTIONS or item.startswith(FACT_BULLETS)
            if not is_fact:
                continue
            low = item.lower()
            if "gap:" in low or "check:" in low or item.startswith("[[") \
                    or item.startswith("Claude's reading:") or "claude's reading:" in low:
                continue
            if fm["type"] == "index" and section == "in five lines" and item in ("…", "..."):
                continue
            m = cite_end.search(item)
            if not m:
                uncited.append(f"{r} [{section}]: {item[:90]}")
                continue
            if labels and not label_ok(m.group(1)):
                bad_labels.append(f"{r}: ({m.group(1)})")
    check(not uncited, "Every fact line ends with a (source) citation, gap: or check:", uncited)
    check(not bad_labels, "Every citation label matches a Sources note label or told me", bad_labels)

    # ---------- dashes and semicolons in every .md ----------
    bad = []
    for path in walk_md(root, skip={".git", ".obsidian", "Inbox"}):
        r = rel(root, path)
        if r.startswith(".claude/skills/humanizer/"):
            continue  # quotes the characters it removes
        for n, line in enumerate(read(path).split("\n"), 1):
            if "x{2014}" in line:
                continue  # quotes the check's own search pattern (as make-zip.sh allows)
            if "\u2014" in line or "\u2013" in line or ";" in line:
                bad.append(f"{r}:{n}: {line.strip()[:90]}")
    check(not bad, "No em dash, en dash or semicolon in any .md (humanizer skill excluded)", bad)

    # ---------- forbidden strings ----------
    bad = []
    forbidden = [r"Jordan Pike", r"\bPike\b"]
    for dirpath, dirnames, filenames in os.walk(root):
        top = rel(root, dirpath).split("/")[0]
        if top in ("Inbox", ".git", ".obsidian"):
            dirnames[:] = []
            continue
        for fn in filenames:
            if not fn.endswith((".md", ".html", ".js", ".json", ".csv")):
                continue
            path = os.path.join(dirpath, fn)
            r = rel(root, path)
            if r.startswith(".claude/skills/humanizer/"):
                continue
            text = read(path)
            for pat in forbidden:
                if re.search(pat, text):
                    bad.append(f"{r}: {pat}")
    check(not bad, "The sample recommender's name appears in no file outside Inbox", bad)

    # ---------- safe file names ----------
    bad, odd = [], []
    for path in list(notes) + link_files:
        base = path.split("/")[-1]
        stem = base[:-3] if base.endswith(".md") else base
        if re.search(r'[:/\\?*"<>|]', stem) or len(stem) >= 60:
            bad.append(path)
        elif not re.match(r"^[A-Za-z0-9 ().\-\[\]]+$", stem):
            odd.append(path)
    check(not bad, "File names have no colons or Windows-unsafe characters and are under 60 characters", bad)
    check(not odd, "File names use only letters, digits, spaces, hyphens, brackets and full stops", odd, warn_only=True)

    # ---------- job ad never a source ----------
    bad = []
    for r in by_type.get("source", []):
        fm = notes[r][0]
        if "job ad" in fm.get("file", "").lower() or fm.get("kind") == "job-ad":
            bad.append(f"{r}: source note for a job ad")
    for r, (fm, body, _) in notes.items():
        if fm["type"] in ("index", "build-log"):
            continue
        if re.search(r"kestrel|job ad - |\(job ad", body, re.I):
            bad.append(f"{r}: mentions the job ad")
    check(not bad, "Trap 9: the job ad is never a source outside Targets, Index and Build log", bad)

    # ---------- Sam specific ----------
    if is_sam:
        sam_checks(root, notes, by_type)
    else:
        check(len(by_type.get("role", [])) >= 1, "At least one role note", ["Roles is empty"])

    # ---------- Targets ----------
    targets_checks(root)

    finish()


def sam_checks(root, notes, by_type):
    print("\nSam Whitlock checks:")
    bad = []
    blog = notes.get("Build log.md", ({}, "", ""))[1]
    mins = dict(SAM_MIN)
    if re.search(r"How:\s*quick", blog, re.I):
        mins.update(SAM_MIN_QUICK)  # quick build leaves stories and scope notes to the full build
        print("      (quick build minimums)")
    for t, n in mins.items():
        have = len(by_type.get(t, []))
        if have < n:
            bad.append(f"{t}: {have}, need {n}")
    src = [r for r in by_type.get("source", []) if notes[r][0].get("kind") != "told-me"]
    if len(src) < 3:
        bad.append(f"source (not counting Told me): {len(src)}, need 3")
    themes = len(by_type.get("theme", []))
    if not 1 <= themes <= 5:
        bad.append(f"theme: {themes}, need 1 to 5")
    check(not bad, "Minimum note counts for Sam", bad)

    def bodies(types=None):
        for r, (fm, body, raw) in notes.items():
            if types is None or fm["type"] in types:
                yield r, fm, body, raw

    # Trap 1: years
    has_fourteen = any(re.search(r"fourteen years", b, re.I) for _, _, b, _ in bodies())
    gap_years = [r for r, fm, b, _ in bodies(["gap"])
                 if re.search(r"fourteen", b, re.I) and fm.get("kind") == "disagree"]
    inflated = []
    for r, fm, b, _ in bodies():
        for line in b.split("\n"):
            if re.search(r"15\+|fifteen|over 15|more than 15", line, re.I) or \
                    re.search(r"(?<!about )\b15 years", line):
                inflated.append(f"{r}: {line.strip()[:90]}")
    check(has_fourteen and gap_years and not inflated,
          "Trap 1: 'fourteen years' shown with a disagree gap, no '15 years' stated as fact",
          ([] if has_fourteen else ["'fourteen years' not found in any note"])
          + ([] if gap_years else ["no disagree Gap note mentions fourteen"])
          + inflated)

    # Trap 2: Calder title
    calder = [r for r, fm, b, _ in bodies(["role"]) if "calder" in fm.get("employer", "").lower()]
    problems = []
    if not calder:
        problems.append("no Calder Freight role note")
    for r in calder:
        if notes[r][0].get("title_disagrees") != "yes":
            problems.append(f"{r}: title_disagrees is not yes")
    if not any("Operations Manager, Victoria" in b for _, _, b, _ in bodies()):
        problems.append("'Operations Manager, Victoria' not found")
    if not [r for r, fm, b, _ in bodies(["gap"]) if "Victoria" in b]:
        problems.append("no Gap note mentions the Victoria title")
    check(not problems, "Trap 2: Calder title shown both ways, title_disagrees: yes, one Gap note", problems)

    # Trap 3: complaints
    problems = []
    lines = [(r, l) for r, _, b, _ in bodies() for l in b.split("\n")]
    if not any("31%" in l and re.search(r"\(CV\b|\(CV p", l) for _, l in lines):
        problems.append("no line with 31% cited to the CV")
    if not any("almost a third" in l and "LinkedIn" in l for _, l in lines):
        problems.append("no line with 'almost a third' cited to LinkedIn")
    for r, l in lines:
        if re.search(r"over 30%|more than 30%", l, re.I):
            problems.append(f"{r}: {l.strip()[:90]}")
        if "complaint" in l.lower() and re.search(r"(?<!almost )\ba third\b", l, re.I):
            problems.append(f"{r}: {l.strip()[:90]}")
    check(not problems, "Trap 3: '31%' (CV) and 'almost a third' (LinkedIn) both kept, nothing rounded", problems)

    # Trap 4: one-source facts (text search is rough, so WARN only)
    idx = notes.get("Index.md", ({}, "", ""))[1]
    m = re.search(r"### Found in one source only\n(.*?)(?:\n#|\Z)", idx, re.S)
    one_list = m.group(1) if m else ""
    one_gaps = " ".join(b for _, fm, b, _ in bodies(["gap"]) if fm.get("kind") == "one-source")
    pool = (one_list + " " + one_gaps).lower()
    wanted = {
        "Graduate Analyst role": r"graduate analyst",
        "vulnerability team": r"vulnerability team",
        "treasurer role": r"treasurer",
        "billing system": r"billing system",
        "LTIFR": r"injury|ltifr",
        "team sizes": r"\b140\b|\b210\b|\b12\b|team size",
        "$18M budget": r"\$18m|budget",
    }
    missing = [k for k, pat in wanted.items() if not re.search(pat, pool)]
    check(not missing, "Trap 4: one-source facts listed in a one-source Gap or the Index list",
          [f"not found: {k}" for k in missing], warn_only=True)

    # Trap 5: with the planning team
    dock = [(r, fm) for r, fm, b, _ in bodies(["achievement"]) if "with the planning team" in b]
    problems = []
    if not dock:
        problems.append("no achievement keeps 'with the planning team'")
    for r, fm in dock:
        if fm.get("my_part") != "team":
            problems.append(f"{r}: my_part is {fm.get('my_part')}, expected team")
    check(not problems, "Trap 5: dock scheduling keeps 'with the planning team' and my_part: team", problems)

    # Traps 6 and 7 (WARN only, wording varies)
    ltifr = [(r, b) for r, _, b, _ in bodies(["achievement"]) if re.search(r"injury", b, re.I)]
    check(ltifr and all("gap:" in b.lower() for _, b in ltifr),
          "Trap 6: the lost-time injury achievement has a gap: line",
          [r for r, b in ltifr if "gap:" not in b.lower()] or ["no lost-time injury achievement"],
          warn_only=True)
    vuln = [(r, b) for r, _, b, _ in bodies(["achievement"]) if re.search(r"vulnerability team", b, re.I)]
    check(vuln and all("gap:" in b.lower() for _, b in vuln),
          "Trap 7: the vulnerability team achievement has a gap: line",
          [r for r, b in vuln if "gap:" not in b.lower()] or ["no vulnerability team achievement"],
          warn_only=True)

    # Trap 8: recommender's name
    bad = [r for r, _, _, raw in bodies() if re.search(r"\bJordan\b|\bPike\b", raw)]
    check(not bad, "Trap 8: the recommender's name appears in no note", bad)

    # Not a gap: the Jan 2019 month artefact
    bad = [r for r, fm, b, _ in bodies(["gap"]) if re.search(r"jan(uary)? 2019", b, re.I)
           and fm.get("kind") == "disagree"]
    check(not bad, "The Jan 2019 month in Volunteering.csv is not treated as a disagree gap", bad, warn_only=True)


def targets_checks(root):
    tdir = os.path.join(root, "Targets")
    if not os.path.isdir(tdir):
        return
    folders = [d for d in sorted(os.listdir(tdir)) if os.path.isdir(os.path.join(tdir, d))]
    if not folders:
        return
    print("\nTargets checks:")
    for f in folders:
        base = os.path.join(tdir, f)
        missing = [n for n in ("Ad.md", "Fit.md", "CV.md", "CV.html")
                   if not os.path.isfile(os.path.join(base, n))]
        check(not missing, f"{f}: has Ad.md, Fit.md, CV.md and CV.html", [f"missing {m}" for m in missing])

        cv = os.path.join(base, "CV.md")
        if os.path.isfile(cv):
            bad = []
            in_exp = False
            for line in read(cv).split("\n"):
                s = line.strip()
                if s.startswith("## "):
                    in_exp = "experience" in s.lower()
                    continue
                if in_exp and re.match(r"^[-*]\s+", s):
                    if not re.search(r"\(from \[\[[^\]]+\]\][^()]*\)\s*\.?\s*$", s):
                        bad.append(s[:90])
            check(not bad, f"{f}: every experience line in CV.md ends (from [[note]])", bad)

        fit = os.path.join(base, "Fit.md")
        if os.path.isfile(fit):
            t = read(fit)
            rows = [l for l in t.split("\n") if l.strip().startswith("|")
                    and re.search(r"\b(Strong|Partial|Gap)\b", l)]
            has_line = re.search(r"Fit:\s*\d+ Strong, \d+ Partial, \d+ Gap", t)
            check(bool(rows) and bool(has_line), f"{f}: Fit.md has a Strong/Partial/Gap table and the Fit: line",
                  ([] if rows else ["no table rows with Strong, Partial or Gap"])
                  + ([] if has_line else ["no 'Fit: N Strong, N Partial, N Gap' line"]))

        h = os.path.join(base, "CV.html")
        if os.path.isfile(h):
            words = visible_words(read(h))
            check(words < 900, f"{f}: CV.html has under 900 words of visible text ({words})")


def finish():
    fails = results.count("FAIL")
    warns = results.count("WARN")
    passes = results.count("PASS")
    print(f"\n{passes} passed, {fails} failed, {warns} warnings")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
