#!/bin/sh
# Round 6 extension, cheatsheet track: the first program inside every trial's
# confinement (instruction 6.5, round 6's instruction 6.4 and its plan flag F18).
# The confinement has no network. socat turns the filtering proxy's Unix socket,
# bound at /run/proxy/filter.sock, into 127.0.0.1:3128, and then the arguments
# are executed.
socat TCP-LISTEN:3128,bind=127.0.0.1,fork,reuseaddr UNIX-CONNECT:/run/proxy/filter.sock &
sleep 0.3
exec "$@"
