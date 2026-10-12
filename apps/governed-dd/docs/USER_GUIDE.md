# Using Governed DD

For a copy-and-paste Paperclip exercise, use the [ten-task DD trial](SIMPLE_DD_TRIAL.md): two supplied documents, multi-source research, financial/scenario analysis and two independent reviewer tasks.

Open **http://localhost:8081** and select **Sign in to your workspace**. Use the consultant username and password supplied privately by your administrator. You see only engagements assigned to you. An empty list means no engagement assignment yet.

Select an engagement deliberately before starting work. Its name stays visible above the navigation. **Switch engagement** returns to your directory; searches and evidence never combine engagements. A stopped workspace retains its work but needs an administrator to start its services.

## Request analysis

From Overview choose **Open Paperclip**. Paperclip has separate native authentication: use the engagement-specific email and password supplied by your administrator. Your portal session and current membership are also required. Choose **New Task**, describe the question, reporting periods, calculations and expected output, and assign the DD analyst. Request independent DD reviewer work before acceptance. Periodic research is disabled.

Upload supplied sources in Explorer first and put their exact object/version links in the Paperclip task. Explain content and access limitations. Paperclip attachments are not automatically indexed: use the Explorer upload link for governed source preservation. A file attached only to a task is not automatically searchable evidence.

An Explorer upload opens the saved source automatically. In its details panel, use **Copy link** beneath **Exact version link**, then paste into your Paperclip task. You can also select the displayed link and copy it manually if clipboard access is blocked. The same control appears when you open a source from Sources and on other governed records. If you already attached a document in Paperclip, ask your administrator to import it with its task and attachment IDs. The import verifies original bytes and preserves those IDs; retrying does not create another source version.

Fictional example: “Use the supplied 2024 and 2025 revenue document, calculate comparable growth, explain assumptions, register definitions and exact evidence, and provide a report for review.” Public search needs project authorization and a configured provider. Missing or inaccessible evidence must remain a limitation.

## Inspect evidence

Use Overview, Findings, Sources, Knowledge Graph, Definitions, Analyses and Deliverables. Search applies only to this engagement. BM25 and LiteLLM dense retrieval work locally and combine in hybrid search. The interface reports its active mode.

Open a finding to inspect its claim, implications, assumptions, uncertainty, producing run and metric definitions. Follow **Open exact version** to the supporting source and page, paragraph, row or section. **Download original** retrieves that byte version. Text/HTML previews safely display source content as text; PDF originals have an inline preview link. Long extractions have previous/next passage controls.

In Knowledge Graph choose an object and expand its connected evidence. Filter relations and select one to three steps. Queries are bounded. Click a node or connection to inspect the exact underlying version. Memgraph Lab is an advanced owner tool with graph write privileges; ordinary graph exploration stays in Explorer.

Analyses record inputs, task/run provenance, code commit, parameters, environment and outputs. Original deterministic calculations and later report corrections may have different versions. Historical image digests declared by an administrator are distinguishable from a reviewer’s own verification.

## Review outputs

Open the exact deliverable version, follow its findings/output links and inspect independent checks. **Compare with previous version** shows changed fields and linked added/removed findings, evidence and output versions.

Owners and human reviewers enter a rationale to **Accept version** or **Reject**. Acceptance is blocked by incomplete evidence, bytes, manifests, graph projection, native provenance verification or independent checks. Ask your administrator to verify the completed native run before accepting. Agents cannot grant human acceptance. Acceptance preserves the exact version and decision; later edits need another version/review. Completed Paperclip tasks do not silently publish.

Local fictional examples and real-provider acceptance tasks are visibly synthetic and establish no real company conclusions. Request corrections through follow-up tasks rather than editing original evidence.

## Interrupt and sign out

Overview shows source processing status and cancellation. Cancellation preserves original bytes and records the stopped job; completed passages may remain as partial progress. Use Paperclip’s native cancellation for analytical runs. Failed/cancelled tasks do not count as successful outputs.

Return to the portal and **Sign out**. Membership removal denies the next protected request and terminates active component streams. Signing in again does not restore revoked membership. Contact your administrator about missing assignments or stopped workspaces.
