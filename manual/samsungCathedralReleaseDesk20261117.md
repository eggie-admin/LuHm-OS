# LuHm-OS | Samsung Core → Blender Studio | Cathedral release desk

**Crown:** `STOP` until an owner-signed APK actually launches, is verified and survives same-signer update, and an independent public/ChatGPT host acceptance is recorded.
**Product:** LuHm-OS. **Publisher:** Eggie Bagelface. **Studio:** PIRATE DADDIES FILM. **World:** Project Premonition. GitHub `eggie-admin/LuHm-OS` `main` owns source truth.

## What this pass actually improves

- Existing bundled Android Web3 cockpit gains a **Samsung Core ↔ Blender Studio** touch-friendly panel in `frontEnd/index.html`, accessible from the top navigation and LuHm app menu; it is purely local UI, not a privileged command bridge.
- Existing canonical horned-L SVG from `publicationSite/logo.svg` and `plugins/luhm-os/assets/logo.svg` produces **four standard/adaptive APK icon files** in the isolated signed-build job, through `tools/samsungCathedralIcons.py`.
- Android's `export_presets.cfg` is only patched **within the guarded Actions build checkout**. The tracked `.testing` identity remains intact, and the owner beta uses `art.eggiebagelface.luhmos.beta`.
- Source audit independently checks the PNG byte signatures/dimensions, hashes, logo mirror, exact preset hooks, screen navigation code, source-only security boundaries, and rejection of duplicate icon-stage overwrite.
- The Blender connection is a **reviewed file interchange** (`.blend` → rights/texture/rig audit → GLB → Godot import), not a magical full desktop Blender service running inside the Samsung tablet.

## Existing machine layers, do not rebuild casually

**Samsung device:** Android 16 / SDK 36, ARM64, Godot 4.7.2, native `AndroidWeb3Cockpit` AAR + local offline HTML/jQuery WebView with typed allowlisted bridge.

**Ubuntu / Codespaces studio:** Ubuntu 26.04 environment with Blender and the previously CI-verified pinned Blendkit v3.21.5.261103 add-on. Existing personal Codespaces still needs a local verification. Asset-level rights are separate from the add-on install; no Fallout/Resident Evil/Blizzard donor game file is cleared for redistribution.

**ChatGPT / web:** Read-only LuHm plugin bridge and deployed Linux/Godot public candidates exist, but a source edit cannot register an MCP `ui://` app resource or install a private Android APK on the tablet.

## Reproduce the source audit (no secrets)

```bash
python3 tests/testSamsungCathedralStage.py
node --check frontEnd/samsungStudioSwitch.js
python3 tools/crownCathedralBrandAudit.py
python3 tests/testSignedBetaWorkflow.py
python3 tools/fdroidTabletSourceAudit.py
```

For an existing **Codespace** only, after reviewing any uncommitted work:

```bash
git pull --ff-only
python3 tools/blendkitSetup.py verify
```

Do **not** delete an existing Codespace or private art vault as an installation shortcut.

## The signer gate is intentionally hard

The repository's `doctrine/androidBetaReleaseBaselineV1.json` still has `status=UNVERIFIED`. That protects existing beta users from accidental key change. The owner must determine whether there was a previous **.beta** signer/version and record a real evidence reference or separately attest a genuine first beta.

On an owner-controlled authenticated machine, read only signing policy and secret **names** via:

```bash
bash tools/auditBetaSigningPolicy.sh
```

The protected GitHub environment `luhm-beta-signing` needs a required independent reviewer, no self-review, protected branch gate, existing PKCS#12 APK signer and pinned certificate fingerprint plus separate read-only policy token. Never paste private signing material in chat or put it in GitHub source. Do not generate a replacement keystore for an existing update lineage.

Only when those prerequisites are genuinely green, dispatch `samsung-lite-signed-beta.yml` on the **actual current main SHA** with an explicit owner `cast` input. It builds a **private** nondebug candidate, confirms package/ABI/SDK, signer SHA-256 and ZIP alignment, and stages an unsigned offline F-Droid repository draft. It does **not** publish a stable app.

The installer and Google Play signing chain, if later used, are distinct. The F-Droid repository index has its own key.

## GPG, TLS and APK certificates never collapse into one key

- **Owner Git GPG/OpenPGP:** verify owner-held public fingerprint, GitHub account binding and a genuinely owner-signed commit/tag. A GitHub API commit from a bot is not proof of the owner's OpenPGP key.
- **Android APK signing:** verify the exact built APK certificate and SHA-256 with `apksigner`, then same package/signature and increasing `versionCode` during an actual update.
- **HTTPS/TLS:** check serving hostname, trusted chain, expiration and **real issuer** at the actual public deployment. Render/Cloudflare-managed certificates may not be Let's Encrypt; a green HTTPS URL alone does not satisfy a strict issuer policy.

## Physical SM-X400 proof before Crown

Only use a user-authorized device and intended exact `.beta` APK. Confirm: first launch, system launcher glyph, original brand, portrait/landscape and touch, WebView local asset load, Godot game scene, the Studio switch, safe-area/cutout, suspend/resume, no unexpected network or private file disclosure. Then perform an in-place update with the **same signing certificate** and higher versionCode. No uninstall/clear data workaround.

Record package name, APK SHA-256, signer fingerprint, version, exact GitHub source commit/run ID and physical device evidence. **Do not** mark a source-only CI job as phone-tested.

## Promotion ledger

| Gate | Truth from source review |
| --- | --- |
| Canon naming/logo | Existing authoritative logo, derived raster source staged for CI |
| Samsung ↔ Blender switch | Local cockpit source implemented, physical touch unverified |
| Build integration | Existing Android/Gradle/Godot pipeline, icon hooks in signed candidate workflow |
| APK signed with owner key | Not proven, blocked by unverified baseline and environment |
| GPG owner signing | Not verified |
| SSL issuer and domain | Not independently live-proven |
| ChatGPT inline MCP/CAST | Existing read-only bridge only; no new host resource deployed |
| Public F-Droid/store | Not published |
| Professor final Crown | STOP |

This document records the maximum bounded source improvement without falsifying keys, builds, device observation, or public release.
