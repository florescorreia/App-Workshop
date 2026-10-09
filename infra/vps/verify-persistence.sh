#!/bin/sh
# Run as root. Stop/start only this stack and remove only a generated test DB.
set -eu
cd /home/ideaflow
uid=$(id -u ideaflow)
as_app() { runuser -u ideaflow -- env XDG_RUNTIME_DIR="/run/user/$uid" "$@"; }
check() {
    as_app podman cp /home/ideaflow/bin/verify-workspace.py ideaflow-backend:/tmp/verify-workspace.py
    as_app podman cp /home/ideaflow/handover/source-report.json ideaflow-backend:/tmp/source-report.json
    as_app podman exec -e PYTHONPATH=/app ideaflow-backend python /tmp/verify-workspace.py --expected /tmp/source-report.json --output /handover/vps-report.json
}
as_app /usr/local/libexec/cockpit-app-stacks list
as_app /usr/local/libexec/cockpit-app-stacks stop app-ideaflow.target
as_app systemctl --user stop ideaflow-frontend.service ideaflow-backend.service ideaflow-postgres.service
attempt=0
until [ "$(as_app podman ps -q | wc -l)" -eq 0 ]; do
    attempt=$((attempt + 1)); [ "$attempt" -lt 30 ] || exit 1
    sleep 2
done
if curl --fail --silent http://127.0.0.1:18081/api/health/ready; then exit 1; fi
as_app systemctl --user reset-failed
as_app /usr/local/libexec/cockpit-app-stacks start app-ideaflow.target
test "$(as_app podman ps -q | wc -l)" -eq 3
check
# Restart the dedicated user manager to exercise unattended stack autostart.
systemctl restart "user@$uid.service"
attempt=0
until curl --max-time 5 --fail --silent https://vps-8104e6c8.vps.ovh.us:8443/api/health/ready; do
    attempt=$((attempt + 1)); [ "$attempt" -lt 80 ] || exit 1
    sleep 2
done
check
as_app systemctl --user start ideaflow-backup.service
backup=$(find /home/ideaflow/backups -name 'ideaflow-*.dump' -type f | sort | tail -1)
test -n "$backup"
database="ideaflow_restore_$(date -u +%Y%m%d%H%M%S)"
cleanup() { as_app podman exec ideaflow-postgres dropdb -U ideaflow_migrator --if-exists "$database"; }
trap cleanup EXIT
as_app podman cp "$backup" ideaflow-postgres:/tmp/restore-test.dump
as_app podman exec ideaflow-postgres createdb -U ideaflow_migrator "$database"
as_app podman exec ideaflow-postgres pg_restore -U ideaflow_migrator -d "$database" --exit-on-error --no-owner --no-acl /tmp/restore-test.dump
as_app podman exec ideaflow-backend python -m app.restore_check --database "$database"
check
as_app systemctl --user is-enabled app-ideaflow.target ideaflow-backup.timer
as_app systemctl --user list-timers ideaflow-backup.timer --no-pager
as_app podman ps
as_app podman stats --no-stream
for container in ideaflow-postgres ideaflow-backend ideaflow-frontend; do
    echo "$container cgroup limits:"
    as_app podman exec "$container" cat /sys/fs/cgroup/memory.max /sys/fs/cgroup/cpu.max
done
as_app /usr/local/libexec/cockpit-app-stacks list
echo "Verified stack stop/start, user-manager restart, fingerprints, replay and isolated restore. Backup: $backup"
