# LuHm-OS Machine-to-AI Audit · private npm workspace

**State:** source-only local deterministic auditor, 4×4 canon overlay, ZERO production npm dependencies. Not an LLM, offline model, plugin installation, runtime agent, daemon or remote deployer. This is a safe **audit/control-plane skeleton** that can be integrated with an approved AI provider later.

## One command, four read-only actions

```sh
cd tools/luhm-machine-agent
npm test
npm run audit
node bin/luhm-machine-audit.mjs audit --with-python
node bin/luhm-machine-audit.mjs plan --task "Review First Night browser WebGL source"
npm run remote-plan
```

Node.js **24 LTS or 26 LTS** (package requires Node >=24), Python 3 with `sqlite3` for the optional source-only bridge. No `npm install` is needed to run the package source. The package is **private:true** and is never published to npm by CI. The actual artifact under GitHub Actions is source/receipts only.

Commands accept no user-provided execution path, shell command, URL or cloud credentials. `audit` creates bounded SHA-256 file receipts for ten exact repo source paths; `verify` repeats source-policy checks; `plan --task` classifies and proposes up to four manual steps; `remote-plan` emits a *blocked* remote escalation plan. `audit --with-python` invokes only `tools/machineDebianSnapshot.py` with fixed arguments and an in-memory SQLite STRICT receipt, no host inventory.

The package doesn't make a network request, install software, open a socket, start a model, render a video, execute a shell, or write to the host. Source CI is not a real device benchmark.

## Four domains × four phases

| Audit row | Detect | Bound | Test | Escalate |
| --- | --- | --- | --- | --- |
| `0x00..03` **Kernel** | Host/kernel/CPU facts | Privilege, ABI, firmware policy | Read-only driver/audio/Vulkan capability when approved | Human host/GPU review |
| `0x04..07` **Data** | Python/Node/JSON/SQLite | UTF-8 byte size, typed SQL, Git SHA vs payload hash | In-memory SQLite STRICT + fixed-source hash | Optional scoped compute |
| `0x08..0B` **Browser** | DOM/WebGL2/WebGL1 capabilities | CSP, origin and media permissions | Firefox/Samsung/Chromium/Safari device test | Approved origin and kiosk |
| `0x0C..0F` **AI** | Intent and source | Allowlisted deterministic plan | Negative tests, exact-source receipt | **BLOCKED** remote provider until approval |

Hex values are **logical coordinates only**. Real x86/ARM machine registers, Vulkan feature bits, CSS pixels, media samples and file byte offsets are different namespaces.

## Sound and graphics

- **Linux audio:** ALSA and PipeWire can expose PulseAudio/JACK compatibility for supported desktop configurations. We should inspect the actual backend before tuning sample rates or latency; never run `pactl` or replace a service from a source audit. Android and Apple audio require their respective platform APIs.
- **Vulkan:** The loader connects applications to installed drivers. A Vulkan loader package or `vulkaninfo` source cannot prove the real GPU is compatible. WebGL/WebGPU in browsers are separate APIs and require browser feature detection.
- **DOM:** Mozilla docs are our compatibility reference, but Firefox, Samsung Internet, Safari and Chromium must each report feature support at runtime. PR #476's DOM-first Babylon kiosk remains independently proposed, not merged here. This package audits its interface, it doesn't embed a browser.
- **Video/AI:** FFmpeg is an optional CPU media worker. AI planning is represented by deterministic typed receipts, not a running inference engine. Existing Godot/Blender/Unreal studio tools remain separate.

## NGINX, Apache, PHP and SQL reduction

Treat popular servers as **reference architectures**, not packages to combine into the kernel:

| Project | Study | Decision for one-phone demo |
| --- | --- | --- |
| **NGINX** | TLS gateway, caching, static content, request limits | Optional authenticated remote edge only |
| **Apache httpd 2.4** | Reverse proxy, modules, auth | Exclude by default; alternative to NGINX, not required alongside it |
| **PHP/PHP-FPM** | Request lifecycle, server-side scripting and isolation | Exclude unless an actual legacy application needs it |
| **SQLite** | STRICT local records and explicit transactions | Retain, no daemon |
| **Postgres/MariaDB** | Shared SQL consistency, migrations, backups | Exclude until multi-user persistent backend is justified |

Official SQLite WAL notes explicitly restrict normal WAL shared-memory concurrency to processes on the same host; **do not host a SQLite WAL database on a network share**.

## Remote escalation (not activated)

`local plan → source and rights audit → exact source hash → task scope → human approval → authenticated TLS origin → scoped remote worker → signed receipt → review`

No origin, credential, billing entitlement, agent worker, network port, SQL endpoint, MCP execution route or model has been enabled. Existing Project Hydra / LuHm plugins remain separate from this package. A future connector must validate source authority independently of untrusted model text.

## References and support

- PipeWire Pulse compatibility: https://pipewire.pages.freedesktop.org/pipewire/page_pulseaudio.html
- Vulkan loader: https://docs.vulkan.org/guide/latest/loader.html
- Browser WebGPU fallback: https://developer.mozilla.org/en-US/docs/Web/API/WebGPU_API
- Node release maintenance: https://github.com/nodejs/Release
- SQLite STRICT and WAL: https://www.sqlite.org/stricttables.html and https://www.sqlite.org/wal.html
- NGINX: https://nginx.org/en/docs/
- Apache reverse proxy: https://httpd.apache.org/docs/current/en/howto/reverse_proxy.html
- PHP security: https://www.php.net/manual/en/security.php

**Crown STOP:** no production kernel mutation, public deployment, npm publication, owner-signed APK, cloud GPU activation, persistent SQLite database or remote execution. Source checks do not prove any physical machine, Firefox/Safari/Samsung rendering or actual AI inference.
