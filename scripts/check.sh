#!/usr/bin/env bash
# Blocks a commit or push if anything sensitive is in the repo.
# 1. gitleaks on the whole history and on staged changes.
# 2. A private deny list (client names, employer-internal words, personal terms) kept OUTSIDE this repo,
#    at ~/.config/builds-denylist.txt, one term per line. It never gets committed, because the list itself is private.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
fail=0
command -v gitleaks >/dev/null || { echo "BLOCKED: gitleaks is not installed (brew install gitleaks)"; exit 1; }
gitleaks git --no-banner --redact . || fail=1
gitleaks git --staged --no-banner --redact . 2>/dev/null || true
gitleaks dir --no-banner --redact . || fail=1
DENY="${BUILDS_DENYLIST:-$HOME/.config/builds-denylist.txt}"
if [ -f "$DENY" ]; then
  while IFS= read -r term; do
    [ -z "$term" ] || [[ "$term" == \#* ]] && continue
    if git ls-files -z | xargs -0 grep -Iil -- "$term" 2>/dev/null | grep -q .; then
      echo "BLOCKED: a deny-listed term was found in:"; git ls-files -z | xargs -0 grep -Iil -- "$term"; fail=1
    fi
  done < "$DENY"
else
  echo "BLOCKED: deny list missing at $DENY"; fail=1
fi
[ "$fail" = 0 ] && echo "check: clean" || { echo "check: BLOCKED, nothing may be published"; exit 1; }
