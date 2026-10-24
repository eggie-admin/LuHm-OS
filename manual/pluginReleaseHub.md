# LuHm OS GitHub Release Hub

**Live Downloads:** https://github.com/eggie-admin/LuHm-OS/releases

**Canonical GitHub source:** `eggie-admin/LuHm-OS`. Use `python3 tools/pluginReleaseHub.py --format markdown` to query the GitHub Releases API without cache and display the latest *verified published package* for each of **Proposed**, **Beta**, and **Stable**. This inventory updates from release metadata whenever it is run; no stale static pointer or false "latest" claim.

## Channel definitions

| Channel | Release tag | GitHub behavior | Minimum proof |
| --- | --- | --- | --- |
| Proposed | `luhm-plugin-proposed-vX.Y.Z-s<sha8>` | Prerelease; not GitHub's overall "Latest" | Owner CAST built package, exact source/version, checksum, manual owner promotion |
| Beta | `luhm-plugin-beta-vX.Y.Z-s<sha8>` | Prerelease; never automatically promoted to stable | All Proposed checks **plus** accepted in-ChatGPT install, independent mobile client test, Urd review, Professor promotion |
| Stable | `luhm-plugin-stable-vX.Y.Z-s<sha8>` | Full release; explicit GitHub "Latest" | All Beta checks **plus** beta acceptance, rollback receipt, supported ChatGPT host/provider publication approval and owner sign-off |

**Separate distribution formats:** existing `android-web3-*` GitHub prerelease APKs belong to the Android/F-Droid family. They are **not** ChatGPT plugins and cannot install into iOS. The ChatGPT plugin ZIP is a distributable *developer package*, not a one-click install for another person's ChatGPT account. Alex's private iPhone arm64 test still requires supported plugin invitation or provider-approved distribution plus on-device UI mount.

## Merge → deploy → reconcile → cache → ping

1. **Merge:** Review exact-head source diff, GitHub Actions negative tests, private asset/secret safety and scope; preserve protections on `main`. No unreviewed direct commit or automatically merged source.
2. **Deploy:** Source PR merge is not live ChatGPT deployment. An explicit **Professor CAST** compiles a plugin package in `.github/workflows/public-plugin-package-cast.yml`. The new `plugin-release-hub.yml` can, on a separate owner-only manual dispatch, publish a verified CAST artifact to GitHub Releases. This publication does not install the Site app, update MCP backend, deploy Render, or grant agent permissions.
3. **Reconcile:** Verify SHA-256 equals the artifact receipt and embedded manifest; verify owner, originating workflow run, source commit, release tag, version monotonicity and actual published asset listing. Never overwrite a release tag or silently change Stable.
4. **Cache:** For public download health, request fresh GitHub release metadata with `Cache-Control: no-cache`. **Do not purge Cloudflare/DNS/CDN or production caches** on a GitHub package publish; website and MCP cache invalidation require separate origin/host authority and runtime receipts.
5. **Ping:** Download the public ZIP from the new GitHub release URL, hash its exact bytes again, confirm the checksum and record the outcome. **HTTP 200 alone is not proof** that the ZIP is correct or installed in ChatGPT.

## Current reality and command

As of the October 23, 2026 audit, GitHub listed 13 Android Web3 prereleases and **zero confirmed LuHm ChatGPT plugin release packages**. GitHub `/releases/latest` returned 404. The index must therefore say **NOT PUBLISHED** for these three plugin channels until genuine files are released. Never point ChatGPT plugin buttons at Android APKs or the owner-private Site plugin.

Commands:

```bash
python3 -m unittest tests/testPluginReleaseHub.py tests/testPluginReleasePromotionGate.py -v
python3 tools/pluginReleaseHub.py --format markdown
python3 tools/pluginReleaseHub.py --format json
```

The source CI check runs on scoped pull requests, **without publishing anything**. Channel publication is available only through the manual `workflow_dispatch` path with verified `PROMOTE_RELEASE`, Professor repository-owner actor, exact current main source, original successful CAST workflow run ID, SHA-256 digest and no pre-existing matching tag.

**Beta and Stable are fail-closed:** The promotion gate additionally requires `pluginReleaseAcceptance.json` bound to exact source, channel and package digest, with genuine external ChatGPT host, mobile device, independent review and Professor receipts. Stable also requires tested rollback, successful beta and provider approval. The current CAST artifact workflow does not supply this acceptance receipt, so Beta/Stable release dispatches will **fail by design until independent proof is implemented and attached**. Do not modify proofs merely to flip status.

## Release and security boundaries

- GitHub repository `main` protection must be restored before merging this proposal. Do not rely on temporarily open branch rules as production safety.
- The installed Project Hydra personal Site plugin v1.0.11 and repository `plugins/luhm-os/plugin.json` are distinct; this release workflow does not change the Site backend or grant a tester access.
- The 15-agent crew is registered, but currently operationally quarantined. Package publication is not Lum independent-agent execution.
- No private asset archive, Drive IDs/tokens, secrets, signing keys, user conversations, emails or tester identities belong in public releases.
- Public forks follow the existing repository GPLv3; forking the GitHub code does not inherit owner app bindings, private Site access, trademarks or third-party artwork rights.
- GitHub `Latest` resolves a full Stable release, **not** the three parallel lanes. A live per-channel inventory is produced by `tools/pluginReleaseHub.py` and can be consumed by a future approved GitHub Pages download front end.

**Status:** SOURCE_CANDIDATE | DOWNLOAD_CHANNELS_PENDING_VERIFIED_PACKAGES | CROWN_STOP.
