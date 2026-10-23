# LuHm OS | World Headquarters Final Form (source-only candidate)

**Professor:** human creative/Crown authority. **Lum:** one central coordinator.

## The two required compatibility layers
1. **OpenAI / ChatGPT first:** in-chat Work, MCP, plugin Sites and artist-facing cockpit. These interfaces are access paths, not canonical source or paid API entitlements. Work mode must actually be available on the user's account. No Codex required.
2. **GitHub second:** `eggie-admin/LuHm-OS` on `main` is authoritative for immutable source, workflows, tests, manifests and receipts. The second layer is **not** a second competing truth. Codespaces is the checked-out R&D working mirror.

Both layers carry exact `taskId`, `scopeId`, `sourceRef`, budget and evidence references; disagreements fail closed. Contract: `doctrine/studioCompatibilityFastMeshV1.json`.

## World Headquarters and traffic
Professor → Lum (cabinet: Urd for diagnosis, Belldandy for records, Skuld for research; Yume for creative production) → minimum task specialists. Cloudflare handles DNS, TLS, Zero Trust and optional tunnel, **not** AI or GitHub authority. Existing Render harness and Godot services remain preview/MCP runtime sidecars. Do not add new paid services or expose private LAN.

## Professor's Basement / R&D
Reuse `.devcontainer/devcontainer.json`, `manual/professor-ubuntu2604-basement.md`, `scripts/professorGarageSmoke.sh`: Ubuntu 26.04 userland in GitHub Codespaces, Python 3, FFmpeg, headless Blender, GIMP 3 under Xvfb, Godot 4, optional Nginx and MariaDB socket. The actual Codespaces runtime and binaries are **not verified by this document**.

## Forge Twins and Oni
- **Tetsu:** protect, ingest, and prepare exact source candidates; no compile.
- **Kaji:** compile only after exact one-use CAST envelope and specified build scope; no source mutation.
- **Kugi:** deterministic bounded mutation bridge; Urd adjudicates evidence.
- **Kiri, Momo, Shiori, Fumi, Sumi, Koe, mediaAssetFactory:** specialize when task scope requires them.
- **Company-wide task workers remain quarantined.** Goddess/Yume conversational presentation is not hidden worker execution.

## Canonical workflow
`sanityCheck → audit → ingest → mutation → test → apply → continue → deploy`

The phrase **RECONCILE MERGE DEPLOY CAST FINAL FORM FINAL BOSS** selects the structural review procedure, **not** a bypass of exact SHA, scoped CAST, CI, user-approved merge, deployment-target verification, signing, permission, or Crown gates. A CI-green commit is not a live MCP, Android, or Blender proof. Do not place private Drive IDs, private art, signing keys, or OAuth tokens in the public repository.

### Static source audit
Run `python3 tools/worldHeadquartersAudit.py` and `python3 -m unittest tests/testWorldHeadquartersAudit.py`.

A source-only GREEN result does not activate independent agents, update ChatGPT entitlements, merge GitHub branches, redeploy Render, change DNS, or promote canon.


## Reconciliation receipt
The candidate was rerolled onto current `main` at `a795edac042f968e439ecd93293c99d48d40c696`. The prior candidate head was `bec22bcbb04ae26212754b9c94c94694f8e67647`; its 30 reported check runs succeeded. Fresh checks must pass on the rerolled head before review. The PR remains draft and source-only.
