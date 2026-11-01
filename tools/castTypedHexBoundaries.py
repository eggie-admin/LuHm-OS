#!/usr/bin/env python3
"""LuHm CAST typed boundary classifier: source-only, no kernel/network mutations."""
from __future__ import annotations
import argparse
import hashlib
import hmac
import ipaddress
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine/castTypedHexBoundariesV1.json"
HEX40 = re.compile(r"[0-9a-f]{40}\\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\\Z")
ROWS = ("firmwareTrust","kernelIsolation","networkScope","applicationCast")
COLS = ("identify","verify","enforce","escalate")
SOURCE_SYNTAX = 0x01
FIXTURE_DIGEST = 0x02
BOUNDARY_CLASS = 0x04
HUMAN_RELEASE = 0x08

class BoundaryError(ValueError):
    pass

def logical_cell(row: int, column: int) -> str:
    if type(row) is not int or type(column) is not int or not (0 <= row < 4 and 0 <= column < 4):
        raise BoundaryError("OUTSIDE_4X4")
    return f"0x{row*4+column:02X}"

def receipt_flags(source_ref: str, binary_fixture: bytes, expected_sha256: str, boundary: str) -> dict:
    if type(source_ref) is not str or HEX40.fullmatch(source_ref) is None:
        raise BoundaryError("GIT_SOURCE_40_HEX_REQUIRED")
    if type(binary_fixture) is not bytes or len(binary_fixture) > 4096:
        raise BoundaryError("SYNTHETIC_BYTES_ONLY")
    if type(expected_sha256) is not str or HEX64.fullmatch(expected_sha256) is None:
        raise BoundaryError("SHA256_DIGEST_64_HEX_REQUIRED")
    if boundary not in ROWS:
        raise BoundaryError("UNKNOWN_TYPED_BOUNDARY")
    if not hmac.compare_digest(hashlib.sha256(binary_fixture).hexdigest(), expected_sha256):
        raise BoundaryError("DIGEST_NOT_MATCHED")
    value = SOURCE_SYNTAX | FIXTURE_DIGEST | BOUNDARY_CLASS
    return {"auditFlags":f"0x{value:02X}","sourceSyntaxChecked":True,
            "syntheticBytesHashMatched":True,"boundaryClassified":True,
            "cryptographicSignatureVerified":False,"kernelPolicyEnforced":False,
            "firmwareWritten":False,"humanReleaseAuthorized":False,"crownStatus":"STOP"}

def ipv6_network(prefix: str) -> dict:
    if type(prefix) is not str or len(prefix) > 64 or "%" in prefix:
        raise BoundaryError("IPV6_PREFIX_BAD_FORMAT")
    try:
        net = ipaddress.ip_network(prefix, strict=True)
    except (ValueError, TypeError) as exc:
        raise BoundaryError("IPV6_PREFIX_BAD_FORMAT") from exc
    if not isinstance(net, ipaddress.IPv6Network):
        raise BoundaryError("IPV4_IS_NOT_IPV6")
    return {"cidr":str(net),"prefixLength":net.prefixlen,"addressBits":128,
            "securityAuthorization":False,"firewallConfigured":False,"routingProven":False}

def validate(config: dict, root: Path = ROOT) -> dict:
    if type(config) is not dict or config.get("schema") != "luhmOs.castTypedHexBoundaries.v1":
        raise BoundaryError("SCHEMA_DRIFT")
    if config.get("status") != "PROPOSED_SOURCE_ONLY" or config.get("crownStatus") != "STOP":
        raise BoundaryError("PROMOTION_DRIFT")
    if config.get("sourceLaw") != "AI proposes. Policy authorizes. CI proves. Human promotes.":
        raise BoundaryError("SOURCE_LAW_DRIFT")
    if config.get("namespace") != "castSecurityMatrixV1" or config.get("bytesOrFirmwareOffsets") is not False:
        raise BoundaryError("HEX_NAMESPACE_DRIFT")
    if config.get("hasLiveDeviceProof") is not False or config.get("activeAgentWorkers") != 0:
        raise BoundaryError("CLAIMED_RUNTIME_OR_AGENT_AUTHORITY")
    if any(config.get(k) is not False for k in ("mutationsPerformed","networkChanged","firmwareChanged")):
        raise BoundaryError("UNAUTHORIZED_MUTATION")
    rows=config.get("rows",[])
    if [r.get("id") for r in rows] != list(ROWS) or config.get("columns") != list(COLS):
        raise BoundaryError("FOUR_AXES_DRIFT")
    for row in rows:
        p=row.get("canon")
        if type(p) is not str or p.startswith("/") or ".." in Path(p).parts or not (root/p).is_file():
            raise BoundaryError("CANON_PATH_MISSING")
        if row.get("liveProof") is not False or type(row.get("evidence")) is not str:
            raise BoundaryError("FALSE_PROOF_CLAIM")
    cells=config.get("matrix",[])
    if len(cells) != 16:
        raise BoundaryError("MATRIX_SIZE")
    for i,c in enumerate(cells):
        if (c.get("index") != i or c.get("hex") != logical_cell(i//4,i%4)
            or c.get("row") != ROWS[i//4] or c.get("column") != COLS[i%4]
            or c.get("canon") != rows[i//4]["canon"] or c.get("status") != "SOURCE_ROUTE_ONLY"):
            raise BoundaryError("MATRIX_CELL_DRIFT")
    if config.get("levels") != [
        {"name":"4x4","logicalCells":16,"sourceMapped":16,"runtimeVerified":0},
        {"name":"8x8","logicalCells":64,"sourceMapped":0,"runtimeVerified":0},
        {"name":"16x16","logicalCells":256,"sourceMapped":0,"runtimeVerified":0},
        {"name":"0to2048","logicalCells":2048,"sourceMapped":0,"runtimeVerified":0}
    ]:
        raise BoundaryError("FALSE_SCALE_COVERAGE")
    flags=config.get("flags",{})
    wanted={"sourceSyntax":"0x01","fixtureDigestMatches":"0x02",
      "boundaryClassified":"0x04","humanRelease":"0x08","sourceOnlyMaximum":"0x07"}
    if any(flags.get(k) != v for k,v in wanted.items()) or flags.get("humanReleaseCannotBeSetByThisModule") is not True:
        raise BoundaryError("FLAG_AUTHORITY_DRIFT")
    typed=config.get("typedIdentities",{})
    if typed.get("ecdsa") != "DigitalSignatureAlgorithmNotEscalationSystem":
        raise BoundaryError("ECDSA_MISINTERPRETATION")
    if typed.get("ipv6") != "128BitAddressAndCIDRPrefix":
        raise BoundaryError("IPV6_MISINTERPRETATION")
    integ=config.get("integrity",{})
    if (integ.get("sha256DigestIsSignature") is not False
        or integ.get("signatureNeedsVerifiedSignerKeyAndAlgorithm") is not True
        or integ.get("ecdsaImpliesAuthorization") is not False
        or integ.get("gitShaDoesNotProveDeployment") is not True):
        raise BoundaryError("SIGNATURE_CONFLATION")
    network=config.get("network",{})
    if (network.get("ipv6PrefixDoesNotAuthorizeTraffic") is not True or
        network.get("noFirewallWrites") is not True or
        network.get("noUnverifiedAAAA") is not True):
        raise BoundaryError("IPV6_AUTHORIZATION_CONFLATION")
    for cidr in ("2001:db8::/32","::1/128","fe80::/10"):
        if ipv6_network(cidr)["securityAuthorization"] is not False:
            raise BoundaryError("PREFIX_IS_NOT_FIREWALL")
    debian=config.get("debian",{})
    for field in ("declaredSource","packageAuthority"):
        p=debian.get(field)
        if type(p) is not str or p.startswith("/") or ".." in Path(p).parts or not (root/p).is_file():
            raise BoundaryError("DEBIAN_PROVENANCE_PATH")
    if any(debian.get(k) is not True for k in ("kernelIsCodespacesHostNotContainer","noPackageAutoInstall","noDriverAutoBind")):
        raise BoundaryError("DEBIAN_KERNEL_ROLE")
    if config.get("quarantineRef") != "doctrine/companyWideOperationalQuarantineV1.json":
        raise BoundaryError("QUARANTINE_SOURCE")
    quarantine=json.loads((root/config["quarantineRef"]).read_text(encoding="utf-8"))
    if quarantine.get("state") != "QUARANTINED" or quarantine.get("activeTaskWorkersAllowed") is not False:
        raise BoundaryError("QUARANTINE_DISABLED")
    forbidden=set(config.get("prohibited",[]))
    if not {"flashFirmware","modifySelinuxPolicy","loadKernelModule","applyFirewall","openIpv6Port",
        "installPackage","autoMerge","signRelease","activateAgents","autoCrown"}.issubset(forbidden):
        raise BoundaryError("MISSING_STOP_ACTION")
    return {"schema":"luhmOs.castTypedHexBoundaryReceipt.v1","status":"AMBER_SOURCE_ONLY",
        "cellsMapped":16,"planned8x8RuntimeVerified":0,"planned16x16RuntimeVerified":0,
        "activeWorkers":0,"firmwareWrites":0,"networkWrites":0,"signedRelease":False,
        "crownStatus":"STOP"}

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    config=json.loads(CONTRACT.read_text(encoding="utf-8"))
    receipt=validate(config)
    synthetic=b"CAST_SOURCE_ONLY"
    check=receipt_flags("f0cb6ee54066b490c0e80efc2c96200fec76ee2d",
      synthetic,hashlib.sha256(synthetic).hexdigest(),"applicationCast")
    receipt["syntheticFlagBits"]=check["auditFlags"]
    receipt["ipv6DocumentationPrefix"]=ipv6_network("2001:db8::/32")["cidr"]
    if args.self_test:
        assert receipt["syntheticFlagBits"]=="0x07"
        assert check["humanReleaseAuthorized"] is False
    print(json.dumps(receipt,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
