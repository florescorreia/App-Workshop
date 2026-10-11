> Document status: dated reference evidence. Counts, imported links, runtime state and old role names describe the recorded run; they are not a current workspace inventory. Current User/Admin behavior and command locations are in [README.md](README.md). Local scripts run from `apps/ideaflow/` after deliberate staging. No fictional import is part of startup, documentation review or deployment.

> Historical evidence: the live workspace was explicitly emptied on 2026-10-09. These idea links/counts and role labels describe the archived showcase, not current live data. Use [UX_WALKTHROUGH.md](UX_WALKTHROUGH.md) for the new two-role experience.

# HarborWorks live import evidence

Explicitly authorized additive import executed **2026-10-07**, anchor **2026-10-07** in the running application's **America/New_York** timezone. Batch **harborworks-demo-v1**, seed **42**. URL **http://localhost:8080**, verified Rancher Desktop Moby context **default**, production project **ideaflow**. Only frontend, backend and postgres run permanently. Data remains in **ideaflow_pgdata**; no reset, volume removal or existing-record overwrite occurred.

Commands actually executed:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 doctor
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 seed-demo -DryRun -BatchKey harborworks-demo-v1 -Seed 42 -AnchorDate 2026-10-07
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 seed-demo -BatchKey harborworks-demo-v1 -Seed 42 -AnchorDate 2026-10-07
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 seed-demo -BatchKey harborworks-demo-v1 -Seed 42 -AnchorDate 2026-10-07
docker --context default compose exec -T backend python -m app.reconciliation
docker --context default compose cp scripts/verify-showcase.py backend:/tmp/verify-showcase.py
docker --context default compose exec -T -e PYTHONPATH=/app backend python /tmp/verify-showcase.py
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/browser-showcase.ps1
```

Before import: **0 ideas, 0 events, 0 batches, 1 bootstrap Admin**. The existing Admin's full row fingerprint remained unchanged. Dry run validated all histories through the domain importer and left every business-table count/SHA-256 fingerprint identical. Commit created **60 ideas, 747 events, 25 tasks, 60 comments, 91 plan versions, 31 approved snapshots, 558 plan periods and 87 actual periods**. **61 periods** are verified; **26** await Finance. Three fictional role accounts were added without changing the Admin. Generated credentials remain private in gitignored `local/harborworks-demo-v1-credentials.json`.

The second committed invocation returned **no_op: true** and “Batch already exists. No records changed.” All nine business-table fingerprints remained identical. Full commit manifest is preserved privately as `local/harborworks-import-manifest.json`; the preview, no-op and detailed read-only verification reports are also in `local/`. Dry-run reference gaps are normal: committed records are **IF-00121–IF-00180**.

| Lifecycle stage | Cases |
| --- | ---: |
| New | 5 |
| Screening | 11 |
| Analysis | 13 |
| Approved | 6 |
| Implementation | 8 |
| Validation | 5 |
| Realized | 12 |

Dispositions: **46 Active, 5 On hold, 6 Rejected, 3 Cancelled**. Rejected/Cancelled cases retain their lifecycle stage. There are **13 overdue active initiatives**, **8 cases with backward rework** and **14 observed variants**. Sites: **Tampa 21, Atlanta 19, Dallas 20**. Created dates range **2025-05-07 through 2026-06-11**, within the previous 18 months; imported events stop no later than the anchor timestamp. No future actuals or future historical occurrences exist. Every imported event retains fictional/batch/seed/anchor provenance and separate recorded time.

Read-only checks passed event ordering and contiguous case sequences, valid transition pairs, stage-preserving holds/resumes, full current-state replay, stage/disposition/site counts, approved snapshots for advanced cases, elapsed results, hero states and preservation. Process shows a plausible Analysis bottleneck: **42 completed Analysis visits**, **222.5-day median**, **266-day p90**, **10 open visits**, and **5 currently held over 30 days**. Other completed medians: New 7, Screening 10, Approved 7, Implementation 61, Validation 61 days. Open visits are excluded from completed medians.

Independent Decimal sums reconciled the authenticated dashboard responses for **January–December 2026**:

| Metric | USD / result |
| --- | ---: |
| Annual net potential | $4,318,480.00 |
| Approved horizon net benefit | $1,194,619.94 |
| Planned project spend | $739,000.00 |
| Planned net cash flow | $455,619.94 |
| Planned ROI / cash payback | 61.7% / October 2026 month-end |
| Reported net benefit | $280,337.23 |
| Finance-verified net benefit | $195,778.87 |
| Expected for matched reported cohort | $276,460.02 |
| Expected for matched verified cohort | $193,506.64 |
| Coverage through September | 87 / 129 eligible idea-months reported; 61 verified |

Unreported period values and unverified amounts were checked to remain null/Unknown. Actual cash flow is **−$360,662.77**: implementation spend is already incurred while benefits ramp up. Working-capital cash release stays in narrative rather than recurring-benefit sums.

Containerized Chromium **1 passed in 29.7 seconds** on the actual live app. Overview, register, Pipeline, Process, Value and Financials were reviewed at **1440×900**, **1280×720** and **390×844**, with no page-wide overflow or page errors. Tests exercised retained Tampa filters, process drilldown, all five hero records and provenance History, an unsaved create form, Manager assignment/approval controls and Finance review. External requests were blocked. The Finance dialog was opened and closed without committing a sign-off; no idea, task, actual or verification was changed. Screenshots are private local evidence in `artifacts/showcase-*.png`.

[DEMO_GUIDE.md](DEMO_GUIDE.md) uses actual committed hero references and a ready unverified September period on **IF-00124**. Presenter actions are future live actions; they were not committed by this browser review. The verification helper expects this import's private snapshots and unchanged business rows; it is evidence for this import, rather than an ongoing check after presenter writes. Final health and backup evidence are recorded in [VERIFICATION.md](VERIFICATION.md).

Post-import custom backup **backups/ideaflow-20261007-192449.dump** passed isolated restore verification with matching full row fingerprints for all nine business tables. Live data was unchanged and only the temporary restore database was removed. Final HTTP readiness reports **ready / 1.0.0**; frontend, backend and postgres are healthy with only loopback port 8080 published.
