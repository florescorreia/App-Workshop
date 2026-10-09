#!/bin/sh
# One-time copy into a NEW dedicated database volume, never a live restore.
set -eu
cd /home/ideaflow
uid=$(id -u ideaflow)
as_app() { runuser -u ideaflow -- env XDG_RUNTIME_DIR="/run/user/$uid" "$@"; }
if as_app podman volume exists ideaflow-pgdata; then
    echo 'Database volume already exists: refusing initial copy.' >&2
    exit 1
fi
stage=/home/ubuntu/ideaflow-deploy-20261009
postgres=$(as_app podman image inspect postgres:17.6-bookworm --format '{{.Id}}')
backend=$(as_app podman image inspect ideaflow-backend:1.0.0 --format '{{.Id}}')
frontend=$(as_app podman image inspect ideaflow-frontend:1.0.0 --format '{{.Id}}')
for name in postgres backend frontend; do
    sed -i "s|@POSTGRES_IMAGE@|$postgres|; s|@BACKEND_IMAGE@|$backend|; s|@FRONTEND_IMAGE@|$frontend|" "$stage/ideaflow-$name.container"
done
sh "$stage/install-release.sh" "$stage"
install -d "/etc/systemd/system/user@$uid.service.d"
sed "s/1001/$uid/g" "$stage/zz-ideaflow.conf" > "/etc/systemd/system/user@$uid.service.d/zz-ideaflow.conf"
chmod 644 "/etc/systemd/system/user@$uid.service.d/zz-ideaflow.conf"
systemctl daemon-reload
for file in "$stage"/demo-*.json; do
    [ -f "$file" ] || continue
    name=$(basename "$file" | cut -c6-)
    install -o ideaflow -g ideaflow -m 644 "$file" "/home/ideaflow/demo/$name"
done
as_app systemctl --user start ideaflow-postgres.service
as_app podman cp /home/ideaflow/backups/initial-workspace-20261009.dump ideaflow-postgres:/tmp/initial.dump
as_app podman exec ideaflow-postgres pg_restore -U ideaflow_migrator -d ideaflow --exit-on-error --no-owner --no-acl /tmp/initial.dump
as_app systemctl --user start app-ideaflow.target
as_app systemctl --user start ideaflow-backup.timer
as_app podman ps
echo 'Initial database copied and full application ready.'
