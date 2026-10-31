---
name: project-hydra-release
description: Use for Project Hydra plugin launch, cockpit recovery, Godot handoff, pets, and release checks. Preserve existing Site App binding, distinguish in-chat studio from playable Web Godot, and verify current GitHub/Render source.
---

# Project Hydra cockpit recovery and release

## First, use the connected personal plugin

Use the existing Site-backed personal **Project Hydra** plugin. Its identity and installed Site App binding must be preserved. When a Professor message requests the cockpit, invoke available `luhmConnectionStatus`, then prefer `luhm_open_mobile_cockpit` for Samsung, Android, tablet or phone requests; use `luhm_open_cockpit` for the full studio. Do not propose reinstallation or merely echo JSON. Read the actual returned resource URI instead of assuming the desktop URI. If the mobile card appears, offer its user-clicked Send in-chat mount test once. Record a missing card as unverified and investigate the existing Site binding; do not repeatedly relaunch it. The source contract's `SOURCE_CONFIGURED_CANDIDATE` status does not deny that a live tool was invoked, but neither status alone proves mobile device rendering.

## Separate 3D play surface and fail-safe route

The MCP cockpit at `https://luhm-os-harness-green.onrender.com/harness/` and the built Godot Web player at `https://luhm-os-godot-harness-green.onrender.com/harness/godot-export/index.html` are two DIFFERENT Render services. The MCP service does not build the Godot assets. If the MCP web page says `LOCAL EXPORT PENDING`, that is a same-origin WebAssembly/PCK integrity result, not proof the independent Godot server failed. The cockpit includes a user-initiated separate-service 3D link as of GitHub PR #353. Open the dedicated Godot URL when a player is requested; do not invent a playable in-chat `luhm_open_godot_player` Site tool if it is not connected. Never bypass SHA256 gates or silently iframe an unverified cross-origin runtime.

## Reconcile exact current deployment

For each deployment claim recheck `eggie-admin/LuHm-OS` main, exact SHA CI, Render service deploy status AND SHA. Historical reference: cockpit handoff merged in PR #353 at `870661cecc3ac68701ad2e1301b4f1e0a6300f98` on 2026-10-21; recheck future turns. Keep source present, CI passed, merged, hosted live, plugin installed, host tool invoked, and device tested distinct. Site private plugin release version and repository package version are separate identities; updating a personal plugin skill cannot edit its Site frontend or force third-party runtime auto-sync.

## Update behavior and boundaries

When Professor authorizes an update, inspect the current personal plugin release, alter only warranted skill/manifest files with `Plugin_Creator.update_plugin` and the observed current-release id, preserve omitted files/assets/App binding and keep the plugin private. Update Render only against validated current main when permitted, not simply because a GitHub workflow succeeded. Never claim unattended self-updates without an independently scheduled workflow and supported privileges. Do not grant external invites, publication, paid access, secret exposure or autonomous agents. Lum coordinates; Urd checks evidence; Belldandy records it; Skuld verifies compatibility; Yume handles art. The in-chat goddess cast is a supervised conversational presentation, while independent backend workers remain quarantined. Professor retains human publication and promotion authority.

## Samsung and F-Droid handoff

Treat ChatGPT's in-chat cockpit and the standalone Android beta as separate installations. F-Droid cannot install the ChatGPT plugin. Do not require Termux, root, a replacement launcher, or router changes for the beta route. Treat informal device names such as Samsung Light LS as unverified; the current repository targets SM-X400, and confirm model/Android version only when artifact compatibility depends on it.

For an easy-install request, inspect the current main SHA, latest `samsung-lite-owner-signed-beta` run, its failed step or verified artifact, and `doctrine/samsungTabletInstallV1.json`. Prefer existing valid artifacts. If signing inputs are absent, report the missing secret names only; never collect key material in chat or rerun the same blocked build. Inspect pending signing hardening before recommending a workflow dispatch; a source-only preflight does not attest protected environment configuration.

Give an Add repository link or QR only after verifying the actual HTTPS repository URL, independent index-signing fingerprint, signed index and matching release APK. A staged folder, successful debug build or plugin version bump is not install availability. Keep owner-controlled signer provisioning separate from ordinary source repairs. Continue reversible preparation without asking again, then report one concrete remaining blocker and the smallest device action. Never promise the offline beta includes remote ChatGPT or cloud AI integration.
