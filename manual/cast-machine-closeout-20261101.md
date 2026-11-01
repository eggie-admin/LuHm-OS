# LuHm-OS | Machine-layer CAST reconciliation checkpoint
**2026-11-01 · protected draft · single-use CAST NOT ISSUED · Crown STOP**

## Decision: stop adding machine architecture and run real hardware

The four-source machine chain is **#477 → #478 → #479 → #480**. Those are stacked draft branches, not four independent changes to merge out of order. Their GitHub source checks ran green at the exact historically recorded PR commits. The present closeout records those SHA and workflow-run identifiers as **historical observations only**, not a claim that CI on today's branches will always be green. Recheck active PR head, parent branch, source SHA and required checks at the moment of promotion.

Protected `main` remained at `f0cb6ee54066b490c0e80efc2c96200fec76ee2d` when this closeout was drafted. Do not blindly merge any of these PRs, rebase their protected base, or substitute a portable ZIP for full repository reconciliation. Shared source/Cast policy is `doctrine/forgeTwinsV3.json`.

### Proposed machine ledger

| Lane | Observable evidence | Status and gate |
| --- | --- | --- |
| **Concept** | Minimal Pi OS Lite headless; 4×4 scoped hex `piOsMachine:0x00..0x0F`; named trust boundaries | ✅ Specified, not physical |
| **Prototype** | Debian nonroot/FFmpeg offline container, Python + SQLite, zero-dependency npm audit, Pi loopback HTML preview and adversarial tests | 🟢 Historically tested in exact-head CI |
| **Proposed** | Full parent chain, source/rights review, exact-current-head checks and Professor scope acceptance | 🟡 Ready for source review; not promoted or merged |
| **Beta** | A real Pi boot, drivers/kernel ABI, FFmpeg/Godot smoke, authenticated phone access, rollback, one-use exact-source CAST | 🔒 BLOCKED |
| **Final** | Physical beta acceptance, licensing/privacy, signed distribution, owner release approval, rollback and production observability | 🔒 BLOCKED |

Source and test CI do not create a signed release and do not confer deployment authorization. The Professor CAST Bridge GitHub workflow triggers only on **specific owner-authored PR comments**, not a casual chat request or the word "CAST" in a document. It does not automatically merge, install, release or publish. The canonical Forge model requires a new **single-use** CAST envelope for an exact candidate, milestone and build scope; release/install has separate authority. Existing `Professor CAST Bridge` runs labeled *skipped* on `main` are expected for events/comments not meeting its guarded condition. Do not diagnose them as a failing build.

## Last meaningful machine-layer source security patch

The Pi preview now rejects mismatched HTTP `Host` headers with `421`, including DNS-rebinding names pointing to `127.0.0.1`. Exact tests cover hostile hostnames, path traversal, arbitrary HTTP methods, CSP, no uploads and no public network binding. **This does not make the loopback service safely accessible from other devices.** Do not loosen to `0.0.0.0` to make a phone demo work; use an independently authorized and tested authenticated transport when needed.

## Four next blockers, smallest human requirements first

1. **Physical Raspberry Pi:** owner's board model/RAM/ARM64 OS/kernel/Device Tree/page size/driver/GPU/boot and backup. A CI x86 container does not prove a Pi install. No firmware flash without real rollback.
2. **Studio runtime on Pi:** one measured nonroot FFmpeg frame, a real Godot headless import, CPU/memory budget and clean restart with source and artifact hashes. Unreal and NVIDIA rendering remain remote optional candidates, never headless Pi prerequisites.
3. **Phone path:** test identity-restricted private HTTPS/tunnel transport, failure handling and revocation without a public unprotected listener; open the existing minimal browser GUI and confirm tap/motion/accessibility.
4. **Build/release authority:** only after real physical acceptance may the Professor issue an exact-source, single-use CAST attempt. A produced artifact needs hash, rights, signer, runtime and installation evidence. A separate human release gate controls beta and final publication.

The phone-first **First Night #475 / browser kiosk #476** branches are separate software-lane proposals, not merged into the Pi chain. They may be reconciled after this machine closure evidence without changing the physical kernel.

## New source CI and honest result

```sh
python3 -m unittest discover -s tests -p 'testCastMachineCloseout.py' -v
python3 tools/castMachineCloseoutAudit.py
```

The receipt reports `AMBER_MACHINE_SOURCE_READY_FOR_PROPOSED_REVIEW`, lists all nine source hashes, pins four historical PR heads, and emits the five external blockers. The gate **will not** output `betaReleaseReady`, `castAuthorized` or `publicDeployment` as true. It refuses changed source SHA claims, noncanonical hex, forged machine evidence and disappearing release gates.

**Machine closeout criterion:** Source-only changes stop when this audit is green and no high-value source security bug remains. The machine layer is **not physically complete**; the outstanding work is an actual Raspberry Pi evaluation and secure runtime. Moving to OS/studio **planning** is allowed, but producing a beta requires the separate physical and CAST gates. No invisible background build, bootloader mutation, agent activation, public deploy, or production merge.
