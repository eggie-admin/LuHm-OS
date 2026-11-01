# LuHm-OS: Project Premonition | GitHub-first SQL source authority

**Status:** proposed source-only. GitHub holds schema definitions, not runtime database contents. Python validates and optionally uses private SQL on separately authorized hosts. Nothing here edits a production database or grants autonomous workers execution.

## What is actually controlled

The exact, locked SQL sources are named in `doctrine/githubSqlSourceRegistryV1.json`:

| Source | Dialect | Purpose | Where SQL can execute |
|---|---|---|---|
| `host/api/typedLanesV1.sql` | SQLite STRICT | Scope-bound typed stream events, evidence, AI manifest and binary *pointers* | Ephemeral in-memory CI, or authorized private host when independently configured |
| `host/api/premonitionAssetLedgerV1.sql` | SQLite STRICT | Original art and GLB/texture/video metadata, provenance and non-public transformation state | Ephemeral in-memory CI; private host application not currently proven |
| `host/api/luhmMariaDbReceiptV1.sql` | MariaDB candidate | Hash-based receipt metadata in an optional TLS-authenticated private server | **Not applied or connected** |

The SQL source registry uses GitHub's `gitBlobSha1` for each exact SQL file. The source auditor recomputes that native Git blob identifier, additionally reports SHA-256 for the file bytes, verifies the allowed tables and rejects unapproved source drift. Git hashes represent source integrity, **not** a publisher signature, database backup or encrypted content.

Python source consumers are explicitly recorded. These files are not schema owners and are forbidden from silently redefining or upgrading authoritative tables:
`tools/typedSqlStub.py`, `host/api/luhmCryptoSqlite.py`, `host/api/luhmCanonOrchestration.py`, `tools/premonitionPlatformArtAudit.py`, and the optional `host/api/luhmMariaDbReceipt.py`.

## Source and runtime boundaries

**GitHub:** branches, reviewed schema changes, CI, exact-source hashes and receipts. Keep private credentials out of code and database rows. The canonical release branch is `main`. Proposed schema definitions stay in the existing draft until reviewed.

**Private Python:** bound values using parameterized statements, compare exact task/source/scope, never use client-provided table names, and avoid logging raw user art or secrets. No direct browser or Android SQL connection.

**SQLite:** simplest default for a tiny solo-studio app and scoped local control receipts. Existing offline CI runs the two canonical schemas in disposable **:memory:** connections and checks STRICT tables, foreign keys and integrity. In-memory proof is not a production migration.

**MariaDB:** optional private shared receipt indexing only if real host identity, TLS, cost boundary, backup and precise approval are available. The read-only schema auditor does not install drivers, open port 3306, connect to servers or run MariaDB DDL.

**Media/art:** editable SVG/Blender masters, GLBs, images and videos stay in their approved durable storage. SQL stores bounded IDs, content digests, provenance and authorized private pointers, never image or movie blobs.

## Versioned migration checklist

1. **R1 Source:** identify exact commit, repository, schema version, expected Git blob, review and full rights.
2. **R2 Validate:** confirm typed fields, relevant Python consumers and schema compatibility. Reject source drift and destructive SQL.
3. **R3 Ephemeral test:** create a fresh SQLite in-memory fixture and test identity/constraints; for MariaDB use static checks until a separately approved private test database exists.
4. **R4 Explicit authority:** owner confirms a specific database identity, encrypted private transport where applicable, backup+rollback, tested migration plan, exact head, and release target. Only then can another authorized component apply a real migration.

A revision to any locked v1 schema requires a **new reviewed version and its own hash/migration assessment**. Do not edit a pinned schema in place and silently relock it. The CLI `python tools/githubSqlSourceAudit.py` and read-only MCP source definitions `luhm_sql_source_status` / `luhm_sql_migration_plan` expose these checks without creating workers. There is no hidden scheduling or live DB activity.

No schema or CI pass is evidence of a running Samsung app, verified Google Drive file bytes, Cloudflare proxy session, remote VM, real MariaDB, Apple runtime, or connected private ChatGPT Site plugin. No merge, paid service, new VM, public SQL port or autonomous quarantine change is implied.
