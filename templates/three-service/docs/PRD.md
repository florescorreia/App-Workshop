# {{APP_TITLE}} — Product Requirements Document

Status: **Draft — product definition required**
Owner: [person responsible for the product]
Last updated: [date]

This is the implementation contract for `apps/{{APP_SLUG}}/`. Replace the bracketed prompts with your requirements. A brief can start with ordinary prose; the sections below help make it buildable. Use **Ready for implementation** when the intended scope and acceptance criteria are clear. The starter's empty notes screen is an infrastructure example and is not a product requirement.

## 1. Problem and outcome

Describe the problem, who experiences it, how they handle it today and what a useful result looks like. Include one concrete example. Explain how you will judge whether the app helped.

## 2. Users and responsibilities

List the intended users, what each needs to accomplish and what requires restricted access. Decide whether records belong to individuals, teams or everyone in the workspace. Describe account creation, sign-in, sign-out, password recovery/reset, deactivation and handling of historical authors. Use the simplest roles that meet the actual need; IdeaFlow's roles/workflow are not inherited requirements.

## 3. Scope

List the capabilities required in the first usable version. Separately list deferred features and explicit exclusions. Name any external integrations; if none are required, the app should work without an external runtime API. Identify information that is sensitive and retention needs.

## 4. User journeys and screens

Describe the first sign-in experience with no records. For each main journey, give the trigger, inputs, actions, saved outcome, success feedback and recovery from errors. Include an end-to-end example using your own domain. List screens, navigation, search/filter/sort requirements, mobile behavior, keyboard access, loading/error/empty states and any exports.

## 5. Records and terminology

Define entities and fields in everyday language: required/optional, defaults, permitted values, uniqueness, relationships and ownership. Distinguish missing/unknown from zero or false. Specify currencies, units, date/timezone rules and attachments if needed. Include create/edit/archive/restore/delete behavior and what happens to related records/history.

## 6. Workflow and business rules

If records have states, list states and valid transitions, who can act, prerequisites, reasons and backward/correction paths. Define which actions are explicit commands. Describe validation, concurrent edits, cancellation and history. If no workflow is needed, say so. Persist business changes and their audit evidence together in PostgreSQL; reject stale edits with actionable feedback.

## 7. Calculations and reporting

Define each metric with its formula, units, time horizon, included/excluded records and treatment of missing data. Supply worked examples and edge cases, including zero denominators and partial data. Explain chart date ranges, filters, supporting tables and drilldown. If the app has no calculations or dashboards, state that explicitly.

## 8. Initial data, imports and exports

Start with a usable empty workspace and the necessary bootstrap account/configuration. Describe any reference values genuinely needed at boot. Fictional examples must be an explicit optional command, visibly identified, additive and idempotent. Specify import validation/dry run/provenance and conflict handling if imports are in scope. Never seed showcase data on startup or overwrite live records during an import.

## 9. Architecture and operations

Default stack: React/TypeScript served by nginx, FastAPI and PostgreSQL — exactly three long-running services. Use containers for build/development/test tools and the discovered Rancher Desktop Moby context explicitly for local Docker Compose. Backend/database remain private; only the loopback frontend publishes locally. Keep this app's project, images, volume, ports and credentials independent of every other app.

Describe versioned migrations, least-privilege runtime database access, session/authentication/CSRF protections, backups, isolated restore, health checks and resource needs. VPS deployment uses the shared secured rootless Podman/Quadlet and Caddy foundation with a dedicated app account/volume. Credentials stay in private local files or Windows User environment variables and protected server files; no credentials in docs/source/frontend. Publishing requires a separate user instruction after local acceptance. Local data transfer is a separate verified handover.

## 10. Acceptance criteria

For each main capability, write an observable **Given / When / Then** example. Cover invalid inputs, unauthorized operations, stale concurrent edits, atomic history, empty screens and missing data. Include the full main journey and at least one correction/rework path where applicable. State practical volume/performance expectations.

Required delivery checks: meaningful business/API tests; browser journey and desktop/mobile layout review; restart/rebuild persistence; isolated backup/restore; actual health/login verification. Record commands/results and limitations in `docs/VERIFICATION.md`; provide a non-technical `docs/USER_GUIDE.md` with the real UX. Do not claim a check passed unless it ran.

## 11. Open questions and decisions

List unresolved product choices and their impact. Routine library/implementation choices can use engineering judgment within this contract. Ask about a product ambiguity that changes the outcome; keep progressing on independent work. Record accepted changes here so the PRD remains authoritative.
