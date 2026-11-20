# Operation Titan 7 | Reaper Film Desk

**Status: tested private development candidate, not production deployment.**

A low-drama film edit desk built from existing LuHm-OS Canon for **Pirate Daddy Film**. Editing tools belong to **Pirate Daddy Studios**. This project adds a private Python 3 + SQLite + FFmpeg workbench and mobile HTML UI without changing the existing Render MCP host, Cloudflare DNS, or Godot/Vulkan/Android release pipelines.

## What you can do today

1. Upload footage from the phone or pull a temporary working copy into a local terminal. Originals belong in the **owner-only Drive vault**.
2. Open the private web desk, choose an ingested video, generate a 480px-wide 24fps silent proxy and contact sheet, then scrub it with approximate 24fps frame steps.
3. Mark in/out, select `stressShake` or `hardMono`, add shots to a cut list, download EDL JSON, or render a silent 540×960 portrait rough cut (max 24 cuts, max 10 minutes).
4. Download the rough cut from the private web desk and polish it in your chosen desktop/Android editor. The result is *not* an automated public release.

The backend stores SHA-256 receipts and media pointers in **SQLite**, not media blobs. MariaDB and PHP tools are **optional future services**; this release does not start them. Each uploaded clip is a processing copy and does not imply that the Drive master was backed up.

## In Codespaces (existing Ubuntu devcontainer)

Do not replace the existing `.devcontainer/` image. In the on-demand Codespace terminal:

```bash
cd host/titan-film-desk
export TITAN_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
python3 titan_film.py serve --port 8786
```

The worker requires a `TITAN_TOKEN` of at least 24 characters and never prints it. Keep the environment private; enter the token in the editor form. Open port **8786 as PRIVATE only** in the Codespaces Ports tab. Do **not** publish the port or paste the token into GitHub or chat.

For a local test without exposing a port:

```bash
python3 -m unittest discover -s tests -v
python3 titan_film.py ingest /path/to/approved.mp4
python3 titan_film.py list
python3 titan_film.py proxy YOUR_MEDIA_ID
python3 titan_film.py render /path/to/reaper_edit_decisions.json
```

Optional Docker on a local Ubuntu/Debian host:

```bash
export TITAN_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
docker compose up --build
```

`compose.yaml` binds to localhost only and uses a Docker-managed volume so UID 10001 can write without running as root. No Docker, Render or Cloudflare service is actually created simply by committing this source. If replacing the named volume with a host bind mount, create an authorized private folder and grant it to UID 10001 first; otherwise the non-root container cannot write there.

## User-facing file destinations

- Private Drive: original live footage, high-quality audio and versioned masters.
- GitHub: source code, JSON shot decisions, sanitized metadata, templates and tests.
- Local/Codespace `/data`: disposable copies, proxies, thumbnails, contact frames, SQLite metadata and review exports.
- Public/social: only after artist approval and rights checks, and only via an explicitly initiated publish task.

There is **no automatic deletion of originals**, no remote source pull without authentication, no embedded provider secret, no persistent agent fleet, no paid GPU or billing integration. The `raw` folder inside the organizational art tree is public-write; it is **not** a private vault.

## Known limits

- Each upload is limited to 500 MB; combined working media, cache and exports are limited to 2 GB. Media processing is serialized and each generated file is capped at 256 MB. Proxies cache the first 300 seconds; long recordings need segmenting or an on-demand follow-up.
- Rendering is a **silent** rough cut. Multitrack audio, captions, precise timeline XML for a particular NLE, multi-segment long-form proxies and camera timecode reconciliation remain separate tasks.
- Client frame steps are approximate, not frame-perfect. Export and decode verification belongs to FFmpeg.
- Real Cloudflare Access, Codespaces Android rendering, Apache reverse proxy, Samsung APK, Pi deployment and MariaDB connections are **not yet tested**.
- Tests are synthetic and run without any user footage or secret.

## Canon crosswalk and infrastructure

| Layer | Concrete role |
|---|---|
| GitHub `eggie-admin/LuHm-OS` | Canon, code, CI; exactly one mutable candidate branch at a time |
| `doctrine/namingNamespaceCanonV1.json` | The four-stage identity: `REAPER_FILM_DESK` → `operation-titan7-film-desk` → `rprFlmDsk` → `reaperFilmDesk` |
| Internal `art.eggiebagelface.LuHmOS.reaperFilmDesk` | Organizational identity only, **not** public DNS or reverse PTR |
| Drive | Canonical original media/binary file server and backup; SQL stores references/hashes |
| Codespaces | On-demand sandbox. Temporary cache and private 8786 HTTP API; not a permanent VM |
| Apache HTTP Server | Optional, isolated, private reverse proxy config; does not replace existing working MCP/Render route |
| Cloudflare Access/Tunnel | Future approved ingress only, with authentication and real end-to-end proof |
| PHP/WordPress/phpBB/Webmin | Separate optional admin surfaces, **not** dependencies of the media engine; avoid bundling privileged admin tools with video ingestion |
| SQLite → optional MariaDB | Begin with SQLite for zero-config typed metadata; move only with a measured concurrency need and a reviewed migration |
| Raspberry Pi | Ubuntu or Raspberry Pi OS Lite with Python and FFmpeg is possible **headlessly**; no GUI desktop required |
| Samsung/Android | Browser viewer first, native APK/Vulkan separately gated and device-tested |
| Netplan | Host networking definition, never an automation scheduler; systemd timers or GitHub Actions handle scheduling |

## Existing source to reuse

`host/ai-ffmpeg/ai-ffmpeg.py` (older local worker), `media/pirate-daddy-film/episode-template.json`, `doctrine/artistFirstProductionWorkflowV1.json`, `doctrine/storageTopologyV1.json`, `doctrine/operationTitan7ChatTriggerV2.json`, and Yume/Lum/Urd/Skuld/Belldandy skills. This candidate is a separate lightweight editing **interface**, not a new competing agent authority.

## Open-source licensing

Preserve repository root GPL-3.0 notices. Do not relicense user code or merge GPLv2-only sources with Apache-2.0 sources without a compatibility review. `Apache HTTPD` is a web server, not the Apache-2.0 license. Keep per-asset footage/music rights and distribution-specific obligations separate from app source licensing.

## Copilot and Gemini review prompt

**Copilot:** check source/history/candidate diff, package security, data placement, SQLite parameterization, test failures, Codespaces private port, Docker non-root, FFmpeg subprocess allowlists, compatibility with existing `ai-ffmpeg` and 15-agent quarantine. Produce an exact-SHA code review with specific fixes. No automatic public deploy or main merge.

**Gemini (when independently connected):** adversarial architecture-only review, verify Python/Apache/MariaDB and Android/Pi technical assumptions against official docs; treat model output as candidate advice, not an execution or proof receipt. Do not send personal video assets or provider secrets to external LLMs without a specific authorized task.

**Lum:** reconcile both reviews, ask Urd to adjudicate contradictions and proof, Skuld for hard tool blocks, Belldandy for receipts, and Yume for edit quality. Agent roles in chat do not imply background workers.
