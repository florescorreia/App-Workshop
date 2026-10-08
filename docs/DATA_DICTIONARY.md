# Data dictionary and metric definitions

All IDs are UUID strings except reference-list codes, case sequence integers, readable references and normalized first-of-month dates. Timestamps use PostgreSQL timezone-aware columns and UTC; UI displays America/New_York by default. USD money is `NUMERIC(18,2)`. Nullable amounts mean unassessed/unknown. Nonnegative components may produce negative net benefit or cash flow. PostgreSQL foreign keys, unique keys, checks and snapshot/audit triggers enforce domain integrity.

| Table | Purpose and key constraints |
| --- | --- |
| app_user | Name, unique email, four roles, Argon2 password hash, active and record_version. Hashes never returned. |
| app_session | SHA-256 cookie token digest, user FK, random CSRF token and expiration. |
| site | Code/label, business unit and active flag. |
| category | Code/label and active flag. |
| idea | Unique UUID/readable IF reference, problem/solution, submitter/owner FKs, site/category FKs, separate stage/disposition, progress 0–100, expected/actual dates, screening note/evidence URL, versions/timestamps, unique external import key and optional demo batch FK. Dates are ordered. |
| financial_plan | Per-idea unique version; Draft/Approved/Superseded/Invalidated; annual gross/recurring/upfront, nullable probability/confidence 0–1, rationale, approval actor/time, USD only. Approval contents immutable. |
| financial_plan_period | Plan/month composite key, normalized month, explicit gross/recurring/spend. Approved schedules immutable. |
| value_period | Idea/month composite key; nullable actual components and nullable Finance-confirmed components, verification actor/time/reason and period record_version. A corrected actual clears sign-off. |
| task | Idea/assignee FKs, title, due date, Open/In progress/Done, required flag and completion time. Idea version protects changes. |
| comment | Idea/actor FKs, body and occurrence timestamp. |
| idea_event | UUID and unique idea/sequence, event type/activity, from/to stage/disposition, actor, UTC occurrence/recording time, reason, structured old/new metadata and optional fictional import provenance. Append-only. |
| demo_batch | Unique batch key, seed, anchor date, importer, counts and recorded time. |
| alembic_version | Applied schema revision; readiness checks current revision. |

Annual net potential = annual steady-state gross − annual recurring cost. Upfront implementation cost is excluded. It is never combined with period totals.

Monthly net benefit = gross − recurring; net cash flow = net benefit − implementation spend. Planned values come from approved rows; actuals and verification are independently recorded. Missing results are unknown. Risk-adjusted expected benefit = expected net × probability, with confidence reported independently.

ROI over a labeled horizon = `(sum(net benefit) − sum(spend)) / sum(spend) × 100`. Portfolio ROI uses aggregate sums. Zero spend produces Not applicable; unknown spend produces Insufficient data. Planned cash payback is the earliest month boundary where cumulative planned net cash flow becomes nonnegative after being negative and remains so through the chosen horizon. Elapsed months count from the first spend month. No spend is No upfront investment; no sustained crossing is Beyond plan horizon.

Coverage counts eligible elapsed months in included current approved schedules, reported matched months and verified matched months. Full-horizon forecasts are separate from matched-cohort comparisons. On-hold forecasts are included by default and can be excluded in Value. Rejected/Cancelled forecasts are excluded; achieved historical value remains available. Charts preserve gaps for unreported months and are accompanied by tables.

Process calendar residence includes hold time; active residence subtracts explicitly held intervals. A resume continues a visit, while stage re-entry creates another. Completed medians/p90 exclude open visits. Fewer than five visits is Small sample. Edge performance measures elapsed time between observed activities, with sample counts; a stage is evaluated from completed visits plus separately labeled ongoing aging. Backward moves include Realized corrections and exclude hold/resume.
