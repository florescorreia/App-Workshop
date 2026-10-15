# Redeploy IdeaFlow to another machine

The source, pinned dependencies and production release assets here preserve the deployed IdeaFlow implementation. Current live PostgreSQL data remains on the VPS; local `.env` and historical backups are independent and do not track later production edits.

## Update the existing VPS — VAVE release, 2026-10-15

Current release is **1.2.0 / schema 0006**. Code deployment itself creates no programs, ideas, accounts or demo data. The two existing evaluation ideas were adapted separately through explicitly user-authorized, audited API commands. Verified release: `local/releases/vave-20261015T173846Z/`, backend content ID `9cb301d060e450f8a10df078d56fd13bfd59f63ac8723858cc40fa7eca3048c9`, frontend `eeeb57ddd9811988b1345c70a8a603403f58f158bebdf41b9982085b354993c1`. Evidence: [VERIFICATION.md](VERIFICATION.md).

Run from this app folder. Build and test locally first, using the detected Rancher Desktop Moby context explicitly. For isolated testing, include **both** `compose.verify.yaml` and the private port override `artifacts/vave-compose.yaml`; port 18883 avoids governed-dd's 8081. Verify the PostgreSQL mount is `ideaflow_verification_pgdata` before a test journey.

```powershell
docker --context default compose -p ideaflow-verification -f compose.yaml -f compose.verify.yaml -f artifacts/vave-compose.yaml build
docker --context default compose -p ideaflow-verification -f compose.yaml -f compose.verify.yaml -f artifacts/vave-compose.yaml up -d --wait --wait-timeout 180
docker --context default compose -p ideaflow-verification -f compose.yaml -f compose.verify.yaml -f artifacts/vave-compose.yaml exec -T backend pytest -q
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-vave.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/prepare-vave.ps1
```

Preparation exports immutable locally built images and checksums without touching the VPS. Review the printed release directory and its `release.json`. After the user's deployment instruction, pass that exact directory to `scripts/vps.ps1 vave-update -File <release-directory>`, then run `scripts/vps.ps1 app-check`, `scripts/browser-vave.ps1 -Public`, `scripts/vps.ps1 ports-check` and service/event reconciliation checks. The public browser wrapper checks VAVE entry/setup cancellation and the existing HTTPS workspace without business writes.

The updater preserves the existing account, credentials, PostgreSQL volume, network, resource limits and Caddy route. It retains old image archives and Quadlets, pauses only IdeaFlow for a coherent fresh dump, restores the dump into a unique temporary database and compares every table and the reference sequence, downloads and verifies its SHA-256, then changes only backend/frontend image pins. Startup applies the additive migration. Health, credential-file checksums and preexisting rows must match before success is recorded in private `deployment.json`.

On an update verification failure, the updater restores previous image pins and the captured prior readiness marker (0005 or 0006), while retaining additive tables and every business row. It never restores a historical database over production. Rollback assets from the final deployment are `/home/ideaflow/backups/vave-update-20261015T173953Z/`; the previous 1.1 assets remain at `vave-update-20261015T164437Z/`, and the initial pre-VAVE assets also remain at `/home/ideaflow/backups/vave-update-20261015T132654Z/`. An intentional rollback/failure was not exercised in production. Safe recovery requires reviewing the matching prior image/schema pair and verifying current data and health.

## Explicit evaluation-record adaptation

The user's 2026-10-15 instruction authorized converting IF-00205/IF-00206. The operator script is specific to those two records; it creates no accounts and never runs at startup. It first authenticates with unchanged Windows User credentials, inspects existing versions and saves a private proposal. Adoption validates the exact case preview and optimistic version, retains the original snapshot and all old relational/history rows, and starts a fresh Draft/M0 case with no copied approvals/actuals. Bracket M1/M2 completeness reviews are explicit and independent; M3 remains blocked by missing functional acceptance/critical risk.

The reviewed production proposal is `local/vave-adaptation/production-20261015.json`; its applied and preservation files are retained beside it. It was rehearsed on an isolated clone of a verified production backup (`ideaflow_vave_pilot_pgdata`, port 18884) before application. `scripts/vave-adapt.ps1 -Action prepare|apply -File <private-proposal> -LocalNetwork <isolated-network>` supports rehearsal. Production uses `scripts/vps.ps1 vave-adapt-preview|vave-adapt-apply -File <private-proposal>`. Preparation chooses a new file and refuses overwrites; application checks versions and supports resuming the same proposal. The current records are already adopted; do not prepare a new legacy conversion for them or force stale versions.

Apply only after validated code deployment and its fresh restore-verified production backup. The VPS apply wrapper captures a private repeatable-read baseline, compares original account/password, financial/task/comment/reference rows and original events after conversion, and checks replay and credential-file hashes. Only authorized idea fields, new VAVE records/events and ordinary sessions may differ. Evidence remains in `/home/ideaflow/backups/vave-adaptation-20261015T174146Z/`. A code rollback retains all current data; previous code may lack the new adoption/evidence views. Never restore a pre-adaptation dump over production as an image rollback.

## Move to another machine

Build/check source with `scripts/workshop.ps1 up -App ideaflow` from the workspace root, then run its app tests, browser checks and backup/restore verification. Stop with `down -App ideaflow` after testing. Exactly three long-running application services remain.

For a different cloud machine, first apply the shared VPS foundation/security/Cockpit guidance in `../../../docs/`. Obtain an explicit current-data handover request and take/download a fresh production backup, restore it into isolated storage and compare tables/event replay before routing traffic. A historical workstation backup alone cannot promise the latest live ideas or logins.

The files under `infra/vps/` record the initial installation; the current immutable update manifests and retained server Quadlets identify the newer release. Scripts intentionally contain the original account, host, UID, staging paths and image IDs. They are not portable one-click installers. Copy them into a separate reviewed release, replace host/port bindings, discovered UID/subids, safe staging paths, SSH host-key pins, certificate routes and locally built image content IDs, and place fresh credentials only in Windows User environment variables and mode-600 server files. Do not run the initial-restore scripts against an existing app or reuse a database password by accident.

Keep migration/application database roles, transactional append-only history, secure cookie/origin settings, ordered health checks, direct resource/log limits, per-account shutdown ordering, persistent volume and backup timer. Verify public TLS, login, screens, business-table fingerprints, event replay, isolated restore, container restart/rebuild and a full host reboot before declaring the new deployment ready. Preserve the existing VPS until the new machine has passed acceptance. Source export is faithful; another cloud deployment is not claimed as tested here.


New products follow [START_NEW_APP.md](../../../docs/START_NEW_APP.md); copying this reference app or its historical production snapshot is not their starting point.
