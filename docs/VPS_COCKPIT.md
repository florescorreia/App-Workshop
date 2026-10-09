# Cockpit access and application control — 2026-10-09

Subsequent deployment: **IdeaFlow application** is available in Application stacks when signed in as the dedicated **ideaflow** Linux account. Its password is in Windows User variable `IDEAFLOW-VPS-COCKPIT-PASSWORD`. The `ubuntu` session does not list that separate account's stack. See [VPS_IDEAFLOW.md](VPS_IDEAFLOW.md) for access and verified operation. Initial installation evidence below predates this deployment.

Installed Cockpit 360, cockpit-podman 124 and cockpit-storaged 360 on the VPS. Cockpit provides machine/resource monitoring, logs, services, storage and Podman container controls. The custom **Application stacks** page starts/stops complete application targets belonging to the signed-in Linux account.

## Connect

Keep this command running in PowerShell:

```powershell
ssh -N -o ExitOnForwardFailure=yes -L 127.0.0.1:9090:127.0.0.1:9090 -F "$env:USERPROFILE\.ssh\vps-8104e6c8.conf" vps-8104e6c8
```

Then open `http://127.0.0.1:9090`. HTTP is local to the workstation; the connection to the VPS is encrypted by SSH. Cockpit listens only on VPS loopback, and port 9090 is not opened in the firewall or Caddy. Root login is disallowed. Close the tunnel to end local access.

To see **IdeaFlow's containers and application stack**, sign in as **`ideaflow`**. If already signed in as `ubuntu`, use Cockpit's account menu to **Log out**, then enter `ideaflow` on the login screen. This is the Linux/Cockpit account, separate from the email/password used inside IdeaFlow. Open **Application stacks** for the full app and **Podman containers** for its three containers. Administrative access does not automatically select another account's rootless container storage.

Retrieve the dedicated Cockpit password privately in PowerShell:

```powershell
[Environment]::GetEnvironmentVariable('IDEAFLOW-VPS-COCKPIT-PASSWORD','User')
```

For host administration, sign in as `ubuntu` with its existing strong account password. Its own container/stack list is empty; that does not mean IdeaFlow is stopped. Persistent Windows **User** environment variables for the host account were written and read back:

- `VPS-OVH-US-8104e6c8-COCKPIT-USERNAME`
- `VPS-OVH-US-8104e6c8-COCKPIT-PASSWORD`
- `VPS-OVH-US-8104e6c8-COCKPIT-URL`

Retrieve the password locally with:

```powershell
[Environment]::GetEnvironmentVariable('VPS-OVH-US-8104e6c8-COCKPIT-PASSWORD','User')
```

The SSH key passphrase remains in `VPS-OVH-US-8104e6c8-SSH-KEY-PASSPHRASE`. The Cockpit password variable duplicates the account password: future account password changes must update both password variables. No password is stored in this repository. Windows environment variables are persistent local storage, not a dedicated secret vault.

## Whole application controls

The **Application stacks** page lists user systemd targets named `app-NAME.target`. Each member container unit must declare `PartOf=app-NAME.target`. The target requires and orders its member units; deployment must also establish readiness/dependencies and direct Podman resource limits. Start/Stop preserves persistent volumes. Per-container controls remain available through **Podman containers**.

IdeaFlow is deployed under `ideaflow` as **app-ideaflow.target**, displayed as **IdeaFlow application (frontend, backend, PostgreSQL)**. Its containers are **ideaflow-frontend**, **ideaflow-backend** and **ideaflow-postgres**. The stack page manages only the signed-in account's stacks. Separate application accounts require their own Cockpit sessions; this page does not enumerate/control other users' containers. Administrative host actions use Cockpit's privilege elevation and the account password.

Source files are in `infra/cockpit/`. Installed UI files are `/usr/local/share/cockpit/app-stacks/`; its unprivileged helper is `/usr/local/libexec/cockpit-app-stacks`. The helper accepts only start/stop of existing user targets matching the application naming convention and uses argument arrays, without shell command construction. Cockpit uses its own authenticated transport to invoke it.

`ubuntu` user lingering and its local Podman Unix socket are enabled so its managed containers and user services can persist after logout. No Podman TCP socket is exposed. Dedicated production application accounts should use their own lingering and sockets as needed.

## Actual verification

- Authenticated Cockpit login over an SSH forwarded channel returned HTTP 200 using the persisted password.
- Authenticated manifests included `app-stacks`, `podman`, metrics, system and storage modules.
- A temporary two-container Quadlet target was listed, started and stopped by the installed helper. Both containers ran, then were removed on stop; an unrelated `ssh.service` request was rejected. The temporary target/files were removed and empty-stack listing passed.
- Verified direct Podman memory/CPU limits during earlier runtime verification; see `VPS_FOUNDATION.md`.
- Cockpit socket restart preserved its loopback-only binding. External TCP 9090 was inaccessible; no public management route was added.
- Socket auto-start, `ubuntu` lingering and the rootless Podman socket were enabled; no systemd units were failed.
- Actual browser rendering/click interaction was not exercised in this session. Login, package discovery and the actual control helper were verified. Cockpit supplies live monitoring; long-term metrics retention and off-host alerting are not configured.

Installation logs are root-readable under `/root/vps-cockpit-20261009/`. Existing Caddy, firewall and SSH access remain in place. See `VPS_FOUNDATION.md` and `VPS_SECURITY.md` for infrastructure and recovery.
