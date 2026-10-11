# {{APP_TITLE}} architecture

Status: generated starter, awaiting product implementation.

React/TypeScript static output is served by nginx, which proxies same-origin `/api/` to FastAPI. FastAPI reads/writes PostgreSQL. Only the frontend publishes locally on loopback {{LOCAL_PORT}}. Compose project {{APP_SLUG}}, volume {{APP_SLUG}}_pgdata and all credentials are independent of other apps. Build/development/test tools run in transient containers.

The notes example uses local Argon2 accounts, a server session with HttpOnly/SameSite cookie, CSRF header, explicit origin checks, versioned note updates and transactionally appended note events. It starts with bootstrap Admin and no notes. Starter schema setup is a single idempotent SQL script and runtime currently uses the database owner role. This is not the finished product's migration/security design.

Before production implement the [PRD](PRD.md), versioned migration process, least-privilege runtime roles, account administration/recovery and failed-login protections appropriate to the product. Update this document with actual modules, records, access boundaries, data flows and recovery behavior. Follow [shared hosting](../../../docs/APP_WORKSHOP.md); generic VPS env/health/deployment assets must be adapted if your finished runtime differs from the starter. Do not change another app to fit this one.
