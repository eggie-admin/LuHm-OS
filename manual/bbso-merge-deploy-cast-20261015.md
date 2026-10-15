# BBSO | LuHm-OS Merge / Deploy / CAST Sign-Off Packet

**Packet:** `bbso-luhm-artist-studio-20261015`  
**Authority:** Professor, explicit "MERGE DEPLOY CAST FINAL FORM" and BBSO packet request.  
**Scope:** artist-first ChatGPT studio source; bounded existing Render harness refresh; public F-Droid **preparation only**.  
**Crown:** human creative director controls original masters, promotion, production credentials, and final public releases.

## 100. Source of truth and artistic purpose

**LuHm-OS exists to make art.** The ChatGPT MCP Apps cockpit is the artist's in-chat desk, not a developer dashboard. Yume assists the human artist, rather than replacing or approving original artwork, music, animation, composition, or source masters. Android and Godot are creative output and interactive surfaces. GitHub is the remote garage; FFmpeg and Codespaces are production instruments; Google Drive holds binary masters. Do not confuse infrastructure completion with a working visual editor.

The current slice adds a locally editable seven-shot *Into the Warp* **storyboard draft** inside the existing `luhm_open_cockpit` MCP widget. Undo/Redo, shot selection, timing, direction and explicit JSON export are candidate source features; browser host behavior and saving editable GIMP/Blender masters are **not** proved by source CI.

## 200. Immutable narrative and art locks

- Sealed **Into the Warp** screenplay is not mutated by the studio widget.
- Seven render/story slots: `100, 200, 300, 401, 402, 403, 500`. Sections `100 / 200 / 300 / 400 / 500`, with three shots in section 400.
- **Belldandy reads Anti-Daddy's DADDY Codex lore at Shot 401, Movement II.** Big Daddy interrupts; Shot 500 revisits the *same* archive for a root-access stinger, not another lore lookup.
- Preserve one Big Daddy across inventor / Old Guard / Berserker / Witching Hour. Lum physically follows; four lab screens stay geographically fixed. Audio remains deferred.
- Human-authored original sprites, film, music and editable art files remain protected and require individual approval before public export.

## 300. Repository reconciliation

- Repository: `eggie-admin/LuHm-OS`.
- Base at packet creation: `8b507584cdebd9b91ca6ab4c56b478a63a47833a`.
- PR: **#288** (`candidate/artist-first-canon-120-reconcile-20261015`), artist-first ChatGPT widget + separate F-Droid delivery lane.
- Previous source run `38806421830` is RED due to **Belldandy Housekeeping 50-commit ancestral checkpoint ceiling**, even though the other **41/42** checks passed on `8af89a045006816f03c227781e213d8128ae638b`.
- **Protective checkpoint created with Professor authorization:** `snapshot/belldandy-manual-20261015-8b507584` points to exact base `8b507584cdebd9b91ca6ab4c56b478a63a47833a`.
- Belldandy operational quarantine stays in force. Snapshot is protective, **does not release the agent** and does not grant merge authority by itself.
- **Re-run ALL exact-head CI after this packet commit.** The new nearest-ancestor checkpoint should make the actual count verifiable. Do not mark GREEN by arithmetic prediction; use `tools/belldandyCheckpointWindow.py` and GitHub's own workflow result.
- Source audit at prior head: 120 named controls, **102 source PASS / 3 editor GAP / 15 runtime UNVERIFIED**. New head requires fresh run.

### Merge gate

Only merge when the current head, branch-base ancestry, critical checks, and housekeeping all pass. Preserve exact SHA in the merge request. Prefer squash to keep reviewable one-change-group source history. No blanket "FINAL FORM GREEN" may be inferred from a source merge.

## 400. Existing remote service deploy

- **Existing** service: Render `luhm-os-harness-green`, service `srv-daubsi1srm7s73bl5lh0`; **auto-deploy OFF**.
- Previously provider-reported LIVE deploy: `dep-db8h6iu7bikc73e46qp0` for source `697e6690ee98b2dad2aea62a2de63b2710db136a`.
- If and only if #288 merges with exact-head checks, trigger **one** existing service deployment from new `main`; do not create a duplicate Render instance, public media processor, or backend.
- Independently verify provider's deployed SHA, LIVE status, HTTPS `/mcp` initialization and the mounted `ui://luhm-os/cockpit-v2.html` resource. Provider LIVE alone cannot establish ChatGPT host install, a clickable widget, or end-user operation.
- Rollback candidate is the previously live Render source/ref above. Rollback is deliberate and evidenced, not automatic.

## 500. Android public F-Droid update lane: distinct, not published

- `art.eggiebagelface.*` is an **Android package namespace**, not a DNS address. User also dictated `art.egguebagelface.*`; treat that alternative spelling as unconfirmed.
- Proposed public repository URI: `https://art.eggiebagelface.art/fdroid/repo/`. The *hostname, DNS, HTTPS, signed index and actual client update route* remain unverified.
- Existing `.testing` and `.beta` APK packages **cannot** substitute for a stable public release.
- Requires independently protected Android release signer, separately protected F-Droid index signing identity, exact APK checksum and version, install/upgrade proof, signed repository index, F-Droid client acceptance, and Professor publication.
- Never claim official F-Droid catalog inclusion when only a custom F-Droid-compatible repo is proposed. Never place key bytes in GitHub, prompts, Render or a public ZIP.
- The remote F-Droid APK update channel is **not** the ChatGPT plugin's MCP/asset update channel.

## 600. Media and Drive privacy

- Original masters and sealed screenplay must remain in the owner-only LuHm Audit Vault.
- Previously detected **anyone-with-link reader** on the main media tree remains RED. Do not archive private art there until access is restricted and reverified.
- Synthetic FFmpeg MP4 proof is a test fixture, not the rendered pilot, an authorized commercial music file, or public publication evidence.

## 700. CAST acceptance

**Scope that may be promoted after proof:** GitHub artist studio source + backward-compatible MCP resource on the **existing** Render service, with an exact-SHA deployment and independent smoke receipt.

**Separately blocked until their own proofs:** installed and usable ChatGPT widget, production paint/motion timeline, persistent FFmpeg worker, actual *Into the Warp* render, Samsung installed app, F-Droid public signed index, approved licenses, public website/DNS and any Facebook output.

**BBSO sign-off outcomes**
- `SOURCE_MERGE`: pending fresh exact-head all-green checks
- `RENDER_DEPLOY`: pending merged `main`, provider LIVE and HTTP/MCP smoke receipts
- `APP_HOST`: unverified
- `FDROID_PUBLIC_RELEASE`: STOP
- `ARTWORK_PUBLICATION`: STOP
- `GLOBAL_FINAL_FORM_GREEN`: STOP

Nothing in this sign-off document itself auto-merges, deploys, signs or publishes.
