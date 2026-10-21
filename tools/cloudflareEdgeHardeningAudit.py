#!/usr/bin/env python3
"""Read-only source and optional public edge probe for Cloudflare LuHm OS.

Default is local policy assertions only. --live invokes bounded DNS/TLS checks
for public domains; it never connects to private .lan, Cloudflare account APIs,
tunnels, SSH, databases, or runs cloudflared/certbot/terraform.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import socket
import ssl
import subprocess
from urllib.request import urlopen

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"doctrine/cloudflareEdgeHardeningV1.json"


def audit(data: dict) -> list[str]:
    problems=[]
    def need(condition: bool, label: str) -> None:
        if not condition: problems.append(label)
    need(data.get("schema")=="luhmOs.cloudflareEdgeHardening.v1","schema")
    need(data.get("authority")=="Professor","owner")
    need(data.get("status")=="CANONICAL_SOURCE_POLICY_ONLY","policyNotRuntime")
    need(data.get("canonicalZone")=="eggiebagelface.art","zone")
    for p in data.get("inherits",[]):
        resolved=(ROOT/p).resolve()
        need(resolved.is_relative_to(ROOT) and resolved.is_file(),"missingContract:"+str(p))
    a=data.get("authorityAndDelegation",{})
    for field in ("preserveExistingRegistrarDelegation","noSelfHostedNameserverFleet",
                  "noReversePtrForSharedRenderOrCloudflareIp","noPublicLanSuffix",
                  "noRawWanIpToLan","noRouterPortForwarding","noInferredIpv6Aaaa"):
        need(a.get(field) is True,"network:"+field)
    need(a.get("existingProvider")=="Cloudflare","provider")
    need(a.get("currentAssignedNsHostnames")=="LIVE_PROVIDER_LOOKUP_REQUIRED","nameserverUnknown")
    lanes=data.get("lanes",{})
    need(set(lanes)=={"chatGptMcp","privateSystemPortal","publicAssets","androidFdroid","apexAndLegacy"},"fiveLanes")
    mcp=lanes.get("chatGptMcp",{})
    need(mcp.get("activeOrigin")=="https://luhm-os-harness-green.onrender.com/mcp","mcpOrigin")
    need(mcp.get("activeTransport")=="directRenderManagedTls","directMcp")
    need(mcp.get("plannedCloudflareProxy") is False and
         mcp.get("plannedCloudflareTunnel") is False and mcp.get("noCache") is True,
         "mcpProxyOrCache")
    private=lanes.get("privateSystemPortal",{})
    for k in ("zeroTrustAccessRequired","defaultDeny","originTlsVerify",
              "noPortForward","cloudflaredValidateAccessJwt"):
        need(private.get(k) is True,"portal:"+k)
    need(private.get("currentTunnelState")=="NOT_VERIFIED","tunnelClaim")
    assets=lanes.get("publicAssets",{})
    need(assets.get("externalCdnState")=="NOT_VERIFIED","cdnClaim")
    need(assets.get("noPrivateArt") is True and assets.get("noCredentials") is True,"cdnPrivate")
    need(lanes.get("androidFdroid",{}).get("noAutomaticPublication") is True,"fdroidPublish")
    tls=data.get("tls",{})
    need(tls.get("modeWhenCloudflareProxied")=="FullStrict","strictTls")
    for k in ("privateKeysInGithub","privateKeysInAndroid","allowNoTlsVerify",
              "noHstsPreloadByDefault"):
        need(tls.get(k) is (k=="noHstsPreloadByDefault"),"tls:"+k)
    need(data.get("reverseProxy",{}).get("noExposeLanThroughPublicDns") is True,"proxyLeak")
    cache=data.get("cdn",{})
    need(cache.get("onlyForProxiedStaticPublicAssets") is True,"cdnScope")
    need(cache.get("immutablePublicHashedOnly") is True,"cdnImmutable")
    need(cache.get("noCacheAuthOrPersonalData") is True,"cdnSecrets")
    need(cache.get("cacheRulesNotEffectiveOnDnsOnlyHosts") is True,"cacheRuleTruth")
    need("/mcp" in cache.get("bypassPaths",[]) and
         cache.get("bypassAuthorizationAndSetCookie") is True,"mcpCacheBypass")
    for k in ("accountZoneRead","currentNsDelegation","liveDnsRecords",
              "liveDnssec","liveTlsCerts","liveCloudflareTunnel",
              "liveZeroTrustAccessPolicies","liveCdnCacheRules"):
        need(data.get("evidence",{}).get(k) in
             ("UNVERIFIED","NOT_AVAILABLE_IN_THIS_CHAT"),"runtimeEvidence:"+k)
    for name,permission in data.get("changes",{}).items():
        need(permission is False,"unexpectedLiveMutation:"+name)
    need(data.get("crownStatus")=="STOP_FOR_NETWORK_CHANGES","crown")
    return problems


def self_test(base: dict) -> None:
    assert not audit(base),audit(base)
    scenarios=[
      ("dangerousProxy",lambda x:x["lanes"]["chatGptMcp"].update(plannedCloudflareProxy=True)),
      ("insecureOrigin",lambda x:x["tls"].update(allowNoTlsVerify=True)),
      ("openLan",lambda x:x["authorityAndDelegation"].update(noRouterPortForwarding=False)),
      ("cacheMcp",lambda x:x["cdn"].update(bypassPaths=[])),
      ("unknownAsGreen",lambda x:x["evidence"].update(liveDnsRecords="GREEN")),
      ("claimPermission",lambda x:x["changes"].update(mayMutateCloudflareZone=True)),
      ("portalPublic",lambda x:x["lanes"]["privateSystemPortal"].update(defaultDeny=False)),
    ]
    for name,mutation in scenarios:
        new=copy.deepcopy(base)
        mutation(new)
        assert audit(new),"FAILED_NEGATIVE_CONTROL:"+name
    print("GREEN_CLOUDFLARE_EDGE_SOURCE_7_NEGATIVE_CONTROLS")
    print("NOT_PROVEN: registrar, NS, DNSSEC, certificate, CDN, WAF, Tunnel, Access, host plugin")


def dns_query(host: str, kind: str, resolver: str) -> dict:
    tool=shutil.which("dig")
    if not tool:
        return {"status":"UNVERIFIED_DIG_MISSING"}
    try:
        process=subprocess.run([tool,"+time=3","+tries=1","+short",
                                "@"+resolver,host,kind],
                               capture_output=True, text=True, timeout=6, check=False)
        if process.returncode:
            return {"status":"QUERY_FAILED","kind":kind,"resolver":resolver}
        # Only public DNS names / record values, no local resolver files.
        answers=[x.strip()[:300] for x in process.stdout.splitlines() if x.strip()]
        return {"status":"OBSERVED_RECURSIVE_ONLY","answers":answers[:15]}
    except (OSError, subprocess.TimeoutExpired):
        return {"status":"UNVERIFIED_TIMEOUT"}


def tls_probe(host: str) -> dict:
    try:
        ctx=ssl.create_default_context()
        with socket.create_connection((host,443),timeout=5) as sock:
            with ctx.wrap_socket(sock,server_hostname=host) as secure:
                cert=secure.getpeercert()
                chain_bytes=secure.getpeercert(binary_form=True)
                return {"status":"TLS_VALIDATED_BY_SYSTEM_CA",
                        "hostname":host,"tlsVersion":secure.version(),
                        "issuer":cert.get("issuer"),
                        "notBefore":cert.get("notBefore"),
                        "notAfter":cert.get("notAfter"),
                        "san":cert.get("subjectAltName",[])[:12],
                        "fingerprintSha256":hashlib.sha256(chain_bytes).hexdigest()}
    except (OSError,ssl.SSLError,TimeoutError) as e:
        return {"status":"UNVERIFIED_TLS_PROBE_FAILED","reason":type(e).__name__}


def live_probe(policy: dict) -> None:
    zone=policy["canonicalZone"]
    # These queries do not prove parent delegation. A current Cloudflare zone
    # dashboard and registrar record remain necessary for authoritative proof.
    dns={kind:{res:dns_query(zone,kind,res) for res in ("1.1.1.1","8.8.8.8")}
         for kind in ("NS","SOA","DS","CAA")}
    target=policy["lanes"]["chatGptMcp"]["activeOrigin"]
    assert target=="https://luhm-os-harness-green.onrender.com/mcp"
    report={
        "schema":"luhmOs.cloudflareReadOnlyProbe.v1",
        "sourceStatus":"SOURCE_ONLY",
        "dns":dns,
        "mcpOriginTls":tls_probe("luhm-os-harness-green.onrender.com"),
        "notProven":["cloudflareAccountAuthority","tunnelState",
                     "accessPolicy","cdnCacheRules","inChatCockpit",
                     "registrationOrApexDnsChange"],
        "liveMutation":False
    }
    print(json.dumps(report,indent=2))


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--live",action="store_true",
                        help="opt in to bounded read-only public DNS/TLS probes")
    args=parser.parse_args()
    policy=json.loads(PATH.read_text(encoding="utf-8"))
    errors=audit(policy)
    if errors:
        print("RED_CLOUDFLARE_EDGE_SOURCE",errors)
        raise SystemExit(2)
    self_test(policy)
    if args.live:
        live_probe(policy)


if __name__=="__main__":
    main()
