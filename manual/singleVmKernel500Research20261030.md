# LuHm-OS: single-VM kernel-to-K9000 4x4 research | 2026-10-30

**Status: candidate research.** Protected main, #448, live Render, Google account, Cloudflare, DNS, agents, and physical machines remain unchanged. Crown STOP.

## 4x4 doctrine: keep four distinct systems
- Four *composition columns*: coreLibrary; pluginExtension; classWidgetOrganization; stubAdapterBoundary.
- Four *platform rows*: kernelHost; networkDns; headlessRuntime; appAndProviders.
- Four *interaction beats*: hear; resolve; act; verify.
- Four *escalation levels*: 0,1,2,3. Each escalates only through explicit policy and evidence. No layer or named agent grants Crown.

## 500 assessment slots with truthful evidence
`tools/kernelVm500Audit.py` defines 25 specific controls per layer, totaling 100 distinct control definitions. Each is scoped to five targets: actual GitHub Actions Linux runner; Google Compute Engine e2-micro; Oracle Cloud A1; Raspberry Pi; Samsung Android/Shizuku. Result: 500 unique `target/layer/control` assessments. The 400 non-runner assessments **must remain UNVERIFIED until that exact machine is reached**. Runner sysctls only establish *ephemeral runner* state, not local Mint, GCE, OCI or Samsung kernel security. Source policy and real DNS syntax tests are a separate CI lane. Existing Titan 500 is an independent source/document audit, not a physical 500-kernel test.

## Zero-cost contenders (official public terms read October 30, 2026)
| Candidate | Free VM resources | Caveat | LuHm suitability |
| --- | --- | --- | --- |
| Google Compute Engine | One e2-micro-month in us-west1/us-central1/us-east1; 1 GiB RAM, 30 GB-month standard PD, 1 GB qualifying egress | Public IPv4 is billed (current $0.005/hour on a standard VM, except narrow first-hour exemption); budget alert is NOT a hard spending cap; extra network/storage/API/AI can cost | Very lean test/MCP status endpoint. **Not proven $0 public replacement for Render.** |
| Oracle OCI Always Free A1 | 1500 OCPU-hours, 9000 GB-hours: equivalent to up to 2 OCPU and 12 GB all month; up to 200 GB eligible boot/block combined, 10 TB/month eligible outbound | Home region and capacity; idle-resource reclamation; some resources are billed on paid accounts. A1 is ARM64, not AMD64 | Best first conditional single-node candidate for lightweight MCP+SQLite+small web assets, subject to real benchmarks |
| Raspberry Pi OS Lite | User-owned ARM64 SBC, headless | Physical board, power/storage/network and local WAN reachability not evidenced; not literally free hardware | Optional local DNS/audio/camera bridge, not publicly required |
| GitHub Codespaces | Personal-account quota varies by plan; development workspace, auto-sleeps | Not 24/7 app hosting; organization-owned quota differs | Development and CI only |
| Render | Existing free-plan MCP/Godot sidecars already configured in doctrine | Live deployed SHA, uptime and public endpoint must be compared | Retain while migration measured |

Oracle's current official free-tier description states **2 OCPU/12 GB**, not older 4 OCPU/24 GB material. Free A1 shapes may be unavailable, and Oracle may reclaim idle instances. Both GCP and OCI need verified IAM, region, quota, network and payment state before a launch. **No such cloud-account access has been evidenced here.**

## Proposed low-fat one-VM architecture
- One ARM64 Ubuntu/Oracle Linux VM only if eligible: host distro kernel, systemd user or bounded service, Python 3 and typed SQLite on local restricted file, optionally static web bundle; expose **only authenticated HTTPS/MCP** through an approved ingress.
- No Blender/GIMP, GParted, Node/npm, full model weights, database server, Termux, Shizuku or browser renderer in the VM service. Vite/npm remains CI build time. Blender and high-load media tasks remain a separately authorized workstation/worker.
- GitHub remains source/CI and artifact hashes. Google Drive is the existing durable **binary archive**, not replaced by SQLite; back up VM state *off-VM* with private access and test restoration before cutover.
- No direct public SQL, MCP admin, cloud credentials in code, paid Gemini inference or open internet recursive DNS.

## DNS separation, without changing the registrar
- Canonical **Cloudflare** remains public authoritative DNS (doctrine/cloudflareEdgeHardeningV1.json). Do not switch nameservers or DNSSEC/DS. A single private BIND9 server cannot safely replace redundant public authoritative DNS.
- Staged BIND9 standalone reference in `infra/single-vm/bind9/` answers the **private illustrative** `vm.luhm.test` namespace on `127.0.0.1:53`, recursion disabled, transfers and dynamic updates refused. Zone addresses are local-only placeholders, **not routable public service discovery**.
- Optional `dnsmasq` at `127.0.0.1:5353` forwards `vm.luhm.test` to private local BIND9. This is a **Linux or local LAN companion**, not a DNS daemon inside the Android application. For remote clients, require a separately authenticated private tunnel and privacy-aware split DNS design. Do not open WAN TCP/UDP 53.
- CI parses these with `named-checkconf`, `named-checkzone` and `dnsmasq --test`. A syntax pass is **not** a live DNS response or routing proof.

## Shizuku, Raspberry Pi, OpenAI Sidecar
- Android **Shizuku** (canonical spelling, not Shizuka): separate explicit ADB/root-mediated binder permission bridge; Ubuntu/OCI VM cannot run Shizuku to control the phone. Existing `doctrine/samsungAntennaV1.json` has a proposed Termux/X11 experiment that remains distinct from public APK runtime dependencies; protect Samsung vendor kernel/GKI.
- Raspberry Pi OS Lite ARM64 as local peripheral concentrator only after board proof; never use Pi as a hidden prerequisite for one app.
- Existing `doctrine/githubRenderSidecarV1.json` is a canonical GitHub-primary/Render-runtime **OpenAI-facing** sidecar, not proof an OpenAI first-party sidecar exists. Changing the Render runtime to OCI/GCP would require approved doctrine revision, exact-source TLS/MCP/auth canary and rollback; no unattended Render deletion.

## Proposed cutover receipt, not launch authority
1. Inventory Render services, endpoint contracts, secrets source (without exposing values), Drive pointers, static sizes, CPU/RAM, requests, logs and dependency versions.
2. Prove zero-spend/eligible VM shape and IAM/region, calculate public IP + egress + backup costs and define strict quotas. A Google Cloud budget alone cannot enforce $0.
3. Bootstrap non-root SSH/host firewall/private DNS in a **separate, explicitly approved** deployment; apply source-pinned Python packages and migration script; no public 53/SQL.
4. Run kernel500 on real VM, external HTTPS/MCP tests, SQLite backup/restore, offline operation and auth negative controls.
5. Canary ChatGPT MCP and Godot preview against exact source SHA; compare Render baseline latency/uptime and app API contracts. Keep Cloudflare and existing DNS until human cutover.
6. Decommission Render/HF only after real source-to-runtime receipts plus a tested rollback; optional paid resource uplift requires separate approval and budget.

## Audit commands
```sh
python3 tools/kernelVm500Audit.py --runner-scope --output build/kernel500/receipt.json
python3 -m unittest tests/testKernelVm500.py -v
python3 tools/hardSystemAudit200.py
```

## Official sources
- Google free: https://docs.cloud.google.com/free/docs/free-cloud-features
- Google external IPv4: https://cloud.google.com/vpc/pricing
- Google budgets not a cap: https://docs.cloud.google.com/billing/docs/how-to/budgets
- Oracle Always Free (and idle reclamation): https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm
- Raspberry Pi OS Lite: https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/computers/os/rpi-os-introduction.adoc
- Shizuku official: https://github.com/RikkaApps/Shizuku
- BIND security: https://kb.isc.org/docs/bind-best-practices-recursive
- GitHub Codespaces: https://docs.github.com/en/billing/concepts/product-billing/github-codespaces
