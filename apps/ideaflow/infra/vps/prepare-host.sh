#!/bin/sh
# Run as root via the authenticated SSH wrapper. No existing app is replaced.
set -eu
cd /
if getent passwd ideaflow >/dev/null; then
    echo 'ideaflow account already exists; refusing fresh installation.' >&2
    exit 1
fi
if [ -e /etc/caddy/apps.d/ideaflow.caddy ]; then exit 1; fi
useradd --create-home --shell /bin/bash ideaflow
test "$(getent passwd ideaflow | cut -d: -f6)" = /home/ideaflow
grep '^ideaflow:' /etc/subuid
grep '^ideaflow:' /etc/subgid
loginctl enable-linger ideaflow
uid=$(id -u ideaflow)
systemctl start "user@$uid.service"
install -d -o ideaflow -g ideaflow -m 700 /home/ideaflow/.config /home/ideaflow/.config/containers /home/ideaflow/.config/systemd
install -d -o ideaflow -g ideaflow -m 700 /home/ideaflow/.config/ideaflow /home/ideaflow/.config/containers/systemd /home/ideaflow/.config/systemd/user /home/ideaflow/backups /home/ideaflow/handover
install -d -o ideaflow -g ideaflow /home/ideaflow/bin /home/ideaflow/demo /home/ideaflow/releases
runuser -u ideaflow -- env XDG_RUNTIME_DIR="/run/user/$uid" systemctl --user enable --now podman.socket
echo 'Dedicated rootless account prepared.'
