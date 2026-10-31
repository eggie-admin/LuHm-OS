# Green Crown Cathedral | Forking, vendor provenance and release channels

**Status:** SOURCE governance milestone. **Not** a public beta or certified security audit.

The public repository is [LuHm-OS](https://github.com/eggie-admin/LuHm-OS). GitHub source forks are available immediately because the repository is public; forkability does not imply a signed installable package or license clearance for every included asset. Project Premonition is the current product identity; Project Hydra remains historical provenance. The repository is GPLv3; individual third-party files and artwork may carry separate notices.

## The three source channels

| Channel | Fork developer source? | Official release? | Gate |
|---|---|---|---|
| Proposed | Yes, via fork or review branch | Not automatic | Exact-source CI, license review, hash/receipt |
| Beta | Yes, from public source | Blocked until evidence | Stable owner signer, real-device acceptance, privacy and art rights, explicit CAST |
| Stable | Yes, subject to licenses | Blocked until independent proof | Beta upgrade/rollback, provider/channel acceptance, Professor final artifact review |

GitHub branches and prerelease tags are **not** environments. Forks keep their own permissions and workflows; they do not inherit Professor's production credentials. Community forks should use distinct package names/signers and avoid impersonating official LuHm binaries.

## Contributor quick start

1. GitHub **Fork** the repository, choose your namespace, clone your fork; add `upstream` pointing to the canonical project.
2. Create a branch `candidate/<small-purpose>`, review `SECURITY.md`, `CONTRIBUTING.md`, `LICENSE`, and current doctrine.
3. Use `npm ci --ignore-scripts` only in the approved npm package directories; never run unknown donor install scripts. For Python/Gradle/Godot, use each native package manager rather than npm as a replacement.
4. Commit source, deterministic tests, sanitized evidence references, SPDX/NOTICE obligations and rollback instructions. Open a fork-to-upstream PR for review.
5. To sync: `git fetch upstream`, inspect the upstream diff, then deliberately update the fork branch. Do not force-push over reviewed history.
6. Private vulnerabilities go through GitHub **Security Advisories** if enabled, never a public reproduction containing live secrets.

## Vendor fork intake and ComfyUI

The source-only inventory `doctrine/communityForkChannelsV1.json` pins eight currently observed dependency declarations (npm, Python MCP and Android Gradle). Its exact version snapshots **do not** prove dependency integrity, license grants, security fixes or installed native runtimes.

Before creating each vendor fork: find and verify its official upstream repository/tag, inspect the actual license and any NOTICE, review transitive dependencies and provenance, identify the smallest needed patch, record original+fork remotes, tag and commit hashes, fork owner, security update route, rollback and all redistribution obligations. Do not automatically clone/fork every dependency. Prefer upstream packages and patches over maintaining an uncontrolled vendored codebase.

ComfyUI's editor-save workflow JSON and API execution JSON differ. Treat untrusted custom nodes and workflow scripts as executable software requiring separate sandbox review, not harmless HTML UI metadata. The mobile thin client should exchange typed task/receipt JSON only and never execute foreign node code.

## Security and deployment boundary

- Protected source PR and no automatic release.
- Dependabot reviews are proposals. Confirm secret scanning, push protection, CodeQL, Dependabot alerts and repository rulesets in live GitHub settings.
- Original art and owner keys remain out of public Git. Check the **full Git history** before broad external promotion; no source-only policy proves absence of historical leaks.
- Official Proposed package, signed Beta APK/F-Droid, ChatGPT host and Stable each have distinct release receipts. Use existing `manual/pluginReleaseHub.md` and `doctrine/finalFormPublicReleaseGateV1.json`, not this guide, for actual promotion.
- A Cloudflare or Render build result, public web availability and physical Samsung acceptance are distinct independent proofs.

**Green source milestone is not the same as full Green Crown.**
