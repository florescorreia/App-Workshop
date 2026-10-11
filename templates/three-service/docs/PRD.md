# {{APP_TITLE}} product contract

Status: **Product definition required**.

Describe your users, the problem, the workflow, records, access rules, calculations, acceptance criteria and initial empty experience here before implementing the actual app. The generated starter supplies local login and a small durable notes surface to exercise the infrastructure; notes are ordinary user records and start empty. It does not implement IdeaFlow or invent your product requirements.

Operational defaults: three services, container-only development, PostgreSQL-authoritative records, transactional note events, optimistic concurrency, unique app identity, local-only frontend publishing, independent VPS account/storage when deployed. No automatic showcase data, direct production resets, shared application passwords or Git repositories nested inside this folder.

Before production: replace the starter notes surface with the specified product; define least-privilege database roles/migrations and account management, security policy and failed-login protections, then complete meaningful business tests, browser/layout review, restart/rebuild preservation, isolated restore and current-data handover. The generated VPS package is a reviewable release, not automatic authorization to publish an unfinished app.
