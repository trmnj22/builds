#!/usr/bin/env bash
# Runs scripts/check.sh before every commit and every push.
set -e; cd "$(git rev-parse --show-toplevel)"
for h in pre-commit pre-push; do printf '#!/usr/bin/env bash\nexec "$(git rev-parse --show-toplevel)/scripts/check.sh"\n' > .git/hooks/$h; chmod +x .git/hooks/$h; done
echo "hooks installed"
