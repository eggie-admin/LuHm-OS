# Pirate Daddies Film · Big Brother video job bridge

Candidate source only, **not deployed**. Reuse the current API Spine, current Godot/FFmpeg scripts and an **existing approved** SQL database. There is no evidence of a Render PostgreSQL instance, nor has any Cloud SQL/MySQL production DSN been inspected. Do not create a replacement database or service.

## Actual missing lifecycle

1. Current API Spine plans providers; it does not execute Veo jobs. Register `videoCandidateGeneration` under the existing `googleAi` / `bigBrother` adapter, with readiness still requiring execution receipts.
2. Install worker Python dependencies **only on an approved private worker host**, not on the public harness, then configure host-side ADC/workload identity and the existing SQL DSN, without sharing secrets in chat or source.
3. A DBA reviews and applies `yumeVideoJobSchemaV1.sql` in the approved existing database after confirming backup. Production worker fails closed if the table is absent. SQLite is for disposable local tests only.
4. Cloud provider's **`predictLongRunning`** returns an operation name. Store it durably with exact task identity before doing anything else. The `fetchPredictOperation` request polls exactly that operation; retrieve the resulting *private* `gs://` asset URI, not an unsecured public URL.
5. Yume and Urd review returned footage as **private candidate**; FFmpeg may produce review videos. Rights/identity/artistry and final publication require Professor's review.


### Independent Google Cloud preflight (read-only)

The original worker \`doctor\` reports local environment flags, **not independently verified Google entitlement**. The supplementary source-audited preflight \`host/api/luhmCloudVideoPreflight.py\` defaults to zero network requests.

On an **already-authorized private host**, with approved Google Cloud Application Default Credentials:

\`\`\`bash
python host/api/luhmCloudVideoPreflight.py --online --project "$GOOGLE_CLOUD_PROJECT"
\`\`\`

This performs only Google Cloud Billing \`GET /v1/projects/{projectId}/billingInfo\` and Service Usage \`GET /v1/projects/{projectId}/services/aiplatform.googleapis.com\`. It never enables APIs or modifies billing. It emits no bearer tokens. Even two ENABLED results do **not** prove service-account permission for a Veo job, Veo model entitlement, quota, GCS write permission, SQL availability, current account credit, or authorization to spend. All of those remain independent gates. This probe has no autonomous scheduling or production deployment.

### Read-only preflight

`python host/api/luhmVideoJobWorker.py doctor`

### Local test in disposable SQLite

`LUHM_VERTEX_GCS_OUTPUT=gs://example-private-vault/yume LUHM_EXISTING_SQL_DSN=sqlite:////tmp/yumeVideoTest.sqlite3 python host/api/luhmVideoJobWorker.py enqueue --task-id yume-Lum-test-20261012 --shot lum`

Never treat a local SQLite result as evidence of a durable production queue.

### Cloud gate

Only after verified entitlements: use ADC on a private runtime, set `LUHM_EXISTING_SQL_DSN` to an existing approved PostgreSQL or MySQL connection, `GOOGLE_CLOUD_PROJECT`, an authorized `LUHM_VERTEX_GCS_OUTPUT` prefix, and exact approval receipts for billing/Vertex/IAM/quota. A **single** reviewed Lum task can be submitted by an operator with `--approve-spend --cost-ceiling-usd 0.90`. This is a safety ceiling for a bounded candidate, **not** a confirmed price quote. Never blindly repeat a submit, especially following a timeout. A poll reads the same operation ID and is safe to repeat.

**Do not automatically set or guess `LUHM_CROWN_VIDEO_COST_APPROVED`, `LUHM_GOOGLE_BILLING_CURRENT_CONFIRMED`, `LUHM_VERTEX_API_READY`, `LUHM_VERTEX_IAM_READY`, or `LUHM_VERTEX_QUOTA_READY`.** These require external evidence and owner authority.

Production SQL connection values are secret and must never be committed, printed or exposed through browser-facing MCP. Cloud images and footage live in the private asset vault. The SQL record holds hashes and references, not binary media.

## BBSO limitations and exact blockers

- No Cloud authentication or entitlement test was executed here. Earlier Gmail billing warnings make any claim of usable project entitlements unsafe.
- No existing Cloud SQL/Postgres/MySQL DSN was disclosed or confirmed in this source environment. A Render workspace query returned no hosted Postgres instances, which does not rule out Google Cloud SQL, local MariaDB, or external databases.
- No auto-deploy, no DB schema migration, no Cloud video jobs, no production Reel, no public Meta/Instagram post.
- An eventual dedicated scheduler or existing approved host service can invoke the CLI on a stable cadence **only after** SQL, auth, quota and budget are verified. The process is not a hidden background agent.
