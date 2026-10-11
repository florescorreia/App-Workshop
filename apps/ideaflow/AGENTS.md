# IdeaFlow implementation contract

Read docs/PRD.md before changing domain behavior. Exactly three long-running services: React/nginx frontend, FastAPI backend, PostgreSQL. Build and test with containers, using the detected Rancher Desktop Moby context explicitly. Preserve other projects, configuration and volumes; never use destructive resets. PostgreSQL is authoritative. Every business mutation and append-only event share a transaction, with optimistic concurrency. Stage, disposition, approval and verification use explicit validated commands. Startup is empty except references and bootstrap Admin. Demo imports are explicit, additive, validated, replayed and batch-idempotent. Never commit credentials or load demo data automatically. Record actual verification and limitations.


This contract applies only to apps/ideaflow. Read accepted PRD amendments before original V1 requirements. Current business actions use User/Admin accountability, and no new app inherits this domain. Run app-relative scripts from this folder; shared scripts run from the workspace root. Preserve the reference VPS and start local containers only for deliberate testing.
