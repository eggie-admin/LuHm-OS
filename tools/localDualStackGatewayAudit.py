#!/usr/bin/env python3
"""Source-only cross-platform, DNS, PKI and SQL hardening consistency gate."""
from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
POLICY="doctrine/localDualStackGatewayV1.json"

def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

def audit(p, *, check_files=True):
    problems=[]
    def need(ok, label):
        if not ok:
            problems.append(label)
    if check_files:
        for path in p.get("inherits",[]):
            need((ROOT/path).is_file(), "missing_existing_canon:"+path)
        need((ROOT/p.get("dns",{}).get("dynamicUpdate",{}).get("proposedSourceTool","")).is_file(), "missing_dry_run")
    need(p.get("schema")=="luhmOs.localDualStackGateway.v1", "schema")
    need(p.get("status")=="FINAL_MUTATION_SOURCE_CANDIDATE_ONLY", "source_only")
    need(p.get("authority")=="Professor", "authority")
    need(p.get("sourceCanon",{}).get("snapshotSourceRef")=="5eb8388e7309cef4c90ff5fb8a854bbc11907acf", "frozen_rollback")
    need(p.get("sourceCanon",{}).get("snapshotBranch")=="snapshot/pre-final-mutation-20261107-5eb8388e", "snapshot_identity")
    need(p.get("sourceCanon",{}).get("candidatePr")==537, "one_existing_pr")
    platforms=p.get("platformAdapters",{})
    need(set(platforms)=={"androidSamsung","samsungDebian","ios","debianGateway"}, "platforms")
    android=platforms.get("androidSamsung",{})
    need(android.get("hardwareAuthority")=="Samsung OEM and Android platform" and android.get("bootloaderOrFirmwareMutation") is False, "android_oem")
    need(android.get("useAndroidKeystoreForClientSecrets") is True and android.get("persistedPrivateTlsKey") is False, "android_no_tls_key")
    samsung=platforms.get("samsungDebian",{})
    for field in ("isReplacementAndroidKernel","requiresRoot","publicTlsTerminationByDefault","dynamicDnsSchedulerByDefault"):
        need(samsung.get(field) is False, "samsung:"+field)
    need(samsung.get("stableAlwaysOnHostPreferred") is True and samsung.get("shizukuIsNotRootOrHostAuthority") is True, "debian_android_boundary")
    ios=platforms.get("ios",{})
    need(ios.get("iOSKernelModification") is False and ios.get("backgroundDnsDaemon") is False and ios.get("useKeychainForClientTokens") is True, "ios_client_not_server")
    host=platforms.get("debianGateway",{})
    for field in ("actualHostVerified","osInstalledVerified","localHostnameKnown","systemdActivation","cloudflaredInstalledVerified"):
        need(host.get(field) is False, "unproved_host:"+field)
    dns=p.get("dns",{})
    need(dns.get("zone")=="eggiebagelface.art", "existing_zone")
    mcp=dns.get("existingMcp",{})
    need(mcp.get("fqdn")=="mcp.eggiebagelface.art" and mcp.get("proxyChange") is False and mcp.get("preserveCurrentTransport") is True, "mcp_no_breakage")
    portal=dns.get("privatePortal",{})
    need(portal.get("fqdn")=="system.eggiebagelface.art" and portal.get("preferredMode")=="CLOUDFLARE_OUTBOUND_ONLY_TUNNEL", "tunnel_identity")
    for k in ("noAOrAaaaAtSameCnameOwner","cloudflareAccessOwnerMfa","noInboundRouterForwarding"):
        need(portal.get(k) is True, "portal:"+k)
    need(portal.get("installed") is False, "tunnel_not_activated")
    v6=dns.get("optionalDirectIpv6",{})
    need(v6.get("fqdn") is None and v6.get("state")=="UNSELECTED_DISABLED" and v6.get("recordKind")=="AAAA", "AAAA_not_guessed")
    for k in ("onlyGloballyRoutableUnicast","refuseLinkLocalUniqueLocalLoopbackDocumentationAndMulticast","publicExposureRequiresSeparateApproval","distinctFromTunnelCname"):
        need(v6.get(k) is True, "AAAA:"+k)
    need(v6.get("recordChangesDisabled") is True and v6.get("originPublicIpv6Observed") is False, "AAAA_not_live")
    v4=dns.get("optionalDirectIpv4",{})
    need(v4.get("fqdn") is None and v4.get("state")=="UNSELECTED_DISABLED" and v4.get("recordKind")=="A", "A_not_guessed")
    need(v4.get("noIpv4ToIpv6DnsRedirect") is True and v4.get("recordChangesDisabled") is True, "no_dns_redirect")
    dyn=dns.get("dynamicUpdate",{})
    need(dyn.get("execution")=="DRY_RUN_OFFLINE_ONLY" and dyn.get("automatedProviderWrites") is False and dyn.get("hostBackgroundService")=="NOT_INSTALLED", "no_automatic_ddns")
    need(dyn.get("tokenInRepo") is False and dyn.get("onlyAfterOwnedFqdnAndExactRecordIdAndSourceApproval") is True, "token_and_scope")
    tls=p.get("tls",{})
    need(tls.get("edgeModeWhenProxied")=="FullStrict" and tls.get("cloudflareEdgePublicCaManaged") is True, "edge_public_ca_strict")
    need(tls.get("tunnelOriginTls")=="PUBLIC_CA_VALIDATED_HTTPS" and tls.get("tunnelOriginSniName")==portal.get("fqdn"), "origin_certificate_name")
    need(tls.get("cloudflaredNoTlsVerify") is False and tls.get("selfSignedAllowed") is False and tls.get("originCaAsPublicBrowserTrust") is False, "no_untrusted_tls")
    for key in ("noPrivateKeyInGitHub","noPrivateKeyInSql","noPrivateKeyInChatGpt","noPrivateKeyInAndroid","noPrivateKeyInCloudflareDns","originKeyGeneratedOnApprovedHostOnly"):
        need(tls.get(key) is True, "no_key_leak:"+key)
    need(tls.get("certificateChainHostnameAndRenewalProof")=="PENDING" and tls.get("hstsPreload")=="NO_AUTOMATIC_CHANGE", "no_certificate_promotion")
    sql=p.get("sqlCrypto",{})
    need(sql.get("existingSqlModel")=="doctrine/typedFourLaneSqlV1.json" and sql.get("existingMachineRegistry")=="host/api/machineRegistrySqliteV1.sql", "no_second_sql")
    for key in ("newDatabase","migrationPerformed","sqlWriteAuthorized","providerApiTokensInSql"):
        need(sql.get(key) is False, "sql:"+key)
    need(sql.get("sqlNeverContainsPrivateKeys") is True and sql.get("hexIsEncodingNotEncryption") is True, "sql_crypto_boundary")
    need(sql.get("sqlEncryptionAtRest")=="NOT_PROVEN_SQLITE_DOES_NOT_ENCRYPT_AUTOMATICALLY", "no_fake_encryption")
    gates=p.get("liveGates",{})
    need(gates.get("crown")=="STOP", "crown")
    for key,value in gates.items():
        if key!="crown":
            need(value is False, "unapproved_live_action:"+key)
    need(len(p.get("completionProofRequired",[]))>=9, "runtime_proof_gate")
    if check_files:
        spine=load("doctrine/networkSpineV1.json")
        cloud=load("doctrine/cloudflareEdgeHardeningV1.json")
        q=load("doctrine/companyWideOperationalQuarantineV1.json")
        need(spine["lanes"]["publicChatPluginMcp"]["mode"]=="dnsOnlyRenderBootstrap", "mcp_Canon")
        need(spine["tls"]["noTlsVerify"] is False, "existing_tls_Canon")
        need(cloud["lanes"]["privateSystemPortal"]["currentTunnelState"]=="NOT_VERIFIED", "tunnel_unverified_Canon")
        need(cloud["tls"]["privateKeysInGithub"] is False and cloud["tls"]["allowNoTlsVerify"] is False, "cloudflare_policy_Canon")
        need(q["state"]=="QUARANTINED" and q["activeTaskWorkersAllowed"] is False, "agent_quarantine")
    return problems

def main():
    policy=load(POLICY)
    problems=audit(policy)
    if problems:
        raise SystemExit("RED_DUAL_STACK_POLICY: "+", ".join(problems))
    # Adversarial controls prove that a dangerous policy mutation fails the audit.
    mutation_paths=[
        ("liveGates","dnsUpdated",True),
        ("liveGates","finalProfessorApproval",True),
        ("liveGates","tunnelInstalled",True),
        ("tls","cloudflaredNoTlsVerify",True),
        ("tls","selfSignedAllowed",True),
        ("tls","noPrivateKeyInSql",False),
        ("sqlCrypto","newDatabase",True),
        ("sqlCrypto","sqlWriteAuthorized",True),
        ("dns","zone","attacker.invalid"),
        ("platformAdapters","ios",{}),
    ]
    for group,key,value in mutation_paths:
        dirty=deepcopy(policy)
        dirty[group][key]=value
        if not audit(dirty,check_files=False):
            raise AssertionError("unsafe mutation accepted: "+group+"."+key)
    from dynamicDnsDryRun import self_test
    self_test()
    print("GREEN_DUAL_STACK_SOURCE_ONLY_10_NEGATIVE_CONTROLS_CROWN_STOP")

if __name__=="__main__":
    main()
