FROM ghcr.io/paperclipai/paperclip:2026.1005.0@sha256:de762433b50d56ed9180fef96a13fa236b37856c5c7a7718e8f19afe3d1e8670
USER root
RUN apt-get update && apt-get install -y --no-install-recommends python3 openssh-client && rm -rf /var/lib/apt/lists/*
COPY infra/tenant-template/patch-paperclip.py /tmp/patch-paperclip.py
RUN python3 /tmp/patch-paperclip.py && rm /tmp/patch-paperclip.py
USER node
