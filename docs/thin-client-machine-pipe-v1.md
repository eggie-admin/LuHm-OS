# Machine-only thin-client piping contract (PROPOSED)

Exact source: evaluate each run against the current GitHub main SHA. No promotion from this document.

## Scope and reduction

- Firmware/BIOS/UEFI: inventory and read-only compatibility evidence only; no firmware mutation. Android devices keep their OEM boot chain.
- TOS: terminology pending contextual definition; do not import Atari TOS or any alternative kernel as a dependency.
- Linux/Android kernel: use the vendor-supported kernel, system calls and hardware APIs. No custom kernel build unless a reproducible device blocker proves necessary.
- Display: Android WebView or browser for Samsung; headless Linux needs no X11. On Linux kiosk, prefer supported Wayland, add Xwayland/X11 only for a proven compatibility requirement.
- Thin client: frontEnd HTML/JS and existing Godot bridge; no duplicate web frontend framework. Keep the existing jQuery lockfile until tests prove replacement is beneficial.
- Transport: same-origin HTTPS, simple JSON API, explicit allowed routes, no unauthenticated administrative endpoints.
- NGINX: optional edge reverse proxy for the remote deployment, NOT a replacement for the application or AI model. Reuse official upstream packages, pin versions, and test config before reload.
- Backend: existing host/api/luhmApiSpine.py capability router plus current SQL adapters; keep vendor routing explicit and fail closed.
- SQL: pointer/receipt index only; artifacts remain files. Verify exact SHA-256 and byte sizes before update.
- Update: testing/debug Build A -> proposed reproducible Build B -> separately owner-approved CAST -> beta; no autonomous promotion.

## Four-by-four validation

1. BOOT: source identity, supported hardware/ABI, OS/runtime API, rollback path.
2. CLIENT: HTML lint/tests, offline fallback, touch responsiveness, CSP/security review.
3. PIPE: explicit request/response schema, API allowlist, error/timeout behavior, optional NGINX config test.
4. UPDATE: SHA-bound build receipt, SQL artifact pointer, signed artifact validation, physical-device install/update proof.

Each check yields GREEN (verified), AMBER (missing proof), RED (failing), or BLOCKED (external prerequisite).
A new sourceRef invalidates any prior promotion claim. Verify each layer both downward and upward.
Stop when evidence is sufficient; do not attempt byte tuning, BIOS flashing, X11 installation, or NGINX deployment without a demonstrated need.

## Target in-chat loop

Professor describes a feature -> supervised chat interface produces scoped change -> draft branch -> automatic CI build and 4x4 checks -> receipt -> proposed candidate -> owner CAST -> beta update.

This contract does not claim a running AI agent, completed NGINX deployment, or a working Android installation.
