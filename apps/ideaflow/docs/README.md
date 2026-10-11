# IdeaFlow documentation

IdeaFlow is the existing reference app under `apps/ideaflow/`, running on the VPS. Product/domain rules apply only to this app. For another app start with [the workspace guide](../../../docs/START_NEW_APP.md).

| Document | Scope/status |
| --- | --- |
| [PRD.md](PRD.md) | Authoritative IdeaFlow contract; later accepted amendments override original conflicting V1 requirements |
| [UX_WALKTHROUGH.md](UX_WALKTHROUGH.md) | Current normal User walkthrough, with optional Admin account/removal exercises |
| [ARCHITECTURE.md](ARCHITECTURE.md) / [DATA_DICTIONARY.md](DATA_DICTIONARY.md) | Current schema, transactional behavior, roles and calculations |
| [DEMO_IMPORT.md](DEMO_IMPORT.md) | Current explicit additive importer contract; never automatic |
| [VPS_IDEAFLOW.md](VPS_IDEAFLOW.md) / [REDEPLOY.md](REDEPLOY.md) | Current-host operations and reviewed another-machine handover |
| [DEPENDENCIES.md](DEPENDENCIES.md) | Locked dependency inventory and shared tool distinction |
| [VERIFICATION.md](VERIFICATION.md) | Dated implementation/deployment/reboot/import evidence; counts describe each check's snapshot |
| [DEMO_GUIDE.md](DEMO_GUIDE.md), [DEMO_V2_GUIDE.md](DEMO_V2_GUIDE.md), [SHOWCASE_IMPORT.md](SHOWCASE_IMPORT.md) | Historical fictional HarborWorks imports/presentation; recorded references and old role labels are not current live data |
| [VPS_EXTERNAL_ASSESSMENT.md](VPS_EXTERNAL_ASSESSMENT.md), [VPS_PORT_REVIEW.md](VPS_PORT_REVIEW.md), [VPS_WEB_HARDENING.md](VPS_WEB_HARDENING.md) | Dated security findings and remediation; later web hardening supersedes the closed-443 snapshot |
| [START_AND_DEMO_PROMPTS.md](START_AND_DEMO_PROMPTS.md) | Reference-app maintenance/import prompts; not a new-app implementation contract |

Run app-relative commands from `apps/ideaflow/`; commands explicitly using `apps/ideaflow/...` run from the root. Local containers are stopped outside testing. `http://localhost:8080` works only after deliberate local startup. Production URL is https://vps-8104e6c8.vps.ovh.us:8443. Account roles are User and Admin; any active user can perform valid business actions, while Admin manages access/import/removal. Verification records review with an actor/reason, not independent Finance certification.
