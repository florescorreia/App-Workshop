# App Workshop

Build independent applications in one Git repository and run them on the existing VPS. IdeaFlow is preserved at `apps/ideaflow/`. New apps live in `apps/<slug>/`; each has its own product contract, source, Compose project, database volume, credentials and deployment account. Shared tools and templates live at the root. The workspace directory is now `App-Workshop`; the original Git history and GitHub remote are preserved. 

Open `App Workshop.code-workspace` in VS Code, or continue opening this directory normally. Use this new side-by-side workspace going forward. There is one root Git repository and no nested repositories.

## Create your next app locally

Run these commands from the repository root in PowerShell. Choose a permanent lowercase name, for example `supplier-portal`:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 doctor
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 new -App supplier-portal
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 init-env -App supplier-portal
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 up -App supplier-portal
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 list
```

The catalog reserves available application ports, starting with local 8081, VPS HTTPS 8444 and VPS loopback 18082. Existing IdeaFlow retains local 8080, HTTPS 8443, loopback 18081, its account, storage and commands. The catalog checks identity and port collisions; real listener checks may still identify conflicts with software outside the catalog. Resolve such conflicts by changing both `workshop.json` and the app's `app.json` before first launch, and the app's private `.env` origin/port where applicable. Do not change an established app identity or volume name to reorganize folders.

The starter has three services: React/TypeScript behind nginx, FastAPI and PostgreSQL. It opens with login and an empty notes workspace. Notes provide a small working persistence example; no IdeaFlow source, accounts, ideas or data are copied. Open `apps/supplier-portal/.env` privately for the generated Admin email/password. Local frontend binds to loopback; PostgreSQL and backend have no host ports.

Write the actual product requirements in `apps/supplier-portal/docs/PRD.md`, then implement inside that app. Ask your coding assistant: “Read the root AGENTS.md, apps/supplier-portal/AGENTS.md and its PRD. Implement this app without changing IdeaFlow or other apps.” Keep domain code inside the app; use the shared tools for infrastructure.

All Python/Node builds and tests run in transient containers using the discovered Rancher Desktop Moby context explicitly. The workspace tools image is built automatically when needed. No host Python or Node installation is required.

The frontend starter uses IdeaFlow's tested Vite settings (minification/tree shaking disabled), plus a temporary in-memory build directory. This avoids the native executable locking and build stalls observed on this workstation's Rancher Desktop engine. Static output is bundled into nginx. Registry connection resets are environmental download failures; rerun a failed build once network access is restored.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 test -App supplier-portal
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 backup -App supplier-portal
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 restore-test -App supplier-portal
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 status -App supplier-portal
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 down -App supplier-portal
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 up -App supplier-portal
```

`down` preserves the app volume. `restore-test` compares every public table with a restored copy in a uniquely named temporary database, removing only that verification database afterward. Avoid concurrent writes during the comparison. Backups and private deployment archives are gitignored. The starter test similarly uses a unique test database rather than altering live notes. Never use `down -v`, prune, database resets or shared volume names.

Existing IdeaFlow operations continue using `apps/ideaflow/scripts/ideaflow.ps1` and `apps/ideaflow/scripts/vps.ps1`. The workspace wrapper delegates supported local IdeaFlow commands to the existing tool.

## Deploy a completed app to the VPS

Finish the app's own business tests, security review, account management, least-privilege database roles, schema migration strategy, browser/layout checks and backup/restore verification first. The generated notes starter uses an owner database role and has no failed-login throttling or user administration UI; it is a development starting point. Do not mistake its infrastructure readiness for completed product/security acceptance.

The existing host uses rootless Podman/Quadlet and host Caddy. Local development continues using Docker Compose; do not replace the VPS runtime or move IdeaFlow to Docker. See [foundation](VPS_FOUNDATION.md), [security](VPS_SECURITY.md), [Cockpit](VPS_COCKPIT.md) and [IdeaFlow operation](../apps/ideaflow/docs/VPS_IDEAFLOW.md).

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 prepare-vps -App supplier-portal
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop-vps.ps1 init-secrets -App supplier-portal
```

`prepare-vps` exports the three locally built images and creates an immutable reviewable release under `apps/supplier-portal/local/releases/<release-id>/`. Review its Quadlets, health commands, resource budgets and Caddy route. It performs no VPS mutation. Images are pinned by their configuration content hashes extracted from the exported archive, suitable for Podman image identity checks. For a later rebuild, preserve/rename `local/release-images.tar` privately before preparing another export; the tool refuses to overwrite it. Keep app image version tags and Compose/app.json definitions aligned when updating versions.

Secrets are stored in persistent Windows **User** environment variables under `APPWORKSHOP-SUPPLIER-PORTAL-VPS`: `DB-PASSWORD`, `ADMIN-EMAIL`, `ADMIN-PASSWORD`, `COCKPIT-PASSWORD`, `URL`. Existing variables are preserved. Retrieve privately with `[Environment]::GetEnvironmentVariable('APPWORKSHOP-SUPPLIER-PORTAL-VPS-ADMIN-PASSWORD','User')`. Never put values in committed docs. SSH/sudo reuse the existing pinned host key, encrypted key and host credential variables. Protect the workstation and keep a recovery copy in a password manager.

After your explicit deployment instruction, run with the actual release ID printed during preparation:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop-vps.ps1 deploy -App supplier-portal -Release <release-id>
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop-vps.ps1 status -App supplier-portal
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop-vps.ps1 backup -App supplier-portal
```

Deployment transfers and verifies SHA-256 checksums, creates a dedicated account with unique subordinate IDs and lingering, installs only its units and protected env files, loads/pins images, starts its three healthy services, installs its daily backup timer, validates/reloads the shared Caddy configuration and opens only its HTTPS port. The frontend stays loopback-only. A scoped user-manager shutdown drop-in follows IdeaFlow's verified reboot solution. An existing Linux account without the workshop ownership marker is rejected. Updates preserve server credentials and volume and take a pre-update dump when the database is running. Updates interrupt only that app. There is no automated migration or rollback of an arbitrary future product; keep release copies and app-specific recovery instructions.

Fresh deployment starts with an empty database plus bootstrap Admin. Local notes/data are **not copied**. If you want to migrate the local workspace, request a separate current-data handover: coherent snapshot, isolated restore test, schema compatibility, server-side verification and credential/session handling before publication. Never restore onto an existing live workspace as part of an update.

The route uses the app's own HTTPS port; it does not claim standard 80/443 or replace IdeaFlow's shared redirect. Secure, unique `__Host-<slug>_session` cookies distinguish apps. Cookies are not port-isolated; mutually untrusted apps should use different hostnames and a separate security review. Adapt route headers/CSP to the completed product, following [web hardening](../apps/ideaflow/docs/VPS_WEB_HARDENING.md).

Daily backups remain on VPS storage; `backup` also downloads a checksum-verified copy privately to this workstation. Backups are retained without automatic deletion, so monitor disk space and arrange another off-host destination. Provider disk loss is different from a restart. Check summed app budgets against host headroom before adding apps; there is no automatic capacity admission controller.

Cockpit remains available through the existing SSH tunnel. Sign in as the new app's Linux account (`supplier-portal`) with its separate `COCKPIT-PASSWORD` variable to see its Podman containers and `app-supplier-portal.target` in Application stacks. An `ubuntu` or `ideaflow` session does not list another account's rootless containers. `start`, `stop`, `status` and `backup` accept the same `-App` option; stopping retains storage.

## Git and GitHub

One `.git` directory at the root tracks IdeaFlow, shared tools and every new app. GitHub stays `https://github.com/florescorreia/MINDcan-inspired-architecture.git`; the new directory name does not rename the GitHub repository or alter remote configuration. A single root commit/push includes selected apps:

```powershell
git status
git add apps/supplier-portal workshop.json
git diff --cached --stat
git commit -m "Add supplier portal"
git push origin main
```

Review staged files before committing. `.env`, nested private env variants, `local/`, `backups/`, `artifacts/`, dependency folders, generated builds and key files are ignored at every app depth; `.env.example` remains tracked. Do not initialize Git inside an app. A Git push publishes source only; it does not deploy, migrate databases or transfer credentials.
