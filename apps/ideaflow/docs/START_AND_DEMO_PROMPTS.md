# IdeaFlow maintenance and optional showcase prompts

IdeaFlow is already implemented at `apps/ideaflow/`. These prompts maintain the reference app; for a new product use [START_NEW_APP.md](../../../docs/START_NEW_APP.md) and that app's own PRD. Keep the root workspace open in VS Code.

## Local maintenance

```text
Read apps/ideaflow/AGENTS.md, its docs/PRD.md completely (accepted amendments override original V1 text), README and docs/VERIFICATION.md. Make the requested IdeaFlow change without altering other apps or the VPS. Use its existing three-service stack, migrations, User/Admin model and transactional history/concurrency. Build/test in containers with the detected Rancher Desktop Moby context, exercise the affected UX and persistence as appropriate, update current docs and record checks actually passed. Stop local containers after testing; retain all volumes and records. Do not import fictional data automatically.
```

## Explicit fictional import, only when requested

```text
Read apps/ideaflow/docs/DEMO_IMPORT.md and its PRD amendments. Stage IdeaFlow locally if needed and import my specified JSON/batch through the backend importer. Validate a dry-run preview before this explicitly authorized additive commit. Preserve every existing account/idea/history, retain fictional provenance, and confirm the same batch is a no-op on repeat. Do not overwrite, reset, backdate ordinary API actions or generate future actuals. Record actual references/counts; old HarborWorks guides are historical and not the current record inventory. Current role labels are User/Admin; business verification is a recorded user review, not independent Finance certification.
```

Supply the target workspace and exact batch/file when requesting an import. Local changes do not synchronize to production. A production import/deploy/restore requires its own explicit instruction. Admin import controls and valid workflow prerequisites remain enforced.
