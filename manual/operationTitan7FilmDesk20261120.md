# OPERATION TITAN 7 — Source candidate snapshot · 2026-11-20

**Current baseline verified:** `eggie-admin/LuHm-OS` main truth, Titan7 trigger/execution, namespace law, network spine, storage topology, film/Yume and company-wide quarantine. This note is a scoped, historical *architecture* reconciliation, not a claim that every commit from the previous six months was individually audited.

## Reconciled decisions

- **Machine aliases:** reuse four-stage naming law; SQL table names are not required to mirror public hostnames. Store stable media IDs, SHA-256, project scope, rights and file pointers, not the media blobs.
- **One coherent media path:** Private Drive originals → short-lived working copy → FFmpeg probe, proxy, contact sheet → timecoded human EDL → silent rough MP4 → Drive-reviewed candidate → editor final polish.
- **Source:** existing GitHub repository; no new repository to keep in sync. Do not overwrite the Titan or media workers already present.
- **Compute:** on-demand Codespaces/local Ubuntu/Pi, never a 24/7 app server by implication. Retain existing Render MCP until alternate route gets independent live proof.
- **Languages:** Python control plane, SQL metadata, browser HTML/JS for UI, FFmpeg for actual video; GIMP/Blender/Godot remain optional art engines. PHP CMS/BBS/admin plugins are isolated services, not mandatory in first editing path.
- **Routing:** no DNS/PTR/Cloudflare mutation. Apache HTTPD/2 example remains private, selected by deployment; existing Nginx architecture must not be broken by a preference change.
- **Networking/scheduling:** Netplan for NIC/IP on supported host; systemd timers for recurring local jobs; GitHub Actions for finite CI; neither is replaced by the other.
- **Android:** first prove browser touch/file picker via Samsung, then optional APK packaging later. Vulkan is a graphics API, not a requirement for FFmpeg editing or server administration. Pi OS Lite can run headlessly without Raspberry Pi Desktop.
- **Licenses:** GPL-3.0 root stays. Apache-2.0 component license compatibility is not blanket permission to relicense GPLv2-only material. Original footage, stock CC terms and platform music license independently checked.
- **Crown:** user may ask for full Titan escalation, but existing quarantine prohibits interpreting this as permission to reactivate 15 external workers, charge vendors, leak private originals, or auto-publish.

## Implementation proof

Python standard library HTTP/SQLite backend + ffprobe/FFmpeg; browser scrubber with IN/OUT/EDL, private MP4 proxy/contact and rough cut download. Synthetic test suite validates hashes, deduplication, trim limits, two video effects, no original mutation. Docker and Apache private templates included. Full code is kept under `host/titan-film-desk/` without changing existing devcontainer.

## Outstanding gates

- Host Android/private Codespaces browser test.
- Authenticated **server-side** Drive ingest and archive worker (ChatGPT connector copy is currently available per user-authorized task; permanent storage access is not automatically inherited by arbitrary Docker containers).
- Real media >500 MB and long-video multi-chunk proxies.
- Asynchronous job queue and deletion policy after explicit Urd/human review.
- Direct export format for user's chosen professional finishing editor (DaVinci/Kdenlive/CapCut etc).
- Tested MariaDB migration, Apache/PHP coexistence and separate admin security.
- Copilot actual review and external Gemini advisory review, if connected.
- Canon merge and public deployment authorization and evidence.
