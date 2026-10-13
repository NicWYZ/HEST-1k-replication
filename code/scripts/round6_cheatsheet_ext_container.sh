#!/bin/sh
# Round 6 extension, cheatsheet track: start the trial container on the Mac and
# the filtering proxy inside it (instruction 6.5). Run from the clone's root.
#
#   sh code/scripts/round6_cheatsheet_ext_container.sh
#
# Mounts, and nothing else: the clone read-only at /repo, the trial folders at
# /trials, the private folder at /private, the harness's outputs at /results.
# The harness runs as the unprivileged user `node` with every capability
# dropped. bwrap needs user namespaces (seccomp and apparmor unconfined) and a
# /proc without Docker's masked paths (systempaths=unconfined). --privileged
# and SYS_ADMIN are not needed.
set -eu
H="$HOME/hest-1k"
docker rm -f r6ext >/dev/null 2>&1 || true
docker run -d --name r6ext --user node \
  --security-opt seccomp=unconfined --security-opt apparmor=unconfined \
  --security-opt systempaths=unconfined --cap-drop ALL \
  -v "$PWD":/repo:ro -v "$H/r6ext_trials":/trials -v "$H/r6ext_private":/private \
  -v "$H/r6ext_results":/results \
  r6ext:1
docker exec r6ext sh -c 'cp /repo/code/scripts/round6_cheatsheet_ext_proxy_start.sh /srv/r6_proxy/start.sh && chmod 755 /srv/r6_proxy/start.sh && mkdir -p /private/logs'
docker exec -d r6ext python3 /repo/code/scripts/round6_cheatsheet_ext_filter_proxy.py \
  /srv/r6_proxy/filter.sock /private/logs/filter.log --direct
sleep 1
docker exec r6ext sh -c 'ls -l /srv/r6_proxy && tail -1 /private/logs/filter.log'
