#!/bin/bash
# Rebuilds My-Career.zip from the My Career folder.
# Keeps the hidden .claude folder, .gitignore and the LinkedIn folder. Drops Mac junk and the scout and scan logs.
# Refuses to zip if a build, a tailored CV, a LinkedIn draft, a scout run or a file in Inbox other than the sample is still inside the folder.
cd "$(dirname "$0")" || exit 1
R="My Career"
problems=()

[ -d "$R/.claude" ] || problems+=(".claude folder is missing")
[ -f "$R/.gitignore" ] || problems+=(".gitignore is missing")
[ -d "$R/LinkedIn" ] || problems+=("LinkedIn folder is missing")

[ -f "$R/Profile.md" ] && problems+=("Profile.md")
[ -f "$R/Build log.md" ] && problems+=("Build log.md")
[ -d "$R/Old builds" ] && problems+=("Old builds/")
grep -q '^type: index' "$R/Index.md" 2>/dev/null && problems+=("Index.md is a built map, not the placeholder")

# Inbox may hold only About inbox.md and the fictional Sam Whitlock sample files
while IFS= read -r f; do problems+=("$f (only About inbox.md and the Sam Whitlock sample may be in Inbox)"); done < <(find "$R/Inbox" -mindepth 1 -maxdepth 1 ! -name 'About inbox.md' ! -name 'Sam Whitlock *' ! -name '.DS_Store' 2>/dev/null)
[ -d "$R/Inbox/Sam Whitlock LinkedIn data export" ] && while IFS= read -r f; do problems+=("$f is not part of the sample export"); done < <(find "$R/Inbox/Sam Whitlock LinkedIn data export" -type f ! -name '*.csv' ! -name '.DS_Store' 2>/dev/null)

# Built notes in the type folders (About notes are fine)
for d in Sources Roles Employers Achievements Skills Stories Themes Education Certifications Recommendations Gaps; do
  while IFS= read -r f; do problems+=("$f"); done < <(find "$R/$d" -type f -name '*.md' ! -name 'About *.md' 2>/dev/null)
done

# Anything personal in folders that ship with only an About note
for d in "Targets" "Job Scout/Shortlists" "LinkedIn/Drafts" "LinkedIn/Posted"; do
  while IFS= read -r f; do problems+=("$f"); done < <(find "$R/$d" -mindepth 1 ! -name 'About *.md' ! -name '.DS_Store' 2>/dev/null)
done

if [ -f "$R/Job Scout/Seen.md" ]; then
  rows=$(grep -c '^|' "$R/Job Scout/Seen.md")
  [ "$rows" -gt 2 ] && problems+=("Job Scout/Seen.md has table rows")
fi
grep -q '^set: yes' "$R/Job Scout/Preferences.md" 2>/dev/null && problems+=("Job Scout/Preferences.md has set: yes")
grep -q '^status: empty' "$R/LinkedIn/Voice.md" 2>/dev/null || problems+=("LinkedIn/Voice.md is not the blank version")
grep -q '^## 20' "$R/LinkedIn/Ideas.md" 2>/dev/null && problems+=("LinkedIn/Ideas.md has dated ideas")
# LinkedIn engine notes ship with empty tables. A row starting with a date is personal.
for f in "Topic radar.md" "Topic backlog.md" "Already said.md" "About LinkedIn.md"; do
  [ -f "$R/LinkedIn/$f" ] || problems+=("LinkedIn/$f is missing")
  grep -q '^| 20' "$R/LinkedIn/$f" 2>/dev/null && problems+=("LinkedIn/$f has dated rows")
done
grep -A3 '^## What I scan for' "$R/LinkedIn/Topic radar.md" 2>/dev/null | grep -q '^- [^ ]' && problems+=("LinkedIn/Topic radar.md has scan topics filled in")
[ -f "$R/LinkedIn/run-linkedin-scan.cmd" ] && problems+=("LinkedIn/run-linkedin-scan.cmd")
[ -f "$R/Job Scout/run-scout.cmd" ] && problems+=("Job Scout/run-scout.cmd")
[ -f "$R/.claude/settings.local.json" ] && problems+=(".claude/settings.local.json")

# Plain-English rules: no em dashes or semicolons in any note or instruction file.
# CSS in CV style.md is code. The humanizer skill quotes the characters it removes, so it is skipped.
# Lines that quote the check's own search pattern are allowed.
while IFS= read -r f; do problems+=("$f has an em dash or semicolon"); done < <(grep -rn --include='*.md' -e $'\xe2\x80\x94' -e ';' "$R" 2>/dev/null | grep -v 'CV style.md' | grep -v '/.claude/skills/humanizer/' | grep -v 'x{2014}' | cut -d: -f1 | sort -u)

if [ ${#problems[@]} -gt 0 ]; then
  echo "Not zipping. The folder still has built or personal files:"
  printf '  %s\n' "${problems[@]}"
  echo "Remove them (or test in a copy) and run this again."
  exit 1
fi

rm -f My-Career.zip
zip -rq My-Career.zip "$R" -x "*.DS_Store" -x "__MACOSX*" -x "$R/Job Scout/scout-log.txt" -x "$R/LinkedIn/scan-log.txt" || exit 1
for must in "$R/.gitignore" "$R/.claude/settings.json" "$R/LinkedIn/"; do
  unzip -Z1 My-Career.zip | grep -qxF "$must" || { echo "Zip is missing $must"; exit 1; }
done
echo "Entries in My-Career.zip: $(unzip -Z1 My-Career.zip | wc -l | tr -d ' ')"
