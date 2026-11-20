---
name: assignment-grader
description: Grade any assignment against a rubric or guideline using two INDEPENDENT professor agents (strict and lenient) graded blind to each other, then synthesise a polished HTML dashboard with a strict/lenient toggle. Use when the user wants to grade, mark, assess, score, or evaluate an assignment, essay, report, code submission, or any student work against a rubric or marking guideline. Grills the user to disambiguate file roles and capture the professor's name before grading.
---

# Assignment Grader

Grade an assignment of **any type** (essay, report, code, design, lab, presentation, dataset analysis, etc.) against a rubric or marking guideline, from the perspective of **two professor personas**, a strict professor and a lenient professor, and render the result as a self-contained HTML dashboard.

This skill runs as a **multi-agent flow**. You (the invoking agent) are the **orchestrator**: you grill, prepare inputs, and synthesise, but you do **not** grade yourself. Two **independent sub-agents** do the grading, blind to each other, so the two lenses can genuinely diverge instead of one anchoring the other. The flow has four phases. Do them in order. Do not skip the grilling phase.

---

## Phase 1: Grill for clarity (REQUIRED before grading)

Inspect everything the user gave you (attached files, paths, pasted text, prior turns) and resolve every ambiguity below. Ask only the questions that are still open after inspection. Never ask for something you can already determine. Batch open questions into a single message (use the AskUserQuestion tool when the choices are discrete).

Resolve these before proceeding:

1. **Which file is the rubric/guideline, and which are the submission?**
   - If file names are ambiguous (e.g. `doc1.pdf`, `final.docx`, `submission.zip`), peek at each file's first page/lines to infer its role, then confirm your inference with the user rather than assuming silently.
   - There may be **one or many** submission files. Confirm the full set.
   - If no rubric/guideline is present at all, ask the user to provide one, OR offer to grade against a generic academic rubric (clarity, completeness, correctness, structure, originality) and label the output clearly as "graded against a generic rubric, no rubric supplied."

2. **Professor's name.** If not already provided, ask for it. This name is shown on the dashboard and used to sign both persona reviews (e.g. "Prof. <Name>, Strict lens"). If the user declines, use "The Examiner."

3. **Which personas to run.** Default to running **both** strict and lenient. Confirm if the user wants only one.

4. **Anything ambiguous about scope.** If the rubric references components that don't appear in the submission (e.g. rubric mentions a "live demo" or "viva" but only a PDF was submitted), flag it now and ask whether to (a) skip that criterion as not-applicable, or (b) mark it as missing/zero. Default: skip as N/A and note it.

5. **Grade scale.** Detect from the rubric (points, %, letter, bands). If none is implied, default to a 0–100 scale per criterion rolled up to an overall %. Confirm only if genuinely unclear.

Keep grilling tight, typically one or two rounds. The goal is shared understanding of *what* is being graded and *against what*, not an interrogation.

> A standalone `grill-me` skill exists for stress-testing plans. This skill has its own purpose-built grilling above. Use this one. Do not invoke the generic skill for grading.

---

## Phase 2: Understand the rubric and the submission

1. Read the rubric/guideline in full. Extract a **criteria list**: each criterion's name, what it asks for, its weight/max points, and any descriptors (what earns full vs partial vs no marks).
2. Read every submission file. For code, read the actual source and, where feasible, reason about correctness. For documents, read the content, not just headings.
3. Build a mapping: for each criterion, locate the evidence in the submission (file + location). If a criterion has no corresponding evidence, mark it N/A or missing per the Phase-1 decision.
4. **Leave out criteria the input cannot support.** Grade only what the supplied material lets you judge. Never fabricate evidence, never invent a demo you didn't see, never assume content that isn't there. An honest "not assessable from the provided files" is correct and must appear on the dashboard.

---

## Phase 3: Grade with two INDEPENDENT professor agents (multi-agent flow)

Do **not** grade in your own head. Spawn **two sub-agents** with the Agent tool, one strict and one lenient, and launch them **in a single message so they run concurrently and blind to each other**. Each receives the *same* rubric, the *same* evidence, and the *same* Phase-1 grading decisions. Only the judgement posture differs. Independence is the whole point: it removes the anchoring bias where one lens drags the other toward the middle.

**Prepare the shared input once** (so both agents grade identical material):
- The full rubric, with each criterion's id, description and max points.
- The submission content. If files are large, extract their text to a scratch file first and pass the path. For images the agents can't see, pass a faithful written description.
- The Phase-1 decisions verbatim (N/A skips, missing components, scale, anything graded as-is, anything unverifiable).
- Any rubric arithmetic to normalise (e.g. a section whose sub-points don't match its header). Tell the agents to score sub-criteria at face value and note that **you**, the orchestrator, will normalise.

**Each sub-agent returns structured JSON**. For every criterion: `score`, `earns` (1–4 concrete things in the submission that earn marks on that criterion), `loses` (0–3 concrete things that hold the score below max, empty only at full marks), and a one-sentence `justification`. Plus an overall `verdict` paragraph in that professor's voice and a `band`. Instruct each to **return only JSON**.

Give each its posture:

**Strict Professor**: high standards, holds the work to the top descriptor. Penalises missing detail, unsupported claims, weak structure, shallow analysis. Ambiguity counts against the submission. Rewards only what is clearly demonstrated. Rounds down.

**Lenient Professor**: generous, rewards effort and intent. Credits partial attempts and good-faith reasoning. Forgives minor errors and omissions that don't undermine the core. Ambiguity counts in the submission's favour. Rounds up.

**Then you (orchestrator) synthesise.** Do not re-grade:
- Parse both JSON results. Apply any normalisation, then compute each lens's section subtotals, overall score, and percentage. Keep the two lenses' numbers exactly as each agent returned them. Divergence is expected and desirable.
- Derive each band from the rubric's scale (or the detected institution's bands).
- Write a shared set of **actionable improvements** (3–6 bullets), each tied to the specific criteria the strict lens marked down. These are the highest-value fixes.

Fallbacks: if a sub-agent returns malformed output, send it back once asking for valid JSON only. If the Agent tool is genuinely unavailable, grade the two lenses yourself but in **separate passes** (fully score strict before looking at lenient) and say on the dashboard that grading was not independently agented. If only one persona was requested in Phase 1, run a single agent and build a single-lens dashboard (no toggle).

---

## Phase 4: Render the HTML dashboard

Produce a **single self-contained `.html` file** (all CSS/JS inline, no external requests, works offline by double-click). Apply genuine frontend craft, not a generic table. Load and follow the principles in the `frontend-design` skill for visual quality (typographic hierarchy, restrained palette, spacing rhythm, considered colour). Use `assets/dashboard-template.html` in this skill as the structural starting point and adapt it to the actual data.

**A lens TOGGLE is the core interaction.** Do not show both professors' grades side by side on one page. Put a strict/lenient segmented toggle near the top. Switching it must swap the **entire** page to that lens: hero score, every criterion's score/bar/justification, the earns/loses lists, the section subtotals, and the verdict. Implement it with vanilla JS toggling a `body` class (`lens-strict` / `lens-lenient`) and CSS that shows only the active `.v-strict` / `.v-lenient` blocks, no external libraries, works offline. Default to the strict lens. Make the toggle keyboard-accessible (`aria-pressed`). Keep a small, quiet comparison line in the hero showing the *other* lens's headline number so the spread stays visible without leaving the lens.

The dashboard MUST include:

1. **Header**: assignment title, professor's name, grade scale, date, and the file(s) graded.
2. **Headline scorecard**: for the active lens: overall score, points, and band, plus the quiet "other lens scored X" comparison line, and a one-line callout of the spread between the two independent graders.
3. **Per-criterion breakdown**: a card per criterion showing, *for the active lens*: criterion name, max/weight, score, a visual bar, the one-line justification, and (required) two boxes: **"What earns marks"** (✓ list) and **"What loses marks"** (✗ list), populated from that lens's `earns`/`loses`. At full marks the loses box reads "Nothing, full marks." Criteria marked N/A or "not assessable" are visually muted and excluded from the denominator.
4. **Professor verdict**: the active lens's signed overall verdict and score. Make the personalities legible (strict = cooler and sharper treatment, lenient = warmer) without being cartoonish. Recolour the accent per lens.
5. **Improvements**: the actionable bullets, ideally noting which lens/criterion each fix targets.
6. **Methodology footnote**: that two independent agents graded blind to each other, what was graded, what was skipped or normalised and why, and the explicit note if a generic rubric was used or grading wasn't independently agented.

Design requirements:
- Responsive, readable on a laptop and a phone. Wide tables scroll inside their own container. The page body never scrolls horizontally.
- Accessible contrast. Don't encode meaning in colour alone (pair colour with a label or icon).
- A restrained, intentional aesthetic: one accent, a clear type ramp, generous whitespace. Avoid the generic purple-gradient-card look.
- Print-friendly (a clean `@media print` so the professor can export a PDF).

Save the file to the working directory (or where the submission lives) as `<assignment-slug>-grade-dashboard.html`. After writing it, tell the user the path and offer to open it. If a Claude preview/browser tool is available and the user wants it, render a screenshot.

---

## Guardrails

- **Honesty over flattery.** Report what the evidence supports. If the work is weak, the strict column says so plainly. If it's strong, say that too.
- **No fabrication.** Never invent submission content, citations, results, or features that aren't in the files.
- **Scale to the input.** A one-paragraph rubric and a single PDF gets a lean dashboard. A 12-criterion rubric and a multi-file repo gets a full one. Don't pad.
- **Transparency.** Anything skipped, assumed, or graded against a fallback rubric is stated on the dashboard, not buried.
