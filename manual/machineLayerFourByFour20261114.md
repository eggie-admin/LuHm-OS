# LuHm-OS Machine Layer: source snapshot and 4 × 4 escalation (2026-11-14)

This is a **reviewable source candidate**, not a runtime release or full-green seal. GitHub main commit at the audit was `a6e3ce843d099361a8696eab68869dcf367c4f26`. Draft creator work is in PR #547; draft Control Room work is in PR #546. Do not merge one and silently attribute its proof to another.

## Exact checks observed

- LuHm-OS bridge: connection-status tool reported **reachable**, tools read-only. An actual attempt to invoke `luhm_open_cockpit` returned **unavailable**. No automatic @-mention widget host routing was proven.
- Render: one candidate workspace shown as **GitHub Workspace**, but session workspace **not selected**. Provider tools require Professor to confirm the target workspace before live service/DB/cron changes. No live PostgreSQL query, migration, deployment, or cron run took place.
- Company-wide source hold: `doctrine/companyWideOperationalQuarantineV1.json` forbids active agent work routes. 15 registered agent identities are not 15 running LLM workers.
- Current Godot `project.godot` has GL Compatibility. No Vulkan or NVIDIA runtime probe on an actual device took place.
- No firmware was extracted, reflashed, incorporated into a custom kernel, or claimed owned.

## One consistent architecture

**Four composition layers:**

0. `coreLibrary`: source SHA, naming, SQL typed lanes, event identity, cryptographic packet checks.
1. `pluginExtension`: Godot 4, SQLite/Postgres reviewed adapters, libgphoto2/CUPS/Wacom interfaces, Blender Python adapter.
2. `classWidgetOrganization`: Lum boss cockpit, characters, inventory, cutscenes, dialogue, 4×4 status board.
3. `stubAdapterBoundary`: provider-safe MCP site, Android WebView, local Godot world bridge and explicit private SQL transport.

**Four escalation tiers:** `readOnlyProbe` (0); `localCandidate` (1); `supervisedExternal` (2); `professorPromotion` (3). Cross with four lanes `deviceInterface`, `graphicsRuntime`, `dataTransport`, `orchestraStudio`: **16 independently auditable cells**. Each cell records status and authority; no FULL_GREEN follows from a missing receipt.

## Local SQL is real source, not a remote database claim

Reuse `host/api/typedLanesV1.sql`, `tools/typedSqlStub.py`, and the current typed-source ledger. `tools/machineLayerSql.py` seeds exactly 16 scoped immutable `streamEvent` rows with typed `textStream` and `booleanStream` fields. It outputs authenticated JSON packets and validates their HMAC on read-back. A packet is an exchange artifact, not authorization to merge/publish or connect to any network. The sync key must come from a private environment variable, never GitHub. In a local workstation:

```sh
python3 tools/machineLayerSql.py validate
python3 tools/machineLayerSql.py seed --db /tmp/luhm-machine.sqlite
python3 tools/machineLayerSql.py status --db /tmp/luhm-machine.sqlite
# Supply LUHM_SQL_SYNC_KEY securely from local secret management (>=32 chars).
python3 tools/machineLayerSql.py tx --db /tmp/luhm-machine.sqlite --output /tmp/luhm-tx.json
python3 tools/machineLayerSql.py rx --db /tmp/luhm-receiver.sqlite --input /tmp/luhm-tx.json
```

`host/api/machineSqlRemote.py` implements a **disabled-by-default PostgreSQL adapter** using parameterized INSERT and same-transaction SELECT verification of exactly those 16 public machine-state records. It requires `LUHM_REMOTE_SQL_SYNC=scopedSourceTxRx`, a private `LUHM_DATABASE_URL` with `sslmode=verify-full` and CA trust, an authorized least-privilege DB role, and a separately applied/baseline-reviewed `host/api/typedPostgresReviewV1.sql`. No remote DDL; no generic SQL execution, open ports or secret logging.

The desired Render Cron candidate is recorded in `doctrine/machineSqlCronCandidateV1.json` at 30-minute intervals, **not created or running**. Before any activation: select workspace, verify existing DB and pricing, take backups, prove TLS and DB grants, apply scoped migration with separate authority, confirm exact SHA, run one manual TX/RX and read-back, then authorize the scheduled job. A cron schedule alone is not transmission proof. The current profile's no-unapproved-paid-services rule remains in force.

## Device and firmware path: software before hardware

Never gather arbitrary firmware into a universal kernel. No device-specific model numbers, USB IDs, signed vendor packages, kernel KMI, licensing or physical smoke receipts have been verified for the requested Epson, Canon, Nikon, Wacom, wireless keyboards, displays, Raspberry Pi or NVIDIA board. Samsung SM-S721U1 is present in current app environment metadata; SM-X400 is a repository Android test target, not a physical-device receipt.

Read-only `tools/machineHardwareProbe.py` reports only host OS architecture and **presence** of diagnostic commands. It deliberately does not execute `fwupdmgr`, `mokutil`, `vulkaninfo`, `lsusb`, `lspci`, `adb`, `nvidia-smi`, `gphoto2` or `scanimage`; does not record MAC addresses, camera serials, Android device IDs, and cannot manipulate kernel or firmware. Hardware-backed keys should use platform keystores/TPM where verified, never hardcoded hex permission flags. Obtain explicit device identities and grant scopes before the advanced probe.

- Canon/Nikon **cameras**: prefer libgphoto2/PTP, after model-specific proof.
- Epson/Canon **printers**: CUPS driverless IPP first, followed by licensed vendor adapter if required.
- Epson/Canon **scanners**: SANE/eSCL when compatible.
- Wacom: in-kernel input driver, LinuxWacom/libinput; validate pressure and tablet IDs.
- Keyboards, webcams, LCD/monitors: kernel HID/UVC/DRM/KMS/EDID support first, not vendor firmware repack.
- Samsung Android: preserve Android GKI/vendor modules and ordinary app permissions. Do **not** replace phone kernel with generic Ubuntu kernel.
- Desktop Linux: OEM/distribution-supported kernel and signed, provenance-checked firmware packages; secure boot/lockdown/TPM only after model-specific inspection. Keep update and rollback records.

Official reference entrypoints: Linux kernel firmware request docs https://www.kernel.org/doc/html/latest/driver-api/firmware/request_firmware.html ; libgphoto2 https://github.com/gphoto/libgphoto2 ; LinuxWacom https://linuxwacom.github.io/ ; OpenPrinting https://openprinting.github.io/cups/drivers.html ; SANE https://www.sane-project.org/sane-backends.html .

## GPU / Valve / creative backend

Prefer **NVIDIA Vulkan Forward+** for a tested Linux desktop workstation, **Vulkan Mobile** on certified Android GPUs, **Direct3D 12** on capable Windows machines, **Metal** on supported Apple systems; keep OpenGL Compatibility/WebGL 2 for web and lower-end fallback. This is an explicit multi-backend configuration, **not** a hardcoded Vulkan-only switch. Godot docs: https://docs.godotengine.org/en/4.7/engine_details/architecture/internal_rendering_architecture.html .

Valve Source SDK 2013 is a non-commercial-mod SDK with license restrictions, not the copyright-free Source 2 engine or a general commercial Godot dependency: https://github.com/ValveSoftware/source-sdk-2013 . Use architectural references for level/trigger tools, never bundled Valve engine code or game data. No custom GPU driver, unlicensed firmware redistribution or Source SDK runtime fork is in this candidate.

`host/blender/luHmShotStage.py` is an optional **original scene generator** run by Blender's own Python interpreter. It accepts a rights-gated LuHm-OS Creator Studio JSON manuscript and creates only procedural boxes, camera and light in a new `.blend` file; no file overwrite, no vendor assets, no network execution, no claiming finished cutscenes.

## Agent and ChatGPT widget boundary

`plugins/luhm-os/plugin.json` now proposes Lum's Canon cockpit as the leading default prompt. `doctrine/luhmPluginDefaultBoss20261114V1.json` records the requested behavior. This **does not guarantee** ChatGPT opens the app on every mention; ChatGPT decides tool choice/host presentation. Installed plugin versions and separate Site service require deployment and host proof. The named Lum, Urd, Belldandy, Skuld, Yume and Oni cabinet remains source-registered, not autonomous, per quarantine.

## CAST gate

`sanityCheck → audit → ingest → mutation → test → apply → continue → deploy`.

Source can reach candidate **tested** while remote SQL, cron, plugin host popup, GPU, physical Samsung, exact hardware/firmware, Blender runtime, source merge and public release stay **STOP**. A general “full Professor approval” does not replace the repository's exact single-use taskId + sourceRef + buildScope + human review, rollback and independent CI evidence. Stage-by-stage migration to production remains a separate operation.
