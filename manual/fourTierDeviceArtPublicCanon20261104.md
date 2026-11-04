# LuHm Four-Tier Device / Art Canon / Public Footprint
## Source and authority
As of 2026-11-04, GitHub main 69e8d2fc7df1288aaa1665efaea2bf2674056a1b. Existing four-tier operating model remains independent. New delivery stages: **Design → Testing**, **Propose**, **Data**, **Final**. No branch merges or app release are implied.

## Device lanes
- Samsung: reuse existing private LuHm Android beta companion and androidWeb3Plugin source; antenna and device API are explicit-permission, read-only-first, local-first. Need real signed install and on-device proof.
- iPhone: no verified native client. A native iOS export requires macOS + Xcode, signing, TestFlight/device proof. Do not present Android plugin as iOS-compatible.
- Raspberry Pi Linux: prove Pi model, distro and ARM ABI. Netplan applies only if selected distro uses it; headless starts without X11. X11/Wayland for a real kiosk-only need.
- Windows WSL: document WSL2 and Windows Firewall isolation, do not assume Linux boot service or root app runs on Windows. No accidental mirrored network exposure.
- Basement studio: current Codespaces contract and docker image are not a physically running basement server. Keep public-repo CI on GitHub-hosted ephemeral runners; basement build must be a separate owner-initiated private, ephemeral lane. Never attach persistent public PR runner to LAN or bridge MariaDB/SSH.

## Godot browser-to-device handoff
Godot 4 Compatibility renderer -> WebAssembly/WebGL2 browser export -> HTTPS static path. Browser performs WebGL graphics. Hosting the exported files is not remote GPU rendering. Test exact generated files, hashes and runtime in Firefox, Samsung, iOS Safari and Raspberry Pi. No unsafe asset CDN copy; use approved public derivatives only.

## Art canon and rights
Resolve identity through game/canon/CHARACTER_CANON_V1.json and doctrine/characterCanonRegistryV1.json, staging via media/public-release-art-ledger.json. Private Drive Art Magic Character Bible v0.1 is approved only for art direction/roleplay/pet cards. Separate original visuals from anime-derived names/concepts: Lum, Urd, Belldandy and Skuld have third-party lineage concerns, even if costumes are original. Do not publish without a real rights/licensing or legally reviewed original-character redesign. Urd source pack is private-only and unapproved. Per-asset human authorship, creator credits, license, source SHA, approved public derivative, and exact Professor signoff are mandatory. GPL-3.0 for code does not itself prove rights to every image/character.

## Protect the names and art
Copyright registration and trademarks require a distinct owner-driven legal process; there is no filing/registration evidence in current reviewed sources. Capture human creative authorship and original files, record AI-assisted portions honestly, prepare registrations of eligible original works; do a USPTO search and clearance before filing mark applications. Use provider-neutral logos only and do not imply GitHub/OpenAI co-ownership or endorsement.

## Public inventory and rollback
See doctrine/publicSurfaceInventory20261104.json. The connected GitHub account lists 19 public repositories; connected Render workspace lists 9 externally configured origins. These are not a comprehensive public-post census, successful HTTP tests, app store releases, or proof art assets are rights-cleared. Historical Instagram record is a single September reel and might be outdated. Do not publish private ChatGPT sites or restricted Drive files. Existing exact-main source snapshot ref is available; each specific app change gets its own source+artifact recovery receipt.

## Release and security
No public-LAN runner, automatic Cloudflare/Render changes, SQL exposure, automatic brand correction, app signing, IP claims or Crown. CI tests the proposed source only. Physical tests, local machine configuration, store credentials, legal clearance, and final distribution remain separate.
