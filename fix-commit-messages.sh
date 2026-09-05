#!/bin/bash
# Commits the English comment conversion and rewrites the two Hinglish
# commit messages, then force-pushes. Safe to re-run: it tags the current
# state first so nothing is lost.
set -e
cd "$(dirname "$0")"

echo "==> Safety tag on current HEAD"
git tag -f backup-hinglish-history HEAD
echo "    backup-hinglish-history -> $(git rev-parse --short HEAD)"

echo "==> Committing English comment conversion"
git add -A
git commit -q -F .git/rewrite-msgs/msg3.txt

echo "==> Rewriting the two Hinglish commit messages"
FILTER_BRANCH_SQUELCH_WARNING=1 \
  git filter-branch -f --msg-filter 'python3 .git/rewrite-msgs/filter.py' bb4db21..HEAD

echo
echo "==> New history:"
git log --format='%h  %s' bb4db21..HEAD

echo
read -p "Force-push these to origin/main? [y/N] " ok
[ "$ok" = "y" ] || { echo "Skipped. Run: git push --force-with-lease origin main"; exit 0; }
git push --force-with-lease origin main
echo "Done."
