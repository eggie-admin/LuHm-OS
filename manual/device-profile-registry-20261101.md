# LuHm-OS | Device-aware registry and quiet studio workflow
**Status:** proposed source-only. Parent machine/npm PR #478, itself stacked on Debian PR #477. No protected-main merge, store submission, actual device performance claim, network server, agent release or firmware write.

## 4×4 namespaced registry: no pretend kernel addresses

`doctrine/deviceCapabilityRegistryV1.json` defines **deviceCapability:0x00..0x0F**, scoped to **Android / Samsung / iOS / web+Linux** × **runtime / graphics / storage / distribution**. These are logical lookup keys, distinct from other 4×4 audit namespaces, physical addresses, cache lines, PCI identifiers, firmware values, Windows Registry, Android Settings providers and signed vendor certificate identities. No host registry is written.

| Device | ABI/runtime boundary | Render | Delivery |
| --- | --- | --- | --- |
| Android | Godot ARM64; SDK 36 target configured in current `export_presets.cfg` | GLES/WebGL baseline, Vulkan if observed | Play Internal App Sharing for first install, later appropriately signed AAB |
| Samsung | Android same core ABI plus opt-in Galaxy SDK functionality | Samsung RTL physical test; thermal and driver capability | Separate Galaxy Store Seller Portal authority |
| iPhone/iPad | iOS sandbox; native requires actual macOS/Xcode | WebKit/Safari browser fallback, Metal only in native app | Apple signing and TestFlight authorization |
| Linux/browser | Debian host retains distro kernel, browser is unprivileged | DOM/SVG first → optional Babylon WebGL → remote Unreal separate | HTTPS/CDN only after asset/privacy and owner review |

**Upstream check as of Nov 1, 2026:** Google Play ordinary handset new apps/updates require target API 36 from Aug 31, 2026. Native Android packages need 16 KiB ELF and ZIP alignment compatibility: inspect *the produced APK/AAB* using `zipalign -c -P 16`, `bundletool dump config` and real runtime tests. Android’s own guidance notes that **AGP 8.5.1+ and NDK r28+** help, but do not cure incompatible prebuilt native libraries. Existing `androidWeb3Plugin/build.gradle.kts` pins AGP 8.13.2; review in its own compatibility PR rather than blindly moving to the newest major. `arm64-v8a` in Godot export is a declared target, not installed app evidence. Sources:
- https://developer.android.com/google/play/requirements/target-sdk
- https://developer.android.com/guide/practices/page-sizes
- https://developer.android.com/studio/releases
- https://developer.samsung.com/remote-test-lab
- https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases

## One packet contract: Node ↔ Python 3 ↔ SQLite STRICT
Fields: `schema, registryHex, kind, byteCount, payloadBase64, sha256, rssBytes, rightsState`.

- JSON schema/value checks first; reject unknown keys, malformed Base64, noncanonical encoding, UTF-8 errors, >4 KiB raw payload, altered declared byte count, forged or malformed SHA-256 digest and out-of-range integer RSS.
- `rssBytes` means **resident set size measured in bytes**. Null indicates unknown. The reproducible CI example uses **8,388,608 bytes as a synthetic value**, not a real tablet RAM observation. No RSS-feed parser is included.
- `rightsState=LOCAL_DRAFT` prohibits interpreting this packet as a public-media license. Never place real credentials, private media, customer content or full original art in public source CI.
- SQL parity uses a **temporary in-memory STRICT SQLite** table, no migrations/server/DB file. Git commit SHA and payload SHA-256 remain distinct.
- The hexadecimal registry is namespaced and checked for a contiguous 4×4 mapping. It is not a register write, tuning knob, signature or permission.

To exercise (from repo root, Node 24+/26 and Python 3 with SQLite STRICT available):

```sh
cd tools/luhm-machine-agent
npm test
node bin/luhm-machine-audit.mjs audit --with-python --with-device
```

`--with-device` sends a fixed **synthetic** Unicode note through strict JavaScript Base64/SHA, Python UTF-8/SHA, and SQLite integers. It never probes a physical handset, invokes a model, accesses the network or writes to protected machine areas.

## Minimal GUI that learns only what is selected in this session

`tools/luhm-machine-agent/demo/index.html` is a non-privileged responsive DOM/SVG session-only task index, not a shipped native app or a live playable game. Initial curated order: **Play First Night → Edit Scene → Review Assets → Build & Test → Inspect Evidence → Settings**.

A button selection increments only an **in-memory** integer; frequently selected tasks move up, ties retain the curated order. The **Reset order** control clears the counts. Closing/reloading the tab resets them too. No analytics, localStorage, cookies, hidden sessions, user-profile syncing, private media inspection or automated task dispatch. Source links explicitly lead to **draft review**, never mislabel themselves as one-tap Play Store installation.

`tools/luhm-machine-agent/src/workflow-rank.mjs` is a single browser-and-Node sorting implementation with zero vendors; no duplicate jQuery or Vue application is needed for this small page. The existing progressive Babylon kiosk #476 and playable First Night #475 remain separately reviewable projects.

## Platform hardening and vendor-game update discipline

Each proprietary platform gets a **small opt-in adapter**, never a universal firmware patch. Version-controlled update policy: `source notice → exact SDK/ABI/license → isolate optional adapter → static/security tests → native 16 KiB/signature checks → physical Samsung/iOS/browser check → staged private build → human approval`. The owner must authorize signing keys, privacy declarations, store identities, paid APIs and publication.

Android protected app components, SELinux/AVB/Knox, iOS sandbox/signing, Git branch protections, and vendor license restrictions are not overridden by this source contract. Game assets, proprietary engines/mods, vendor SDKs and licenses cannot be copied into an Apache-oriented public core without permission.

### Escalation/finish criteria

**0:** 4×4 source registry + byte/hash/SQL pass. **2×2:** device-profile selection based on observed ABI/page size and browser feature tests. **4×4:** Godot+web studio input/asset rendering, actual frame-time p95/RSS. **8×8:** remote backend adapter with authentication, cost and rights receipts. **16×16:** releases and updates per platform, requiring authorized signing and install/rollback proofs.

**Current finish line:** draft-source contract and CI tests only. Runtime/installer proof still outstanding. **CROWN STOP**.
