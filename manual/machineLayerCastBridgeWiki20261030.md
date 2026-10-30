# LuHm-OS machine layer wiki / CAST bridge staging (2026-10-30)

Status: DOCUMENTATION ONLY; no device, key, deployment, agent or protected-main change. Source baseline: `360381ef34ff8e38f3f3b4cee6241121f2fbb27b`. Crown STOP remains until independent approval and physical evidence.

## Two 4×4 matrices
Machine matrix: (1) kernel/systemd/APT/permissions; (2) Python/Flask/Node/npm/Java; (3) SQLite/schema/migrations/backup/integrity; (4) networkd/Netplan/TLS/firewall/antenna. For each: source provenance, configuration, security and benchmark/test evidence.
Bridge matrix: Android/Gradle; browser adapters; AI mock/provider adapters; studio Godot/Blender/FFmpeg. For each: API contract, license boundary, headless fallback and physical/reproducible verification.

## Architecture policy
- The Linux kernel is GPL-2.0-only (with syscall note); repository root is GPL-3.0-only. Preserve both and all upstream notices. Apache-2.0 code can enter GPLv3 projects, but GPLv3 derivatives cannot simply be relicensed Apache-2.0. Only separately owned, proven clean-room first-party modules are Apache candidates.
- Categorize dependencies as: exact Apache-2.0, other permissive, reciprocal/copyleft, proprietary/terms, unknown. SPDX metadata alone is not source/binary redistribution proof. No automatic vendor substitution.
- Keep npm for JS builds, Python for service/API, Gradle for Android, APT for host provisioning; do not pretend npm owns the host. Pin and verify exact dependency versions; no install scripts on trusted devices without review.
- Headless service should expose versioned JSON capabilities, health, read-only status and explicit permission-gated jobs. Mock AI adapter first; cloud/paid/privileged execution disabled. Browser and studio adapters are optional.
- Stage machine-human SQL boundary with schema_version, device_capability, job_request, job_receipt, audit_event, vendor_provenance and migration_history entities. No user secrets in receipts. Enforce foreign keys, migrations with reversible plans, transaction rollback, bounded query size, and backup/restore tests before any live schema mutation.

## Source-only quick-start checks (not execution authorization)
```sh
git rev-parse HEAD
git status --short
find . -name package-lock.json -o -name pyproject.toml -o -name requirements.txt -o -name build.gradle -o -name '*.sql'
npm --version
python3 --version
java -version
```
Review manifests and lockfiles before running `npm ci`; npm lifecycle scripts may execute code. Use isolated ephemeral CI with restricted network and no secrets. Never run `apt upgrade`, `netplan apply`, certificate issuance, cloud requests, migrations or device installation from this wiki.

## NPM help / developer runbook
1. Locate the package root and committed `package-lock.json`; inspect `package.json` scripts and `.npmrc`.
2. For deterministic CI, `npm ci` requires lockfile agreement and does not update manifests. Treat dependency lifecycle scripts as executable third-party code.
3. Record Node/npm versions, exact Git SHA, resolved lockfile package versions, SPDX identifiers, NOTICE/LICENSE files and package integrity hashes. Compare baseline vs proposed dependency count before reducing vendors.
4. Fail closed on unreviewed postinstall, absent license evidence, unpinned remote scripts, native addons or silent cloud calls.

## Required benchmarks / acceptance gates
Record host model, kernel, distribution, tool versions, exact SHA, wall clock, CPU, peak RSS, disk, network bytes and pass/fail for each applicable run. Cover clean boot, service cold start, SQLite integrity/migration rollback, offline API, network disconnect/recovery, microphone/camera enumeration (owner-authorized hardware only), Gradle source build, ZIP portability and mock AI adapter. 500 passes is a planned budget, NOT 500 completed executions.

## Vendor documentation
- npm clean install: https://docs.npmjs.com/cli/commands/npm-ci/
- npm lifecycle scripts: https://docs.npmjs.com/cli/v11/using-npm/scripts
- Flask deployment: https://flask.palletsprojects.com/en/stable/deploying/
- SQLite: https://www.sqlite.org/docs.html
- SQLAlchemy: https://docs.sqlalchemy.org/
- Alembic: https://alembic.sqlalchemy.org/
- Netplan: https://netplan.readthedocs.io/en/latest/
- Certbot: https://certbot.eff.org/instructions
- SPDX: https://spdx.org/licenses/
- Apache/GPL compatibility: https://apache.org/licenses/GPL-compatibility.html
- Kernel licensing: https://kernel.org/doc/html/next/process/license-rules.html
- Android Gradle: https://developer.android.com/build
- Python ZIP: https://docs.python.org/3/library/zipfile.html
- Godot: https://docs.godotengine.org/
- Blender: https://docs.blender.org/
- FFmpeg: https://ffmpeg.org/documentation.html

## Next smallest safe action
Read-only inventory at exact SHA of package manifests, Python dependencies, SQL schemas, Gradle, workflow definitions and network config; produce a versioned dependency/provenance matrix and bounded mock migration test. Do not declare CAST-ready until CI receipts, license files and owner-authorized hardware checks exist.
