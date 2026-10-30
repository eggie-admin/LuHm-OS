#!/usr/bin/env python3
"""Privacy-safe source preflight. Never prints suspected credential values."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
HIGH_CONFIDENCE = {
    "private_key_material": re.compile(r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----"),
    "github_token": re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b"),
    "openai_token": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{30,}\b"),
    "aws_access_id": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "google_api_key": re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
}
PRIVATE_PATH = re.compile(r"(?:^|/)(?:\.env(?:\..+)?|[^/]+\.(?:p12|pfx|pem|key)|id_rsa|id_ed25519)$", re.I)
BAD_WORKFLOW = re.compile(r"^\s*(?:pull_request_target:|permissions:\s*write-all\s*$)", re.I)


def scan_added_patch(patch: str) -> list[str]:
    """Only category names escape, never secret values, line excerpts or paths."""
    hits: set[str] = set()
    in_workflow = False
    for line in patch.splitlines():
        if line.startswith("diff --git "):
            in_workflow = ".github/workflows/" in line
            continue
        if line.startswith("+++ b/"):
            path = line[6:].strip()
            if PRIVATE_PATH.search(path):
                hits.add("private_file_added")
            continue
        if not line.startswith("+") or line.startswith("+++"):
            continue
        added = line[1:]
        for name, expression in HIGH_CONFIDENCE.items():
            if expression.search(added):
                hits.add(name)
        if in_workflow and BAD_WORKFLOW.search(added):
            hits.add("unsafe_workflow_trigger_or_permission")
    return sorted(hits)


def inspect(root=ROOT):
    policy = json.loads((root / "doctrine/dataProtectionLadderV1.json").read_text(encoding="utf-8"))
    quarantine = json.loads((root / "doctrine/companyWideOperationalQuarantineV1.json").read_text(encoding="utf-8"))
    stage = json.loads((root / "doctrine/castBridgeStageGateV1.json").read_text(encoding="utf-8"))
    social = (root / ".github/workflows/social-video-orchestrator.yml").read_text(encoding="utf-8")
    checks: dict[str, bool] = {}
    def ck(name, good): checks[name] = bool(good)
    ck("schema", policy.get("schema") == "luhmOs.dataProtectionLadder.v1")
    ck("fourDataClasses", set(policy.get("classes",{})) == {"publicApproved","internalStudio","restrictedPersonal","secretsSigning"})
    ck("localSyntheticException", policy["environments"]["basement"]["allowUnencryptedLocalDataOnly"] == "PUBLIC_APPROVED_OR_DISPOSABLE_SYNTHETIC_NON_IDENTIFYING")
    ck("restrictPrivateLocal", policy["classes"]["restrictedPersonal"]["localAtRest"] == "ENCRYPTED_STORAGE_AND_ACCESS_CONTROL_REQUIRED")
    ck("secretVault", policy["classes"]["secretsSigning"]["localAtRest"] == "OS_KEYSTORE_OR_SECRETS_VAULT_NOT_PLAINTEXT_PROJECT")
    ck("ltsBackups", policy["environments"]["lts"]["backupsEncryptedAndRestoreTested"] is True)
    ck("remoteTls", policy["api"]["remoteTransport"].startswith("HTTPS_TLS_1_3_PREFERRED"))
    ck("base64NotCrypto", policy["api"]["base64urlIsEncryption"] is False)
    ck("apiAuthz", policy["api"]["defaultDenyPrivateWrite"] is True and "EVERY_PRIVATE_OR_WRITE_REQUEST" in policy["api"]["authorization"])
    ck("corsAndCsrf", any("CSRF" in x for x in policy["api"]["requestSecurity"]) and any("CORS" in x for x in policy["api"]["requestSecurity"]))
    ck("noPrivateSql", policy["api"]["privateSqlAdminPublic"] is False)
    ck("quarantinePreserved", quarantine["state"] == "QUARANTINED" and quarantine["activeTaskWorkersAllowed"] is False and policy["agentAI"]["activeWorkersAllowed"] is False)
    ck("agentNoSelf", "selfAuthorization" in policy["agentAI"]["blocked"] and "unapprovedPrivateMediaUpload" in policy["agentAI"]["blocked"])
    ck("ownerCast", "EXACT_CURRENT_MAIN_SHA" in policy["github"]["ownerCast"] and stage["ownerCast"]["dispatchTriggered"] is False)
    ck("noProductionAutomation", policy["github"]["noProductionAutoMerge"] is True and policy["github"]["noProductionAutoDeploy"] is True)
    ck("privacyReportedNoIds", policy["privacy"]["observedMetadataOnly"] is True and policy["privacy"]["publicRepoMayContainPrivateDriveIds"] is False and policy["privacy"]["permissionMutationAuthorized"] is False)
    ck("teenFamilyIsolation", policy["privacy"]["familyAndAdultCatalogIsolation"].startswith("SERVER_SIDE_ACL"))
    ck("publishRequiresAclFix", "privateDocumentSharingFixedAndVerified" in policy["brandRelease"]["publicRequired"] and policy["brandRelease"]["publicPublish"] is False)
    ck("noFakeRuntime", all(x == "UNVERIFIED" for k,x in policy["runtimeProof"].items() if k in ("apiAuthorization","atRestEncryption","liveTls","renderDeployment","deviceCapture")))
    ck("stop", policy["crownStatus"] == "STOP")
    ck("socialPinnedCheckout", "actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09" in social and "actions/checkout@v4" not in social)
    ck("socialPinnedRunner", "runs-on: ubuntu-24.04" in social and "ubuntu-latest" not in social)
    ck("socialNoPersistentCredentials", "persist-credentials: false" in social)
    ck("socialLeastPrivilege", "contents: read" in social and "write-all" not in social)
    ck("socialExactHead", 'git rev-parse HEAD' in social and 'LUHM_SOURCE_REF' in social)
    failed = sorted(k for k,v in checks.items() if not v)
    return {"schema":"luhmOs.deepDungeonSecurityAudit.v1","checks":len(checks),"passed":len(checks)-len(failed),"failedCategories":failed,"stage":"SOURCE_POLICY_GREEN_ONLY" if not failed else "FAIL_CLOSED","liveAccountSecurityVerified":False,"crown":"STOP"}


def changed_patch(base_sha: str, head_sha: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{40}", base_sha) or not re.fullmatch(r"[0-9a-f]{40}", head_sha):
        raise ValueError("exact 40-character source identities required")
    result = subprocess.run(["git","diff","--no-ext-diff","--unified=0",base_sha,head_sha,"--"], cwd=ROOT, capture_output=True, text=True, check=True, timeout=30)
    if len(result.stdout) > 2_000_000:
        raise ValueError("diff exceeds audit budget")
    return result.stdout


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--base-sha",default="")
    parser.add_argument("--head-sha",default="")
    args=parser.parse_args()
    result=inspect()
    if args.base_sha or args.head_sha:
        if not args.base_sha or not args.head_sha:
            parser.error("both exact base and head SHAs are required")
        violations=scan_added_patch(changed_patch(args.base_sha,args.head_sha))
        result["newContentRiskCategories"]=violations
        if violations:
            result["stage"]="FAIL_CLOSED"
    print(json.dumps(result,sort_keys=True,indent=2))
    return 0 if result["stage"] == "SOURCE_POLICY_GREEN_ONLY" else 1


if __name__=="__main__":
    raise SystemExit(main())
