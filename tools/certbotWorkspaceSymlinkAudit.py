#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

parserValue = argparse.ArgumentParser(description="Read-only Certbot live-path/symlink audit")
parserValue.add_argument("--cert-name", dest="certName", default="")
parserValue.add_argument("--runtime", action="store_true")
argsValue = parserValue.parse_args()

resultValue = {
    "schema": "luhmOs.certbotWorkspaceSymlinkAudit.v1",
    "status": "SOURCE_CONTRACT_ONLY",
    "certName": argsValue.certName or "UNSET",
    "secretValuesRead": False,
    "mutationAuthority": False,
    "checks": {},
    "crownStatus": "STOP",
}

if not argsValue.runtime:
    print(json.dumps(resultValue, indent=2))
    raise SystemExit(0)

if not argsValue.certName:
    resultValue["status"] = "VERIFY_CERT_NAME_REQUIRED"
    print(json.dumps(resultValue, indent=2))
    raise SystemExit(2)

liveRootPath = Path("/etc/letsencrypt/live") / argsValue.certName
certificatePath = liveRootPath / "fullchain.pem"
privateKeyPath = liveRootPath / "privkey.pem"
renewalPath = Path("/etc/letsencrypt/renewal") / f"{argsValue.certName}.conf"

resultValue["checks"] = {
    "liveRootExists": liveRootPath.exists(),
    "fullchainExists": certificatePath.exists(),
    "privkeyExists": privateKeyPath.exists(),
    "fullchainIsSymlink": certificatePath.is_symlink(),
    "privkeyIsSymlink": privateKeyPath.is_symlink(),
    "renewalConfigExists": renewalPath.exists(),
}

requiredState = (
    resultValue["checks"]["liveRootExists"]
    and resultValue["checks"]["fullchainExists"]
    and resultValue["checks"]["privkeyExists"]
    and resultValue["checks"]["renewalConfigExists"]
)

resultValue["status"] = "GREEN_CERTBOT_LIVE_PATH_PRESENT" if requiredState else "VERIFY_CERTBOT_RUNTIME_STATE"
print(json.dumps(resultValue, indent=2))
raise SystemExit(0 if requiredState else 3)
