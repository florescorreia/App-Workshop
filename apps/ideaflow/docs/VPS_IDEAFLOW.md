# IdeaFlow on the VPS — 2026-10-09

**Full VPS reboot verified on 2026-10-09:** host rebooted at approximately **18:03:52 America/New_York**, and IdeaFlow's three containers became healthy automatically by **18:04:34**. Every database table, including accounts/password hashes, stored sessions and the reference sequence, matched the fresh pre-reboot snapshot exactly. The current test snapshot contains five accounts, two ideas and 27 idea-history events. Existing Admin login and Cockpit authentication passed afterward. See the full-reboot evidence at the end of [VERIFICATION.md](VERIFICATION.md).

Open **https://vps-8104e6c8.vps.ovh.us:8443**. The VPS runs IdeaFlow 1.0.0 using the existing rootless Podman/Quadlet and Caddy foundation. Exactly three application containers run under the dedicated Linux account `ideaflow` (UID 1001): React/nginx, FastAPI and PostgreSQL. Local build/test tooling uses the detected Rancher Desktop Moby context `default`; no host Python or Node is required.

The user selected **copy current workspace**. A coherent PostgreSQL snapshot taken on October 9 at approximately **16:28 America/New_York / 20:28 UTC** was restored into a new, separate VPS volume before backend startup. Accounts, password hashes, idea references, history, classifications, plans, tasks and results are preserved. Existing browser sessions were excluded; sign in again. Later local edits are not synchronized to the VPS. No fictional dataset was loaded.

The snapshot contains **2 ideas, 27 idea events, 2 accounts, 6 financial plan versions, 24 monthly schedule rows, 1 result period, 1 task, 1 comment, 1 location, 1 category and 1 account event**. There are zero demo batches. Idea **IF-00205 — Reduce repeated dispatch checks** is in Validation; **IF-00206 — Agree a daily dispatch cutoff** is New. The readable-reference sequence remains at 206. All 12 business-table counts and SHA-256 fingerprints match the restored local snapshot, including account hashes and event rows.

## Sign in and Windows credentials

Use your existing IdeaFlow email and password. The normal User account is copied unchanged; its password is retained as a hash and is not recoverable by deployment tooling. The bootstrap Admin was authenticated locally before copying and again in the public browser check. Its access details, fresh VPS database credentials and the dedicated Cockpit account credentials are persisted in **Windows User environment variables**:

| Variable | Purpose |
| --- | --- |
| `IDEAFLOW-VPS-URL` | Public application URL |
| `IDEAFLOW-VPS-ADMIN-EMAIL` | Existing bootstrap Admin email |
| `IDEAFLOW-VPS-ADMIN-PASSWORD` | Existing bootstrap Admin password; unchanged |
| `IDEAFLOW-VPS-DB-PASSWORD` | Separate VPS migration/database owner password |
| `IDEAFLOW-VPS-APP-DB-PASSWORD` | Separate VPS application database role password |
| `IDEAFLOW-VPS-TIMEZONE` | Application timezone |
| `IDEAFLOW-VPS-COCKPIT-USERNAME` | `ideaflow`, for this application's stack |
| `IDEAFLOW-VPS-COCKPIT-PASSWORD` | Dedicated Linux account/Cockpit password |

Retrieve credentials privately in PowerShell; never share the output or commit it:

```powershell
[Environment]::GetEnvironmentVariable('IDEAFLOW-VPS-ADMIN-EMAIL','User')
[Environment]::GetEnvironmentVariable('IDEAFLOW-VPS-ADMIN-PASSWORD','User')
```

Query User scope because already-running programs can have stale process environments. `scripts/vps.ps1` imports persisted values temporarily and passes environment names to its transient SSH container; values do not appear in command arguments. Server environment files are mode 600 under `/home/ideaflow/.config/ideaflow/`. The existing encrypted SSH key, passphrase variables and pinned host fingerprint remain unchanged. Windows environment variables are not a dedicated secret vault; protect this workstation and retain a private recovery copy.

If you change the Admin password in Settings, update its Windows variable privately as well. Existing normal User passwords are managed through the app's Admin controls. Changing a Windows credential variable alone does not change a deployed account or database role. Deployment secrets must be updated deliberately together with their corresponding server credentials.

## Start, stop and inspect

Build the transient SSH tool image if needed:

```powershell
docker --context default build -t ideaflow-vps-tools:1.0.0 ../../infra/vps-tools
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/vps.ps1 stack -Command status
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/vps.ps1 stack -Command stop
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/vps.ps1 stack -Command start
```

Stop/start preserves the named volume. The Caddy route remains present while stopped, so a public request receives a gateway error until the stack becomes ready. Startup waits for database, backend and frontend health in that order. App target and daily backup timer are enabled; the dedicated account has lingering and a local Podman socket. A scoped `/etc/systemd/system/user@1001.service.d/zz-ideaflow.conf` stops the app before restarting its rootless user manager and overrides the host's five-second user-manager shutdown timeout with 180 seconds. No other account's manager configuration is changed.

For Cockpit, use the SSH tunnel in [VPS_COCKPIT.md](../../../docs/VPS_COCKPIT.md), open **http://127.0.0.1:9090**, and sign in as **ideaflow** using its Windows credential variable. **Application stacks → IdeaFlow application → Start/Stop** controls this stack. `ubuntu` remains the host administration account and does not list another account's application target. SSH still admits only the existing `ubuntu` key; the new account does not receive SSH access or sudo rights. Cockpit authentication through an encrypted SSH channel and its actual stack-control helper were verified; Cockpit GUI clicking was not exercised.

## Data, resources and HTTPS

The dedicated account owns the independent `ideaflow-pgdata` named volume. Do not remove it, prune volumes, reset Podman, run initial-copy scripts again, or restore over the live database. The local `ideaflow_pgdata` volume and other projects remain untouched.

| Container | Memory ceiling | CPU quota | Network exposure |
| --- | --- | --- | --- |
| PostgreSQL | 1,536 MiB | 1.5 CPUs | Container network only |
| FastAPI | 768 MiB | 1 CPU | Container network only |
| React/nginx | 128 MiB | 0.5 CPU | `127.0.0.1:18081` |

The app's total configured memory ceiling is 2,432 MiB, leaving substantial host headroom on the observed 11,671 MiB VPS. Limits were read from each container's cgroups. Container logs cap at 10 MB; Caddy access logs rotate at 10 MiB with five backups. Images are pinned by their full local content IDs in the installed Quadlets. Source templates in `infra/vps/` contain placeholders resolved during the initial release installation; they are not directly runnable with unresolved image names.

Caddy proxies HTTPS port **8443** to loopback **18081** using the existing trusted certificate and automatic renewal. Only the new 8443 firewall rule and IdeaFlow route were added. Shared port 443 retains its prior empty 404, and management endpoints remain loopback-only. External checks confirmed 8443 reachable and 18081, 8000, 5432, 9090 and 2019 inaccessible.

Production authentication uses the configured exact origin, including `:8443`, and a unique **`__Host-ideaflow_session`** cookie with Secure, HttpOnly, SameSite=Strict and Path=/. CSRF tokens remain required for authenticated writes. TLS ends at Caddy; the app does not depend on accepting arbitrary forwarded protocol headers. Local HTTP authentication retains its existing defaults.

## Backups and restore

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/vps.ps1 stack -Command backup
```

The oneshot backup runs `pg_dump -Fc` inside the existing database container. Private dumps and checksums are stored under `/home/ideaflow/backups/`; partial dumps are not promoted. A daily timer runs around **04:00 UTC**, with up to 15 minutes of randomized delay and a persistent catch-up. Scheduled configuration and a manual invocation passed; the first overnight invocation has not yet occurred. No automated deletion policy is enabled: monitor disk use and choose retention deliberately.

The deployment backup **ideaflow-20261009T204728Z.dump** was restored into an isolated database, compared against every live business-table fingerprint and then only that temporary database was dropped. Live data remained unchanged. Its verified off-host copy is `backups/vps-ideaflow-20261009T204728Z.dump` on this Windows machine (gitignored), SHA-256 **3cd010e555393bb4c19361d5895c917223d649c00caf26f491da9833c5a44f1d**. Initial-copy dump SHA-256: **628760e778c151b8d7a7a6ad325f5afcc0334eec95a9571af7795c36dfc77a9c**.

For a new off-host backup, run the backup command, stage only the selected dump into a private `ubuntu` directory with mode 600 via password-authenticated sudo, then use `scripts/vps.ps1 download -File backups/UNIQUE-NAME.dump -Command /home/ubuntu/PRIVATE-DIRECTORY/SELECTED.dump`. The download refuses to overwrite an existing local file and compares SHA-256. Backups contain private account/session data; keep them out of source control. Future automatic off-host copies are not configured.

Live recovery should restore into a separate database/volume and verify it before changing the app's connection. The initial setup scripts intentionally refuse an existing account/volume or Caddy route; they are installation evidence, not an update/reset command. Keep the approved old image IDs and take a fresh backup before an upgrade. Update only IdeaFlow's image pins, reload its user units and restart its target; do not restore the initial snapshot during a code upgrade.

## Optional fictional import

Nothing imports automatically. Admin can validate JSON in **Settings**, inspect the dry-run report, then explicitly confirm. Alternatively, after connecting as `ubuntu`, use password-authenticated sudo to execute the backend importer under the dedicated account:

```bash
cd /tmp
uid=$(id -u ideaflow)
sudo runuser -u ideaflow -- env XDG_RUNTIME_DIR=/run/user/$uid podman exec ideaflow-backend python -m app.demo --batch-key harborworks-demo-v1 --seed 42 --dry-run
sudo runuser -u ideaflow -- env XDG_RUNTIME_DIR=/run/user/$uid podman exec ideaflow-backend python -m app.demo --batch-key harborworks-demo-v1 --seed 42
```

The second line is an explicit data import, not part of deployment or verification. See [DEMO_IMPORT.md](DEMO_IMPORT.md). Additive/idempotent behavior is unchanged. Backend-generated reports/fictional credentials are private in `/home/ideaflow/handover/`; do not project or commit them. Built-in seed/import was not invoked on the VPS.

## Verification and limits

See [VERIFICATION.md](VERIFICATION.md) for actual checks and failures corrected. Local app remains **http://localhost:8080**, with its original three healthy services and preserved volume. Local and VPS are independent copies. Whole-stack stop/start, dedicated user-manager restart/autostart and a subsequent **full VPS reboot** passed. Rootless Podman 5.7 sometimes reports a network-process cleanup permission error on the last container's stop; final restart, data and health checks pass. This upstream runtime message remains documented, not treated as a failed data restore. No SSO, account lockout/rate limiting, off-host alerts or automatic off-host backups were added. TLS secures transport; the application retains its existing local-account authentication model.
