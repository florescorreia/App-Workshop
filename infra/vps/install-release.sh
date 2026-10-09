#!/bin/sh
# Run as root after transfer/load. Preserve all volumes and application data.
set -eu
stage=${1:?Protected staging directory required}
test "$stage" = /home/ubuntu/ideaflow-deploy-20261009
test -d /home/ideaflow
cd /home/ideaflow
uid=$(id -u ideaflow)
as_app() { runuser -u ideaflow -- env XDG_RUNTIME_DIR="/run/user/$uid" "$@"; }
for name in postgres backend; do
    install -o ideaflow -g ideaflow -m 600 "$stage/$name.env" "/home/ideaflow/.config/ideaflow/$name.env"
done
for name in wait-container.sh backup.sh healthcheck.py launch-backend.sh; do
    install -o ideaflow -g ideaflow -m 750 "$stage/$name" "/home/ideaflow/bin/$name"
done
chmod 644 /home/ideaflow/bin/healthcheck.py /home/ideaflow/bin/launch-backend.sh
for name in ideaflow.network ideaflow-postgres.container ideaflow-backend.container ideaflow-frontend.container; do
    install -o ideaflow -g ideaflow -m 600 "$stage/$name" "/home/ideaflow/.config/containers/systemd/$name"
done
for name in app-ideaflow.target ideaflow-backup.service ideaflow-backup.timer; do
    install -o ideaflow -g ideaflow -m 600 "$stage/$name" "/home/ideaflow/.config/systemd/user/$name"
done
as_app podman unshare chown 10001:10001 /home/ideaflow/handover
as_app systemctl --user daemon-reload
as_app systemctl --user enable app-ideaflow.target ideaflow-backup.timer
echo 'Release installed; database restore must precede target startup.'
