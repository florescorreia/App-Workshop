# Start a new app from a PRD

The permanent location is **`apps/<app-name>/docs/PRD.md`**. Keep the root App Workshop folder open in VS Code so the assistant can read shared tools and the selected app together. Use lowercase letters/numbers/hyphens, start with a letter and keep the app name at most 24 characters.

## 1. Land the product brief

In VS Code Explorer create `apps/supplier-portal/docs/PRD.md` and paste your brief, or copy [the template](../templates/three-service/docs/PRD.md) there. Replace the template's title/slug placeholders and fill in the product sections. Describe the problem, users, main journey, records, rules, screens, calculations if any, scope and observable acceptance criteria. Do not include passwords, tokens or real personal data.

Use `supplier-portal` only as an example; no such app is automatically installed. Start the PRD as Draft if you are still shaping the idea. The assistant can refine the brief with you before implementing; use Ready for implementation when scope is clear. You do not need to invent API endpoints or select libraries.

## 2. Register and prepare the app

Start Rancher Desktop with dockerd/Moby. From the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 doctor
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 new -App supplier-portal
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 list
```

`new` supports two starting states: no app directory, or an app directory containing **only `docs/PRD.md`**. In the latter case it preserves the PRD byte-for-byte. It refuses registered names and folders with other existing files. Do not rerun it over an implemented app. If your draft folder has extra research files, keep them outside that app temporarily or ask the assistant to register the existing folder deliberately without overwriting it.

Generation reserves unique app/Compose/VPS identities and ports in `workshop.json`, creates `app.json`, an app `AGENTS.md`, source/build files, locked dependencies and app docs. It creates no `.env`, records, accounts or running containers. The initial notes screen is a persistence example to replace with your product. A product brief alone can be committed before any implementation.

Alternative: run `new` before creating the folder, then fill in its generated `docs/PRD.md`. Both paths converge on the same structure.

The supplied generator is specifically a React/nginx, FastAPI and PostgreSQL starter. If your PRD requires other services or integrations, have the assistant review that architecture first and deliberately adapt the scaffold, app/catalog metadata, test commands and deployment assets. The generic installer expects the starter's service/environment/health conventions and does not deploy an arbitrary stack automatically. Keep IdeaFlow's established architecture unchanged.

## Implementation prompt

Replace the example app name and paste this into your coding assistant:

```text
Implement the app defined in apps/supplier-portal/docs/PRD.md end to end. Read it completely, plus the root AGENTS.md, apps/supplier-portal/AGENTS.md and docs/APP_WORKSHOP.md. Treat this app's PRD as the implementation contract. If only the PRD exists, register/scaffold it with the shared generator while preserving my brief. Keep source and app documentation in apps/supplier-portal.

Choose routine libraries and implementation details using engineering judgment. Ask about missing product decisions that materially change the result, while progressing on independent work. Replace the starter notes surface with the specified product. Preserve IdeaFlow and all other apps, Git configuration, credentials, ports and volumes.

Build/test in containers through the discovered Rancher Desktop Moby context explicitly. Keep React/nginx, FastAPI and PostgreSQL as the three long-running app services. Make PostgreSQL authoritative; preserve transactional audit evidence and optimistic concurrency for business writes. Implement the PRD's actual account/access rules and versioned migrations. Start with a usable empty workspace and never import showcase data automatically.

Complete meaningful tests, browser/desktop/mobile review, restart/rebuild persistence, backup and isolated restore verification. Fix failures. Record commands/results/limitations in the app's docs/VERIFICATION.md and write its docs/USER_GUIDE.md from a normal user perspective. Report actual local URL, login instructions and any blockers. Do not deploy or mutate the VPS during this local implementation task.
```

## 3. Build and review locally

These commands are normally executed by the implementing assistant, or you can use them yourself:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 init-env -App supplier-portal
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 up -App supplier-portal
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 test -App supplier-portal
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 backup -App supplier-portal
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 restore-test -App supplier-portal
```

Use the actual URL reported by `up`/`list`. Read generated credentials privately from that app's `.env`; they must not appear in committed guides. Review your main journey against the PRD and have the assistant fix UX gaps. Keep accepted product changes in the PRD. Stop local services after review with `down -App supplier-portal`; volumes are retained. The starter's default test command must be adapted if the finished app uses another test runner.

## 4. Commit source

```powershell
git status
git add apps/supplier-portal workshop.json
git diff --cached --stat
git commit -m "Add supplier portal"
git push origin main
```

Review staged files first. Git is shared at the root and does not deploy. Do not create another `.git` inside the app or copy IdeaFlow accounts/data into it.

## 5. Deploy when you are ready

After local acceptance, ask explicitly:

```text
Deploy apps/supplier-portal to the existing VPS using docs/APP_WORKSHOP.md, VPS_FOUNDATION.md, VPS_SECURITY.md and VPS_COCKPIT.md. Keep IdeaFlow and other apps running unchanged. Prepare/review this app's release, separate account/volume, credentials in Windows User environment variables, private bindings, TLS, health checks and backup plan. Start production fresh unless I explicitly request a verified current-data handover. Verify the actual public URL, login, screens, persistence and isolated restore; record evidence and limitations in this app's docs/VERIFICATION.md. Never claim deployment without checks.
```

The generic VPS installer is prepared tooling; it has not yet been exercised with another production app. App-specific least-privilege roles, migrations, authentication protections, runtime limits and recovery procedures must be completed before publishing. See [workspace deployment](APP_WORKSHOP.md#deploy-a-completed-app-to-the-vps).
