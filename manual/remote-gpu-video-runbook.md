# LuHm-OS GPU video forge: local → enterprise, staged source candidate

**State:** draft PR candidate; no paid GPU, deployed worker, autonomous agent, remote VM, API model call, or source-owned video delivery claimed.

## First usable goal

From the existing **ChatGPT / Project Hydra** thin cockpit the Professor selects duration, original content, output size/frame rate, memory mode, and review cadence. The MCP tool `luhm_gpu_video_plan` builds a deterministic plan under `taskId / sourceRef / scopeId`. The host's private FastAPI `POST /v1/video/minute-plan` offers the same bounded plan with a host-only control token; never expose that control token, GPU IDs, SSH credentials or model keys in a mobile browser.

For a 10-minute project at six seconds per shot:
- 10 **deliverable timeline minutes**, each comprising 10 planned shots;
- 100 exact-ID placeholders, with one reviewed result and digest per shot;
- a 60-second chunk is marked reviewable only after actual bytes, ffprobe streams, media rights, continuity, source and snapshot authenticity are checked;
- the existing Godot/FFmpeg production route may assemble independently rights-approved final clips after an explicit private-render approval.

**This is a timeline segmentation plan, not a promise of generating a minute of video every wall-clock minute.** Some AI video providers can generate only short shots per request; validate each chosen provider's exact model, entitlement, quota, per-shot duration, aspect ratio, resolution and audio policy. The existing `host/api/luhmVideoJobWorker.py` is a separate, legacy provider-specific *source candidate* and is not re-enabled or copied into a new public service.

## Four escalation levels × four operational lanes

| Profile | Security and identity | Compute | Video | Receipts |
| --- | --- | --- | --- | --- |
| 0 Localhost | loopback, in-process dry run | no GPU allocation | plan shot IDs/60s delivery | local transient digest only |
| 1 Private host | strong server-side token, least privilege, authenticated tunnel | read-only GPU telemetry | media format/proof validation | private SQLite STRICT evidence |
| 2 Remote GPU | private mTLS, workload identity, device allowlist, one isolated worker per GPU | trusted GPU memory attestation and scheduler admission | generation only after approved budget and rights | exact operation IDs, verified hashes, encrypted snapshots |
| 3 Enterprise | tenant RBAC, short-lived identity, audit/key rotation, per-task cost and rate limits | optional Ray/Kubernetes GPU resource scheduling with actual driver/device isolation | bounded workers, backpressure, retry semantics, cancellation, checkpoints | durable SQL pointers, private artifacts, SLOs and rollback |

Every level retains LuHm Canon's **hear → resolve → act → verify** and **R1–R4** proof gates. Increasing compute complexity never increases agent or release authority.

## VRAM controls

The Professor's `maxApproved` preset means maximum *safe policy-bound* utilization, **not** 100% of total VRAM. The source planner computes a suggested `candidateUsableMiB = max(0,min(floor(total × 0.90), free − 1024))`. This cap is a conservative design starting point, **not** an empirical memory guarantee or real GPU admission. Change it only after actual headroom benchmarks, ECC/driver/runtime overhead and model-specific measurements.

Read NVIDIA NVML total/free/used and, for PyTorch models, separately monitor `memory_allocated`, `memory_reserved`, `max_memory_reserved`; don't double-count caching allocator memory. AMD ROCm or Intel Level Zero need their own measured adapters. If model VRAM estimate is unknown, the worker is unknown. If data is stale or user-supplied rather than verified by an authenticated host worker, **no admission is possible**. A multi-GPU model does not pool memory merely by listing devices; support requires explicit model parallelism and interconnect benchmarks.

Prefer one GPU job per device until measured. Ray/Kubernetes are optional future scheduling layers: logical resources are admission hints, not hard VRAM caps. Driver/device isolation, cgroup constraints, queue backpressure and worker teardown are required for true multi-tenant control.

## Resumption, privacy and cost

- At *every* subshot save exactly the matching `taskId/sourceRef/scopeId/shotId`, provider operation ID, rights, timeline offset, requested model/version, created/observed-at timestamp, bytes SHA-256 and private artifact pointer.
- Source change or shot-ID mismatch invalidates previous review GREEN; uncertain paid-submit outcome becomes `UNKNOWN_OUTCOME`, **never automatic resubmit**.
- SQL/MariaDB stores only metadata, not large video binaries or keys. Archive the actual bytes in approved private durable storage with digest, signed provenance and AES-GCM where required.
- Separate the work into preflight, permitted model call, private clip retrieval, actual file hash+ffprobe, continuity check, reviewed 60-second FFmpeg assembly, final media export and owner approval.
- Stop on GPU OOM, thermal limits, data rights, authentication failure, exceeded budget, disk exhaustion, dangling snapshots and missing host proof. A task may be canceled and manually resumed from last verified shot.
- Model rights, provenance and publication restrictions apply independently; public generative art defaults remain governed by existing Yume/Canon law.

## Transport and hosting

Reuse the existing Python MCP host; **do not add a public FastAPI admin port** or a new paid Render GPU service. A future remote worker uses outbound authenticated private transport, separate least-privilege workload identity, mTLS, bounded API schemas and zero browser credentials. The client receives status and reviewed artifact pointers only.

For a real remote GPU proof, capture hardware name, drivers, exact VRAM, CPU/RAM/disk/thermal, API authentication, local model checksum, network throughput, render frames/sec, one brief privacy-safe licensed fixture, and an actual video playback receipt. Do not treat a source/CI pass as hardware verification.

## Research

- NVIDIA `nvidia-smi` query memory fields: https://nvidia.custhelp.com/app/answers/detail/a_id/3751
- PyTorch CUDA allocator: https://docs.pytorch.org/docs/main/notes/cuda.html
- FFmpeg segment/concat muxers: https://ffmpeg.org/ffmpeg-formats.html
- Ray logical vs physical resource isolation: https://docs.ray.io/en/latest/ray-core/scheduling/resources.html
- Kubernetes GPU device plugin: https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/
- NIST 800-207 zero trust: https://csrc.nist.gov/pubs/sp/800/207/final
- OWASP API risks: https://owasp.org/API-Security/editions/2023/en/0x11-t10/

**Operator next gate:** prove source-head offline CI, then register one private read-only GPU telemetry adapter on a real authorized host. No GPU spin-up, paid vendor API, public publication, signing or live agent unquarantine is authorized by this document.
