# Governed DD

Try the [ten-task DD example](docs/SIMPLE_DD_TRIAL.md), with copy-ready tasks for DD analyst and DD reviewer.

Local due diligence workspace with Keycloak login, native Paperclip/Codex work, governed evidence/review, PostgreSQL BM25/vector capability, Memgraph and React Explorer. Acceptance work remains in progress; [verification](docs/VERIFICATION.md) records actual checks and gaps. No VPS deployment was performed.

Portal: **http://localhost:8081**. Identity administration: **http://localhost:8081/identity**. Open native Paperclip through engagement Overview; component origins require a membership ticket and separate native credentials.

## Container-only administration

From repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File apps/governed-dd/scripts/governed-dd.ps1 doctor -Context default
powershell -NoProfile -ExecutionPolicy Bypass -File apps/governed-dd/scripts/governed-dd.ps1 build -Context default
powershell -NoProfile -ExecutionPolicy Bypass -File apps/governed-dd/scripts/governed-dd.ps1 setup -Context default
powershell -NoProfile -ExecutionPolicy Bypass -File apps/governed-dd/scripts/governed-dd.ps1 up -Context default
powershell -NoProfile -ExecutionPolicy Bypass -File apps/governed-dd/scripts/governed-dd.ps1 test -Context default
```

The manager verifies Rancher Moby and passes its discovered context explicitly. Python/Node/Codex run in containers. Setup/start begins empty. Provision with `tenant-create -Name <name>` and `tenant-start -Tenant <id>`. Create identity with `user-create -Name <login>`; use returned subject with `member-add -Tenant <id> -Subject <subject> -Role owner|analyst|reviewer|viewer`. `member-remove` revokes membership. `demo-seed` is explicitly additive/idempotent fictional data.

`runtime-enable` requires named `LITELLM_API_KEY`. `native-bootstrap` and `native-user -Name <login> -Role <role>` provision upstream authentication with ingress detached. `database-harden` installs serving-role permissions after schema installation. Other actions: `rebuild-graph`, `reindex`, `tenant-stop`, `status`, `down`, `backup`, `config-check`. Full tenant starts must fit aggregate configured memory reservations; stop inactive tenants rather than bypassing admission.

Private portal passwords: named volume `governed-dd-identity-private`, `<login>.password`. Native credentials: tenant Paperclip volume `native-<login>.json`. Identity bootstrap admin: `governed-dd-admin`; private password `local/secrets/keycloak-admin`. Retrieve privately through administrator tooling; never place values in task text/logs/Git.

[Setup](docs/SETUP.md), [user guide](docs/USER_GUIDE.md), [architecture](docs/ARCHITECTURE.md), [security](docs/SECURITY.md), [records](docs/DD_PROJECT.md), [future VPS migration](docs/VPS_MIGRATION.md). Portable Unix administration uses scripts/governed-dd.sh and the transient Python tooling container; see SETUP.md for commands and verification limits.

Control has four services. Base tenants have five; isolated analyst/reviewer/egress add three and Lab adds one (nine total). All runtime repositories, artifacts, state and backups remain outside platform source control in tenant volumes/private app folders.
