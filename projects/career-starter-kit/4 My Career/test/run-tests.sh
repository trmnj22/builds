#!/bin/bash
# Copies the starter to a temp folder and runs each command headless.
#
# Usage:
#   ./run-tests.sh            base, tailor, scout setup, quick scout, then the graph checks
#   ./run-tests.sh workflow   the ultracode build (/build-graph auto) on a fresh copy
#   ./run-tests.sh rerun      builds twice on one copy, checks nothing was duplicated
#   ./run-tests.sh swap       builds Sam, swaps in a made-up CV, checks Sam moved to Old builds
#
# Needs the claude CLI signed in, and python3. Mac (bash). Logs are stream-json.
set -u
MODE="${1:-all}"
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$HERE/../My Career"
RUN="${TMPDIR:-/tmp}"
RUN="${RUN%/}/my-career-test-$MODE-$(date +%Y%m%d-%H%M%S)"
TOOLS="Read,Write,Edit,Glob,Grep,WebSearch,WebFetch,Agent,Skill"
FAILED=0

command -v claude >/dev/null 2>&1 || { echo "claude CLI not found"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "python3 not found"; exit 1; }

mkdir -p "$RUN" && cp -R "$SRC" "$RUN/My Career" && cd "$RUN/My Career" || exit 1
echo "Test copy: $RUN/My Career"

step(){ name="$1"; shift; t0=$(date +%s)
  claude -p "$1" --permission-mode acceptEdits --allowedTools "$TOOLS" --output-format stream-json --verbose > "$RUN/log-$name.jsonl" 2>&1
  rc=$?; echo "== $name: exit $rc in $(( $(date +%s)-t0 ))s"
  if [ "$rc" -ne 0 ]; then FAILED=1; fi; }

checkgraph(){ label="$1"
  python3 -I "$HERE/check_graph.py" "$RUN/My Career" | tee "$RUN/check-$label.txt"
  rc=${PIPESTATUS[0]}
  if [ "$rc" -ne 0 ]; then FAILED=1; fi; }

# Counts notes the build writes (type folders plus Profile, Index, Build log), not About notes
count_notes(){
  find Sources Roles Employers Achievements Skills Stories Themes Education \
    Certifications Recommendations Gaps -type f -name "*.md" ! -name "About *" 2>/dev/null | wc -l | tr -d " "
}

case "$MODE" in
  all)
    step base   "/career-base auto"
    checkgraph base
    step tailor "/tailor-cv auto"
    step setup  "/scout-setup auto"
    step scout  "/job-scout quick auto"
    checkgraph all
    if ls "Job Scout/Shortlists/Shortlist "*.md >/dev/null 2>&1; then
      echo "PASS  a shortlist was written"
    else
      echo "FAIL  no shortlist in Job Scout/Shortlists"
      FAILED=1
    fi
    ;;

  workflow)
    TOOLS="$TOOLS,Workflow"
    step base "/build-graph auto"
    if [ -f "Build log.md" ] && grep -qiE "^- How:.*workflow" "Build log.md"; then
      checkgraph workflow
    else
      echo "Workflow path needs an interactive test"
      echo "(Headless -p did not run the saved workflow. Run /build-graph in the desktop Code tab with ultracode on.)"
      if [ -f "Build log.md" ]; then
        echo "A build did run, by another path:"
        grep -i "^- How:" "Build log.md"
        checkgraph workflow-fallback
      fi
    fi
    ;;

  rerun)
    step base1 "/career-base auto"
    first=$(count_notes)
    checkgraph rerun-1
    step base2 "/career-base auto"
    second=$(count_notes)
    checkgraph rerun-2
    echo "Notes after first build: $first, after second build: $second"
    if [ "$first" != "$second" ]; then
      echo "FAIL  note count changed on a rerun"
      FAILED=1
    else
      echo "PASS  note count unchanged on a rerun"
    fi
    dups=$(find . -path ./.claude -prune -o -type f \( -name "* 1.md" -o -name "* 2.md" \) -print)
    if [ -n "$dups" ]; then
      echo "FAIL  duplicate notes found:"
      echo "$dups"
      FAILED=1
    else
      echo "PASS  no duplicate notes"
    fi
    if [ -d "Old builds" ]; then
      echo "FAIL  a rerun on the same person moved notes to Old builds"
      FAILED=1
    fi
    ;;

  swap)
    step base-sam "/career-base auto"
    checkgraph swap-sam
    rm -rf Inbox/"Sam Whitlock"*
    cat > "Inbox/Alex Example CV.txt" <<'CVTEXT'
Alex Example
Geelong VIC
alex.example@example.com

PROFILE
Supply chain planner who likes tidy data and short meetings.

EXPERIENCE

Planning Lead
Harbourline Foods, Geelong
Jan 2020 to present
- Led weekly demand planning for 40 product lines.
- Cut stock write-offs by 12% in 2023 by moving to weekly forecast reviews with the sales team.

Planning Analyst
Harbourline Foods, Geelong
Mar 2016 to Dec 2019
- Built the first shared forecast spreadsheet for the site.
- Reduced late orders from 9% to 6% over two years.

EDUCATION
Bachelor of Business, Corio Institute, 2015

SKILLS
Demand planning, Forecasting, Excel
CVTEXT
    step base-alex "/career-base auto"
    checkgraph swap-alex
    if ls -d "Old builds/Sam Whitlock "* >/dev/null 2>&1; then
      echo "PASS  Sam's notes are in Old builds"
    else
      echo "FAIL  no Old builds/Sam Whitlock folder"
      FAILED=1
    fi
    leftovers=$(grep -rl "Whitlock" Profile.md Index.md "Build log.md" Sources Roles Employers \
      Achievements Skills Stories Themes Education Certifications Recommendations Gaps \
      "Job Scout/Shortlists" "Job Scout/Seen.md" 2>/dev/null)
    if [ -n "$leftovers" ]; then
      echo "FAIL  notes outside Old builds still mention Whitlock:"
      echo "$leftovers"
      FAILED=1
    else
      echo "PASS  no note outside Old builds mentions Whitlock"
    fi
    ;;

  *)
    echo "Unknown mode: $MODE (use: all, workflow, rerun or swap)"
    exit 2
    ;;
esac

echo "Results in $RUN"
if [ "$FAILED" -ne 0 ]; then
  echo "OVERALL: FAIL"
  exit 1
fi
echo "OVERALL: PASS"
