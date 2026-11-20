#!/usr/bin/env python3
"""Check a visual spec against the Whiteboard design system (tokens.json) before rendering.

    python3 check_visual.py spec.json          exit 0 = passes, 1 = errors (listed), warnings printed either way

Rules come from tokens.json: text limits, the grammar (exactly one 'matters' element, at most one risk,
a person where the picture has people, a takeaway), and banned characters. make_visual.py runs this
first and refuses to render a spec with errors, so every image follows the system.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOK = json.load(open(os.path.join(HERE, "tokens.json"), encoding="utf-8"))
LIM = TOK["limits"]; BAN = TOK["grammar"]["banned_in_text"]
TYPES = {"boxes", "number", "ladder", "compare"}
POSES = {"down", "up", "tap", "walk", "think"}

def check(spec):
    errors, warnings = [], []
    def need(cond, msg): (errors if not cond else []).append(msg) if not cond else None
    def lim(kind, s, where):
        if s is None: return
        s = str(s); L = LIM.get(kind)
        if L and len(s) > L: errors.append(f"{where}: {kind} is {len(s)} chars, limit {L}: '{s[:40]}'")
        for b in BAN:
            if b in s: errors.append(f"{where}: banned '{b}' in text '{s[:40]}'")
    t = spec.get("type")
    if t not in TYPES: errors.append(f"type must be one of {sorted(TYPES)}, got {t!r}"); return errors, warnings
    lim("title", spec.get("title"), "title"); lim("subtitle", spec.get("subtitle"), "subtitle"); lim("takeaway", spec.get("takeaway"), "takeaway")
    if not spec.get("title"): errors.append("title is required (it carries the blue underline)")
    if not spec.get("takeaway"): errors.append("takeaway is required (the boxed sentence at the bottom)")
    title = spec.get("title", "")
    if title[:1].isupper() and title.split()[0] not in TOK["grammar"].get("capital_ok", []):
        warnings.append("title starts with a capital: the whiteboard writes lowercase unless it is a proper noun")
    for i, a in enumerate(spec.get("asides", [])): lim("aside", a, f"asides[{i}]")
    if len(spec.get("asides", [])) > 2: errors.append("at most two asides")
    matters = 0
    if t == "boxes":
        bx = spec.get("boxes", [])
        if not LIM["boxes_min"] <= len(bx) <= LIM["boxes_max"]: errors.append(f"boxes: give {LIM['boxes_min']} to {LIM['boxes_max']}")
        ids = set()
        for i, b in enumerate(bx):
            if "id" not in b or "label" not in b: errors.append(f"boxes[{i}] needs id and label")
            ids.add(b.get("id")); lim("label", b.get("label"), f"boxes[{i}]"); lim("line", b.get("line"), f"boxes[{i}]")
            matters += bool(b.get("matters"))
        for i, a in enumerate(spec.get("arrows", [])):
            if a.get("from") not in ids or a.get("to") not in ids: errors.append(f"arrows[{i}] refers to an unknown box id")
            lim("arrow_label", a.get("label"), f"arrows[{i}]")
        if spec.get("layout", "stack") not in ("stack", "row"): errors.append("layout must be stack or row")
    elif t == "number":
        lim("number_value", spec.get("value"), "value"); lim("unit", spec.get("unit"), "unit"); lim("how", spec.get("how"), "how")
        if not spec.get("value") or not spec.get("unit"): errors.append("number needs value and unit")
        matters = 1
    elif t == "ladder":
        st = spec.get("steps", [])
        if not LIM["steps_min"] <= len(st) <= LIM["steps_max"]: errors.append(f"ladder: give {LIM['steps_min']} to {LIM['steps_max']} steps")
        for i, s in enumerate(st):
            lim("step", s.get("label"), f"steps[{i}]"); lim("step_line", s.get("line"), f"steps[{i}]"); matters += bool(s.get("matters"))
    elif t == "compare":
        for side in ("left", "right"):
            c = spec.get(side)
            if not c or "title" not in c or "items" not in c: errors.append(f"compare needs {side}.title and {side}.items"); continue
            lim("compare_head", c["title"], f"{side}.title")
            if len(c["items"]) > LIM["compare_items_max"]: errors.append(f"{side}: at most {LIM['compare_items_max']} items")
            for i, it in enumerate(c["items"]): lim("compare_item", it, f"{side}.items[{i}]")
            matters += bool(c.get("matters"))
        if spec.get("left", {}).get("items") and spec.get("right", {}).get("items") and len(spec["left"]["items"]) != len(spec["right"]["items"]):
            warnings.append("compare: columns have different lengths, the picture reads better when they match")
    if matters != 1: errors.append(f"exactly one element must carry 'matters': true (found {matters})")
    r = spec.get("risk")
    if r:
        lim("risk_head", r.get("head"), "risk.head"); lim("risk_body", r.get("body"), "risk.body")
        if not r.get("body"): errors.append("risk needs a body")
        if t == "boxes" and r.get("from") and r["from"] not in {b.get("id") for b in spec.get("boxes", [])}: errors.append("risk.from must be a box id")
    p = spec.get("person")
    if t in ("boxes", "ladder", "compare") and not p: warnings.append("no person in the picture: the system expects a stick figure wherever the post is about people")
    if p:
        lim("person_label", p.get("label"), "person.label"); lim("aside", p.get("aside"), "person.aside")
        if p.get("pose", "down") not in POSES: errors.append(f"person.pose must be one of {sorted(POSES)}")
    return errors, warnings

def main():
    if len(sys.argv) < 2: raise SystemExit(__doc__)
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    errors, warnings = check(spec)
    for w in warnings: print("warning:", w)
    for e in errors: print("error:", e)
    print("passes the Whiteboard system" if not errors else f"{len(errors)} error(s): fix the spec, not the renderer")
    sys.exit(1 if errors else 0)

if __name__ == "__main__": main()
