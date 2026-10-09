# Podman and Caddy foundation — 2026-10-09

Subsequent deployment: IdeaFlow now runs at **https://vps-8104e6c8.vps.ovh.us:8443** under its dedicated rootless account. See [VPS_IDEAFLOW.md](VPS_IDEAFLOW.md). The initial foundation evidence below describes the state before that deployment.

Installed on `vps-8104e6c8.vps.ovh.us` (`40.160.88.11`): rootless-capable Podman 5.7.0, Quadlet generators, uidmap/passt, and host Caddy 2.11.7. IdeaFlow has not been deployed; its existing local container configuration is unchanged.

## Public routing

The existing OVH hostname obtained a trusted Let's Encrypt certificate. No purchased domain is needed. Caddy handles automatic certificate renewal, HTTP redirects, and HTTPS routing. Keep TCP 80 and 443 open for certificate validation and the shared endpoint.

`https://vps-8104e6c8.vps.ovh.us/` currently returns an intentionally empty 404. Applications will use individual HTTPS ports, such as `:8443`, `:8444`, and `:8445`. None of those application ports remains open or configured yet.

For an application frontend published only on loopback port 18081, add `/etc/caddy/apps.d/app-name.caddy`:

```caddyfile
vps-8104e6c8.vps.ovh.us:8443 {
    reverse_proxy 127.0.0.1:18081
}
```

Then validate, reload, and open only that public port:

```bash
sudo -u caddy caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
sudo ufw allow 8443/tcp
```

Use explicit `https://` URLs. Keep container ports bound to `127.0.0.1`; only Caddy's application ports are public. Backends and databases require no published ports. Applications must support their actual external origin, including port, in authentication redirects and frontend configuration. Cookies are scoped by hostname/path, not port: use unique cookie names per application and avoid assuming ports isolate cookies or untrusted applications. A stopped application with a retained route returns a gateway error until restarted.

Caddy's admin API is bound to `127.0.0.1:2019`; it is not public. HTTP/3 is disabled, so no UDP web port is needed. Certificate/account data resides in `/var/lib/caddy`, and configuration in `/etc/caddy`. Protect and back up certificate private keys. Access logs rotate at 10 MiB with five retained backups. Caddy has a 512 MiB memory ceiling and one CPU quota; observed idle memory was approximately 10 MiB.

## Rootless application lifecycle

Use a dedicated Linux account per real application, with subordinate UID/GID ranges and `loginctl enable-linger ACCOUNT` so its user systemd manager persists after logout. No application accounts or automatic-start application targets have been created yet. Rootless containers were tested under `ubuntu` only and removed afterward.

Put Quadlets in that account's `~/.config/containers/systemd/` and an application target in `~/.config/systemd/user/`. Each container unit should declare `PartOf=app-name.target`; the target should `Requires=` and order `After=` all its member services. Set additional dependency/readiness rules between the application's containers; target membership alone does not establish database readiness.

Operate as the application account:

```bash
systemctl --user daemon-reload
systemctl --user start app-name.target
systemctl --user stop app-name.target
systemctl --user status app-name.target
podman stats --no-stream
journalctl --user -u app-name-frontend.service
```

Keep independent named database volumes and secrets per application. Stop/start must preserve volumes. Do not use volume removal or pruning as a stop action. Production images should be pinned to approved digests and have health checks, log limits, restart policies and application-specific backup procedures.

Set direct Podman container limits in each Quadlet, for example:

```ini
[Container]
PodmanArgs=--memory=256m --cpus=0.5
```

Direct limits were verified inside a rootless container: `--memory=64m --cpus=0.25` produced `memory.max=67108864` and `cpu.max=25000 100000`. Systemd service limits alone should not be assumed to cap all Podman payload processes with split cgroups. Check actual container cgroup limits and account/slice ancestry before enforcing a whole-application budget. Reserve host headroom and sum per-container budgets when deciding which applications may run simultaneously.

## Verification and remaining scope

- Rootless Podman reported cgroup v2, systemd cgroup management, and netavark networking. A resource-limited container executed successfully.
- A temporary two-container Quadlet target started, stopped both containers, closed the loopback frontend listener, and started again successfully.
- Caddy proxied the test frontend through HTTPS port 8443. An external TLS 1.3 request received the expected response with certificate validation enabled. The private frontend port 18443 and admin port 2019 were externally inaccessible.
- Removed the temporary containers, target, route and firewall opening. No application containers remain running. Downloaded test images remain cached; no destructive cleanup was performed.
- Caddy restart retained HTTPS operation and the certificate. Final listeners are SSH, public TCP 80/443, loopback admin/DNS, and existing local services. Existing Fail2ban, auditd and AppArmor remain active, with no failed system units.
- The signed Caddy Cloudsmith repository returned HTTP 402. Its repository file was moved out of APT sources, and the official GitHub release `.deb` was installed after SHA-256 verification against release metadata. Digest: `a22b914ffd1958da42bc7ab13b7b62c6100634e0798ab594891d2d61d53ba749`. Caddy upgrades need an explicit verified-release upgrade until a working update repository is established; Ubuntu security-only unattended updates do not update this package.
- Setup evidence and configuration backups are root-readable under `/root/vps-foundation-20261009/`.

This completes the Caddy gateway and tested Podman runtime foundation. A graphical monitoring/stack-control dashboard, production application accounts/deployments, automatic whole-stack budget admission, and off-host backup destinations have not been configured. Basic inspection is available through SSH, Podman statistics and systemd. Those remaining infrastructure features require their own concrete setup and verification.

See `VPS_SECURITY.md` for SSH access and recovery. Its earlier statement that only port 22 is open describes the pre-gateway state; the current firewall also permits TCP 80 and 443.
