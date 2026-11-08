# LuHm-OS | Final infrastructure mutation: operator handoff

**State:** SOURCE CANDIDATE ONLY. Professor Crown **STOP**. Not installed, deployed, merged, or approved.

**Rollback anchor:** `snapshot/pre-final-mutation-20261107-5eb8388e`, exact SHA `5eb8388e7309cef4c90ff5fb8a854bbc11907acf`.
**Candidate:** draft PR #537. Canon source stays `eggie-admin/LuHm-OS`, and the existing machine SQL registry is a projection, never a second source authority.

## One safe traffic model

```text
Android Samsung/One UI (WebView)      iOS (WKWebView/ChatGPT)
                      \               /
                       Cloudflare public CA TLS (A/AAAA client reachability)
                                  |
                         Cloudflare Access + MFA
                                  |
                      outbound-only cloudflared Tunnel
                                  |
                  VERIFIED HTTPS (public CA; correct SNI)
                                  |
                    Debian host loopback origin / bounded app
                                  |
                   local-only SQL metadata + artifact pointers
```

The `system.eggiebagelface.art` private portal uses a **single Tunnel CNAME**, not colocated A/AAAA records. Cloudflare's edge can respond to IPv4 and IPv6 clients. **DNS is not an IPv4-to-IPv6 redirect**. Keep `mcp.eggiebagelface.art` on the existing Render DNS-only bootstrap until independently proven streaming and ChatGPT host behavior permit a change.

If the Professor later selects a *different* direct-origin hostname that genuinely needs public IPv6, a scoped AAAA may be dynamically updated by the **persistently running origin host**, but only after recording exact Cloudflare zone/record identity, verified public-unicast address provenance, DNS readback, service reachability, firewall review, certificate/renewal readiness, and explicit release approval. A real public IPv4 A record is optional only if an IPv4 origin actually exists. Never substitute a router's RFC1918 address or a phone's temporary IPv6 address. Never open SQL, private admin, shell, or other internal services publicly.

## Certificates and keys

- Use Cloudflare's publicly trusted **managed edge certificate** on proxied hostnames. Use **Full (strict)** where applicable.
- For the Tunnel's local `https://localhost:443` origin, use an independently validated **publicly trusted** certificate with SAN for `system.eggiebagelface.art`, and `originServerName` matching that hostname. Local Certbot/ACME DNS-01 and a least-privilege DNS challenge token are **operator-only**, not run by this proposal. `noTLSVerify=false`; refuse weak/self-signed/expired/untrusted certificates.
- The local private key is created and stays on the persistent approved origin or secret store with restrictive permissions. The public certificate, serial, expiry, issuer, SAN and certificate/SPKI SHA-256 fingerprints may be recorded in SQL. **Private key bytes and API tokens never enter SQL, GitHub, the ChatGPT Library, mobile bundles, logs or DNS records.**
- **Do not confuse** a Cloudflare Origin CA certificate (suitable for certain Cloudflare-to-origin cases) with a publicly trusted browser certificate. This candidate intentionally requires a publicly trusted origin certificate.
- Do not enable automatic HSTS preload before subdomain inventory, valid certs and Professor approval. Enforce HTTPS only once TLS is proven.

## Device adapters, not new kernels

- **Samsung Android core:** keep OEM boot chain and app sandbox; reuse `androidWeb3Plugin` SDK bridge, Android Keystore for client credentials, and actual physical-device WebView tests. No bootloader/firmware changes.
- **Samsung Debian:** optional Termux/proot Debian unprivileged **development environment**, not a replacement Android kernel, permanent server, root permission, or automatic DNS daemon. A genuinely always-on Debian/Linux machine is the recommended Tunnel and DDNS origin.
- **iOS:** supported ChatGPT client or WKWebView thin client, iOS Keychain for client tokens; Apple signing/entitlements and iPhone client testing remain separate. No assumption that iOS will reliably schedule a DDNS background service.
- **SQL and crypto:** existing SQLite machine/typed-lane metadata registry only. TLS public fingerprints and audit receipts are okay; signing keys, TLS private keys, and Cloudflare tokens are not. SQLite is **not automatically encrypted at rest**. Verify host disk encryption and backup access controls separately if required.

## Offline checks (do not contact Cloudflare)

```sh
python3 tools/localDualStackGatewayAudit.py
python3 tools/dynamicDnsDryRun.py --self-test
# Only for a FUTURE, approved distinct direct-origin hostname and a REAL observed global IPv6:
python3 tools/dynamicDnsDryRun.py --fqdn candidate.eggiebagelface.art --ipv6 '2606:4700:4700::1111'
```

The last line is only a syntax/example demonstration using Cloudflare's public resolver address, **not a record to install**. There is deliberately **no --apply flag** and no network API call. For genuine deployment, author a separately reviewed least-privilege updater with exact record-ID compare-and-swap/readback, retries/rate limit, alerting, secure token storage, system service installation and rollback, then approve it before activating anything.

## Professor's live gate

Review actual host identity, domain/zone ownership and current DNS, Tunnel health **and origin health**, Cloudflare Access policy, public CA chains, expiry/renewal, origin SNI, IPv4/IPv6 reachability, protected forwarded headers, no public port-forward, SQL socket restrictions and backup/restore proof. Confirm Samsung and any iOS client behavior. Independent source CI cannot substitute for this field evidence.

**Never merge, publish, enable cloud services, create private keys, change the router/DNS, or release agents from this source candidate alone.**
