#!/bin/bash
# Rewrites the two Hinglish commit messages into English, then force-pushes.
# A backup tag is created first, so nothing is lost.
set -e
cd "$(dirname "$0")"

REPO="$(git rev-parse --show-toplevel)"
FILTER="$REPO/.git/rewrite-msgs/filter.py"   # absolute: filter-branch runs in a temp dir

echo "==> Safety tag on current HEAD"
git tag -f backup-hinglish-history HEAD >/dev/null
echo "    backup-hinglish-history -> $(git rev-parse --short HEAD)"

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "==> Committing pending changes"
  git add -A
  git commit -q -F .git/rewrite-msgs/msg3.txt
else
  echo "==> Nothing pending to commit, skipping"
fi

echo "==> Rewriting the two Hinglish commit messages"
FILTER_BRANCH_SQUELCH_WARNING=1 \
  git filter-branch -f --msg-filter "python3 '$FILTER'" bb4db21..HEAD

echo
echo "==> New history:"
git log --format='%h  %s' bb4db21..HEAD
echo
echo "==> Body check (commit 1):"
git log --format='%b' -1 "$(git log --format=%H --grep='^fix: DB resilience' -1)" | head -4

echo
read -p "Force-push to origin/main? [y/N] " ok
[ "$ok" = "y" ] || { echo "Skipped. To push later: git push --force-with-lease origin main"; exit 0; }
git push --force-with-lease origin main
echo "Done."
