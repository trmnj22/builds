---
name: grill-me
description: Ask the person what their career base is missing, one question at a time with clickable options, and save each answer into the notes, Job Scout preferences and LinkedIn voice. Use when the person types /grill-me or says "Grill me", "Grill me again", "Ask me what's missing" or "Keep going", and straight after "Build my career base" finishes.
argument-hint: "[number | gaps | jobs | linkedin | skipped | auto]"
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion
---

# Grill me

My files never say everything. This skill reads my career base, works out what is missing, and asks me, one question at a time, with options to click. Every answer is saved word for word, so new facts can cite it. Follow CLAUDE.md in this folder at all times.

## 1. Before you ask

1. If `Roles/` has no notes other than `About roles.md`, say "Type Build my career base first." and stop.
2. Read `Index.md`, `Profile.md`, the frontmatter and Gaps section of every Roles and Achievements note, every open Gap note (`status: open`), `Job Scout/Preferences.md`, `LinkedIn/Voice.md` if it exists, `LinkedIn/Topic backlog.md` if it exists, and `Sources/Grill me answers.md` if it exists.
3. Find the target job, used only to put the questions in order (never as a fact about me):
   - the newest folder in `Targets/` with an `Ad.md`, else
   - a job ad in `Inbox` (a file that reads as a job ad), else
   - the roles under "Roles I want" in `Preferences.md`, else
   - none. Then order by `ask_priority` alone.
4. Read the words after the command (`$ARGUMENTS`):
   - nothing (the default, and what the build uses): no limit. Keep asking down the whole list, one at a time, until I say "That's enough for now" or nothing is left.
   - a number, for example `/grill-me 10`: ask up to that many.
   - `gaps`, `jobs` or `linkedin`: ask only that group.
   - `skipped`: ask again only the questions I skipped before.
   - `auto`: never ask. Write the question list under "Questions" in the reply and stop. Save nothing.

## 2. Build the question list

Make the full list first, in this order. Leave out anything already answered: a gap with `status: answered`, a filled line in `Preferences.md`, a filled section in `LinkedIn/Voice.md`, or a question already in `Sources/Grill me answers.md` (answered or skipped). Skipped questions come back only with `skipped`, or after everything else has been asked.

### Group 1. Gaps that matter most for the target job
Rank open gaps by these, in order:
1. Disagreements about titles or dates (`kind: disagree`). A CV with the wrong title or dates fails a reference check.
2. Gaps on achievements or roles that match what the target job asks for (the ad's words that match a skill, achievement or role note).
3. Missing results, team size, budget or reporting line on the newest role.
4. `ask_priority` 1, then 2, then 3.
5. Facts found in one source only that the target job would care about.

### Group 2. Job Scout preferences
Only the lines that are still blank in `Job Scout/Preferences.md`, in this order: Roles I want, Locations and work mode, Pay floor, Work type, Deal-breakers.

### Group 3. LinkedIn voice and goals
Only what `LinkedIn/Voice.md` does not hold yet, in this order: who I want to reach, what I want from LinkedIn, the topics I can speak on, my tone, and a sample of my own writing.

### How many from each group
With no number (the default, and straight after a build): there is no limit. Ask all of Group 1, then Group 2, then Group 3, until I stop you or the list is empty. Straight after a build, put Roles I want from Group 2 third, after the first 2 gap questions, so the job scout has what it needs early. With a number: keep the same order and stop when that many are asked.

## 3. Ask, one question at a time

Ask one question, wait for the answer, save it (section 4), then ask the next. Never put two questions in one message.

One fact per question. If a gap needs two things (for example a result and a date), ask about the result first and leave the date for a later question.

**Backstop.** If you were called straight after a build and the line "Built your career base" has not been shown in this conversation, read `Build log.md` and show reply lines 1 to 5 first.

**The first question after a build.** When the build started you, the message with Question 1 always starts with the build summary, then a blank line, then the question. Take the numbers from `Build log.md` and `Index.md`:

```
Built your career base in a quick build: N roles, N achievements, N skills, N themes, N gaps. Every fact shows its source.
Checked N facts against your files myself. N need you.
Strongest achievements: [[...]], [[...]], [[...]]

Now some questions to fill what your files leave out. Answer as many as you like. Click "That's enough for now" whenever you want to move on.

Question 1. ...
```

Skip the summary only if those lines are already in this chat.

**Each question:**
- One short plain sentence. Name the note it is about, for example "At <Employer>, your CV says <title 1> and LinkedIn says <title 2>. Which is right?"
- 2 options with content, then "Skip this one" and "That's enough for now". The recommended option comes first and ends with "(recommended)".
- The recommended option comes from my files or my notes, never from a guess. Label where it came from, for example "<title> (from your CV) (recommended)".
- Never offer a number, a result, a team size, a budget or a pay figure as an option. For those, the first option is "I'll type it (recommended)" and the second is "There isn't one" or "I don't know".
- For a question that needs my own words (a result, a sample of writing), say I can type my answer instead of clicking.

**With the AskUserQuestion tool:** ask with it, one question per call, up to 4 options as above. It also lets me type my own answer.

**Without it:** write the question, then the options numbered 1 to 4, then "Reply with a number, or type your own answer."

**Option ideas by group:**
- Gaps, disagree: each version found in a source, labelled with that source. Recommend the more modest one unless a later source is clearly more exact.
- Gaps, missing result: "I'll type it (recommended)", "There was no measurable result".
- Gaps, missing team size or budget: "I'll type it (recommended)", "I didn't manage a team or budget in this role".
- Roles I want: the newest title and one step up from it (use `Job Scout/Fit Rubric.md` for one step up). Recommend the pair.
- Locations and work mode: "Hybrid in <city from Profile> (recommended)", "Remote anywhere in Australia".
- Pay floor: "I'll type a floor (recommended)", "No floor, show me everything". Never suggest a figure.
- Work type: "Permanent only (recommended)", "Permanent or contract".
- Deal-breakers: "I'll type them (recommended)", "None".
- Who to reach on LinkedIn: "Hiring managers and recruiters in <industry from Employers notes> (recommended)", "People in my own field".
- What I want from LinkedIn: "Be found for my next role (recommended)", "Share what I know with my field".
- Topics: two topics taken from my strongest skills or themes, by name. Recommend the one with the most evidence.
- Tone: "Plain and practical (recommended)", "Warm and personal".
- Sample of my writing: "I'll paste a post or email I wrote (recommended)", "I don't have one yet".

**Stopping:**
- "That's enough for now", "that's enough" or "stop": stop asking at once.
- When the list is empty, or a number was given and that many are asked, stop.
- With no limit, number each question ("Question 4.") without a total, and every 5 questions add one short line before the question: "Keep going, or click That's enough for now to move on."
- Then reply in at most 6 lines: how many answers were saved, the notes they went into as links, and "Type Grill me any time to keep going." If nothing is left to ask, say "Nothing left to ask for now." instead. Last line: 'Next, type "Tailor my CV to the ad in Inbox".' If a target CV already exists, say 'Next, type "Tailor my CV to the ad in Inbox" again to use your answers.'

## 4. Save each answer straight away

Save after each answer, before the next question, so nothing is lost if I stop.

### 4.1 The source note
Add the answer to `Sources/Grill me answers.md`. If it does not exist, make it from `Templates/Source.md` with these values:

```
---
type: source
key: source/grill-me-answers
kind: told-me
label: told me
file: "Answers typed in Claude"
checked: yes
built: YYYY-MM-DD
---
# Grill me answers

- What it is: my answers to Grill me, word for word, with the date.
- Belongs to: <person from Profile>

## D Mon YYYY
```

Under today's date heading (add it if it is not there), add one block per question. When I pick a numbered option and also type text, save the option as `Picked: <option text>` on its own line, without its number, and my typed text, word for word, as the answer. When I only pick an option, save its text, without the number, as the answer.

```
- Q: <the question as asked>
  - Picked: <option text, only if I picked one and also typed text>
  - A: "<my answer, word for word>" (told me D Mon YYYY)
  - Went into: [[<note>]], [[<note>]]
```

A skipped question is saved as `- A: skipped` with no citation, so it is not asked again straight away. Keep `[[Index]]` as the last line.

### 4.2 The career notes (Group 1)
A told-me citation is exactly `(told me D Mon YYYY)`, in its own brackets at the end of the line. Never merge it into another citation and never add words inside it. A line with a source and my answer reads, for example, `Title confirmed as <title>, see [[Gap - ...]] (CV p1) (told me 11 Nov 2026)`.

1. On the gap note: write the answer on the `Answer:` line, cited `(told me D Mon YYYY)`. Set `status: answered`. Add `"[[Grill me answers]]"` to its `sources:`.
2. On every note the gap affects: add the new fact as one line in the right section, cited `(told me D Mon YYYY)`. For a disagree gap, keep both source versions and add "Confirmed by me: <answer> (told me D Mon YYYY)". Never change `title_disagrees`, `dates_disagree` or any other disagree flag. The sources still disagree. My choice goes only on the "Confirmed by me" line. Add `[[Grill me answers|told me]]` to the note's Sources line and `"[[Grill me answers]]"` to `sources:`.
3. If the answer gives a result, set the achievement's `has_number` to match. If it gives what I did, set `my_part` from my own verb.
4. Remove the gap's link from the note's `## Gaps` section only when the gap is fully answered. Keep disagree gap links, since the sources still differ.
5. If you change a line in `Index.md`, keep its citation last and add the told-me citation as its own bracket after it.

### 4.3 Job Scout preferences (Group 2)
Write the answer on the matching line in `Job Scout/Preferences.md`. Keep the headings exactly. Set `updated:` to today. Set `set: yes` once Roles I want and Locations are both filled. Preferences are wishes, not facts, so they need no citation.

### 4.4 LinkedIn voice (Group 3)
Write the answer into `LinkedIn/Voice.md`, under the section that fits (who I want to reach, goals, topics, tone, samples of my writing). If there is no section that fits, add one at the end with a plain heading. If the file does not exist, make it with the heading `# My LinkedIn voice` and those sections. A writing sample is pasted word for word under its own heading, with the date. Never tidy it up. End each line you write with (told me DATE), as the linkedin-post skill does. If the answer says who I want to reach or how I want to sound, fill "Who I write for" or "How I sound" too, so Write a LinkedIn post does not ask again. Set `status: started`.

When the answer names topics I am happy to post about, also seed `LinkedIn/Topic backlog.md`. For each topic, add one row from the Theme or Achievement note that fits it best, up to three rows in all: today's date, the topic in my words, what a reader gets in one plain line, the note as a link under Evidence, status `new` (or `needs-fact` when the achievement has no result or `my_part: not stated`), and Score left blank. Skip a topic that already has a row. The LinkedIn engine scores rows when it offers them. A topic with no matching note goes into Voice.md only.

### 4.5 Quick check of what you wrote
After each save, read back the lines you added and confirm each one says no more than my answer did. Then set the changed career notes to `checked: yes`, or `checked: flagged` with a `check:` note if the answer disagrees with a source.

## 5. Rules for answers

1. **Never make my answer bigger.** "about 20 people" stays "about 20 people". "helped with the budget" stays "helped with the budget". Never round, never add a number I did not give, never swap my verb for a stronger one.
2. **Keep my words.** Save the answer word for word in the source note. In the career notes, use my words, shortened only by cutting filler.
3. **Vague stays vague.** If I say "I think it was around 2019", write that, and leave the gap open with "check: date not certain".
4. **If my answer disagrees with a source,** keep both versions, each with its citation, keep the gap open as `disagree`, and flag the note. Never delete what a source says.
5. **Other people stay out.** If I name someone, save their role instead, for example "my manager at the time".
6. **Never put pay or private details anywhere except `Job Scout/Preferences.md`.**
7. No em dashes, no semicolons, plain English, Australian spelling.
8. Stay inside this folder. Never change anything in Inbox.
