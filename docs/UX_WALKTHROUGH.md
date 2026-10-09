# Your first IdeaFlow process · User walkthrough

Work through this exercise while signed in with the **User account you already created**. You can capture ideas, define classifications, assign work, move through the workflow, approve plans and review results with that account. The optional Admin exercises are at the end; switch accounts only for those steps.

Open **http://localhost:8080** and sign in with your existing User email and password. No account creation or predefined locations/categories are needed. For general guidance on your own opportunity, open **Walkthrough** in the app, or [the in-app manual](http://localhost:8080/guide). Help links on forms open the relevant topic in a separate tab so your draft stays available.

This is a manual practice exercise. The dispatch example and all amounts below are hypothetical, but you create and work the ideas through the ordinary screens. Their values appear in shared totals while the ideas remain in the workspace. Keep their references so Admin can remove the exact exercise records afterward. Reading this document creates no records.

Keep the references assigned to your exercise ideas. If you repeat the exercise, reopen them rather than creating duplicates. Use a distinctive suffix, such as your initials and today's date, in practice titles and classification names so you can identify your own records.

## 1. Get oriented as a User

1. Open **Settings** and check **Your profile** shows your account and role **User**. Locations and categories are available here. Account management, demo import and removed-idea administration belong to Admin.
2. Open **Ideas**. This view may be empty or contain existing work; your account does not require an empty database.
3. Open **My Work**. It shows ideas you own and open tasks assigned to you.
4. Find **New idea**. You are ready to capture without asking Admin to define anything.

Throughout the exercise, save each form before moving to another tab or screen. Workflow decisions are separate actions: saving a business case does not move its stage. History records who made each change and when.

## 2. Capture an opportunity · New

You can substitute your own idea throughout. Start with an observed problem, a possible improvement and a way to judge success. For a reproducible practice exercise, choose **New idea** and enter:

| Field | Practice entry |
| --- | --- |
| Idea title | Reduce repeated dispatch checks — [your suffix] |
| Problem / opportunity | Two teams repeat the same order checks, adding about ten minutes to each dispatch. We need to establish which checks are necessary and measure the delay. |
| Proposed improvement | Agree one checklist and one person responsible for release. Pilot it for two weeks and compare dispatch time and error rates with the baseline. |
| Owner | Keep your own account, which is selected by default |
| Location (optional) | North dock — [your suffix] |
| Category (optional) | Dispatch — [your suffix] |
| Dates and initial estimates | Leave blank for now |

Click **Create idea**. Note its assigned reference, for example `IF-…`, and bookmark the workspace. Check the **New** stage and your name as owner. The location/category names you typed are now available as choices. Monetary value remains unknown until you assess it.

Optional: capture another idea with location/category blank to see how unassigned work behaves. It still appears in the register and unfiltered dashboards. Enter enough detail to distinguish it from your first idea.

**Check:** you have a saved New idea with your own reference, without Admin setup or approval.

## 3. Reuse classifications and find your work

1. Create a second idea named **Agree a daily dispatch cutoff — [your suffix]**. Describe the problem as variable release times causing queues, and the improvement as an agreed cutoff with exceptions recorded.
2. Open the arrow beside **Location (optional)** and select your practice North dock value. In **Category (optional)**, choose your practice Dispatch value. You can also type its name and select it with Arrow Down and Enter. Case and extra spaces reuse an existing name.
3. Leave estimates blank and click **Create idea**. Note the second reference.
4. Return to **Ideas** and search for your suffix or a saved reference. Open the first idea from its title.
5. Open **My Work**. Both ideas should appear because you own them. In **Pipeline**, they appear in New.

**Check:** the two ideas share choices you created; both appear in the shared workspace.

## 4. Screen and investigate your first idea

1. In **Pipeline**, find the dispatch-check idea and click **Move →**. This opens its workspace; stage changes use the buttons beside its title.
2. Click **Move to Screening →**. Enter **Decision reason**: `Practice: the problem has an owner and a measurable pilot scope`. Click **Confirm screening** and wait for the dialog to close.
3. On **Overview**, enter **Screening note**: `Compare dispatch time and error rates before and after the checklist pilot. Confirm that removing duplicate checks will not weaken controls.` Click **Save business case** and wait for the saved message.
4. Add a comment explaining the next investigation or a question for colleagues, then **Post comment**. An Evidence URL is optional; use a real relevant document when working on a real idea.
5. Click **Move to Analysis →**, give reason `Practice: investigate the pilot, costs and expected monthly benefit`, then **Confirm analysis**.

To experience reassignment, you may choose another active account in **Owner** and **Save business case** after agreeing responsibility with that person. The idea moves to their My Work list; you can still contribute to it. Keep yourself as owner for this solo exercise if you want your practice work to stay together.

**Check:** Analysis is reached only after the screening note is saved. History shows both decisions and your account as actor.

## 5. Try a pause and a backward move · optional User exercise

While your first idea is in Analysis:

1. Choose **Hold →**, explain `Practice: waiting for baseline measurements`, and confirm. Its disposition becomes On hold while its stage stays Analysis.
2. Inspect Pipeline and History. To continue, choose **Resume →**, explain that the prerequisite is available, and confirm.
3. Choose **Move to Screening →**, give reason `Practice: revisit the pilot scope`, and confirm. Refine the screening note, save it and move to Analysis again with a reason.
4. Open History to see the retained pause, resume and repeated stage visit.

Supported backward moves are Analysis → Screening, Approved → Analysis, Validation → Implementation and Realized → Validation. Returning Approved to Analysis invalidates its current financial approval. Returning Validation to Implementation reopens required tasks, clears completion and reduces progress. Use those decisions only when the work needs them.

Reject and Cancel are terminal workflow decisions and cannot be resumed. They are not practice cleanup controls. There is no general undo that erases history.

## 6. Build a monthly plan · Analysis

For real work, use evidence and appropriate dates, and wait for actual delivery/reporting. To experience the whole UX in one practice session, use the **last fully completed calendar month in the app timezone** as the hypothetical pilot month. On **9 October 2026**, that is **September 2026**. Call it **P** below: for that example, start is **1 September 2026**, finish/completion is **30 September 2026**, and the plan/result month is **September 2026**. Use the corresponding dates when practicing later; actual dates must be no later than today. These are hypothetical practice business dates; History still records your actions at the time you perform them.

1. On **Overview**, set **Expected start** to the first day of P and **Expected finish** to its last day. Click **Save business case**.
2. Open **Financials** and enter these practice estimates:

| Field | Value |
| --- | --- |
| Annual gross benefit (USD) | 12000 |
| Annual recurring cost (USD) | 1200 |
| Upfront estimate (USD) | 3000 |
| Probability of success (0–1) | 0.8 |
| Confidence in estimate (0–1) | 0.6 |
| Estimate rationale | Hypothetical practice case: a full-rate month produces $1,000 gross benefit and $100 recurring cost, with $3,000 setup spend. Real savings would require baseline evidence. |

3. Choose **Generate ramp**. Set **Start month** to P, **Months to steady state** to 1, **Horizon (months)** to 12, and **Allocate project spend over months** to 1. Click **Generate editable preview**.
4. Inspect the editable rows. The first month should show gross 1000, recurring 100 and spend 3000. The next eleven months should show gross 1000, recurring 100 and spend 0. Adjust a real schedule to reflect its actual rollout; the helper starts benefits in its first month.
5. Click **Save financial draft** and wait for the saved message. A generated preview alone is not saved, and a saved draft is not yet approved.

Annual net potential is **$10,800**. Over these twelve full-rate months, planned net benefit is **$10,800**, spend **$3,000**, cash flow **$7,800**, and ROI **260%**. The probability-adjusted expected benefit is **$8,640**; confidence is a separate assessment. These are expectations, not achieved savings.

**Check:** expected dates, assessed monetary components/probability and an explicit monthly schedule are saved. Approval does not require a separate Manager or Finance account.

## 7. Approve the expectation · Approved

1. Choose **Move to Approved →**. If the dialog lists missing prerequisites, cancel, complete and save them, then reopen it.
2. Inspect the exact saved financial version, expected dates and monthly rows in the preview.
3. Enter **Decision reason**: `Practice: approve this hypothetical pilot and its saved monthly schedule`.
4. Click **Approve plan and advance**. Check the stage is Approved and Financials identifies a valid approved version.
5. Use **View saved plan version** to inspect earlier versions and the approved snapshot.

You can perform this as User. For real work, agree who should approve the plan and ask another person when independent review matters. If a later plan changes, saving a new draft preserves the current forecast until **Preview plan reapproval** and its explicit confirmation approve the replacement.

**Check:** the approved expectation appears in Value; no actual or verified result has been invented by approval.

## 8. Coordinate and complete delivery · Implementation → Validation

1. Open **Implementation** and add task **Pilot the dispatch checklist**, assigned to yourself (or the agreed active owner). Set its due date to the last day of P, status Open and **Required for completion** checked. Click **Save task**.
2. Under **Delivery milestones**, enter **actual start** as P's first day for this hypothetical exercise. Click **Save milestones**.
3. Choose **Move to Implementation →**, give a practice delivery reason and **Confirm implementation**. The prerequisites are a valid approved plan, actual start and at least one task.
4. Use **Edit task** to set it In progress, then **Save task**. Edit it again to Done and save to experience both actions.
5. Set **Progress (%)** to 100 and **actual completion** to P's last day. Click **Save milestones**. Task completion does not automatically set overall progress.
6. Choose **Move to Validation →**, explain `Practice: the hypothetical pilot and required task are complete`, then **Confirm validation**.

On a real idea, record start/completion when the work actually occurs. Remain in Implementation while required tasks are incomplete. Discuss blockers in comments or use Hold for a deliberate pause.

**Check:** Validation is reached with required tasks Done, progress 100% and a saved completion date. Monthly results still need reporting and review.

## 9. Report and review an elapsed month · User

1. Open **Financials → Monthly outcomes and result verification**. Set **Outcome month** to P, the completed practice month used in the plan.
2. Enter **Actual gross benefit (USD)** 800, **Actual recurring cost (USD)** 100, and **Actual implementation spend (USD)** 3000.
3. In **Outcome / correction reason**, write `Hypothetical exercise result: benefit is below plan; these are practice amounts, not measured business savings`. Click **Save actual outcomes**.
4. Use **Open period** for P if needed. Check that it is reported and unverified. Net benefit is **$700**, compared with expected **$900**, a **$200 shortfall**. Cash flow is **−$2,300**; ROI for this reported month alone is approximately **−76.7%**.
5. Choose **Review result verification**, inspect all three components and enter **Verification reason**: `Practice: checked the hypothetical result against the example baseline and plan`.
6. Click **Confirm result verification**. Check the period's reviewed status and History entry.

All of these steps are available to your User account. For real results, use measured evidence and ask another person to review when appropriate. “Verified” means explicitly reviewed in this workspace; it is not an enforced independent Finance certification.

The three actual fields are monthly amounts: gross is the benefit measured against the baseline before recurring costs; recurring is the improvement's operating cost in that month; implementation spend is one-time setup/delivery spending in that month. Do not enter the annual estimate here. In a later month with no setup spending, use 0 only after confirming there was none.

Blank components and missing months mean unknown. Use zero only when assessed as zero. Do not record current or future month actuals. Correcting a verified actual clears its earlier sign-off and requires another review; **Revoke verification** is also an explicit reasoned action in the review dialog.

### Read Cumulative value evidence

There are no figures to enter here. The graph and supporting table calculate expected, actual and verified running net benefit from the saved financial evidence. Net benefit excludes implementation spend; cash flow and ROI include it separately.

The default **Full idea timeline** covers the current approved schedule (or latest saved draft before approval) and saved outcome months. For this exercise it is September 2026 through August 2027, even though the pilot itself ends in September. Expected benefits can continue after delivery ends. Before approval there is no approved expected line; before reporting/review there is no actual/verified line.

For a closer view, set **Evidence from month** and **Evidence through month** to P and click **Apply date range**. You should see expected $900, reported $700 and, after review, verified $700. Click **Full idea timeline** to restore the 12-month view. Current/future actuals and unreported/unverified months remain gaps. The controls support up to 120 months and survive a page reload; changing them does not change saved records or clear the forms above. Cumulative totals start at the selected From month.

## 10. Confirm the outcome · Realized

1. From Validation, choose **Move to Realized →**.
2. Select P in **Verified through month**. Tick **I confirm implementation is complete**.
3. Enter **Decision reason**: `Practice: hypothetical delivery is complete and the elapsed result has been reviewed`.
4. Click **Confirm realized** and check the stage and History.

Selecting a verified-through month does not fill missing earlier results or certify all periods. Realized closes the delivery lifecycle; later elapsed results can still be reported and reviewed. For real work, stay in Validation until the evidence supports completion.

## 11. Inspect the path and value

Use your suffix/reference to focus the exercise where a Search field is available. Use the same location/category filters when comparing screens.

| View | What to inspect |
| --- | --- |
| Ideas | Find your saved references, their owners and current stages. Reload a filtered URL and confirm the filter remains. |
| Pipeline | The first idea is Realized; the second is still New. A held idea remains in its stage column. |
| History inside the first idea | Your identity, times and reasons for capture, workflow, approval, tasks, actual reporting and review. Include pause/rework entries if you tried step 5. |
| Process | The observed path and repeated Screening/Analysis visit if you tried rework. Compare calendar and active duration when you used Hold. Fast practice cases do not establish a real bottleneck; unfinished visits and small samples need care. |
| Value | Set **From month** to P and **Through month** to eleven months after P for the full 12-month planned ROI. For September 2026, that range is September 2026 through August 2027. The default calendar year may cover only part of the plan. |
| Overview | Shared counts and exceptions, including exercise ideas until Admin removes them. |

In Value, focus the first idea using its practice location and category together (the second has no assessed financials). The full approved schedule has **260% planned ROI**. The single reported/reviewed month has **$700 net benefit** and approximately **−76.7% actual/verified-to-date ROI**. Expected benefit matched to that month is **$900**. Check coverage: one of one eligible plan months is reported and verified when P is the last completed month. Later months remain unreported; they do not become zero actuals.

Annual potential, the full planned horizon and elapsed matched-month results are different measures. Compare like-for-like periods and coverage rather than treating their totals as interchangeable.

## 12. Reorganize your reporting groups · optional User exercise

You can change classifications as a User. First try changing only the second idea: on its **Overview**, type a new category **Cost improvement — [your suffix]** and **Save business case**. The first idea keeps its original category.

For shared regrouping, use only the distinctive practice values created in this exercise, because these actions affect every idea using a selected value:

1. Open **Settings → Locations and categories**. Set **Classification type** to Locations and **Value to change** to your practice North dock value.
2. Enter **New name** `North operations — [your suffix]`, optionally set **Business unit** to `Operations — [your suffix]`, and enter **Classification change reason** `Practice: agree a broader location name`.
3. Click **Save name / business unit**. Both exercise ideas now use the renamed location. Inspect their History and the location filters.
4. Select Categories and your original practice Dispatch value. Choose your practice Cost improvement value under **Merge into existing value** and enter reason `Practice: combine these reporting categories`.
5. Click **Merge into [your target name]**. The first idea joins the target category; the source choice is retired. Inspect its History and current filters. Plans, results and workflow history remain retained.

A shared rename does not keep every earlier spelling as an alias. A merge redirects its retired source to the target. For real classifications, agree shared changes with affected users before applying them. Admin permission is not needed for classification changes.

## If a step is blocked

- **An idea seems missing:** clear unrelated filters and search its reference. My Work shows ownership/assignment; it is not the whole register. A removed idea needs Admin inspection or restoration.
- **A move is unavailable:** open the decision dialog and read its missing prerequisites. Save the relevant note, dates, financial draft, tasks or milestones, then reopen the move. Resume a held idea before advancing.
- **Your change conflicts with another edit:** keep a copy of unsaved text, refresh, inspect the newer version and reapply what is still appropriate.
- **A financial total differs:** check idea filters, plan version, approval, month range and coverage. Unassessed or missing values are unknown.
- **Login fails:** ask Admin to check access or provide a replacement password. You do not need a new account just to repeat this exercise.

## Optional Admin exercise A · remove and restore practice ideas

Finish the User workflow first and keep its references. Sign out using **Sign out** beside your profile, then sign in with your existing Admin credentials. Use this section only when you want to try Admin cleanup.

1. Open **Ideas** and find one of your exercise references. Inspect its title and History to confirm it is the intended practice record.
2. Open **Admin actions → Remove idea**. Review stage, owner and counts of tasks, plans, results, verified results, comments and events. A removal preview does not change the idea.
3. Enter reason `Manual UX practice complete; retain the records for review`, tick the confirmation and submit **Remove idea**. Its stage and evidence are retained, while it leaves everyday views and becomes read-only.
4. Open **Settings → Removed ideas**, search the reference and select **Inspect / restore →**. Inspect the read-only tabs and history.
5. To try restoration, choose **Restore idea**, keep the active owner, enter a reason, tick the restoration confirmation and submit. If its owner or open task assignees became inactive/retired, choose an active owner and explicitly confirm reassignment of the listed tasks.
6. Sign out and return to your User account. Find the restored idea in **Ideas** at its retained stage. You can leave it there or switch to Admin later to remove it again.

Removal archives the complete record; it is not permanent deletion. Use exact exercise references for cleanup and retain your User account for further practice.

## Optional Admin exercise B · account maintenance

Your existing User account is already ready for the walkthrough. To explore account controls, use a separate disposable practice account rather than interrupting that account's access.

1. Sign in as Admin and open **Settings → Local user management**. If needed, create a distinct practice account with a private password and role User.
2. In that account's row, choose **Regenerate password**, enter an account action reason and click **Generate new password**. Share the replacement privately and close with **Done**. It is shown once; the old password and earlier sessions stop working. An inactive account stays inactive.
3. **Set password** lets Admin choose a replacement instead. Setting the currently signed-in Admin's own password signs that Admin out.
4. If the disposable account is no longer needed, choose **Delete account** and inspect the preview. Reassign listed open work first. Enter a reason and **Confirm account deletion** only for the intended disposable account.
5. An unused account is removed. A historical account is retired from access while its name remains on previous work. Signed-in and bootstrap Admin accounts are protected. **View account history** shows the actions, actors and reasons without passwords.
6. Return to your existing User account to continue normal work.

The User exercise covers the entire idea lifecycle. Admin is needed for account access and practice archival/restoration, not for developing, assigning, approving or reviewing the idea itself.
