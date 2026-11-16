---
name: luhm-gpu-video-minute-pipeline
description: Plan high-throughput AI motion-video production from the existing ChatGPT cockpit through a private GPU worker, with 60-second review segments and Canon-bound VRAM/cost gates.
---

# GPU video forge: sixty-second deliverables

Use `doctrine/remoteGpuVideoPipelineV1.json`, `manual/remote-gpu-video-runbook.md`, `doctrine/yumeVideoAutomationBridgeV1.json`, and `doctrine/companyWideOperationalQuarantineV1.json` before interpreting video generation or worker status.

Existing LuHm MCP tools `luhm_gpu_video_status` and `luhm_gpu_video_plan` are **read-only source candidates**, not proof they are installed or reachable in the user's Android client. A future private FastAPI endpoint can plan with a trusted host-side control token; never put that token, GPU credentials, or sensitive prompt data in HTML or chat receipts.

The four security profiles are `localhost`, `privateHost`, `remoteGpu`, and `enterprise`. Their four lanes are `security`, `compute`, `media` and `evidence`. The user can request `conservative`, `balanced`, or `maxApproved` VRAM mode. No mode means 100% VRAM usage: preserve driver/OS/encoder/recovery capacity and require actual trusted GPU telemetry.

For one minute of *video timeline* output, create bounded provider-compatible subshots (e.g., ten six-second placeholders), then verify and assemble only actual rights-approved, hashed, format-compatible media. Show source SHA, per-shot operation ID, per-minute receipts, cost caps, runtime/power bounds, retries, error states and final owner approval. Do not promise one-minute wall-clock production.

No live worker, AI generation, model API request, GPU allocation, media streaming, paid compute, device access, provider unquarantine, VM mutation, merging, publication or Crown occurs in the candidate planner. Continue only with independently verified rights, execution budget, authenticated worker identity, matching source, measured GPU reserve, and scoped permissions. Source-only/test CI green is not live rendering green.
