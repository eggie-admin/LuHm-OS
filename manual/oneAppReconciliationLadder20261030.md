# LuHm-OS old Magic to one-app reconciliation ladder | 2026-10-30

**Lane:** existing draft PR #461 only. **Main:** `f0cb6ee54066b490c0e80efc2c96200fec76ee2d`. **Crown:** STOP. No physical kiosk, firmware, Android, cloud runtime, live database, signed APK, or ChatGPT host install is proven by this source pass. This extends the existing 2x2 / 4x4 proposed orchestration rather than creating another authority system.

## Compatibility order: legacy → supported stable → optional bleeding edge

| Layer | Reuse source | Retain/replace/reduce | Acceptance gate |
|---|---|---|---|
| L00: old Magic | `agents/professorOldMagicStudy/SKILL.md`, `doctrine/magicEscalationProfileV1.json` | Retain as task-bound teaching/diagnostic mode, **not authorization** | exact-source evidence |
| L01: Debian and kiosk | `doctrine/chromeCanaryKioskMilestonesV1.json`, host recovery ladder from draft PR #460 | Retain working kiosk, inventory actual OS; Debian 13 Trixie is stable upstream, NOT proof the Pi/host has that OS; use rollback-first major-version migration | boot/recovery/keyboard/touch proof |
| L02: kernel/hardware | Android OEM, Pi board, Pico firmware, USB Host, BlueZ, UVC/V4L2, ALSA/PipeWire | Prefer stock OS upstream drivers; isolate model-specific vendor blobs | physical enumeration and restart/permissions |
| L03: system services | Debian APT/dpkg, `systemd`, host Python, SQLite JSON1 | Do not make npm own apt/kernel/firmware; one network owner, one service supervisor | offline restart and DB transaction/restore |
| L04: transport/data | `tools/archiveIntake.py`, `tools/fnCastSqlJson.py`, **`tools/oneAppExchange.py`** | RSS/Atom local XML -> typed JSON -> Base64url bounded envelope -> SHA-256 integrity; never treat encoding/hash as auth; source-owned artifact receipts | malformed, oversized, DTD, traversal and tamper tests |
| L05: ZIP/7z/JAR | `tools/archiveIntake.py` and safe ZIP reader | ZIP/JAR inspect only, no JAR execution; 7z magic inspection stays blocked until explicitly pinned safe Python reader/extractor and sandbox evidence; never install extractor implicitly | source, rights, bomb, symlink/absolute-path negative tests |
| L06: API/backend | `host/api/luhmApiSpine.py`, service/MCP contracts | Python 3 control plane; Flask **optional** if there is an actual HTTP adapter requiring it. Flask built-in dev server is never a production runtime; use approved WSGI + reverse-proxy config | schema, auth, rate/size, disconnect tests |
| L07: frontend | `frontEnd/package.json`, local jQuery 3.7.1 | npm ci --ignore-scripts on inspected lockfile; keep local assets. Bootstrap is an **optional pinned npm CSS/UI dependency** only after UX and size measurement; no runtime CDN dependency | offline local kiosk 320/390/960 + real Samsung touch |
| L08: Java/Android | `androidWeb3Plugin`, Gradle/SDK and existing exact-CAST Android workflows | JAR is library/container format, Gradle builds APK/AAB; npm builds browser assets, not Android installer. Preserve package ID/owner cert. | Gradle/ABI/signature + physical install/upgrade |
| L09: creative studio | Blender, Godot, FFmpeg, editable source/art metadata | Desktop/remote render workers behind permissioned APIs, not bundled in Android APK | import/edit/render/export with file rights |
| L10: ChatGPT files | ChatGPT Project files, Drive evidence archive, GitHub canonical source | ChatGPT **file-first coordination**: inspect and stage private data via scoped file links, produce sanitized manifest/hashes, request permission before Drive/share changes. Never move private art into public repo or infer device mount. | actual app/file visibility and user acknowledgment |
| L11: Base44 | optional `Base44` third-party AI app builder | It is **not an encoding** and must not silently become canonical backend. Research as detachable prototype/adapter; GitHub sync, portability, billing, terms and private-data policy need owner proof. `Base64url` is the encoding. | export/rebuild offline and account consent |
| L12: one app | one branded LuHm interface spanning web/mobile/kiosk | One **user-facing shell** and one versioned capability/API spine, multiple **bounded** APT/npm/Python/SQL/Gradle/media runtimes. Do not deploy all tools into one process or Android APK. | actual daily workflow end to end |
| L13: distribution | existing CAST bridge and release gates | Separate proposed / beta / public. No signing, publish, merge or distro upgrade on document-only evidence. | independent exact-source artifacts + Crown |

## Top-down reconciliation

1. Begin at **one user journey**: Samsung/desktop opens the LuHm shell, accepts a selected *local* RSS, ZIP, or JAR, previews a JSON file manifest, stages approved studio work, saves a private receipt, and exports a reproducible preview.
2. Bind the typed envelope to `sourceRef`, hash, MIME, payload budget, rights, and capability; avoid double serialization into Base64 for large media blobs. Assets should stay as files with hash references.
3. Keep *file import*, *source authority*, *service compute*, *Android packaging*, and *publication authorization* distinct. Only the UI is one app.
4. Reuse existing source in PR #460 for portable npm package manager and machine layer, but reconcile commits by exact-file diff rather than blind merge. PR #461 owns the cross-lane integration and new file contract tests only.
5. Deduplicate only after evidence: keep/replace/remove/investigate matrix by actual import graph, lockfile, license, vendor runtime behavior, size and rollback. No mass deletion of similar GitHub workflows.
6. Link new `tests/testOneAppExchange.py` to **existing** `.github/workflows/feature-mutation-architecture-gate.yml`, rather than adding another standalone workflow. Its current CI run must report success on **the latest exact head**.

## 2x2 → 4x4 → 8x8 → 16x16 evidence reduction

- **2×2:** local/remote × hardware/software, no unknowns silently pass.
- **4×4:** inventory/harden/test/promote × hardware/kernel/services/studio, 16 evidence cells.
- **8×8:** expand only failures by device/toolchain, privacy boundary, exact version, interface, tests, provenance, rollback and user acceptance. This is a prioritization grid, not 64 required agents.
- **16×16:** optional regression index for actual platform+dependency surfaces, deduplicated by `sourceRef+control+target`; no 256 blind mutations, and certainly no shell/paid execution in parallel.
- **Snapshot after each:** `observedAt`, `sourceRef`, command, result (`VERIFIED/FAILED/BLOCKED/UNTESTED`), evidence link, SHA256, next safe action, Crown=STOP.

## Full automation ownership

- Existing daily **Vendor Hardening Audit**: read-only/source-draft fixes; pursue failing exact-head tests; escalate only genuinely blocked prerequisites. Existing conditional **Premonition Release Watch** remains read-only release observer.
- GitHub CI: source/test receipt only, no device runtime inference. Keep package install scripts off by default; no background ChatGPT session execution promised.
- Remote AI: mock adapters first; provider entitlements, API billing, actor IAM and user consent independently verified. ChatGPT file processing is scoped and does not constitute provider token entitlement.
- Hard stop at host migration, signing, Android OTA, Pi EEPROM, Flash, pairing, network apply, privileged shell, public art publishing or paid account creation.

## Immediate evidence

- 11 local Python contract/negative tests of the new adapter passed in the 2026-10-30 task workspace, with a *representative local subset* of the repo ZIP intake helper; exact repository full integration test is CI-dependent.
- New Python adapter and test files are in PR #461 source only. Existing workflow updated to exercise tests. The local .7z signature fixture is intentionally not a valid archive and demonstrates **fail-closed** behavior, not successful Python 7z decoding.
- A file digest checks integrity; it does NOT authenticate publisher or replace signed artifacts. A local source snapshot does NOT imply user-host backup.

## Official upstream

- Debian stable: https://www.debian.org/releases/stable/
- Python XML security: https://docs.python.org/3/library/xml.html
- Python ZIP/JAR-compatible format: https://docs.python.org/3/library/zipfile.html
- 7z / py7zr: https://py7zr.readthedocs.io/en/latest/user_guide.html
- Flask deployment: https://flask.palletsprojects.com/en/stable/deploying/
- Bootstrap npm/install: https://getbootstrap.com/docs/5.3/getting-started/download/
- Android Gradle: https://developer.android.com/build
- Base44: https://base44.com/developers
