# Applications

Your next product brief belongs in **`apps/<name>/docs/PRD.md`**. Follow [Start a new app](../docs/START_NEW_APP.md). The generator accepts an app folder containing only that brief and preserves its contents; alternatively generate first and fill in its PRD.

Every app owns its source, tests, docs, configuration, images and PostgreSQL volume. Its PRD defines the product; the root/app AGENTS.md define development boundaries. Shared scripts run from the repository root. Do not initialize nested Git repositories or copy another app's data.

[IdeaFlow](ideaflow/README.md) is the reference production app, not a template to duplicate wholesale. Its local containers are stopped outside tests. Future products do not inherit its workflow, classifications or financial rules.
