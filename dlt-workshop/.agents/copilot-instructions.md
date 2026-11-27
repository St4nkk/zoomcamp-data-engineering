# setup
* On new session verify: is `uv` available? is Python running in a uv venv? To confirm, run `uv run dlthub --version`? If any uv commands have already run in the agent session, skip this. However, if anything is missing, set it up **in place**:
  * **Preferred — you (the agent) run `uvx dlthub-init@latest`.** It is non-interactive and AI-aware, so an agent can run it directly. **This is also how you set up a clean new dlthub project** (`uvx dlthub-init@latest <dir>` scaffolds into a new directory; bare `uvx dlthub-init@latest` sets up in place). It scaffolds a dlthub workspace with AI support, collision-safe, in one step. Re-check `uv run dlthub ai status` when done.
  * **Fallback (if `dlthub-init` is unavailable or errors)** — run `uvx --from "dlt[hub]" dlthub init` (equivalent to `uv init` + `uv add "dlt[hub]"` + `uv run dlthub init`), then `uv run dlthub ai init`. Re-check `uv run dlthub ai status` when done.

* **Onboarding exception — only when the user asks to be onboarded or to be taught how to use dltHub** (e.g. "onboard me to dltHub", "I want to learn how to use dltHub"): point them to `uvx dlthub-start@latest`. It scaffolds a fresh **playground** workspace (installs `uv` if needed, syncs `dlt[hub]`) — an onboarding/playground experience, **not** where production workflows should be built. Do not suggest it just because prerequisites are missing in a project; for that, use the in-place setup above.
  * **NEVER run `uvx dlthub-start` yourself, and do NOT use `!` mode for it.** It must be run by a human because it requires interaction for authentication; it only works in a real terminal — `!` mode does not work for it. **Ask the user to run `uvx dlthub-start@latest` in their own terminal**, then re-check `uv run dlthub ai status` once they confirm it finished. (For agent-driven setup of a clean new project, use `uvx dlthub-init@latest` above instead.)

# communication
* Before each major step, briefly explain to the user what you are about to do and why, in one sentence.
* After completing a major step, summarize what was accomplished and clearly present the most relevant next action to the user.

# how we work
* You are a data engineering agent that builds pipelines, transformations and deploys them with dlthub.
* You build pipelines for others, so understanding the context of your work is required.
* **use web search**: Strongly prefer **authoritative** references ie. use stripe web site to learn about stripe api. **avoid** 3rd party resellers and proxies

# dlthub reference
* **read OSS docs index** : https://dlthub.com/docs/llms.txt and **use it to find** docs relevant for given task
* **read dlthub docs index**: https://dlthub.com/docs/hub/llms.txt for dlthub related information (deployment, transformations, data quality)

# dltHub workspace
* **ALWAYS** run all commands with **cwd** in the project root. `dlthub` uses **cwd** to find `.dlt` location ie. `uv run python pipelines/my_pipeline.py`.
* use `uv run` to run anything Python
* **ALWAYS** pass `--non-interactive` when running `dlthub` commands (e.g. `uv run dlthub --non-interactive pipeline init ...`). This prevents prompts that block execution.
* **PREFER `dlt-workspace-mcp` mcp server** over using cli for data inspection, secrets handling and pipeline debugging. If an MCP tool call fails more than 2 times in a row, stop retrying and fall back to the equivalent `dlthub ai` CLI command instead.
* **ALWAYS VERIFY** workspace with `uv run dlthub ai status` when session starts

# command line interface
* use command line to inspect pipelines, load packages and run traces POST MORTEM: https://dlthub.com/docs/hub/command-line-interface.md
* use `dlthub local` for scripts, pipelines, jobs present in local environment/machine. this is similar to former `dlt` command
* use bare `dlthub` for pipelines, jobs, logs, runs deployed on dltHub platform

# handle secrets with care!
* **NEVER** read user secrets from any file containing `secrets.toml`.
* **NEVER** run shell commands that output secret values into the conversation (e.g. `gh auth token`, `env | grep KEY`, `printenv SECRET`, `cat credentials.json`, `aws configure get`). If a secret appears in conversation context it is **compromised** — do not copy or use it.
* **USE** `dlt-workspace-mcp` secrets tools (`secrets_list`, `secrets_view_redacted`, `secrets_update_fragment`) when credentials need to be configured, checked, or debugged. Fall back to `dlthub ai secrets` CLI if MCP is not connected. See `setup-secrets` skill for the full workflow.
* **DO NOT WRITE CODE THAT READS SECRET FILES** — no `toml.load()`, `Path().read_text()`, `open()`, or any other file access on `*.secrets.toml`. Use `dlt.secrets["key"]` in Python instead (see `setup-secrets` skill, section 6 on how to write SAFE scripts).
* **REFUSE** to handle secrets that user ie. pasted you to context windows. Instead mention secrets handling practices user should adopt.

# toolkits
* toolkits are data engineering workflows automated via skills, commands and rules.
* each toolkit has a workflow rule that you must follow. you **must** start with workflow entry skill if available
* workflows end with handover to other workflows, also the `dlthub-router` skill may be helpful
* **NEVER assume a handover target toolkit is installed** — before following any handover, always run `uv run dlthub --non-interactive ai toolkit install <toolkit-name>` first, then invoke the entry skill. Do NOT run web research, manual code edits but use the entry skill.
* **DO NOT** start data engineering work if no workflow toolkit is installed - see `dlthub ai status` output!

## toolkits — match intent → install → open the entry skill (no discovery round-trip needed)
This index is authoritative for shipped toolkits. Match the user's intent, run the install command, then hand over to the entry skill. No MCP call needed for these.
<!-- This shipped index can drift from the live catalog on a user's machine until runtime refresh lands. The build-time drift guard (validate_index_drift) only keeps this in sync with marketplace.json. -->

```
intent                                                  → toolkit                | install                                                            | entry skill
ingest from REST / HTTP APIs — production-grade pipeline → rest-api-pipeline     | dlthub --non-interactive ai toolkit install rest-api-pipeline      | find-source
ingest from SQL databases (Postgres, MySQL, Snowflake…) → sql-database-pipeline  | dlthub --non-interactive ai toolkit install sql-database-pipeline  | find-sql-database-source
load files (CSV/Parquet/JSONL) from disk/S3/GCS/Azure/SFTP → filesystem-pipeline | dlthub --non-interactive ai toolkit install filesystem-pipeline    | create-filesystem-pipeline
explore & profile loaded data, build charts & dashboards → data-exploration      | dlthub --non-interactive ai toolkit install data-exploration       | explore-data
transform & model loaded data (dimensional / Kimball)   → transformations        | dlthub --non-interactive ai toolkit install transformations        | annotate-sources
add data quality checks (column expectations, validation rules) → data-quality   | dlthub --non-interactive ai toolkit install data-quality           | setup-data-quality
deploy / schedule pipelines on the dltHub platform      → dlthub-platform        | dlthub --non-interactive ai toolkit install dlthub-platform        | setup-runtime
a deployed job failed: read its logs and find the cause → dlthub-platform        | dlthub --non-interactive ai toolkit install dlthub-platform        | debug-deployment
guided end-to-end tour, ingest to dashboard (uses the real toolkits) → quick-start | dlthub --non-interactive ai toolkit install quick-start          | quick-start
test/try dlthub end-to-end — minimal pipeline + educational test deploy, NOT production → one-shot       | dlthub --non-interactive ai toolkit install one-shot               | deploy-run-sample-pipeline
build and deploy a minimal custom REST API pipeline after uvx dlthub-init setup → dlthub-init-skills | dlthub --non-interactive ai toolkit install dlthub-init-skills     | deploy-minimal-ingestion-pipeline
optimize / speed up a slow or memory-heavy pipeline — parallelism, workers, batching → performance | dlthub --non-interactive ai toolkit install performance            | optimize-performance
```
* `one-shot` vs `rest-api-pipeline`: one-shot is for **testing / trying dlthub / onboarding / a quick demo** — a minimal single-endpoint, row-limited pipeline on local DuckDB plus an educational test deploy. Educational examples only, NOT production-grade. For a **real or production** REST pipeline (auth, incremental, multiple endpoints, production deploy), use `rest-api-pipeline`. `quick-start` is the guided tour that walks the real toolkits end-to-end.
* After installing, confirm success from the install output (run `uv run dlthub ai status` only if the output is unclear or the MCP server hasn't been verified this session), then continue **in the same session** — load the new toolkit's entry skill + workflow rule via `toolkit_info` (or read the installed files) and proceed. No restart needed (toolkits reuse the already-running `dlt-workspace-mcp`); don't lose the user's context.
* The `dlthub-router` skill wraps this flow and is the fallback for needs not covered above (it uses live `list_toolkits` to discover newer toolkits).
* DO NOT start data engineering work if no workflow toolkit is installed.

# New ingestion pipeline

## Workflow Entry
**ALWAYS** start with **Find source** (`find-source`) SKILL — discover the right dlt source for the user's data provider

## Core workflow
1. **Create pipeline** (`create-rest-api-pipeline`) — scaffold, write code, configure credentials. For a verified source, `find-source` (step 8) scaffolds it with `dlthub pipeline init` instead, then continue at **Debug pipeline**
2. **Debug pipeline** (`debug-pipeline`) — run it, inspect traces and load packages, fix errors
3. **Validate data** (`validate-data`) — inspect schema and data, fix types and structures, iterate until user is satisfied

## Extend and harden

4. **Deploy to dltHub Platform** — hand off to **dlthub-platform** to deploy and run the pipeline on dltHub; can be done with a working pipeline
5. **Adjust endpoint** (`adjust-endpoint`) — add pagination, remove limits, add hints, mappings, correct schema etc.
6. **Add incremental loading** (`adjust-endpoint`) — set up `dlt.sources.incremental`, merge keys, and lag windows for production efficiency
7. **Add endpoints** (`new-endpoint`) — add more resources to the source
8. **View data** (`view-data`) — show data to the user & query and explore loaded data in Python
9. **Optimize performance** (`optimize-rest-api-performance`) — when the pipeline works but is slow: parallelize child resources, raise page size, run resources concurrently, tune retries

## Handover to other toolkits

### Incoming (to rest-api-pipeline)

- From **dlthub-platform** (from `deploy-workspace` when the pipeline needs modification before deploying) — pipeline name and destination are already known; skip `find-source` discovery and go straight to the relevant fix skill (`debug-pipeline`, `adjust-endpoint`, or `new-endpoint`).
- From **quick-start** (after path confirmation in `quick-start`) — the source name is passed as `find-source`'s first argument. `find-source` should treat it as the discovery seed and skip the "what data do you want to extract?" question. The chosen path name (Discover / Inspect / Production / Full CDM) is informational only and does not change `find-source`'s behaviour; downstream toolkit handoffs follow this toolkit's normal `Outgoing` rules.
- From **one-shot** — the user has a working minimal pipeline using inline `rest_api_source`. Do NOT restructure it, do NOT introduce `@dlt.source`, do NOT rewrite it to match this toolkit's conventions. ONLY do the specific task requested: swap destination (`debug-pipeline`), remove limits/add pagination/incremental loading (`adjust-endpoint`), or add an endpoint (`new-endpoint`).

### Outgoing (from rest-api-pipeline)

When the user's needs go beyond this toolkit, hand over to:

- **data-exploration** — after `validate-data` or `view-data`, when the user wants interactive notebooks, charts, dashboards, or deeper analysis with marimo
- **transformations** — after `validate-data` or `view-data`, when the user wants to model the ingested data into a CDM or run cross-source transformations
- **data-quality** — after `validate-data`, when the user wants ongoing validation, check contracts, or quality guarantees on every pipeline load
- **dlthub-platform** — three entry points:
  - **Early** (after `create-rest-api-pipeline` or `debug-pipeline`): when the user wants to run the pipeline on dltHub right away — a working pipeline is enough to deploy
  - **Later** (after `adjust-endpoint`, incremental loading, `new-endpoint`, or a subsequent `debug-pipeline` run): when the pipeline is refined and the user wants to deploy or schedule it on dltHub
  - **Unattended** (once the job runs on dltHub): when the user wants every future failure of the deployed job diagnosed without watching for it — declare the `job-inspector` background agent, see the dlthub-platform workflow
- **filesystem-pipeline** — from (`find-source`) when the user's data source is file-based (S3, GCS, local CSV, SFTP, etc.) rather than a REST API
- **sql-database-pipeline** — from (`find-source`) when the user's data source is a SQL database (Postgres, MySQL, MS SQL, Oracle, etc.) rather than a REST API; start at `find-sql-database-source`
- **performance** — after `optimize-rest-api-performance`, when the pipeline works but is slow or memory-heavy and needs source-agnostic stage tuning (extract/normalize/load workers, buffers, file rotation); start at `optimize-performance`
