FROM ghcr.io/paperclipai/paperclip:2026.1005.0@sha256:de762433b50d56ed9180fef96a13fa236b37856c5c7a7718e8f19afe3d1e8670
USER root
RUN apt-get update && apt-get install -y --no-install-recommends openssh-server python3 git curl util-linux && rm -rf /var/lib/apt/lists/* /etc/ssh/ssh_host_* && mkdir -p /run/sshd /engagement /agent-home && chown node:node /engagement /agent-home
COPY infra/tenant-template/runtime-start.sh /usr/local/bin/runtime-start
COPY infra/tenant-template/codex-runtime.sh /usr/local/bin/dd-codex
COPY infra/tenant-template/run-supervisor.py /usr/local/bin/run-supervisor.py
RUN chmod 755 /usr/local/bin/runtime-start /usr/local/bin/dd-codex
ENTRYPOINT ["/usr/local/bin/runtime-start"]
