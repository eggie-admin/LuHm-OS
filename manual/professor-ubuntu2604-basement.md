# Professor's Ubuntu 26.04 LTS Basement

## Workspace contract
The canonical development workspace is the GitHub repository `eggie-admin/LuHm-OS` inside GitHub Codespaces. `.devcontainer/Dockerfile` creates an Ubuntu **26.04 LTS userland** (headless, no GNOME or display manager). Codespaces uses its provider-hosted kernel; this is not a dedicated Ubuntu Server VM and cannot guarantee 24/7 uptime.

**Professor's LAMP** = Linux + AI + MariaDB + Python. Nginx is the optional local HTTP gate. Do not install Apache/PHP merely because of the conventional acronym.

The image installs Python 3 and venv, Node/npm, Nginx, MariaDB, Certbot CLI, Blender, GIMP, FFmpeg, Xvfb, and a SHA-256-verified **Godot 4.7.2** binary (amd64). The repository contains the doctrine and project sources. This does **not** prove running AI models, active services, hardware acceleration, physical-device status, or in-chat cockpit mounting.

## Operational boundaries
- Docker build must succeed before calling the image ready. Run `bash scripts/professorGarageSmoke.sh` inside the **actual** Codespace to verify tools.
- Existing `scripts/ai-ffmpeg-codespaces.sh` creates private localhost-only worker credentials in the Codespace user's home and starts the worker on loopback port 8797. Leave port forwarding **private**.
- Nginx and MariaDB packages are present, **not auto-started**. MariaDB is configured with `skip-networking=1` and local UNIX socket only. Start services explicitly for a specific task with a runtime receipt. Never open database ports, Apache ports, or raw-IP ingress.
- Certbot is installed as an **offline-capable client**; no cert is issued, no `/etc/letsencrypt` material is assumed, and Cloudflare/Render managed TLS remains separate. No hostname or certificate change is implied.
- GIMP's interactive UI is not available headlessly; use its batch interface under `xvfb-run` when a concrete job is defined. Blender uses `-b`; Godot uses `--headless`. Real rendering still requires representative test assets and output review.
- **GABE** is requested by Professor but has no verified package/project identifier yet. Do not invent a package or claim installation. Add it only with exact source identity and audited installation proof.
- The 15 registered LuHm role workflows remain **quarantined** per `doctrine/companyWideOperationalQuarantineV1.json`. No agent is activated by installing the toolchain.
- Secrets and artwork do not enter public GitHub. GitHub Actions outputs are temporary; Drive remains the approved long-lived binary archive.

## Tests and recovery
Run `bash scripts/professorGarageSmoke.sh` after creating or rebuilding Codespace. Run `bash scripts/ai-ffmpeg-codespaces.sh status` to prove the worker. Build/test Godot scene imports and headless Blender renders separately. Run contract audit via `python3 tools/professorGarageContractAudit.py`.

A failed migration can return to the prior devcontainer definition at source `96d426108347c8c17e9c462806479279ef835822` without deleting private media or changing Render/Cloudflare.

**Release status:** source candidate only, no Codespace host invocation or runtime validation yet. Crown: STOP.
