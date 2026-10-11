#!/bin/sh
set -eu
task_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
task_context=${DD_DOCKER_CONTEXT:-default}
task_os=$(docker --context "$task_context" info --format '{{.OperatingSystem}}')
case "$task_os" in *'Rancher Desktop'*) ;; *) echo 'Explicit Rancher Moby context required' >&2;exit 1;;esac
task_engine=$(docker --context "$task_context" info --format '{{.ID}}')
cd "$task_root"
if [ "${1:-doctor}" = build ];then
 docker --context "$task_context" build -f services/governance/Dockerfile -t governed-dd-governance:0.1.0 .
 docker --context "$task_context" build -f frontend/Dockerfile -t governed-dd-explorer:0.1.0 .
 docker --context "$task_context" build -f infra/tenant-template/Paperclip.Dockerfile -t governed-dd-paperclip:2026.1005.0 .
 docker --context "$task_context" build -f infra/tenant-template/Runtime.Dockerfile -t governed-dd-runtime:2026.1005.0 .
fi
docker --context "$task_context" build -f scripts/Tooling.Dockerfile -t governed-dd-tools:0.1.0 .
if [ "${1:-doctor}" = build ];then exit 0;fi
exec docker --context "$task_context" run --rm --user root \
 --mount "type=bind,source=$task_root,target=/workspace" \
 --mount type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock \
 -e "HOST_APP_ROOT=$task_root" -e "DD_ENGINE_ID=$task_engine" \
 -e LITELLM_API_KEY -e DD_RUNTIME_SUBNET -e DD_PROVIDER_EDGE_SUBNET \
 -e DD_SEARCH_API_KEY -e DD_EMBEDDING_API_KEY governed-dd-tools:0.1.0 "$@"
