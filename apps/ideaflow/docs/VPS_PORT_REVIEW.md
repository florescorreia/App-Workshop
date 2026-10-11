> Document status: dated reference evidence. Counts, imported links, runtime state and old role names describe the recorded run; they are not a current workspace inventory. Current User/Admin behavior and command locations are in [README.md](README.md). Local scripts run from `apps/ideaflow/` after deliberate staging. For current hosting, see [VPS_IDEAFLOW.md](VPS_IDEAFLOW.md); the later web-hardening record supersedes the old closed-443 inventory.

# Public port review — 2026-10-09

Reviewed the running IdeaFlow deployment and reduced public exposure to:

| TCP port | Purpose |
| --- | --- |
| 22 | Key-only SSH administration, rate limited, monitored by Fail2ban |
| 80 | Caddy certificate HTTP validation and redirect to IdeaFlow HTTPS |
| 8443 | IdeaFlow HTTPS through Caddy |

Removed Caddy's empty default HTTPS site and the IPv4/IPv6 firewall allowance for TCP 443. Caddy no longer listens on 443. HTTP redirects to `https://vps-8104e6c8.vps.ovh.us:8443/`. Certificate renewal can continue through HTTP-01 on port 80. Existing documentation describing the empty port-443 endpoint is historical; this review supersedes that exposure inventory.

The firewall defaults to denying incoming and routed traffic. Cockpit (9090), Caddy administration (2019), and the rootless frontend binding (18081) listen only on loopback. PostgreSQL and FastAPI have no host port bindings. All three IdeaFlow containers run rootless under the dedicated `ideaflow` account and are not privileged. DHCP client UDP 68 remains required by cloud networking; DNS and Chrony management listeners are local. No public UDP application listener was added.

Added an `ideaflow-login` Fail2ban jail: eight failed POST `/api/v1/session/login` responses in ten minutes trigger a one-hour ban on TCP 8443, inheriting escalating repeat-offender bans. Its filter reads Caddy JSON access logs and uses the actual socket peer address, not forwarded headers. Local loopback remains exempt. This is a reactive source-IP ban, not application account lockout or protection against every distributed denial-of-service attack.

## Verification

- Fresh key SSH and password-authenticated administration succeeded during the review.
- SSH, Caddy and Fail2ban syntax checks passed; no systemd units were failed.
- External targeted TCP checks found only 22, 80 and 8443 reachable. Ports 443, 8444, 9090, 2019, 18081, 8000, 5432, 2375, 2376, 3306, 6379 and 8080 were filtered/unreachable. This was not a full 65,535-port scan; listener and firewall inventories were also reviewed. IPv6 firewall rules were verified locally; external IPv6 reachability was not tested.
- Public HTTPS frontend returned 200 with certificate validation enabled; readiness returned 200; unauthenticated idea access returned 401.
- One failed login to a nonexistent account produced 401 and matched the new filter. A reserved documentation address was manually banned, its nftables TCP-8443 enforcement rule inspected, and the test ban removed. Eight-failure end-to-end banning was not induced against a real client.
- Existing SSH Fail2ban protection was active and had banned actual attacking sources. Auditd and AppArmor remained active.

Configuration backups and the earlier firewall inventory are private under `/root/vps-port-review-20261009/`. The deployed filter is `/etc/fail2ban/filter.d/ideaflow-login.conf`, and its jail configuration is `/etc/fail2ban/jail.d/70-ideaflow-login.local`.

Two non-security software-properties updates remain phased by Ubuntu. Caddy's official release installation still requires an explicit update procedure as documented in `VPS_FOUNDATION.md`. No credentials, business data, containers or volumes were reset. No complete application penetration test, provider DDoS configuration change, or off-host monitoring setup was performed.
