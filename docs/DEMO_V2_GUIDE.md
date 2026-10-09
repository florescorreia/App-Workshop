> Historical evidence: the live workspace was explicitly emptied on 2026-10-09. These idea links/counts and role labels describe the archived showcase, not current live data. Use [UX_WALKTHROUGH.md](UX_WALKTHROUGH.md) for the new two-role experience.

# HarborWorks v2 — additive import and live walkthrough

The batch **harborworks-demo-v2**, seed **84**, anchor **2026-10-07** was explicitly imported at **http://localhost:8080**. Proposed source: [demo/harborworks-demo-v2.json](../demo/harborworks-demo-v2.json). The original v1 batch and all existing records remain untouched. Architecture, images and configuration are unchanged; only the existing importer wrote new business records.

V2 contains **12 ideas**: **6 New, 3 Screening, 2 Analysis, 1 Implementation**; **3 Procurement, 3 Freight, 2 Energy, 2 Scrap/Quality, 2 Productivity**; **4 each in Tampa, Atlanta and Dallas**. All are fictional and Active. Each has a specific problem, pilot proposal, owner and estimates. The eleven early-stage ideas have no approved forecast or actual/verified value.

Commands executed:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 seed-demo -File demo/harborworks-demo-v2.json -DryRun
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 seed-demo -File demo/harborworks-demo-v2.json
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/ideaflow.ps1 seed-demo -File demo/harborworks-demo-v2.json
```

The JSON file supplies the batch key and seed. Keep **-File** when repeating v2: the built-in generator produces the separate 60-record v1 style dataset. This JSON is fixed historical input; repeating its batch key is a no-op. Dry-run reference gaps are expected. The committed manifest is private `local/harborworks-v2-import-manifest.json`; credentials for the three new fictional Contributors are private `local/harborworks-demo-v2-credentials.json`. Existing Morgan Ellis (Manager) and Jordan Chen (Finance) accounts were reused without changes.

Validation passed chronological domain replay, roles/prerequisites, contiguous audit sequences, exact stage/category/site mix, elapsed actuals and current states. Dry-run left all pre-existing row fingerprints identical. Commit added **12 ideas, 64 events, 2 tasks, 12 comments, 13 financial versions, 18 plan periods and 2 actual periods**, with one verified period. Every row that existed before the import — including v1, users and references — retained its original fingerprint. Second committed invocation returned **no_op: true**; all post-import row fingerprints stayed identical. Totals are now **72 ideas, 811 events and two demo batches**.

Actual committed references:

| Reference | Idea | Category | Site | Stage |
| --- | --- | --- | --- | --- |
| [IF-00193](http://localhost:8080/ideas/d2ac03c3-cc58-41a7-b452-f2703da1c305) | Pool standard fastener orders for Tampa assembly cells | Procurement | Tampa | New |
| [IF-00194](http://localhost:8080/ideas/b0f0b6cb-7510-4d01-b8bc-01735f525b6b) | Specify one stretch-film grade for Atlanta pallet wrapping | Procurement | Atlanta | New |
| [IF-00195](http://localhost:8080/ideas/05dd043b-c7b5-41c2-a7c7-4439557ec607) | Reserve Dallas dock slots for scheduled customer pickups | Freight | Dallas | New |
| [IF-00196](http://localhost:8080/ideas/d2a2918c-065a-402e-9776-05eaf7b9195a) | Stop idle Tampa conveyors between production waves | Energy | Tampa | New |
| [IF-00197](http://localhost:8080/ideas/1f0c81d6-9c9f-460d-859e-7f105047a4ab) | Check the first carton after each Atlanta label change | Scrap/Quality | Atlanta | New |
| [IF-00198](http://localhost:8080/ideas/bbe308dc-8910-48dd-93ab-6e8eaccb51a8) | Place charged scanner cradles at Dallas picking zones | Productivity | Dallas | New |
| [IF-00199](http://localhost:8080/ideas/3c3ad09d-d9e2-4b73-90b9-04e86a6e5eb8) | Bundle coolant deliveries for Tampa machining suppliers | Procurement | Tampa | Screening |
| [IF-00200](http://localhost:8080/ideas/5a3c9301-5a02-4cf2-a4ba-f013b2241b80) | Repair leaking Atlanta refrigerated dock seals | Energy | Atlanta | Screening |
| [IF-00201](http://localhost:8080/ideas/5245e9e4-4184-48cf-ba1d-d2e7b5c1e5fd) | Fit a poka-yoke torque fixture to Dallas final assembly | Scrap/Quality | Dallas | Screening |
| [IF-00202](http://localhost:8080/ideas/936f861f-7fdd-42e3-a01f-b048e387bd23) | Pair Tampa supplier returns with inbound carrier backhauls | Freight | Tampa | Analysis |
| [IF-00203](http://localhost:8080/ideas/dd2afe75-cb18-43b9-a710-41139a873ac2) | Sequence Atlanta repair kits before the technician shift | Productivity | Atlanta | Analysis |
| [IF-00204](http://localhost:8080/ideas/9afead83-3292-4ec3-809c-29df4f69219f) | Reduce Dallas emergency freight with a daily dispatch cutoff | Freight | Dallas | Implementation |

## Emergency-freight example

**IF-00204** follows New → Screening → Analysis → Approved → Implementation through historical domain commands. Actual start **1 August 2026**, progress **65%**, expected completion **30 November 2026**. Owner **Jamie Ortiz**; one pilot task Done, one carrier/service review In progress.

The immutable approved v2 financial snapshot contains **18 months, August 2026–January 2028**, with a **50% / 75% / 100% ramp**. Annual gross estimate **$144,000**, annual recurring cost **$12,000**, project spend **$12,000** allocated **$8,000 in August / $4,000 in September**. Probability **75%** and confidence **70%** are independent fields.

| Elapsed month | Planned gross / recurring / spend | Actual gross / recurring / spend | Net benefit expected / actual | Finance |
| --- | --- | --- | --- | --- |
| August 2026 | $6,000 / $500 / $8,000 | $4,200 / $500 / $8,000 | $5,500 / $3,700 | Verified |
| September 2026 | $9,000 / $750 / $4,000 | $7,200 / $750 / $4,000 | $8,250 / $6,450 | Unverified, ready for live review |

For January–December 2026, v2 adds **$46,750 approved net benefit, $12,000 planned spend, $10,150 actual net benefit and $3,700 verified net benefit**. Expected for the matched two reported months is **$13,750**, making the reported variance **−$3,600**. Actual cash flow is **−$1,850**, since project costs are paid before the full benefit ramp. The selected-year planned ROI is **289.6%**; this is a forecast, not achieved ROI. No future actuals were imported.

Combined portfolio January–December 2026: **$1,241,369.94 approved net benefit**, **$290,487.23 reported net benefit**, **$199,478.87 verified net benefit**; coverage **89 of 131 eligible idea-months reported; 62 verified**. Annual potential **$4,869,980** remains a separate run-rate estimate. New drafts contribute potential, not approved/achieved value.

## Short live-demo sequence

Use **[IF-00193](http://localhost:8080/ideas/d2ac03c3-cc58-41a7-b452-f2703da1c305) — Pool standard fastener orders for Tampa assembly cells**. It is still New; the browser review did not advance it.

1. Sign in as Admin (`admin@ideaflow.local`, password in private `local/first-login.txt`) or its assigned Contributor **Sam Patel**. Both can make the two forward moves; **Morgan Ellis (Manager)** can also do so.
2. Open Overview. Explain the separate $28,000 gross and $2,000 annual recurring estimates: **$26,000 annual potential**, with no approved forecast or actual savings. The existing owner is Sam Patel. A Manager/Admin can change ownership if needed.
3. Click **Move to Screening →**. Enter “Named sponsor and fastener invoice baseline are ready for screening”, then **Confirm screening**.
4. Save screening note “Supplier confirms pooled M8/M10 volume; validate landed unit cost and protect two weeks of safety stock.” Click **Save business case**.
5. Click **Move to Analysis →**. Enter “Prepare a supplier quotation and monthly pilot cost-benefit schedule”, then **Confirm analysis**.
6. Show History: the imported fictional creation and the new live decisions are distinguishable by actor/time/provenance. Add a task or comment if useful. A saved estimate remains unapproved; **Manager/Admin** approval needs a reviewed monthly plan and expected dates. **Finance/Admin** alone verifies measured months.

For a Finance follow-on, open IF-00204 Financials and select **September 2026**. Review Finance verification with a reason; confirm the existing numbers only after explaining they are fictional. The latest period was deliberately left unverified. Avoid revoking existing valid sign-offs to repeat a showcase.

To focus each view on v2, use this [register](http://localhost:8080/ideas?ids=d2ac03c3-cc58-41a7-b452-f2703da1c305,b0f0b6cb-7510-4d01-b8bc-01735f525b6b,05dd043b-c7b5-41c2-a7c7-4439557ec607,d2a2918c-065a-402e-9776-05eaf7b9195a,1f0c81d6-9c9f-460d-859e-7f105047a4ab,bbe308dc-8910-48dd-93ab-6e8eaccb51a8,3c3ad09d-d9e2-4b73-90b9-04e86a6e5eb8,5a3c9301-5a02-4cf2-a4ba-f013b2241b80,5245e9e4-4184-48cf-ba1d-d2e7b5c1e5fd,936f861f-7fdd-42e3-a01f-b048e387bd23,dd2afe75-cb18-43b9-a710-41139a873ac2,9afead83-3292-4ec3-809c-29df4f69219f), [Pipeline](http://localhost:8080/pipeline?ids=d2ac03c3-cc58-41a7-b452-f2703da1c305,b0f0b6cb-7510-4d01-b8bc-01735f525b6b,05dd043b-c7b5-41c2-a7c7-4439557ec607,d2a2918c-065a-402e-9776-05eaf7b9195a,1f0c81d6-9c9f-460d-859e-7f105047a4ab,bbe308dc-8910-48dd-93ab-6e8eaccb51a8,3c3ad09d-d9e2-4b73-90b9-04e86a6e5eb8,5a3c9301-5a02-4cf2-a4ba-f013b2241b80,5245e9e4-4184-48cf-ba1d-d2e7b5c1e5fd,936f861f-7fdd-42e3-a01f-b048e387bd23,dd2afe75-cb18-43b9-a710-41139a873ac2,9afead83-3292-4ec3-809c-29df4f69219f), [Process](http://localhost:8080/process?ids=d2ac03c3-cc58-41a7-b452-f2703da1c305,b0f0b6cb-7510-4d01-b8bc-01735f525b6b,05dd043b-c7b5-41c2-a7c7-4439557ec607,d2a2918c-065a-402e-9776-05eaf7b9195a,1f0c81d6-9c9f-460d-859e-7f105047a4ab,bbe308dc-8910-48dd-93ab-6e8eaccb51a8,3c3ad09d-d9e2-4b73-90b9-04e86a6e5eb8,5a3c9301-5a02-4cf2-a4ba-f013b2241b80,5245e9e4-4184-48cf-ba1d-d2e7b5c1e5fd,936f861f-7fdd-42e3-a01f-b048e387bd23,dd2afe75-cb18-43b9-a710-41139a873ac2,9afead83-3292-4ec3-809c-29df4f69219f) or [Value](http://localhost:8080/value?ids=d2ac03c3-cc58-41a7-b452-f2703da1c305,b0f0b6cb-7510-4d01-b8bc-01735f525b6b,05dd043b-c7b5-41c2-a7c7-4439557ec607,d2a2918c-065a-402e-9776-05eaf7b9195a,1f0c81d6-9c9f-460d-859e-7f105047a4ab,bbe308dc-8910-48dd-93ab-6e8eaccb51a8,3c3ad09d-d9e2-4b73-90b9-04e86a6e5eb8,5a3c9301-5a02-4cf2-a4ba-f013b2241b80,5245e9e4-4184-48cf-ba1d-d2e7b5c1e5fd,936f861f-7fdd-42e3-a01f-b048e387bd23,dd2afe75-cb18-43b9-a710-41139a873ac2,9afead83-3292-4ec3-809c-29df4f69219f). Reset filters to show both batches and any user-created work. Process sees 12 v2 cases, including the five entered into Screening and the emergency-freight path; partial paths end In progress. V1's imported Analysis bottleneck and rework history remain preserved.

Verification evidence and browser results are recorded in [VERIFICATION.md](VERIFICATION.md). Presenter actions above are future live actions; the verification review leaves all six New ideas and September's unverified period ready to use.

Post-import backup **backups/ideaflow-20261007-193136.dump** passed isolated restore comparison; all nine business-table fingerprints matched and the temporary database was removed. Both the v2 four-view browser check and the original v1 showcase browser check passed. The final check confirmed every post-import business/reference/user row remained unchanged by the repeated import and read-only review. The local app is ready with exactly three healthy services.
