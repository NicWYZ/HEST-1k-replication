#!/bin/bash
# Round 6 cheatsheet track: after each batch of trials (instruction section 5).
# 1. The filter's log: no host but the API may have been allowed.
# 2. Credential and canary scan of every file about to be committed.
# 3. Commit and push this stage's results to the session's branch.
# 4. Copy this stage's compressed transcripts into the private repository
#    clone under transcripts/<STAGE>/, commit and push there.
#   round6_cheatsheet_batch_push.sh STAGE BRANCH MSGFILE
set -euo pipefail
STAGE=$1; BRANCH=$2; MSG=$3
REPO=/home/user/HEST-1k-replication; DATA=/home/user/hest-r6-data
OTHER=$(awk -F'\t' '$2=="ALLOW" && $3 !~ /^CONNECT api\.anthropic\.com:443 /' /srv/r6_private/filter.log | wc -l)
[ "$OTHER" -eq 0 ] || { echo "filter allowed a host other than the API"; exit 1; }
cd $REPO
FILES=$(git ls-files -mo --exclude-standard -- results/round6/cheatsheet/$STAGE)
if [ -n "$FILES" ]; then
  python3 code/scripts/round6_cheatsheet_scan.py files $FILES --out /srv/r6_private/batch_scan.csv >/dev/null || {
    if grep -q -E "sk-ant|eyJ|Bearer|canary" /srv/r6_private/batch_scan.csv; then echo "credential or canary in results"; exit 1; fi; }
  git add -- results/round6/cheatsheet/$STAGE
  git commit -q -F "$MSG"
  git push -q origin $BRANCH
fi
mkdir -p $DATA/transcripts/$STAGE
cp -n /srv/r6_private/transcripts/$STAGE/*.jsonl.gz $DATA/transcripts/$STAGE/ 2>/dev/null || true
cd $DATA
if [ -n "$(git status --porcelain)" ]; then
  git add transcripts/$STAGE
  git commit -q -F "$MSG"
  git push -q origin HEAD
fi
echo "pushed: $(git -C $REPO log --oneline -1) | data $(git log --oneline -1)"
