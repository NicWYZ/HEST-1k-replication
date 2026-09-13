#!/bin/bash
# Commit and push the tracked (text) portion of the replication tree.
# Usage: bash code/scripts/repo_commit.sh "commit message"
set -euo pipefail
ROOT=/work/users/w/e/weiyang/hest_replication
MSG="${1:?usage: repo_commit.sh \"message\"}"
MAXBYTES=$((50*1024*1024))   # refuse anything over 50 MB

cd "$ROOT"
source "$ROOT/env/miniforge3/etc/profile.d/conda.sh"; conda activate hest
python "$ROOT/code/scripts/make_manifest.py"

git add -A


# --- size guard: block a large file that slipped past .gitignore ---
BIG=$(git diff --cached --name-only --diff-filter=AM | while read -r f; do
        [ -f "$f" ] || continue
        sz=$(stat -c%s "$f")
        if [ "$sz" -gt "$MAXBYTES" ]; then echo "$sz $f"; fi
      done)
if [ -n "$BIG" ]; then
  echo "REFUSING TO COMMIT - files over 50MB staged:"; echo "$BIG"
  echo "Add them to .gitignore and record them in MANIFEST.md instead."
  git reset >/dev/null; exit 1
fi

# --- guard: never commit gated-derived binaries ---
BAD=$(git diff --cached --name-only --diff-filter=AM \
      | grep -E '\.(pkl|h5|h5ad|parquet|safetensors|pt|pth)$' || true)
if [ -n "$BAD" ]; then
  echo "REFUSING TO COMMIT - gated/binary artifacts staged:"; echo "$BAD"
  git reset >/dev/null; exit 1
fi

if git diff --cached --quiet; then echo "nothing to commit"; exit 0; fi
git commit -q -m "$MSG"   # identity comes from repo-local git config
echo "committed: $(git log -1 --oneline)"
git diff --stat HEAD~1 HEAD 2>/dev/null | tail -3 || true
