# Redeploy IdeaFlow to another machine

The source, pinned dependencies and production release assets here preserve the deployed IdeaFlow implementation. Current live PostgreSQL data remains on the VPS; local `.env` and historical backups are independent and do not track later production edits.

Build/check source with `scripts/workshop.ps1 up -App ideaflow` from the workspace root, then run its app tests, browser checks and backup/restore verification. Stop with `down -App ideaflow` after testing. Exactly three long-running application services remain.

For a different cloud machine, first apply the shared VPS foundation/security/Cockpit guidance in `../../../docs/`. Obtain an explicit current-data handover request and take/download a fresh production backup, restore it into isolated storage and compare tables/event replay before routing traffic. A historical workstation backup alone cannot promise the latest live ideas or logins.

The files under `infra/vps/` are a faithful record of the current release; scripts intentionally contain the original account, host, UID, staging paths and image IDs. They are not portable one-click installers. Copy them into a separate reviewed release, replace host/port bindings, discovered UID/subids, safe staging paths, SSH host-key pins, certificate routes and locally built image content IDs, and place fresh credentials only in Windows User environment variables and mode-600 server files. Do not run the initial-restore scripts against an existing app or reuse a database password by accident.

Keep migration/application database roles, transactional append-only history, secure cookie/origin settings, ordered health checks, direct resource/log limits, per-account shutdown ordering, persistent volume and backup timer. Verify public TLS, login, screens, business-table fingerprints, event replay, isolated restore, container restart/rebuild and a full host reboot before declaring the new deployment ready. Preserve the existing VPS until the new machine has passed acceptance. Source export is faithful; another cloud deployment is not claimed as tested here.


New products follow [START_NEW_APP.md](../../../docs/START_NEW_APP.md); copying this reference app or its historical production snapshot is not their starting point.
