#!/bin/sh
# Recover only IdeaFlow's transient rootless DNS namespace after interrupted
# user-manager shutdown. No volumes, images or persistent config are removed.
set -eu
cd /home/ideaflow
test "$(id -u ideaflow)" -eq 1001
as_app() { runuser -u ideaflow -- env XDG_RUNTIME_DIR=/run/user/1001 "$@"; }
as_app systemctl --user stop app-ideaflow.target ideaflow-frontend.service ideaflow-backend.service ideaflow-postgres.service
test "$(as_app podman ps -q | wc -l)" -eq 0
for pid in $(pgrep -u ideaflow -f /usr/lib/podman/aardvark-dns || true); do kill -TERM "$pid"; done
# The runtime-reported recovery path belongs only to this dedicated account.
runtime=/run/user/1001/containers/networks/aardvark-dns
test "$runtime" = /run/user/1001/containers/networks/aardvark-dns
test ! -L "$runtime"
if [ -d "$runtime" ]; then rm -r -- "$runtime"; fi
as_app systemctl --user reset-failed
as_app systemctl --user start app-ideaflow.target
as_app podman ps
