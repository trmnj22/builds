# Step 5. Verify

## Purpose

Check every fact in the notes against the original files, so nothing in the graph is invented, inflated or cited to the wrong place. This step is never skipped.

These are the instructions for the `fact-checker` helper, for the checkers in the workflow, and for a single agent doing every step.

## Input

- A batch of notes (or, in check mode or the single path, every built note).
- The source files themselves in Inbox. Open them yourself.
- Never use the fact lists from step 2. The check must be independent of the reader.

## Do

For every line with a citation, open the cited source at the cited place and give one verdict:

| Verdict | Meaning | Fix |
|---|---|---|
| `supported` | The source says it, in the same or plainer words, with the same number and the same verb strength | none |
| `inflated` | The note is bigger than the source: a number rounded up, a stronger verb, "led" for "with the team", scope widened, years rounded | rewrite the line in the source's words |
| `wrong-cite` | The fact is in the sources, but at a different place | correct the citation |
| `unsupported` | The fact is not in the cited source or in any source | remove the line and list it in Build log under "Removed during checking" |
| `disagree-missed` | Another source says it differently and the note shows only one version | add the other version with its citation, and link or create the disagree gap |

If you are unsure, the verdict is not `supported`. Pick the verdict that fits best and say why.

A line cited `told me DATE` is checked against `Sources/Grill me answers.md` and `Sources/Source - Told me.md`. The line must say no more than the answer did.

Also check each note for:
- No other person's name anywhere (recommenders, managers, referees). Replace with their role.
- No wording taken from a job ad, and no job ad cited as a source.
- No em dash, no en dash used as a dash, no semicolon.
- Every `[[link]]` points at a note that exists.
- Frontmatter has `type`, `key`, `person`, `sources`, `checked`, `built` and the keys for its type.
- Every interpretive line (themes, story framing, why a skill is shown) starts with `Claude's reading:`. So does any line that ties a general statement (sectors, years, team words) to a particular employer, role or achievement.
- Check every `Claude's reading:` line and every theme name against the notes it links, for widened scope or stronger words. Use the `inflated` verdict.
- Skill strength follows the rule: `Strong` needs 2 or more achievements with a stated result that have no open disagree gap. A flagged or `my_part: team` achievement counts towards `Some` only. `Some` is 1 achievement or achievements without results. `Claimed only` is a listed skill with no example.
- Every skill link rests on a cited fact that shows it, and `evidence:` equals the number of Evidence lines.
- Achievement `my_part` matches the person's verb in the source. If What I did is a gap line, `my_part` must be `not stated`.
- When the CV or LinkedIn states the result with the person's own action verb (Reduced, Led, Introduced), that verb is their part. Set `my_part: me` and do not flag who did it. Flag only when the source says the team, "helped" or "with" and the person's part is unclear.
- An achievement name holds no number or verb that a disagree gap covers.
- No two notes share a key, and an achievement's key starts with its role's key (with `role/` swapped for `achievement/`).

## Output

For each note:
- verdict counts: supported, inflated, wrong-cite, unsupported, disagree-missed
- each fix: the note, the line, the verdict, the fix, the reason
- `checked: yes` if every line is now supported, or `checked: flagged` if anything needs the person. On a flagged line, add `check: <what the person needs to confirm>` at the end of that line.

In the workflow and helpers paths, the checker returns the verdicts and fixes as data and does not edit files. A separate step applies them. In the single path, apply the fixes yourself as you go, then set `checked:`.

Keep a running total for the Build log: facts checked, supported, flagged, removed, fixed. Each cited line gets one final state: supported, flagged or removed. Supported + flagged + removed = checked. Fixed counts the lines changed by a fix, whatever their final state. List each fixed line under `## Fixed during checking`.

## Done when

Every cited line in the batch has a verdict, every fix has been applied, and every note has `checked: yes` or `checked: flagged`. No note is left with `checked: no`.
