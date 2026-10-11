Account controls amendment: migration 0003 adds nullable app_user.deleted_at and account_event (actor FK, plain subject ID/name, action, UTC time, reason). Retired actors retain name/ID and cannot log in; unused accounts may be removed without changing business history. Account events are append-only, independent of lifecycle process discovery, and exclude secrets.

Current amendment (2026-10-09): accounts use User/Admin; idea site_id/category_id are nullable. Sites/categories add normalized unique label_key, record_version and nullable merged_into; active merged sources remain only as redirects. The UI calls sites Locations. See the current PRD amendment and migration 0002.

# Data dictionary and metric definitions

All IDs are UUID strings except legacy/reference identifiers, case sequence integers, readable references and normalized first-of-month dates. Timestamps use PostgreSQL timezone-aware columns and UTC; UI displays America/New_York by default. USD money is `NUMERIC(18,2)`. Nullable amounts mean unassessed/unknown. Nonnegative components may produce negative net benefit or cash flow. PostgreSQL foreign keys, unique keys, checks and snapshot/audit triggers enforce domain integrity.

| Table | Purpose and key constraints |
| --- | --- |
| app_user | Name, unique email, User/Admin roles, Argon2 password hash, active and record_version. Hashes never returned. |
| account_event | Append-only actor/subject/action/time/reason for account administration, excluding secrets. |
| app_session | SHA-256 cookie token digest, user FK, random CSRF token and expiration. |
| site | User-created location: stable ID, normalized label_key, optional business unit, active/merge redirect and record_version. |
| category | User-created category: stable ID, normalized label_key, active/merge redirect and record_version. |
| idea | Unique UUID/readable IF reference, problem/solution, submitter/owner FKs, site/category FKs, separate stage/disposition, progress 0–100, expected/actual dates, screening note/evidence URL, versions/timestamps, unique external import key and optional demo batch FK. Dates are ordered. |
| financial_plan | Per-idea unique version; Draft/Approved/Superseded/Invalidated; annual gross/recurring/upfront, nullable probability/confidence 0–1, rationale, approval actor/time, USD only. Approval contents immutable. |
| financial_plan_period | Plan/month composite key, normalized month, explicit gross/recurring/spend. Approved schedules immutable. |
| value_period | Idea/month composite key; nullable actual components and nullable reviewed components, verification actor/time/reason and period record_version. A corrected actual clears sign-off. |
| task | Idea/assignee FKs, title, due date, Open/In progress/Done, required flag and completion time. Idea version protects changes. |
| comment | Idea/actor FKs, body and occurrence timestamp. |
| idea_event | UUID and unique idea/sequence, event type/activity, from/to stage/disposition, actor, UTC occurrence/recording time, reason, structured old/new metadata and optional fictional import provenance. Append-only. |
| demo_batch | Unique batch key, seed, anchor date, importer, counts and recorded time. |
| alembic_version | Applied schema revision; readiness checks current revision. |

Migration **0005** allows Admin removal of any idea; all nonremoved ideas belong to the same workspace/analytics/exports. The old `is_test` column remains only to preserve historical rows/backups and is neither exposed as a current idea field nor used for filtering. Old `idea_scope` query parameters are ignored. Earlier marking/removal events remain unchanged.

`removed_at`, `removed_by` (retained account FK) and `removal_reason` require complete removal metadata and a nonempty reason. Admin commands `/ideas/{id}/remove` and `/ideas/{id}/restore` require a reason, optimistic version and `confirm: true`. Events `IDEA_REMOVED`/`IDEA_RESTORED` retain actor/time/reason without changing lifecycle stage/disposition. Restoration may record explicit inactive-account reassignments through `ASSIGNED`/`TASK_CHANGED`.

Every ordinary view/export excludes removed records. Admin's `/api/v1/removed-ideas` endpoint searches/paginates the archive; `/ideas/{id}/removal-preview` shows the impact, and removed detail is Admin-only/read-only. Restored records rejoin the shared workspace and totals. Fictional import keys/provenance, financial evidence and events remain retained. There is no hard-delete endpoint.
Annual net potential = annual steady-state gross − annual recurring cost. Upfront implementation cost is excluded. It is never combined with period totals.

Monthly net benefit = gross − recurring; net cash flow = net benefit − implementation spend. Planned values come from approved rows; actuals and verification are independently recorded. Missing results are unknown. Risk-adjusted expected benefit = expected net × probability, with confidence reported independently.

ROI over a labeled horizon = `(sum(net benefit) − sum(spend)) / sum(spend) × 100`. Portfolio ROI uses aggregate sums. Zero spend produces Not applicable; unknown spend produces Insufficient data. Planned cash payback is the earliest month boundary where cumulative planned net cash flow becomes nonnegative after being negative and remains so through the chosen horizon. Elapsed months count from the first spend month. No spend is No upfront investment; no sustained crossing is Beyond plan horizon.

Coverage counts eligible elapsed months in included current approved schedules, reported matched months and verified matched months. Full-horizon forecasts are separate from matched-cohort comparisons. On-hold forecasts are included by default and can be excluded in Value. Rejected/Cancelled forecasts are excluded; achieved historical value remains available. Charts preserve gaps for unreported months and are accompanied by tables.

Process calendar residence includes hold time; active residence subtracts explicitly held intervals. A resume continues a visit, while stage re-entry creates another. Completed medians/p90 exclude open visits. Fewer than five visits is Small sample. Edge performance measures elapsed time between observed activities, with sample counts; a stage is evaluated from completed visits plus separately labeled ongoing aging. Backward moves include Realized corrections and exclude hold/resume.


Idea detail financials default to the current approved schedule (latest saved draft before approval) plus outcome months, falling back to idea dates/current month. The read-only /api/v1/ideas/{id}/value endpoint accepts first-of-month start/end dates with the existing 120-month maximum. Evidence range controls persist as value_start/value_end in the idea URL without refetching/resetting editable forms. Cumulative series restart at the chosen start and preserve unknown gaps; drafts never enter expected value. Portfolio date defaults and formulas are unchanged.
