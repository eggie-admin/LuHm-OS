# LuHm-OS | 4x4 SQL-to-phpBB pilot task list

Status: PROPOSED_ONLY. No hosting, secrets, production signing or deployment approved.

## 4x4 machine-to-app tasks
1. Capture OS/CPU/ABI/endianness and pinned PHP version; record hex bytes only for safe synthetic fixtures.
2. Inventory filesystem ownership, symlink targets, umask and writable paths. Run PHP as unprivileged service account; never as root.
3. Test SQLite STRICT schema with `python tools/typedSqlStub.py` and existing `tests/testTypedSqlStub.py`, `tests/testSqlHardeningTenPass.py`; assert foreign keys, CHECK constraints, JSON validity, UTC evidence, and rollback.
4. Keep typed LuHm-OS SQLite ledger separate from phpBB database. Do not share SQL credentials, tables, admin login, or sessions.
5. For phpBB pilot use upstream-supported PHP and MariaDB/PostgreSQL versions per current phpBB installation requirements; verify exact upstream package SHA256 and license before staging. No blind vendor import.
6. Run isolated local-only phpBB installation on disposable environment, with pinned container/image digest or vetted distro packages, no public port and no production account data.
7. Configure HTTPS before any public access; unique admin identity, secure cookies, CSRF controls, least privilege DB account, attachment upload limits, email disabled until explicitly configured, rate limits and backups.
8. Create synthetic users/posts, test moderation roles, uploads, Unicode, migrations, restore, and forum upgrade. Remove installer and lock down write permissions after installation per upstream guidance.
9. Define bridge via bounded authenticated API only; never direct phpBB-to-studio SQL coupling. No cross-system shared admin/root.
10. Publish a forkable reproducible example with .env.example placeholders, public test fixtures, pinned hashes, SBOM and licenses; exclude secrets, personal art, database dumps and signing keys.

## 8x8 escalation
- Cross-check 8 surfaces: kernel, filesystem, PHP runtime, database, web ingress, identity, uploads, backup.
- Each surface: install, read, write, reject, recover, update, audit, rollback.
- Record exact source SHA, command, exit code, sanitized evidence and owner.

## 16x16 escalation
- Expand only for failing controls and real multiuser runtime: permissions, tenancy, secrets, restoration, security regression and load.
- No synthetic 256-pass GREEN. Independent runtime and owner approval required.

## Crown gates
Canonical SQL schema exists as a local-only stub; not a live DB. phpBB is not installed or configured by this proposal. Cloudflare Workers failed build remains separate and unresolved. Crown STOP.
