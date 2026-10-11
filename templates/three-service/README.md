# {{APP_TITLE}}

Independent app in **App Workshop**, folder `apps/{{APP_SLUG}}`. Product definition: [docs/PRD.md](docs/PRD.md). Source shares the parent repository's Git history/remote; do not initialize another Git repository here.

From the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 init-env -App {{APP_SLUG}}
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 up -App {{APP_SLUG}}
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 test -App {{APP_SLUG}}
```

Open **http://localhost:{{LOCAL_PORT}}**. Email and generated password are in this app's private `.env`; do not commit/share/project it. This is a starter for local development, with empty durable notes, not your completed product. Writing a note creates a transactionally associated event. Account/session/password hashes and notes live in `{{APP_SLUG}}_pgdata`. Down/up and rebuild retain that volume. No automatic demo data or host Python/Node.

Use `status`, `logs`, `backup` or `down` with the same `-App` option. Prepare a locally built release with `prepare-vps`; this exports pinned images and reviewable Quadlets/Caddy files but does not write to the VPS. Follow [the workspace deployment guide](../../docs/APP_WORKSHOP.md) to deploy after implementing/testing the product. Never restore local data over an already running production workspace.
