---
name: scout-setup
description: Ask the person once what jobs they want and save it to Job Scout/Preferences.md, using any answers already given in Grill me. Use for /scout-setup, 'Set up my Job Scout', or any request to change Job Scout preferences such as 'Add Sydney to my Job Scout locations'.
argument-hint: "[auto]"
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion
---

Save what I want next to `Job Scout/Preferences.md`. Follow the rules in `CLAUDE.md` in this folder. Write only that one file.

## 1. Check the career map is built
- If `Roles/` has no notes other than `About roles.md`, reply "Type Build my career base first." and stop.
- Read `Profile.md` (location), the Roles notes (title, start, end, employer), the Employer notes (`industry:` if present) and the Skills notes (`strength:`).
- Read `Job Scout/Preferences.md` as it is now.
- Read `Sources/Grill me answers.md` if it exists. Grill me may already have filled lines in Preferences.md.

A line counts as filled when it has my own text, not just the hint in brackets. Lines Grill me or I filled are my answers. Never overwrite them, never ask about them again, and never mark them "(set by scout, please check)".

## 2. Pick the mode
- **Edit mode:** the request changes one thing, for example "Add Sydney to my Job Scout locations", "Remove contract from my work type", "Change my pay floor to $180,000". Edit only that line. Reply with the before and after, two lines. Set `updated:` to today. Done.
- **Auto mode** (`auto` in the arguments, or a scheduled run): do not ask. If Roles I want is blank, fill it with the title of the newest paid role (not volunteer) and one step up from it using the ladder in Fit Rubric step B, and if Locations is blank, fill it with the Profile location, each followed by "(set by scout, please check)". Leave every other line as it is. Set `set: yes` and `updated:` to today. Reply in two lines with what was filled and "Please check Job Scout/Preferences.md". Done.
- **Already set by Grill me:** `set: yes` and Roles I want, Locations and Work mode are all filled, and I did not ask to start again. Do not ask anything. Reply with the filled lines in short form (at most 6 lines), then 'Change any line by saying so, for example "Add Sydney to my Job Scout locations". Next, type "Set up my Job Scout to run every day at 7am".' Done.
- **Setup mode:** everything else. Go to step 3. If I said "start again" or "redo my Job Scout", ask every question in step 3 and replace the old lines.

## 3. Ask (setup mode)
Ask only about lines that are still blank, at most 6 questions, in the order below. Skip a question when its lines are already filled. Build every option from the career map. Put the recommended option first and add "(recommended)" to its label. Never offer a pay figure, never estimate one.

If the AskUserQuestion tool is available, ask in two calls (it takes up to 4 questions at a time): questions 1 to 4, then 5 and 6. Otherwise list them numbered, each with lettered options, and say "Answer like 1a, 2b, or type your own."

1. **Roles** (multi-select): the title of the newest role, the title of the role before it, and one step up from the newest (for example "Head of Customer Operations" leads to "GM Customer and Operations"). Use the ladder in `Job Scout/Fit Rubric.md` for one step up. Recommended: the newest title and the step up.
2. **Level:** "Same level", "One step up", "Either". Recommend "One step up" if the newest role started 3 or more years ago, otherwise "Either".
3. **Locations and work mode:** "Hybrid in <city from Profile>" (recommended), "On site in <city>", "Remote anywhere in Australia", "Any".
4. **Industries** (multi-select): each industry the Employer notes state, "Any regulated essential service", "Any". If no Employer note states an industry, offer only the last two.
5. **Pay floor:** "Skip (recommended)", "Type a number".
6. **Deal-breakers:** "None", "No fixed-term contracts", "No more than 2 days in the office", "Type my own".

If I type "that's enough", stop asking and save what you have.

## 4. Write Preferences.md
- Keep the headings exactly as they are. Keep every line that was already filled. Fill the blank lines under Roles I want, Level, Locations, Work mode, Industries I want, Pay (Floor only, Target stays blank unless I typed one), and Deal-breakers.
- "No fixed-term contracts" also sets Work type to "permanent".
- Leave the other sections as they are.
- Set `set: yes` and `updated:` to today's date.

## 5. Reply
At most 6 lines: the filled lines in short form, then 'Next, type "Find jobs for me, quick".'
