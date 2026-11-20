# Step 4. Write

## Purpose

Write the planned notes to disk, each from its template, with every fact line showing its source.

## Input

- The plan from step 3 (or, for a writer agent, only the notes in its batch).
- The fact entries those notes use.
- The template for each note type in `Templates/`: `Profile.md`, `Source.md`, `Role.md`, `Employer.md`, `Achievement.md`, `Skill.md`, `Story.md`, `Theme.md`, `Education.md`, `Certification.md`, `Recommendation.md`, `Gap.md`.

## Do

### 1. Order

Write batch G (gaps) first, then the R batches and batch P, then batch K (skills and themes). A writer agent writes only the files in its own batch.

### 2. Each note

1. Copy the template for its type. Fill every `{{...}}` placeholder.
2. Frontmatter keys, in this order: `type`, `key`, `person`, `sources`, `checked`, `built`, then the keys for that type from the template. Set `checked: no` (step 5 sets it). Set `built:` to today as YYYY-MM-DD. `sources:` lists the source notes as quoted links, for example `["[[Source - Sam Whitlock CV]]"]`.
3. Use the fact `text`, keeping the source's words and verbs. Do not polish, shorten numbers or swap in stronger verbs.
4. A section with nothing to say gets `- gap: <what is missing>` for a missing fact, or is removed if the template marks it optional.
5. Save it in its folder with its planned name, for example `Roles/Calder Freight - Operations Manager.md`.

### 3. Citations (the most important rule)

Every fact line ends with a citation in round brackets, using the source's label:
- PDF or text file: `(CV p1)`, `(LinkedIn PDF p1)`, `(Performance review 2024 p2)`
- LinkedIn export: `(LinkedIn export, Positions.csv row 1)`
- Two sources: `(CV p1, LinkedIn PDF p1)`
- Something the person told you: `(told me 14 Nov 2026)`
- Sources that disagree, write both: `31% (CV p1). "almost a third" (LinkedIn PDF p1, LinkedIn export, Positions.csv row 1).`

Lines that need no citation: headings, link-only lines (`- [[...]]`), `gap:` lines, `check:` lines.

A line that is Claude's interpretation (a theme, a story framing, why a skill is shown) starts with `Claude's reading:` and links the notes it rests on instead of a source. So does any line that ties a general statement (sectors, years, team words) to a particular employer, role or achievement.

Every note ends with a Sources line that links its source notes with the label as the alias:

```
Sources: [[Source - Sam Whitlock CV|CV]] p1, [[Source - Sam Whitlock LinkedIn profile|LinkedIn PDF]] p1
```

### 4. Type details

- **Role:** set `employer`, `title`, `start`, `end` (YYYY-MM, or `present`). Set `title_disagrees: yes` or `dates_disagree: yes` when a disagree gap covers it, and show both versions on the Title or Dates line.
- **Achievement:** set `role`, `has_number` (yes if the result has a number, otherwise no), and `my_part` from the person's verb: `led` (led, headed, ran), `did` (built, set up, rebuilt, designed), `supported` (supported, helped, contributed), `team` (any "with the ... team" or "we"), `not stated`. Use `not stated` when the source gives a result (halved, cut, lifted) but no action by the person. A result verb is not an action. Keep the phrase itself in the text.
- **Skill:** set `strength` and `evidence` (the number of Evidence lines). Every Evidence line holds a cited fact. No bare links. The Strength line gives the reason in one line, using the strength rule in step 3.
- **Employer:** `What it does:` only as a source states it about this employer by name. Otherwise `gap: not stated`.
- **Education:** if a source gives a past end year and does not say in progress, set `status: completed` and cite the end year. Use `in progress` only when a source says so. Do not flag it.
- **Story:** only for achievements that step 3 planned a story for. Set `achievements` and `complete` (yes only if situation, action and result are all sourced).
- **Theme:** set `roles` to the number of roles its evidence comes from. Keep the "Check this" line.
- **Recommendation:** use the recommender's role and employer, never their name. Quote at most 3 sentences exactly.
- **Gap:** fill every line. `Answer:` stays blank until the person answers.
- **Source:** one per Inbox item read. Use `pages: N` for a PDF or text file, or `files: N` for a LinkedIn export folder. `Facts taken from it:` is the count of fact ids from that source used in notes. For an export, list the CSV files read and say the others were skipped "to keep other people's details and your private data out". `checked: yes` (a source note holds no claims to check).
- **Profile:** the contact lines exactly as the CV has them. Location as the first source states it. Links to roles newest first.

Never write another person's name. Never use any wording from a job ad. No em dashes, no en dashes, no semicolons.

### 5. Updating a note that already exists

1. Read the note first.
2. Keep every line cited `told me`, and every gap note's `Answer:` line and `status: answered`.
3. Keep any section the person added.
4. Replace only lines the build wrote before, and add new facts.
5. Update `built:` and `sources:`.

Never delete or overwrite a note the person made themselves (it has no `key` in its frontmatter). If its name clashes with a planned note, give the planned note a name ending ` (built)` and say so in the Build log.

## Output

The notes, saved on disk. For a writer agent, return the list of files written.

## Done when

Every planned note exists, every fact line has a citation, and every `[[link]]` in it points at a planned or existing note.
