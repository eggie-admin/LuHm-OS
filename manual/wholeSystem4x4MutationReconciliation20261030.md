# Whole-system hardest-first 4x4 mutation reconciliation (source-only)
Source parent babaf6e6a0beeb3561840c45a8ae64a5ac7a5493. Draft PR #460. This is a proposal, not a merge or production promotion.

| Risk order | AI | Background | Frontend | Machine |
|---|---|---|---|---|
| P0 | tool capability allowlists, prompt injection isolation, human approvals | OS privilege boundaries, secret isolation | authentication, CSRF/XSS, session lifecycle | verified boot, firmware provenance, kernel/driver security |
| P1 | local/cloud adapters, deterministic mock | SQL schema/migrations, transactions | Android bridge, versioned contracts | networking, firewall, device permissions |
| P2 | orchestration queue, budgets, cancellation | API health, retry/idempotency, job receipts | browser compatibility, offline mode | apt/npm/python/Gradle lockfiles |
| P3 | latency/token-free mock benchmarks | startup/memory/DB benchmark | accessibility, frame pacing | boot/device performance receipts |

## Mutation pipeline
Inventory -> classify provenance and ownership -> smallest patch on draft branch -> static checks -> offline negative tests -> exact-SHA CI -> independent review -> approved integration candidate -> device-specific validation -> separate promotion. Never bypass earlier gates with a passing downstream check.

## Non-negotiable invariants
No protected-main merge, deployment, secrets, paid cloud, agent activation, firmware flash or Crown promotion from this document. Existing GPL and third-party notices remain intact. Apache-2.0-only for new isolated components only with authorship proof. Browser, game and AI dependencies remain optional from the headless service. Keep SQL machine-human contract backward compatible.

## Failure-injection test targets
- AI tool request without capability token rejected; untrusted text cannot authorize shell or keys; mock adapter requires no network.
- Background duplicate job is idempotent; SQL migration rollback leaves integrity_check clean; logs redact secrets.
- Frontend rejects forged auth state; Android/browser adapters tolerate absent device and offline network.
- Machine capability inventory marks absent firmware/device as unknown, never healthy; archive and package provenance bound to exact source SHA.

## Receipts required
Per cell: test ID, exact commit SHA, platform, source docs, license, commands, expected/actual, duration, peak RSS, failures, rollback and reviewer. CI success is not hardware validation. 500-pass budget is not proof of execution.

## Official starting documentation
https://owasp.org/www-project-top-10-for-large-language-model-applications/
https://docs.python.org/3/library/sqlite3.html
https://www.sqlite.org/lang_transaction.html
https://flask.palletsprojects.com/en/stable/security/
https://docs.npmjs.com/cli/commands/npm-ci/
https://developer.android.com/topic/security/best-practices
https://www.kernel.org/doc/html/latest/
https://spdx.dev/learn/handling-license-info/
