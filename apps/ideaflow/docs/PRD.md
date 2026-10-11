# IdeaFlow — Product Requirements Document

Version: 1.0 | Date: 2026-10-07 | Target: local Rancher Desktop

> Scope: IdeaFlow only, preserved at `apps/ideaflow/`. Read accepted amendments first; they override conflicting original V1 role/preset/test-separation requirements. Current roles are User/Admin and any active account can perform validated business actions; Admin controls accounts, imports and archival removal. Original initial-build/showcase prompts remain historical; do not use this document as a generic new-app PRD. See [the documentation index](README.md) and [new-app guide](../../../docs/START_NEW_APP.md).

## Accepted workspace simplification — 2026-10-09

This amendment implements the user's later instructions and supersedes conflicting V1 role, preset-reference and classification requirements below. The financial formulas, explicit lifecycle prerequisites, transaction/event protections, container architecture and additive importer remain in force.

- Exactly two account roles: **User** and **Admin**. Every active account can create/read/edit/assign ideas, manage tasks, approve monthly plans, make valid forward/backward lifecycle decisions, and record/review/verify/revoke elapsed results. Admin additionally creates/deactivates accounts, sets passwords, and imports fictional datasets. Approval and verification stay separate explicit commands with reasons, identity and immutable history; there is no enforced independent reviewer or finance certification. Recommend another person when independent confirmation matters.
- Start empty with **only the bootstrap Admin**. No predefined locations, categories or business units. Location and category are optional at capture and later stages. Unknown classifications remain null/unassigned and are included in unfiltered portfolio analytics.
- Create/edit forms let every user type a new location/category or choose existing values with keyboard-accessible dropdowns. Normalized whitespace/case/Unicode duplicates resolve to one choice; creation and the idea event commit or roll back together. IDs remain stable and are not user-entered technical codes.
- Everyone can change an individual idea's classifications. Shared Settings allows renaming locations/categories, assigning an optional location business unit, and explicitly merging choices with a reason. Rename/merge updates every affected idea with its own event and version, retains plans/results/lifecycle history, and refreshes current aggregations. A merge retires its source; source spelling/ID resolves to the target. Stale classification/idea edits return 409. A rename does not retain every older spelling as an alias.
- Old non-Admin roles migrate to User, preserving account IDs and all business history. Existing JSON imports accept old role labels as compatibility input mapped to User; no new legacy-role accounts are created. Import remains Admin-only, explicit, additive, validated and batch-idempotent.
- The user explicitly authorized clearing current local data for this iteration. Save and verify a pre-cleanup backup first; clear only this application's business records, references, sessions and non-bootstrap accounts. Retain the bootstrap Admin credentials, schema, volumes, configuration and readable-reference sequence. Cleanup is a one-time operator action and never runs on startup or deployment. Old showcase guides/references become historical evidence.
- Provide a manual walkthrough that starts with capture without Admin definitions, creates/reuses values, regroups them, assigns/works an idea, approves a monthly plan, compares results, and checks history/analytics. Exercise it with a regular User in an isolated workspace and leave live empty.

## Account controls amendment — 2026-10-09

The workspace uses accountability for business actions: all active Users and Admins can work any idea, subject to validated workflow prerequisites; actions retain actor/time/reason. Administrative account access remains restricted to Admin.

- Admin can delete an unused account entirely, including its sessions. An account referenced by ideas, tasks, approvals, result verification, comments, imports or an account audit actor is retired from login, assignments and account management instead, keeping the historical name/ID. Never rewrite/delete idea history. Reassign open active/held non-Realized ideas and open tasks before deletion. Retired accounts cannot be reactivated; inactive accounts can.
- Preserve the signed-in Admin and bootstrap Admin from deletion. Bootstrap Admin remains active/Admin even when another Admin is signed in. Stale account actions return 409; deletion checks and session revocation share a transaction.
- Admin can generate a cryptographically random replacement password for another existing account with a reason. Display it once in the authenticated Admin response/dialog, clear it on close, never include it in history/logs/files. Store only the Argon2 hash. The old password and all previous sessions stop working. Regeneration does not reactivate an inactive account.
- Manual password setting remains available, including the current Admin; resetting your own password signs you out. Settings exposes account-action history with actor, subject, time, action and reason. Account audit rows are append-only and contain no credentials. Deleting an unused account retains its administrative audit subject as a plain ID/name.
- No forced password-change or email delivery workflow is added. The Admin shares generated credentials privately. No existing live account is deleted or reset automatically.

## In-app walkthrough amendment — 2026-10-09

Provide a detailed, general manual available to every signed-in account at **Walkthrough**, with discoverable links from Overview, Settings, the create form and idea workspace. Guide users to choose their own opportunity, scope and baseline, capture without predefined classifications, screen/analyze it, approve an explicit monthly plan, coordinate implementation, report/review elapsed outcomes and interpret value/process evidence. Explain prerequisites, accountability, supported rework and how to reorganize classifications. Include searchable topics, links to relevant app screens, printable instructions and practical troubleshooting. Contextual help opens separately to preserve the current form. The guide creates no example business records and changes no workflow, authorization, financial calculations or architecture.

## Unified ideas and Admin removal amendment — 2026-10-09

This amendment follows the user's request to remove the explicit Test separation and supersedes the earlier Test/removal amendment below.

- All nonremoved ideas use the same capture, register, workflow, My Work, portfolio, Process, Value and exports. Remove Test checkbox/badges, marking controls and idea-set filters. Existing legacy Test flags do not affect behavior or totals; retain earlier rows/events without rewriting history. Old idea_scope bookmarks no longer segregate ideas. Fictional importer provenance remains independent and retained.
- Admin can remove any idea through an explicit removal preview, reason, confirmation and optimistic version. Put the action in a restrained Admin actions control rather than adding noise to normal User work. Removal archives the full idea without changing stage/disposition/plans/results/tasks or deleting history. Ordinary edits are blocked while removed; removed records leave ordinary views and totals.
- Settings → Removed ideas gives Admin read-only inspection and reasoned restoration. Restore to the same shared workspace/stage, validating active ownership and explicitly reassigning inactive open task assignees when needed. Retain all attribution and provenance. No automatic removal/restoration, bulk cleanup, hard deletion, resets or additional services.
- Update the normal-User walkthrough and in-app manual. Practice uses ordinary ideas and can affect totals until Admin removes the exact records after review. No special application-defined practice category or data cohort is required.

## Idea financial evidence timeline clarification — 2026-10-09

Within an idea's Financials, explain actual monthly gross benefit, recurring cost and implementation spend and the separate saved-result review. Cumulative value evidence is calculated, not a data entry form. Its default horizon covers the current approved monthly schedule (or latest saved draft before approval) and saved result months; use idea dates when no financial months exist, then the current month if undated. Benefits may continue after implementation completion. Provide From/Through month controls, Apply date range and Full idea timeline reset, retained in the URL without clearing unsaved forms. Support the existing maximum 120-month horizon; show the latest 120 months if an automatic timeline exceeds it. Keep exact monthly/cumulative supporting values and unknown gaps. Drafts never become approved forecasts. Portfolio calendar-year defaults, formulas, explicit approvals/reviews, records and history remain unchanged.

### Superseded Test/removal amendment — historical design

- Any active user can mark a new idea **Test** at capture. Show a Test badge separately from fictional import provenance. Admin can mark an existing idea Test using a reason and an explicit command; generic edits cannot change that label. Business ideas are the default cohort for register, Pipeline, My Work, portfolio, Process, Value and exports. Users can explicitly choose Test only or Business and test; removed ideas never enter these cohorts.
- Admin can **Remove test idea** using a preview of its stage, owner, tasks, plans, results/verification, comments and history. Require a reason, optimistic version and explicit confirmation. Remove visibility/access to everyday work without deleting any records or changing lifecycle/disposition/approvals/results. Append actor/time/reason and removal metadata in the same transaction. Ordinary edits and workflow commands are blocked while removed.
- Admin has a paginated **Removed test ideas** view and read-only detail/history, and may explicitly restore with a reason and confirmation. Restoration retains the Test label and original lifecycle/history; validate active ownership and open task assignees. Offer an explicit reassignment to an active owner if old accounts became inactive/retired, recording each change. Removed work does not block account retirement but its identities/history remain retained. Shared classification rename/merge remains audited across all affected ideas, including removed records.
- Do not infer Test from titles or automatically relabel/remove existing practice/showcase records. No hard deletion/purge endpoint, reset or automatic cleanup. Rejected/Cancelled remain real lifecycle decisions. Preserve other projects, volumes, import keys and provenance. Update the in-app manual and verify role boundaries, all cohorts/exports, concurrency/atomicity, removal/restoration preservation, restart/rebuild and isolated backup/restore.

## 1. Build mandate

Build a complete, polished, locally deployed idea-to-value application from this document. The starting project contains only `docs/PRD.md`. Create the source code, container definitions, migrations, tests, scripts, and operating documentation required to run it. Use this document as the implementation contract. Proceed through implementation, validation, and deployment; do not stop after scaffolding or a plan.

The application lets non-technical users register improvement ideas, assign responsibility, work ideas through a defined lifecycle, track implementation, and understand their value. A process analytics screen discovers the paths actually followed from an append-only event log and exposes delays and rework.

Deliver exactly three long-running services: React frontend, FastAPI backend, and PostgreSQL. Deploy through Docker Compose on the user's **local Rancher Desktop**. Kubernetes is unnecessary. All development dependencies can run inside containers; host Node.js, Python, PostgreSQL, or administrator rights must not be prerequisites.

Product name: **IdeaFlow**. This is an original implementation of common idea-management workflows, with its own interface and branding.

### Success criteria

1. A non-technical presenter can create an idea, assign it, advance it, approve a value plan, record monthly results, and see dashboards update.
2. The process view shows observed paths, bottlenecks, rework, and current aging using persisted events.
3. Reloading the browser, restarting containers, and rebuilding images preserve business records.
4. First startup is empty and usable. Loading fictional showcase data is a separate, explicit action.
5. The final handover gives the exact local URL, verified deployment commands, tests performed, and a short showcase script.

## 2. Scope and constraints

### Required in V1

- Idea register, guided create/edit forms, search, filters, and a detail workspace.
- Personal work list, lifecycle board, assignments, milestones, simple tasks, and comments.
- Explicit workflow transitions with reasons, server-side role checks, and recorded history.
- Monthly expected, actual, and finance-verified value; approved plan snapshots; documented ROI and payback calculations.
- Embedded portfolio, implementation, financial, and process dashboards.
- Event CSV export and idea register CSV export.
- Minimal local authentication and four roles.
- Deterministic, additive fictional demo import and an eight-minute presentation guide.
- Persistence, migrations, backup/restore instructions, and meaningful verification.

### Defer

Agents, AI calls, Paperclip, MCP, Marimo, Dagster, dbt, OpenMetadata, MinIO, separate BI platforms, ERP integration, Kubernetes, SSO, multi-tenancy, configurable workflow builders, file uploads, email notifications, NPV/IRR, and automatic external actions. Do not add these to prove the architecture. A text comment or evidence URL is enough for V1.

Local authentication is a small app feature, not an enterprise identity platform. No paid services or external runtime APIs. Build-time downloads of dependencies and images are expected; the running application must work without internet access. Bundle fonts and assets locally.

## 3. Users and permissions

| Role | Responsibilities | Allowed operations |
| --- | --- | --- |
| Contributor | Submit and develop ideas | Create; read portfolio; comment; edit own New ideas; work assigned ideas/tasks |
| Manager | Evaluate and run initiatives | Assign owners; edit business cases; approve plans; perform workflow transitions; manage tasks |
| Finance | Confirm reported gains | Read all; record financial results; verify/unverify a period with a reason; send Validation back for rework; mark Realized |
| Admin | Operate the local application | Manager and Finance permissions; manage local users; import demo datasets |

All authenticated users can read the local portfolio. Contributors assigned as owners may perform New → Screening, Screening → Analysis, and Implementation → Validation; manager-only decisions remain enforced. Finance may perform Validation → Implementation and Validation → Realized. Publish this permission matrix in the README and test it at the API boundary.

Bootstrap one Admin account from `.env`, with no committed real password. Provide a script that creates `.env` from `.env.example` with generated local secrets and prints the first-login instructions privately. Demo import creates fictional role-specific accounts with generated passwords and records those credentials in a gitignored local handover file. Never expose password hashes or secrets in API responses or logs. Login/logout and current-user display are required; a server-issued HttpOnly session cookie is sufficient. Same-origin reverse proxy avoids unnecessary CORS complexity. Passwords must use an established password-hashing library.

## 4. Information architecture and design

Sidebar: **Overview, Ideas, My Work, Pipeline, Process, Value, Settings**.

Use a clean business application aesthetic: warm white background, dark navy sidebar, restrained teal accent, clear typography, generous spacing, compact readable tables, and distinct stage/status chips. Display currency consistently as USD, with abbreviations on charts and exact amounts in detail/tooltips. Put plain-language explanations beside unfamiliar metrics. Avoid decorative charts that do not help a decision.

- Desktop: optimized for 1440 × 900; usable at 1280 × 720. Small screens: navigation collapses, tables scroll, cards stack.
- Accessibility: labeled controls, keyboard operation, visible focus, sufficient contrast, and charts accompanied by a summary/table. Never encode meaning through color alone.
- Dates display in the configured application timezone, default America/New_York; persist timestamps in UTC.
- Loading, empty, error, and permission-denied states must be designed. Failed edits preserve user input. No fake success notifications.
- Active filters are visible, resettable, and retained in URL query parameters where useful. Detail screens return to the previous list/filter state.
- No database names, container jargon, or implementation instructions in ordinary business screens. Show a subtle “Fictional demo data” badge on imported demo records.

### Overview

Show an as-of timestamp, a shared site/business-unit/category filter bar, stage counts, active ideas, overdue initiatives, and open approvals. Show three clearly labeled value cards: annual net potential, approved net benefit for the selected horizon, and verified net benefit through the as-of date. Include a lifecycle distribution, top opportunities table, and action-oriented exceptions list. Clicking counts/charts opens the filtered idea register.

### Ideas

Search title/description/reference; filter site, business unit, category, owner, stage, and disposition. Sort by age, annual gain, expected completion, or updated date. Paginate server-side. Columns: reference, title, owner, site, stage, disposition, annual net potential, expected finish, current stage age. Provide New idea, saved record links, and export of the filtered register.

### Create idea

Required: title, description/problem, proposed improvement, site, category. Owner defaults to the submitter. Optional initial annual benefit estimate, upfront implementation cost, recurring annual cost, probability, confidence, and expected dates. Unassessed amounts remain unknown (`null`), never silently become zero. Clearly separate probability of success from confidence in the estimate.

### Idea workspace

Header: reference, title, stage/disposition, owner, site, expected finish, and explicit next-action buttons. Tabs:

1. **Overview:** problem, proposed solution, category, assignments, dates, progress, evidence URLs, and comments.
2. **Financials:** editable draft, monthly plan, approved plan version, results grid, metric explanations, and cumulative value chart.
3. **Implementation:** editable tasks with assignee, due date, status; progress percentage; planned/actual start and completion.
4. **History:** immutable chronological events with actor, occurrence date, recorded date where different, reason, and meaningful field changes.

Manager approval uses a preview showing the exact plan to approve. Workflow dialogs explain missing required fields. An idea's estimated gain is not a finance-approved saving. A recorded outcome is not automatically verified.

### My Work

Current user's assigned ideas and tasks; overdue items first; quick links to update an idea, complete a task, or add a comment. Empty state has a clear next step.

### Pipeline

Seven lifecycle columns with count and annual net potential totals. Cards show reference, title, owner, site, age, due date, and value. Include a separate visible disposition filter for On hold, Rejected, and Cancelled records. On-hold cards retain their current lifecycle column and display a hold badge.

Provide an accessible Move action on every card. Dragging is optional; if included, dragging invokes the same transition dialog and server validation as buttons. Never allow dragging to bypass required approvals or silently skip stages.

### Process

An observed directly-follows process graph, edge frequency/performance switch, stage duration chart, top path variants table, and aging/bottleneck table. Clicking an edge, variant, or stage opens contributing ideas. Explain observed paths versus the intended lifecycle. Show sample sizes and distinguish completed visits from ongoing visits. Details appear in section 8.

### Value

Month range, site/business-unit/category filters; monthly/cumulative toggle; expected-versus-actual-versus-verified net benefit chart; implementation spend chart; idea variance table; approved plan version/as-of labels. Show annual net potential separately from period totals. Include a comparison of planned and actual cumulative cash flow, portfolio ROI, and payback where meaningful. Details appear in section 7.

### Settings

Current user/profile, site/category reference lists, Admin user management, and a read-only explanation of the lifecycle and financial definitions. Demo loading is an Admin action or CLI command, never an automatic startup routine. No workflow designer in V1.

## 5. Lifecycle contract

Represent **stage** and **disposition** separately.

Stages in order: New → Screening → Analysis → Approved → Implementation → Validation → Realized.

Dispositions: Active, On hold, Rejected, Cancelled. Keep the stage when disposition changes. On hold freezes workflow transitions until resumed; its time remains measurable. Rejected/Cancelled are terminal in V1. Realized ends the lifecycle; correcting a realized record is an Admin/Finance return to Validation with a reason, preserving all verification and history.

| Transition | Required conditions |
| --- | --- |
| New → Screening | Title, problem, proposed improvement, site/category, and owner |
| Screening → Analysis | Manager/owner has recorded screening note |
| Analysis → Approved | Manager; approved financial snapshot with monthly plan, probability, costs, expected start/finish; approval reason |
| Approved → Implementation | Manager; owner, actual start, at least one implementation task |
| Implementation → Validation | Owner/manager; actual completion date, 100% progress, and required tasks completed |
| Validation → Realized | Finance/Admin; at least one elapsed period with verified financial results; verification-through month; confirmation of implementation completion |
| Analysis → Screening | Manager; rework reason |
| Approved → Analysis | Manager; invalidate current approval; rework reason |
| Validation → Implementation | Finance/manager; rework reason; reopen/update tasks/progress |
| Realized → Validation | Finance/Admin; correction reason |

Hold/resume: owner or manager, non-empty reason, available before Realized. Reject: manager from New/Screening/Analysis, reason. Cancel: manager before Realized, reason. Other transitions are invalid. Return permitted transitions and unmet prerequisites from the API, so the UI can explain them.

Advancing to Approved and approving the associated financial version must occur in one database transaction. A revised approved plan requires a manager reapproval and a new snapshot; drafts alone do not change dashboard forecasts. Resume returns to the same stage. Record holds explicitly rather than inferring them from missing updates.

Use optimistic concurrency on all business edits: integer record version or equivalent, submitted by the client. A stale update returns HTTP 409 with a useful refresh message. No partial writes or orphan events.

## 6. System of record and event model

PostgreSQL is authoritative. Frontend state is transient. Seed data, metric outputs, and current workflow state must not live solely in JSON files or browser storage.

Use SQLAlchemy, Alembic migrations, and PostgreSQL constraints. Prefer a small coherent schema:

| Entity | Key fields |
| --- | --- |
| user | UUID, name, email, role, password hash, active, created_at |
| site/category | ID, label, active; site includes business unit |
| idea | UUID, unique readable reference, title, problem, solution, submitter/owner IDs, site/category, stage, disposition, progress, expected/actual dates, record_version, timestamps, external_key, demo_batch_id |
| financial_plan | ID, idea ID, version, Draft/Approved/Superseded/Invalidated, annual gross benefit, annual recurring cost, upfront estimate, probability, confidence, rationale, approved_by/at, plan_currency |
| financial_plan_period | Plan ID + month unique, expected gross benefit, expected recurring cost, expected implementation spend |
| value_period | Idea ID + month unique, actual gross benefit, actual recurring cost, actual implementation spend, nullable verified values for all three, verified_by/at, reason, record_version |
| task | ID, idea ID, title, assignee, due date, Open/In progress/Done, required flag, completed_at |
| comment | ID, idea ID, actor, body, created_at |
| idea_event | Event UUID, idea ID, per-case sequence, activity, event type, from/to stage and disposition, actor, occurred_at, recorded_at, reason, structured change metadata, import provenance |
| demo_batch | ID, unique batch_key, seed, anchor_date, importer, counts, recorded_at |

Use decimal/numeric money values; no floating-point storage. Currency is USD only in V1. Probabilities/confidence are nullable until assessed, then between 0 and 1; progress is 0–100. Store months as normalized first-of-month dates. Validate nonnegative benefits/cost components and verified values; net benefit can be negative. Validate date ordering and foreign keys. Zero cost is valid; unknown cost is distinct from zero. Do not hard-delete ideas in V1.

### Event requirements

- Every create, substantive edit, assignment, task change, financial plan revision/approval, result update, verification/unverification, comment, transition, hold/resume, rejection, and cancellation creates an event in the **same transaction** as its business change.
- Live actions get server timestamps and actor identity from the authenticated session. Ordinary clients cannot choose their audit actor or backdate events.
- Persist UTC timestamps; deterministic ordering is `(occurred_at, sequence, event_id)`. Enforce unique `(idea_id, sequence)` using case-level locking or equivalent.
- Keep `recorded_at` separately for imported historical demo events. Import provenance and fictional-data labels remain visible. Future plans are allowed; future historical occurrences or actuals are not.
- Audit rows are append-only. Application database role cannot update/delete them; migration/admin role is separate. Use DB permissions and/or a database trigger. This is an application audit trail, not a claim of cryptographic tamper resistance.
- Store old/new values for substantive fields; never passwords or session secrets.
- Distinguish business events (`STAGE_CHANGED`, `HELD`, `RESUMED`) from edits/comments; process discovery does not treat typing a comment as a workflow step.
- Event CSV provides at least `case_id`, `activity`, `timestamp`, `resource`, `sequence`, `recorded_at`, and import provenance. A lifecycle-only export is the default; offer all-events export separately.

## 7. Financial definitions and dashboard correctness

Implement financial calculations in a single tested backend service. The frontend formats returned values and does not implement a conflicting formula set.

### Definitions

- **Annual net potential:** estimated steady-state annual gross benefit minus recurring annual operating cost. It excludes one-time implementation cost and is a run-rate estimate, not achieved value.
- **Expected net benefit in month m:** expected gross benefit minus expected recurring operating cost for that month.
- **Actual net benefit:** recorded actual gross benefit minus actual recurring cost. Missing actuals are unknown, never zero.
- **Verified net benefit:** finance-confirmed gross benefit minus finance-confirmed recurring cost. Finance can verify an actual unchanged or adjust it with a reason. Unverified is unknown.
- **Implementation spend:** separate one-time/project cost cash flow, planned/actual/verified by month. Never subtract it twice.
- **Net cash flow:** period net benefit minus implementation spend.
- **Risk-adjusted expected benefit:** expected net benefit × probability of success. Do not also multiply by confidence. Show missing probability explicitly; do not default to 100%.
- **ROI over the selected horizon:** `(sum(net benefit) − sum(implementation spend)) / sum(implementation spend) × 100`. Label Planned, Actual-to-date, or Verified-to-date and show the horizon. Zero/unknown spend yields “Not applicable”/“Insufficient data”, not infinity.
- **Planned cash payback:** earliest monthly boundary at which cumulative planned net cash flow turns nonnegative after having been negative, and remains nonnegative within the selected plan horizon. Show month and elapsed months from first spend. If no initial investment, “No upfront investment”; if not reached, “Beyond plan horizon”. Do not estimate with steady-state benefit when the ramp is known.
- **Portfolio ROI:** ratio of aggregate cash flows/spend, never the arithmetic mean of individual ROI percentages.

Example for calculation tests: annual gross benefit $120,000; recurring annual cost $12,000; upfront implementation spend $30,000; January implementation spend $30,000 and benefit $0; February–December gross benefit $10,000/month and recurring cost $1,000/month. Annual steady-state net potential is $108,000; first-year plan net benefit is $99,000; first-year net cash flow is $69,000; first-year ROI is 230%; cash payback occurs at May month-end. At 70% probability, first-year risk-adjusted expected benefit is $69,300. These are different metrics and must keep different labels.

### Plan and result rules

Monthly schedules are explicit editable rows, typically 12–24 months. Provide a “Generate ramp” helper: start month, months to reach steady state, horizon, and implementation-spend allocation. Preview and edit before saving; approved snapshots are immutable. Derive all expected period totals from the approved schedule, not from annual estimates divided by 12 without considering ramp-up.

Draft estimates inform potential cards. Implementation forecasts use the latest valid approved plan. Retain all earlier plan versions and allow view-only comparison. If an approval is invalidated, exclude it from current approved forecasts and clearly mark the record.

Actuals are recorded for elapsed months only. Future actual/verified values are invalid. Period completion and verification are independent of lifecycle stage; a Realized initiative may continue monthly value reporting. Verification changes append an event. Editing a verified actual requires a reason and clears verification for that period atomically; it cannot preserve a stale finance sign-off.

Default actual-versus-plan comparisons use elapsed months through the last completed month. For every aggregate, report coverage: e.g., “14 of 20 eligible idea-months reported; 9 verified”. Expected comparison totals use the **same idea/month cohort** as the corresponding actual or verified comparison. Full expected horizon is a separate series/card. Do not draw missing actuals as zero or visually connect gaps without an explanation.

Avoid double counting annual run rates with period savings, or summing the same idea across lifecycle stage buckets. Active/current approved forecasts exclude Rejected and Cancelled. On-hold approved plans remain visible with a hold indicator and a documented include/exclude filter. Historical achieved value remains available for cancelled initiatives. Every aggregate endpoint applies the same visible filters and clearly states the included cohort.

## 8. Process analytics specification

Build lightweight process discovery directly from lifecycle events inside the FastAPI service. SQL/Python is sufficient for V1; **PM4Py is optional, not a deployment dependency**. If added later, review its current license and dependencies. The goal is useful observed paths and timing, not a conformance engine or a Celonis clone.

### Case selection and event scope

- Case ID = idea ID. Activity = lifecycle stage entered, plus On hold/Resumed/Rejected/Cancelled where appropriate. Resource = actor ID/name. Timestamp = occurred_at.
- Include New at creation. Re-entry produces a new visit. Keep holds and terminal dispositions visible.
- Filters select cases by site/business unit/category/owner and **creation-date cohort**. Once a case is selected, load its complete lifecycle history through the as-of timestamp. Do not clip events to the creation-date filter and create artificial paths.
- Separate “all selected cases” and “completed cases only” views. In-progress paths are partial; label them.

### Required metrics

1. **Directly-follows graph:** count consecutive activity pairs per trace, with total traversals and distinct case count. Display an observed graph, including rework edges, not the hardcoded intended workflow. Provide edge median elapsed days and case drilldown. Include start/end markers; partial cases have an in-progress end marker.
2. **Stage visits:** time from stage entry to next stage change or terminal disposition. Split on-hold intervals to calculate calendar residence, active residence, and hold time. Resume continues the same stage visit. Re-entry is a new visit. Open visits are right-censored: exclude them from completed-visit medians and show their current age separately.
3. **Duration distribution:** median and p90 completed stage duration, sample sizes, and a selectable calendar/active-time basis. With fewer than five visits, display “Small sample”.
4. **Rework:** fraction of selected cases with a backward lifecycle move; show numerator/denominator and repeated visits. Realized → Validation is a correction path and counts as rework with its own label. Hold/resume does not count as rework.
5. **Variants:** ordered observed activity sequences, case count, cohort share, completion status, and median completed case duration. Exclude ordinary edits/comments.
6. **Bottlenecks/current aging:** stages ranked by completed-visit duration; open case count, oldest active age, overdue count, and on-hold >30 days. Do not call a stage a bottleneck based solely on a single old open case.
7. **Case throughput:** completed (Realized) cases by month, and created → first Realized elapsed time for completed cases. Label calendar versus active-time choice.

For the graph, use a lightweight open-source graph renderer (e.g., React Flow with automatic layout) and the same backend-derived edge data for its supporting table. Frequency labels should not be ambiguous. Ensure graph readability with seven stages plus disposition branches. Plotly can render duration and throughput charts. Cached metrics, if any, must invalidate on writes and honor as-of/filter parameters; computing live is adequate for demo scale.

## 9. Technical architecture and API

### Services

| Service | Implementation | Responsibility |
| --- | --- | --- |
| frontend | React + TypeScript + Vite build; nginx static server/reverse proxy | Business UI; embedded Plotly charts; graph view; `/api` proxy |
| backend | FastAPI + SQLAlchemy + Alembic + PostgreSQL driver | Auth, permissions, commands, calculations, event generation, exports, demo importer |
| postgres | Supported PostgreSQL image pinned to an explicit version | Durable transactional records and event history |

Choose current compatible stable package versions during implementation; pin images and lock dependencies. Prefer container multi-stage builds; no `latest` tags. Include third-party dependency/license inventory. Do not write a homegrown authentication or graph-layout algorithm when a small established library fits.

### API capabilities

Implement versioned `/api/v1` routes with typed schemas and OpenAPI:

- Session login/logout/me; Admin user creation/update.
- Reference lists: sites, categories, users for assignment.
- Paginated ideas list/get/create/update; filtered CSV export.
- Allowed transitions/prerequisites and workflow transition command.
- Assignment, tasks, comments, and chronological history.
- Financial drafts, approved snapshot history, monthly schedule, explicit approval/reapproval.
- Monthly actuals, verification and verification revocation.
- Portfolio, value, process graph, visits/aging, variants, and drilldown queries.
- Event export; Admin demo import with dry run/manifest and batch idempotency.
- `/api/health/live` and `/api/health/ready`; readiness verifies database and migration readiness.

No generic endpoint may directly change stage, disposition, approval state, or verified values. Those are explicit domain commands. Validate all parameters and use parameterized queries. CSV export must escape cells that spreadsheet applications could interpret as formulas. Session CSRF protection or equivalent same-origin defense must cover mutations. Provide concise errors with actionable messages.

## 10. Rancher Desktop deployment contract

Assume the user has Rancher Desktop installed on Windows and uses VS Code/Codex. The build agent is running on the user's laptop, not on a remote runtime. Never claim local deployment if the current agent cannot access that laptop's engine.

### Preflight

1. Inspect `docker version`, `docker compose version`, `docker context ls`, and the active context. Verify a server is reachable, not only a CLI.
2. Use Rancher Desktop with **dockerd/Moby**, which supports Docker CLI/API. Discover its context name from the installed version; do not assume all versions use the same name. Use explicit `--context <detected-context>` in scripts so another local Docker engine is not selected accidentally.
3. If the engine is containerd-only, explain the exact Rancher Desktop preference to select Moby. Do not switch/reset the user's engine or change Kubernetes/system configuration automatically; complete the source deliverables and report the concrete prerequisite if blocked.
4. Kubernetes can remain off; if already enabled, leave it alone.
5. Check port 8080 before binding. If occupied, use `APP_PORT` override and report the actual URL. Account for locked-down enterprise networks with actionable dependency-download errors.

### Compose configuration

- `compose.yaml` with project name `ideaflow`; services named `frontend`, `backend`, `postgres`; internal service DNS names.
- Publish only frontend: `127.0.0.1:${APP_PORT:-8080}:80`. Browser URL defaults to `http://localhost:8080`.
- nginx proxies `/api/` to `backend:8000`, preserving the prefix expected by FastAPI, and supports SPA route refreshes.
- Backend and PostgreSQL have internal network exposure only. Do not publish PostgreSQL port by default.
- Named volume `ideaflow_pgdata`, with the correct PostgreSQL data mount for the selected image version. No persistent business data in the writable layer of a container.
- Database health check; startup readiness dependencies; backend runs migrations once before serving; frontend/backend readiness and restart policy.
- `.env.example` documents local settings and placeholders. `.env`, passwords, backups, and local demo credentials are gitignored. Never embed secrets in frontend bundles.
- Regular `docker compose down` preserves data. Never run `down -v`, factory reset, or destructive demo cleanup as routine setup/recovery.
- Stable project/volume naming on rebuild; source remains in the project folder. Exported backups are stored outside container volumes.

### Scripts and docs

Provide Windows PowerShell first-class scripts and equivalents for bash:

- `doctor`: preflight and detected context; no mutation.
- `init-env`: create missing local configuration; do not overwrite existing secrets.
- `up`: build/start, wait for readiness, show actual URL.
- `status`, `logs`, `down`: routine operation, preserving volumes.
- `seed-demo`: explicit, additive, idempotent, with dry-run support.
- `backup`: `pg_dump` custom format to a timestamped local file, capturing stdout as binary safely on Windows. Avoid PowerShell text redirection of custom-format dump bytes.
- `restore-test`: restore backup into a separate temporary test database, verify row counts/events, and remove only that temporary test database. Restoring over the live database is a separate explicit user action.

Scripts must work from paths containing spaces. Do not depend on Make, bash, `curl`, host Python, or host Node on Windows. Run seed, migrations, and tests through Compose `exec`/`run`; development/test containers may be transient while the deployed app still has three long-running services.

README must explain first run, login, demo loading, restart/rebuild persistence, backup/restore, port conflicts, engine/context issues, and where all durable state lives. Separate tested commands from untested alternatives.

## 11. Fictional showcase data and injection contract

Startup creates only necessary reference data and the bootstrap Admin. The empty app must be fully useful. Loading demo data requires an explicit `seed-demo` invocation or Admin confirmation with a preview.

### Built-in showcase dataset

Fictional company: **HarborWorks Manufacturing**. Sites: Tampa, Atlanta, Dallas; business units: Assembly and Distribution. Categories: Procurement, Freight, Inventory, Energy, Scrap/Quality, Productivity, Working Capital. Use fictional people and USD.

Create **60 ideas** across the previous 18 months relative to an explicit anchor date, defaulting to the current date in the application timezone. Deterministic seed: 42. Include 15 manually authored, credible titles with specific problems; vary supporting details for the remainder. All records are labeled fictional. No automatic periodic generation.

Include every lifecycle stage, at least five held cases, six rejected cases, three cancelled cases, eight cases with rework, twelve Realized cases, and six overdue active initiatives. Subsets may overlap where the workflow permits. Make Analysis a plausible bottleneck with uneven durations, not a perfect funnel. Holds have explicit start/resume history; some remain open. Events run only through the anchor timestamp. Future expected schedules are allowed.

Use coherent chronological traces and relationally consistent current states. Generate approved financial schedules for Approved and later cases, implementation tasks, comments, monthly actuals with lag/variance, and finance verification for appropriate elapsed periods. Make missing actuals/verification deliberate. Some ideas beat plan, some lag, and some have negative net cash flow during implementation.

Hero ideas:

| Idea | Narrative | Target showcase state |
| --- | --- | --- |
| Consolidate outbound freight into scheduled routes | Reduce partially loaded dispatches without hurting service | Implementation, two reported months below plan |
| Repair compressed-air leaks at Tampa | Metered energy reduction after a small repair program | Realized, verified savings |
| Standardize corrugated packaging across sites | Fewer sizes and better supplier pricing | Analysis, awaiting supplier quotations |
| Reduce changeover scrap on assembly line 2 | Trial new settings and operator checklist | Validation, awaiting Finance review |
| Rationalize slow-moving inventory | Reduce carrying cost; separate cash release | On hold in Analysis |

Working capital release is not recurring P&L savings. For V1, keep cash release as a narrative/non-summed supplemental field or a separately labeled metric; never add it to recurring benefit cards.

### Import mechanics

- A persisted batch key and external keys make rerunning the same seed a no-op with a clear report.
- Default batch key: `harborworks-demo-v1`; changing the anchor date alone must not duplicate the batch. Adding a distinct batch requires a new explicit key.
- Import uses the backend domain/service layer in one controlled transaction or recoverable batch, not arbitrary ad hoc SQL that bypasses audit logic.
- Historical timestamps/actors are allowed only in the Admin/demo import path and carry provenance. Validate histories against the transition rules and derive current state by replay rather than assigning an unrelated final stage.
- Provide a dry run with counts, validation findings, batch key, and anchor date before commit.
- Add a JSON import format and a committed small example fixture. Support a second additive batch without replacing user-created records or the first demo.
- Never reset the database to load data. No destructive reset is part of the showcase prompt.
- After import, verify record/event counts, consistency, dashboard totals, path variants, and idempotency. Save a short import report.

## 12. Acceptance and verification

Implement meaningful backend tests and a browser smoke test; do not test only implementation details. Run these before handover:

| Area | Required evidence |
| --- | --- |
| First boot | Starting with an empty named volume creates schema/reference data/Admin and opens usable empty screens |
| End-to-end workflow | Create → Screening → Analysis → approve → Implementation → Validation → Realized; tasks/results/verification persisted |
| Permissions | Contributor cannot approve or verify via direct API requests; Finance actions follow matrix |
| Atomicity/concurrency | Invalid transition adds no state/event; stale edit returns 409; concurrent updates cannot lose an event |
| Audit | Valid mutation appends event; application role cannot update/delete events; ordinary API cannot backdate |
| Financials | Section 7 example passes; zero cost/unknown/missing results handled; editing verified actual clears sign-off; monthly cohort coverage reconciles |
| Process | Known fixture with hold, rework, ongoing case, tied timestamps, and rejected case yields expected edges, variants, durations, and censored counts |
| Import | Same batch twice gives no duplicates; second batch is additive; chronology and replay match current state |
| UI | Create/edit/transition; browser refresh of nested routes; filtering/drilldown; chart tables; no console errors in tested flows |
| Persistence | Record a unique idea and result, down/up and rebuild, confirm business rows/events remain |
| Backup | Produce dump, restore into isolated test database, verify ideas/events/financials; leave live DB unchanged |

Review screenshots at 1440 × 900 and 1280 × 720. Verify Overview, register, detail financials, Pipeline, Process, and Value; fix clipped labels, broken charts, invisible actions, and unreadable graph layout. Use containerized Playwright or available browser tooling. If an enterprise constraint blocks a check, report precisely what was not verified and the command the user can run; do not fabricate success.

## 13. Implementation sequence and deliverables

Work in vertical slices:

1. Repo scaffold, Compose, database migration, session auth, empty UI, and local readiness.
2. Idea create/edit/assignment; lifecycle commands, transactional event log, history, and concurrency.
3. Work list, tasks/comments, board, and role-specific actions.
4. Financial plans/snapshots, schedules/results/verification, calculations and Value view.
5. Process discovery/aging/variants and portfolio dashboards with drilldowns.
6. Fictional demo importer, JSON format, presentation guide, persistence/backup validation, UI polish, and final local deployment.

Create at minimum:

- `frontend/`, `backend/`, `compose.yaml`, `.env.example`, `.gitignore`, dependency lockfiles, and image build files.
- Alembic migrations, financial/process/workflow tests, demo importer and example JSON fixture.
- PowerShell/bash scripts, `README.md`, `docs/ARCHITECTURE.md`, `docs/DATA_DICTIONARY.md`, `docs/DEMO_GUIDE.md`, and `docs/VERIFICATION.md`.
- `AGENTS.md` summarizing the PRD constraints: three services, container-based local deployment, persisted state, transactional events, explicit commands, additive demo import, and no destructive resets.

In `docs/VERIFICATION.md`, record commands actually run, results, deployed context/URL, app version, and limitations without secrets. In `docs/DEMO_GUIDE.md`, give an eight-minute story for a non-technical audience: see portfolio → create idea → work/assign → show observed bottleneck → show implementation gains/ROI → finance-verify a period. Distinguish live actions from historical imported demo data. Include troubleshooting if there is no demo data or a role lacks permission.

Final build-agent response must state what runs, the exact local URL, how to log in, the exact explicit demo-load command, validation performed, and any blockers. Deployment on the user's laptop is part of completion when that runtime is available. The PRD author is not claiming to have deployed an application by providing this document.

## 14. Reference documentation

Consult official documentation during the build for the installed versions; dependency versions and Rancher Desktop context names may change.

- Rancher Desktop engine options: https://docs.rancherdesktop.io/ui/preferences/container-engine/general/
- Rancher Desktop installation/CLI utilities: https://docs.rancherdesktop.io/getting-started/installation/
- Rancher Desktop 2 context discussion: https://github.com/rancher-sandbox/docs.rancherdesktop.io/blob/main/blog/2026-06-18-installing-rancher-desktop-2.md
- Docker Compose: https://docs.docker.com/compose/
- FastAPI: https://fastapi.tiangolo.com/
- Alembic: https://alembic.sqlalchemy.org/
- PostgreSQL: https://www.postgresql.org/docs/
- Plotly.js: https://plotly.com/javascript/
- React Flow: https://reactflow.dev/
- Optional PM4Py: https://github.com/process-intelligence-solutions/pm4py

## 15. Copy-ready prompts

### Initial build prompt

```text
The project currently contains only docs/PRD.md. Read it completely and implement IdeaFlow end to end as specified. Treat it as the implementation contract.

Create the React/TypeScript frontend, FastAPI backend, PostgreSQL schema/migrations, transactional event log, workflow, monthly value tracking, process analytics, tests, demo importer, scripts, and documentation. Keep the deployment at three long-running services. Use containers for build/development tools; do not require host Python or Node.

Inspect my available Rancher Desktop engine/context, use its Docker/Moby runtime through Docker Compose, and deploy locally. Discover the actual context name instead of assuming it. Preserve other projects, existing configuration, and volumes. If a runtime prerequisite is blocked, finish everything that can be built and give me the exact remaining prerequisite; never claim deployment without verification.

Start with a usable empty application. Do not load fictional showcase data automatically. Implement the explicit additive/idempotent demo import command and JSON format from the PRD so I can populate it later.

Work through the full implementation, meaningful tests, browser/layout review, restart/rebuild persistence, and isolated backup/restore verification. Fix failures. Do not stop at a plan or scaffold. Use routine implementation judgment rather than asking me to choose libraries. Do not expand the stack or run destructive resets.

At completion, report the exact local URL, login instructions, demo-load command, checks actually passed, and limitations. Record the evidence in docs/VERIFICATION.md and provide the eight-minute non-technical showcase guide in docs/DEMO_GUIDE.md.
```

### First showcase injection prompt

```text
Read docs/PRD.md, README.md, and the demo-import documentation in this project. Populate the running local IdeaFlow app with its HarborWorks Manufacturing showcase dataset, using the implemented backend importer, not ad hoc direct SQL.

Use batch key harborworks-demo-v1, seed 42, and today's date in the app timezone as the anchor. First run a dry-run/validation preview; if valid, commit this explicitly authorized additive import. Include 60 fictional ideas across Tampa, Atlanta, and Dallas, covering the last 18 months, with the stage/disposition mix, five hero ideas, delayed Analysis work, holds, rework, completed initiatives, approved monthly financial schedules, implementation tasks, actual results, and finance verification specified in the PRD.

Preserve every existing user-created idea and all history. Rerunning the same batch must be a no-op. Do not reset/recreate the database, delete volumes, overwrite live records, generate future actuals, or create unsupported workflow histories. Clearly label the dataset as fictional and retain import provenance.

Verify current states reconcile with event replay, the counts and dashboard totals are coherent, missing actuals are shown as unknown, and process paths reveal the intended bottleneck. Check a second invocation produces no duplicates. Open or verify the deployed screens if tooling allows.

Update docs/DEMO_GUIDE.md with an eight-minute presentation using actual imported idea references: overview, create a new idea live, assign/work it, inspect a bottleneck and rework path, compare expected and actual gains/ROI, and finance-verify one unverified elapsed month. Point out which steps require Manager/Finance roles. Finish with the local URL, imported counts, and the five best ideas to open. Never expose passwords in committed docs.
```

### Add a second batch of new ideas

```text
Add a new, separate fictional showcase batch to the existing local IdeaFlow application. Follow docs/PRD.md and the JSON import contract. Use batch key harborworks-demo-v2 and seed 84; preserve harborworks-demo-v1 and all user-created records.

Create 12 credible new ideas: three Procurement, three Freight, two Energy, two Scrap/Quality, and two Productivity. Distribute them across Tampa, Atlanta, and Dallas. Keep six New ideas ready to work live, three Screening, two Analysis, and one Implementation idea about reducing emergency freight. For that Implementation idea, create a valid historical lifecycle, approved monthly ramp-up/spend plan, tasks, and two elapsed months of actual results below plan, leaving the latest period unverified. Other ideas have estimates but are not falsely shown as approved or achieved savings.

Write the proposed records to demo/harborworks-demo-v2.json in the existing supported format; validate with a dry run, then import this explicitly authorized batch through the backend importer. Use fictional owners, realistic descriptions and costs, timestamps no later than now, and unique external keys. Repeating this prompt/import must not duplicate records. Do not delete, reset, or overwrite anything.

Confirm that the idea register, Pipeline, Process, and Value views reflect the new records. Give me their actual idea references and a short live-demo sequence for taking one of the six New ideas through Screening and Analysis. Keep the existing application architecture unchanged.
```
