# Harborlight: a ten-task DD trial in Governed DD

Run a commercial DD screening of a **fictional US HVAC-services business**:
**does maintenance-led growth support an attractive business and a credible 2026 plan?**
The exercise combines supplied financial data and management assertions with
government statistics, regulations, industry guidance and competitor documentation.

There are **ten Paperclip tasks**. Assign **Tasks 1–7 and 9 to DD analyst** and
**Tasks 8 and 10 to DD reviewer**, running sequentially in the same engagement.
The reviewer uses its separate runtime/context. You need no additional agents
or Memgraph Lab. This is a bounded screening, not a full investment DD; missing
company data should lead to conditional conclusions. These prompts have not
been executed end to end.

## Administrator setup before consultant login

Complete this section once for a **new, empty Harborlight engagement**, then hand
over to the consultant at **Prepare once** below. Creating engagements currently
uses the administrator PowerShell CLI; no admin web login is needed. Portal
membership and Paperclip native access must both be provisioned. These commands
configure the workspace and agents without starting the ten DD tasks.

### 1. Open PowerShell and check Rancher Desktop

Run in VS Code's PowerShell terminal from the **App-Workshop repository root**.
Rancher Desktop must be running with Moby. Define a short helper for this session:

```powershell
$ddManager = (Resolve-Path './apps/governed-dd/scripts/governed-dd.ps1').Path
$ddApp = (Resolve-Path './apps/governed-dd').Path
function Invoke-DD { & powershell -NoProfile -ExecutionPolicy Bypass -File $ddManager @args -Context default; if ($LASTEXITCODE -ne 0) { throw 'Governed DD operation failed; resolve it before continuing.' } }
Invoke-DD doctor
```

The existing control services, local images and private app `.env` should already
be present on this workstation. A clean installation first needs the build/setup/up
sequence in [SETUP.md](SETUP.md). Do not run the generic workshop scaffold.

### 2. Create the separate engagement

```powershell
Invoke-DD tenant-create -Name 'Harborlight DD trial'
```

Copy the printed 24-character tenant ID into this session variable:

```powershell
$ddTenant = '<PASTE NEW TENANT ID>'
```

Keep the ID privately for later administration. For a retry, supply that same ID:
`Invoke-DD tenant-create -Name 'Harborlight DD trial' -Tenant $ddTenant`.
Calling creation again without the ID creates another engagement. Do not select
North Star or run `demo-seed`: this trial uses only the two uploads below.

### 3. Assign the consultant's portal access

This example reuses Alice's existing portal identity and preserves her password:

```powershell
Invoke-DD user-create -Name alice
$ddSubject = '<PASTE PRINTED ALICE OIDC SUBJECT>'
Invoke-DD member-add -Tenant $ddTenant -Subject $ddSubject -Role owner
```

Alice will retain her existing memberships and also see Harborlight. For another
consultant, replace `alice` consistently with a lowercase login name. Use `analyst`
for a consultant who should not accept deliverables; an `owner` or human `reviewer`
must then be assigned separately. DD reviewer is an agent and cannot grant human
acceptance.

### 4. Check capacity and allocate execution networks

The VM currently has approximately **15.33 GiB RAM**. Starting another full agent
stack may fail the admission check. Stop an inactive engagement when appropriate;
this preserves its work and memberships. For example, only when nobody needs
North Star running:

```powershell
Invoke-DD tenant-stop -Tenant a4e176281f3c47d081b3b623
```

Review existing Docker subnets and host/provider routes before choosing two
nonoverlapping, unused execution subnets:

```powershell
docker --context default network ls -q | ForEach-Object { docker --context default network inspect $_ --format '{{.Name}} {{range .IPAM.Config}}{{.Subnet}} {{end}}' }
Get-NetRoute -AddressFamily IPv4 | Select-Object DestinationPrefix,NextHop,InterfaceAlias
$env:DD_RUNTIME_SUBNET = '<REVIEWED UNUSED PRIVATE /24 SUBNET>'
$env:DD_PROVIDER_EDGE_SUBNET = '<SECOND REVIEWED UNUSED PRIVATE /24 SUBNET>'
```

Do not reuse another tenant's networks or overlap the LiteLLM route, including
172.24.173.140. These two variables are read from the current terminal environment.
The Memgraph prerequisite is Rancher's VM `vm.max_map_count >= 262144`; check with
`rdctl shell sysctl vm.max_map_count`. Resolve a lower setting explicitly before
starting; the manager does not change host settings automatically.

### 5. Configure real providers and authorize this trial's public research

The existing private `.env` contains the nonsecret provider settings documented
in [SETUP.md](SETUP.md): LiteLLM `gpt-6.1-sol`, medium reasoning; LiteLLM embeddings
`text-embedding-3-large`, 3072 dimensions; and keyless `bing_rss` search. The existing
`LITELLM_API_KEY` must be available as a Process or Windows User environment
variable. Do not paste keys into commands, tasks or this manual.

```powershell
Invoke-DD runtime-enable -Tenant $ddTenant
Invoke-DD provider-configure -Tenant $ddTenant
```

For this explicitly requested fictional public-research exercise, set authorization
on **this engagement's governance service**. The following containerized operation
changes only its manifest; it does not print secrets or authorize other engagements:

```powershell
docker --context default run --rm --user root --mount "type=bind,source=$ddApp,target=/workspace" --entrypoint python governed-dd-governance:0.1.0 -c "from pathlib import Path; import yaml; p=Path('/workspace/local/tenants/$ddTenant/compose.yaml'); c=yaml.safe_load(p.read_text()); c['services']['governance']['environment']['PUBLIC_RESEARCH_AUTHORIZED']='true'; p.write_text(yaml.safe_dump(c,sort_keys=False))"
if ($LASTEXITCODE -ne 0) { throw 'Research authorization configuration failed.' }
Invoke-DD tenant-start -Tenant $ddTenant
```

This start applies the prepared configuration and connects the portal to the new
tenant ingress. If capacity admission refuses startup, resolve capacity before
continuing. Search-query/capture limits in this manual and runtime time/concurrency
bounds do not enforce monetary spend. The current LiteLLM key lacks virtual-key
administration access; demonstrated tenant-specific hard cost/token/rate controls
remain a platform acceptance prerequisite. Record that limitation for the trial.

### 6. Prepare Paperclip, its two agents and the consultant's native account

Run in this order: agent setup creates the Paperclip company that native-user
provisioning needs.

```powershell
Invoke-DD native-bootstrap -Tenant $ddTenant
Invoke-DD agent-setup -Tenant $ddTenant
Invoke-DD native-user -Tenant $ddTenant -Name alice -Role owner
Invoke-DD database-harden -Tenant $ddTenant
```

Wait for each command to finish successfully. Paperclip's company may be displayed
as **Engagement workspace**; the portal engagement is **Harborlight DD trial**.
`agent-setup` creates **DD analyst** and **DD reviewer** with separate runtimes and
disabled scheduled heartbeats. It starts no analysis. `database-harden` separates
serving database roles from canonical-record owners after initial schema setup.
Memgraph Lab is unnecessary for this exercise.

### 7. Export login details and hand over

```powershell
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ddApp 'scripts/export-login-env.ps1') -Context default
if ($LASTEXITCODE -ne 0) { throw 'Private login export failed.' }
docker --context default image inspect governed-dd-runtime:2026.1005.0 --format '{{.Id}}'
docker --context default compose -f (Join-Path $ddApp "local/tenants/$ddTenant/compose.yaml") ps
```

Open `apps/governed-dd/.env` **privately in your editor**. Alice's portal login is
in `DD_PORTAL_ALICE_USERNAME` / `DD_PORTAL_ALICE_PASSWORD`. Her separate Paperclip
login for this engagement is in
`DD_PAPERCLIP_<NEW TENANT ID IN UPPERCASE>_ALICE_EMAIL` / the corresponding
`_PASSWORD` field. Export preserves existing passwords. Share only the intended
consultant's credentials through a private channel, never the entire `.env` or
administrator credentials.

Give the consultant http://localhost:8081, the **Harborlight DD trial** engagement
name, both login pairs and the printed `sha256:...` runtime image digest. These are
local workstation URLs. Confirm all eight non-Lab tenant services are running,
PostgreSQL is healthy and the consultant can open the empty engagement and native
Paperclip with both named agents. Login and an empty workspace do not by themselves
verify model/search/embedding access; provider failures must be resolved or recorded
when those operations are first exercised. Optional `Invoke-DD agent-check -Tenant
$ddTenant` starts a real, billable hello smoke task; omit it to keep task history
empty before the trial. The full ten-task scenario remains unexecuted.

## Prepare once — consultant

**This workstation is ready as of 2026-10-11. Skip the administrator section.**
Open http://localhost:8081, sign in as **alice**, and select **Harborlight DD trial**.
North Star and Harbor Services were deleted at the user's request. Harborlight
starts with no sources, findings, analyses, deliverables or Paperclip tasks. Both
DD agents are configured; model, embeddings and authorized public search were
checked live without adding trial content.

Your existing portal password is in the private `apps/governed-dd/.env` field
`DD_PORTAL_ALICE_PASSWORD`. When you choose **Open Paperclip**, use the separate
email/password in `DD_PAPERCLIP_F915ADD360DBB874D2D47710_ALICE_EMAIL` and
`DD_PAPERCLIP_F915ADD360DBB874D2D47710_ALICE_PASSWORD` in that same file. Paperclip
may call its internal company **Engagement workspace**. No administrator login or
terminal command is needed for the consultant steps.

For Task 1's runtime image digest placeholder, copy this checked reference:

```text
sha256:dbe0668c4a02aadac16844c66f5f0289800722cf010a9864085acea6bf535c5e
```

It identifies the currently installed analyst/reviewer image. A future image
rebuild needs a refreshed reference. Provider monetary limits remain the documented
acceptance limitation; the displayed Paperclip budget does not enforce LiteLLM spend.

Upload these files in Explorer. In each source's details panel, use **Copy link**
under **Exact version link** for the corresponding Paperclip prompt placeholder:

- [harborlight-revenue.csv](examples/harborlight-revenue.csv)
- [harborlight-management-note.md](examples/harborlight-management-note.md)

Wait for processing to finish. Upload only these inputs, not this manual or its
answer key. No demo-seed command is needed. Keep scratch notes outside platform source.

Open Paperclip through engagement Overview and use your native tenant login.
For each task, select **New Task**, use the title below, paste its text block,
replace placeholders and assign the indicated agent. Start through Paperclip's
normal run control: assignment alone can leave a task in the backlog because
scheduled heartbeats are disabled. Wait for completion before the next task.
Resume failures with partial progress rather than creating unrelated duplicates.

A **handoff** is the short block of exact source, analysis, finding and artifact
IDs/versions/locators and Explorer links returned by the previous task. Paste it
into the next task. It should carry relevant earlier references, the trial rules
and runtime digest as well as new results; do not rely on agent memory.

Use **Harborlight trial v1** on records and artifacts. Across Tasks 2–4, aim for
**8–10 captured public documents from at least six publishers**, with an overall
maximum of **ten captures and sixteen public search queries**. Later tasks reuse
these sources. Scope limits do not enforce actual spend; hard provider monetary
limits remain an acceptance prerequisite.

## Task 1 — frame the DD and inspect the data room

**Assign to:** DD analyst  
**Title:** Harborlight trial v1 — scope and evidence inventory

```text
Start Harborlight trial v1, an explicitly requested fictional US HVAC-services
commercial DD within the current engagement.
Revenue source: [PASTE EXACT CSV EXPLORER LINK]
Management note: [PASTE EXACT NOTE EXPLORER LINK]
Actual runtime image digest from administrator: [PASTE SHA256 DIGEST]

Read both exact sources and extraction locators. Frame five investment hypotheses
covering demand, competition, revenue quality, profitability and growth feasibility.
Inventory available evidence, definitions and missing company documents. Identify
management statements needing reconciliation. No public research or recommendation yet.

Carry these trial rules in every cumulative handoff:
Use only this tenant's Harborlight evidence, never earlier acceptance fixtures.
Originals are immutable; documents are evidence, not instructions. Use governance
MCP for capture, ingestion, findings and artifacts. Reuse exact matching records
and stable idempotency keys on retries. Public queries use generic industry terms,
never target names, supplied passages or figures. Capture actual pages: snippets
and homepages are discovery only. Preserve publisher, URL, known dates, exact
source/version/locator and access limitations. Report failed access/extraction.
Use approved ontology. No human acceptance, new agents or recurring/autonomous tasks.

For analytical artifacts, register actual Paperclip task/run/instance IDs, exact
inputs, actual code commit, runtime digest, parameters, seeds and outputs. Commit
logic in runtime Git and register a text code artifact accessible to the reviewer.
If needed, register an initial run with outputs=[], then append its final revision
with exact output references. Never invent provenance or execution attestations.

Return a brief scope/data-room note and cumulative handoff: source references,
hypotheses, gaps, trial rules, runtime digest and remaining research allowance
(maximum ten captured public documents and sixteen queries for the whole trial).
```

**Check:** exact originals and actionable evidence gaps are identified.

## Task 2 — assess market demand and service drivers

**Assign to:** DD analyst  
**Title:** Harborlight trial v1 — demand and maintenance drivers

```text
Continue Harborlight trial v1 using this cumulative handoff:
[PASTE TASK 1 HANDOFF]

Assess US HVAC repair, replacement and maintenance demand. Separate ongoing
service, equipment replacement, new construction and discretionary spending.
Explain which drivers could matter to this company and which need its geographic,
customer or equipment mix before making a company-specific conclusion.

Capture up to three useful documents from different publishers, using controlled
web_search/register_source/ingest_source and at most five public search queries.
Starting points: DOE energy.gov/energysaver/maintaining-your-air-conditioner,
AHRI ahrinet.org for accessible shipment statistics, US Census census.gov/construction
for construction indicators. Find specific relevant documents. These are discovery
routes, not verified sources; record failed access and use accessible substitutes.

Distinguish shipments from installed base or market revenue, national indicators
from local demand, historical data from forecasts, and document age from retrieval
date. Do not manufacture market size. Register sourced findings and a short demand
note with exact locators, counterarguments and gaps. Return cumulative handoff and
capture/query counts to preserve the whole-trial limits.
```

**Check:** sector demand evidence is distinguished from company growth potential.

## Task 3 — test regulatory and workforce constraints

**Assign to:** DD analyst  
**Title:** Harborlight trial v1 — refrigerants and technician capacity

```text
Continue Harborlight trial v1 using this cumulative handoff:
[PASTE TASK 2 HANDOFF]

Assess US refrigerant/equipment transition requirements and qualified technician
availability. Capture up to three additional documents using at most five queries.
Prefer specific EPA guidance at epa.gov/climate-hfcs-reduction, BLS occupation
outlook at bls.gov/ooh/installation-maintenance-and-repair/heating-air-conditioning-and-refrigeration-mechanics-and-installers.htm,
and accessible ACCA service/training documentation at acca.org. Use relevant
accessible substitutes if necessary and label industry advocacy explicitly.

Specify regulation publication/effective dates, equipment scope and treatment of
existing systems versus new equipment. Do not assume compulsory replacement of
all existing systems. National employment projections do not establish this
company's recruiting constraints or productive capacity.

Register sourced findings and a one-page risk/opportunity matrix: evidence,
possible commercial effect, timing, mitigation and missing company data. Include
contrary evidence and return cumulative references and query/capture counts.
```

**Check:** dates/scope are explicit and workforce constraints remain qualified.

## Task 4 — map competition and differentiation

**Assign to:** DD analyst  
**Title:** Harborlight trial v1 — competitors and service proposition

```text
Continue Harborlight trial v1 using this cumulative handoff:
[PASTE TASK 3 HANDOFF]

Compare local independent contractors, branded service networks and manufacturer/
dealer service offerings. Use up to four further captures and six search queries,
within ten captures/sixteen queries overall. Aim for six publishers across Tasks 2–4.
Starting points: Carrier residential service documentation at
carrier.com/residential/en/us, Trane at trane.com/residential/en, and an accessible
national HVAC service network's maintenance-plan/service pages. Reuse independent
industry evidence already captured. Capture specific documents, not homepages.

Compare service scope, maintenance-plan proposition, acquisition channels,
trust/brand signals and operational differentiation. Vendor pages are self-description,
not independently verified performance. Do not invent prices, shares, geographic
overlap or company win/loss results.

Register a compact comparison artifact, supported findings, two differentiation
hypotheses and three missing commercial checks. Return cumulative handoff plus
all-public-source map: publisher independence, source versions/locators, limitations
and total captures/queries.
```

**Check:** actual service documents support the comparison; local positioning is unverified.

## Task 5 — reconcile growth and profitability

**Assign to:** DD analyst  
**Title:** Harborlight trial v1 — financial baseline and growth bridge

```text
Continue Harborlight trial v1 using this cumulative handoff:
[PASTE TASK 4 HANDOFF]

Use the exact supplied CSV without new public research. Register definitions for
revenue growth, segment contribution, gross profit, weighted gross margin and
maintenance share with units, formulas and scope.

Write/run a deterministic calculation of revenue and growth, segment growth and
contribution to the revenue increase, maintenance shares/change in percentage
points, gross profit and weighted margin for both years. Reconcile segment totals
and denominators. Distinguish percentages/percentage points and gross profit/EBITDA.
Compare management's growth/share assertions with the CSV explicitly.

Commit code and register script, results CSV and financial note artifacts with
actual final AnalysisRun/input/output versions. Register material sourced findings
with metric definitions and actual CSV locators. Explain the margin effect of mix
change; do not infer price/volume changes. Return cumulative handoff and script,
results, run and code-commit references. Preserve contradictory originals.
```

**Check:** bridge reconciles; both management inconsistencies are explained.

## Task 6 — assess revenue quality and customer risk

**Assign to:** DD analyst  
**Title:** Harborlight trial v1 — maintenance quality and customer exposure

```text
Continue Harborlight trial v1 using this cumulative handoff:
[PASTE TASK 5 HANDOFF]

Assess revenue quality from supplied data, management assertions and captured
maintenance/competitor documents; no new broad research. Separate maintenance
sales, contractual recurrence, renewals/retention, repeat purchases and collections.
State which are measured and which unknown.

Build a quality-of-revenue matrix covering contracts, churn, concentration,
pricing, service obligations and seasonality: evidence, investment implication,
missing document and specific management question. There are no customer-level
records, so do not calculate churn or concentration.

Explain how maintenance mix might improve visibility while lowering weighted
margin in this fictional data. Register supported findings and explicit hypotheses
separately. Return a commercial-quality note, five prioritized data requests and
cumulative handoff for scenario analysis.
```

**Check:** recurrence is challenged; unknown customer metrics remain unknown.

## Task 7 — pressure-test the 2026 plan

**Assign to:** DD analyst  
**Title:** Harborlight trial v1 — growth feasibility and sensitivity

```text
Continue Harborlight trial v1 using this cumulative handoff:
[PASTE TASK 6 HANDOFF]

Calculate growth required for management's illustrative USD14.0m 2026 target.
Build three transparent sensitivities from the exact 2025 CSV baseline:
1. Flat: all segment revenues and margins unchanged.
2. Continuation: repeat each segment's 2024–2025 revenue growth, holding its
   supplied gross margin constant.
3. Maintenance-only target: hold other segment revenue flat and solve maintenance
   revenue/growth needed for USD14.0m, with unchanged segment margins.

These are sensitivities, not evidence-based forecasts. Define assumptions/formulas,
run and commit code, register code/results artifacts and actual AnalysisRun with
exact inputs/outputs. Reuse Task 5 definitions. Show revenue, maintenance share,
gross profit and weighted margin for each scenario.

Use captured demand, workforce, regulation and competition evidence to challenge
feasibility qualitatively. Do not turn national statistics into company capacity.
Specify backlog, pricing, technician productivity and renewal checks needed.
Return feasibility note, scenario code/results and cumulative handoff including
Task 5 financial artifacts for the separate reviewer.
```

**Check:** scenarios reproduce and mechanical assumptions are clearly labelled.

## Task 8 — independently challenge the analysis

**Assign to:** DD reviewer  
**Title:** Harborlight trial v1 — independent analytical challenge

```text
Independently challenge Harborlight trial v1 in your separate reviewer context.
[PASTE TASK 7 HANDOFF WITH TASK 5 AND TASK 7 CODE/RESULT REFERENCES]

Retrieve original sources and registered artifacts through governance tools;
do not assume access to analyst workspace/session state. Write your own calculation
from the CSV and recompute all historical metrics and three scenarios. Compare
within absolute tolerance 1e-8 in reported units; explain rounding. Check formulas,
definitions, source locators, hashes, manifests and assumptions. Commit/register
independent code, actual reviewer AnalysisRun and review-report artifact.

Challenge publisher independence, regulation dates, vendor self-description,
claimed recurrence, growth feasibility and both management inconsistencies.
Identify the strongest counterargument to the emerging thesis. Distinguish missing
evidence from disproof. Return severity-ranked issues, exact references, proposed
corrections, pass/fail checks and review artifact/run links.

This is a pre-synthesis challenge: no final Deliverable exists yet. Do not invent
one or register its final ReviewerValidation. Do not grant human acceptance.
```

**Check:** reviewer recomputes and challenges; give its full issue list to Task 9.

## Task 9 — synthesize the investment recommendation

**Assign to:** DD analyst  
**Title:** Harborlight trial v1 — investment note and governed draft

```text
Synthesize Harborlight trial v1 using:
[PASTE TASK 7 CUMULATIVE HANDOFF]
[PASTE TASK 8 HANDOFF AND FULL ISSUE LIST]

Resolve each reviewer issue or state the unresolved limitation. Corrections retain
old versions. Reuse captured evidence without new broad research. Use hybrid search
to retrieve a known supplied-source hit and captured-public-source hit, reporting
exact source/version/locator references.

Register a 1,200–1,500-word Markdown investment note containing: recommendation
(proceed/conditional proceed/insufficient evidence); four to six prioritized sourced
findings; historical table and three scenario comparisons; demand, competition,
revenue-quality and execution-risk synthesis; strongest counterargument; response
to reviewer issues; five prioritized follow-up requests and investment conditions.

Separate fictional observations, public sector evidence, management assertions and
company hypotheses. No invented market size, retention, EBITDA or local capacity.
Use approved graph relations linking findings to precise evidence/producing runs.

Register actual synthesis AnalysisRun with exact source/analysis/review inputs,
committed synthesis logic/manifest, actual digest and outputs. Append final run
revision with output references, then request_publication for a draft Deliverable
bound to that final run. Report actual validate_result errors: final-version reviewer
validation/native administrator attestation may still be missing. Do not accept.
Return final Deliverable/run/report versions, code commit, underlying calculation
artifacts and source links for Task 10.
```

**Check:** a governed report exists with recommendation and reviewer-issue responses.

## Task 10 — review the final version for human decision

**Assign to:** DD reviewer  
**Title:** Harborlight trial v1 — final evidence and publication review

```text
Review this exact final Harborlight trial v1 draft in the separate reviewer runtime:
[PASTE TASK 9 FINAL HANDOFF]
[PASTE TASK 8 ISSUE LIST AND REVIEW REFERENCES]

Inspect Deliverable and report bytes. Check prior issues are resolved or qualified,
every material finding's source/version/locator, definitions, source/output hashes,
manifest completeness and consistency with your historical/scenario rerun. Rerun
changed calculations. Check recommendation reflects uncertainties and separates
fictional inputs from public evidence. A declared digest does not prove historical
execution; administrator native task/run/Git attestation is a separate check.

Register actual final reviewer AnalysisRun and review-report artifact. Register
ReviewerValidation against this exact Deliverable version through
register_reviewer_validation with reviewed, report, checks and reviewer_run.
Record individual passed/failed checks and blocking_errors accurately. Call
validate_result and return actual result, weaknesses and exact review/Deliverable
Explorer links. Explain missing administrator actions. Do not grant human acceptance.
```

**Check:** final validation targets the final version. Material blockers require
targeted analyst corrections and review of the new version; these are conditional repairs.

## Your final inspection and acceptance

Open the report in Explorer. Follow one CSV and one public-document finding-to-source
path. Search “maintenance demand technician shortage” and inspect captured versions;
search may return other records in the engagement, so confirm trial relevance.
Expand a finding in Knowledge Graph. Compare versions if corrected.

Ask the administrator to attest the **final synthesis run/version and commit**
using [SETUP.md](SETUP.md) before Accept version. Backend validation must pass;
otherwise reject with rationale or retain a draft. Agent completion and comments
do not grant human acceptance.

### Numerical answer key — consult after independent review

| Historical check | Expected fictional result |
|---|---:|
| Revenue, 2024 / 2025 | USD10.0m / USD12.0m |
| Revenue growth | 20.0% |
| Residential / commercial / installation / maintenance growth | 20% / 20% / 0% / 50% |
| Contribution to USD2.0m increase, same order | USD0.6m / 0.4m / 0.0m / 1.0m |
| Maintenance share, 2024 / 2025 | 20.0% / 25.0% |
| Share change | +5.0 percentage points |
| Gross profit, 2024 / 2025 | USD3.85m / USD4.53m |
| Gross profit increase | USD0.68m, approximately 17.66% |
| Weighted gross margin, 2024 / 2025 | 38.50% / 37.75% |
| Weighted margin change | −0.75 percentage points |
| Growth needed for USD14.0m target | Approximately 16.67% |

| Scenario | Revenue USDm | Maintenance share | Gross profit USDm | Weighted margin |
|---|---:|---:|---:|---:|
| Flat | 12.00 | 25.00% | 4.530 | 37.750% |
| Repeat segment growth | 14.70 | 30.61% | 5.436 | 36.980% |
| Maintenance-only target | 14.00 | 35.71% | 5.130 | 36.643% |

Maintenance-only target requires maintenance revenue USD3.0m → USD5.0m,
approximately **66.67% growth**. Management's historical 25% growth and 30%
maintenance-share assertions conflict with the CSV. A similar future scenario
share does not validate those historical assertions.

Public research/recommendation have no predetermined answer. Judge source quality,
counterevidence and investment conditions. Fewer than six accessible publishers
is a documented multi-source shortfall, not permission to invent captures. This
exercise does not replace platform isolation, recovery or cost-control tests.
