# IdeaFlow — Build and showcase prompts

Put the accompanying `PRD.md` in `docs/PRD.md` inside a new project folder. That is the only file needed to start. Open that folder in VS Code, start Rancher Desktop, and paste prompt 1 into Codex. Once the app is deployed, use prompt 2. Prompt 3 adds a second batch later without replacing the first.

The PRD also contains these prompts, so you can keep the initial project limited to `docs/PRD.md`.

## 1. Build and deploy locally

```text
The project currently contains only docs/PRD.md. Read it completely and implement IdeaFlow end to end as specified. Treat it as the implementation contract.

Create the React/TypeScript frontend, FastAPI backend, PostgreSQL schema/migrations, transactional event log, workflow, monthly value tracking, process analytics, tests, demo importer, scripts, and documentation. Keep the deployment at three long-running services. Use containers for build/development tools; do not require host Python or Node.

Inspect my available Rancher Desktop engine/context, use its Docker/Moby runtime through Docker Compose, and deploy locally. Discover the actual context name instead of assuming it. Preserve other projects, existing configuration, and volumes. If a runtime prerequisite is blocked, finish everything that can be built and give me the exact remaining prerequisite; never claim deployment without verification.

Start with a usable empty application. Do not load fictional showcase data automatically. Implement the explicit additive/idempotent demo import command and JSON format from the PRD so I can populate it later.

Work through the full implementation, meaningful tests, browser/layout review, restart/rebuild persistence, and isolated backup/restore verification. Fix failures. Do not stop at a plan or scaffold. Use routine implementation judgment rather than asking me to choose libraries. Do not expand the stack or run destructive resets.

At completion, report the exact local URL, login instructions, demo-load command, checks actually passed, and limitations. Record the evidence in docs/VERIFICATION.md and provide the eight-minute non-technical showcase guide in docs/DEMO_GUIDE.md.
```

## 2. Populate the first showcase

```text
Read docs/PRD.md, README.md, and the demo-import documentation in this project. Populate the running local IdeaFlow app with its HarborWorks Manufacturing showcase dataset, using the implemented backend importer, not ad hoc direct SQL.

Use batch key harborworks-demo-v1, seed 42, and today's date in the app timezone as the anchor. First run a dry-run/validation preview; if valid, commit this explicitly authorized additive import. Include 60 fictional ideas across Tampa, Atlanta, and Dallas, covering the last 18 months, with the stage/disposition mix, five hero ideas, delayed Analysis work, holds, rework, completed initiatives, approved monthly financial schedules, implementation tasks, actual results, and finance verification specified in the PRD.

Preserve every existing user-created idea and all history. Rerunning the same batch must be a no-op. Do not reset/recreate the database, delete volumes, overwrite live records, generate future actuals, or create unsupported workflow histories. Clearly label the dataset as fictional and retain import provenance.

Verify current states reconcile with event replay, the counts and dashboard totals are coherent, missing actuals are shown as unknown, and process paths reveal the intended bottleneck. Check a second invocation produces no duplicates. Open or verify the deployed screens if tooling allows.

Update docs/DEMO_GUIDE.md with an eight-minute presentation using actual imported idea references: overview, create a new idea live, assign/work it, inspect a bottleneck and rework path, compare expected and actual gains/ROI, and finance-verify one unverified elapsed month. Point out which steps require Manager/Finance roles. Finish with the local URL, imported counts, and the five best ideas to open. Never expose passwords in committed docs.
```

## 3. Add new ideas for a second session

```text
Add a new, separate fictional showcase batch to the existing local IdeaFlow application. Follow docs/PRD.md and the JSON import contract. Use batch key harborworks-demo-v2 and seed 84; preserve harborworks-demo-v1 and all user-created records.

Create 12 credible new ideas: three Procurement, three Freight, two Energy, two Scrap/Quality, and two Productivity. Distribute them across Tampa, Atlanta, and Dallas. Keep six New ideas ready to work live, three Screening, two Analysis, and one Implementation idea about reducing emergency freight. For that Implementation idea, create a valid historical lifecycle, approved monthly ramp-up/spend plan, tasks, and two elapsed months of actual results below plan, leaving the latest period unverified. Other ideas have estimates but are not falsely shown as approved or achieved savings.

Write the proposed records to demo/harborworks-demo-v2.json in the existing supported format; validate with a dry run, then import this explicitly authorized batch through the backend importer. Use fictional owners, realistic descriptions and costs, timestamps no later than now, and unique external keys. Repeating this prompt/import must not duplicate records. Do not delete, reset, or overwrite anything.

Confirm that the idea register, Pipeline, Process, and Value views reflect the new records. Give me their actual idea references and a short live-demo sequence for taking one of the six New ideas through Screening and Analysis. Keep the existing application architecture unchanged.
```
