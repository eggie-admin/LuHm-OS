# LuHm-OS | Final brand / hexadecimal / vector / VM architecture seal

**Status:** draft candidate only. No protected merge, kernel replacement, firmware flash, paid VM creation, automatic branding publication or installed plugin update is authorized.

## What was actually established in chat

The connected **Project Hydra** `luhmConnectionStatus` plugin was reachable, and `luhm_open_cockpit` / `luhm_open_mobile_cockpit` returned in-chat MCP Apps UI. That is proof of the *current read-only plugin bridge*, not proof of our newly authored candidate widget or a booted VM. The provider explicitly reports device/agent/Godot checks as `notChecked`. Only a newly installed/reloaded candidate Site backend with a true user-visible invocation can certify the new widget mount.

Render read-only evidence on 2026-11-01:
- `luhm-os-godot-harness-green`, service `srv-dauc8lnavr4c738kfd0g`, **web service**, historical live deploy `dep-dbg48lijnfac73f7ngng`, source `ca369e6925406e9a00008bbc629bb5db67a7d02c`.
- `luhm-os-harness-green`, service `srv-daubsi1srm7s73bl5lh0`, **web service**, historical live deploy `dep-dbg32q4ipgvc73ebud7g`, same historical source commit.
- Both services are on `main` with auto-deploy off, not the active draft, and are **not general-purpose hypervisors**. A deployed web service or old Godot demo is not a VM guest boot or the current proposal's runtime proof.

The user-invoked existing Project Hydra plugin is the only already reachable in-app UI in this pass. The new source-only widget `ui://luhm-os/brand-vm-seal-v1.html` is registered via `host/mcp/luhmBrandVmSealTools.py` in the proposed harness, without touching the existing widget URIs. Deployment of that candidate and installation of the refreshed plugin require separate approval and proof.

## The four-by-four seal

| Axis | Source | Adversarial test | Host proof | Owner approval |
| --- | --- | --- | --- | --- |
| Hex codec | width-locked identifiers | reject bus/domain collisions | actual device/codec receipt | human gate |
| Bitmap → vector | owner-original pixels | bounded P3 RGB parser and SVG whitelist | raster/vector render acceptance | human art provenance |
| Brand | `LuHm-OS`, existing art preserved | no external SVG scripts, logos or third-party assets | preview appearance on Samsung | final visual rights and signoff |
| VM cockpit | source-only MCP Apps UI | detect simulated boot vs real runtime | actual guest + kernel + in-chat UI mount | signed release approval |

The four axes × four gates are sixteen **evidence candidates**, not sixteen running autonomous workers.

## Hexadecimal sorting rules

`tools/brandVmSealAudit.py` cross-checks the older machine Canon `doctrine/machineFourArchitectureForgeV1.json` and returns `kind:fixedWidthLowercaseHex` keys for USB/PCI IDs (16-bit), CPUID leaf (32-bit), IPS offset (24-bit), GUID text (128-bit), Git SHA-1 source identity (160-bit) and SHA-256 artifact digest (256-bit). Never compare numeric identifiers from different namespaces. Leading zero padding ensures a stable numeric sort inside one type, not a performance ranking or signing proof. UEFI GUID text and binary field ordering must be interpreted separately. No hexadecimal identifier grants boot authority.

## Bitmap → vector, safely

`bitmap_to_vector()` accepts an **owner-original, plain P3 ASCII bitmap** up to 16×16 pixels with six explicit brand palette colors. It returns a deterministic SVG of horizontal rectangles for exact pixel-run representation, plus source/vector SHA-256. It is a real, exact-pixel SVG derivative, **not an artistic Bézier trace or a semantic conversion of photographs**. Originals stay with the caller; no raw input pixels are stored in Git.

For smooth bitmap tracing of scans, Inkscape's **Path → Trace Bitmap** (Potrace) is a later *human-reviewed external tool*, with the original kept untouched. Its traces can be imperfect, especially with multicolor imagery. Source reference: https://wiki.inkscape.org/wiki/Potrace

The final candidate `publicationSite/brandSealCandidate.svg` is an original vector artwork proposal with a four-tier ring, neon violet/cyan geometry, LuHm-OS wordmark, and source-only rights warning. The existing `publicationSite/logo.svg` remains unchanged; neither candidate is silently made a published logo or social image. The SVG validator allows only a small static SVG feature set, refusing script, external image, foreign objects or arbitrary CSS.

## In-chat machine loader

`publicationSite/vmBootPreview.html` is a noindex source-only page with a simulated terminal/progress display. It never executes a real guest, reads local hardware, opens a network connection for status checks or copies secrets. The button *Play boot preview* only animates local text. A distinct user-clicked button may open the **historical Godot web-harness page** from one allowlisted Render host; it does not boot a VM and may be blocked by host framing rules. A separate external link remains available.

`host/mcp/luhmBrandVmSealTools.py` registers:
- MCP Apps resource `ui://luhm-os/brand-vm-seal-v1.html` with its own mobile page, embedded safe vector art, and a single opt-in existing Godot frame domain.
- Tool `luhm_open_brand_vm_seal`, returning source-only status, no mounted-plugin or VM claims.

The currently connected Project Hydra tool does **not** yet expose this new resource. Registration in the GitHub proposal is not a live installed plugin update.

## Kernel/platform discipline

The true near-term Linux objective is a reviewed **application package and optional Debian/Ubuntu kiosk profile**, not a new distribution or universal BIOS. Follow upstream supported architectures and genuine Android GKI/vendor-module separation; avoid a false claim that a custom mainline kernel is compiled, booted, supported or tested on Samsung. No production signing, Play Store submission, VM provisioning or company-worker activation is performed.

## Test locally

```sh
python tools/brandVmSealAudit.py
python -m unittest discover -s tests -p 'testBrandVmSealAudit.py' -v
npm test --prefix packages/luhm-canon-registry
```

GitHub workflow `.github/workflows/brand-vm-seal.yml` runs source tests and confirms all guarded, source-only status. The final CAST promotion path is exact GitHub commit → clean CI → human-reviewed branded asset → plugin update under owner control → true in-app UI invocation → separately authorized host/guest and kernel proof → owner public release. No skipped gates.
