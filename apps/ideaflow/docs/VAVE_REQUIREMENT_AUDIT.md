# Differential VAVE requirement audit — release 1.2

The complete supplied DOCX was read, including release priorities and A1–A9. Its first release explicitly requires FR01–FR14 and FR16–FR20 at a practical minimum. Accepted implementation choices are in [VAVE_DELTA.md](VAVE_DELTA.md); newer user-authorized adoption/design choices are in [PRD.md](PRD.md). This audit describes implemented behavior, not MINDcan product parity or sponsor acceptance.

| Requirement | Delivered practical minimum | Verification evidence |
| --- | --- | --- |
| FR01 | Program objective/sponsor/client/scope/horizon/currency, cadence, rules, thresholds, decision team and mandatory evidence | Program governance and target tests; browser setup |
| FR02 | Product family/product/assembly, part/revision, plant/supplier/commodity/region/cost category; distinct applications; target allocations | Structured-filter and scoped-report tests; two-plant adoption rehearsal |
| FR03 | Unassigned submission, owner/action/date at M1; program memberships, external boundaries, independent review | A1, A9 and independent-verification tests; ownership notices |
| FR04 | Minimal capture, unknown values, stable reference, current/future condition, files and discussion | Capture/browser attachment journey; adoption preservation test |
| FR05 | PRD categories, content/part/supplier search, structured filters, sort/group, saved personal views, duplicate/surviving links | Register/export/filter tests; superseded duplicate remains retained/excluded |
| FR06 | Sequential M0–M6 with missing prerequisites, explicit reasoned requests/reviews/advance and snapshots | A1/A2 gate tests; browser blocked gate and M1 |
| FR07 | Separate maturity/activity/schedule, holds/rework/dispositions/lessons, material-change reapproval, partial rollout | A6/A8, disposition and approval-invalidation tests |
| FR08 | Comparable cost/units/usage/conversion, native currency/rate, volume/monthly timing, low/base/high, recurring offsets, cash/payback | A3/A4 exact calculations, unknown/negative economics tests |
| FR09 | Separate value types and operational metrics, givebacks/sharing/offsets; capacity mechanism required | Value-type/calculation/report tests |
| FR10 | Selected overlap controls, duplicate/parent exclusions, rate basis and separate opportunity/forecast/verified | A5/A9 reconciliation and alternative-exclusion tests |
| FR11 | Actual quantity/cost/evidence/variance, elapsed defined observation periods, independent signoff/revocation and corrections | A7/A8; application-owner denial and invalid-period atomicity |
| FR12 | Required actions/owners/dates/costs/dependencies/evidence, per-application Planned/Released/In production | A6 rollout and dependent-action tests |
| FR13 | Risk severity/likelihood/mitigation/owner/date, mandatory functional evidence and critical-risk block | A2; rehearsal bracket intentionally blocked before M3 |
| FR14 | Discussion/mentions/meeting decisions, work/review queues, assignment/return/change/deadline notices, routine preferences and Manager exceptions | Notices/preferences/work tests and meeting views |
| FR16 | Transactional append-only events, optimistic versions, snapshots, preserved IDs/old evidence, archival dispositions | A8, adoption preview/concurrency, backup/rebuild and replay checks |
| FR17 | Register/board, structured product/part applications, full detail, My VAVE work, program/finance/leadership/meeting views | Browser desktop/mobile journey; Viewer report permissions |
| FR18 | Metric/currency/horizon/scope/freshness, snapshot date, supporting applications/exclusions, scoped targets, maturity/cohort/gate time | A9; scoped reporting and unknown-value tests; report browser drill-down |
| FR19 | Retained savings/spend/payback/timing plus effort/resource/risk and reasoned priority; selected alternatives | Financial calculations, priority sorting/reasons and overlap tests |
| FR20 | Guided capture-field CSV mapping, duplicate/error preview, exact confirmation/idempotency, authorized filtered export/print pack | Import/idempotency/boundary/export tests |

A1–A9 run in isolated containerized tests. Public production checks are read-only apart from ordinary sessions and generated in-app notices. The authorized two-record conversion is a separate explicit, audited operator action, rehearsed on a fresh isolated production copy before application.

Limits: FR15 broader replication, generalized knowledge publication, richer resource/scenario optimization, assisted discovery, QR intake and operational integrations are subsequent-release scope per the DOCX. Reuse links preserve concept relationships but do not copy approvals. Gates are fixed/default sequential; program evidence/reviewer/threshold rules are configurable, with no fast-track or independence bypass. Escalation uses the configured cadence/stale thresholds, due dates, blockers and Manager queue rather than an arbitrary rule engine. Notifications are in-app. Financial classification, exchange rates and overlapping scopes require explicit human inputs. Actual corporate pilot participation, sponsor acceptance and real savings remain business activities; illustrative test records assert none of them.

Actual command results, deployment identifiers and preservation checks are recorded in [VERIFICATION.md](VERIFICATION.md).
