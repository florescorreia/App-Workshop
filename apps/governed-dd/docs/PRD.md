# Governed Due Diligence Workspace — V1 PRD

Build locally on Rancher Desktop; move to a VPS only after acceptance testing.

Status: **Local implementation in progress; acceptance checks and remaining gaps are recorded in VERIFICATION.md.**
App identity: **`governed-dd`**.
Contract location: **`./apps/governed-dd/docs/PRD.md`**, relative to the App Workshop repository root.

## 0. App Workshop integration and scope

This is one application in App Workshop, not a new source repository or a replacement for IdeaFlow. Keep all product source, tests, docs, infrastructure templates and scripts under `apps/governed-dd/`. Root documents/tools concern shared workspace/hosting capabilities only. Read root AGENTS.md and [new-app guide](../../../docs/START_NEW_APP.md), [workspace operations](../../../docs/APP_WORKSHOP.md), [VPS foundation](../../../docs/VPS_FOUNDATION.md), [security](../../../docs/VPS_SECURITY.md) and [Cockpit](../../../docs/VPS_COCKPIT.md). Paths below are app-relative unless explicitly labeled repository-root or runtime paths.

**Governed DD intentionally exceeds the generic three-service starter.** Identity/portal infrastructure and isolated per-engagement Paperclip/Codex, PostgreSQL, DD service, Memgraph, optional Lab and Explorer components are required. Do not collapse isolation or omit components to fit the starter. Do not run the generic generator/deployer unchanged and claim this PRD is implemented. On explicit implementation request, create an app-specific AGENTS.md and deliberately adapt app registration, commands and release assets. Preserve IdeaFlow's existing three-service architecture and all other apps.

During implementation, register governed-dd in root `workshop.json` with a management kind/path that shared dispatch actually supports; extend shared tooling minimally where necessary. Its app-specific `app.json` must describe the real control-plane/tenant topology, entrypoints, ports, volumes and commands. Do not pass incompatible metadata into the generic three-service deployment renderer. Use unique `governed-dd`-prefixed project/account/target/volume identities and opaque tenant IDs. Never reuse another app's credentials or storage.

Allocate ports against the live catalog and actual listeners. **Local 8080, VPS HTTPS 8443 and VPS loopback 18081 are reserved for IdeaFlow.** No governed-dd port or URL is allocated by this document. Keep one root Git repository (`https://github.com/florescorreia/App-Workshop`); engagement analytical Git repositories live only on isolated runtime volumes, never nested in platform source.

This review permits documentation changes only: no scaffolding, registration, dependencies, credentials, tenant provisioning, agents, containers or VPS mutation until implementation is explicitly requested. A later local build still does not authorize production deployment. Start empty; fictional acceptance fixtures are explicit test/demo actions.

## 1. Product and outcome

Create a multiuser, multiproject application where consultants request DD work in natural language through Paperclip. Codex agents research, analyze, produce deliverables, and maintain a searchable, source-linked knowledge base automatically. Consultants inspect findings, source documents, definitions, analytical runs, and a knowledge graph in a thin DD Explorer. Memgraph Lab provides advanced graph inspection.

Every engagement is a security tenant. Users may belong to several engagements, but must neither access nor discover engagements they do not belong to. Ordinary users must never receive unauthorized project names, IDs, counts, routes, search hits, or activity. Platform administrators are explicitly trusted and necessarily see provisioning information.

V1 is a working vertical slice, not a collection of empty integrations. Acceptance requires a real Paperclip-to-Codex task producing registered sources, analysis, findings, graph records, and a reviewable output.

## 2. Scope and decisions

Required: Paperclip, Codex CLI, PostgreSQL with pgvector and pg_search for BM25, Memgraph, Memgraph Lab, artifact storage, per-project Git, FastMCP tools, FastAPI backend, React/TypeScript DD Explorer, authenticated portal, and Docker Compose.

FastAPI serves the Explorer and authorization endpoints. FastMCP exposes the same Python domain services to agents. They must share validation and persistence logic.

Do not add Kubernetes, Dagster, dbt, OpenMetadata, a separate vector database, or an additional agent framework in V1. Do not replace Codex with a home-built LLM loop. Paperclip organizes tasks; Codex remains the execution harness.

Default artifact storage: immutable, content-addressed files on a separate named volume per engagement, accessed through the governance service. Keep a storage adapter interface for later S3-compatible storage. No object-storage container is necessary initially. Original bytes and versions are authoritative; retrieval indexes are rebuildable.

Default agent roles: one DD analyst and one reviewer per engagement. The analyst handles research, extraction, indexing, ontology proposals, and analysis through deterministic service tools. The reviewer checks material outputs in a separate run and context. Consultant actions initiate work; disable periodic heartbeats, cron research, and self-starting work. Follow-on processing is allowed only within an explicitly started task. Human acceptance remains separate from reviewer validation.

## 3. Deployment and trust boundaries

Use Rancher Desktop with **dockerd/Moby**, the explicitly detected Docker context and Docker Compose locally. Do not change host settings automatically. All Python/Node/Codex development and execution tools run in containers; host requirements are Rancher Desktop, Git, and an editor. Provisioning tools may receive scoped engine access as transient administrator tooling; public services and tenant agents never receive it.

Shared services:

Here “shared” means shared among governed-dd engagements, not with IdeaFlow or other apps. Existing host Caddy, Cockpit and SSH remain the shared VPS hosting layer. The governed-dd authorization gateway is app-owned behind host Caddy and must not replace it.

- Reverse proxy and authorization gateway.
- Keycloak for OIDC login, with persistent identity database.
- Portal/tenant directory storing user memberships and opaque tenant IDs.

Persist identities, OIDC realm/client configuration and portal memberships/audit in dedicated governed-dd control-plane storage. Use separate databases/least-privilege roles on an app-owned control-plane PostgreSQL container, independent of engagement and IdeaFlow databases. Include that container in the service inventory, resource budget and backup/restore. Verify the pinned Keycloak release's actual login/redirect/logout behavior.

Per-engagement services and storage:

| Component | Deployment and responsibility |
|---|---|
| Paperclip + Codex runtime | Dedicated Paperclip instance and supported Codex adapter; native UI and execution history |
| PostgreSQL | Dedicated server/container with pgvector and pg_search; separate Paperclip and DD databases and least-privilege roles |
| DD service | FastAPI + FastMCP; registry, validation, ingestion, retrieval, artifact access, graph projection |
| Memgraph | Dedicated graph instance and persistent volume |
| Memgraph Lab | Dedicated instance, protected route, expert access only |
| Explorer | Same frontend build, configured for one tenant; separate service instance or explicitly tenant-bound route |
| Persistent files | Separate artifact, Git/workspace, Paperclip state, and agent-home volumes |

A dedicated PostgreSQL container per engagement intentionally favors simple local isolation over the smallest container count. Sharing database hosts is a later optimization requiring equivalent tests.

Document the actual control-plane service count and per-active-engagement count, including optional Lab when enabled. Codex subprocesses and transient provisioning/test/backup tooling are not additional long-running services. Resource admission and isolation apply even though the generic three-service count does not.

Each engagement gets its own backend network. Do not attach agents to a common network exposing all tenants. Route only the tenant's frontend-facing endpoints through the shared gateway. Do not expose PostgreSQL, Bolt, MCP, or Paperclip backend ports publicly. Expose only the gateway on loopback locally; use TLS and configured domains on the VPS.

On the VPS host Caddy routes the allocated app HTTPS entrypoint to the governed-dd gateway's allocated loopback port. Do not replace shared 80/443 redirects or IdeaFlow's route. Tenant ingress must not permit agents to traverse from their backend into other engagements. Select subdomain/path routing only after verifying OIDC, Paperclip and Lab compatibility; the existing provider hostname does not automatically provide tenant DNS or wildcard certificates.

The Paperclip local adapter executes wherever Paperclip launches its CLI. Start with a per-tenant Paperclip execution container containing Codex and analytical dependencies. Do not draw a separate worker boundary unless the pinned Paperclip version supports and demonstrably uses remote/sandbox workers. Document the actual execution topology.

A shared container is not an isolation boundary between Paperclip and generated analysis code. Verify subprocess environment, filesystem permissions and credential access; agent code must not read Paperclip database/admin credentials or impersonate human publication roles. If the adapter cannot enforce this separation, document the blocker and use a supported isolated execution arrangement before accepting security claims.

Agents must have no Docker socket, privileged mode, host root mount, provisioning credentials, or other engagement volumes. Drop unnecessary capabilities, run nonroot where supported, and bound CPU, memory, execution time, and concurrency. Agent-created analysis code executes only inside the tenant runtime/workspace.

Tenant provisioning is an explicit administrator CLI command generating local Compose from app-owned templates. Future VPS provisioning generates rootless Podman/Quadlet units, targets and private routing against the existing host foundation; it must not install Docker or replace the VPS runtime. The public app must not have engine/provisioning control. Creation is idempotent; deleting a tenant requires an explicit command and backup policy. Normal startup has bootstrap administration/configuration only and no fictional engagements/tasks. Explicit test/demo commands provision the two acceptance tenants, with one active analytical run at a time per tenant.

## 4. Identity, membership, and non-discoverability

Roles: platform administrator; engagement owner; analyst; reviewer; viewer. Owners manage their team's membership; viewers inspect accepted and permitted draft assets but cannot start tasks. Publication requires an owner/reviewer permission distinct from agent permissions.

The shared portal lists only memberships authorized server-side. Use OIDC subject IDs as identities, not user-editable email values. Never trust an engagement ID submitted by the browser or agent as authorization.

Every route, API request, download, MCP call, websocket, and background job must be bound to the authenticated tenant. Agent credentials identify one tenant and one role and cannot acquire another tenant by changing parameters. Validate token issuer, audience, signature, expiry, and membership/session revocation. Check current membership on each request; do not rely only on long-lived token claims.

Protect direct Paperclip and Lab access as well as the portal. Verify Paperclip's authenticated deployment mode and native user permissions against the pinned release. Either integrate supported identity mechanisms or retain native authentication behind the membership gateway. Do not assume Paperclip trusts arbitrary reverse-proxy identity headers. Authenticated upstream access and tenant membership must both work; tenant-local users may need provisioning through supported APIs.

Use opaque tenant subdomains/routes and tenant-scoped cookies. Gateway authorization must cover every path, including static metadata, API aliases, websocket upgrades, and attachments. A route known to a user must stop working immediately after membership revocation. Unauthorized tenant IDs return uniform 404 responses without descriptive error bodies. Tenant enumeration counters, suggestions, and UI payloads must be filtered before delivery.

Cookies are not isolated by port. Use app/tenant-specific names, appropriate path scope, CSRF protection and exact external origins including ports. Verify upstream base-path support before using route prefixes. Realm/redirect/cookie configuration belongs to governed-dd and must not change another app's login behavior.

Memgraph Lab is an expert tool, not the default consultant workflow. Ordinary consultants use Explorer graph traversal. Enable Lab only after validating tenant-specific connection behavior and available read-only permissions in the selected Memgraph edition. If enforceable read-only Lab access is unavailable, restrict it to engagement owners/admins; keep ordinary graph exploration in the read-only Explorer API. No arbitrary graph write endpoint for consultants.

Tenant data, sessions, agent memories, embedding caches, deduplication, backups, and logs must remain separate. Shared templates may contain generic schemas and skills only. A multi-engagement consultant must deliberately switch context; no automatic cross-project copying or combined search.

This isolates ordinary users and tenant agents within a shared host. It does not protect against a compromised VPS administrator or kernel, nor prove absence of every timing side channel. Stronger host isolation is outside V1; do not describe the system as absolutely isolated.

## 5. Consultant workflows and frontend

1. Sign in and see only assigned engagements.
2. Open an engagement landing page showing its task and knowledge status.
3. Open native Paperclip to submit a natural-language task, attach the DD assignment, upload sources, or request a follow-up analysis.
4. Follow progress and receive a concise result plus links to Explorer assets in the Paperclip task.
5. Inspect sources, claims, definitions, calculations, and connected entities in Explorer.
6. Review or reject a deliverable; acceptance freezes a version, not the entire evolving project.

Explorer sidebar: Overview, Findings, Sources, Knowledge Graph, Definitions, Analyses, Deliverables. Provide search, filters, breadcrumbs, review badges, and persistent links. Use a clear consulting workspace design with restrained colors and dense but readable tables.

Graph view: expand neighbors, filter relation type, inspect a node/edge, and navigate to its evidence. Bound each query by depth and result count; never load the full graph by default. Selecting a finding shows its supporting/refuting evidence, source page/section, assumptions, and producing run. Source viewer shows authorized PDF/text previews and downloads. Dataset previews are paginated. Deliverable version comparison shows changed findings and evidence.

Consultants do not manually populate catalogs. They can correct a definition or challenge a finding through a task/review action, creating a new version and audit record. All destructive or model-generated changes remain attributable.

Paperclip attachments must be ingested through a documented integration: import attachment bytes through supported APIs, or attach an authorized source upload link to the task. Register the task ID and attachment ID. Do not assume attachments are automatically indexed or persist only inside ephemeral containers.

## 6. System of record and governance contract

PostgreSQL holds canonical versioned registry records; files hold artifact bytes; Git holds analysis logic, ontology versions, and instructions. Memgraph is the traversable representation of these records. Paperclip is authoritative for work requests and native task history. Registry records reference Paperclip instance, issue, and run IDs.

Every governed object has an opaque ID, tenant binding, version, timestamps, creator/run, status, and typed references. At minimum implement:

| Record | Required content |
|---|---|
| Source | URL or original filename, publisher, publication/retrieval dates where known, hash, byte version, access limitations |
| Extraction/chunk | Source version, page/sheet/section or cell range, extractor version, text hash, configuration |
| Entity/assertion | Type, properties, time scope, evidence references, extraction run, confidence, review state |
| Definition | Name, meaning, formula when applicable, units, scope, owner, version |
| Finding | Claim, implications, supporting/refuting evidence, assumptions, uncertainty, review state |
| Analysis run | Task/run IDs, input versions, code commit, image digest/lockfile, parameters, seeds, outputs, execution status |
| Artifact | Content hash, media type, storage reference, size, version, producing run |
| Review/publication | Exact reviewed versions, reviewer identity, decision, validation report, timestamp |
| Audit event | Actor, operation, object/version, correlation ID, timestamp; redact credentials |

Preserve published revisions. Updates produce new versions; corrections can supersede or retract old assertions while retaining history. Avoid labelling agent-extracted assertions as verified facts. Unknown is a valid value; invented provenance is not.

Use a transaction outbox in PostgreSQL for graph/index updates. Commit the canonical record and event together; apply graph projection idempotently; expose pending/failed projection state. A small worker in the DD service polls the outbox; no broker is required. Rebuild Memgraph from canonical records and ontology versions. This prevents incompatible dual-authority graph and database writes.

Enforce governance at publication in the backend: valid evidence references, retrievable artifact bytes, hashes, registered semantics for material metrics, run manifest, review of the exact artifact version, and no unresolved blocking validation errors. Agents may propose/review but cannot grant human acceptance. Paperclip task completion must not silently publish results.

Do not claim to record absolutely every action. Capture harness-supported execution events/transcripts with redaction, tool calls, run manifests, and resulting artifacts. Report capture gaps. Analytical reruns should reproduce deterministic calculations; LLM answers and changing web pages are not guaranteed to reproduce byte-for-byte. Preserve source snapshots and report this distinction in validation.

## 7. Ontology and retrieval

Version YAML ontology definitions in the tenant repo. Initial types: Company, Person, Market, Product, Geography, Metric, Definition, Source, Evidence, Finding, Assumption, AnalysisRun, Artifact, Task.

Initial relations: SUPPORTS, REFUTES, DERIVED_FROM, GENERATED_BY, USES, DEFINES, ABOUT, OWNS, COMPETES_WITH, OPERATES_IN. Define allowed endpoints, required properties, units/time scope, and evidence requirements. Validate before writing. Agents propose ontology additions; an owner approves schema changes before ingestion uses them. No silent unrestricted relation creation.

Hybrid retrieval combines BM25 and dense results using reciprocal rank fusion, followed by bounded graph expansion. Preserve source and version identifiers in all hits. Implement real pg_search BM25; standard PostgreSQL text ranking is not an equivalent implementation. Pin a compatible PostgreSQL/pgvector/pg_search build, verify the extensions, and test BM25 scores and vector similarity.

Embeddings use a separately configurable model/provider and dimension; the analytical LLM endpoint may not offer embeddings. Record model, dimension, chunking version, and extraction configuration. Reindex on incompatible changes; never mix embedding spaces. Index suitable text and descriptions, rather than blindly embedding every binary file. Store structured tables for calculation, and only useful text representations for search. Start with PDF, DOCX, TXT/Markdown, CSV/XLSX, and web HTML; flag scanned PDFs requiring optional OCR rather than pretending extraction succeeded.

## 8. Agent capabilities and research policy

Expose authenticated, tenant-bound MCP tools backed by the shared service layer:

`search_knowledge`, `get_definition`, `register_source`, `ingest_source`, `register_artifact`, `register_analysis`, `propose_assertions`, `propose_definition`, `register_finding`, `trace_provenance`, `validate_result`, `request_publication`.

Add controlled web search and fetch capabilities. Codex native search may be enabled when supported by the configured provider; a selectable external search backend is required when it is not. Test real search through the configured endpoint before declaring integration complete. A search snippet is discovery evidence, not a captured full source. Store the used page or authorized excerpt, retrieval metadata, and precise citation. Mark inaccessible sources and never fabricate page access.

Fetch tools must reject localhost, private networks, cloud metadata endpoints, file URLs, unsafe redirects, and oversized downloads. Validate DNS/redirect destinations. Default worker egress is restricted to configured model/search providers and controlled public fetch tooling; general internet access requires an explicit deployment setting. Never send confidential client names or passages to public search without project authorization. Documents and web pages are untrusted content, not instructions; they cannot override tenant identity, tool permissions, or publication rules.

Large extraction, embedding, and indexing jobs execute deterministically within the service after the analyst requests them. Agent role names do not imply independent agents for every ingestion stage. Reviewer checks evidence and calculations, and reports weaknesses rather than merely endorsing prose. Provide cost, timeout, cancellation, and bounded retry controls. Persist partial progress and display failures honestly.

## 9. Environment configuration

Generate `.env.example`, documented secret templates, and a configuration validator. User edits values before real runs. The following are application-owned settings, not assertions about upstream Paperclip variable names; map them to verified upstream configuration in code.

```dotenv
DEPLOYMENT_MODE=local
APP_BASE_URL=http://localhost:ALLOCATED_LOCAL_PORT
HOST_BIND_ADDRESS=127.0.0.1
GATEWAY_PORT=ALLOCATED_LOCAL_PORT
OIDC_ISSUER_URL=
OIDC_CLIENT_ID=dd-portal
OIDC_CLIENT_SECRET_FILE=/run/secrets/oidc_client_secret
DATABASE_PASSWORD_FILE=/run/secrets/database_password
AGENT_MODEL=gpt-6.1-sol
AGENT_REASONING_EFFORT=medium
LLM_AUTH_MODE=api_key
LLM_PROVIDER=custom
LLM_BASE_URL=
LLM_API_KEY_ENV=DD_LLM_API_KEY
WEB_SEARCH_BACKEND=external
WEB_SEARCH_PROVIDER=
WEB_SEARCH_API_KEY_ENV=DD_SEARCH_API_KEY
EMBEDDING_PROVIDER=
EMBEDDING_BASE_URL=
EMBEDDING_MODEL=
EMBEDDING_DIMENSIONS=
EMBEDDING_API_KEY_ENV=DD_EMBEDDING_API_KEY
ARTIFACT_BACKEND=filesystem
MAX_CONCURRENT_RUNS_PER_TENANT=1
RUN_TIMEOUT_SECONDS=1800
ALLOW_GENERAL_INTERNET=false
ENABLE_MEMGRAPH_LAB=false
```

Use the user's selected model alias only if the endpoint supports it; fail clearly instead of silently substituting models. Support LiteLLM/custom provider configuration through the pinned Codex/Paperclip adapter. Determine required API/wire protocol, provider auth, managed agent-home behavior, MCP setup, and noninteractive execution from actual installed versions. Do not blindly copy a host `.codex/config.toml` or share host authentication/state across tenants. If the user supplies it, read only authorized provider settings and the named key environment variable; never log its value. Secrets must be injected explicitly into containers; host environment variables are not inherited automatically.

Generate tenant-specific configs and credentials during provisioning, with secret files outside Git. Never commit `.env`, auth files, tokens, client data, generated analysis inputs, or Paperclip secrets to the platform source repository. Store tenant analytical artifacts and Git repos on their own persistent volumes. Provide a mock profile for development without keys, visibly marked simulated; real integration tests are mandatory before acceptance.

## 10. Persistence, recovery, and VPS transition

The allocated-port tokens in section 9 are placeholders, not runnable settings; the configuration validator must reject unresolved values. During local setup generate app-owned settings without changing the root catalog's existing reservations. For VPS access keys, use persistent Windows User variables prefixed `APPWORKSHOP-GOVERNED-DD-...`, documenting the variable names/purposes only. Reuse the existing secured SSH transport by reference; never copy the host key/passphrase or IdeaFlow secrets into tenant containers. Inject each secret only into the component and tenant that needs it.

Persist all databases, graph snapshots/WAL, evidence bytes, run manifests, per-tenant Git/workspaces, agent state, identity configuration, and Paperclip state. Restarting or rebuilding containers must not erase work. Document every volume and owner. Pin images/dependencies and record their versions; never use unqualified `latest` for the accepted deployment.

Backup via an explicit admin command: quiesce writes or take consistent supported snapshots, dump tenant databases, export graph if useful, copy artifact/Git/state volumes, capture checksums and configuration versions, and encrypt the backup. Restore onto a fresh deployment and validate hashes/relations/memberships. Graph and search indexes may be rebuilt; originals and canonical registry must be preserved. Named volumes alone are not backups.

Provide app-specific local Docker Compose profiles/overrides and a separately reviewed **VPS rootless Podman/Quadlet release**, retaining host Caddy, Cockpit and SSH. VPS configuration adds HTTPS, actual OIDC redirect URIs, secure cookies, reviewed firewall rules, persistent encrypted backups, secret rotation, resource limits and authenticated operations access. Define whole-app control-plane/tenant targets visible to the appropriate dedicated account in Cockpit, with correct start/stop/readiness and shutdown ordering. Do not run the generic three-service VPS installer on this topology or assume Compose-to-Quadlet conversion preserves isolation. Do not deploy to the VPS during the local build. Document migration using backup/restore and rollback rather than copying live database directories.

Measure RAM, disk, ingestion time, and run concurrency with two demo engagements. A 32 GB machine is a planning target, not a guaranteed minimum; graph and agent workloads may dominate. Report actual usage and enable stopping inactive tenant stacks while preserving portal membership and volumes.

## 11. Repository and developer deliverables

All paths in this layout are **relative to repository-root `apps/governed-dd/`**. Portal and Explorer are components of this one app, not separate root `apps/portal` or `apps/explorer` products. Create these files only when implementation is requested:

```text
docs/PRD.md
docs/USER_GUIDE.md
docs/VERIFICATION.md
docs/DD_PROJECT.md
docs/SETUP.md
docs/ARCHITECTURE.md
docs/SECURITY.md
docs/VPS_MIGRATION.md
frontend/portal/
frontend/explorer/
services/governance/
infra/compose/
infra/vps/
infra/tenant-template/
schemas/ontology/
agents/analyst.md
agents/reviewer.md
scripts/
tests/
.env.example
app.json
AGENTS.md
README.md
```

Implement commands for setup checks, shared-stack startup, tenant provisioning/start/stop, membership management, demo seed, agent integration check, test, backup, restore, and index/graph rebuild. Commands must be repeatable and documented for PowerShell and a Unix shell, or use a portable Python CLI. Render and validate Compose configurations before applying them. No manual database editing as a routine setup step.

“Shared-stack” commands manage governed-dd's control plane only. Run app-specific scripts from their documented app root or dispatch through the minimally adapted workspace wrapper. Any Python CLI runs in a tooling container; host Python/Node are not prerequisites. Preserve root Git/remote and other app sources/configuration. Keep tenant repos, source uploads, artifacts, model credentials and generated analytical inputs outside source control on their own volumes. Add app-local ignore rules for private files not already covered by root `.gitignore`.

Maintain app README with actual commands/URLs/login method, `docs/USER_GUIDE.md` from a normal consultant perspective, and `docs/VERIFICATION.md` with observed results, topology/resources and precise blockers. Shared host docs may link to this app's runbook, but product documentation stays in this folder. Do not commit passwords or confidential engagement identifiers/content as examples.

Keep upstream Paperclip integration thin. Pin its release/commit, document supported configuration and extension points, and avoid a broad fork. If a critical authentication or execution feature is unsupported, implement the smallest documented adapter or surface the blocker; do not simulate success.

## 12. Build sequence and acceptance

Build in increments, running appropriate checks after each increment:

1. Verify upstream versions, licensing/image architecture support, Rancher runtime, model/search/embedding interfaces, and Paperclip execution/authentication behavior. Record findings and lock decisions.
2. Stage identity, gateway and portal locally with an empty normal startup. Explicitly provision two isolated acceptance-test tenants and prove membership checks before adding agent work; this is not VPS deployment or automatic demo loading.
3. Implement canonical registry, versioned artifacts, YAML validation, outbox, graph projection, hybrid search, and MCP/API contracts.
4. Wire a real Paperclip task to Codex with tenant-scoped tools and persistent analytical workspace. Demonstrate source ingestion, a calculation, a finding, and reviewer feedback.
5. Build Explorer traversal and publication controls; load two visibly fictional DD examples only through explicit additive, batch-idempotent test/demo commands, with validation/provenance and no live-record overwrite.
6. Complete isolation, restart, backup/restore, rebuild, cancellation, and real provider tests. Deliver the local application and VPS runbook.

Required acceptance evidence:

- Alice belongs only to A; Bob only to B; Carol to both. Alice cannot discover or access B through portal, guessed routes, direct Paperclip APIs, attachments, search, Lab, downloads, websocket connections, or MCP. Carol must explicitly switch contexts.
- An A agent cannot connect to B networks/services, read B volumes/secrets, retrieve B graph/vector records, or change tenant identity in a tool call. Test service authorization independently of UI.
- Membership removal denies the next protected request and terminates active streams. A re-login cannot restore access without renewed membership.
- Natural-language task in A yields actual web evidence, an ingested supplied document, a reproducible calculation, sourced findings, graph edges, and an Explorer link in Paperclip. Run a real provider smoke test; mocked output cannot satisfy this criterion.
- Every accepted finding opens the exact supporting source version and locator. Unsupported claims remain explicit hypotheses. A failed extraction cannot appear as indexed success.
- Real BM25 and dense retrieval return known test evidence; filtering is tenant-bound. Reindexing/rebuilding preserves source identities and hashes.
- Duplicate/retried ingestion and graph projection do not duplicate canonical versions or corrupt lineage. A projection failure remains visible and repairable.
- A deliberately incomplete output is rejected by publication checks. Agent credentials cannot accept it; editing an accepted artifact requires a new version/review.
- Calculation rerun from recorded input versions and environment agrees within a defined tolerance. Nondeterministic narrative reruns are reported separately.
- Container restart/rebuild preserves records and bytes. Fresh-host restore recovers both tenants and identity/membership, with verified checksums.
- No secret appears in logs, exported task text, browser payloads, repository history, or backup manifests. Test SSRF and untrusted-document instructions.

- Published output directory is `apps/governed-dd/`; source has no nested `.git` and runtime tenant Git repos remain on isolated volumes. App operations do not change IdeaFlow or another app's identities, routes, credentials, records or volumes. Allocated ports do not collide with existing catalog entries/listeners.
- Stopping governed-dd or one inactive tenant preserves all its storage and does not stop another application. Capacity checks include control-plane identity storage, all enabled tenant services, graph/index jobs and agent peaks; refuse an unsafe start with a clear resource explanation rather than silently exceeding host capacity.
- The future VPS runbook maps the real topology to dedicated rootless accounts, targets, private ingress, host Caddy and backup/restore. No VPS deployment is claimed during local acceptance. A later explicitly authorized deployment requires its own target-host tests, including restart/autostart and data preservation.

Provide an acceptance report with commands, results, measured resource use, remaining limitations, and links to relevant screenshots/log extracts with secrets removed. Do not claim unexecuted checks passed. If external credentials are missing, complete all independent work and list the precise outstanding real tests.

## 13. Upstream references and implementation caution

### Local implementation decisions (2026-10-11)

The user's implementation instruction supersedes the earlier documentation-only restriction. Allocated local gateway is `http://localhost:8081`, future VPS HTTPS/loopback reservations are 8444/18082. No VPS change is authorized. Normal startup remains empty; acceptance tenants/data are explicit additive commands.

User selected the authorized Codex LiteLLM Responses endpoint, `gpt-6.1-sol`, medium reasoning, named `LITELLM_API_KEY`. Search/embedding providers remain separate configurable prerequisites. Do not substitute models or simulated acceptance.

Pinned Paperclip 2026.1005.0 carries Codex CLI 0.160.1. Its default ACP engine rejects SSH targets; use supported SSH with explicit CLI engine. A small inherited-environment allowlist patch prevents server database/admin variables from being serialized to remote commands. Generated analysis runs as UID 1000 in a dedicated tenant runtime; model/tool secrets are scoped there. This adds a runtime and provider-egress proxy to each enabled tenant. Real smoke and workspace restoration passed; complete acceptance remains tracked in VERIFICATION.md.

Native component origins use opaque `paperclip-<id>.localhost:8081` behind whole-path membership authorization and native authentication. Explorer retains `/t/<id>/`. Component tickets are short-lived/single-use and cookies are host-only. Real Paperclip websocket proxy and membership/session revocation checks passed; native authentication remains separately required. Lab is owner-only because the pinned community edition does not enforce read-only graph roles.

The user explicitly authorized `vm.max_map_count=262144` in Rancher's VM; the setting was applied and verified without persistent host configuration changes. Controlled public fetch may use the installed workstation Cloudflare public CA through an app-owned CA-file setting; TLS verification remains mandatory.

Design references supplied with this PRD; upstream behavior is **not verified by this documentation review**. Verify during implementation and record the chosen versions/licensing/interfaces and checks actually run:

- Paperclip repository/deployment documentation: https://github.com/paperclipai/paperclip
- Paperclip Codex adapter: https://github.com/paperclipai/paperclip/blob/master/docs/adapters/codex-local.md
- Codex configuration: https://developers.openai.com/codex/config-basic/
- Codex MCP: https://developers.openai.com/codex/mcp/
- ParadeDB/pg_search: https://github.com/paradedb/paradedb
- Memgraph Lab: https://memgraph.com/docs/memgraph-lab

Paperclip supports multi-company operation, but this PRD deliberately uses separate instances rather than making client confidentiality depend on an unverified company permission boundary. Adapter authentication and configuration evolve; verify actual behavior before mounting credentials. Memgraph Lab is an advanced database interface, not a ready-made DD application. The Explorer is intentionally custom and small.

Accepted implementation refinements: dedicated reviewer runtime/home/key and shared bounded execution gate; actual count four control, eight tenant services with execution, nine including Lab. Approved ontology YAML is replayed into a separate tenant Git volume. DD serving role cannot update/delete canonical versions or audit history after explicit administrator schema installation. Publication rejects failed nested reviewer checks. Full two-tenant start is subject to aggregate configured memory reservations and an exclusive administration lock.

Accepted continuation decisions (2026-10-11): native Lab Authorization headers pass only after gateway membership/origin checks. Owner-only Lab real graph querying works; optional edition/network-dependent UI features remain limited. SSH cancellation uses an app-owned Linux descendant supervisor because native cancellation alone left detached Codex tools running. Native task/run linkage and Git commit existence require explicit administrator attestation before acceptance. Attestation does not prove historical image execution. Embedding spaces include provider, endpoint, model, dimension and extraction configuration identity. Production component origins and secure cookies are configurable; target-host acceptance remains required.

Provider discovery decision (2026-10-11): user authorized read-only discovery in recent sibling projects. DD-platform ADR0005 specifies LiteLLM text-embedding-3-large,3072dimensions,LITELLM_API_KEY; live endpoint returned200/3072. Vulcan uses public Bing RSS with no API key; add selectable bing_rss alongside Brave, preserving engagement research authorization and controlled HTTPS capture. No sibling credentials/configuration are changed.

Native attachment decision: explicit administrator import through supported Paperclip issue/attachment APIs verifies task binding, size and SHA256 and stores native task/attachment/instance IDs on the canonical Source. Retrying is additive/idempotent. Explorer uploads open their exact source link for inclusion in tasks. User authorized checking the existing LITELLM_API_KEY capabilities: model pricing discovery returns200, key/account information returns403. Hard tenant monetary limits remain a provider administration prerequisite.
