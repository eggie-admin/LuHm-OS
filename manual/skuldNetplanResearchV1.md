# Skuld | Netplan Advanced Study Brief

**Brand:** LuHm-OS  
**Study owner (proposed):** Skuld  
**Research date:** 2026-10-25  
**Status:** RESEARCH_NOT_APPLIED  
**Scope:** upstream vendor documentation, version truth, advanced scenarios, and lessons for LuHm-OS. No live configuration changes.

## Version identity and correction

Ubuntu **26.04 LTS** is the long-term-support **operating-system** release. Ubuntu's 26.04 LTS release notes refer to Netplan **1.2**. The Canonical/Netplan upstream releases page currently identifies **Netplan v1.2.2** as latest. A separate release named "Netplan 1.26 LTS" was **not verified** in the surveyed official sources. Never infer installed package versions from documentation; query the target system when authorized.

Sources:
- https://documentation.ubuntu.com/release-notes/26.04/summary-for-lts-users/
- https://github.com/canonical/netplan/releases

## Netplan mental model

1. Declarative **YAML** describes network interfaces, DNS, routes, and virtual devices.
2. Backends are primarily **NetworkManager** and **systemd-networkd**; their support and behavior differ.
3. Netplan generates backend configuration from YAML; applying generated configuration is a distinct operation.
4. Netplan configuration namespaces and YAML keys are **external protocol contracts**. Keep their exact spelling, even if they differ from LuHm-OS internal camelHump.
5. **Layer precedence is not access control.** An overlay can override a base configuration. A configuration filename cannot by itself stop a privileged AI or process from writing another overriding file.

## File precedence (official `netplan-generate` rule)

- Scanned locations: `/lib/netplan/*.yaml`, `/etc/netplan/*.yaml`, and `/run/netplan/*.yaml` (some distributions expose vendor location as `/usr/lib/netplan`).
- **Same basename:** `/run` shadows `/etc`, which shadows the vendor location. The shadowed file is replaced as a whole for that name.
- **Different basenames:** all files are processed in lexical filename order **across directories**. Later files amend or override earlier settings.
- **Same key:** scalars are replaced; lists are concatenated; maps merge recursively.
- Example: a `20-admin.yaml` in `/etc/netplan` can amend `10-vendor.yaml` in `/lib/netplan`; `/run/netplan/10-vendor.yaml` can completely shadow the same-name vendor YAML. The numbers do not create an immutable boundary.
- Therefore a protected LuHm-OS baseline would require independent ownership/permissions, write restrictions, validation of the fully resolved result, and governance for overriding layers.

Source: https://netplan.readthedocs.io/en/stable/netplan-generate/

## Study catalogue: advanced official examples

| Study topic | What Skuld should learn and test in an isolated fixture |
| --- | --- |
| Multiple files / namespace layers | shadowing by identical basename, ordering across directories, scalar/list/map merges |
| Desktop renderer | NetworkManager compatibility, interface selection, WPA Personal and enterprise EAP-TLS |
| Source routing | routing tables and `routing-policy`; distinguish interface addresses from routes |
| VRF | multiple logical routing contexts, explicit tables, interface membership |
| VLANs and bridges | tagged VLANs, bridge membership, virtual machine host connectivity |
| Bonding | multi-interface aggregation and failure-domain behavior |
| WireGuard | tunnel, routing, external secrets, key-handling considerations |
| IPv6 | RA, SLAAC, DHCPv6, tunnels, deliberate handling of link-local addresses |
| SR-IOV | PF/VF relationships and restrictions; test only on hardware that supports it |
| Stable interface binding | `match:` by MAC address and `set-name:` caveats |
| API interaction | `netplan get`, `netplan status`, `netplan set --origin-hint`, and D-Bus API |
| VM host | single-NIC VM host, multi-NIC bonding, VLAN segmentation |
| Runtime and rollback | `netplan generate --root-dir`, `netplan try` (with independent recovery checks) |

Official guides and reference:
- https://netplan.readthedocs.io/en/stable/howto/
- https://netplan.readthedocs.io/en/stable/netplan-yaml/
- https://netplan.readthedocs.io/en/stable/netplan-tutorial/
- https://netplan.readthedocs.io/en/stable/netplan-set/
- https://netplan.readthedocs.io/en/stable/netplan-try/
- https://netplan.readthedocs.io/en/stable/netplan-generate/
- https://github.com/canonical/netplan/tree/main/examples
- https://wiki.debian.org/Netplan (cross-distro context; upstream documentation takes priority)

## Safety and security findings

- Official Netplan security guidance recommends root-owned YAML with mode `0600`. YAML can contain Wi-Fi passwords and VPN private keys.
- Netplan may emit systemd service units readable by unprivileged users; never place secrets into fields that can be reproduced in such units.
- `netplan try` usually reverts unconfirmed changes after 120 seconds, but upstream warns that rollback may be incomplete and must be verified. It is **not** a guaranteed recovery mechanism.
- `netplan generate` without isolated `--root-dir` writes backend configuration; it is not a completely inert lint action on the host. Use scratch-root fixtures for research.
- Do not deploy experimental Netplan configuration on the LuHm-OS/Mint workstation merely because the tutorial targets Ubuntu. First verify which networking stack actually owns the live connection.
- No direct file edits, `netplan set`, `netplan apply`, `netplan try`, `systemctl` network changes, or rollout is authorized by this study.

Sources:
- https://netplan.readthedocs.io/en/stable/security/
- https://netplan.readthedocs.io/en/stable/netplan-try/
- https://netplan.readthedocs.io/en/stable/netplan-generate/

## Proposed LuHm-OS adaptation (not Netplan-native capability)

Distinguish **ownership** from **merge precedence**:
- **Professor-owned baseline:** canonical identity, brand `LuHm-OS`, protected security contracts, and explicit review gates.
- **AI candidate overlay:** narrowly scoped proposals on a review branch, never an assumed higher-authority runtime layer.
- **Legacy archive:** existing nonconforming authored machine identifiers/files are classified `LEGACY` by the contract-selected namespace; never silently rewritten.
- **Contract exceptions:** upstream-mandated spellings, Netplan keys such as `access-points`, status `DRAGONTAIL` tokens, and repository slugs remain valid in their selected namespaces.
- **Resolver/auditor:** produce effective merged configuration, flag overrides of protected keys, compare to an exact-source approved baseline, report actionable drift.
- **Promotion boundary:** repository ruleset/CODEOWNERS where available, human approval, CI proof, service-specific permissions. A YAML declaration by itself is not a write-protection boundary.
- **Execution:** separate read/plan/validate from apply; no automatic network mutation, production signing, publication, Crown, or CAST dispatch.

## Evidence and handoff

This is a **Skuld-ready research brief**, not proof that the Skuld agent ran, studied, or validated the live workstation. Connected in-chat cockpit functions are read-only and cannot activate agents. Assign/ingest through an authorized agent runtime later if available. Preserve provenance and refresh upstream pages before implementing.

**Crown:** STOP. **Branch:** draft documentation only.
