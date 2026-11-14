# LuHm-OS machine SQL source-of-truth candidate · 512 escalation

**State:** source-only research, SQLite synthetic executable prototype, and
MariaDB/phpMyAdmin REVIEW-ONLY DDL. **Not** a live database, device crawl,
firmware reader, private ChatGPT plugin migration, or public SQL service.

## Professor correction: no ten-pass machine migration

Machine inspection intensity is **512**. Preserve Canon's existing
`doctrine/fnCastV1.yaml` 4 CAST stages × 4 interaction beats × 4 audit tiers
= 64 source-only coordinates. Index these over eight machine registry domains:

| Domain | Records represented | Source-only audit coordinates |
| --- | --- | ---: |
| identity | pseudonymous machine identity, provenance | 0x00..0x3F |
| source | exact Git SHA-1-format 40-character sourceRef, SHA-256 schema fingerprint | 0x00..0x3F |
| device | safe aliases, profile and unknown verified-boot state | 0x00..0x3F |
| firmware | component/version, OPTIONAL verified image SHA-256, unknown state | 0x00..0x3F |
| registry | case-sensitive namespaces, names, source bindings | 0x00..0x3F |
| machineApi | read-only MCP/OS API route metadata and access policy | 0x00..0x3F |
| artifact | SHA-256, size, durable storage pointer, provenance | 0x00..0x3F |
| governance | signed-off receipts are NOT inferred from source checks | 0x00..0x3F |

**Total 8 × 4 × 4 × 4 = 512**. These coordinates are audit
*identifiers*, not physical registers, CPU/firmware addresses, automatic CAST
commands, 512 independent AI agents, or a new fourth escalation authority.
The existing `doctrine/escalationKernelV1.json` tiers 0–3 remain intact.
SHA-256 is **64 lowercase hexadecimal characters** representing 32 digest
bytes. That must never be confused with Base64 transport encoding or the
64-coordinate CAST matrix. Git SHA refers to the existing exact 40-hex
commit ID, not to a device serial.

## What phpMyAdmin actually offers

phpMyAdmin is a **PHP administration client**, not a relational database
engine or source-of-truth service. It manages an existing MySQL/MariaDB server,
supports SQL execution, browse/search, CSV/SQL import and export, and a
graphical relational Designer. Its separate `pmadb` configuration storage
is for optional UI conveniences like bookmarks, history and layout; it is
NOT the LuHm machine evidence database.

Use real **InnoDB foreign keys**, not phpMyAdmin's special UI-only relation
metadata, so server-side constraints work even when the Python MCP service
or another client writes data. Review schema with
`host/api/machineRegistryMariaDbReviewV1.sql` in a **private disposable**
MariaDB server only after manual approval. phpMyAdmin requires its own PHP
runtime and authenticated web surface. It should remain uninstalled by
default. MariaDB's JSON data type is LONGTEXT with JSON validation; it is not
binary-identical to MySQL's JSON. Existing SQLite JSON1/camelHump source
remains the local default, not a transparent MariaDB migration.

Official upstream references, verified for this design:
- https://docs.phpmyadmin.net/en/latest/intro.html
- https://docs.phpmyadmin.net/en/latest/relations.html
- https://docs.phpmyadmin.net/en/latest/setup.html
- https://docs.phpmyadmin.net/en/latest/import_export.html
- https://mariadb.com/docs/server/reference/data-types/string-data-types/json
- https://mariadb.com/docs/server/reference/data-types/string-data-types/binary
- https://mariadb.com/docs/server/ha-and-performance/optimization-and-tuning/optimization-and-indexes/foreign-keys

## Sanest design and source-ownership boundary

One **relational machine-metadata registry**, not one monolithic database
holding keys, files, raw firmware and ChatGPT conversations.

- GitHub `main` and exact commit hashes remain authoritative for approved
  source code, doctrine, schema migration scripts and CI receipts.
- A future authenticated MariaDB registry can be promoted as the **one
  operational source of truth for machine *metadata*** and reconciled facts
  only after real source binding and backup/restore verification.
- SQLite STRICT supports portable offline synthetic tests, portable review,
  bounded local device metadata and 512-case inspection without installing
  database daemons.
- Private Google Drive stays the durable binary archive. SQL holds pointers,
  sizes and hashes, not APKs, models, private photos or bulk firmware bytes.
- The ChatGPT front end sees a least-privilege, read-only **Python MCP API**,
  never an exposed MySQL port or a browser-held SQL credential.
- Live firmware modification, bootloader unlock, public database administration,
  device collection, API activation and SQL schema promotion are OFF.
- Pseudonymous random keys stand in for device/host identities in SQL;
  raw IMEI, MAC, disk serial, hardware ID, credentials, exact physical
  address, and private Drive IDs stay out of publicly shared receipts.
  A pseudonym still requires privacy controls when linked to a real device.

## Prototype proof

```bash
python3 tools/machineSqlHex512Audit.py
```

The standard-library script creates **one disposable SQLite in-memory
database**, enforces real foreign keys and strict CHECK constraints,
inserts only synthetic device/firmware/artifact identity fixtures, iterates
every unique surface + 64 Canon coordinate, and runs negative corruption
controls. It prints no sensitive machine identifier.

It does **not** run MariaDB, parse SQL with phpMyAdmin, verify physical
firmware, authenticate a device or deploy an OpenAI plugin. Before any live
migration: record precise MariaDB/server version, actual DB availability
and owner scope; private backups with successful restore rehearsal;
full DDL and collation diff; role/auth grant review; local UNIX socket;
replay fixture and FK tests in MariaDB; source-bound dual-read comparison;
explicit owner approval and reversible cutover.

**Crown:** STOP. **Agent quarantine:** remains. No external publication.
