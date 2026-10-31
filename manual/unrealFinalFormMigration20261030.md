# Unreal Final Form Migration | Proposed source gate | 2026-10-30

**PR #463 candidate only.** No engine installation, runtime, GPU, signing, paid API, mods, device proof, merge, deploy or publication. CROWN STOP.

## One destination, small integration boundaries

Unreal Engine 5 is the **target final 3D game and cinematic runtime**, not the existing tested engine. Evaluate UE 5.8 on compatible desktop hardware; retain the current playable Godot 4 build until one original environment plus one rights-cleared character passes Unreal import, input, performance, licensing and packaging proof. Blender remains master for private editable art. Authorize and hash derivatives: GLB for simple content, FBX for skeletal rigs, USD as an optional complex-scene interchange. The Unreal Interchange pipeline owns import and reimport. No untrusted scene scripts.

NVIDIA ACE and DLSS are **optional RTX integrations**. AMD FSR is an **optional Unreal graphics feature**, while ROCm/ROCDXG is **separate optional GPU inference** on supported hardware/WSL. Oracle OCI AI is **opt-in**, authenticated, budget-gated and off by default. Vulkan is a possible Unreal rendering API, not a second engine. SDL3 is optional for standalone native input/diagnostic tooling, not a requirement inside Unreal. WSL2 is for development tools and supported GPU compute; native desktop Unreal Editor remains the primary installation path. The Samsung tablet is the capture/control cockpit, not the assumed heavy Unreal build machine.

## Nexus Mods boundary

Research official Nexus Mods API v3 and the current Vortex extension package `@nexusmods/vortex-api`. Start with a versioned mod manifest, dependency/conflict model and user-initiated metadata access. **Never** auto-scrape, download/rehost others' mods, store personal keys on a server, execute untrusted installers or claim a public application is registered without Nexus approval.

## Git alignment and slimming

Live GitHub inventory shows **19 accessible repositories**, of which **18 are public and one is private**. This public draft registry records the 17 public donors plus canonical LuHm-OS and does not expose the private repo's identity. Treat other repos as exact-SHA donors with keep / selectively-port / investigate / retire decisions after individual license review; do not bulk-merge histories or delete old branches.

Current protected `main` baseline `f0cb6ee54066b490c0e80efc2c96200fec76ee2d` has **129 workflow files**. Compare actual triggers, permissions, dependency versions, checks and artifacts before retiring any; avoid new workflows. Reuse `.github/workflows/free-first-workspace-daily.yml` on PR #463.

## Evidence command
```bash
python3 -m unittest tests.testUnrealFinalFormBridge -v
python3 tools/unrealFinalFormAudit.py --source-ref "$(git rev-parse HEAD)" --output /tmp/unreal-source-only.json
```
A PASS means only that the **policy source gate** passed at that exact SHA. It is **not** hardware or gameplay GREEN.

Official source references: https://www.unrealengine.com/license ; https://dev.epicgames.com/documentation/unreal-engine/importing-assets-using-interchange-in-unreal-engine ; https://developer.nvidia.com/game-engines/unreal-engine ; https://gpuopen.com/unreal-engine/ ; https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/docs/install/installrad/wsl/howto_wsl.html ; https://docs.oracle.com/en-us/iaas/Content/generative-ai/ ; https://github.com/Nexus-Mods ; https://help.nexusmods.com/article/114-api-acceptable-use-policy ; https://learn.microsoft.com/en-us/windows/wsl/tutorials/gpu-compute

**AI proposes. Policy authorizes. CI proves. Human promotes.**
