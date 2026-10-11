# {{APP_TITLE}}

App folder: `apps/{{APP_SLUG}}/`. Read [docs/PRD.md](docs/PRD.md) as the product contract and [the workspace start guide](../../docs/START_NEW_APP.md) for implementation. The generated notes screen is an empty infrastructure example to replace with the specified product. No credentials, data or running services are created by generation.

After completing the PRD, implement/test from the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 init-env -App {{APP_SLUG}}
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 up -App {{APP_SLUG}}
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 test -App {{APP_SLUG}}
```

Reserved local URL: **http://localhost:{{LOCAL_PORT}}**; readiness is verified only after `up` succeeds. Read the generated email/password privately from this app's `.env`. Durable data lives in `{{APP_SLUG}}_pgdata`. `down` and rebuild retain it. Exactly three services run; Python/Node tools are containerized.

Replace this README with the finished product's scope, startup/login instructions, commands, backup/restore and known limits. Complete [USER_GUIDE.md](docs/USER_GUIDE.md) and record actual checks in [VERIFICATION.md](docs/VERIFICATION.md). [ARCHITECTURE.md](docs/ARCHITECTURE.md) explains current starter boundaries. Keep one parent Git repository and no credentials/backups in source control.

Use `status`, `logs`, `backup`, `restore-test` and `down` with the same `-App` option. Deploy only after explicit instruction and app acceptance using [workspace operations](../../docs/APP_WORKSHOP.md). No local-data transfer occurs automatically.
