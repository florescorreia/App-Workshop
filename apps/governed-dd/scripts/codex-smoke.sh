#!/bin/sh
set -eu
mkdir -p /tmp/dd-codex
export CODEX_HOME=/tmp/dd-codex
cat > "$CODEX_HOME/config.toml" <<'EOF'
model = "gpt-6.1-sol"
model_provider = "litellm"
model_reasoning_effort = "medium"
[model_providers.litellm]
name = "Governed DD LiteLLM"
base_url = "https://litellm-app.ambitiousground-51296563.westeurope.azurecontainerapps.io/v1"
env_key = "LITELLM_API_KEY"
wire_api = "responses"
EOF
codex --version
codex exec --skip-git-repo-check --json --sandbox read-only 'Return only hello. Do not run commands or access files.'
