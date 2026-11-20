---
name: job-scout
description: Find jobs that fit me from my career graph and write a shortlist with a % fit. Use for /job-scout, 'Run my job scout now', 'Find jobs for me', 'Score the ad in Inbox'.
argument-hint: "[quick | score | auto]"
allowed-tools: WebSearch, WebFetch, Read, Write, Edit, Glob, Grep
---

Read `Job Scout/Job Scout.md` and `Job Scout/Fit Rubric.md` in this folder and follow them step by step.

Run type: $ARGUMENTS

- Nothing, or "full": a full run.
- `quick`: a quick run (the limits are in the Run types table in Job Scout.md).
- `score`: score mode. Score only the job ads saved in Inbox and add them to today's shortlist.
- `auto` (can be combined with any of the above, for example `quick auto`): never ask, never wait for an answer. Fill missing preferences as Job Scout.md step 1 says. Scheduled runs always use `auto`.

Lines in `Job Scout/Preferences.md` that Grill me or I already filled are my answers. Never overwrite them, even when `set: no`. Fill only blank lines.

Also follow the rules in `CLAUDE.md` in this folder. Write only inside `Job Scout/`. If `Job Scout/Job Scout.md` is missing, stop and say so.
