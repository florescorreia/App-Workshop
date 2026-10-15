# VAVE 1.2 differential completion — 2026-10-15

**Implemented, deployed and publicly verified:** https://vps-8104e6c8.vps.ovh.us:8443/vave. Scope follows the complete supplied DOCX, its first-release priorities and the later user authorization to adapt existing test records and the look/feel. Requirement-by-requirement evidence and subsequent-release limits are in [VAVE_REQUIREMENT_AUDIT.md](VAVE_REQUIREMENT_AUDIT.md). DOCX SHA-256: `e01709fc79aaa936cb13a13eb49581ed58f28e91c51e0a2e2ae3781f9b421f12`.

## Local checks actually run

- Root/app contracts, complete PRD and amendments, DOCX, README, hosting/redeployment and shared VPS security/foundation guidance were read. Git state, current source and production 1.1.0/schema 0006 were inspected before this update.
- Containerized backend and TypeScript/Vite frontend builds passed with explicit Rancher Desktop Moby context `default`. Existing locked frontend dependencies previously reported zero npm audit vulnerabilities; no dependency changes were added for this enhancement.
- Final backend suite: **39 passed**, **39.76 seconds**, one existing Starlette TestClient deprecation warning. Tests cover A1–A9, gates, independent review, overlap/partial rollout, financial calculations, corrected actuals, imports/exports, role boundaries, structured filters, unknown/scoped reports, notices/preferences/work and legacy adoption/concurrency. The added verification regression initially omitted required cash spend; its request was corrected, the container rebuilt and the complete suite rerun successfully.
- Local mutating browser journey: **1 passed, 1 intentionally skipped** (21.9 seconds), against the isolated verification database. It covered capture, blocked M1, owner/action/date, economics, screening, reload, attachment/discussion and 1440/1280/390 layouts. No production business mutation was performed by this test.
- Restored a verified production dump into the **fresh isolated** pilot volume `ideaflow_vave_pilot_pgdata` on port 18884. Preview/application of both authorized adaptations passed. All 5 account rows/password hashes, original financial/task/comment/reference rows, idea identities/lifecycle fields and all 27 original events matched. Seven VAVE events were appended; no approval or actual was copied. Pilot browser checks: **2 passed, 1 intentionally skipped** (21.0 seconds). Caddy-specific HTTPS assertions were reserved for the real public endpoint.
- Verification backup `backups/vave-verification-20261015T173311Z.dump`, SHA-256 `762cdcd03e6b50307798fb583d656312f2d99efe0f76d5ff87e4bc3b01be73b2`, was restored into a unique temporary database. All 20 public tables and the reference sequence compared exactly. Ordinary down/up with container rebuild preserved the same rows. Existing volumes and other apps were retained.
- Python AST, VAVE PowerShell parser and Git whitespace checks passed. Stored Windows User credential values were absent from all **154 IdeaFlow deliverables** checked; private env/proposals/backups/evidence/releases are Git-ignored. Values were withheld.

Private local evidence: `artifacts/vave-1.2-local-verification.json`, pilot adoption fingerprint files, screenshots, reviewed proposals and immutable release assets.

## Production update, adaptation and final checks

Final release: **1.2.0**, existing schema **0006**, immutable directory `local/releases/vave-20261015T173846Z/`.

| Asset | Verified identifier |
| --- | --- |
| Backend content ID | `9cb301d060e450f8a10df078d56fd13bfd59f63ac8723858cc40fa7eca3048c9` |
| Frontend content ID | `eeeb57ddd9811988b1345c70a8a603403f58f158bebdf41b9982085b354993c1` |
| Image archive SHA-256 | `49e2ea65a29e419f8d1e353fd4381e2e7aa201609ddf070dcc9494b559d0a60a` |
| Fresh production dump | `backups/vps-vave-20261015T173953Z.dump` |
| Production dump SHA-256 | `f5a5f9e77944ee42b0bf0238653e16d6bafae311d966b43ed0c8281a3b900b48` |
| Current rollback assets | `/home/ideaflow/backups/vave-update-20261015T173953Z/` |
| Conversion preservation evidence | `/home/ideaflow/backups/vave-adaptation-20261015T174146Z/` |

The updater checksummed the transfer, retained previous images/Quadlets, paused only IdeaFlow, took a fresh coherent dump, restored it into a unique temporary database, compared all 20 tables and the reference sequence, downloaded and verified the dump, then replaced only backend/frontend image pins. Existing 1.1 and pre-VAVE rollback assets remain. Maintenance pause: **27.2 seconds**. No production database reset, snapshot replacement, credential change, volume deletion or demo import occurred.

Before conversion, production preserved 5 accounts, 6 account events, 2 ideas, 27 idea events, 6 financial plan versions, 24 plan periods, 1 result, 1 task, 1 comment, 1 category and 1 location. No VAVE data was created by deployment. Public readiness confirmed 1.2.0; unchanged Admin login and original shared-workspace endpoints passed.

The reviewed private proposal `local/vave-adaptation/production-20261015.json` was applied separately through version-checked authenticated commands after deployment/backup verification:

| Retained reference | New evaluation concept | VAVE state |
| --- | --- | --- |
| IF-00205 | Simplify the actuator mounting bracket | Active / M2; critical fatigue risk and missing functional acceptance prevent M3 |
| IF-00206 | Introduce returnable packaging for actuator deliveries | Draft / M0; unknown economics and unassigned idea owner |

Program: “Product cost excellence — VAVE evaluation”, ID `fc64d73c-df60-46f3-9e52-c84614db3982`, EUR, 2026. The bracket's two plant applications total €100,000 annual gross/€90,000 annual net run rate; eligible in-year net opportunity is €36,000, separate €20,000 spend and €16,000 net cash. Packaging opportunity is Unknown. Target €50,000 is illustrative, with €40,000/€10,000 child allocations. Approved forecast, implemented and verified benefits remain **zero**. No real savings or sponsor acceptance is asserted.

Post-conversion and post-public-check fingerprints retained all account/password, original financial/task/comment/reference rows, original lifecycle fields, source IDs/sequence and all 27 earlier events. Current idea events: **34**; VAVE programs/cases: **1/2**; demo batches: **0**. Prior snapshots and financial evidence are readable under History and excluded from VAVE totals. Ordinary sessions and new VAVE rows/events are the only permitted additional records.

Public Chromium: **2 passed, 1 intentionally skipped**, **23.4 seconds**. Checks cover trusted HTTPS, CSP, secure/HttpOnly/Strict session cookie, blocked docs/private paths, VAVE landing, setup cancellation, both renamed references/IDs, retained evidence, exact EUR opportunity/unknown/target/zero approved and verified totals, structured search, report drill-down, desktop/mobile widths, unchanged case details and logout/401. No page errors, API 5xx or CSP violations occurred. Public 8443 is reachable; 18081, 8000, 5432, 9090 and 2019 are inaccessible.

Final inspection matched both running image IDs, unchanged `ideaflow-pgdata`, exactly three healthy services under the rootless `ideaflow` account, active app target/backup timer, unchanged server credential-file checksums, and no failed host/user units. Caddy, UFW, Fail2ban and auditd were active. Both VAVE cases replay to their immutable maturity/status decisions. Private final evidence: `artifacts/vave-1.2-final-verification.json`, the current release's `deployment.json`, reviewed adaptation/applied/preservation files and server `final-public.json`.

Commands actually run from `apps/ideaflow/` include:

```powershell
docker --context default compose build backend frontend
docker --context default compose -p ideaflow-verification -f compose.yaml -f compose.verify.yaml -f artifacts/vave-compose.yaml up -d --wait
docker --context default compose -p ideaflow-verification -f compose.yaml -f compose.verify.yaml -f artifacts/vave-compose.yaml exec -T backend pytest -q
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-vave.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-vave.ps1 -Pilot
powershell -NoProfile -ExecutionPolicy Bypass -File artifacts/vave-local-check.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/prepare-vave.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/vps.ps1 vave-update -File local/releases/vave-20261015T173846Z
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/vps.ps1 app-check
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/vps.ps1 vave-adapt-apply -File local/vave-adaptation/production-20261015.json
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-vave.ps1 -Public
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/vps.ps1 ports-check
powershell -NoProfile -ExecutionPolicy Bypass -File artifacts/vave-final-check.ps1
```

Both isolated IdeaFlow test stacks were stopped with ordinary Compose down after checks. Volumes ideaflow_pgdata, ideaflow_verification_pgdata and ideaflow_vave_pilot_pgdata remain. Governed-dd containers remain running. Final Git scope/whitespace and stored-credential scans passed; all 45 changed paths are confined to IdeaFlow.

Limits: no intentional production failure/rollback or new VPS reboot was performed. The existing reboot evidence remains historical. This release does not claim official Roland Berger brand certification, licensed corporate fonts, actual pilot sponsor acceptance, real savings, full FR15 replication or richer optimization/integrations. See the requirement audit and design reference. Source changes remain uncommitted in the existing repository.

---

> Document status: dated reference evidence. Counts, imported links, runtime state and old role names describe the recorded run; they are not a current workspace inventory. Current User/Admin behavior and command locations are in [README.md](README.md). Local scripts run from `apps/ideaflow/` after deliberate staging. No fictional import is part of startup, documentation review or deployment.

# Previous 1.1 VAVE differential delivery — 2026-10-15

Implemented the supplied [VAVE Tracking PRD](VAVE_Tracking_PRD.docx) in the existing application. The accepted scope and requirement mapping are in [VAVE_DELTA.md](VAVE_DELTA.md). Version **1.1.0**, additive Alembic revision **0006**, runs at **https://vps-8104e6c8.vps.ovh.us:8443**; program entry is **/vave**. The dated 1.0.0 evidence below is historical.

## Local implementation checks

All builds/tests used containers and explicit Rancher Desktop Moby context **default**, with engine identity checked. No host Python/Node, new application scaffold or additional runtime service was introduced. Existing governed-dd containers remained running on 8081. The isolated IdeaFlow verification project used 18883 and `ideaflow_verification_pgdata`; existing historical test records were preserved rather than importing a fresh demo batch.

| Check actually run | Result |
| --- | --- |
| Backend build and complete `pytest -q` | **35 passed** in 67.47 seconds on the final backend; one existing Starlette/AnyIO deprecation warning. Tests use a unique database and preserve the staged application database. |
| Frontend container build | TypeScript and Vite production build passed; pinned dependencies and existing build settings retained. |
| VAVE API journey | M0–M6, missing prerequisites, explicit reviews, independent Finance/actual verification, partial rollout, reapproval and retained snapshots passed. |
| Economics | $10→$9, 100,000 annual units: $100,000 gross/$90,000 net run rate; 40,000 eligible units: $36,000 net recurring; $20,000 spend: $16,000 net cash. Unknown/negative value and overlap/alternative exclusions passed. |
| Access and audit | External program/shared-record boundaries, restricted intake, file checksum/download, controlled import preview/confirmation/idempotency, stale edits, legacy endpoint bypass rejection and append-only program audit passed. |
| Gate correction | Attempts to advance M1 using Return/Reopen target 6 return 422 with unchanged maturity, status, version, history, reviews and data. Valid same-maturity reopening and backward rework still pass. |
| Local browser | VAVE capture/submission, missing prerequisites, M1 screening, application economics, nested reload, attachment/discussion and six workspace tabs: **1 passed, 1 intentionally skipped**. Desktop 1440/1280 and mobile 390 layouts captured/reviewed. Full M2–M6 evidence is from API tests, not a complete browser walkthrough. |
| Backup/rebuild persistence | `artifacts/vave-local-check.ps1`: all **20 tables and reference sequence** matched isolated restore and ordinary down/up/rebuild. Private dump: `backups/vave-verification-20261015T132320Z.dump`. Snapshot included 214 preserved verification ideas, including three VAVE browser fixtures; this was never transferred to production. |
| Replay and scripts | Original lifecycle and VAVE decision replay passed; final Python source/operator AST and VAVE PowerShell parsing passed. `git diff --check` passed. |

During the final backend rebuild, a command initially omitted `compose.verify.yaml` and briefly attached the test stack to the local primary volume. The additive migration ran there; an isolated test run was interrupted when the mount was corrected. The complete rerun above passed. A separate audit restored the latest local primary backup (`backups/ideaflow-20261011-120801.dump`) into a temporary database and compared it to the primary volume: **every existing table, including accounts/password hashes, sessions and history, and the reference sequence matched exactly**; the only additions were six empty VAVE tables and schema metadata. No snapshot was restored over the primary database. The temporary audit stack was removed with ordinary `down`, preserving the volume. Production was unaffected by this local staging mistake.

## Deployment and production preservation

The initial VAVE release and the gate-corrected release each received a fresh production dump, isolated restore comparison, checksum-verified off-host download and retained old images/Quadlets. No initial-copy installer, reset, demo import, credential regeneration or database snapshot replacement was used. The dedicated rootless account/UID, Podman network, `ideaflow-pgdata` volume, resource limits, Quadlets, daily backup timer and host Caddy route remained in place.

Final immutable release: `local/releases/vave-20261015T164349Z/` (private). Actual deployment record: `deployment.json` in that folder.

- Backend content ID: `81492b71e344e8ebb7bc0ebd952784226256b344d99448c8c050faff2f503b49`.
- Frontend content ID: `8e50e9ff9a0d6b7c0466adb85b946bbeea6d6b8da6a27f82d0822d364ef11c58`.
- Image archive SHA-256: `83b85573aa2c28368490036a54d1dc3e503d27ef86ac932a57eac596d947f9dc`.
- Fresh final backup: `backups/vps-vave-20261015T164437Z.dump`, SHA-256 `df509eec5484d5f83b9becb89911798d79b60e44311e09f03423a774f47f679d`.
- Final server backup/rollback assets: `/home/ideaflow/backups/vave-update-20261015T164437Z/`; pre-VAVE assets also retained under `vave-update-20261015T132654Z/`.
- Recorded maintenance pause: **26.1 seconds** for the corrected update; **27.1 seconds** for the initial additive release.

The final dump was restored into a unique temporary database and compared across all 20 public tables and the reference sequence. Live rows matched before and after backup and image replacement. Server `backend.env` and `postgres.env` checksums remained unchanged. Both final image IDs were verified against the running containers; all three containers were healthy. The application target and daily backup timer were active. Caddy, UFW, Fail2ban and auditd were active with no failed host/user units.

Production retained **5 accounts, 6 account events, 2 ideas, 27 idea events, 6 plans, 24 plan periods, 1 result, 1 task, 1 comment, 1 category and 1 location**. Reference sequence and all preexisting rows/password hashes matched. VAVE program/case/evidence/notice/preference/program-event tables remained empty, and demo batches remained zero. A post-public-check comparison again matched all **19 non-session tables** plus the sequence; ordinary login/logout activity was explicitly excluded from that last session comparison. Private evidence: `artifacts/vave-final-verification.json` and server `final-public.json`.

Commands actually executed from this app folder:

```powershell
docker --context default compose -p ideaflow-verification -f compose.yaml -f compose.verify.yaml -f artifacts/vave-compose.yaml build backend
docker --context default compose -p ideaflow-verification -f compose.yaml -f compose.verify.yaml -f artifacts/vave-compose.yaml up -d --wait --wait-timeout 180
docker --context default compose -p ideaflow-verification -f compose.yaml -f compose.verify.yaml -f artifacts/vave-compose.yaml exec -T backend pytest -q
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/prepare-vave.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/vps.ps1 vave-update -File local/releases/vave-20261015T164349Z
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/vps.ps1 app-check
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-vave.ps1 -Public
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/vps.ps1 ports-check
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/vps.ps1 sudo -Command 'cd /home/ideaflow; runuser -u ideaflow -- env XDG_RUNTIME_DIR=/run/user/1001 podman exec ideaflow-backend python -m app.reconciliation'
```

Public API checks passed trusted HTTPS readiness, existing Admin login/Secure session, both preserved ideas and all original dashboards. Event reconciliation reported **2 original ideas / 27 events / 0 VAVE cases**, with unchanged planned net 3,600 and recorded net 515. Public port checks found 8443 reachable and 18081/8000/5432/9090/2019 inaccessible. Credentials were read from Windows User environment variables and were never printed or committed.

Public containerized Chromium checks completed: **2 passed, 1 intentionally skipped in 23.0 seconds**. VAVE login/entry, program setup cancellation, walkthrough, loaded desktop/mobile screenshots and mobile navigation/logout passed without page errors. The existing workspace check verified IF-00205/IF-00206, original dashboards/financials/history, 1440/1280/390 layouts, CSP, secure cookie attributes, blocked documentation/dotfile paths and logout, without business mutations. The skipped test is the mutating VAVE journey, deliberately confined to local verification.

The initial public VAVE test attempted logout while the mobile menu was closed, checked session state before asynchronous logout completed, and took some screenshots before loading finished. The harness now opens the menu, waits for sign-in to appear, and waits for the VAVE heading/actions before screenshots. The completed rerun above passed; loaded public screenshots at `artifacts/vave-public-1440.png` and `vave-public-390.png` were visually reviewed.

The isolated verification stack was stopped using ordinary `down` with all three Compose files. Both `ideaflow_verification_pgdata` and the primary `ideaflow_pgdata` volumes remain. No local IdeaFlow containers remain running; its temporary verification URL was **http://localhost:18883**. Governed-dd's existing containers and loopback 8081 listener remained running. Final Git scope is confined to `apps/ideaflow`; stored credential-value scanning of changed text files passed, and private environments, dumps, release archives and artifacts are ignored. Source changes remain uncommitted.

## Scope limits

The production VAVE browser journey opens program setup and cancels it; mutations and gate completion were exercised only in isolated local databases. No production pilot/program or test business record was created. Independent-account API tests cover financial authorization; only the stored Admin credential was used for live login. Broader FR15 replication, richer scenario/resource optimization, assisted discovery and operational integrations remain subsequent-release scope from the differential PRD. No intentional production rollback or new host reboot was performed for this release; prior reboot evidence below is historical.

# Verified local delivery — IdeaFlow 1.0.0

**Current handover, 2026-10-09:** the user explicitly authorized clearing the local workspace and simplifying it. The live app is now empty with only the preserved bootstrap Admin, no locations/categories, and Alembic revision **0002**. Earlier populated showcase references and role requirements below are historical evidence. Current manual guide: [UX_WALKTHROUGH.md](UX_WALKTHROUGH.md).

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

## Shared workspace delivery — 2026-10-09

The accepted amendment is recorded at the top of PRD.md. User/Admin are the only current account roles. Users create/read/edit/assign/approve/work/review ideas; Admin additionally manages account access/passwords and imports. Workflow prerequisites, separate approval/review decisions, money formulas, transactions, immutable events/snapshots and three-service architecture remain. Review is explicit, not enforced independent finance certification.

Locations/categories are optional, typed or chosen from keyboard-accessible existing choices. New labels resolve using Unicode normalization, case and whitespace normalization in the same transaction as creation/edit. Shared Settings renames labels, sets optional business-unit grouping and merges source choices into an existing target. Each affected idea receives a version increment and event; current filters/aggregations refresh without changing lifecycle or financial records. The source of a merge is retired and redirects; old spellings before a rename are not retained as aliases. The local workspace serializes classification-sensitive mutations with a PostgreSQL advisory lock to avoid creation/merge races.

Verified Rancher Desktop engine/context again with docker context ls, rdctl list-settings and docker --context default info: **default**, **moby**, **Rancher Desktop WSL Distribution**. No engine, project configuration or volume settings changed. Containers were used for all Python/Node/build/browser tooling.

Before cleanup, binary-safe **backups/ideaflow-20261009-104528.dump** was created and restored into a unique temporary database. Full fingerprints matched all nine business tables: **72 ideas, 811 events, 104 plans, 576 plan periods, 89 results, 27 tasks, 72 comments, 2 batches, 8 accounts**. The temporary restore database was removed. This backup retains the previous live state, including an extra account that existed at this turn; its passwords are never printed or committed.

The explicit operator-only **app.empty_workspace** module was copied into the old backend and invoked once with **--confirm-empty-workspace ideaflow** after the verified backup. It truncates an exact list of this app's business/reference/session tables without CASCADE and deletes only non-bootstrap accounts. It retains the bootstrap Admin ID/password hash, schema, configurations, volumes and readable-reference sequence. No database/schema/volume was deleted or recreated; no cleanup runs on startup. Removed live business data includes the two old showcase batches. Generated legacy-role credentials/import fingerprints are historical private evidence; the old showcase guides are labeled accordingly.

Migration **0002** successfully upgraded both the empty live database and the preserved populated verification database; old non-Admin account IDs/history remain in verification with role User. Fresh test databases also migrated successfully. Bootstrap does not create references. Build: **TypeScript/Vite production build and backend container build passed**.

Meaningful backend suite: **16 passed in 14.50 seconds**, in an isolated PostgreSQL test database removed at completion. Checks include optional/unclassified ideas in analytics; User account-admin denial; User workflow/approval/results/rework; password reset/deactivation; normalized duplicate labels, concurrent creation, rollback of label creation after invalid actual dates; rename/merge audit preservation, stale version conflicts and current cohort aggregation; importer dry-run/additive/idempotent replay (including legacy JSON roles); finance decimals/coverage/snapshot immutability; event permissions, CSRF, forbidden backdating, stale/concurrent idea edits; known process fixtures. One existing Starlette/AnyIO deprecation warning remains.

Containerized **scripts/browser-shared.ps1 -Verification**: **1 passed in 21.2 seconds, 1 intentionally skipped**. Created a regular User through Admin Settings, signed out/in, confirmed no account-administration section, created typed labels, reused by dropdown and keyboard, created unclassified work, renamed a location/business unit, merged a category, preserved stale-form text, advanced New through Realized, approved an exact monthly ramp, completed tasks/milestones, entered and reviewed September results, and inspected history/screens. Desktop/mobile layout assertions passed at **1440×900, 1280×720, 390×844**, with no page errors/page-wide overflow. Screenshots **artifacts/shared-user-*.png** were visually inspected (settings at 1280 and detail at 390); create form at 1440 was also visually inspected.

Browser failures found and fixed: transition dialog briefly used the obsolete action list after refresh and crashed on option.allowed; it now tolerates the completed action while closing. Exact typed category now ranks first among dropdown choices, preserving keyboard selection when other labels exist. Plotly's delayed resize rejected after a chart unmounted; observer callbacks check visibility/mount state and handle the rejected resize. Initial test task-button selector was corrected from Edit/Update to the actual Edit task; no domain reset was used. Failed isolated test attempts and prior verification data remain preserved.

Final live **scripts/browser-shared.ps1**: **1 passed in 11.2 seconds, 1 intentionally skipped**. Read-only login/forms/register/Pipeline/Process/Value/Settings/layout checks at all three sizes confirm **zero ideas, zero locations/categories and one Admin**. New-name form preview was not saved. Live readiness reports **ready / 1.0.0** at **http://localhost:8080**, revision **0002**. API reconciliation confirms zero cases/events/coverage, unknown plan/actual/verified sums. Final read-only database count assertion passed and confirmed no temporary test/restore databases.

Populated persistence probe **IF-00396**, result **1,234.56**, two events and version survived restart and rebuild with full fingerprints for **11 tables**, including sites/categories. An initial check compared the old 9-table checker after container restart against the new 11-table baseline; after aligning the deployed checker, fingerprints matched. No business data changed. Re-running **scripts/verify-persistence.ps1 -SkipCreate** completed **restart PASS, rebuild PASS and isolated restore PASS**, with **156 verification ideas / 1,614 events** and all 11 fingerprints matching. The older backups/verification.dump was copied to **backups/verification-before-shared-20261009.dump** before replacing that verification artifact. Preserved verification cohort/event replay also passed. Verification services are stopped at handover; their volume remains intact.

Post-cleanup live backup **backups/ideaflow-20261009-110313.dump** was created with the binary-safe script. Manual starting example and expected financial outcomes are in UX_WALKTHROUGH.md. No practice records were loaded into live; all user-driven writes remain for the manual exercise. Only three healthy live services remain, with frontend loopback port 8080 published.

The post-cleanup live backup restore test also completed **PASS** across all 11 tables, with live unchanged and temporary restore database removed. Final Compose inspection showed the three live services healthy and only 127.0.0.1:8080 published. The readable-reference sequence remains advanced; the first new manual idea need not be IF-00001.

## Admin account controls — 2026-10-09

Implemented the account-controls amendment in PRD.md. Active Users/Admins share business actions subject to workflow prerequisites, recorded actors and reasons; account administration stays Admin-only. Settings now provides **Delete account**, **Regenerate password**, **Set password** and **View account history**. Unused accounts are physically removed with their sessions. Accounts with durable attribution are retired from access and user management, preserving business records and historical names. Open ideas/tasks require reassignment first; signed-in and bootstrap Admin accounts are protected. Regeneration returns a cryptographically random password once, stores only its Argon2 hash, revokes all target sessions and leaves inactive accounts inactive. Manual own-account reset signs the Admin out. No live account was deleted, deactivated or reset during this delivery.

Reverified `docker context ls`, `rdctl list-settings` and `docker --context default info`: detected context **default**, Rancher Desktop **moby / Rancher Desktop WSL Distribution**. All build, Python/Node and browser tooling ran in containers. Migration **0003** adds nullable retirement time and append-only `account_event`; fresh isolated test databases and the preserved populated verification database upgraded successfully. Live also upgraded from 0002 without a reset. Account mutations, session revocation and administrative audit append share a transaction; stale account versions return 409. Passwords are excluded from public users and audit rows.

Commands actually run included:

```powershell
docker --context default compose -f compose.yaml -f compose.verify.yaml -p ideaflow-verification build
docker --context default compose -f compose.yaml -f compose.verify.yaml -p ideaflow-verification up -d --wait --wait-timeout 150
docker --context default compose -f compose.yaml -f compose.verify.yaml -p ideaflow-verification exec -T backend pytest -q
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-shared.ps1 -Verification
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify-persistence.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 up
docker --context default compose up -d --wait --wait-timeout 150
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-shared.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 backup
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 restore-test -File backups/ideaflow-20261009-111810.dump
```

Backend: **21 passed in 19.22 seconds**, with the existing Starlette/AnyIO deprecation warning. New checks cover Admin-only access, unused deletion, historical retirement, reassignment blocking, stale-version/CSRF rejection, session revocation, old/new login behavior, inactive-account regeneration, self/bootstrap protection, own manual reset, preserved idea/history contents and append-only account audit permissions. All earlier financial/process/import/classification/workflow tests also passed. **TypeScript/Vite production build passed**.

Final isolated browser run: **2 passed in 21.1 seconds, 1 intentionally skipped**. The Admin test creates disposable test accounts, exercises generation/manual reset/session invalidation, deletes an unused account, checks open-work blocking, retires a historical account after reassignment, and checks account history and retained idea attribution. The regular User test completes the shared-workspace flow through Realized. Browser checks cover **1440×900, 1280×720 and 390×844**, with no page errors or page-wide overflow. Screenshots of desktop account management, small-screen account rows, reset preview and open-work deletion preview were visually reviewed. Generated passwords were held only in browser memory; screenshots were taken before generation or after closing its dialog.

Failures corrected: the initial history test expected an exact cell name while the displayed cell included its reason; the selector now identifies the account row and action. Small-screen review found account actions required horizontal scrolling; account rows now stack with every action visible. Screenshot checks wait for the sidebar's resize transition. An extra read-only reconciliation invocation mistakenly called the importer replay function, then incorrectly required historical occurrence ordering to equal sequence ordering; the corrected checker verifies contiguous sequences separately and replays lifecycle events in occurrence/sequence/ID order. **All 172 preserved verification cases reconciled**, with valid transition edges and matching current stage/disposition. No historical events were changed.

Populated persistence probe **IF-00412**, **1,234.56** result, two events and record version survived down/up and rebuild. Full sorted row fingerprints matched **12 tables**, including account audit, users and classifications. Populated backup **backups/verification.dump** restored in an isolated temporary database with identical fingerprints: **172 ideas, 1,694 idea events, 241 plans, 1,200 schedule rows, 160 results, 63 tasks, 139 comments, 3 batches, 19 retained accounts, 14 locations, 27 categories and 21 account events**. Later browser test records remain in the verification volume. The older verification dump was preserved as **backups/verification-before-accounts-20261009-111508.dump** before replacing this artifact. No verification data or volumes were reset.

Live pre-deployment backup **backups/ideaflow-20261009-111032.dump** was retained. Post-deployment **backups/ideaflow-20261009-111810.dump** restored successfully into a unique temporary database with identical fingerprints for all 12 tables and live unchanged. The temporary restore databases were removed. Private pre/post row fingerprints confirm the bootstrap Admin's original fields/password hash and every existing business table stayed identical, accounting only for the newly nullable retirement column. Live remains **zero ideas, zero locations/categories, one Admin and zero account events**. Account logins are not business/account-action history entries.

Limitations: historical account deletion preserves the identity row, including its name/email, for attribution; it is not erasure of past participation. Retired accounts cannot reactivate; ordinary inactive accounts can. Replacement passwords must be shared privately by the Admin; no email delivery or forced first-login password change is implemented. Account history displays the latest 100 actions. This remains local authentication and application audit history, not enterprise identity or cryptographic tamper resistance.

Final live browser after the mobile adjustment: **1 passed in 10.5 seconds, 2 intentionally skipped**. Confirmed new account controls and own-account disabled actions, empty account history, login, all requested empty screens and three viewport sizes without business writes. Visually reviewed **artifacts/accounts-live-settings-390.png** and **artifacts/account-row-390.png**: actions are visible without horizontal scrolling. Post-browser fingerprints again confirm unchanged credentials/business tables. Final readiness **ready / 1.0.0**, schema **0003**, URL **http://localhost:8080**. Exactly **three healthy running services** remain, only frontend loopback 8080 published. Verification containers were stopped with ordinary Compose down; **ideaflow_pgdata** and **ideaflow_verification_pgdata** remain. Live database list contains only ideaflow/postgres/template0/template1, with no lingering test/restore databases.

## In-app manual — 2026-10-09

Added **Walkthrough** at **http://localhost:8080/guide** for every signed-in account, with links from Overview, Settings, the create form and each saved idea. Twelve detailed topics cover choosing a user's own opportunity and baseline, capture without predefined classifications, Screening/Analysis, approved monthly plans, implementation tasks/milestones, elapsed actuals and explicit verification, Realized, supported pauses/rework, value/process interpretation, shared grouping and troubleshooting. Instructions use current screen/button names and explain prerequisites and accountability. No sample data is created. Contextual links open a separate tab, directing Financials at Validation/Realized to results guidance and Implementation to delivery guidance. Contents links support section focus, direct URLs and reload; full-text topic search is retained in the URL. Print includes all topics even when search filters the screen. README, PRD and the optional manual exercise document point to the in-app guide.

Reverified detected Rancher Desktop **default / moby** context using context list, rdctl settings and server info. All tools ran in containers. **TypeScript/Vite production build passed** via `docker --context default compose build frontend`. Started the preserved verification project using `docker --context default compose -f compose.yaml -f compose.verify.yaml -p ideaflow-verification up -d --wait --wait-timeout 150`. No backend, migration, package, finance or workflow changes were needed.

`powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-guide.ps1 -Verification`: **1 passed in 11.9 seconds**. Verified Overview/Settings/sidebar discovery, contents navigation, focused anchors and reload, full-text search and empty search, print media with all 12 sections, mobile navigation, stage/tab-specific help targets, and opening help while an unsaved create-form title remains intact. Screenshots **artifacts/guide-start-*.png** and **artifacts/guide-analysis-*.png** passed page-wide overflow checks at **1440×900, 1280×720 and 390×844**; desktop start, desktop Analysis and mobile Analysis were visually reviewed. No browser page errors. Initial test expected an incorrect fixed search-result count; corrected the assertion and extended search from topic metadata to the full instruction text. Search no longer refocuses a section on each keystroke. Workflow instructions were checked against backend prerequisites, including Validation rework reopening required tasks and clearing completion.

`powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-shared.ps1 -Verification`: **2 passed in 31.8 seconds, 1 intentionally skipped**. Regular User opened the detailed manual from Settings, followed Create your own idea, created/classified/reorganized work and completed the workflow through Realized with tasks, a monthly plan, actuals and review. Account controls regression also passed. All test practice records remain only in the isolated verification volume.

Playwright generated **artifacts/guide-print.pdf** using A4/15mm margins. A transient Python container with PyMuPDF 1.26.7 read and rendered the document: **6 pages, all 12 topic headings present, no blank pages**. First/last page images were visually reviewed. This PDF renderer was a temporary verification tool, not an app dependency or service. Browser print/save-to-PDF uses the user's print dialog; physical printing was not tested.

Deployed the built image using `docker --context default compose up -d --wait --wait-timeout 150`. Live `scripts/browser-guide.ps1`: **1 passed in 16.8 seconds**. Live `scripts/browser-shared.ps1`: **1 passed in 14.1 seconds, 2 intentionally skipped**, confirming usable empty screens and account controls. These live tests saved no business records. Full fingerprints before/after deployment and live browser review matched all **12 business/account tables**, including the unchanged Admin password hash: **zero ideas/references/account events, one Admin**. No database reset, volume deletion or demo loading occurred.

Final readiness **ready / 1.0.0**, schema remains **0003**, URL **http://localhost:8080/guide**. Exactly **three healthy long-running services** remain; only frontend loopback 8080 is published. Stopped verification with ordinary Compose down, preserving both named volumes. For this frontend/documentation change, prior backend tests and backup/restore evidence above remain applicable; they were not rerun. The guide is read-only instruction, without persistent per-user progress tracking, and does not automatically advance stages or populate forms.

## Test ideas and reversible Admin removal — 2026-10-09

Implemented the accepted Test/removal PRD amendment in schema **0004**. New ideas can be flagged Test by any active User. Existing marking is an explicit one-way Admin command. Register, Overview, Pipeline, My Work, Process, Value and exports default to business ideas and accept `idea_scope=business|test|all`. Fictional import provenance is independent. Admin removal archives complete Test records, preserving lifecycle, tasks, plans, approved snapshots, actuals, verification, comments and append-only history. Removed detail is Admin-only/read-only. Settings exposes paginated/searchable removed records and restoration as Test, with explicit active-owner/task reassignment when necessary. Reasons, confirmation and optimistic concurrency protect all three commands. Shared classification updates remain audited across archived records. No automatic marking/removal, hard deletion, reset, added service or dependency.

Detected Rancher Desktop again: actual context **default**, container engine **moby**, server **Rancher Desktop WSL Distribution**. All Python/Node/browser/build tools ran in containers with explicit context. Existing live baseline was **zero ideas/classifications/batches, two accounts and one account event**; the second account was created by the user since the prior guide verification. Pre-change backup: **backups/ideaflow-20261009-130051.dump**. Private before/after fingerprints matched all **12 business/account tables**, including every existing account field/password hash and account audit row. No existing account or idea was changed, removed or reset.

Actual checks:

```powershell
docker --context default compose -f compose.yaml -f compose.verify.yaml -p ideaflow-verification build
docker --context default compose -f compose.yaml -f compose.verify.yaml -p ideaflow-verification up -d --wait --wait-timeout 150
docker --context default compose -f compose.yaml -f compose.verify.yaml -p ideaflow-verification exec -T backend pytest -q
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-test-ideas.ps1 -Verification
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-guide.ps1 -Verification
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-shared.ps1 -Verification
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify-persistence.ps1
docker --context default compose up -d --wait --wait-timeout 150
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-test-ideas.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-shared.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-guide.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 backup
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 restore-test -File backups/ideaflow-20261009-132103.dump
```

**TypeScript/Vite production build passed**. Final backend suite: **25 passed in 45.11 seconds**, including all earlier workflow/financial/process/import/classification/account tests. New cases verify Admin-only marking/removal/restoration and removed access; CSRF, blank reason, missing confirmation and unsupported generic fields; default/explicit cohorts across all APIs and exports; exact annual potential totals; developed record preservation and all ordinary mutations blocked; concurrent removal yielding one success/one conflict; retired-owner/open-task reassignment; archived classification audit. Existing Starlette/AnyIO deprecation warning remains.

Isolated Test browser: final **1 passed in 29.4 seconds, 1 intentionally skipped**. User creates a flagged idea and works New → Screening → Analysis; real API creates an approved plan, task, comments, elapsed actual and verification. Admin cancellation leaves the record unchanged; a concurrent comment makes the removal preview stale, produces 409, and preserves the typed reason. Fresh preview removes the idea; read-only tabs retain financial/task/history evidence and hide editing/verification controls; ordinary User direct access returns 403. Admin retires the practice owner, explicitly selects an active owner/reassigns the open task, restores and checks history; marks a separately captured practice idea Test; archives the developed idea again for persistence checks. No live mutations in this test. Screenshots and no page-wide overflow checks cover **1440×900, 1280×720, 390×844** for removal dialog, register, Pipeline, Process, Value, removed list and read-only Financials. No browser page errors. Visually reviewed desktop and mobile removal previews, desktop removed list, read-only Financials and Process filter layout. Mobile modal scrolls vertically to reach its actions; wide financial/history tables retain horizontal scrolling inside their containers.

Isolated guide regression: **1 passed in 8.2 seconds**; shared/account/workflow regression: **2 passed in 27.0 seconds, 1 intentionally skipped**. Live final read-only Test controls/filter/guide smoke: **1 passed in 16.3 seconds, 1 intentionally skipped**; live shared screen/layout/account check: **1 passed in 19.7 seconds, 2 intentionally skipped**; live guide discovery/search/navigation/print check: **1 passed in 8.7 seconds**. Updated walkthrough capture/topic 11 describe Test cohorts, review/removal/restoration and inactive-account reassignment. README, architecture, dictionary and manual exercise now explain cleanup. Live tests saved no business records.

Failures fixed during verification: preservation assertion initially compared available workflow actions, which intentionally become empty while removed; it now checks retained records and disabled transitions separately. Browser link selectors now account for the reference/Test label in a link's accessible name. Browser waits for the workflow dialog to close before typing the next note, preventing a test timing race from saving an empty note. An extra backend regression invocation was interrupted by the verification restart; its unique test database was identified, checked for no active connections and removed individually, then the full suite reran successfully. No live database/volume cleanup was performed.

Persistence was verified twice. Final probe **IF-00440**, actual gross **1,234.56**, two events and version survived ordinary down/up and rebuild. Full row fingerprints matched all 12 tables, including archived **IF-00430** and **IF-00438** with retained approved schedules/results/tasks/removal metadata. Final populated **backups/verification.dump** restored into an isolated temporary database with identical fingerprints: **200 ideas, 1,843 events, 275 financial plans, 1,250 schedule rows, 168 actual periods, 69 tasks, 147 comments, three demo batches, 31 retained accounts, 18 locations, 35 categories and 54 account events**. Earlier dumps preserved as **backups/verification-before-test-ideas-20261009-131428.dump** and **backups/verification-test-ideas-first-20261009-132017.dump**. A separate read-only checker verified contiguous event sequences, valid lifecycle edges and current stage/disposition replay for **all 200 preserved cases**, including both archived Test ideas. Cleanup events are excluded from process lifecycle discovery.

Live post-deploy backup **backups/ideaflow-20261009-132103.dump** restored into a unique temporary database with matching 12-table fingerprints and live unchanged. Temporary restore databases and the interrupted test database were removed individually. Both database lists were checked and contain only ideaflow/postgres/template0/template1. Ordinary verification Compose down preserves **ideaflow_verification_pgdata**; production **ideaflow_pgdata** and all other project volumes/configuration remain. Final live readiness **ready / 1.0.0**, migration **0004**, URL **http://localhost:8080**, exactly three healthy services, only frontend published on loopback 8080.

Limitations: removal is retained archival, not erasure or permanent purge. Only Admin can inspect/restore removed records. Test marking is deliberately one-way; restoration keeps Test status. Existing imported/practice records are not inferred as Test. Test/all scopes intentionally include practice financial amounts and are visibly labeled. Shared classification rename/merge can still change archived grouping labels with history. Physical printing was not tested. There is no bulk cleanup, retention scheduler, or extra authorization role.

## User-perspective manual revision — 2026-10-09

Rewrote **docs/UX_WALKTHROUGH.md** for the user's already-created **User** account. Twelve User steps cover capture, optional classifications, finding Test work, Screening/Analysis, pause/rework, monthly planning, approval, tasks/milestones, elapsed reporting/review, Realized, analytics and shared regrouping. Removed the requirement to create Alex or use bootstrap Admin credentials and the stale assumption of an empty live workspace. Added distinctive practice names, reusable references, explicit saved-state checkpoints and a last-completed-month example for a single-session hypothetical Test exercise. Optional Admin removal/restoration and disposable-account maintenance exercises appear only after the full User workflow. README identifies this intended reader.

Documentation review checked the instructions against current UI labels and backend prerequisites/formulas. PowerShell content checks passed: 12 numbered User sections, two optional Admin sections, no Admin login/setup instructions in the main User flow, required action labels, existing linked local files and example arithmetic ($10,800 annual net, 260% full-plan ROI, $700 reported monthly net). This change edits documentation only; no accounts, business records, application code, configuration, containers or volumes were changed. No new browser/backend test run or deployment was needed or claimed; application verification above remains the latest runtime evidence. The exercise itself remains for the user to perform manually.

## Unified ideas and quiet Admin removal — 2026-10-09

Implemented the latest user instruction: every nonremoved idea belongs to the same workspace. Capture, register, Pipeline, My Work, Overview, Process, Value and exports have no Test checkbox, badge, marking command or idea-set filter. Old query parameters do not segregate ideas. Admin can remove any idea through the collapsed **Admin actions → Remove idea** control, with impact preview, reason, explicit confirmation and optimistic version. **Settings → Removed ideas** provides read-only inspection and reasoned restoration, including explicit active-owner/open-task reassignment when needed. Removal/restoration leave stage, disposition, financial evidence and prior events intact. Updated the normal-User UX_WALKTHROUGH.md, the in-app manual, README, demo guide, architecture and dictionary. The earlier Test design and its verification entries above are historical and superseded by this entry.

Runtime rediscovered and verified: actual Docker context **default**, Rancher Desktop engine **moby**, server **Rancher Desktop WSL Distribution**. All build, Python, Node and Playwright tooling ran in containers using that context explicitly. Live URL **http://localhost:8080**; app version **1.0.0**; Alembic **0005**. Migration 0005 removes only the old restriction that an archived idea must carry a Test flag. Historical flags and append-only events are retained without rewriting; flags are excluded from current API fields and ignored by reporting. Earlier fictional import provenance remains required and retained.

Actual validation:

- **TypeScript/Vite production build passed**, including the subsequent persistence rebuild.
- Backend **25 passed in 20.18 seconds**. Coverage includes unified queries/exports and exact potential totals for ordinary and legacy-flagged records; ignored old cohort bookmarks; rejected marking/generic flag fields; Admin-only removal/restore/read-only access; CSRF/reason/confirmation/version enforcement; retained developed financials/tasks/comments/history; concurrent removal with one success and one conflict; inactive-owner/task reassignment; audited shared classification changes. Earlier financial, process, workflow, importer and account tests also passed. One existing Starlette/AnyIO deprecation warning remains.
- Isolated removal browser **1 passed in 17.5 seconds, 1 intentionally skipped**: ordinary User capture and New → Screening → Analysis, approved plan/task/elapsed verified outcome via the real API; Admin cancellation; stale preview conflict retaining the typed reason; archive/read-only access; historical-account retirement; explicit ownership/task reassignment and restore; developed ordinary idea **IF-00441** archived again for durable verification.
- Isolated shared account/User regression **2 passed in 23.2 seconds, 1 intentionally skipped**; guide **1 passed in 8.0 seconds**. A separate populated view check **1 passed in 16.7 seconds, 1 intentionally skipped** checked fully loaded Overview, register, Pipeline, Process, Value and capture across **1440×900, 1280×720, 390×844**, no separation controls, no page errors or page-wide overflow, and an ordinary Admin detail with removal initially collapsed. Browser screenshot checks now wait for actual Process/Value data instead of only the heading. This additional check made no business writes.
- Deployed read-only browser: unified controls/removed-list/guide **1 passed in 5.7 seconds, 2 intentionally skipped**; shared empty screens/layout/accounts **1 passed in 9.3 seconds, 2 intentionally skipped**; walkthrough discovery/search/navigation/print **1 passed in 9.0 seconds**. No live idea/account mutations were performed.
- Visually reviewed populated normal-User detail, Pipeline and Admin removal previews/read-only Financials; fully loaded populated Overview/Process/Value/capture; live create, Process and Value. Screenshots include **artifacts/unified-admin-detail-1440.png**, **unified-process-1440.png**, **unified-value-1280.png**, **unified-create-390.png**, **test-remove-preview-1440.png**, **test-remove-preview-390.png**, **shared-empty-create-1440.png**, **shared-empty-process-390.png**, **shared-empty-value-1280.png**. Historical artifact naming does not imply a separate current idea type. Mobile modals scroll vertically and wide supporting tables/board/graph scroll within their containers.

Commands actually run included:

```powershell
docker --context default compose -f compose.yaml -f compose.verify.yaml -p ideaflow-verification up --build -d --wait --wait-timeout 150
docker --context default compose -f compose.yaml -f compose.verify.yaml -p ideaflow-verification exec -T backend pytest -q
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-idea-removal.ps1 -Verification
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-shared.ps1 -Verification
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-guide.ps1 -Verification
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify-persistence.ps1
docker --context default compose up -d --wait --wait-timeout 150
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-idea-removal.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-shared.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-guide.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 backup
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 restore-test -File backups/ideaflow-20261009-141256.dump
docker --context default compose exec -T -e PYTHONPATH=/app backend python /handover/unified-check.py
docker --context default compose -f compose.yaml -f compose.verify.yaml -p ideaflow-verification down
```

Populated persistence probe **IF-00447**, gross actual **1,234.56**, two events and record version survived ordinary down/up and rebuild with identical sorted row fingerprints across **12 tables**. **backups/verification.dump** restored to a unique isolated temporary database with matching fingerprints and source unchanged: **207 ideas, 1,889 events, 284 financial plans, 1,263 schedule rows, 171 actual periods, 71 tasks, 150 comments, three demo batches, 34 retained accounts, 19 locations, 37 categories and 63 account events**. Archived ordinary **IF-00441** and earlier archived **IF-00430/IF-00438** survived. A read-only checker confirmed contiguous event sequences, valid lifecycle edges and matching current stage/disposition for **all 207 ideas**, including all three archived records. Removal events do not enter process lifecycle paths.

The older populated dump was preserved as **backups/verification-before-unified-ideas-20261009-140900.dump**. It was independently restored to a unique temporary database; schema 0004 confirmed. Comparing its rows with current schema 0005 confirmed **every earlier row across all 12 tables remained exactly unchanged**, including 200 prior ideas, 1,843 earlier events, all earlier account/financial/classification rows and legacy flags. Only additive verification records were present afterward. Temporary restore databases were removed individually.

Live pre-deployment backup **backups/ideaflow-20261009-140159.dump** retained. Post-deployment **backups/ideaflow-20261009-141256.dump** restored successfully into a unique isolated temporary database with all 12 fingerprints identical and live unchanged. Private pre/post snapshots **local/unified-ideas-before.json** and **local/unified-ideas-after.json** matched exactly, including both existing accounts' fields/password hashes and the existing account audit row. Live remains **zero ideas/classifications/batches, two accounts and one account event**. No cleanup, reset, automatic import, credential change or volume deletion occurred.

Verification correction: the private read-only replay/preservation script initially lacked the application import path and stopped before any check/write; reran with **PYTHONPATH=/app**, yielding PASS. An earlier backend test assertion accidentally omitted the prohibited field in its 422 check; corrected it to send the legacy field explicitly, then all 25 tests passed. Screenshot checks were strengthened after review found some older captures were taken before dashboard data arrived; the completed-data screenshot run passed.

Limitations: archive is retained removal, not permanent erasure. All ordinary ideas, including manual exercise ideas, contribute to shared totals until Admin removes them. Only Admin can inspect/restore removed records. Historical Test-related events may still appear in History because earlier evidence is append-only; no active Test labels or filters remain. Legacy Test endpoints are removed; old cohort query parameters are ignored. No bulk cleanup, automated retention, forced independent finance review, physical print test or extra service was added. Existing accounts use their existing passwords.

Final inspection: exactly **three healthy live services** remain, with only **127.0.0.1:8080** published. Verification containers were stopped with ordinary Compose down; **ideaflow_pgdata**, **ideaflow_verification_pgdata** and other project volumes remain. Both database lists contained only ideaflow/postgres/template0/template1, with no lingering test/restore databases. Final readiness returned ready / 1.0.0, schema 0005; the post-browser live preservation comparison again passed across all 12 tables.

## Monthly outcome guidance and idea financial timeline — 2026-10-09

Addressed the user's difficulty with **Monthly outcomes and result verification** and **Cumulative value evidence**. Monthly outcome fields now explain measured gross benefit, operating recurring cost and one-time implementation spending for that month, with an optional numerical example, blank-versus-zero guidance, saved-period review steps and an app-timezone limit on the Outcome month. No annual estimates are copied into results. The in-app manual and UX_WALKTHROUGH.md explain these sections from a User perspective.

Idea detail now derives its full financial timeline from the current approved monthly schedule (latest saved draft before approval) plus outcome months, then idea dates/current month if no financial months exist. This avoids the old fixed calendar year and allows benefits after delivery completion. Added **Evidence from month**, **Evidence through month**, **Apply date range**, **Full idea timeline** and an exact monthly/cumulative supporting table. Date choices persist in the URL and do not refetch/reset the business forms. The chart axis uses the chosen range even with unknown values. Running totals restart at the chosen From month. Current/future/unreported/unverified results remain gaps; unapproved drafts do not enter expected value. The read-only **GET /api/v1/ideas/{id}/value?start=YYYY-MM-01&end=YYYY-MM-01** follows the existing 120-month cap and Admin-only removed-record access. Financial formulas, portfolio calendar-year defaults, approvals and workflow are unchanged. No migration, new service or dependency was required.

Detected context **default**, Rancher Desktop **moby / Rancher Desktop WSL Distribution**. Build, Python, Node and browser tooling ran in containers with explicit Docker context. Deployed and verified at **http://localhost:8080**, readiness **ready / 1.0.0**, schema **0005**. Live read-only browser opened **IF-00205 · Reduce repeated dispatch checks** with the saved **September 2026–August 2027** timeline, applied a one-month view, reset, checked unsaved outcome text survived and confirmed the saved idea/plans/results/tasks/comments/events/version were unchanged by that browser test. Existing credentials were used privately.

Checks actually passed:

- TypeScript/Vite production build and subsequent persistence rebuild.
- Backend **27 passed in 24.01 seconds**, with one existing Starlette/AnyIO deprecation warning. New cases cover full approved schedule across a year boundary, 260% full-plan ROI, a one-month view, exact net benefit/actual/verified amounts, missing results, retained current forecast after a new draft, undated/result-only fallback, invalid/inverted/overlong ranges, removed-record access and view changes without record/version/history mutations. Existing workflow/import/financial/process/account/removal/classification tests passed.
- Final isolated financial browser **1 passed in 14.8 seconds, 1 intentionally skipped**. Created ordinary fixture **IF-00450**, saved a 12-month plan, confirmed no forecast before approval, worked Screening/Analysis/approval via backend commands, reported $800 gross/$100 recurring/$3,000 spending and explicitly reviewed the result. Confirmed $700 actual/verified monthly net, 260% full-plan ROI, known coverage, unknown future months, one-month graph axis, range persistence on reload, invalid range rejection, reset, wider missing-month gaps, and unsaved financial rationale/outcome text surviving view changes. Layout checks at **1440×900, 1280×720, 390×844** passed without page errors/page-wide overflow. Earlier passing isolated run was 1 passed in 9.3 seconds; final run aligned captures to section headings for visual review.
- Isolated guide **1 passed in 7.9 seconds**; live financials **1 passed in 4.1 seconds, 1 intentionally skipped**; live guide **1 passed in 13.9 seconds**. Guide discovery/search/print/contextual links remain usable. Live browser performs no business writes.
- Visually reviewed desktop/mobile outcome fields, hints, example, date controls, populated and live cumulative chart, coverage and supporting table. Evidence: **artifacts/financial-evidence-1440.png**, **financial-evidence-1280.png**, **financial-evidence-390.png**, **monthly-outcomes-1440.png**, **monthly-outcomes-390.png**, **financial-evidence-live-1440.png**. Mobile tables scroll within their container.

Commands actually run included:

```powershell
docker --context default compose -f compose.yaml -f compose.verify.yaml -p ideaflow-verification up --build -d --wait --wait-timeout 150
docker --context default compose -f compose.yaml -f compose.verify.yaml -p ideaflow-verification exec -T backend pytest -q
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-financials.ps1 -Verification
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-guide.ps1 -Verification
docker --context default compose up -d --wait --wait-timeout 150
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-financials.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-guide.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 backup
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 restore-test -File backups/ideaflow-20261009-150718.dump
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify-persistence.ps1
```

Verification corrections: the new backend test initially used the wrong metric key `benefit`; changed to the existing `net_benefit`, then all 27 passed. The browser initially proceeded while still on the login heading; it now waits for the signed-in Overview before requesting data. A viewport assertion initially caught Plotly's delayed resize; polling for settled layout passed at all three sizes. These were verification timing/assertion corrections, not relaxed business calculations.

Live-data verification limit: the user continued the manual exercise during this delivery. Initial private fingerprints had two ideas, 15 events and no outcome periods; subsequent live activity added lifecycle/approval/edit events and one result. The before/after equality check therefore correctly failed; it was not treated as data loss or reset. Account/reference/schedule/comment tables remained identical in that comparison; live changes were confined to the worked idea, plan approval, events and outcome. The standard restore-test command restored the dump but its equality-to-current-live check also correctly failed because the dump preceded later user writes. Replaced that comparison with an independent isolated restore of **backups/ideaflow-20261009-150718.dump** and a read-only check: **PASS**, all restored idea sequences/current lifecycle states reconciled, and every earlier idea/account event row in the restored backup still exists exactly in live. Restored snapshot: **two ideas, 17 idea events, six plans, 24 plan periods, one actual period, one comment, two users, one location, one category, one account event**, zero tasks/batches. Private checker **local/financial-backup-check.py** was executed in the backend container with PYTHONPATH=/app. Temporary restore databases were removed individually. No live ideas, results, accounts, credentials or history were changed by the agent.

Limitations: date controls change displayed evidence, not business dates or saved schedules. Full planned horizon cards stay attached to the full idea timeline; changing the chart's range restarts the displayed cumulative totals within that range. Benefit is gross minus recurring cost; cash flow separately subtracts spending. A selected historical month range uses current approved plans/results, not historical as-of reconstruction. Missing evidence remains unknown. Maximum horizon is 120 months. Physical printing was not tested. Deployment remains three services and preserves all volumes.
Final persistence verification **PASS**: isolated probe **IF-00451**, actual gross **1,234.56**, two events and record version survived down/up and rebuild; all 12 sorted table fingerprints matched. Populated **backups/verification.dump** restored to a unique temporary database with identical fingerprints and source unchanged: **211 ideas, 1,918 events, 291 plans, 1,299 schedule rows, 175 actual periods, 71 tasks, 150 comments, three batches, 34 users, 19 locations, 37 categories and 63 account events**. Previous verification dump retained as **backups/verification-before-financial-timeline-20261009-151100.dump**. All prior archived/developed records remain in that preserved volume.
Final service inspection: verification containers stopped with ordinary Compose down, volumes retained. Live remains three healthy services, frontend on 127.0.0.1:8080, readiness ready / 1.0.0 and schema 0005. Both database lists contain only ideaflow/postgres/template0/template1 with no lingering test/restore databases.

## VPS deployment — 2026-10-09

User authorized deployment using VPS_FOUNDATION, VPS_SECURITY and VPS_COCKPIT, and explicitly selected copying the current local workspace. Deployed **IdeaFlow 1.0.0 / schema 0005** at **https://vps-8104e6c8.vps.ovh.us:8443**. Native encrypted-key SSH could not unlock noninteractively; a transient, containerized Paramiko client used the existing passphrase from Windows User environment with strict known-host pinning. No host Python/Node installation, SSH policy change or alternative runtime was required.

Actual inspection: Rancher Desktop context list contained **default**, server identified **Rancher Desktop WSL Distribution**, and rdctl reported **moby**. Local image builds and tests used `docker --context default`. VPS: x86_64, Podman **5.7.0**, 11,671 MiB memory and 93 GiB free at inspection. Existing Caddy routes/SSH/firewall/Cockpit were read before changes; no production application account/stack existed. Added dedicated **ideaflow UID/GID 1001**, subordinate ranges **165536:65536**, lingering and its local Podman socket. No sudo/SSH privilege was granted to that account.

Exactly three VPS app containers: **ideaflow-postgres**, **ideaflow-backend**, **ideaflow-frontend**, under **app-ideaflow.target**. Frontend publishes **127.0.0.1:18081 → 80**; backend and database have no published ports. Caddy's separate route and UFW rule expose **8443** only. Existing shared gateway/certificate configuration and other accounts/projects/volumes were preserved. The dedicated database volume is **ideaflow-pgdata**; local **ideaflow_pgdata** remains intact and local app healthy at **http://localhost:8080**. No automatic demo import.

Images built locally, exported and SFTP-transferred, then imported into the dedicated account's storage. Archive SHA-256 **478d18d2e625ab3dc369b4363050761b4457211719a2572f5d999f069ad17628**, 257,183,232 bytes. Installed Quadlets pin full Podman image content IDs:

| Image | Content ID |
| --- | --- |
| Backend | `b3cdf0a7c4bcaf6454e895d123b08081b828c1dd1c3113fbedd307d24b54d648` |
| Frontend | `06d01ea43dbfe5a57f3a7f40e45d9658544b71ecf2871ff30b998dd3d9b143fd` |
| PostgreSQL 17.6 | `567d5d704a3e5a4864393b623a0d50eb1b5a4ad134cdac7cf19555cb2d8ffe9e` |

Docker's manifest-list IDs and Podman's configuration IDs differ; the table records the actual VPS image pins. Deployment templates in infra/vps are resolved at initial installation. No registry image pull is needed for restart.

### Copied data and integrity

`pg_dump -Fc --no-owner --no-acl --exclude-table-data=app_session` captured the local workspace at approximately **2026-10-09 20:28 UTC / 16:28 America/New_York**. Existing user password hashes and all business/audit rows are copied; browser sessions excluded. Dump SHA-256 **628760e778c151b8d7a7a6ad325f5afcc0334eec95a9571af7795c36dfc77a9c**, 41,421 bytes. Restored the same snapshot into a separate local verification database and the fresh VPS volume; compared the two rather than comparing against a changing live local workspace. Temporary local database removed individually afterward.

All 12 business-table SHA-256 fingerprints matched the restored source snapshot before and after full-stack restart, dedicated user-manager restart and isolated backup restore. Private reports: **local/vps-transfer/source-report.json**, **/home/ideaflow/handover/vps-report.json**. Counts:

| Entity | Count |
| --- | --- |
| Ideas | 2 |
| Idea events | 27 |
| Financial plans | 6 |
| Plan periods | 24 |
| Actual result periods | 1 |
| Tasks / comments | 1 / 1 |
| Accounts / account events | 2 / 1 |
| Locations / categories | 1 / 1 |
| Demo batches | 0 |

**IF-00205 — Reduce repeated dispatch checks**, Validation/Active; **IF-00206 — Agree a daily dispatch cutoff**, New/Active. Lifecycle replay matches both current states; complete unique per-idea sequences have no gaps. One existing approval transaction has its stage-change timestamp a few milliseconds earlier than the plan-approved timestamp despite the latter's lower sequence; sorting all sequence numbers verifies their completeness, and lifecycle replay uses the contract's timestamp/sequence ordering. Existing event history was preserved, not rewritten. Reference sequence remains **206 / is_called=true**.

### Checks actually passed

- **Backend:** `docker --context default compose build backend frontend`, then `docker --context default compose run --rm --no-deps backend pytest -q`: **28 passed**, one existing Starlette/AnyIO deprecation warning. New deployment-auth regression covers exact HTTPS origin/port, rejection of another port, Secure/HttpOnly/SameSite host cookie, CSRF requirement and logout/session revocation. Test database was isolated and removed. Live local services were not restarted by the test/build.
- **Public HTTPS:** Windows Invoke-RestMethod and containerized Chromium used certificate validation; readiness returned **ready / 1.0.0**. Caddy configuration validated before reload. Credentials authenticated, copied account hashes stayed identical, and production login issues **__Host-ideaflow_session**, Secure, HttpOnly, SameSite=Strict, Path=/, without Domain. Exact APP_ORIGIN includes port; HTTP upstream does not undermine browser HTTPS authentication.
- **Browser/layout:** `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-vps.ps1`: **1 comprehensive test passed**, 20.3 seconds. Nine screens at **1440×900**, **1280×720**, **390×844**: Overview, Ideas, Pipeline, Process, Value, Walkthrough, Settings, idea Financials and History. **27 screenshots** saved in **artifacts/vps-WIDTH-INDEX.png**. No page errors/API 5xx, no error alerts or page-width overflow in the tested views. Nested route refresh works. Login/logout/session revocation passed and no business records changed. Screenshots reviewed for Process, mobile Process, Financials and Value. The Value view shows unverified benefit **Unknown**, approved selected-year benefit **$3.6K**, annual potential **$10.8K**; idea full-horizon planned ROI **260.0%**. Process has **2 cases**, **1 with backward moves**, no completed cases and 2 ongoing visits. Small live sample was not represented as a showcase bottleneck.
- **Persistence:** final **infra/vps/verify-persistence.sh** invocation passed without manual recovery: Cockpit helper lists target, stops whole stack, loopback listener closes and all app containers stop; helper restarts it with three healthy members. Dedicated **user@1001.service** restart automatically brings stack back; HTTPS and every source fingerprint/lifecycle still match. Host machine reboot was not performed.
- **Backup/restore:** daily backup oneshot invoked successfully. Custom dump **/home/ideaflow/backups/ideaflow-20261009T204728Z.dump** restored into a unique `ideaflow_restore_*` database. `python -m app.restore_check` returned **PASS / live_unchanged=true** for all 12 tables; temporary database then dropped. Final VPS database list contains only ideaflow, postgres, template0 and template1. Dump downloaded to **backups/vps-ideaflow-20261009T204728Z.dump**, SHA-256 **3cd010e555393bb4c19361d5895c917223d649c00caf26f491da9833c5a44f1d**. Private raw persistence log downloaded with checksum verification to **artifacts/vps-persistence-verified.log**. Automatic daily timer enabled, next observed trigger **2026-10-10 04:08:39 UTC**; no deletion retention enabled.
- **Cockpit:** dedicated account authentication returned HTTP 200 with authenticated session cookie through encrypted SSH forwarding. Installed helper listed/started/stopped the actual target; final state active. Cockpit browser GUI click/rendering not exercised.
- **Exposure/resources:** external containerized TCP probes passed: 8443 reachable; **18081, 8000, 5432, 9090 and 2019 inaccessible**. Host listeners confirm loopback frontend/management, public Caddy and existing SSH. Per-container memory.max/cpu.max verified: PostgreSQL **1610612736 / 150000 100000**; backend **805306368 / 100000 100000**; frontend **134217728 / 50000 100000**. Server secret environment files mode **600**. Final host and dedicated user systemd failure lists empty.
- **Tooling:** transient SSH image rebuilt with all Python dependencies pinned; Python compile and shell syntax checks run in that container. Windows credential values written/read back privately in User scope. No credentials in committed docs/source.

### Corrections and remaining limits

Initial account password lacked a special character required by host PAM; generated a compliant password and successfully set it without relaxing the policy. Newly created intermediate configuration directories had root ownership; corrected only those dedicated account directories. Podman execution initially inherited inaccessible /home/ubuntu; remote app operations now use /home/ideaflow. Quadlet stripped part of an inline Python healthcheck's quotes; replaced it with a mounted, world-readable nonsecret healthcheck file. These setup failures were fixed before public browser verification.

Dedicated user-manager restart initially killed rootless pause/DNS processes before containers completed shutdown; Podman advised namespace migration, which hit a Podman 5.7 teardown panic. Recovered only stopped IdeaFlow container objects and its transient runtime DNS directory; kept all volumes, images, database/history and other accounts. Added dedicated user-manager ExecStop and **zz-ideaflow.conf** with 180-second timeout, ordered after the distribution's five-second timeout drop-in. Backend launcher now `exec`s Uvicorn to receive SIGTERM directly. The final complete persistence run passed with the corrected configuration and no manual intervention. Podman still logs a last-container network-process cleanup permission error; containers subsequently recreate successfully and data/health/integrity pass. This remaining runtime message is documented rather than concealed.

Browser test corrections: JavaScript variable `process` shadowed Node environment access; renamed it. Hyphenated environment names survived the direct Python container invocation but were dropped by the Playwright shell; browser wrapper now passes temporary underscore aliases while persisted Windows names remain unchanged. Walkthrough includes a hidden print-only second h1; visibility assertion targets the normal first heading. Final browser run passed; earlier failed attempts are not counted as successful checks.

No full host reboot, Cockpit GUI clicking, overnight timer execution, automatic off-host backups/alerts, SSO or internet-facing account lockout/rate limiting was verified or added. Local/VPS databases are independent after the recorded snapshot. Backup files include private account/session data, and Windows environment variables are persistent storage rather than a secret vault. See [VPS_IDEAFLOW.md](VPS_IDEAFLOW.md) for operation, credential variable names, backup commands and optional additive demo loading.

### Cockpit visibility follow-up — 2026-10-09

User reported no containers/application visible in Cockpit. Read-only inspection confirmed all three IdeaFlow containers healthy and the actual installed stack helper lists **app-ideaflow.target / active** under `ideaflow`; the same helper under `ubuntu` returns **[]**. Dedicated Cockpit account authentication through the encrypted SSH channel passed again. Cockpit socket remains loopback-only, installed Application stacks menu/files present, and both users have lingering enabled. Updated VPS_COCKPIT.md to distinguish the dedicated application login from host administration and remove stale pre-deployment empty-stack instructions. No accounts, permissions, containers or business records changed. The user's current browser account was not inspected; an `ubuntu` session explains the observed empty list. Cockpit GUI rendering still not exercised.

### Full VPS reboot — 2026-10-09 — PASS

User explicitly authorized a full host reboot to verify persistence. Captured the **current VPS data**, including their subsequent account changes, rather than reusing the deployment snapshot. Paused application access for a coherent comparison. Stopping the frontend propagated a full-stack stop through existing target dependencies; the initial attempt to execute a checker in the stopped backend therefore failed. Started PostgreSQL only and ran a transient backend-image tool container, with no API server, to capture a repeatable-read, read-only fingerprint of **every public table**, including sessions/schema metadata, plus reference-sequence state. No business edits or fabricated test ideas/accounts were created. The transient tool exited before reboot.

Fresh baseline: **5 accounts, 6 account events, 2 ideas, 27 idea events, 6 plans, 24 plan-period rows, 1 result period, 1 task, 1 comment, 1 location, 1 category, 1 stored session, 0 demo batches, schema 0005**. Reference sequence **206 / is_called=true**. Account fingerprints include their password hashes and access state. Saved a fresh private custom-format backup **/home/ideaflow/backups/ideaflow-20261009T220252Z.dump** before scheduling `shutdown -r +1`.

Full machine reboot scheduled for **2026-10-09 22:03:52 UTC / 18:03:52 America/New_York**. Previous boot ID **48d8228e-9c49-4249-9bb8-5ef39311bc0b**; new boot ID **9324cb38-337f-4bdb-b7b5-d15481d18203** and uptime under one minute proved a host reboot. SSH connections became unavailable during the scheduled shutdown and resumed at **18:04:25 Eastern**. Previous-boot journal confirms the dedicated user manager deactivated successfully at **18:03:54 Eastern**.

**Automatic startup passed:** no post-reboot start, restore, reset, migration-recovery or repair command was issued. PostgreSQL, backend and frontend recreated automatically from their pinned images and retained volume. **app-ideaflow.target active at 22:04:34 UTC / 18:04:34 Eastern**, with exactly three healthy containers. New container IDs begin **12197e909c53**, **025cc9d93659**, **7c53df998ede**. Recreated containers retained all information in PostgreSQL.

Ran `scripts/verify-vps-reboot.py` in the backend after automatic startup, before any new login. **PASS:** all 14 public-table row counts/fingerprints, account access state and reference sequence exactly equal to the pre-reboot snapshot. Private downloaded baseline and result files **local/vps-reboot-before-20261009.json** and **local/vps-reboot-after-20261009.json** have identical file SHA-256 **bf7a9731a9b4d8bbe14ddbac18181ec1362c16498d059c68e5481393fd8ec4a9**. Stored session row survived unchanged; its ordinary expiry rules remain in force. Lifecycle replay of both current ideas also passed after reboot.

**Post-reboot access passed:** `scripts/vps.ps1 app-check` authenticated the existing Admin password over certificate-validated public HTTPS, checked the Secure session cookie, current user, idea register and Portfolio/Value/Process endpoints, all successful. This login created one normal expiring session **after** the exact persistence comparison. Normal Users' hashes were verified by full-table equality; their private plaintext passwords were not available for separate login tests. Cockpit authentication through the SSH channel passed, and its actual helper lists IdeaFlow active under `ideaflow`. A new app-check import initially shadowed the global HTTP module in the Cockpit branch; corrected the tool import and reran Cockpit successfully. No runtime/application data change was needed.

**Host/services passed:** Caddy, Cockpit socket, UFW, Fail2ban and auditd active after reboot. Both host and dedicated user failed-unit lists empty. Application backup timer resumed, next observed trigger **2026-10-10 04:13:06 UTC**. Host listeners retain public Caddy 80/443/8443 and SSH, with frontend 18081 and management 9090/2019 on loopback only. Reconnect the user's SSH Cockpit tunnel after reboot; an existing terminal tunnel is not automatically restarted.

Downloaded the fresh pre-reboot backup to **backups/vps-ideaflow-20261009T220252Z.dump**, binary-safe and SHA-256 verified **530cd2ea07813c4d54c5fd2c2048c5d405cadf6dd9073b075e6db5340c09fb08** (42,593 bytes). The earlier deployment backup remains preserved. No database restore, volume deletion or reset was performed during this reboot test. Public application URL remains **https://vps-8104e6c8.vps.ovh.us:8443**. This subsequent check supersedes earlier statements that a full VPS reboot had not yet been exercised; it demonstrates restart persistence, not recovery from provider disk loss or VPS deletion.

# App Workshop generalization â€” 2026-10-11

Kept IdeaFlow at the repository root and retained its Compose project, account, volume, ports, scripts, Git history and GitHub remote. Added `workshop.json`, `apps/`, a clean three-service starter, containerized local/release tools, independent VPS deployment tools and `docs/APP_WORKSHOP.md`. Display name is App Workshop; filesystem/GitHub repository names are unchanged. No business/domain behavior changed. No sibling copy or nested Git repositories were created.

**Actual checks passed:**

- Discovered Rancher Desktop **Moby**, actual context **default**, Docker client 29.6.2-rd/server 29.5.3, Compose 5.3.1. Started the previously stopped Rancher Desktop executable without changing settings. Existing local IdeaFlow automatically returned healthy; final readiness remains `http://localhost:8080`.
- Six containerized workspace tests passed: clean generation, two-app identity/port separation, IdeaFlow catalog preservation, traversal/duplicate/collision/drift rejection, image archive configuration digests, private service bindings, separate Caddy route, generated shell syntax and injection/shared-storage rejection.
- Generated **workshop-check-a** and **workshop-check-b** only under gitignored `artifacts/workshop-check/`, using a separate test catalog. Both React/TypeScript/nginx frontend and FastAPI backend images built and both Compose projects reached exactly three healthy services at temporary ports 18881/18882. No sample app was registered in the real catalog or deployed to the VPS.
- Both starter backend test runs passed using unique temporary databases: unauthenticated access rejection, sign-in, empty notes, CSRF enforcement, create/edit plus append-only transactional events, stale-version conflict, history deletion rejection, and sign-out. Additional explicit foreign-Origin rejection passed for app A.
- Pinned Playwright 1.55.1 container exercised login, initial empty workspace, saving an ordinary isolated note, reload, two apps on the same browser hostname with distinct cookies, and logout. Desktop 1440Ã—900 and mobile 390Ã—844 fit without horizontal overflow. Reviewed the mobile screenshot at `artifacts/workshop-check/starter-mobile.png`. Browser test rewrites the request Origin to the configured localhost origin because its network entry uses `host.docker.internal`; production checks below use the actual external origin.
- App A ordinary `down` followed by `up --build` recreated containers while retaining the same named database volume and the saved note. Post-rebuild browser reload/persistence/session checks passed. Both apps passed full public-table fingerprint equality against isolated custom-format backup/restores. App A also produced a binary-safe private backup and a reviewable image-pinned VPS release **6391113f0888** without VPS mutation.
- Git ignore checks passed for nested `.env`, `.env.production`, archives, backups and node_modules. Root `.git`/origin/main remain intact; GitHub remote main was reachable. `git diff --check` passed (informational Windows line-ending notices only).
- Before/after **VPS business-table fingerprints and lifecycle replay matched** using the existing read-only checker and private `/handover/workshop-before-20261011.json` and `workshop-after-20261011.json`. Existing container IDs **12197e909c53 / 025cc9d93659 / 7c53df998ede** stayed unchanged and healthy, with 42 hours uptime; no failed host units. Public certificate-validated HTTPS login with existing Admin credentials, Secure cookie, register (**2 ideas**), Portfolio/Value/Process and readiness all passed at **https://vps-8104e6c8.vps.ovh.us:8443**. The ordinary login was performed after the preservation comparison and created an expiring session.

**Failures fixed / limitations:** Initial native esbuild executable locking and Vite transform stalls required a temporary in-memory build directory and IdeaFlow's existing no-minification/no-tree-shaking configuration; corrected starter builds passed. npm downloads intermittently returned ECONNRESET, including a browser dependency install; retries and a minimal pinned Playwright dependency succeeded. An initial cross-app browser check ran before app B was ready, then passed after both readiness checks. No engine/configuration resets or volume removal were used.

The new generic VPS installer was reviewed and its generated shell/release validation tested, but **was not executed against the VPS**: there is no newly requested completed product to publish. Its fresh-install/update/reboot/Cockpit/backup behavior must be verified for the next actual app. Existing IdeaFlow's previously verified VPS reboot evidence remains applicable only to IdeaFlow. Starter notes are a development surface, not a finished business app; app-specific roles/migrations, failed-login protection and account management need implementation before production. Deployments start fresh; copying local data requires a separate verified handover. Daily backup jobs retain files indefinitely, so monitor disk and configure retention/off-host destinations per app. No automatic capacity controller or arbitrary-schema rollback was added.

Verification app A/B stacks were stopped with project-specific ordinary Compose down after checks; their volumes/backups remain preserved. Final local container listing contains only the original three healthy IdeaFlow containers. No test records were added to IdeaFlow. Changes were staged explicitly; staged whitespace checks and nested secret/artifact exclusion passed. A normal fast-forward GitHub push includes the previously existing local VPS commit 5001941 as well as this workspace change; no force push or history rewrite.
