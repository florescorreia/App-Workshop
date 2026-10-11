# VPS security handover — 2026-10-09

Subsequent application deployment: IdeaFlow uses Caddy HTTPS on TCP 8443, a dedicated rootless account and an independent volume. SSH and management endpoint restrictions remain in place. See [VPS_IDEAFLOW.md](../apps/ideaflow/docs/VPS_IDEAFLOW.md); earlier port checks below describe the pre-gateway state.

Host: `vps-8104e6c8.vps.ovh.us` (`40.160.88.11`), account `ubuntu`.
Verified OS: Ubuntu 26.04 LTS, KVM virtualization. This work changes the VPS host only; it does not deploy or change IdeaFlow or its containers.

## Current exposure and document scope

Last hosting verification: 2026-10-11. Public application/redirect TCP ports are 80/443/8443 plus SSH 22. Cockpit 9090, Caddy admin 2019 and frontend 18081 remain private. IdeaFlow has a dedicated application account, volume and failed-login Fail2ban jail; host protections remain in place. Additional apps require their own reviewed port/routing/authentication configuration. The original 2026-10-09 hardening results below correctly describe the earlier SSH-only phase; they are historical evidence, not the current complete port inventory. See [foundation](VPS_FOUNDATION.md) and [workspace operation](APP_WORKSHOP.md).

## Access

SSH now requires a key. Password and keyboard-interactive SSH authentication and root SSH login are disabled. The account password remains available for `sudo` and console recovery.

On this Windows workstation, connect with PowerShell:

```powershell
ssh -F "$env:USERPROFILE\.ssh\vps-8104e6c8.conf" vps-8104e6c8
```

The encrypted Ed25519 private key is at `%USERPROFILE%\.ssh\vps-8104e6c8_ed25519`. Its public key is in the adjacent `.pub` file. The dedicated configuration pins the server key, uses only this identity, and leaves other SSH configuration untouched.

The following **persistent Windows user** environment variables contain the secrets; no credentials are included in this document or repository:

- `VPS-OVH-US-8104e6c8`: the strong account password, required by `sudo`.
- `VPS-OVH-US-8104e6c8-SSH-KEY-PASSPHRASE`: the strong private-key passphrase, requested by SSH.

To retrieve either value locally, use `[Environment]::GetEnvironmentVariable('VARIABLE-NAME', 'User')` in PowerShell. Existing applications can retain stale process environment values; querying the User scope reads the persisted value. Both passwords are randomly generated, 40 characters long. Windows environment variables are not a secret vault; protect the workstation and store a recovery copy in a password manager. The private key ACL permits only this Windows account and SYSTEM.

Server Ed25519 fingerprint: `SHA256:tL6twfOpRxc1UL6GUISlGTvZE2DWnDSoZNuAnkPsShY`.

Client Ed25519 fingerprint: `SHA256:9rIKKKAnFVgQfO1Y2JQolb9dli+zNlqs3bN7nE2mC8c`.

## Installed and configured protections

- Applied 194 existing-package updates, then four kernel metapackage updates and the new kernel dependencies. Rebooted successfully into `7.0.0-38-generic`. OpenSSH is now `10.2p1 Ubuntu-2ubuntu3.7`.
- UFW enabled at boot, denying unsolicited incoming and routed traffic. Only TCP 22 is allowed, with rate limiting, for IPv4 and IPv6. Outgoing traffic is allowed. No web or database services were present.
- SSH accepts public keys for `ubuntu` only. Root login, SSH passwords, agent forwarding, X11 forwarding, remote TCP forwarding and tunnels are disabled. Local TCP forwarding remains available. Authentication attempts, sessions and login grace time are limited. OpenSSH's current algorithm defaults are retained.
- Fail2ban 1.1.0 monitors SSH through the systemd journal, including OpenSSH 10's `sshd-session` process. Five failures in ten minutes trigger a one-hour nftables ban, escalating for repeat offenders to a maximum of one week. Only loopback is exempt.
- `sudo` requires the account password. Cloud-init's passwordless sudo rule was changed and a later password-required rule was added. Sudoers syntax was validated.
- AppArmor enabled with distribution profiles; 104 profiles enforced at verification. Existing complain/unconfined profiles were retained rather than blindly enforcing them.
- Auditd enabled, with 16 loaded rules monitoring identities, SSH keys/configuration, firewall and intrusion-protection configuration, sudo policy/use, audit configuration, service/cron configuration, and kernel module changes. Audit logs recorded actual sudo and configuration activity, with zero lost events at verification.
- Network/kernel controls reject redirects and source routing, enable SYN cookies, use loose reverse-path filtering appropriate for the cloud network, restrict kernel-address/log/BPF access, and protect links and shared-directory files. Unused DCCP, SCTP, RDS and TIPC modules are blocked from loading.
- Password quality checks require at least 20 characters and multiple character classes for future local password changes, including changes made by root.
- Persistent system journals are capped at 512 MB, retain up to 30 days, and preserve 1 GB free disk space. Chrony synchronization was verified.
- Daily security-only unattended updates are enabled and validated by a dry run. Automatic reboots and automatic dependency/kernel removal are disabled.
- Weekly Lynis audits and `debsums` package integrity checks are enabled through systemd timers. Logs/results stay on the VPS.

## Actual verification

- Tested a fresh encrypted-key SSH connection before disabling passwords, and again after SSH/firewall changes and after reboot.
- Confirmed password SSH was rejected with `publickey` as the offered method.
- Confirmed `sudo -n true` fails after clearing cached authentication, while password-authenticated sudo succeeds.
- Validated SSH, Fail2ban and sudoers configuration syntax. Verified security services and timers are active/enabled after reboot, with no failed systemd units and no pending reboot.
- Tested a Fail2ban ban against reserved documentation address `192.0.2.123`, confirmed its nftables rule, and removed the test ban. The filter matched 3,618 lines when replaying 6,405 historical SSH journal lines; actual attacking addresses were banned. Counts and ban membership naturally change over time.
- Externally checked TCP ports 22, 80, 443, 2375, 2376, 3306, 5432, 6379 and 8080: only 22 was reachable. The others timed out as filtered/unreachable. This was a targeted check, not a complete port scan.
- The post-reboot `debsums --silent` check completed successfully without reporting package-file mismatches. This verifies packaged files against local distribution checksum records; it is not proof that a system has never been compromised.
- Post-reboot Lynis completed with hardening index 73 and no warnings. Suggestions remain in its report. This index is an audit heuristic, not a security guarantee.
- Unattended-update dry run exited successfully, allowed only `Ubuntu/resolute-security`, and found no pending unattended upgrades.
- Two non-security `software-properties` updates remain deferred by Ubuntu's phased rollout; phasing was respected.

## Operations and recovery

Useful commands after connecting:

```bash
sudo ufw status verbose
sudo fail2ban-client status sshd
sudo auditctl -s
sudo journalctl -u ssh -n 50
sudo systemctl status vps-security-audit.timer vps-package-integrity.timer
sudo cat /var/log/vps-lynis-report.dat
sudo journalctl -u vps-package-integrity.service
```

Weekly checks run Sundays at 05:00 UTC (Lynis) and 06:00 UTC (integrity), each with up to 30 minutes of randomized delay. They log locally; no email, remote monitoring or third-party telemetry was configured.

Configuration backups and initial verification evidence are root-readable under `/root/vps-hardening-20261009/`. The pre-change configuration archive passed `gzip -t` and archive listing validation. It contains sensitive system configuration and must remain private. This is a configuration backup, not an OVH snapshot or off-host disaster-recovery backup.

If SSH access is lost, use the OVH web console or rescue facility. Log in as `ubuntu` with the account password, then use password-authenticated sudo. For a confirmed Fail2ban false positive, remove only the affected address with `sudo fail2ban-client set sshd unbanip ADDRESS`. A console-only SSH recovery can move `/etc/ssh/sshd_config.d/00-vps-hardening.conf` aside, validate with `sudo /usr/sbin/sshd -t`, and reload SSH. Restoring password SSH weakens the protection, so re-establish a working key and re-enable the hardened configuration promptly. The temporary access rollback timer used during setup was cancelled after successful access verification.

Maintain a separate recovery copy of the encrypted key and credentials. Review audit/integrity failures and pending-reboot notifications. Newly deployed services need explicit firewall rules and service-specific authentication/TLS; Docker-published ports need separate review because they can bypass UFW's incoming rules. OVH account security, upstream DDoS controls, provider firewall rules, off-host alerts/backups and application security were outside this host configuration and were not changed or verified.
