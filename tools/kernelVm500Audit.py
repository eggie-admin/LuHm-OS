#!/usr/bin/env python3
"""LuHm-OS 500-slot kernel-to-app readiness matrix: five targets, 100 distinct controls each.

Only the GitHub-hosted runner is probed. All unconnected devices and cloud VMs
remain UNVERIFIED. No root, package install, cloud SDK or network side effect.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
import platform
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
LAYERS = {
    "kernelHost": """linuxKernel kernelReleaseObserved architectureObserved procFilesystemMounted
    sysFilesystemMounted operatingSystemRelease kernelBootParameters cgroupVersionObserved
    namespacesSupported seccompObserved apparmorStatusObserved selinuxStatusObserved
    addressSpaceRandomization kernelPointerRestriction kernelDmesgRestriction
    unprivilegedBpfRestriction protectedSymlinks protectedHardlinks protectedFifos
    protectedRegularFiles userNamespacePolicy kernelModuleLoadPolicy moduleSignaturePolicy
    securityUpdatesEvidence ntpTimeSyncEvidence""".split(),
    "networkDns": """loopbackInterface ipv4RouteInventory ipv6PolicyInventory noPublicDnsListener
    bind9OptionsPrivate bind9RecursionDisabled bind9ZonePrivate bind9NoZoneTransfers
    bind9NoDynamicUpdates bind9ZoneSyntax dnsmasqLoopback dnsmasqNoDhcp
    dnsmasqPortSeparated dnsmasqNoPublicBind dnsmasqBoundedCache noOpenResolver
    cloudflarePublicAuthority registrarDelegationPreserved dnssecStateObserved
    dnsARecordTargetProof mcpTlsEndpointProof apiReverseProxyBounded
    firewallOnlyExpectedPorts egressBudgetProof publicIpv4CostProof""".split(),
    "headlessRuntime": """pythonInterpreter pythonSslModule sqlite3Module sqliteVersion
    sqliteStrictTables sqliteParameterizedQueries userServicesNoRoot systemdConfigValidated
    noDaemonOnImport loopbackApiSmoke healthResponse postRejected corsDisabled
    memoryBudget diskBudget cpuBudget sqliteBackupPlan offVmRestoreProof
    logRotation secretStoreProvider secretRedaction cloudCallsDisabled
    blenderOptional npmBuildOnly serviceRestartPolicy""".split(),
    "appAndProviders": """sourceShaBound githubCiExactSource gpartedOperatorOnly
    androidVendorGkiPreserved shizukuOptional shizukuConsent raspberryArmBuild
    googleE2MicroFreeShape googleBillingUnknown googleIpv4Cost oracleA1FreeShape
    oracleIdleReclaim oracleCapacityUnknown oracleHomeRegion renderSidecarPreserved
    huggingFaceBaselineNotDeleted openAiAdapterOptional mcpAuthReady
    googleDrivePrivateArchive noAiModelBundled agentQuarantine crownStop
    fourLayerComposition fourBeatRhythm fourTierEscalation""".split(),
}
TARGETS = ("githubActionsRunner", "googleE2Micro", "oracleA1", "raspberryPi", "samsungAndroid")

def policy_failures(policy, files):
    e = []
    def need(ok, why):
        if not ok: e.append(why)
    m = policy["matrix"]
    need(len(LAYERS) == 4 and all(len(c) == 25 and len(set(c)) == 25 for c in LAYERS.values()), "100_DISTINCT_CONTROLS")
    need(m["totalAssessmentSlots"] == 500 and m["assessmentsPerTarget"] == 100, "500_SLOTS_REQUIRED")
    need(m["auditTargets"] == list(TARGETS), "TARGETS_MUST_REMAIN_EXPLICIT")
    need(m["auditLayers"] == list(LAYERS), "FOUR_LAYERS_REQUIRED")
    need(m["composition"] == ["coreLibrary","pluginExtension","classWidgetOrganization","stubAdapterBoundary"], "FOUR_LAYER_COMPOSITION")
    need(m["escalation"] == [0,1,2,3] and m["rhythm"] == ["hear","resolve","act","verify"], "FOUR_BEATS_AND_TIERS")
    g = policy["provider"]["google"]
    o = policy["provider"]["oracle"]
    need(g["publicIpv4Billed"] is True and g["budgetWarningNotHardCap"] is True, "GOOGLE_BILLING_MUST_NOT_BE_CALLED_FREE")
    need(g["ramGiB"] == 1 and g["standardDiskGbMonth"] == 30 and g["eligibleEgressGbMonth"] == 1, "GOOGLE_FREE_TIER_SOURCE_CHANGED")
    need(g["defaultDeploy"] == "DENY", "GOOGLE_DEPLOY_DENIED")
    need(o["nominalFullMonthOcpu"] == 2 and o["nominalFullMonthRamGb"] == 12, "ORACLE_FREE_TIER_MUST_USE_CURRENT_LIMIT")
    need(o["idleReclamationPossible"] is True and o["defaultDeploy"] == "DENY", "ORACLE_RECLAMATION_OR_DEPLOY_GATE")
    need(o["accountCapacity"] == "UNKNOWN_HOME_REGION", "ORACLE_AVAILABILITY_NOT_PROVEN")
    dns = policy["dns"]
    need("Cloudflare" in dns["publicAuthoritative"] and dns["noOpenResolver"] is True, "PRESERVE_PUBLIC_DNS_AND_NO_OPEN_RESOLVER")
    need(dns["bind9"]["recursive"] is False and dns["bind9"]["publicPort53"] is False, "BIND_MUST_BE_PRIVATE")
    need(dns["dnsmasq"]["androidAppEmbedded"] is False and dns["dnsmasq"]["publicPort53"] is False, "DNSMASQ_NOT_IN_ANDROID")
    named = files["named"]
    opts = files["options"]
    zones = files["zones"]
    dhcp = files["dnsmasq"]
    need('include "/etc/bind/named.conf.options";' in named and 'include "/etc/bind/named.conf.local";' in named, "BIND_INCLUDES")
    need("recursion no;" in opts and "127.0.0.1;" in opts and "listen-on-v6 { none; };" in opts, "BIND_LOOPBACK_AND_RECURSION")
    need("allow-query { any;" not in opts and "0.0.0.0" not in opts, "BIND_NO_WILDCARD")
    need('zone "vm.luhm.test"' in zones and "allow-transfer { none; };" in zones and "allow-update { none; };" in zones, "PRIVATE_ZONE_LOCK")
    need("listen-address=127.0.0.1" in dhcp and "port=5353" in dhcp and "bind-interfaces" in dhcp, "DNSMASQ_LOOPBACK")
    need("dhcp-range" not in dhcp and "port=53\n" not in dhcp, "DNSMASQ_NO_DHCP_NO_PORT53")
    need("server=/vm.luhm.test/127.0.0.1#53" in dhcp, "DNSMASQ_PRIVATE_FORWARD")
    sec = policy["security"]
    need(all(sec[k] is False for k in ("createCloudResources", "createBillingAccount", "chargeableCalls", "openInboundDns", "turnOffCloudflare", "unquarantineAgents", "deployOrPublish")), "NO_MUTATION_OR_COST")
    need(sec["crownStatus"] == "STOP", "CROWN_STOP")
    return e

def read_policy_files(root=ROOT):
    p = json.loads((root / "doctrine/singleVmKernel500V1.json").read_text(encoding="utf-8"))
    prefix = root / "infra/single-vm"
    f = {
       "named": (prefix/"bind9/named.conf").read_text(encoding="utf-8"),
       "options": (prefix/"bind9/named.conf.options").read_text(encoding="utf-8"),
       "zones": (prefix/"bind9/named.conf.local").read_text(encoding="utf-8"),
       "dnsmasq": (prefix/"dnsmasq/k9000-lan-compat.conf").read_text(encoding="utf-8")
    }
    return p, f

def _sysctl_value(path, minimum):
    try:
        n = int(Path(path).read_text(encoding="utf-8").strip())
        return "PASS" if n >= minimum else "GAP"
    except (OSError, ValueError):
        return "UNVERIFIED"

def probe_runner():
    """Bounded read-only kernel and in-memory SQL tests on this runner, not on remote VMs."""
    evidence = {}
    def emit(layer, name, verdict, kind):
        evidence[(layer,name)] = (verdict, kind)
    linux = platform.system() == "Linux"
    emit("kernelHost","linuxKernel","PASS" if linux else "GAP","platform.system")
    emit("kernelHost","kernelReleaseObserved","PASS" if linux and platform.release() else "UNVERIFIED","platform.release")
    emit("kernelHost","architectureObserved","PASS" if platform.machine() else "UNVERIFIED","platform.machine")
    for name, path in (("procFilesystemMounted","/proc/self/mounts"),
                       ("sysFilesystemMounted","/sys/kernel"),
                       ("operatingSystemRelease","/etc/os-release"),
                       ("kernelBootParameters","/proc/cmdline"),
                       ("cgroupVersionObserved","/sys/fs/cgroup/cgroup.controllers")):
        emit("kernelHost", name, "PASS" if Path(path).exists() else "UNVERIFIED", "filesystem_presence")
    for name, path, minval in (
       ("addressSpaceRandomization","/proc/sys/kernel/randomize_va_space",2),
       ("kernelPointerRestriction","/proc/sys/kernel/kptr_restrict",1),
       ("kernelDmesgRestriction","/proc/sys/kernel/dmesg_restrict",1),
       ("unprivilegedBpfRestriction","/proc/sys/kernel/unprivileged_bpf_disabled",1),
       ("protectedSymlinks","/proc/sys/fs/protected_symlinks",1),
       ("protectedHardlinks","/proc/sys/fs/protected_hardlinks",1),
       ("protectedFifos","/proc/sys/fs/protected_fifos",1),
       ("protectedRegularFiles","/proc/sys/fs/protected_regular",1)
    ):
        emit("kernelHost",name,_sysctl_value(path,minval),"read_only_sysctl")
    emit("networkDns","loopbackInterface","PASS" if Path("/sys/class/net/lo").exists() else "UNVERIFIED","loopback_present")
    emit("headlessRuntime","pythonInterpreter","PASS" if sys.version_info >= (3,10) else "GAP","python_version")
    try:
        import ssl
        emit("headlessRuntime","pythonSslModule","PASS" if ssl.OPENSSL_VERSION else "GAP","ssl_version_present")
        with sqlite3.connect(":memory:") as db:
            version = sqlite3.sqlite_version_info
            emit("headlessRuntime","sqlite3Module","PASS","sqlite_connect")
            emit("headlessRuntime","sqliteVersion","PASS" if version >= (3,37,0) else "GAP","sqlite_version_min_strict")
            if version >= (3,37,0):
                db.execute("CREATE TABLE readiness (id TEXT PRIMARY KEY, value INTEGER NOT NULL) STRICT")
                db.execute("INSERT INTO readiness VALUES (?, ?)", ("one", 1))
                result = db.execute("SELECT value FROM readiness WHERE id = ?",("one",)).fetchone()
                emit("headlessRuntime","sqliteStrictTables","PASS","in_memory_sqlite")
                emit("headlessRuntime","sqliteParameterizedQueries","PASS" if result == (1,) else "GAP","in_memory_sqlite")
    except (ImportError, sqlite3.Error):
        pass
    return evidence

def assess(run_here=False):
    current = probe_runner() if run_here else {}
    rows=[]
    for target in TARGETS:
        for layer, controls in LAYERS.items():
            for name in controls:
                verdict, proof = current.get((layer,name),("UNVERIFIED","remote_runtime_or_manual_receipt_required")) if target == "githubActionsRunner" else ("UNVERIFIED","no_live_target_access")
                rows.append({"id":target+"/"+layer+"/"+name, "target":target,
                             "layer":layer, "control":name, "verdict":verdict, "evidence":proof})
    assert len(rows)==500 and len({r["id"] for r in rows})==500
    return rows

def audit(run_here=False):
    policy, files = read_policy_files()
    errors = policy_failures(policy,files)
    rows = assess(run_here=run_here)
    counts = dict(Counter(r["verdict"] for r in rows))
    return {"schema":"luhmOs.kernelVm500Receipt.v1", "sourcePolicyFailures":errors,
            "sourcePolicy":"PASS" if not errors else "RED",
            "verdict":"RED_SOURCE" if errors else "AMBER_REMOTE_VM_UNVERIFIED",
            "assessmentCount":len(rows),"uniqueControlDefinitions":sum(len(x) for x in LAYERS.values()),
            "targets":list(TARGETS),"counts":counts,"assessments":rows,
            "runnerOnly":run_here,"liveCloudInspection":False,"cloudResourcesCreated":False,
            "osUpgraded":False,"dnsChanged":False,"crownStatus":"STOP"}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runner-scope",action="store_true")
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    out=audit(args.runner_scope)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:out[k] for k in ("schema","sourcePolicy","sourcePolicyFailures",
                                        "verdict","assessmentCount","uniqueControlDefinitions",
                                        "counts","liveCloudInspection","crownStatus")},indent=2))
    return 2 if out["sourcePolicyFailures"] else 0

if __name__=="__main__":
    raise SystemExit(main())
