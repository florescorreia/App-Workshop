# IdeaFlow

Version **1.2.0 / schema 0006** is deployed and publicly verified. VAVE is the landing page, with program access, M0–M6 evidence gates, independent financial decisions, benefit applications, attachments, rollout, personal work, notifications and scoped reconciliation. Open [VAVE programs](https://vps-8104e6c8.vps.ovh.us:8443/vave). Read the [differential audit](docs/VAVE_REQUIREMENT_AUDIT.md), [accepted decisions](docs/VAVE_DELTA.md) and [user guide](docs/USER_GUIDE.md).

The two user-authorized test records are now **IF-00205 — Simplify the actuator mounting bracket** (M2) and **IF-00206 — Introduce returnable packaging for actuator deliveries** (Draft/M0). Original IDs, account/password hashes, financial rows and history are preserved; prior evidence is readable under History. Illustrative opportunity/targets do not constitute approved or verified savings. Their explicit adaptation is separate from startup/code deployment, which creates no business data.

The interface follows the public [Roland Berger Germany design reference](docs/DESIGN_REFERENCE.md), with bundled Inter. Earlier IdeaFlow screens remain in a navigation disclosure. The instructions below describe the original shared workspace; VAVE membership rights and independent review supersede its general business permissions and USD-only reporting within programs.

This application now lives in `apps/ideaflow/`. Run the following app-specific commands from that directory, or use the shared root wrapper with `-App ideaflow`. The VPS is authoritative for current live data; local data is an independent historical copy. Local containers are stopped outside tests.

VPS deployment: **https://vps-8104e6c8.vps.ovh.us:8443**. Your current local accounts and business history were copied on 2026-10-09; existing passwords work. Access credentials are persisted in Windows **User** environment variables. See [VPS operation and credentials](docs/VPS_IDEAFLOW.md) and [verification evidence](docs/VERIFICATION.md). Local and VPS databases are independent after that snapshot; no demo was loaded during deployment.

IdeaFlow turns improvement proposals into assigned work, approved monthly plans and reviewed outcomes. React/TypeScript and bundled Plotly/React Flow run behind nginx; FastAPI and PostgreSQL are the other two long-running services. Version 1.2.0. The runtime has no external API dependency.

A fresh installation starts **empty**, with only the bootstrap Admin. Existing volumes preserve their records; local containers are currently stopped outside tests. Locations, categories and business units are defined by users as work develops; no prior Admin setup is needed. The local workspace was explicitly cleared on 2026-10-09 after a verified backup, retaining the Admin login and all configuration/volumes. Old HarborWorks showcase guides are historical evidence; their records are no longer loaded. Start with the [manual UX walkthrough](docs/UX_WALKTHROUGH.md), written for an existing User account, with optional Admin exercises at the end. The retained local snapshot later contains user-created ideas; it is independent of production. Durable records, sessions, approved snapshots, results and append-only events live in `ideaflow_pgdata`.

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

Use [the documentation index](docs/README.md) to distinguish current guides from dated showcase evidence. The detailed manual is available inside the app under **Walkthrough**, or directly at **http://localhost:8080/guide** after sign-in. It helps users choose and develop their own idea from a first observation through reviewed outcomes, with topic search, a contents list, printable instructions, financial definitions, rework guidance and troubleshooting. Overview and Settings link to it; help on the create form and idea workspace opens the relevant section in a separate tab to keep the current form available. Reading it creates no records. Use **Create your own idea** when ready to begin.

All ideas use the same capture, workflow and reporting. Admin can open **Admin actions → Remove idea**, review the full impact, enter a reason and confirm. This archives the complete record and removes it from everyday views and totals while retaining tasks, plans, actuals, comments and history. **Settings → Removed ideas** provides read-only review and restoration with a reason. Inactive owners/open task assignees require explicit reassignment on restoration. No existing ideas are removed automatically. The User walkthrough uses ordinary ideas; hypothetical exercise amounts contribute to shared totals until Admin removes those exact records.

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

| Operation | User | Admin |
| --- | --- | --- |
| Create/read/edit/assign ideas; manage tasks/comments | Yes | Yes |
| Create locations/categories; rename/merge shared reporting groups | Yes | Yes |
| Advance/rework/hold/reject/cancel under workflow prerequisites | Yes | Yes |
| Approve plans; record, verify or revoke elapsed results | Yes | Yes |
| Create/deactivate/delete accounts, set/regenerate passwords, import demo batches | No | Yes |
| Remove ideas; inspect or restore removed ideas | No | Yes |

Approval and result review are explicit decisions with reasons and history. Any User can perform them; independent review is recommended but not enforced, so "verified" means reviewed within this workspace rather than finance certification. Generic edits cannot change stage, disposition, approval or verification. Idea edits and classification edits use record versions; stale requests return 409 and preserve form input.

Admin account controls are in **Settings → Local user management**. **Delete account** first shows a usage preview and requires a reason. Unused accounts are removed; historical accounts are retired from access and the account list while names/history stay intact. Reassign open ideas/tasks first. The bootstrap Admin and your own signed-in account are protected.

**Regenerate password** creates a random replacement for another account, shows it once, and revokes all of that user's sessions. Share it privately, then close the dialog. It does not reactivate an inactive account. **Set password** also revokes sessions; setting your own password signs you out. **View account history** shows the latest 100 Admin actions, without credentials. No account or password is changed during deployment.

In **New idea**, location/category are optional: type a new name or open the dropdown. Saving reuses existing names regardless of case/spacing. **Settings → Locations and categories** renames values or merges them with an existing target. This updates all affected ideas and current dashboard aggregations, retaining their earlier history. Edit an individual idea's Overview to change only that idea. Business unit is an optional grouping of a location, set in shared Settings. A merge retires its source choice; a later rename does not preserve every older spelling as an alias.

## Backup and isolated restore verification

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 backup
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 restore-test -File backups/ideaflow-YYYYMMDD-HHMMSS.dump
```

The custom-format dump is created in the database container and copied as a binary file into `backups/`; PowerShell never text-redirects dump bytes. Restore verification creates a unique `ideaflow_restore_*` database in the same PostgreSQL service, restores there, compares counts and SHA-256 fingerprints of all business tables, then removes only that temporary database. Avoid edits during the comparison. Live restore is an explicit operator action, outside the routine restore-test command; keep the original dump and restore into a separate database first. Backups contain sensitive account/session data and must be stored privately. `.env` and credentials are also sensitive local files.

## Tests and development

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 test
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-shared.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-idea-removal.ps1
```

Backend tests create and drop only a unique isolated test database. `browser-shared.ps1` reviews the empty live workspace without business writes; `browser-shared.ps1 -Verification` runs the complete regular-User flow in the isolated `compose.verify.yaml` workspace. That project preserves its own old/test records and should be stopped after verification. Old showcase/browser scripts are compatibility checks for imported data, not the default empty-workspace verification. See [actual evidence](docs/VERIFICATION.md). All build and test tooling runs in containers.

`browser-financials.ps1` checks the current live idea timeline, range controls and form preservation without business writes; `-Verification` creates an isolated monthly plan/result/review fixture and checks amounts, unknowns, the graph axis and desktop/mobile layouts.

`browser-idea-removal.ps1` checks the live shared screens/removal controls/guide without business writes; `-Verification` exercises creation, workflow, stale previews, Admin removal, retained financial evidence and restoration only in the isolated workspace.

Run these app-relative commands from `apps/ideaflow/`. Bash equivalents are `bash scripts/ideaflow.sh doctor|init-env|up|status|logs|down|test|backup`, `bash scripts/ideaflow.sh seed-demo --dry-run`, and `bash scripts/ideaflow.sh restore-test backups/file.dump`. Windows PowerShell commands are the tested operating path; bash syntax/behavior validation is documented separately.

Architecture, definitions and schema: [architecture](docs/ARCHITECTURE.md), [data dictionary](docs/DATA_DICTIONARY.md), [licenses](docs/DEPENDENCIES.md). OpenAPI is available through nginx at `/api/docs` with bundled offline assets; the backend OpenAPI JSON is `/api/openapi.json`. This is local authentication and an application audit trail; it does not claim enterprise identity or cryptographic tamper resistance.
