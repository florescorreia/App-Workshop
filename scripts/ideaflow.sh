#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
action="${1:-status}"; shift || true
if [[ -f .env ]]; then set -a; source .env; set +a; fi
detect_context() {
  if ! rdctl list-settings | grep -q '"name": "moby"'; then
    echo 'Select Rancher Desktop > Preferences > Container Engine > General > dockerd (Moby). No configuration was changed.' >&2; exit 1
  fi
  if [[ -n "${DOCKER_CONTEXT:-}" ]]; then
    docker --context "$DOCKER_CONTEXT" info --format '{{.OperatingSystem}}' | grep -q 'Rancher Desktop' || exit 1
  else
    while IFS= read -r candidate; do
      if docker --context "$candidate" info --format '{{.OperatingSystem}}' 2>/dev/null | grep -q 'Rancher Desktop'; then DOCKER_CONTEXT="$candidate"; break; fi
    done < <(docker context ls --format '{{.Name}}')
    [[ -n "${DOCKER_CONTEXT:-}" ]] || { echo 'No reachable Rancher Desktop context' >&2; exit 1; }
  fi
}
detect_context
compose() { docker --context "$DOCKER_CONTEXT" compose "$@"; }
case "$action" in
 doctor) docker version; docker compose version; docker context ls; echo "Verified Moby context: $DOCKER_CONTEXT";;
 init-env)
  [[ ! -f .env ]] || { echo 'Existing .env preserved'; exit; }
  mkdir -p local
  docker --context "$DOCKER_CONTEXT" run --rm -i --mount "type=bind,source=$PWD,target=/workspace" -w /workspace -e "DETECTED_CONTEXT=$DOCKER_CONTEXT" python:3.13.7-slim-bookworm python - <<'PY'
import os,secrets,pathlib,socket
port=8080
while True:
    with socket.socket() as s:
        # Container cannot reliably inspect host listeners; up reports any bind conflict.
        break
text=pathlib.Path('.env.example').read_text().replace('DOCKER_CONTEXT=default','DOCKER_CONTEXT='+os.environ['DETECTED_CONTEXT'])
password=secrets.token_urlsafe(24)
for key in ['POSTGRES_PASSWORD','APP_DB_PASSWORD','ADMIN_PASSWORD']:
    text=text.replace(key+'=GENERATE_LOCALLY',key+'='+(password if key=='ADMIN_PASSWORD' else secrets.token_urlsafe(24)))
pathlib.Path('.env').write_text(text)
pathlib.Path('local/first-login.txt').write_text('URL: http://localhost:8080\nEmail: admin@ideaflow.local\nPassword: '+password+'\n')
PY
  chmod 600 .env local/first-login.txt
  echo 'Secrets generated; open local/first-login.txt privately. Set APP_PORT in .env if port 8080 is occupied.';;
 up) compose up --build -d --wait --wait-timeout 180; echo "IdeaFlow: http://localhost:${APP_PORT:-8080}";;
 status) compose ps;;
 logs) compose logs --tail 100;;
 down) compose down; echo 'Named volume preserved';;
 seed-demo) compose exec -T backend python -m app.demo "$@";;
 test) compose exec -T backend pytest -q;;
 backup)
  mkdir -p backups; stamp="$(date +%Y%m%d-%H%M%S)"; dump="ideaflow-$stamp.dump"
  compose exec -T postgres pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc -f "/tmp/$dump"
  compose cp "postgres:/tmp/$dump" "backups/$dump"; compose exec -T postgres rm "/tmp/$dump"; echo "backups/$dump";;
 restore-test)
  file="${1:?Specify backups/file.dump}"; temp="ideaflow_restore_$(docker --context "$DOCKER_CONTEXT" compose exec -T backend python -c 'import uuid;print(uuid.uuid4().hex)')"
  [[ "$temp" =~ ^ideaflow_restore_[a-f0-9]{32}$ ]] || exit 1
  cleanup() { compose exec -T postgres dropdb -U "$POSTGRES_USER" --if-exists "$temp"; compose exec -T postgres rm "/tmp/$temp.dump"; }
  trap cleanup EXIT
  compose cp "$file" "postgres:/tmp/$temp.dump"; compose exec -T postgres createdb -U "$POSTGRES_USER" "$temp"
  compose exec -T postgres pg_restore -U "$POSTGRES_USER" --exit-on-error --no-owner -d "$temp" "/tmp/$temp.dump"
  compose exec -T backend python -m app.restore_check --database "$temp";;
 *) echo 'Actions: doctor init-env up status logs down seed-demo backup restore-test test' >&2; exit 1;;
esac
