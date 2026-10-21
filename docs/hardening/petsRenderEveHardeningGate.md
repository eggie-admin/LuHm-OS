# Pets + Rebel EVE: Render hardening gate

Status: candidate only. Do not merge or deploy before tests and asset authorization.
Date: 2026-10-20
Source: direct Render workspace inspection; GitHub direct. Codex not used.

## Verified service inventory
- Production harness: `srv-daubsi1srm7s73bl5lh0`, branch `main`, manual deploy, latest checked deploy status `live`.
- Godot web harness: `srv-dauc8lnavr4c738kfd0g`, branch `main`, manual deploy, latest checked deploy status `live`.
- Pet/MCP service: `srv-dasptdm0tbcc738guitg`, branch `feature/oni-pet-activity-dock-v2-20260927`, manual deploy, latest checked deploy status `live`, deployed commit `55da3d2bc464686da4761ddde69553c5e9989c15`.
- Yume auto beta: `srv-db006bqd0e5s739jrm00`, branch `beta/yumeArtChatV1-20261002`, auto-deploy enabled.
- Several web services expose `0.0.0.0/0` and have no `healthCheckPath` configured. Do not change ingress until ChatGPT connector authentication requirements have been tested.

## Required release gates
1. Preserve main production and Godot services. Keep this candidate branch isolated from auto-deployed beta branch.
2. Inventory Pets chat routes, 3D pet interaction endpoints, MCP tool auth, any websocket transport, and actual start-up binding. No guesses about routes.
3. Add unauthenticated liveness endpoint with zero private data, and authenticated readiness/diagnostics separately. Configure Render health check only after verifying the path returns 200 during warm and cold starts.
4. Authenticate privileged actions; verify tenant/session authority; enforce request-size limits, rate limits, CORS origin allowlist, and no browser-accessible secret material. Preserve legitimate MCP ingress.
5. Treat Rebel EVE donor as rights-pending and PRIVATE. Never commit unreviewed donor archives, textures, or models to a public repo, static site, or Godot Web export.
6. Archive inspection lane: validate archive format (RAR vs ZIP), hash, licensed origin, file count/size caps, decompression bombs, traversal paths, symlinks and malicious scripts before Blender import. Do not execute scripts inside the archive.
7. Private Yume pipeline: headless Blender import on isolated worker; generate sanitized GLB/WebP/LOD previews; publish only explicitly approved derivatives.
8. Godot web lane: public-safe placeholder until rights gate passes; asset firewall and no private donor bytes in HTML/JS/WASM/PCK bundles.
9. CI: dependency lock/audit, secret scan, Python tests, MCP auth negatives, asset firewall, Godot headless smoke, Render build smoke. All required before merge.
10. Deployment: one reviewed GitHub PR, immutable commit SHA, staging manual deploy, smoke test, then manual production deploy; retain rollback commit and compare response metrics.

## Current evidence
Render reports `live` for the latest checked deployments of the three core services. Live status does not prove end-to-end pet or EVE functionality, security posture, or device playback.

## Rollback
Stop promotion on failed health check, error spike, access-control failure, missing asset proof, or exposed archive. Redeploy previous verified SHA via controlled Render action; confirm service health and Godot playback.
