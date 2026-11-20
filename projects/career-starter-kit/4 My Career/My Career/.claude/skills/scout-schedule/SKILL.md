---
name: scout-schedule
description: Schedule, pause or change the daily job scout. Use for /scout-schedule, 'Set up my Job Scout to run every day at 7am', 'Pause my Job Scout', 'Turn my Job Scout back on'.
argument-hint: "[time | pause | resume]"
allowed-tools: Read, Write, Glob, AskUserQuestion, mcp__scheduled-tasks__list_scheduled_tasks, mcp__scheduled-tasks__create_scheduled_task, mcp__scheduled-tasks__update_scheduled_task, mcp__scheduled-tasks__run_scheduled_task
---

Set up the job scout to run on its own every day. Follow the rules in `CLAUDE.md` in this folder. Never change any file in this folder, except what scout-setup writes in step 1 and `Job Scout\run-scout.cmd` on Windows after I say yes.

Request: $ARGUMENTS

## 1. Check it is ready
- If `Roles/` has no notes other than `About roles.md`, reply "Type Build my career base first." and stop.
- If `Job Scout/Preferences.md` says `set: no`, run the `scout-setup` skill first (if it is not available, open `.claude/skills/scout-setup/SKILL.md` and follow it). It uses my Grill me answers and asks only what is still blank. Then come back here. With `auto`, run it as `scout-setup auto`.

## 2. Work out what to do
- `pause` or "Pause my Job Scout": go to step 5.
- `resume` or "Turn my Job Scout back on": go to step 5.
- Anything else: a time. Read it from the request ("7am", "6.30am", "19:00"). If there is no time, use 7am. Turn it into a daily cron line in local time, minute first: 7am is `0 7 * * *`, 6.30am is `30 6 * * *`.

## 3. The prompt the task runs
Work out the full path of this My Career folder (the folder this session is working in). Use this prompt, with the path filled in:

> Run /job-scout auto. If that command is not available, read .claude/skills/job-scout/SKILL.md in this My Career folder and follow it. This is a scheduled run, so never wait for an answer. The My Career folder is at: <full path>

## 4. Create or update the task
Pick the first that fits.

**A. A scheduled-task tool is available** (the Claude desktop app has one in the Code tab and in Cowork).
1. List the scheduled tasks. If one has the id `job-scout`, update it with the new time and prompt. Otherwise create one with id `job-scout`, title "Job Scout", description "Daily job scout for my My Career folder", the cron line from step 2 and the prompt from step 3.
2. The tool cannot set the folder. In the reply, tell me to open Scheduled > Job Scout and set the folder to My Career if it is not already.
3. Reply as in step 6.

**B. No scheduled-task tool, but this is the Claude desktop app.** Give the steps for the app I am in, then the reply in step 6.
- Claude Code tab: Scheduled in the left sidebar (older versions: Routines, or under More) > New task > name Job Scout > paste the prompt from step 3 > Daily > the time > turn on "Only on this computer" > folder My Career > permission mode Accept edits > Save > Run now once.
- Cowork: Scheduled in the left sidebar > Set up manually > name Job Scout > paste the prompt from step 3 > frequency Daily > the time > folder My Career > an approval mode that allows file edits > Save > Run now once. You can also type "Set up my Job Scout to run every day at 7am" in the Cowork project.

**C. Command line only (a terminal, no desktop app).** The command to schedule is:

`claude -p "/job-scout auto" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Glob,Grep,WebSearch,WebFetch"`

It must run from inside the My Career folder. Show me the line for my computer and ask before adding it. Never add it without a clear yes. If `claude` is not found when the schedule runs, use its full path (on Mac, `which claude` shows it).
- Mac (crontab):
  `<minute> <hour> * * * cd "<full path>" && <command> >> "Job Scout/scout-log.txt" 2>&1`
  If the folder is in Documents or Desktop, cron needs Full Disk Access (System Settings > Privacy and Security > Full Disk Access > add /usr/sbin/cron). Setting it up in the Claude app is easier.
- Windows (Task Scheduler): first make a file `Job Scout\run-scout.cmd` holding these two lines:
  `cd /d "<full path>"`
  `claude -p "/job-scout auto" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Glob,Grep,WebSearch,WebFetch" >> "Job Scout\scout-log.txt" 2>&1`
  Then schedule it:
  `schtasks /Create /SC DAILY /ST <HH:MM> /TN "Job Scout" /TR "\"<full path>\Job Scout\run-scout.cmd\""`

Do not use `/loop`, because it stops when the terminal closes. Do not use cloud routines, because they cannot see this folder.

Ultracode never applies to scheduled runs. The scout does not need it.

## 5. Pause or resume
- With a scheduled-task tool: list the tasks, find `job-scout` and set it to off (pause) or on (resume). Reply in one line with the new state.
- Without one: tell me where the switch is. Claude desktop: Scheduled in the left sidebar > Job Scout > the on and off switch. Mac crontab: put `#` at the start of the line to pause. Windows: Task Scheduler > Job Scout > Disable or Enable.
- To delete the task, open it in the Scheduled list and delete it yourself. Never delete it for me.

## 6. Reply
At most 8 lines:
1. "Job Scout will run every day at <time> on this computer."
2. Check three things in the task: the folder is My Career, the permission mode is Accept edits or Auto, and it runs only on this computer.
3. Your computer must be awake and Claude open. If it was asleep or closed, the run happens once when it next wakes.
4. "Today click Run now once and approve anything it asks, so tomorrow's run won't stop."
5. Each run adds to `Job Scout/Shortlists/Shortlist YYYY-MM-DD.md`.
