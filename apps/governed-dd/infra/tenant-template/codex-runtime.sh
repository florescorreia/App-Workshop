#!/bin/sh
set -eu
# Runtime holds only model and tenant-agent credentials. Server/DB/human keys are never injected.
export LITELLM_API_KEY="$(cat /run/secrets/model-key)"
export DD_AGENT_TOKEN="$(cat /run/secrets/agent)"
export HTTPS_PROXY=http://egress-runtime:8888 HTTP_PROXY=http://egress-runtime:8888
export NO_PROXY=governance,paperclip,localhost,127.0.0.1
# One active analytical/reviewer process per tenant, including native UI starts.
exec python3 /usr/local/bin/run-supervisor.py "$@"
