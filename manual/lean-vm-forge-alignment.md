# LuHm-OS lean VM Forge: machine-readable source map and provider boundary

**Scope:** exact `eggie-admin/LuHm-OS` draft source. **Status:** source-only, not a deployed VM, SSH/netplan change, new paid account, ChatGPT Site backend mutation, public proxy, MariaDB migration, or actual Samsung installation.

## The actual minimal LuHm stack

The user-facing ChatGPT cockpit is a thin client. GitHub `main` is source authority; reviewed draft branches hold proposed changes. Existing Render Python MCP services are specified in `render.yaml` with `autoDeployTrigger: off` and `plan: free`. These are managed **web services**, not a substitute for a self-administered general-purpose VM. The private `host/api/luhmClientFastApi.py` is an **optional source-only** token-authenticated host loopback planner and must not appear as a public admin API or be assumed to run on a Samsung tablet.

For a headless Linux VM, reuse Python 3 plus SQLite STRICT for local receipt indexing. Add the existing private MariaDB receipt adapter only when approved persistent storage and TLS-authenticated operator infrastructure actually exist. SQL indexes metadata and binary pointers; verified media and APKs go to approved private durable binary storage, per `doctrine/storageTopologyV1.json`. No SQL/FFmpeg on an Android thin client.

`doctrine/leanVmForgeAlignmentV1.json` is the canonical candidate map of **four concern lanes** (source, execution, transport, rights) and **four security levels** (localhost, private VM, trusted proxy, enterprise candidate). `tools/leanVmForgeAudit.py` validates real source references and options, not a hypothetical tech catalog. Only the **same GitHub exact SHA and task/source/scope receipt** may advance to the next bounded gate; anything missing is HOLD.

### What the file types actually do

| Representation | Actual LuHm role | What it is not |
| --- | --- | --- |
| Markdown `.md` | Operator knowledge, runbooks, copyright notes | CPU machine language or executable permission |
| JSON | Typed Canon identities and capability contracts | A verified VM or execution authority |
| YAML `.yaml/.yml` | Render, Actions, candidate Netplan configuration | A live network change until applied and observed |
| SQL `.sql` | Local SQLite STRICT structure or candidate private MariaDB schema | A media file server or encrypted byte stream |
| Python `.py` | Host-side planners, validators, optional media scripts | A real worker unless installed, launched, authenticated and measured |
| Hexadecimal | Readable encoding for Git refs and SHA-256 receipts | Encryption, consent, signed publisher identity or machine code |

One schema maps file paths and identifiers, while **GitHub commit SHA** identifies code. Content SHA-256 verifies bytes. HMAC and AES-GCM play different roles for authenticated and encrypted receipts; none grants promotion.

## Netplan, Cloudflare and origin proxy

`config/netplan/90-luhm-vm-dhcp.example.yaml` is **never installed**. It uses an illustrative `eth0` match, which **is not universal**: observed OCI, GCE, Azure or AWS images might name the NIC differently, and cloud-init may already own `/etc/netplan`. Before even considering applying a real config, read the actual machine identity, active NIC and cloud-init ownership; obtain console recovery and rollback. Validate with `netplan generate`; use `netplan try` with timeout and actual console confirmation and verify network recovery separately. Some virtual device rollback paths need special care. No network mutate, static IP, gateway, DNS override, SSH opening or service restart is triggered by the source example.

Preserve the current `https://luhm-os-harness-green.onrender.com/mcp` and Render-managed TLS. `doctrine/networkSpineV1.json` and `doctrine/cloudflareEdgeHardeningV1.json` make the public MCP path **DNS-only direct Render** until ChatGPT's streaming and authentication contract is verified. Cloudflare Tunnel is an optional **outbound-only private-portal candidate** with separate identity and origin TLS proof; it does not license exposing `/v1/`, MariaDB (3306), Postgres (5432), SSH (22), GPU job control, cameras, raw shell or any admin route. NGINX is optional and only when an actual private reverse proxy is necessary. Do **not** run redundant Apache httpd and NGINX merely because they are upstream examples.

## Real remote free-tier VM candidates (researched 2026-11-01)

**These are offers, not proof of active entitlements, provider access, or guaranteed zero cost. A credit card, home region, capacity, disks, IPs, transfer and plan rules may affect cost. GPU models and paid AI video are not free-tier resources.**

- **Oracle Cloud Always Free:** A1 Arm: first 1,500 OCPU hours and 9,000 GB hours per month (equivalent to about 2 OCPUs and 12 GB continuously), plus eligible AMD micro instances. Subject to home-region availability and account approval. https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm
- **Google Cloud:** free e2-micro month-hour allotment in selected US regions; 30 GB-month standard disk and restricted outbound bandwidth. GPUs are expressly excluded. https://docs.cloud.google.com/free/docs/free-cloud-features
- **Azure:** eligible introductory free B-series VMs, commonly up to 750 hours/month over 12 months. Verify current shape, region, disk, eligibility and whether an account already used the promotional window. https://azure.microsoft.com/en-us/pricing/free-services/
- **AWS:** new-account introductory free plan of up to $200 credits, ending after six months or depletion, **not** an always-free EC2 VM. https://aws.amazon.com/about-aws/whats-new/2025/07/aws-free-tier-credits-month-free-plan/

GitHub Actions is CI, not a persistent VM. The two existing Render free **web** services remain existing source infrastructure. Cloudflare Tunnel is a network path, not a compute provider. The preferred next real VM proof after first-party eligibility is **one** small read-only Oracle A1 or Google e2-micro test host, not simultaneous signups or duplicate always-on servers.

## Licensing: separate Apache-2.0 target from existing GPLv3 root

The repository's root `LICENSE` currently carries the **GNU GPL version 3**. We must not rewrite it, strip notices or announce an Apache-2.0 relabeling based on a target preference. Apache-2.0 **original, independently licensed components** are a possible future sidecar. Review copyright and individual files/dependencies before packaging or combining. GPLv3 code cannot simply be imported into a distributed Apache-2.0-only whole; independent programs communicating over ordinary process boundaries often have different licensing consequences from combining source or linking. Keep RetroArch/libretro core licenses, Kodi, Plex proprietary binaries, third-party game assets and Android vendor drivers **outside LuHm core licensing claims** until specifically reviewed.

## Machine-proof loop, never false green

The auditor computes per-file SHA-256, validates schema and rights, parses YAML with duplicate-key rejection, creates actual SQLite STRICT tables **only in memory**, inspects the existing MariaDB DDL as text and cross-checks the existing Render/network/Cloudflare Canon. It exposes source-only MCP `luhm_forge_alignment_status` and `luhm_forge_vm_plan` as candidates. Source status is never live VM state.

The next physical test requires a known private VM target identity, source SHA, free-tier account and cost guard, approved machine snapshot, native console access, actual NIC readout, SSH host authenticity, private transport proof, and separate owner approval before any mutation. Company agent quarantine remains in force; no model-powered worker can self-promote. The final owner remains the Professor.

## Primary upstream references

- Netplan official manual and safe trial: https://netplan.io/ and https://github.com/canonical/netplan/blob/main/doc/netplan-try.md
- Cloudflare Tunnel: https://developers.cloudflare.com/tunnel/
- Apache license compatibility: https://apache.org/licenses/GPL-compatibility.html
- GitHub plans/CI limits: https://github.com/pricing
