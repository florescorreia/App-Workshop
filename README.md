# App Workshop

Build apps locally, then deploy them independently to the secured VPS. Open `App Workshop.code-workspace` in this **App-Workshop** directory.

- `apps/ideaflow/`: faithful IdeaFlow application/deployment source, docs, tests and private local configuration/backups. Production remains **https://vps-8104e6c8.vps.ovh.us:8443**; existing accounts work.
- `apps/<new-app>/`: each future app's product contract, source, Compose stack and deployment assets.
- `docs/`: shared VPS foundation, security, Cockpit and [workspace guide](docs/APP_WORKSHOP.md).
- `scripts/`, `templates/`, `tests/workshop/`, `infra/`: reusable app tooling, three-service starter, infrastructure tests and host Cockpit/SSH-tool assets.

The root `.git` preserves the original history and remote **https://github.com/florescorreia/MINDcan-inspired-architecture.git**. Do not initialize Git inside an app. Source pushes do not deploy or migrate production.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 list
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 new -App your-app-name
```

IdeaFlow runs on the VPS. Local containers are stopped outside testing; their database volume is retained. To test it deliberately, use `scripts/workshop.ps1 up -App ideaflow` and stop afterward with `down -App ideaflow`. See [IdeaFlow](apps/ideaflow/README.md), [deployment/recovery](apps/ideaflow/docs/VPS_IDEAFLOW.md) and [relocation evidence](docs/RELOCATION.md). All Python/Node builds/tests run in containers.
