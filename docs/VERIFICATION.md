# Verified local delivery — IdeaFlow 1.0.0

Verification date: **2026-10-07**, America/New_York. The original build below was delivered empty. A later explicitly authorized HarborWorks live import is documented in the final section and [SHOWCASE_IMPORT.md](SHOWCASE_IMPORT.md); the application is now populated. Commands ran from the user's Windows project directory (including its spaces) against the laptop's Rancher Desktop engine. No host Python, Node or PostgreSQL was used. Passwords and session secrets are omitted from this evidence.

## Local deployment evidence

`docker version`, `docker compose version`, `docker context ls`, `rdctl list-settings`, and `docker --context default info` were inspected. Detected context: **default**. Server: Docker/Moby 29.5.3, client 29.6.2-rd, Compose v5.3.1. Engine OS reports **Rancher Desktop WSL Distribution**. Rancher settings showed `containerEngine.name = moby`, Kubernetes disabled. No engine/Kubernetes/system configuration was changed. Existing containers and volumes from other projects were inventoried and left untouched. Port 8080 had no listener before first binding.

Verified business URL: **http://localhost:8080**. Only frontend publishes `127.0.0.1:8080:80`; backend and PostgreSQL have no host port. Compose production project is `ideaflow`; services are `frontend`, `backend`, `postgres`. Named live volume: `ideaflow_pgdata`. App version 1.0.0, Alembic revision 0001.

Executed first-run and operating commands:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 init-env
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 up
docker --context default compose exec -T backend pytest -q
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-test.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 backup
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 restore-test
```

`up` verified the same-origin `/api/health/ready` response before printing the URL. Login succeeded with the generated Admin account. The committed source contains no real password; private instructions are in `local/first-login.txt`. Direct script invocation was initially blocked by Windows execution policy; the process-only Bypass invocation worked without changing the system policy.

First startup created schema, references and exactly one Admin. SQL count evidence: **0 ideas, 0 demo batches, 1 user**. The empty browser test revisited Overview, Ideas, Pipeline, Process, Value, My Work and Settings and refreshed nested routes; it passed without business writes. Later live reconciliation still reported zero ideas, zero events, zero variants and unknown financial totals. Demo data was never committed to the live application.

## Acceptance checks actually passed

| Area | Result and evidence |
| --- | --- |
| Container builds | React/TypeScript typecheck and Vite production build passed; FastAPI image built from fully pinned Python dependencies. Local Plotly/Dagre/font assets are bundled. No runtime external calls. |
| Backend tests | **12 passed** in a unique isolated PostgreSQL test database. Each test invocation creates only its own database and drops it on completion. |
| Workflow | API create → Screening → Analysis → approved snapshot/Approved → Implementation → Validation → Finance-verified Realized. Rework/correction paths, task completion and result persistence passed. |
| Roles | Direct API attempts deny Contributor approval/verification and Manager realized correction. Finance lifecycle actions follow matrix. Contributor owner moves, hold/resume and assigned task status pass. |
| Atomicity/concurrency | Invalid transition leaves state/event count/version unchanged; forbidden audit fields rejected; stale edit returns 409; two simultaneous edits yield one 200 and one 409 with unique contiguous case event sequences and no lost event. |
| Audit/auth | Application role UPDATE, DELETE and TRUNCATE on events fail. CSRF-less mutations and cross-origin requests fail. User responses omit password hashes. Approved snapshot and schedule mutation fail in PostgreSQL. |
| Finance | PRD example: annual potential 108,000; first-year plan 99,000; cash flow 69,000; ROI 230%; May month-end payback; probability-adjusted benefit 69,300. Zero/unknown costs, sustained payback crossing and ramp rounding pass. |
| Cohorts/snapshots | Two-idea fixture: 4 eligible months, 1 reported, 1 verified. Matched expected cohort 900 versus actual 700 and verified 650. Full planned 5,400; portfolio ROI 170%; risk-adjusted 3,780. New draft leaves forecast unchanged; invalidation removes current forecast and retains historical verified value. |
| Process | Known fixture with tied timestamps, explicit hold/resume, backward re-entry, rejected case and ongoing visit passes edge counts/distinct cases, variants, calendar/active durations and right-censoring. Comments excluded. |
| Additive import | Dry-run rollback, same-key no-op, separate JSON batch addition, chronological replay/current-state reconciliation and provenance pass. No future occurrence/actual accepted. |
| Browser | Containerized Playwright Chromium: empty suite **1 passed, 2 intentionally skipped**; populated isolated suite **2 passed, 1 intentionally skipped**. Create/edit/transition/comments/tasks, nested reload, filters/drilldown, Finance verification and retained stale-form input tested. No browser page errors in these flows. |
| Layout | Overview, register, detail Financials, Pipeline, Process and Value captured at **1440×900**, **1280×720**, and **390×844**. Assertions found no page-wide overflow. Screenshots visually reviewed; table/board scrolling is intentional. Charts have supporting tables and graph has an edge table. The graph uses Dagre-provided routes and label space on a horizontally scrollable canvas; both ends of the graph were captured and reviewed. × labels mean total traversals; d labels mean median elapsed days. |
| Persistence | Unique probe **IF-00364**, gross result **1,234.56**, two audit events and version preserved after down/up and image rebuild. All nine business-table count/SHA-256 fingerprints unchanged. |
| Backup/restore | Live empty custom dump restored into a unique temporary DB and matched; populated verification custom dump matched all business tables. Live/source DB unchanged; only temporary restore databases removed. |
| Scripts | PowerShell init-env/up/tests/backup/restore-test and browser scripts exercised from path containing spaces. Bash script passed `bash -n` in a Node container; bash operating actions were not exercised on Windows. |
| Dependencies | Frontend npm audit reported **0 vulnerabilities** after patched versions pinned. Full backend/frontend license inventories generated from containers/lockfile. |

The additional dashboard test verifies exact decimal Pipeline totals, annual-value sorting with server pagination, and count-to-register cohort reconciliation. Overview exposes its selected month horizon and drilldown IDs; Pipeline money totals come from PostgreSQL/Decimal rather than browser floating-point sums.

One third-party Starlette/AnyIO deprecation warning remains in backend TestClient; the tests pass. No uncaught application failure remains in the exercised tests.

## Isolated populated verification evidence

The separate project **ideaflow-verification**, port 8081 and volume **ideaflow_verification_pgdata** were used for all fictional writes and browser mutations. This project is stopped at handover; its volume and private evidence remain preserved. It is not the user's live showcase. The final generator was added as a distinct verification batch to preserve earlier test records rather than resetting them.

Commands executed:

```powershell
docker --context default compose -f compose.yaml -f compose.verify.yaml -p ideaflow-verification up -d --wait
docker --context default compose -f compose.yaml -f compose.verify.yaml -p ideaflow-verification exec -T backend python -m app.demo --dry-run
docker --context default compose -f compose.yaml -f compose.verify.yaml -p ideaflow-verification exec -T backend python -m app.demo
docker --context default compose -f compose.yaml -f compose.verify.yaml -p ideaflow-verification exec -T backend python -m app.demo
docker --context default compose -f compose.yaml -f compose.verify.yaml -p ideaflow-verification exec -T backend python -m app.demo --file /demo/example.json
docker --context default compose -f compose.yaml -f compose.verify.yaml -p ideaflow-verification exec -T backend python -m app.demo --batch-key verification-corrected-v1 --dry-run
docker --context default compose -f compose.yaml -f compose.verify.yaml -p ideaflow-verification exec -T backend python -m app.demo --batch-key verification-corrected-v1
docker --context default compose -f compose.yaml -f compose.verify.yaml -p ideaflow-verification exec -T backend python -m app.demo --batch-key verification-corrected-v1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-test.ps1 -Verification
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify-persistence.ps1
```

Final corrected 60-record batch: **747 events, 25 tasks, 87 value periods**; all seven stages, **12 Realized, 5 held, 6 rejected, 3 cancelled, 8 rework cases**, and at least 6 overdue active initiatives. Batch repeated with no change. Analysis completed residence median **222.5 days**, compared with Approved 7 days, Implementation 61 days, Validation 61 days, Screening 10 days and New 7 days. Sample sizes and open ages are separate in the UI.

Corrected verification hero references were IF-00304 through IF-00308 in table order from the PRD; these references are **verification-only**, and live import receives its own references. The live demo guide uses titles and the actual import manifest to avoid claiming nonexistent live references.

Reconciliation before the final probe: 123 ideas, 1,470 events across preserved verification batches/live browser checks; 258 eligible idea-months, 149 reported, 110 verified. These numbers include the earlier generator and later corrected batch, so they are not advertised as a single 60-record live dataset. Batch-by-batch replay passed.

Populated backup snapshot counts: **124 ideas, 1,472 events, 186 financial plans, 1,116 plan periods, 151 value periods, 51 tasks, 122 comments, 3 batches, 6 users**. Custom-format backup is `backups/verification.dump`. Restore compared full sorted row SHA-256 fingerprints, not counts alone. Both restart and rebuild probes reported PASS and identical fingerprints. Later browser test writes are beyond this backup snapshot and remain only in the verification project.

## Failures found and fixed

Initial TypeScript JSX syntax failed for a literal `>` label; corrected and rebuilt. Router/Vite/Playwright advisories were resolved with patched pins (npm audit zero). Registry lacked the newer requested Playwright image; matching 1.55.1 package/image was available and verified.

Rollup tree-shaking caused excessive build CPU/memory on the selected dependency combination. Static prebuilt Plotly/Dagre assets and disabled tree-shaking/minification produced reliable builds in seconds; nginx gzip serves the larger app bundle. TypeScript remains checked. This has a bundle-size tradeoff, documented below.

Two browser installs initially collided in a shared host node_modules directory; test dependencies now install into each transient container's private filesystem. Large trace artifacts also slowed OneDrive output; traces are disabled and screenshots remain local evidence. Native select accessible labeling failed; explicit aria-labels fixed it and both populated tests passed. Structured JSON history metadata was corrected before final review.

Verification handover bind directory initially had root-only mode; changing only that task-owned directory allowed the nonroot importer to write credentials. Failed import rolled back business rows. Live handover directory was already writable. The demo chronology initially overstated Approved residence and omitted initial actual spend; generator corrected and tested, without overwriting imported records or rewriting future events into the past.

## Limits and unverified alternatives

- Financial dashboards support current approved snapshot forecasts and current reporting as-of. **Historical financial as-of reconstruction is unavailable** and is explicitly rejected rather than returning misleading totals. Process supports historical as-of through its API.
- Chromium was exercised; Firefox/WebKit and a formal accessibility audit were not. Explicit labels, visible focus, responsive controls and chart tables were reviewed/tested, but this is not an accessibility certification.
- Plotly and the graph are bundled locally. Tree-shaking/minification are disabled to avoid the observed bundler behavior; app JS is about 1.53 MB before gzip (about 307 KB gzip), plus the local Plotly distribution. This local application favors reproducible builds over bundle optimization.
- PowerShell operations are the verified path. Bash script syntax passes; its full operating sequence is provided as an untested alternative.
- Package advisory checks covered npm. A full base-image vulnerability scan, independent security review, login rate-limit hardening and enterprise authentication are outside this local delivery. Sessions are local app authentication, with CSRF protection and Argon2.
- This implementation has one initial migration. Schema changes should add migrations; destructive downgrade/reset is unsupported. Reference lists can be added, but this V1 does not offer a reference-list deletion or workflow designer.
- Backup tests restore into isolated databases on the local PostgreSQL service. Restoring over live data or recovery on another machine was not performed.

Official documentation HTTP checks returned 200 for Rancher Desktop engine settings, Docker Compose, FastAPI, Alembic tutorial, PostgreSQL 17 backup dump, React Flow layout and Plotly JavaScript docs. Installed-runtime facts came from CLI/server evidence rather than assumed context names.

Repeated Finance browser runs originally exhausted the selected hero's unverified results. The test now preserves previous sign-offs and adds a fresh elapsed fixture period when required. Final screenshot capture waits for loading to finish; the monthly throughput axis is explicitly categorical with a supporting table. Dagre routing fixes the previous overlapping edge labels. An additional money serialization assertion initially failed and was corrected to return exact decimal strings.

## Final handover checks

Final backend execution: **12 passed in 16.76 seconds**, with one third-party deprecation warning. Final Chromium execution: empty live suite **1 passed in 5.0 seconds** (two populated-only skips), populated isolated suite **2 passed in 37.4 seconds** (one empty-only skip). Final frontend build passed TypeScript and production bundling. Screenshot review includes loaded Overview and both scroll positions of the readable observed graph at 1440/1280; the canvas scroll is intentional.

Final live reconciliation: **0 ideas, 0 events, 0 demo batches, 1 Admin**. All financial totals remain unknown and process variants zero. Latest empty live backup **backups/ideaflow-20261007-191154.dump** restored successfully into an isolated temporary database, with identical business-table fingerprints and source unchanged. The restore database was removed by the verified script.

The isolated verification project was stopped with ordinary Compose down, preserving **ideaflow_verification_pgdata**. Live **ideaflow_pgdata** is preserved. Only the three production IdeaFlow services remain running. No fictional batch was committed to the live app.

Final offline correction: Swagger UI 5.30.2 is pinned and bundled locally. API documentation uses same-origin JS/CSS/favicon rather than CDN assets. The dependency inventory was regenerated and npm audit again reported zero advisories.

Final HTTP checks: business URL 200; readiness/live version **1.0.0**; OpenAPI JSON has **30 API paths**; migration revision **0001**; API docs and local Swagger bundle both 200. Swagger's external validator is disabled. The empty browser check also opens API docs while blocking external origins. Final Compose inspection shows frontend/backend/postgres healthy, only loopback frontend port 8080 published, no running verification containers, and no lingering test/restore databases. Generated login/config files exist and remain private.

## Subsequent authorized live showcase import — 2026-10-07

The user explicitly authorized populating the live app after empty delivery. Read PRD/README/import contract, verified Rancher Desktop default Moby context and healthy services, and obtained today's app-zone date **2026-10-07 / America/New_York** from the running backend. Used implemented importer **harborworks-demo-v1, seed 42**: dry-run validation, committed additive import, then repeated committed invocation. No existing ideas were present; bootstrap Admin's full row fingerprint stayed identical. Dry-run left all business tables unchanged. Repeat returned no_op and left all nine count/SHA-256 fingerprints unchanged.

Live imported totals: **60 ideas, 747 events, 25 tasks, 60 comments, 91 financial versions, 31 approved snapshots, 558 plan periods, 87 actual periods, 61 verified periods**; three fictional role accounts added. Stage counts **5 New, 11 Screening, 13 Analysis, 6 Approved, 8 Implementation, 5 Validation, 12 Realized**. Dispositions **46 Active, 5 On hold, 6 Rejected, 3 Cancelled**. Sites **21 Tampa, 19 Atlanta, 20 Dallas**. **13 overdue active**, **8 rework cases**, **14 variants**. Chronology, contiguous event sequences, valid workflow, provenance, all current states against full lifecycle replay and independent Decimal value/cohort/ROI sums passed. Analysis completed median **222.5 days**, p90 **266**, sample **42**; open visits censored. Missing results/unverified amounts remain null/Unknown. Hero refs are **IF-00121–IF-00125**.

Read-only live browser command `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-showcase.ps1`: **1 passed in 29.7 seconds**. Tested all six requested business screens at 1440×900, 1280×720 and 390×844; no page-wide overflow or page errors, external origins blocked. Tested retained site filter, process drilldown, five hero details/history badges, unsaved create form, Manager actions and a Finance review preview. Closed the Finance dialog without saving; both August and September on IF-00124 remain ready for the presenter. Post-browser business fingerprints identical. Process and Finance screenshots visually reviewed; scrollable graph retains readable labels.

Read-only independent check: `docker --context default compose cp scripts/verify-showcase.py backend:/tmp/verify-showcase.py`, then `docker --context default compose exec -T -e PYTHONPATH=/app backend python /tmp/verify-showcase.py`. Initial invocation without PYTHONPATH failed to locate app, then the corrected container command passed. No business writes occurred. The checker uses private import snapshots; after presenter writes, those snapshots should remain historical evidence rather than be treated as a new baseline.

January–December 2026 values: annual potential **$4,318,480**, approved net **$1,194,619.94**, reported net **$280,337.23**, verified net **$195,778.87**. Matched expectations **$276,460.02 reported / $193,506.64 verified**. Coverage **87/129 reported, 61 verified**. Portfolio planned ROI **61.7%**, October month-end payback. Full details and executed commands: [SHOWCASE_IMPORT.md](SHOWCASE_IMPORT.md). Eight-minute guide rewritten around actual references and ready Finance month: [DEMO_GUIDE.md](DEMO_GUIDE.md). Generated passwords remain only in private gitignored local files.
Post-import backup **backups/ideaflow-20261007-192449.dump** was produced using the binary-safe PowerShell backup command and restored with powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 restore-test -File backups/ideaflow-20261007-192449.dump. All nine business-table row fingerprints matched; live/source unchanged; temporary restore database removed. Final app health reports ready/version 1.0.0, only three healthy production services, frontend loopback 8080, and the post-import baseline still matches all business rows.

## Separate authorized v2 import — 2026-10-07

Created JSON **demo/harborworks-demo-v2.json**, batch **harborworks-demo-v2**, seed **84**, fixed anchor **2026-10-07** in the app's America/New_York timezone. Used existing domain importer with **seed-demo -File demo/harborworks-demo-v2.json -DryRun**, then committed with the same command without -DryRun, then repeated the committed command. No image rebuild, configuration change or stack expansion. Original 60 ideas/747 events and all business/user/reference rows were captured as per-primary-key SHA-256 snapshots before import. All retained their original fingerprint after commit and browser review; all post-import fingerprints unchanged by repeated invocation (no_op true).

V2 adds **12 ideas, 64 events, 2 tasks, 12 comments, 13 financial versions, 18 plan periods, 2 actual periods and 1 verified period**. Exact mix **6 New / 3 Screening / 2 Analysis / 1 Implementation**, **3 Procurement / 3 Freight / 2 Energy / 2 Scrap/Quality / 2 Productivity**, **4 each Tampa/Atlanta/Dallas**. Three new fictional Contributor accounts; existing Manager/Finance accounts reused without modification. All records/events labeled fictional with batch provenance. No future historical occurrence/actual. Six New records remain ready for the presenter; other early cases have estimates with no approved/achieved value.

Actual refs **IF-00193–IF-00204**. Emergency-freight **IF-00204** has valid historical lifecycle, immutable approved 18-month ramp, $12,000 spend allocated August/September, two tasks and 65% progress. August actual net **$3,700** against **$5,500** plan, verified; September **$6,450** against **$8,250**, unverified. V2 January–December approved net **$46,750**, reported **$10,150**, verified **$3,700**, coverage **2/2 reported, 1 verified**. Combined **72 ideas/811 events**, approved **$1,241,369.94**, actual **$290,487.23**, verified **$199,478.87**, coverage **89/131 reported, 62 verified**. Verified sums against preserved existing cohort plus new batch; Process includes 72 cases/consistent variants, register and stage counts reconcile, all new current states match lifecycle replay.

Read-only checker **scripts/verify-demo-v2.py** was copied into the backend and executed with **PYTHONPATH=/app** in snapshot/unchanged/verify/preserved modes. Snapshots contain row hashes, not raw credentials, and remain private under local/. These are historical evidence and intentionally fail if presenter writes change the captured baseline.

Containerized live v2 browser script **scripts/browser-demo-v2.ps1**: **1 passed in 8.1 seconds**. Register, Pipeline, Process and Value show the v2 cohort at **1440×900 / 1280×720**, including 12 cards, six New, 12 process cases, 11 unapproved rows and actual/verified coverage. No page errors/page-wide overflow. Screening action and Finance dialog preview enabled; dialogs closed without business mutation. Screenshots visually reviewed. All post-import business/user/reference fingerprints stayed identical after browser review. [DEMO_V2_GUIDE.md](DEMO_V2_GUIDE.md) contains actual links, monetary examples and the short IF-00193 New → Screening → Analysis presentation.

Final readiness **ready / 1.0.0**; exactly three healthy production services remain, only frontend loopback port 8080 published. Binary-safe backup **backups/ideaflow-20261007-193136.dump** created after v2. Generated new-role passwords remain only in private gitignored **local/harborworks-demo-v2-credentials.json**.

Post-v2 isolated restore command **powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 restore-test -File backups/ideaflow-20261007-193136.dump** completed with **restore PASS** and identical full sorted row fingerprints for all nine business tables. Live/source records were unchanged; the temporary restore database was removed. Final database-list check found only **ideaflow, postgres, template0 and template1**, with no temporary test/restore databases.

The existing v1 live browser suite was updated to derive full-register and Tampa counts from the API so additional batches do not invalidate its fixed 60-record assumptions. **scripts/browser-showcase.ps1: 1 passed in 29.2 seconds**, reviewing Overview, register, Pipeline, Process, Value, hero Financials and role previews at **1440×900, 1280×720 and 390×844**. No business actions were saved. The final post-browser check against **local/harborworks-v2-after.json** reports **All row fingerprints unchanged: PASS**. Readiness was checked again and reports **ready / 1.0.0**; Compose lists exactly three healthy live services.
