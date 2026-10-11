#!/bin/sh
set -eu
mkdir -p /agent-home/ssh /home/node/.ssh /run/sshd
mkdir -p /run-gate
chown node:node /run-gate
if [ ! -f /agent-home/ssh/host_ed25519 ]; then ssh-keygen -q -t ed25519 -N '' -f /agent-home/ssh/host_ed25519; fi
cp /run/secrets/runtime-public /home/node/.ssh/authorized_keys
chmod 700 /home/node/.ssh
chmod 600 /home/node/.ssh/authorized_keys
chown -R node:node /home/node/.ssh /engagement
cat > /etc/ssh/sshd_config <<'EOF'
Port 2222
HostKey /agent-home/ssh/host_ed25519
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
AllowUsers node
AuthorizedKeysFile /home/node/.ssh/authorized_keys
AllowTcpForwarding no
X11Forwarding no
PermitTunnel no
PermitUserEnvironment no
UsePAM yes
PidFile /run/sshd.pid
Subsystem sftp internal-sftp
EOF
exec /usr/sbin/sshd -D -e
