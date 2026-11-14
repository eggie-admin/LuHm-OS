# LuHm-OS Canon Control Room · candidate distribution upgrade

Status: PROPOSED_ONLY. Not merged, released, deployed, hosted in ChatGPT, or installed on Samsung.

## Where it runs

- Entry: frontEnd/canonControlRoom.html, a local HTML module that can be served by the existing frontEnd static server.
- Existing chat stays the default. The Canon tab in frontEnd/index.html opens the new control room.
- Core logic: frontEnd/canonControlRoom.mjs. No third-party CDN, remote API call, browser secrets or live worker invocation.
- Tests: frontEnd/tests/canonControlRoom.test.mjs, also appended to the existing npm check script.

## Why the entitlement correction matters

The account's September 2, 2026 Google AI Pro welcome email historically confirms consumer subscription enrollment. A November 5 support response supplied Google Developer Program enrollment links but explicitly did not attest that enrollment was complete. On October 30 Google reported the Gemini API billing account moved to Suspended Service Tier; the subsequent November 6 Google Cloud notice reported billing account and related project/service termination. No authenticated live reinstatement or API quota proof is available through the current ChatGPT connection.

The separate, sanitized evidence review is doctrine/googleAiEvidenceReview20261114V1.json. It does not contain billing identifiers, Google account identifiers, Gmail bodies, keys, or private Drive IDs. It does not overwrite the existing doctrine/googleAiDeveloperEntitlementsV1.json. Consumer Gemini access and developer API execution are separate.

## What actually works at the candidate layer

1. Six touch/XMBI-style panels, with vertical swipe switching.
2. Canonical 15-agent role roster and supervised route planning for Lum, Skuld, Belldandy, Urd, Yume and Sumi.
3. Task envelope exports matching the primary fields of doctrine/aiTaskManifestV2.template.json. Primary OpenAI chat exists; a separately running mini-thread is **not** asserted.
4. Local file/folder metadata discovery for ZIPs, assets and models. File contents are not transmitted, unpacked or hashed; manifests retain unknown rights and publicApproved:false. The earlier inventory records 110 verified starter assets, **not** the complete 1+ GiB collection.
5. Local PNG/GIF/JPEG/WEBP preview selected by the user. No automatic redistribution of private character art.
6. Read-only service state cards with evidence-grounded distinctions.
7. Local, non-authoritative frontend audit and JSON receipt shape checks.
8. Distribution-upgrade preview/receipt exports, without an API that can silently install, authorize Cloud spend, merge, deploy, sign or Crown.

## Sanest install path (not executed by this PR)

Phase A: keep source in GitHub and large rights-controlled binaries in Google Drive. Use existing tools/sortArtArchives.py only on authorized local ZIP files to a private, non-repo destination. RAR/7z and .pck donors require separate reviewed importers.

Phase B: build and test the existing Godot 4 runtime and Android WebView shell using one pinned source. Stage a private APK and digest in the existing installPortal artifact. Ensure a stable signing identity across upgrades, verify package identity, keep rollback snapshot, and do not clear installed data.

Phase C: on a device, the owner taps a verified private LAN install link, accepts Android's standard download/install prompts, then starts the cockpit. The initial allow button cannot bypass Android OS permissions, signature continuity or unknown-source protections. Android physical proof is separate.

Phase D: ChatGPT app widget/MCP hosts expose only typed, read-only preview and candidate import status until exact current host invocation and permission checks. Do not connect private binary contents to public deploy. The secondary OpenAI thread and Google AI adapter need actual host/provider execution receipts.

Phase E: only after current Google billing/API activation, budget/region/quota/IAM, least privilege, and authorized smoke test may paid Google AI runtime be proposed. If billing remains terminated, route to deterministic local and independent non-Google work. Google AI Pro subscription must not be treated as developer API authorization.

## Canon constraints

- Existing names are preserved: LuHm-OS, projectPremonition with historical Project Hydra, plus the 15 existing camelHump IDs.
- Current source truth: doctrine/currentSourceTruthV3.json. No silent rename.
- Order: sanityCheck → audit → ingest → mutation → test → apply → continue → deploy.
- One mutable source lane, max three parallel support specialists, role registration does not equal running workers.
- Company-wide worker quarantine remains intact; no automation unquarantines anyone.
- Human promotion and publication remain separately Crown gated.

## Proposed next review

- Run the exact frontEnd npm check workflow at the PR head and record it.
- Check Android WebView compatibility and Godot 4 scene boundary in isolated CI.
- Reconcile Drive asset size/rights using exact owner-controlled metadata, no bulk publication.
- Verify ChatGPT app host invocation against the exact candidate and obtain a bounded read-only receipt.
- Resolve current Google billing/API state directly through Google's authenticated account interface, never by assuming the September subscription email authorizes API spending.
