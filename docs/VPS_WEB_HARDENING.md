# External assessment remediation — 2026-10-09

Applied the assessment improvements at Caddy and updated `infra/vps/ideaflow.caddy` so future publication retains them. Application containers, business data and credentials were not changed.

- Public `/api/docs`, `/api/openapi.json`, their subpaths, and paths containing dotfile segments return 404. Documentation remains accessible privately through the loopback frontend/SSH tunnel if needed; the backend has no public port.
- Server and Via identification headers are removed from application responses.
- An enforcing Content-Security-Policy restricts scripts/connections to the same origin, forbids objects/frames and restricts base/form destinations. Inline styles remain permitted for React/Plotly visualizations; data/blob images and blob workers are allowed for chart functionality. No unsafe-eval or inline script permission was added.
- HTTPS responses send `Strict-Transport-Security: max-age=86400`, a deliberately short initial one-day policy. Neither preload nor includeSubDomains is enabled on the provider-owned hostname.
- Restored TCP 443 as a required HTTPS redirect to the existing application port 8443, preserving paths and queries. HSTS otherwise upgrades port-80 navigation to closed port 443. Current public TCP ports are 22 (SSH), 80 (HTTP redirect/certificate validation), 443 (HTTPS redirect), and 8443 (IdeaFlow). Management/internal ports remain private. This supersedes the earlier port review's closed-443 inventory.

## Actual verification

- Caddy validation and reload passed. External TLS-validated HTTP checks confirmed docs/dotfiles return 404, CSP/HSTS are present, and Server/Via are absent.
- An external Python TLS-validated request to 443 received a 308 preserving `/ideas?tab=history` in the redirect to 8443. VPS-local curl with certificate verification also confirmed the redirect.
- The existing full public browser regression passed after applying the policy: login, secure cookie checks, desktop/mobile pages, financial/process views, history and logout, with no business mutations.
- Added browser assertions for security headers, blocked routes, and securitypolicyviolation events. The enhanced regression passed with zero CSP violations using Playwright in the detected Rancher Desktop Moby context `default`.
- A browser navigation test to standard port 443 failed with ERR_CERT_AUTHORITY_INVALID in the container/workstation network path. The cause was not established; earlier observations indicate an intermediary on standard web traffic. Certificate verification was not disabled. Therefore port-443 browser/HSTS navigation through this specific network remains a limitation despite independent validated HTTP checks passing; it should be checked from another network before increasing HSTS duration. The failed browser-navigation assertion was removed; the 8443 regression remains enforced.
- Caddy, Fail2ban, auditd and AppArmor stayed active; SSH configuration validation and fresh administration connection succeeded.

Backup: `/root/vps-web-hardening-20261009/ideaflow-before.caddy` (private on VPS). Reverting HSTS requires serving `max-age=0` over trusted HTTPS; deleting the header alone does not clear browser-cached policy. Keep the HTTPS redirect available during rollback and cached-policy expiry.

These changes improve configuration defenses; they do not substitute for authenticated authorization testing or comprehensive penetration testing.
