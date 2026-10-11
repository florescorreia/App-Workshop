# Applications

Create a new independent application with `scripts/workshop.ps1 new -App your-app` from the repository root. New source lives in `apps/your-app/`, with its own PRD, Compose project, environment, named volume and deployment identity. Read [the workspace guide](../docs/APP_WORKSHOP.md) first.

IdeaFlow intentionally remains at the repository root so existing commands, local secrets, Compose mounts, Git history and the production deployment keep working. It is registered as `ideaflow` in `workshop.json`; do not copy it into a second runnable folder with the same project/volume names.

This is one Git repository. Do not run `git init` inside application folders or copy a nested `.git` directory. App-specific data, credentials, artifacts and backups are ignored at every depth.
