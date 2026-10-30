# LuHm-OS | Deep Dungeon privacy, API and release-hardening review | 2026-10-30

**Scope:** public `eggie-admin/LuHm-OS` candidate branch based on CAST #455; selected owner-private Google Drive permission **metadata**; workflow source; release and agent security contracts. **Source audit, not penetration test or proof of live account security.**

## Time boundary

The requested six-month window is 2026-04-30 through 2026-10-30. This GitHub repository was **created 2026-09-25**, so the six-month lookback cannot be represented as six months of repo history. Existing private documents from other dates may contribute only when individually authorized and relevant. Do not infer absence of earlier project history from the GitHub repository's creation date.

## Findings

| ID | Severity | Observation | Required next evidence |
| --- | --- | --- | --- |
| PRIV-001 | HIGH | In a six-document targeted Drive permission-metadata sample, **five** owner-private artifacts have `anyone:writer` (link-wide editor) and one is not shared. This is not evidence of unauthorized access. | Owner-authorized restriction to named editors; independent readback; revision and access review. |
| CI-001 | MEDIUM | Existing social-video orchestrator used floating `ubuntu-latest` and `actions/checkout@v4` without exact PR-head binding. | Current candidate fixes with pinned Ubuntu/checkout SHA, `persist-credentials: false`, least privilege and source-check tests. |
| AGENT-001 | HOLD | Canonical all-15 worker quarantine is active, including both human-facing goddess and specialist agent names. | Explicit individual worker resume and current ChatGPT host evidence, not source role labels. |
| API-001 | UNVERIFIED | A public read-only MCP surface and static UI exist; end-to-end private API authn/authz, remote TLS endpoint settings and storage encryption have not been verified in the live providers during this review. | Scoped runtime tests, authenticated negative tests, transport proof, request budgets and key custody. |
| CAST-001 | HOLD | Source-stage CI green is not the owner `/cast` dispatch, real Samsung app, signing or public release. | Exact-current-main owner CAST, build artifact, installed physical QA, separate Crown approval. |
| MEDIA-001 | HOLD | Rights/age/privacy approval for family content and adult catalog is separate from a working render. | Proven licenses, private-to-public asset derivation, parental consent and platform publishing policy. |

**Public-source privacy:** This review deliberately omits private Drive URLs, file IDs, access emails, media contents and potentially sensitive personal details from the repository. Fix permissions using the owner account outside public CI. Do not paste secret values into issue comments.

## Encryption by data, not by release channel

Four data classes: **PUBLIC_APPROVED**, **INTERNAL_STUDIO**, **RESTRICTED_PERSONAL**, and **SECRETS_SIGNING**. LTS and remote operations need approved TLS, encrypted restricted data at rest, access control, encrypted backups, verified recovery and owner-held signing secrets. Cleartext local storage can only be an opt-in disposable **synthetic/non-identifying** test case. Plaintext local SQLite is not acceptable for family data, original private footage, exact personal hardware inventory, API tokens or credentials without an independently encrypted storage boundary.

No custom cryptosystem; choose established platform mechanisms. Base64url is an envelope, not confidentiality. TLS and encrypted disks do not replace authenticated authorization. Never send agent secrets or private photos to remote LLM providers without explicit consent and provider entitlement review.

## API and agent threat model

Bind each operation to identity, scope, action, task ID and exact immutable source. Keep truly public, read-only, bounded routes distinct from private writes. Require authentication for private endpoints, per-object authorization, idempotency and replay protections for writes, content-type/size validation, hardened CORS, CSRF defenses for cookie-authenticated requests, trusted proxy-header rules, redacted logs, request and streaming limits, and no public SQL admin or shell.

The agent registry does **not** grant execution. Source text, web pages, model outputs, social comments and remote manifests are untrusted data; they cannot grant permissions, expand scope, pick arbitrary tools or activate workers. Default to zero background workers, one mutable source lane, explicit user consent and a verified rollback receipt.

## Social and media readiness

- **Creator desk:** draft brand identity, original logo/thumbnail/storyboard and teaser privately; no publish until rights, account ownership, consent and audience restrictions are proved.
- **Family and minors:** keep family assets and roles isolated by server-side access controls, not merely CSS or client age check. Supervised content and publishing flows must follow relevant platform policies; no public exposure of children's private footage by default.
- **Adult:** restricted catalogs and age-appropriate access review separate from family outputs. No adult assets in F-Droid/public family package.
- **Release:** public-safe marketing cannot be treated as permission to publish APK, private AI model, third-party game mod or assets without rights.

## Source candidate implementation

- `doctrine/dataProtectionLadderV1.json`: descriptive policy only, not actual TLS/ACL/OS encryption changes.
- `tools/deepDungeonSecurityAudit.py`: offline fail-closed policy verification and high-confidence **newly added** tracked-source credential/private-file/workflow-risk categories. It only emits categories, never candidate values; it does not exhaustively scan historical commits or prove there are no secrets.
- `tests/testDeepDungeonSecurityAudit.py`: offline synthetic negative regressions.
- `.github/workflows/deep-dungeon-security-audit.yml`: exact-source, least-privilege read-only workflow; preserves CAST and quarantine gates.
- `.github/workflows/social-video-orchestrator.yml`: pinned GitHub Actions inputs, deterministic runner, no persisted checkout token; social media upload remains OFF.

**No Drive permission changes, secret rotation, API deployment, Render mutation, Cloudflare change, owner CAST dispatch, physical Android build/installation, agent activation, signing, marketing publication or merge to protected `main`.**

## Prioritized next owner tasks

1. Restrict the five over-shared Drive documents and verify current permissions without embedding their links in public source. Investigate suspicious revision history if indicated.
2. Review exposure and rotate any **actually compromised** credentials, while avoiding routine public disclosure. Confirm GitHub scanning and branch/release protection in the owner's settings.
3. Exercise the private API with real authenticated/unauthenticated requests, token expiry and object-level access denial; verify LTS device encryption and encrypted backups.
4. Confirm current ChatGPT host visual mount against the deployed source/URI; measure signed APK installation and real Godot gameplay separately.
5. Prepare a rights-cleared, family-safe brand kit and an independently reviewed social/YouTube publishing plan.

**Verdict:** private-sharing remediation and runtime proof are outstanding. Source staging may proceed to review; **CROWN STOP** for production/public release.

## Security reference standards

- OWASP ASVS 5.0: https://asvs.owasp.org/
- NIST SP 800-63B-4: https://csrc.nist.gov/pubs/sp/800/63/B/4/final
- GitHub Actions hardening: https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions
