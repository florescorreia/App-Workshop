#!/bin/sh
set -eu
case "$1" in ideaflow-postgres|ideaflow-backend|ideaflow-frontend) ;; *) exit 2 ;; esac
attempt=0
while [ "$attempt" -lt 80 ]; do
    if [ "$(podman inspect --format '{{.State.Health.Status}}' "$1")" = healthy ]; then exit 0; fi
    attempt=$((attempt + 1))
    sleep 2
done
echo "Readiness timeout for $1" >&2
exit 1
