#!/bin/sh
set -eu
umask 077
stamp=$(date -u +%Y%m%dT%H%M%SZ)
backup="/home/ideaflow/backups/ideaflow-$stamp.dump"
test ! -e "$backup"
podman exec ideaflow-postgres pg_dump -U ideaflow_migrator -d ideaflow -Fc --no-owner --no-acl > "$backup.partial"
test -s "$backup.partial"
mv "$backup.partial" "$backup"
sha256sum "$backup" > "$backup.sha256"
echo "$backup"
# Retention is deliberate operator work: no automated file deletion.
