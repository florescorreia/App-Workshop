# Non-destructive external assessment — 2026-10-09

Authorized target: the user's VPS `40.160.88.11`, hostname `vps-8104e6c8.vps.ovh.us`, and IdeaFlow HTTPS on TCP 8443. Scope selected by the user: external, unauthenticated, non-destructive assessment. Requests were low concurrency, with no credential guessing, successful login, business mutation, exploitation, denial-of-service test or data export. No server configuration was changed during this assessment.

## Results

No authentication bypass or sensitive-file disclosure was demonstrated in the checks below. This is a limited assessment, not a certification or comprehensive penetration test.

| Check | Observed result |
| --- | --- |
| Targeted TCP exposure | Only 22, 80, 8443 reachable. 443, 8444, 9090, 2019, 18081, 8000, 5432, 2375, 2376, 6379, 8080 filtered/unreachable. |
| TLS | TLS 1.2 and 1.3 negotiated with certificate validation. TLS 1.0 and 1.1 rejected with protocol-version alerts when client legacy cipher support was explicitly enabled. |
| Public frontend/readiness | Returned 200. |
| Unauthenticated ideas/session | `/api/v1/ideas` and `/api/v1/session/me` returned 401. |
| Forged session cookie | Invalid `__Host-ideaflow_session` cookie did not grant access; ideas returned 401. |
| Cross-origin login | POST with an unrelated Origin and empty JSON returned 403, same-origin requirement. No valid credential was submitted. |
| CORS preflight | Unrelated-origin OPTIONS returned 405 without Access-Control-Allow-Origin. |
| HTTP TRACE | Rejected with 405. |
| Sensitive-file probes | `/.env`, `/.git/config`, `/server-status`, `/actuator/env` returned the same bytes as the React frontend; no configuration/file disclosure observed. |
| SQL-like unauthenticated search | Ideas request with a SQL-like query string returned 401. This tests the authentication boundary, not authenticated SQL injection resistance. |
| Existing headers | X-Frame-Options DENY, X-Content-Type-Options nosniff, Referrer-Policy same-origin present on frontend. |

## Observations to address

1. **Public API documentation/schema (informational).** `/api/docs` and `/api/openapi.json` returned 200; the schema reveals API structure. This is common and is not a demonstrated authentication bypass. Decide whether experimental users need it; otherwise restrict these paths to authenticated administrators or private access.
2. **No Content-Security-Policy on frontend (defense-in-depth gap).** Add a policy compatible with the actual scripts/styles and test browser behavior before enforcing it. Lack of CSP alone does not demonstrate XSS.
3. **No Strict-Transport-Security header (defense-in-depth gap).** A hostname-wide HSTS policy needs care here: the app uses nonstandard HTTPS port 8443, and HSTS can upgrade plain port-80 visits to now-closed port 443 before the intended redirect. Choose a canonical routing design and test before enabling HSTS. Do not preload or include subdomains of the provider-owned hostname.
4. **Server version disclosure (informational).** Frontend responses disclose `nginx/1.28.0`. Suppress version details to reduce easy fingerprinting; this does not replace patching.
5. **SPA fallback masks nonexistent sensitive paths (informational).** No files leaked, but explicit 404/deny behavior for dotfiles would make probing clearer and guard against future deployment mistakes.

An alternate Host header request produced an ambiguous empty 200 response. Requests on this workstation can traverse a corporate network intermediary (an earlier HTTP check showed intermediary headers), so this is not recorded as a confirmed host-header weakness. It needs corroboration through an independent external vantage point before drawing conclusions.

## Limits and follow-up

No authenticated authorization/IDOR checks, stored/reflected XSS testing, upload testing, dependency-CVE analysis, credential attack, exhaustive port scan, external IPv6 check, or resource-exhaustion testing was performed. Previously verified Fail2ban source-IP bans were not repeatedly triggered in this assessment. Browser CSRF and session lifecycle behavior were not exercised end to end. Infrastructure firewall/binding verification is recorded separately in `VPS_PORT_REVIEW.md`.

Recommended next work: remediate the configuration observations with browser regression verification, then assess authenticated role/object boundaries in an isolated test workspace with dedicated test accounts and explicit permission to create test records. Production business data should remain untouched.
