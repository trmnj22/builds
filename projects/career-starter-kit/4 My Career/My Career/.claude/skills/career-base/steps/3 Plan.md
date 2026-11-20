# Step 3. Plan

## Purpose

Decide every note the graph needs, which facts go in each one, how they link, and which gaps to raise, before anything is written. This is the only step that sees every source at once.

## Input

- Every fact list from step 2.
- The scan list from step 1, including `existing_keys`.
- `Templates/` for the note shapes.

## Do

### 1. Group facts into notes

| Note type | Folder | Name | One per |
|---|---|---|---|
| profile | root | `Profile` | person |
| source | `Sources/` | `Source - <file or folder name without extension>` | Inbox item that was read, plus `Grill me answers` (made by Grill me) and `Source - Told me` (made by add mode) once the person tells you anything. Both use the label `told me` |
| role | `Roles/` | `<Employer> - <Title>` | title held. A promotion is a new role |
| employer | `Employers/` | `<Employer>` | organisation worked or volunteered for |
| achievement | `Achievements/` | short past-tense phrase in the source's own words, under 60 characters, for example `Halved the lost-time injury frequency rate` | distinct thing delivered or changed |
| skill | `Skills/` | the skill name as a source writes it, sentence case | see the rule below |
| story | `Stories/` | a plain phrase, for example `Fixing complaints at the source` | achievement with enough detail to tell |
| theme | `Themes/` | `Theme - <phrase>` | pattern across 2 or more roles, at most 5 |
| education | `Education/` | `<Qualification> - <Institution>` | qualification |
| certification | `Certifications/` | `<Name> - <Issuer>` | certification or licence |
| recommendation | `Recommendations/` | `Recommendation - <recommender role>` | recommendation received |
| gap | `Gaps/` | `Gap - <short phrase>` | missing fact, disagreement, or a fact only one source family has |

There is no cap on roles, employers, achievements, skills, education, certifications, recommendations or gaps. Detailed means every distinct fact lands in a note. The only caps: themes at most 5, questions listed in the build reply at most 3 (Grill me then asks the rest, with no limit).

If a disagree gap covers an achievement's number, wording or verb, leave the disputed part out of the name, for example `Cut written complaints`, not `Cut written complaints by 31%`.

Note names use only letters, digits, spaces, hyphens, brackets and full stops. Spell `%` as "percent". No commas, colons, slashes or question marks. Under 60 characters.

### 2. Match the same thing across sources

- Match roles by employer and overlapping dates, not by title. The CV may call it "Operations Manager, Victoria" and LinkedIn "Operations Manager". That is one role with a title disagreement.
- Match achievements by what was done and where, not by the number. "31%" and "almost a third" about the same complaints are one achievement with a disagreement.
- Match employers by name.

### 3. Linking and creation rules

- Every achievement links to exactly one role and to 1 to 4 skills it shows.
- Every role links to its employer, its achievements, its skills and any gap notes about it.
- Every employer links to its roles.
- Every skill links to every achievement or role that shows it. Link an achievement or role to a skill only when one of its facts names that skill's subject in the source's words. For a skill name with two parts, such as "Contact centre and frontline operations", the fact must fit the part it is linked for, and the Evidence line says which. Every Evidence line holds a cited fact. No bare links.
- Strength: `Strong` needs 2 or more achievements with a stated result that have no open disagree gap. Count a flagged or `my_part: team` achievement towards `Some` only, and say so in the Strength line, for example "Some: 2 achievements, both team efforts with results to confirm". `Some` means 1 achievement, achievements without results, or achievements that only count towards Some. `Claimed only` means listed in a skills section with no example.
- Make a skill note for every skill named in any source's skills list, and for any skill that 2 or more achievements clearly show, named in the source's own words. Never invent a skill name the sources do not use or plainly describe.
- When two sources list skills that plainly mean the same thing in different words (for example "Large-scale change" and "Change management"), keep both notes, because each is sourced, but link them to each other under `## Same as` and give them one shared evidence list. The tailor lists only the one that matches the ad's wording.
- Make a story only when the sources give at least one fact beyond the achievement's own action and result: a situation, a how, a who, or a second source's view. Otherwise add the interview-theme line to the achievement under `## Story` and make no story note. Stories link to their achievements, and achievements link back under `## Story`.
- A theme needs evidence from 2 or more roles. Every theme line starts `Claude's reading:` and links its evidence. A theme name and its `Claude's reading:` line must be true of every evidence line it links. Leave out a role the wording does not fit, or use plainer words.
- A gap note links to every note it affects, and each affected note lists it under `## Gaps`.
- Education links to Profile. Recommendations link to the role and employer they speak about and to any achievement they support.
- Source notes link only to Index. Every other note links to its sources through its Sources line.
- Profile links to every role (newest first), education, certifications, recommendations and themes.
- Links use the note name only, for example `[[Calder Freight]]`, never the folder. The one exception is Targets, which use path links.

### 4. Raise gaps

Make a gap note for each of these (a quick build caps them, see `steps/Quick build.md`):
- **disagree:** two sources say different things about a title, dates, a number, the wording of a result, a location, or years of experience compared with the role dates. Keep both versions. Never pick one.
- **one-source:** a fact only one source family has, when it matters to a CV: numbers, scope, team size, budget, or a whole role. A LinkedIn PDF and a LinkedIn export are one family. Raise these only when Inbox has two or more source families. With a CV only, raise none.
- **missing:** a role with no team size, budget or reporting line, or an achievement with no result, or an achievement with no action. A team, system or process that was set up is not a result. If no source states a change, the achievement gets `gap: result not stated`.

A whole role found in only one source family always gets a one-source gap and a line in the Index "Found in one source only" list.
- **unclear:** a fact you cannot place, for example a result with no role or a date that could be two things.

Do not raise a gap when the LinkedIn PDF and export differ only in date precision (year compared with month and year).

Years of experience are only ever worked out from role dates, written as "from Feb 2011, about 15 years by Nov 2026". If a source states a different number of years, that is a disagree gap.

Set `ask_priority`:
- `1` for the three gaps that would most change a CV, in this order: titles or dates that disagree, then missing results on the newest role, then missing scope (team, budget).
- `2` for other gaps on the two newest roles.
- `3` for the rest.

### 5. Names, keys and updates

Give every note a `key`, a lower-case slug path that stays the same from one build to the next:

- `role/<employer>/<title>`
- `employer/<name>`
- `achievement/<employer>/<title>/<slug of the first 6 words>` (the whole role key path, then the slug)
- `skill/<name>`
- `story/<slug>`
- `theme/<slug>`
- `education/<institution>/<qualification>`
- `certification/<issuer>/<name>`
- `recommendation/<employer>/<recommender role>`
- `gap/<slug>`
- `source/<file stem>`

Slugs are lower case with hyphens, for example `role/fernmoor-water/head-of-customer-operations`.

If a key is already in `existing_keys`, mark the note `update: true`. Never plan a second note with the same key.

### 6. Put every note in a batch

Batches let several writers and checkers work at once without touching the same file.

- **Batch G:** every gap note. Written first, so other notes can link to them.
- **Batch R1, R2, ...:** one per role, newest first: the role note, its achievements and its stories. Volunteer roles get their own R batch.
- **Batch P:** Profile, employers, education, certifications, recommendations and source notes.
- **Batch K:** skills and themes. Written after every R batch, because they link achievements.
- `Index.md` and `Build log.md` are written last, by step 6.

## Output

The plan:

```
notes:
  - type: role
    name: Fernmoor Water - Head of Customer Operations
    key: role/fernmoor-water/head-of-customer-operations
    batch: R1
    fact_ids: [CV-010, LinkedIn PDF-012, LinkedIn export-004]
    links: [Fernmoor Water, Cut written complaints, Gap - Team size at Fernmoor Water]
    update: false
gaps:
  - name: Gap - Calder Freight title
    key: gap/calder-freight-title
    kind: disagree
    ask_priority: 1
    fact_ids: [CV-020, LinkedIn PDF-015]
    affects: [Calder Freight - Operations Manager]
unused:
  - id: CV-003
    reason: page footer
```

## Done when

Every fact id is in at least one note, or is listed under `unused` with a reason. Every planned link points at a planned or existing note. No two notes share a key.
