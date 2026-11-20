# My Career

A Claude project that turns your CV and LinkedIn into a knowledge graph of your career, linked notes with every fact traced to the file it came from. It uses that graph to tailor CVs to job ads, look for jobs that fit you each morning, draft LinkedIn posts in your voice and test career decisions.

Everything runs in the Claude desktop app on your own computer. It ships with files for Sam Whitlock, a made-up person, so you can try it before you add your own.

**New here? Read [START HERE.md](START HERE.md).** It takes two minutes.

## Folder map
```
My Career/
  README.md          this page
  START HERE.md      the steps for your first hour
  CLAUDE.md          the rules every skill follows, and the command table
  CHANGELOG.md       what changed in each version
  .gitignore         keeps your files and notes out of any git repo
  Inbox/             your CV, LinkedIn and job ads go here (Sam's files to start)
  Index.md           the map of your career, written by the build
  Sources/ Roles/ Employers/ Achievements/ Skills/ Stories/
  Themes/ Education/ Certifications/ Recommendations/ Gaps/
                     one note per thing, written by the build
  Targets/           one folder per job: Fit, CV and any board memo
  Job Scout/         your job preferences, the scout's rubric and shortlists
  LinkedIn/          your LinkedIn engine: voice, topic radar, backlog, ideas,
                     drafts, posted posts and what you have already said
  Templates/         the shape of every note
  .claude/
    skills/          career-base, grill-me, tailor-cv, job-scout, scout-setup,
                     scout-schedule, linkedin-post, linkedin-schedule,
                     board-of-advisers, humanizer
    agents/          helpers for checking facts and for the board of advisers
    workflows/       the full build for ultracode
```
`workflows/build-graph.js` is a script for Claude Code's Workflow tool, not a Node program. It runs only inside that tool, so `node` on its own reports errors for its top-level `await` and `return`.

On a Mac, `.claude` and `.gitignore` are hidden. Press Cmd+Shift+full stop in Finder to see them. Leave them where they are.

## Commands
Type the sentence in the Claude app, or the short command in the Code tab.

| Type this | Or | What it does |
|---|---|---|
| Build my career base | `/career-base` | Quick build from Inbox in about 5 to 7 minutes, then Grill me starts |
| Grill me | `/grill-me` | Asks what your files leave out, one click at a time, and saves your answers |
| Tailor my CV to the ad in Inbox | `/tailor-cv` | Writes Fit.md and a CV for that job, every line traced to a note |
| Set up my Job Scout to run every day at 7am | `/scout-schedule 7am` | Runs the scout each morning on this computer |
| Run my job scout now | `/job-scout` | Searches now and writes a shortlist with % fit |
| Write a LinkedIn post | `/linkedin-post` | Three scored ideas from this week's news and your notes, then a draft. You post it yourself |
| Set up my LinkedIn scan every Monday at 8am | `/linkedin-schedule` | Leaves three scored post ideas each week. Never drafts or posts |
| Build my full career base | `/career-base full` | The slower build with independent checkers. Best with ultracode |
| Ask my board of advisers | `/board-of-advisers` | Four advisers test a decision, such as "Should I take this job?" |
| Start fresh with my own files | `/career-base fresh` | Moves the notes built so far into Old builds |

More commands, such as Pause my Job Scout, Score the ad in Inbox, Fill it, I posted it and Log my LinkedIn numbers, are in CLAUDE.md. How the LinkedIn engine works is in LinkedIn/About LinkedIn.md.

## Privacy
- Everything stays in this folder on your computer. Claude reads your files under your own account. Nothing is uploaded anywhere else.
- Job searches use job titles, skills and places, never your name or employers.
- Claude drafts. It never posts to LinkedIn, sends an email or applies for a job. If you say Fill it and Claude in Chrome is connected, it fills the LinkedIn composer in your own Chrome and stops at the Post button. It never types a password.
- `.gitignore` keeps Inbox, your built notes, Targets, your LinkedIn drafts, posts, radar, backlog and Already said, Job Scout results and your preferences out of any git repo you make from this folder. Only the starter files would be shared.
- Shortlists hold real employer names from public ads, and your notes hold your career. Think before you share the folder.

## Works with
Claude desktop app on Mac or Windows, on a paid plan (Pro or above). Code tab (Claude Code) is the main path. Cowork works too, see START HERE. Obsidian is optional, for viewing the notes as a graph.

## Credits
- The humanizer skill is a short plain-English editing pass written for this kit. Swap in your own if you prefer, at the same path.
- Sam Whitlock, the employers, schools, club and recommender in Sam's files, and the company in the job ad are all made up. Any likeness to a real person or organisation is chance.
