#!/bin/sh
set -eu
route=/etc/caddy/apps.d/ideaflow.caddy
test ! -e "$route"
install -o root -g root -m 644 /home/ubuntu/ideaflow-deploy-20261009/ideaflow.caddy "$route"
if ! runuser -u caddy -- caddy validate --config /etc/caddy/Caddyfile; then
    # Only this newly added route is withdrawn; existing gateway stays active.
    mv "$route" /home/ubuntu/ideaflow-deploy-20261009/ideaflow.caddy.rejected
    exit 1
fi
systemctl reload caddy
ufw allow 8443/tcp comment 'IdeaFlow HTTPS via Caddy'
curl --fail --silent --show-error https://vps-8104e6c8.vps.ovh.us:8443/api/health/ready
