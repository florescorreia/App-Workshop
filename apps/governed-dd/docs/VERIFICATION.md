# Local verification — 2026-10-11

Documentation addition: docs/SIMPLE_DD_TRIAL.md was expanded at the user's request to ten sequential Paperclip tasks: eight analyst tasks for scope, demand, regulation/workforce, competition, financial baseline, revenue quality, scenarios and synthesis; two separate reviewer tasks for pre-synthesis challenge and final validation. Two explicit fictional input files remain under docs/examples. Container-only checks verified ten task prompts, local input references and the historical/scenario answer key. This scenario has not been run end to end; no task was started or data imported while writing it.

The local real analytical vertical slice works. Real search and dense retrieval now pass. Full local PRD acceptance remains open for enforceable custom-provider cost limits. Future VPS target tests require a separate deployment instruction. No VPS contact, deployment or mutation was performed. All Python, Node and Codex ran in containers using verified Rancher Desktop Moby context `default`; Compose configuration was validated before applying it. Normal setup/start is empty. Fictional tenants, sources and tasks were explicit additive acceptance actions.

## Local access and topology

Portal http://localhost:8081; Keycloak http://localhost:8081/identity. Enter Paperclip through engagement Overview: opaque `paperclip-<tenant>.localhost:8081` requires current portal membership and native login. Lab is an owner-only opaque origin. Explorer uses `/t/<tenant>/`. Portal credentials are private `<login>.password` files in `governed-dd-identity-private`; native credentials are `native-<login>.json` in each tenant Paperclip volume. Bootstrap identity admin is governed-dd-admin, with its private app secret file. No passwords are documented here.

Four control services: gateway, portal, Keycloak, dedicated control PostgreSQL. Base tenant has five: dedicated PostgreSQL, governance/MCP, graph, Explorer, Paperclip. Isolated analyst, reviewer and egress add three; optional Lab adds one. A runs nine services, B five. Separate tenant DB/network/file/Git/home credentials and volumes are retained. VPS tenant ingress bridge adds a preparation-only service. Runtime analytical Git is on volumes, never nested under platform source Git.

Acceptance A `a4e176281f3c47d081b3b623` is Fictional Northstar Components; B `b5e287392a4d58e192c4c734` is Fictional Harbor Services. Alice belongs to A, Bob to B, Carol to both. Existing v1 fixtures use shared synthetic revenue content to test isolation; labels do not imply real company evidence. No live/client conclusions are represented.

## Executed checks

| Check | Result |
|---|---|
| Builds | Governance, React/TypeScript/nginx, pinned Paperclip adapter, SSH runtimes and portable tooling built |
| Unit checks | 14 passed, including immutable content-addressed bytes, unsafe HTTPS/DNS rejection, incomplete manifests and agent acceptance denial |
| PostgreSQL | Actual PostgreSQL17.11, vector0.8.6, pg_search0.26.1; real BM25 known evidence score0.28768212 |
| Registry | Exact version/locator validation, hash verification, additive duplicate/retry behavior, incomplete publication denial and deterministic calculation passed |
| Database permissions | NOLOGIN owner, DD SELECT/INSERT canonical records/audit, UPDATE only jobs/chunks/outbox; canonical UPDATE/DELETE and schema CREATE denied |
| Graph | Real Memgraph projection, bounded traversal, typed relation/filter validation, replay/idempotence passed; pending failures remain visible |
| Ontology | Canonical proposals, owner approval, agent approval denial, idempotent approval and approved YAML on tenant Git passed |
| MCP | Real discovery/provenance, authentication and unknown tenant parameter rejection passed |
| Portal authorization | Alice/Bob/Carol filtering, guessed routes, CSRF, next-request membership removal passed |
| Tenant service boundary | Both tenant service token checks, agent publication denial, other-tenant DNS denial and absent engine socket passed |
| Runtime boundary | UID1000, forbidden DB/admin/native credentials/host keys, no DB/other-tenant DNS, no socket/direct internet and provider allowlist denial passed |
| OIDC/browser | Authorization code/PKCE, callback, Alice filtering/guessed routes, finding graph1440/390px, no checked page JS errors/overflow passed |
| Carol/browser | Exactly two memberships, explicit A/B switch, exact v5/v4 comparison with linked evidence/output versions and logout passed |
| Native Paperclip | Alice/Carol A and Bob/Carol B native API login/single-company membership passed; Alice dashboard rendered and visually reviewed |
| Native streams | Earlier real native authenticated Paperclip websocket membership revocation, whole-path/static/API/attachment denial and sign-up-disabled check passed |
| Lab | Owner HTTP entry, direct/reviewer denial, CSRF/logout, real Memgraph3.6.0 bounded Cypher query and active-stream logout/next-request denial passed |
| Provider | Real LiteLLM Responses and Codex gpt-6.1-sol medium succeeded; no model substitution |
| Controlled fetch | Python.org HTTPS capture51862bytes with TLS verification and configured installed Cloudflare public CA passed |
| Formats | CSV/DOCX/XLSX, safe HTML script exclusion, scanned/blankPDF explicit OCR failure passed |
| Ingestion cancellation | Cancelled job/original bytes retained, checked source zero chunks passed |
| Runtime cancellation | First native cancellation left detached Codex/sleep active. Fixed Linux descendant/SSH supervisor; repeat native API cancellation exited both and released shared gate |
| Concurrency/timeouts | Same-tenant lock contention and cross-reviewer lock denial passed; bounded timeout returned124 |
| Publication | Independent v5 reviewer validation, failed nested v4 check denial, synthetic human accepted copy, immutable old version/new-review gate and agent acceptance denial passed |
| Provenance | Native API confirmed successful historical run/task/instance; Git verified commit exists; administrator attestation persisted and v5 validation true |
| Persistence | Rebuild/restart retained records, source bytes, ontology/workspace and native state; final registry regression passed |
| Secret checks | 114 source text files zero configured secret-value matches;19 native transcripts zero configured matches/zero JWT-pattern files |
| Source/workspace | No nested source Git; only root changes are9-line custom dispatch and14-line catalog registration; other apps unchanged |
| Portable tooling | Container engine identity/doctor and14 unit tests passed; full Unix-host operations not executed |
| VPS preparation | Final control/fullA immutable-image Quadlet inventories and dependency health-gate render passed; no target installation |

Native browser test initially skipped its form due a fixed delay. It now waits for visible form and hidden form after sign-in; final live dashboard passed and was visually reviewed. Native UI still calls administrator-only adapter/experimental endpoints and receives403; consultant company/task navigation remains accessible. Lab retains upstream optional module/version/notification/storage errors and a standalone editor bootstrap JS warning; core real graph query works. Community privilege management requires enterprise, so Lab is owner-only and does not claim enforced read-only rights.

## Real analytical result

Paperclip created an actual Codex SSH run, ingested supplied synthetic evidence, captured a public page, calculated `(120/100-1)*100`, wrote/committed analysis code and registered definition, finding, run, artifact, deliverable and graph references. Real AnalysisRun `493446f8-a9cc-46cb-8889-03a2c1f40df7` v5, Deliverable `f1bd2434-5041-4088-b40c-e3ecd95df135` v5, report Artifact `8228b37d-fe93-443f-8fe7-e83f8d802a5b` v1. Code commit `2a6e6dddfe24a219d67797bc7178c06bcec96db4` persists. Reviewer FIC-14 used a separate runtime/home/credential/context and recomputed19.999999999999996 within1e-10, inspected exact evidence/report and registered checks. v4 stale report was correctly invalidated; final v5 valid. Human acceptance of this real result remains deliberately unperformed; only a separate explicit synthetic copy tested acceptance.

Native task `8656c192-e27a-4b3a-927a-924129fb9225`, run `c382dbe8-1078-490b-9d18-425428a2937d` were verified using supported native APIs. An administrator attestation is now required before publication. This confirms linkage, successful status and commit existence, not proof that declared historical code/image executed. Independent calculation/report evidence remains required. Historical image declaration is explicitly administrator-inspected. Harness logs capture supported events; comprehensive capture is not claimed. Narrative/web reruns are nondeterministic.

Cancellation repeat native run status is cancelled, started20:51:53UTC, finished20:52:29UTC. Remote Codex/sleep were absent and gate acquired afterward. The supervisor adopts and cleans detached descendants; Paperclip remains the actual execution harness.

## Commands actually used

Run from repository root unless stated otherwise:

```powershell
docker --context default run --rm --entrypoint python governed-dd-governance:0.1.0 -m pytest -q -p no:cacheprovider /app/tests/test_security.py
docker --context default exec -e PYTHONPATH=/app governed-dd-control-portal-1 python /app/tests/access.py
docker --context default exec -e PYTHONPATH=/app governed-dd-a4e176281f3c47d081b3b623-governance-1 python /app/tests/integration.py
docker --context default exec -e PYTHONPATH=/app governed-dd-a4e176281f3c47d081b3b623-governance-1 python /app/tests/mcp_check.py
docker --context default exec -e PYTHONPATH=/app governed-dd-a4e176281f3c47d081b3b623-governance-1 python /app/tests/publication.py
docker --context default exec -e PYTHONPATH=/app governed-dd-a4e176281f3c47d081b3b623-governance-1 python /app/tests/database_roles.py
powershell -NoProfile -ExecutionPolicy Bypass -File apps/governed-dd/scripts/attest-run.ps1 -Tenant a4e176281f3c47d081b3b623 -Analysis 493446f8-a9cc-46cb-8889-03a2c1f40df7 -Version 5 -Context default
```

Runtime security script was copied into the runtime and executed with `docker exec --user1000 ... python3 /tmp/runtime-check.py`. Browser scripts run from the Playwright test image with app tests/evidence mounts, private identity-volume mount and the relevant gateway network. No secret values are arguments. Tests/oidc.cjs, consultant.cjs and lab-browser.cjs were executed. Private evidence screenshots: local/evidence/graph-desktop.png, finding-mobile.png, native-paperclip-desktop.png, version-comparison.png and lab-desktop.png. Layouts were visually reviewed. Build instructions are in SETUP.md; frontend dependency audit had zero vulnerabilities after pinned Vite6.4.4 update.

## Recovery

Fresh encrypted backup `backups/20261011-165825` quiesced only app services, packed all persistent volumes/private configuration and restarted live. Fresh restore prefix `governed-dd-restore-52a76cdafce2`, range10.251.x/24, authenticated every archive checksum. Complete service copy had no published ports/external egress; analytical runtimes remained stopped. tests/restored_stack.py passed both registries, hashes, BM25, graphs, native consultant login, ontology Git and code. Restored OIDC/portal filtering/graph/finding desktop/mobile and native dashboard browser passed. Copy stopped; volumes retained. No model rerun in isolated copy.

Defects fixed: retain root volume numeric ownership/mode; restore private provider/runtime/governance ownership; skip only pinned regenerable upstream skill links and exact Codex tmp executable aliases. Arbitrary absolute links remain rejected. New fresh-prefix restore hit the new provider-secret ownership defect, which was corrected in that copy and the script; no live overwrite. One earlier attempted copy failed and its partial volumes were retained outside acceptance. Never run two PostgreSQL containers on the same volume. Earlier accidental overlapping restored database processes were stopped and excluded. Backup-key recovery must be independent.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File apps/governed-dd/scripts/backup.ps1 backup -Context default
powershell -NoProfile -ExecutionPolicy Bypass -File apps/governed-dd/scripts/backup.ps1 restore-test -Context default -Backup <absolute-folder>
powershell -NoProfile -ExecutionPolicy Bypass -File apps/governed-dd/scripts/restore-stack.ps1 -Prefix <printed-prefix> -Context default -SubnetPrefix <checked-10.x-prefix>
powershell -NoProfile -ExecutionPolicy Bypass -File apps/governed-dd/scripts/verify-restored.ps1 -Prefix <printed-prefix> -Context default
```

The verifier attaches its transient container to control and both tenant ingress networks explicitly. Keep canonical restored bytes, not only index counts. Graph/search may be rebuilt. Test stop preserves volumes. Named volumes alone are not backups.

## Pinned capabilities and measurements

Paperclip2026.1005.0 MIT commit467125fafb47a8520856504fecc48d6e32055db1, Codex0.160.1. Supported SSH uses engine CLI; ACP rejected SSH. Small upstream inherited-environment allowlist prevents server secrets serialization. Bubblewrap namespaces failed on this VM and are not an accepted boundary. Generated code runs UID1000 in dedicated runtime; no host/engine/admin credentials. Analyst and reviewer share bounded gate but have separate workspace/home/tool credentials. Model key is runtime-only; custom auth file empty.

ParadeDB0.26.1-pg17, Keycloak26.4.7, Memgraph/Lab3.6.0 immutable digests in render.py. Actual extension versions above. Base image digests were inspected; PostgreSQL/nginx renderer pins added. Python/frontend direct/transitive packages locked. Final Python37 scripts and PowerShell syntax passed; shell parsed in prior checks. Prepared VPS files need installed target generator validation.

Engine14CPUs/15.33GiB. Live steady sample about3.1–3.3GiB; small analytical sample about3GiB earlier, not peak guarantee. Persistent live volumes about1.14GiB, plus images/backups. Graph volumes~315MiB each, PostgreSQL~175/167MiB, control75MiB, workspace~75/19MiB. Explicit1,120,000-byte synthetic TXT benchmark produced623chunks in50.220seconds initial timestamp interval; retry0.020seconds is not first-ingestion speed. Dense disabled. Paperclip smoke used127842 raw input/1011 output tokens including harness/cached context.

Configured full B execution start refused20.62GiB running/proposed reservation plus2GiB headroom versus15.33GiB engine. No RAM change authorized/applied. Stop inactive stacks or review additional RAM. Temporary restored copy was bounded, model-disabled and stopped after checks; its startup is not evidence of production peak admission. Rancher warns swap limits unavailable. User explicitly authorized vm.max_map_count262144; applied/verified without persistence. Future starts may need authorized VM setting again.

Automatic172.24/16 allocations collided with LiteLLM172.24.173.140. Only app-owned B runtime/provider networks moved to checked10.253.20/21. Other networks/volumes/apps preserved. Future execution networks require explicit reviewed subnet values.

## Precise outstanding prerequisites and limitations

1. Real external search and embeddings are configured and checked; see the provider continuation below. Bing RSS is a public, uncontracted interface and can become unavailable.
2. Provider-inclusive encrypted recovery passed; see the final continuation. The isolated copy is stopped and retained.
3. Cost enforcement: custom LiteLLM Paperclip reports$0; company/agent budgets are not an authoritative bill or enforceable monetary limit. Configure tenant-specific LiteLLM virtual keys with hard token/cost/rate limits and verify denial, or provide actual pricing/accounting capability. Runtime time/concurrency bounds work. Do not describe these as monetary enforcement.
4. VPS: actual DNS/certificates, production Keycloak build, Caddy origins, cross-account mTLS transport/reachability, resource admission, Quadlet generator/readiness, encrypted off-host destination/rotation and reboot/autostart tests require a separately authorized deployment. Reviewable templates/runbook prepared; none target-tested.
5. Unix: portable core administration implemented; doctor/test executed in tooling container. Full Unix-host lifecycle/recovery and wrapper operations remain unexecuted. Explicit native attestation currently has a PowerShell command.
6. Historical provenance: API confirms run/task and commit existence; runtime digest is administrator-declared/inspected, not cryptographic execution attestation. Native uploads use documented Explorer source link workflow; Paperclip attachments are not silently indexed. Explicit native attachment import now verifies and stores task/attachment/instance linkage; see the final continuation.

A final repeat of native authenticated stream regression was rejected by automatic approval review before execution; the command used private credentials in a transient container and no further reason was provided. Earlier native stream test passed, latest native API/browser login passed, and latest Lab session stream denial passed. No new native stream repeat is claimed.

PRD status remains implementation/acceptance in progress. These results supersede historical in-progress notes; unsupported or unexecuted integrations are not counted as passed.

## Provider continuation — 2026-10-11

User directed read-only provider discovery in sibling projects. DD-platform/backend/dd_platform/config.py and ADR0005 specify LiteLLM text-embedding-3-large,3072dimensions,LITELLM_API_KEY. The existing environment variable was injected into separate app-owned private tenant provider files; no sibling files/credentials were changed. Live /embeddings returnedHTTP200 and3072dimensions. Vulcan/scripts/web_search.py uses Bing RSS without a key; recent sibling source/env-name search found no configured paid search-provider key. Added selectable bing_rss alongside Brave and verified live results using controlled DNS-pinned HTTPS fetch and the configured public CA.

Executed tests/providers.py in A and B: known evidence reindexed, real cosine distance0.691411, valid3072dimensions, BM25+dense RRF hits, incompatible endpoint-space exclusion and original source hash preserved. Full A reindex625chunks completed using batches32. B has1chunk. A live public query returned5results and captured/registered8056bytes from Python's official documentation. Public research authorization denial passed. Agent-facing tests/provider_mcp.py passed real dense search, tenant override rejection and live external search. tests/vector_authorization.py passed both dense APIs missing/wrong-tenant credential404 and fixed tenant binding even with an override parameter. Private transient test token copies were removed afterward. Registry/publication regression and14unit tests passed.

Command-line Domain operations now load only declared named provider secrets just as serving operations do. Reindex updates batches transactionally; incompatible spaces are excluded, successful partial batches remain replayable. Search reports its actual BM25/dense counts and embedding-space identity. Bing discovery snippets are never full-source evidence. Default env template records verified settings; public research remains false by default. No client text/names were sent in these checks.

Commands: scripts/governed-dd.ps1 provider-configure -Tenant <id> -Context default; docker --context default compose -f <tenant-manifest> up -d --no-deps governance; docker --context default exec -e PYTHONPATH=/app <governance-container> python /app/tests/providers.py; provider_mcp.py likewise. Execute public provider fixtures explicitly and additively only. Full reindex uses the existing reindex management action.

Earlier missing search/embedding blockers are resolved. Cost enforcement and future VPS target tests remain as documented. Bing RSS has no service guarantee; fail visibly on network/parser errors. This continuation does not assume native model search support or claim a paid search credential was found.
## Final continuation � 2026-10-11

Provider-inclusive backup backups/20261011-185137 quiesced all live Governed DD services, encrypted volumes/private configuration and restarted them. All archive checksums authenticated into fresh volumes, prefix governed-dd-restore-718bb03b8b1f, reviewed10.250.x/24 networks, no published ports or provider egress. Complete restore checked real Keycloak realm, both registries/source bytes/BM25/graphs/native consultant login and ontology/analysis Git. tests/restored_vectors.py verified every restored source hash, tenant-scoped key presence (no value output), configured model/embedding space and625 A/1 B vectors of3072dimensions. No provider call occurred in the isolated copy. Copy stopped with all volumes retained. The later additive native attachment fixture is newer than this recovery point.

Search snippets now bound280characters/three lines, with full exact source still accessible. Rebuilt frontend screenshot hybrid-search.png reduced from1440x15917 to1440x3178 and was visually reviewed. Carol real hybrid search, deliberate context switch, exact version comparison and logout passed. The final frontend also opens the uploaded exact source automatically. Docker nginx now resolves upstream service names dynamically with127.0.0.11; portal replacement retains gateway reachability without reload after its networks are attached. A browser attempt during replacement failed before attachment; repeat passed. Full portal recreation loses manually attached ingress networks, so managed up/tenant-start reattaches them; raw Compose recreation needs the same step. VPS Podman DNS is separately documented, not assumed portable.

Explicit native attachment API fixture uploaded fictional-attachment-v1.txt to the existing acceptance task. scripts/import-attachment.ps1 verified native issue/attachment binding, byte size/SHA256, registered Source7ecfce63-335f-45d2-9694-a8c10da58850v1 with task/attachment/instance IDs and indexed it. Repeat retained the same ID/version. Attempt in B rejected the unavailable A task. Portable tooling image import-attachment command passed the same idempotent check. Transient byte copies removed afterward; originals remain on the artifact volume. No automatic source import. The example native upload test supplies Origin as required by native CSRF enforcement; first omitted-Origin upload failed403 and was fixed.

Existing named LITELLM_API_KEY capability probe: /model/info200, selected LLM/embedding pricing fields present; /key/info403. No upstream configuration mutated. Key administration/virtual-key hard-limit enforcement remains unavailable to this key. Required prerequisite: a scoped authorized LiteLLM administrator or preconfigured separate tenant virtual keys with demonstrated hard budget/token/rate denial. Pricing metadata alone is not enforcement. Current time/concurrency/cancellation bounds work; Paperclip custom monetary accounting remains$0.

Final builds passed: Explorer image config sha256:95def0b4b4faf25bc7d99d073325baf0c902385ae58ee50a9f99b84e79d23b9e, governance sha256:a8afc09aaecc80dc1c48cd0b1d44ae30de6aea519e2aa33049c68fe8cf944c53, administrator tooling sha256:89d157d959f4a92f3325fed74f4d5781536348da3fe407b6683d52ee19e83b5e. Serving code unchanged by final test additions.14unit checks, final registry/publication/access regression passed. Source scan122textfiles0secretmatches, including individual values in private provider JSON;42Python files and PowerShell scripts syntax passed. Final steady18services sample~2.88GiB; no new analytical peak measurement. Other apps/root Git configuration untouched; root changes remain23lines of catalog/dispatch only.

Recovery commands additionally use verify-restored.ps1 (now includes restored_vectors.py). Native import commands and portable equivalent are in SETUP.md. Browser OIDC test now uses actual native-alice.json; earlier final repeats failed because a historical test filename no longer existed. Those failures are not counted as passed.
Final corrected OIDC browser test passed Alice portal filtering/guessed routes, exact finding graph1440/390px and native consultant login; native dashboard screenshot visually reviewed. Initial MCP repeat used an older serving image test path and failed before execution; copied test invocation recorded separately.
Final copied tests/provider_mcp.py invocation passed real dense retrieval, tenant override denial and authorized Bing external search. Source has no nested Git outside ignored private upstream material; no running containers remain in the final restore prefix. Final native dashboard renders consultant tasks; upstream dashboard recent-run cards retain Loading task labels despite completed status, a native display limitation. The native attachment and later browser upload fixtures postdate the verified recovery point.
Final consultant browser check includes source upload and exact source-link opening and passed. Browser retry key now hashes filename plus bytes to preserve idempotence. Latest Explorer config digest is sha256:c9efbe7f831278f4c89d2906e72095785ac1da82f28907e5038f07ae20f95a7a, superseding the earlier final build digest. Native import PowerShell and portable retry passed; final PowerShell syntax rechecked. Final secret scan122files0matches.
