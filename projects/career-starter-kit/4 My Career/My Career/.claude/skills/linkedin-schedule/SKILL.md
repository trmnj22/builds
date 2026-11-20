---
name: linkedin-schedule
description: Schedule, pause or change the weekly LinkedIn scan, which leaves three scored post ideas in LinkedIn/Ideas.md. It never drafts or posts. Use for /linkedin-schedule, 'Set up my LinkedIn scan every Monday at 8am', 'Pause my LinkedIn scan', 'Turn my LinkedIn scan back on'.
argument-hint: "[day and time | pause | resume]"
allowed-tools: Read, Write, Glob, AskUserQuestion, mcp__scheduled-tasks__list_scheduled_tasks, mcp__scheduled-tasks__create_scheduled_task, mcp__scheduled-tasks__update_scheduled_task
---

Set up the LinkedIn scan to run on its own once a week. Each run searches for news on my topics, scores it, and leaves three ideas in `LinkedIn/Ideas.md`. It never drafts, never opens LinkedIn and never posts. Follow the rules in `CLAUDE.md` in this folder. Never change any file in this folder, except `LinkedIn\run-linkedin-scan.cmd` on Windows after I say yes.

Request: $ARGUMENTS

## 1. Check it is ready
If `Roles/` has no notes other than `About roles.md`, reply "Type Build my career base first." and stop.

If `LinkedIn/Voice.md` says `status: empty`, carry on, and add one line to the reply: "Type Grill me or Write a LinkedIn post once first, so the scan knows who you write for."

## 2. Work out what to do
- `pause` or "Pause my LinkedIn scan": go to step 5.
- `resume` or "Turn my LinkedIn scan back on": go to step 5.
- Anything else: a day and a time. Read them from the request ("every Monday at 8am", "Tuesday 7.30am"). If there is no day, use Monday. If there is no time, use 8am. Turn them into a weekly cron line in local time, minute first, with the day as a number (Sunday 0, Monday 1 and so on to Saturday 6): Monday 8am is `0 8 * * 1`, Tuesday 7.30am is `30 7 * * 2`.

## 3. The prompt the task runs
Work out the full path of this My Career folder (the folder this session is working in). Use this prompt, with the path filled in. Always fill in the real path, never a placeholder. If the folder is in a temporary or cloud-only location (for example /tmp, or a cloud folder not kept on this computer), warn me in one line that the scan may not find it, and still fill in the path.

> Run /linkedin-post auto. If that command is not available, read .claude/skills/linkedin-post/SKILL.md in this My Career folder and follow it with the argument auto. This is a scheduled run, so never wait for an answer, never draft a post and never open LinkedIn. Write only inside the LinkedIn folder. The My Career folder is at: <full path>

## 4. Create or update the task
Pick the first that fits.

**A. A scheduled-task tool is available** (the Claude desktop app has one in the Code tab and in Cowork).
1. List the scheduled tasks. If one has the id `linkedin-scan`, update it with the new day, time and prompt. Otherwise create one with id `linkedin-scan`, title "LinkedIn scan", description "Weekly LinkedIn topic scan for my My Career folder", the cron line from step 2 and the prompt from step 3.
2. The tool cannot set the folder. In the reply, tell me to open Scheduled > LinkedIn scan and set the folder to My Career if it is not already.
3. Reply as in step 6.

**B. No scheduled-task tool, but this is the Claude desktop app.** Give the steps for the app I am in, then the reply in step 6.
- Claude Code tab: Scheduled in the left sidebar (older versions: Routines, or under More) > New task > name LinkedIn scan > paste the prompt from step 3 > Weekly > the day and time > turn on "Only on this computer" > folder My Career > permission mode Accept edits > Save > Run now once.
- Cowork: Scheduled in the left sidebar > Set up manually > name LinkedIn scan > paste the prompt from step 3 > frequency Weekly > the day and time > folder My Career > an approval mode that allows file edits > Save > Run now once. You can also type "Set up my LinkedIn scan every Monday at 8am" in the Cowork project.

**C. Command line only (a terminal, no desktop app).** The command to schedule is:

`claude -p "/linkedin-post auto" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Glob,Grep,WebSearch,WebFetch"`

It must run from inside the My Career folder. Show me the line for my computer and ask before adding it. Never add it without a clear yes. If `claude` is not found when the schedule runs, use its full path (on Mac, `which claude` shows it).
- Mac (crontab):
  `<minute> <hour> * * <day> cd "<full path>" && <command> >> "LinkedIn/scan-log.txt" 2>&1`
  If the folder is in Documents or Desktop, cron needs Full Disk Access (System Settings > Privacy and Security > Full Disk Access > add /usr/sbin/cron). Setting it up in the Claude app is easier.
- Windows (Task Scheduler): first make a file `LinkedIn\run-linkedin-scan.cmd` holding these two lines:
  `cd /d "<full path>"`
  `claude -p "/linkedin-post auto" --permission-mode acceptEdits --allowedTools "Read,Write,Edit,Glob,Grep,WebSearch,WebFetch" >> "LinkedIn\scan-log.txt" 2>&1`
  Then schedule it, with the day as MON, TUE and so on:
  `schtasks /Create /SC WEEKLY /D <DAY> /ST <HH:MM> /TN "LinkedIn scan" /TR "\"<full path>\LinkedIn\run-linkedin-scan.cmd\""`

Do not use `/loop`, because it stops when the terminal closes. Do not use cloud routines, because they cannot see this folder. Never give the scheduled run any browser tools.

## 5. Pause or resume
- With a scheduled-task tool: list the tasks, find `linkedin-scan` and set it to off (pause) or on (resume). Reply in one line with the new state.
- Without one: tell me where the switch is. Claude desktop: Scheduled in the left sidebar > LinkedIn scan > the on and off switch. Mac crontab: put `#` at the start of the line to pause. Windows: Task Scheduler > LinkedIn scan > Disable or Enable.
- To delete the task, open it in the Scheduled list and delete it yourself. Never delete it for me.

## 6. Reply
At most 8 lines:
1. "Your LinkedIn scan will run every <day> at <time> on this computer."
2. Check three things in the task: the folder is My Career, the permission mode is Accept edits or Auto, and it runs only on this computer.
3. Your computer must be awake and Claude open. If it was asleep or closed, the run happens once when it next wakes.
4. "Click Run now once and approve anything it asks, so the next run won't stop."
5. Each run adds signals to `LinkedIn/Topic radar.md` and three scored ideas to `LinkedIn/Ideas.md`. It never drafts or posts.
6. "When you like an idea, type Write a LinkedIn post about idea 2 (or any number)."
