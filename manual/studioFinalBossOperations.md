# Studio final-boss operations: scoped, boring, recoverable

**2026-11-15. Owner: Professor. Source repository:** `eggie-admin/LuHm-OS`. **Public home:** `eggiebagelface.art`. **Global product Crown:** STOP. Only the Instagram comeback image/caption is live-verified by provider readback. [Public post](https://www.instagram.com/p/DfxLQKuDbOM/).

## The one sane architecture

| Responsibility | System | State |
| --- | --- | --- |
| Public identity / art updates | `@eggiebagelface` Instagram through Windsor.ai | CONNECTED, one verified published post |
| Studio, film, personal art | One brand registry, three independently branded production desks | GITHUB SOURCE + PRIVATE DRIVE |
| Social approval | Owner-only Google Drive release desk / native Sheet | VERIFIED PRIVATE, record EBA-002 PUBLISHED |
| Future Meta/Facebook syndication | Metricool brand connection + native account approval | BLOCKED: Metricool brand has no social account connected; Facebook business access unverified |
| Source / CI / partner fork | GitHub immutable commits, PRs, code review | ACTIVE |
| Public landing page | `studioLanding/index.html` | SOURCE READY; domain DNS/provider host not proven |
| Private masters and backup | Owner-only Google Drive, offline encrypted restore copies | OWNER DRIVE KNOWN; automated restore tests not verified |
| Registry & audit receipts | Small local SQLite snapshot (optional later PostgreSQL) | NONSECRET SCHEMA, NO LIVE PRODUCTION DATABASE CLAIM |
| Remote AI research/agents | One Lum-owned task manifest and provider adapter | DOCUMENTED ONLY; independent workers quarantined |
| Firmware signing / OTA | Platform and OEM-specific signing gates | UNPROVEN; no firmware keys created |

Do not create three competing sources of truth. GitHub is source authority; Drive stores durable binaries; SQL indexes metadata and receipts. Never duplicate a private key into SQL, Git, prompt, project file, APK or Drive plaintext. Even a private SQL database is a high-value exfiltration target.

## Release lanes: visibility and derivative rights

1. `privateMutation` (private): all experiments, originals, unapproved characters, private keys (in separate key vault), internal builds, donor triage and proposed patches. No public links.
2. `proposedInvite` (invite-only): strictly **private** repository/folder, named collaborators and least-privilege access. A link to a public pull request is NOT invite-only. Do not use public Git PRs for confidential source or issue contents.
3. `betaAfterDark` (invite-only): existing mature Art/Content Canon; do not silently make this family public. No explicit private media exports.
4. `publicBeta` (public forkable *source*): sanitized code, README, license compatibility, attribution, CI, build/test receipt. A public source fork does **not** imply the binaries are production-signed or authorized to install as an OS update.
5. `cathedralPublic`: rights-cleared safe art and approved public website/social posts.
6. `ltsPublic`: supported signed app/runtime releases only after verified install/update, rollback, key custody, dependency manifests and incident response.

The only presently approved social asset is `campaign/instagramReturn20261115Receipt.json`. Keep exact media hash/source URL and permalink in the nonsecret registry; private internal storyboards remain private.

## Google's AI fast lane, then optional higher-value OpenAI

Use `deterministicLocal -> verifiedGoogleFlashOrAntigravity -> explicitlyEntitledOpenAI`.

- The Google choice should be a **provider adapter**, not a global hidden agent or a rewrite of ChatGPT's model selection. Google's Antigravity agent and Gemini Flash are candidates; their current access and account quotas must be read from an **authenticated** Google project before activation.
- Google Drive storage (terabytes) is **not** Gemini tokens or API budget. Google AI consumer Pro/Ultra, AI Studio projects, Antigravity credits and Gemini paid API billing are separate entitlements. Avoid hidden auto-spend.
- Set **USD 0 default budget for paid external inference**, modest `max_total_tokens`, rate limit, fixed scope, time limit, per-provider request cap, PII/secret redaction, source commit binding, and durable task receipts. Only increase after explicit budget approval.
- Google Antigravity is capable of autonomous tools. Existing `companyWideOperationalQuarantineV1` still prohibits hidden active agents. A proposal for an autonomous worker is not evidence that it is running.
- Treat external AI output as **candidate evidence**. Never allow a provider to approve, sign, publish or merge by itself. Any fallback to OpenAI/Astra requires real entitlement/cost proof, not assumptions about subscription.
- Use local existing caches, static checks, GitHub and connected Drive before spending inference tokens. Provider capacity pays for novel reasoning, not repeated status polling.
- Never forward full private personal art sets or key material to third-party model endpoints without a separate purpose and owner permission.

## Android, Samsung, Google, Apple: separate certificates, never a fake global signer

- **GitHub/GPG:** owner identity signs Git commits/tags, key held on trusted owner hardware. GitHub bot commits may be GitHub-Verified but not owner-GPG-signed.
- **TLS:** publicly trusted Let's Encrypt only for the user's strict public certificate policy; Cloudflare/Render issuer requires live check. TLS cert is **not** APK/OTA code signing.
- **Android APK:** maintain one production app signing lineage; preserve original signing identity when publishing updates. Google Play App Signing is service-specific and requires Play developer enrollment. Never replace a signed app via unrelated key.
- **AOSP/firmware OTA:** OEM/ROM boot chain and recovery accept only their expected update keys. A freshly generated signing key does not grant trust on Samsung, Apple, Google, or any existing device. Firmware/bootloader unlock or recovery changes can destroy user data and are blocked without verified device ownership, backups, test hardware and vendor-specific documented path.
- **Samsung Knox:** a separate enterprise/mobile trust model. No Samsung signing certificate or partnership is inferred.
- **Apple Developer:** actual developer enrollment/team and Apple-issued signing certificate are mandatory for Apple's platforms. No Google/Samsung certificate becomes an Apple distribution identity.
- **Public key evidence only:** fingerprint, certificate chain *public* info, expiry, issuer, rotation plan, signed artifact SHA-256. Private signing keys live in hardware-backed keystore or encrypted owner vault, with offline backup and restore proof.
- **TTL:** metadata/artifact digests can be preserved indefinitely with versioned receipts; use provider-managed renewal for public TLS; access tokens minutes/hours and narrowly scoped, never maximize credential TTL simply to avoid maintenance. Rotate or expire privileges according to risk. Never have unexpiring bearers.

## SQL: metadata, not a secret vault

- Schema: `host/api/studioRegistrySqliteV1.sql`.
- Builder: `python3 tools/buildStudioRegistrySqlite.py --output /secure/local/path/studioRegistry-20261115.sqlite3`.
- Builder refuses to overwrite an existing snapshot; only documented public branding, current nonsecret verification receipts, release policy and UNVERIFIED vendor enrollments are seeded.
- Use encrypted and access-controlled owner backups; verify a restore on a second independent device. SQL `CREATE TABLE` and a local dry run are **not** evidence that a Render, PostgreSQL, MySQL or phpMyAdmin service has been deployed. Do not add phpMyAdmin/phpBB to the kernel: that would add attack surface without helping app signing or studio releases. phpBB may later serve a separate community site behind authentication, not the boot chain.
- PostgreSQL migration is a separate task on a chosen authenticated workspace with backup, restore, migrations, least privilege, point-in-time recovery and read-only health checks.

## Default new ChatGPT project chats: practical bootstrap

ChatGPT Projects can share **project instructions, uploaded files and supported connected sources**. There is no documented guarantee that merely starting a new project chat automatically mounts a particular third-party plugin, executes remote providers or live-refreshes a GitHub repo.

Add the short template below once to **Project settings > Instructions**, and add the private Google Drive release desk or appropriate source links under **Project sources**. Keep all secrets out of project instructions:

> This project is LuHm-OS: Project Premonition (legacy Project Hydra). Professor is final authority; Lum is the sole conversational orchestrator. On substantive work, first inspect current GitHub main at eggie-admin/LuHm-OS and its doctrine/currentSourceTruthV3.json, doctrine/projectChatCanonV1.json, AGENTS.md, doctrine/studioFinalBossControlV1.json, plus the relevant skill and verified receipts. Distinguish observed runtime state from source plans. Use deterministic/local checks first, authenticated Google Flash/Antigravity only within proven quota, then OpenAI capabilities only when justified and entitled. Do not auto-publicize art, expose keys, buy resources, start independent agents or override the quarantine. Keep private/review lanes private; publish only scoped Professor-approved artifacts. Respect existing Canon and release boundaries.

Review this setting when platform app/tool availability changes. **Project instructions provide context, not automation or connection credentials.** The user must connect provider apps and authenticate billing independently.

## Follow-up order, strict evidence gates

1. **DONE:** Instagram 2026-11-15 post published and independently read back.
2. **PENDING:** Facebook Page/Business Manager asset inventory, page access, verified relationship to the Instagram professional account, and an intentional crosspost approval.
3. **PENDING:** Connect `@eggiebagelface` and any verified Facebook Page to Metricool for approval-based scheduling; first test a single dated **draft**, then review, then publish after owner approval.
4. **PENDING:** Verify DNS/Cloudflare and domain control, publish standalone static landing without disturbing existing hosts and ensure actual Let's Encrypt issuer policy before declaring domain GREEN.
5. **PENDING:** Activate studio email aliases only after verified Cloudflare routing destination/MX, test inbound delivery, secure outbound reply identities separately.
6. **PENDING:** Verify Google project and Antigravity/Flash credits, start with zero-cost bounded read-only one-shot task.
7. **PENDING:** Validate local SQLite snapshot and private backup; choose PostgreSQL only after workspace identity and storage needs are proven.
8. **PENDING:** Owner platform developer enrollments, firmware signing custody and real hardware update tests.
9. **PENDING:** Public forkable beta source and LTS release pipeline after distinct security/release receipts.

Never present the full system as production GREEN based only on the source and one successful Instagram post.
