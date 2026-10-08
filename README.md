# IdeaFlow

IdeaFlow turns improvement proposals into assigned work, approved monthly plans and Finance-verified outcomes. React/TypeScript and bundled Plotly/React Flow run behind nginx; FastAPI and PostgreSQL are the other two long-running services. Version 1.0.0. The runtime has no external API dependency.

The local application starts **empty**, with sites/categories and one bootstrap Admin. This workspace subsequently received the explicitly authorized HarborWorks batch on 2026-10-07; see [live import evidence](docs/SHOWCASE_IMPORT.md) and the updated [showcase guide](docs/DEMO_GUIDE.md). A separate 12-record v2 batch was subsequently added; see [its actual references and walkthrough](docs/DEMO_V2_GUIDE.md). Demo loading is a separate explicit action. Durable records, sessions, approved snapshots, results and append-only events live in the named `ideaflow_pgdata` volume. No business state depends on browser storage.

## Windows first run

Start Rancher Desktop with **dockerd (Moby)**. Scripts discover and verify its actual context; they never switch engines or change Kubernetes settings. This installation was verified using context `default` (Rancher Desktop WSL Distribution).

Run from this project directory; paths with spaces are supported. Host Python, Node, PostgreSQL, Make and curl are unnecessary.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 doctor
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 init-env
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 up
```

`init-env` creates missing `.env` secrets and a gitignored `local/first-login.txt`; it preserves existing secrets. Open that file privately for the generated Admin password. Email defaults to `admin@ideaflow.local`. The verified URL is **http://localhost:8080**. Login is a 12-hour server-issued HttpOnly/SameSite session. The Admin can create local accounts in Settings; use 12+ character passwords. Sign out with the arrow beside your profile.

The process-only execution-policy argument handles machines that block local unsigned scripts. It does not change the machine execution policy.

## Everyday operations

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 status
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 logs
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 down
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 up
```

`down` preserves the volume. `up` rebuilds images and waits for database/backend/frontend health before reporting readiness. Do not delete the named volume or run `down -v`. Other Compose projects are untouched. Edit `APP_PORT` in `.env` for a port conflict; `init-env -Port 8082` can choose a different initial port. Scripts use `DOCKER_CONTEXT` from `.env` only after verifying it belongs to Rancher Desktop. If that context changes, run doctor and update the setting. A containerd engine needs Rancher Desktop Preferences → Container Engine → General → dockerd (Moby); scripts do not make that change automatically.

Dependency/image download failures need access to Docker Hub, the npm registry and PyPI; browser tests additionally need Microsoft's container registry. Check your enterprise proxy/registry policy. After a successful build, normal application use works offline.

## Explicit fictional demo loading

Validate before committing:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 seed-demo -DryRun -BatchKey harborworks-demo-v1 -Seed 42
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 seed-demo -BatchKey harborworks-demo-v1 -Seed 42
```

Anchor defaults to today's date in `APP_TIMEZONE`; optionally supply `-AnchorDate 2026-10-07`. Same batch key is a no-op even if the anchor changes. A new batch requires a distinct key and unique external keys. This creates 60 fictional HarborWorks ideas, all seven stages, holds/rework, approved schedules, tasks and deliberately incomplete reporting. Generated fictional account passwords are saved only in `local/<batch-key>-credentials.json`, never in API responses or committed docs. The report is `local/last-import-report.json`; use its actual references in your presentation. See [demo import contract](docs/DEMO_IMPORT.md) and [eight-minute guide](docs/DEMO_GUIDE.md).

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 seed-demo -File demo/example.json -DryRun
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 seed-demo -File demo/example.json
```

Admins may also paste a JSON dataset into Settings, validate a preview and explicitly confirm. The importer never replaces existing business records. Dry runs roll back business changes; PostgreSQL readable-reference sequences can advance, so gaps are normal.

## Permissions

| Operation | Contributor | Manager | Finance | Admin |
| --- | --- | --- | --- | --- |
| Read portfolio, create ideas, comment | Yes | Yes | Yes | Yes |
| Edit business case/draft | Own New or assigned idea | Yes | No | Yes |
| Assign owner | No | Yes | No | Yes |
| Manage tasks | Assigned idea; status of own assigned tasks | Yes | No | Yes |
| New → Screening; Screening → Analysis; Implementation → Validation | Assigned owner | Yes | No | Yes |
| Analysis → Approved; Approved → Implementation; Analysis → Screening; Approved → Analysis | No | Yes | No | Yes |
| Validation → Implementation | No | Yes | Yes | Yes |
| Validation → Realized; Realized → Validation | No | No | Yes | Yes |
| Hold/resume (before Realized) | Assigned owner | Yes | No | Yes |
| Reject/cancel | No | Yes | No | Yes |
| Record actual outcomes | Assigned idea | Yes | Yes | Yes |
| Verify/revoke monthly results | No | No | Yes | Yes |
| Manage local users/references; import demo | No | No | No | Yes |

Transitions also enforce the PRD prerequisites. Reasons are required. Contributors cannot bypass approval or verification through API requests. Generic edits cannot change stage, disposition, approved status or verification. All idea-related mutations take the idea record version; period edits additionally take a period version. Stale requests return 409 and retain the user's unsaved form input.

## Backup and isolated restore verification

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 backup
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 restore-test -File backups/ideaflow-YYYYMMDD-HHMMSS.dump
```

The custom-format dump is created in the database container and copied as a binary file into `backups/`; PowerShell never text-redirects dump bytes. Restore verification creates a unique `ideaflow_restore_*` database in the same PostgreSQL service, restores there, compares counts and SHA-256 fingerprints of all business tables, then removes only that temporary database. Avoid edits during the comparison. Live restore is an explicit operator action, outside the routine restore-test command; keep the original dump and restore into a separate database first. Backups contain sensitive account/session data and must be stored privately. `.env` and credentials are also sensitive local files.

## Tests and development

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 test
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-test.ps1
```

Backend tests create and drop only a unique isolated test database. The browser empty check makes no business writes to an empty deployed workspace. For this imported live showcase, use `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-showcase.ps1`; it reviews the populated app without saving business changes and requires the private import reports/credentials. Populated browser checks use the isolated `compose.verify.yaml` project. See [actual evidence](docs/VERIFICATION.md) for the commands run and scope. All frontend build tools run in its multi-stage container; backend tests run through Compose. For frontend interactive development, run a transient Node container with a source bind mount and `npm ci && npm run dev`; this alternative has not been exercised as a development server. No extra permanent service is needed.

Bash equivalents are `bash scripts/ideaflow.sh doctor|init-env|up|status|logs|down|test|backup`, `bash scripts/ideaflow.sh seed-demo --dry-run`, and `bash scripts/ideaflow.sh restore-test backups/file.dump`. Windows PowerShell commands are the tested operating path; bash syntax/behavior validation is documented separately.

Architecture, definitions and schema: [architecture](docs/ARCHITECTURE.md), [data dictionary](docs/DATA_DICTIONARY.md), [licenses](docs/DEPENDENCIES.md). OpenAPI is available through nginx at `/api/docs` with bundled offline assets; the backend OpenAPI JSON is `/api/openapi.json`. This is local authentication and an application audit trail; it does not claim enterprise identity or cryptographic tamper resistance.
