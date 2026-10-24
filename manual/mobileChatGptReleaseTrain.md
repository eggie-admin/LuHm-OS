# LuHm OS ChatGPT in-chat mobile release train (source candidate)

**Scope:** ChatGPT plugin experience on supported mobile clients. An iPhone arm64 test uses the iOS ChatGPT application and its supported plugin/Web UI facilities; it does **not** install a GitHub build or Android APK. The independent Android F-Droid lane remains separate. No Render workspace or OpenAI Codex workflow is required for this source proposal.

## Immutable identities and source truth

- Repository: `eggie-admin/LuHm-OS`; exact Git commit recorded with every test, package and review. Existing main-CI laws and protected PR promotion remain active. A future proposal to make a durable workspace the first staging source needs a separate atomic Canon migration: the currently promoted source authority remains GitHub.
- GitHub MCP app: `luhm_open_cockpit` -> `ui://luhm-os/cockpit-v2.html` (full studio).
- New *candidate* mobile fallback: `luhm_open_mobile_cockpit` -> `ui://luhm-os/mobile-cockpit-v1.html`. The full studio is retained. Mobile fallback is single-file, no external assets, read-only, and returns a human-readable status when iframe rendering fails.
- Owner personal ChatGPT Site plugin `Project Hydra` v1.0.11 is **USER/PRIVATE** and has an independent Site/App binding. GitHub MCP source commits do not automatically update the installed Site plugin. Plugin ZIP skill updates do not create Site backend methods.
- **Required proof before calling the screenshot fixed:** GitHub exact-source tests, the selected MCP endpoint's tools/resources discovery, ChatGPT current-account mount on a mobile browser/app, and independently a tester device invocation. A successful backend tool response is not an accepted UI mount.
- Screenshot symptom: ChatGPT says “Couldn't open Open Lu…” with Retry; this is *host/UI load failure observed on one Android browser*, not evidence of failed MCP transport, and it says nothing yet about iPhone behavior. Check host resource metadata, registered `text/html;profile=mcp-app` resource, client console/CSP, source size and UI handshake.

## Alex-class private iPhone testing lane (no identities in public source)

Only one approved outside tester, privately coordinated by the Professor. **Testing**, not beta/release/publishing:
1. Confirm an authorized ChatGPT distribution method (eligible shared workspace plugin or independently approved distribution); personal USER/PRIVATE plugins are not automatically shareable.
2. Give the tester the *ChatGPT plugin*, not a website, APK, Godot Web link or GitHub branch. No login/password exchange, personal contact data, or account token in public GitHub issues/CI.
3. First prove a simple text tool call. Then explicitly open the **mobile** tool and confirm an interactive inline card, portrait/landscape, display expansion, touch targets, VoiceOver, scroll, and return to conversation. Check on iPhone arm64 with device/iOS/client version receipt. If mobile fallback renders but full studio does not, record this discrepancy.
4. Confirm all 15 crew identities display as registered while operationally quarantined; no false autonomous work, server writes, signing, paid API calls, personal Drive assets, or access to other users' data.
5. Store tester results through an approved private feedback channel, keeping only redacted pass/fail and exact plugin version/source mapping in public receipts.

## Four canonical policy lanes plus final stable publication

| Lane | Who acts | Required acceptance | External users |
| --- | --- | --- | --- |
| `testing` | Professor, Skuld compatibility, Yume mobile UI, Urd evidence | source fixture + in-chat owner mobile probe | Not admitted by a source commit |
| `proposed` | Tetsu source candidate, Belldandy receipts, Urd review | exact-head CI, rights/privacy, rollback and diff | None |
| `beta` | Scoped Kaji package CAST + authorized tester | signed/hashed or otherwise provider-accepted artifact, working tester ChatGPT install/mount, privacy and feedback | Only through actually supported opt-in distribution |
| `betaLts` | Professor-controlled compatibility/maintenance | pinned accepted beta, repeat mobile checks and rollback rehearsal | Explicitly accepted beta maintenance |
| **stable** (future publication milestone, **not** a fifth activated doctrine lane) | Professor final Crown | independent beta acceptance, versioned plugin package/source evidence, OpenAI review/approval when required, security and rights checks, accessible current host, demonstrated rollback | Only after separate approval and publication receipt |

GitHub PR merge is source promotion only; it cannot publish a ChatGPT directory plugin, add tools to an unrelated Site app, install a user-private plugin for an outside tester, or release Oni workforce quarantine.

## Lum and Oni ownership for real orchestration

Lum coordinates task envelopes and explicitly scoped dispatch. Urd adjudicates live receipts and security; Belldandy records source hashes, tester evidence and rollback; Skuld handles iOS/Android/MCP protocol compatibility; Yume handles functional mobile UI; Tetsu prepares source candidates without compiling; Kaji packages **only** after an exact scoped single-use CAST. Other Oni may take real work only after their runtime capabilities, task scopes and company quarantine release are independently proven. Max three support workers in parallel, one mutable source lane. Never represent display animations, roleplay or training files as autonomous workers.

## Owner's phone acceptance and host refresh gate (October 24)

The connected Project Hydra personal Site currently exposes only `luhmConnectionStatus` and
`luhm_open_cockpit`, even though the exact live Render `main` service has source for
`luhm_open_mobile_cockpit` and `luhm_open_oni_summoner`. A GitHub/Render deployment
**cannot update the independently managed Site connector tool list**. Refresh or repair
the existing Site's MCP connection in the ChatGPT plugin settings without deleting the
private plugin or changing its Site binding. First compare the current Site-visible tool
names with the endpoint `tools/list` result and inspect the UI resource metadata.
Do not offer desktop mode as Android acceptance.

When the full or mobile cockpit card *actually displays inside the current ChatGPT
conversation*, press **Send in-chat mount test**. The widget requests a follow-up message
with resource URI, source reference, viewport width, and `userClicked=true`. This is
a **candidate receipt** for a visible interactive widget, not platform identity
attestation: the Professor must also report whether the card was in the ChatGPT mobile
client, portrait/touch worked, and no browser harness navigation occurred. If the
button is missing or no message returns, retain `HOST_MOUNT_BLOCKED` and investigate
resource discovery/client mount instead of promoting green.

The 15-agent Canon registry remains held by `companyWideOperationalQuarantineV1.json`;
no runtime mesh activation is allowed until the specified supervised Belldandy/Urd
receipts, explicit scoped Professor release, and verified provider-side task route.
Source-only tests and animation cannot stand in for real agent mesh deployment.

## What remains to be proven

- [ ] Host that serves GitHub MCP resources includes the new mobile route/tool, with exact deployed source SHA
- [ ] The *actual installed ChatGPT Site app* is wired to that host or implements equivalent native UI functionality
- [ ] Owner's Android browser/mobile ChatGPT UI mounts without “Couldn't open”
- [ ] Private external iPhone arm64 ChatGPT installation + interactive mount, permission and rollback evidence
- [ ] Beta and stable review/publication receipts
- [ ] Runtime supervised worker task with signed or trusted receipt, followed by separately authorized quarantine release

**Source configured != UI mounted != device tested != agent executing != beta published != stable release.**
