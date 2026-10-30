# Network-to-kernel 4x4 hardening gate (source-only)
Date: 2026-10-30. Candidate branch only. No host network commands executed.

| Layer | Local Linux | Raspberry Pi | Remote VM | AI/studio |
|---|---|---|---|---|
| Kernel | NIC/driver, nftables | onboard/USB NIC, firmware | virtio NIC, routes | network namespace |
| Config | Netplan or NetworkManager/systemd-networkd | distro-specific manager | cloud-init/provider routes | service endpoints |
| Trust | OpenSSL/TLS trust store | device keys, least privilege | OpenVPN and cert rotation | scoped service credentials |
| Traffic | local reverse proxy | edge discovery | health-checked load balancer | bounded queues/retries |

## Read-only inventory
On a specifically approved Linux host only:
```sh
uname -r
ip -brief link
ip route show
ip -6 route show
resolvectl status
ss -lnt
openssl version -a
openvpn --version
netplan --version
systemctl --failed --no-pager
```
Missing binaries are UNKNOWN, not FAIL. Redact IP addresses, interfaces, certificate paths and hostnames from public receipts.

## Safety and reduction
Never run `netplan apply`, modify firewall, restart VPN, rotate certificates, flash NIC firmware, or alter load-balancer upstreams without out-of-band console access and an explicit rollback. Prefer the existing distro network manager; don't layer Netplan, NetworkManager and systemd-networkd as competing owners. Use OpenVPN only where an actual tunnel requirement exists. Prefer a single existing reverse proxy/LB instead of stacking Apache, nginx, Traefik and bespoke Go gateways. Record chosen owner and version before removing anything.

## Tests
Synthetic contract fixtures for disconnected DNS, route mismatch, expired cert, wrong trust root, VPN down, unreachable upstream, partial LB health, retry storm, interface rename, and clock skew. Verify fail-closed privileged routes, bounded retries, stable read-only health, idempotent receipts, and rollback plan. Test load balancer on isolated fixtures, never production endpoints.

## Release gates
Require exact SHA CI, host-specific inventory, kernel/driver provenance, config owner, secret-safe receipt, rollback demonstration, and separate approval for network mutation and production deployment. Do not claim connectivity or firmware readiness from documentation.

## Upstream
https://netplan.readthedocs.io/
https://openvpn.net/community-resources/reference-manual-for-openvpn-2-6/
https://docs.openssl.org/
https://docs.kernel.org/networking/
https://www.freedesktop.org/software/systemd/man/latest/systemd-networkd.service.html
https://docs.nginx.com/nginx/admin-guide/load-balancer/http-load-balancer/
