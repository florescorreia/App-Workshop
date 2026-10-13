# App Workshop verification — 2026-10-11

Scope: documentation readiness and PRD-first generation. Current repository is `https://github.com/florescorreia/App-Workshop`; IdeaFlow is under `apps/ideaflow/`. Each new product contract belongs at `apps/<name>/docs/PRD.md`. This document records shared workspace checks; each implemented app needs its own `docs/VERIFICATION.md`.

## Checks for this revision

| Check | Result/evidence |
| --- | --- |
| Existing Git configuration | Read-only inspection confirmed root `main` and origin `https://github.com/florescorreia/App-Workshop.git`; no remote change or repository initialization |
| Container runtime | Rancher Desktop settings reported Moby; discovered context `default` reported Rancher Desktop WSL Distribution; tools invoked with explicit context |
| PRD-first generation | Isolated test created a PRD-only app folder, generated its independent starter and compared the original CRLF PRD bytes exactly; `.env` and nested `.git` remained absent |
| Existing-file protection | Folders containing code or another document were rejected; PRD and catalog remained unchanged |
| Existing generator/release tests | Identity/port separation, traversal/duplicate/collision/drift rejection, image config digests, private bindings, shell syntax and injection/shared-storage rejection passed |
| Documentation audit | All repository Markdown outside private/generated folders checked as UTF-8; relative links resolve. Root/new-app instructions and generated guide/evidence links included |
| Source changes | Only shared generator/tests/documentation changed; IdeaFlow business implementation, volumes, runtime configuration and VPS unchanged |

Commands run from the root through containers:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/workshop.ps1 verify
docker --context default run --rm --mount "type=bind,source=$PWD,target=/workspace,readonly" --entrypoint python ideaflow-vps-tools:1.0.0 scripts/check_docs.py
git diff --check
```

The complete verification run includes eight tests: seven generator/release checks and one Markdown audit. The documentation covers current workflow, shared hosting state, new-app boundaries and dated IdeaFlow evidence. Historic counts/import traces were retained with status notices rather than presented as current data. Current guide paths and GitHub references were corrected. Root/app/template AGENTS.md remain scoped to their respective responsibilities.

## Operational limits

A product brief appeared during the historical documentation review and was outside the implementation scope of that review.

No new product brief was invented, no app registered in the live catalog, no demo import performed and no application/VPS started, restarted or deployed during this revision. Browser tests and full IdeaFlow business regression were not rerun for documentation changes; the previous source-preserving relocation checks (28 backend tests, build/readiness and isolated restore) are in [RELOCATION.md](RELOCATION.md), with prior browser/deployment/reboot evidence in [IdeaFlow verification](../apps/ideaflow/docs/VERIFICATION.md).

Generic VPS installation remains prepared/reviewed tooling, not an exercised second-app deployment. A finished app must define and verify its migrations, least-privilege roles, authentication/account management, business journeys and runtime configuration before publication. Documentation link checks do not verify external websites or live host state; current-host summaries explicitly refer to the last verification on 2026-10-11. Private dependency caches, backup contents and credentials are excluded from the Markdown audit and from commits.
