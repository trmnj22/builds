# Step 1. Scan

## Purpose

Find out what is in Inbox, whose files they are, and what the graph already holds, so the later steps know what to read and what to update.

## Input

- The `Inbox` folder.
- Notes already built in this folder: `Index.md`, `Profile.md`, and the notes in `Sources/`, `Roles/`, `Employers/`, `Achievements/`, `Skills/`, `Stories/`, `Themes/`, `Education/`, `Certifications/`, `Recommendations/`, `Gaps/`.
- The mode the caller passed (`build`, `add`, `check` or `fresh`) and whether it is `auto`.

## Do

### 1. List Inbox

List everything in Inbox, and one level down inside any folder. Ignore `.DS_Store`, `desktop.ini` and files that start with `~$`.

### 2. Give every item a kind

| Kind | How to tell | Read for facts? |
|---|---|---|
| `cv` | PDF, .txt or .md that reads as a CV: a name at the top and an experience section | yes |
| `linkedin-pdf` | A PDF that has "Experience" and "Top skills", or a LinkedIn footer, or a PDF whose name contains "LinkedIn" | yes |
| `linkedin-export` | A folder that holds `Positions.csv` or `Profile.csv` | yes, one CSV at a time, see `steps/LinkedIn export.md` |
| `linkedin-zip` | A `.zip` whose name contains `LinkedInDataExport` | no. Ask the person to unzip it (Mac: double-click it, Windows: right-click > Extract All) |
| `job-ad` | Describes a job to apply for: "about the role", "you will", "apply", "closes", a pay band, "key selection criteria" | never. List it in Build log as "job ad, not used for facts" |
| `other-about-me` | A review, award, reference or project list about the person | yes |
| `unreadable` | A Word or Pages file, an image with no text, or PDF pages past 10 that cannot be read | no. Name it in the reply with "please save it as a PDF or .txt" |
| `unsure` | You cannot tell whether it is a job ad | Interactive: ask. Auto: skip it and list it in the reply |

Give each source a `label` for citations:
- `cv` is `CV`, `linkedin-pdf` is `LinkedIn PDF`, `linkedin-export` is `LinkedIn export`.
- If there are two files of the same kind, use each file name without its extension instead (for example `CV 2024` and `CV 2019`).
- Any other file: its file name without the extension.

Count pages for each PDF from what the Read tool shows. For an export, count the CSV files that will be read. Use the Read, Glob and Grep tools only. Never use Bash or a terminal command (such as pdfinfo or mdls) to count pages or read files.

### 3. Spot Sam

Sam Whitlock is the made-up example person. A source is Sam's if ANY of these is true:
- its file or folder name contains "Sam Whitlock"
- its text contains `sam.whitlock@example.com`
- its `Profile.csv` has First Name "Sam" and Last Name "Whitlock"

Sam's example job ad (`Sam Whitlock job ad - ...`) is a `job-ad`, never a source. It does not count as one of Sam's sources when you decide whether Sam's files and someone else's are both in Inbox.

Then:
- **Only Sam's sources:** build Sam's graph as normal. Step 6 starts the reply with the Sam line.
- **Sam's sources and someone else's:** never mix two people. Interactive: ask "I found Sam's example files and yours. Build from yours only?" with the options "Yes, ignore Sam's files (recommended)" and "No, build Sam's example". Auto: use only the files that are not Sam's, and say so in the reply. Mark the sources you will not read with `read: false`.

### 4. See what already exists

- Read `Index.md` if it has been built.
- Read the frontmatter (`type`, `key`, `person`, `sources`) of every note in the type folders and `Profile.md`. Keep the list of existing `key` values.
- Read every `Sources/Source - *.md` note to know which files were already read and their page counts.
- A note with no `key` in its frontmatter was made by the person. Never move, overwrite or delete it.

### 5. Build or update

- No built notes yet: this is a new build.
- Built notes for the same person: this is an update. Step 3 merges by `key`.
- In `add` mode: a source is new if it has no `Source - ...` note yet, or its page count has changed. Only new sources go to step 2.

### 6. Move an old build out of the way (only when needed)

Do this when ANY of these is true:
- `Profile.md` has a `person:` that is not the person in the sources you will read now.
- Every existing note cites only sources that are no longer in Inbox.
- The mode is `fresh`.

Move every built note into `Old builds/<person> <YYYY-MM-DD>/`, keeping the subfolders. `<person>` is the old `person:` value and the date is today. Built notes are:
- `Profile.md`, `Index.md`, `Build log.md`
- every note with a `key` in `Sources/`, `Roles/`, `Employers/`, `Achievements/`, `Skills/`, `Stories/`, `Themes/`, `Education/`, `Certifications/`, `Recommendations/`, `Gaps/`
- every folder in `Targets/` that the build or the tailor-cv command made
- every file in `Job Scout/Shortlists/` except `About shortlists.md`, because they were scored against the old person
- the table rows in `Job Scout/Seen.md` (copy the file to Old builds, then leave the header and an empty table, with "Last run: never")

Never move or change `Inbox`, `Templates`, any `About *.md` note, notes without a `key`, `Job Scout/Preferences.md` or the other Job Scout settings files. After the move, put the plain `Index.md` placeholder back:

```
# Career map
Empty until you type "Build my career base". Your map of roles, achievements, skills and stories appears here, with links to every note.
```

Say so in one line: "I moved the notes for <person> into Old builds/<person> <date>."

In `fresh` mode, stop here.

## Output

A scan list. For paths W and H, return it to the caller. For path S, keep it in mind.

- `person`: the person's name as their sources write it
- `sources`: one entry per Inbox item with `path`, `kind`, `label`, `pages` (or CSV count), `is_new`, `is_sam`, `read` (true if step 2 should read it)
- `existing_keys`: every `key` already in the graph
- `moved_to_old_builds`: the folder name, or nothing
- `notes`: one line each for unreadable files, job ads, zips, unsure files and anything else the person should know

## Done when

Every Inbox item has a kind. Unreadable items and job ads are listed with their reasons. If no source has `read: true`, stop and tell the person what to add: "Inbox has no CV yet. Put your CV in Inbox (PDF is best), then type Build my career base again."
