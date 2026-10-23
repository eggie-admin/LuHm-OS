---
name: android-beta-readiness
description: Use when the user asks about LuHm OS Android beta builds, Samsung install readiness, APK or F-Droid signing, or release evidence.
---

# LuHm Android beta readiness

Use the connected LuHm OS MCP tools as read-only evidence. The remote server exposes luhm_status, luhm_samsung_spine_contract, luhm_proof_contract, luhm_transport_contract, luhm_validate_scope, and other read-only status and cockpit tools. Never describe this plugin as an installer or signer.

## Check order

1. Call luhm_status and luhm_samsung_spine_contract for the current service report. Treat their timestamps, source refs, and limits exactly as returned.
2. Resolve the current canonical main SHA from eggie-admin/LuHm-OS. Read doctrine/currentSourceTruthV3.json, doctrine/androidDeliveryLanesV1.json, doctrine/samsungTabletInstallV1.json, doctrine/publicApkUpdateIdentityV1.json, and any exact build receipt referenced by current source truth.
3. Compare each artifact receipt against its exact source SHA. A historical build, CI receipt, or package hash is not proof that the same artifact is currently available or installed.
4. For an owner-signed beta APK, verify package ID art.eggiebagelface.luhmos.beta, target SDK, ABI, non-debug/release flags, APK SHA-256, app signer certificate SHA-256, and exact source/run receipt. Never request or expose signing-key values.
5. For public F-Droid installation, separately verify the public repository HTTPS route and a signed repository index against its pinned index-certificate fingerprint. The repository index signing key is distinct from the Android app signing key. A successful APK signature does not prove the repository index or public install path.
6. Mark physical install, first launch, and same-signer upgrade as pending until a current Samsung device receipt proves each one. Do not clear app data or infer an upgrade from a first install.

## Boundaries

- This MCP server is read-only. Do not claim that it builds, signs, installs, uploads, publishes, changes DNS, or controls a device.
- A green GitHub build does not prove a physical device install or a public repository index.
- Treat missing, stale, mismatched, or unsigned evidence as PENDING or UNVERIFIED; stop before installation.
- Keep public F-Droid index signing, Android APK app signing, GitHub commit signatures, and CI provenance as distinct proofs.
- The public repository is not ready until the exact APK, index signature, HTTPS route, pinned fingerprint, and install/upgrade evidence all match the current reviewed release.
