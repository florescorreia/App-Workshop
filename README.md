# App Workshop

Start your next app with **`apps/<app-name>/docs/PRD.md`**. Open this repository in VS Code using `App Workshop.code-workspace`. Develop each app locally, then deploy it to the VPS when you explicitly request publication.

## Start here

1. Choose a permanent lowercase name, such as `supplier-portal`.
2. Create `apps/supplier-portal/docs/PRD.md` and write or paste your product brief. Use [the PRD template](templates/three-service/docs/PRD.md) as a checklist; plain prose is also welcome.
3. Follow [Start a new app](docs/START_NEW_APP.md). The generator preserves your existing PRD and adds independent starter files. It creates no credentials/data and starts no containers.
4. Ask the coding assistant to implement that PRD, complete the local checks and document the actual results. [Copy-ready prompts](docs/START_NEW_APP.md#implementation-prompt) are provided.

You can also run the generator first and fill in its generated PRD:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 new -App supplier-portal
```

## Where things belong

| Folder/file | Purpose |
| --- | --- |
| `apps/<name>/docs/PRD.md` | The selected app's product and implementation contract |
| `apps/<name>/` | Its source, tests, docs, configuration and deployment assets |
| `docs/` | Shared creation, hosting, security, Cockpit and workspace evidence |
| `scripts/`, `templates/`, `tests/workshop/`, `infra/` | Reusable tooling, starter, infrastructure checks and shared host assets |
| `workshop.json` | Reserved app identities, ports and VPS host configuration |

Each app has exactly three long-running services: React/nginx, FastAPI and PostgreSQL. Build/test tools run in containers through the detected Rancher Desktop Moby context. No host Python or Node is required. Apps have separate ports, accounts, credentials and durable volumes. Startups are empty; showcase imports are explicit.

## Reference app and hosting

[IdeaFlow](apps/ideaflow/README.md) is preserved under `apps/ideaflow/` and runs at **https://vps-8104e6c8.vps.ovh.us:8443**. Its local containers are stopped outside deliberate testing; the database volume is retained. Its workflow, roles and financial calculations are app-specific examples, not requirements for your next app. See [workspace operations](docs/APP_WORKSHOP.md), [VPS foundation](docs/VPS_FOUNDATION.md), [security](docs/VPS_SECURITY.md) and [Cockpit](docs/VPS_COCKPIT.md).

## Git

Current source repository: **https://github.com/florescorreia/App-Workshop**. One root `.git` tracks all apps and shared tools; never initialize Git inside an app. Review changes, commit and push from the root. Private `.env`, `local/`, `backups/` and `artifacts/` are ignored. A source push does not deploy or transfer credentials/data. Run `git remote -v` if checking your configured destination.

See [documentation index](docs/README.md) and [verification evidence](docs/VERIFICATION.md) for scope, checks and limitations.
