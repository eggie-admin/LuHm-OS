---
name: luhm-wms-virtual-manager
description: Route the Professor's ChatGPT cockpit requests for remote WMS virtual machines and hardware/software plugin slots through canonical, read-only, evidence-bound plans.
---

# Remote WMS manager cockpit (candidate)

Use when the Professor describes ChatGPT connecting to a remote WMS virtual manager, a VM or its devices, or wishes to plug in hypervisors, guest OS tools and studio hardware.

- Read `doctrine/remoteWmsMachineBridgeV1.json`, `doctrine/remoteWmsPluginSlotsV1.json`, `doctrine/currentSourceTruthV3.json`, `doctrine/everlastingCovenantV1.json`, `doctrine/companyWideOperationalQuarantineV1.json`, and `doctrine/storageTopologyV1.json` before interpreting machine state.
- "WMS" is the Professor's working name for a remote manager. Do **not** assert vendor, protocol, address, installed VM, guest OS, or credentials unless there is a current verified receipt.
- The established hierarchy is ChatGPT in-chat UI → existing LuHm MCP host → Lum Canon/policy → host-only WMS adapter → registered guest VM → separately approved devices. GitHub remains source authority; Google Drive is the durable binary archive.
- `luhm_wms_status` describes planning capabilities and plugin slots, never a live VM inventory.
- `luhm_wms_plan` accepts explicit taskId + exact 40-character sourceRef + scopeId + opaque machineId + allowlisted operation. For manager-wide inventory/capabilities use machineId `manager`. The planning tool has **no** network or execution capability.
- A valid plan, source checks, registered roles or apparently available MCP tool never imply machine login, real VM inventory, active workers, model billing, GUI mount, remote execution, or Crown.
- No remote shell, arbitrary URL, secrets in user prompts/repo/browser, auto plugin installation, public port exposure, VM power writes or agent unquarantine.
- Respect Canon's four beats (hear, resolve, act, verify), escalating tiers only for evidence. Stop on unregistered target, mismatched source, absent transport/auth receipt or separate authorization.
- When a real provider/host becomes known, add its narrow read-only driver behind a verified server-side authentication and TLS boundary, validate on a disposable test VM, and open a separate reviewable PR before any privileged actions.

Current state: proposal/implementation only. No WMS vendor or guest VM has been connected or remotely operated.
