# Explicit additive fictional import

No showcase data loads at boot. Run `seed-demo -DryRun` before an explicit commit, or use Admin Settings with a preview. The built-in HarborWorks generator uses seed 42, 60 records and an explicit anchor (default current app-zone date). Batch idempotency depends on persisted `batch_key`, not the anchor or generated titles. Existing records are never updated or deleted. A second batch needs another batch key and unique external keys.

The committed small fixture is `demo/example.json`. It illustrates a new distinct batch containing one idea and a valid New → Screening → Analysis history. Do not expect its single record to equal the 60-record built-in showcase.

The separately authored and imported **12-record v2** fixture is `demo/harborworks-demo-v2.json` (batch key harborworks-demo-v2, seed 84). Its actual references, preservation evidence and live walkthrough are in [DEMO_V2_GUIDE.md](DEMO_V2_GUIDE.md). Repeat it with `seed-demo -File demo/harborworks-demo-v2.json`, retaining the JSON input; the batch key makes it a no-op.

The 2026-10-09 authorized cleanup removed live v1/v2 batches. Their JSON files remain importable, but importing them again now adds a new batch to the current workspace, preserving existing records. Their old references and generated credentials describe the archived backup, not the current live app. Startup does not load them.

Top-level JSON:

```json
{
  "format_version": 1,
  "fictional": true,
  "batch_key": "a-unique-explicit-key",
  "seed": 42,
  "anchor_date": "2026-10-07",
  "people": [{"key":"owner","name":"Fictional Person","email":"person@example.invalid","role":"User"}],
  "ideas": []
}
```

At least one idea is required. Person keys/emails and external idea keys must be unique. Current roles are User and Admin. Older Contributor, Manager and Finance labels are accepted for compatibility and map to User. An existing fictional email may be reused only if name and mapped role match; collisions never overwrite live users. New fictional passwords are generated and written privately to the gitignored handover directory. API/CLI reports never print them.

Each idea contains `external_key`, timezone-aware `created_at`, `creator_key`, `owner_key`, `fields` and ordered `actions`. `fields` supports the normal create contract: title, problem, solution, optional site_id/category_id or site_name/category_name (created on import), optional expected_start/expected_finish and nullable annual_gross/annual_recurring/upfront/probability/confidence. Importer resolves owner UUID from owner_key. Normalized money may be decimal strings. Unknown values use null. Working-capital cash release belongs only in narrative, never recurring benefit sums.

Each action contains `occurred_at`, `actor_key`, `kind` and `data`. Equal timestamps retain array order; sequence resolves ties. Future historical occurrences and future/unelapsed actuals are rejected. The importer validates actor roles, supported transitions, prerequisites and relational links through the domain layer, deriving current state by replay. A failed batch transaction adds no business records or orphan events. Repeating a committed batch is a no-op.

| kind | data |
| --- | --- |
| edit | Partial business-case/milestone fields. `owner_key` can resolve a fictional assignment; all other normal edit fields apply. |
| transition | `action` target stage or Hold/Resume/Reject/Cancel; nonempty `reason`; optional normalized `verification_through` and `confirm_completion` for Realized. |
| plan | annual_gross, annual_recurring, upfront, probability, confidence, rationale; explicit `periods` with month/gross/recurring/spend. Saves a draft. Analysis → Approved approves atomically. |
| task | local `task_key`, title, `assignee_key`, due_date, status and required. Same task_key updates the task through the domain service. |
| comment | nonempty body. |
| result | normalized elapsed `month`, nullable gross/recurring/spend and reason. |
| verify | month, Reviewed gross/recurring/spend and nonempty reason. Requires existing complete actuals. |
| revoke | month and nonempty reason. |

Do not provide `record_version` or `period_version`: replay derives them. Ordinary API endpoints cannot set historical timestamps/actors or import provenance. All imported events visibly retain fictional label, batch key, seed and anchor; recorded_at is the actual import time.

Run the following app-relative commands from `apps/ideaflow/` after deliberate local startup. Import remains Admin-only. PowerShell JSON batch command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 seed-demo -File demo/my-second-batch.json -DryRun
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 seed-demo -File demo/my-second-batch.json
```

CLI equivalent inside the backend is `python -m app.demo --file /demo/example.json --dry-run`. Built-in generator JSON can be exported explicitly with `python -m app.demo --batch-key harborworks-demo-v1 --seed 42 --anchor-date 2026-10-07 --write-json /handover/proposed-dataset.json`. The report lists actual assigned references, counts, validation and whether the batch was a no-op. Dry runs do not reserve readable references; sequence gaps are expected. Import credentials are local sensitive handover files, excluded from git along with reports/backups.
