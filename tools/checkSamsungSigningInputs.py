#!/usr/bin/env python3
"""Check input presence before expensive builds; never read or decode a key file."""
import os
import re
import sys

FIELDS = {
    "BETA_P12_B64": "LUHM_BETA_SIGNING_P12_B64",
    "BETA_PASSWORD": "LUHM_BETA_SIGNING_PASSWORD",
    "BETA_ALIAS": "LUHM_BETA_SIGNING_ALIAS",
    "TRUSTED_SIGNER": "LUHM_BETA_SIGNER_SHA256",
}


def check(env):
    errors = ["missing:" + name for key, name in FIELDS.items() if not env.get(key)]
    signer = env.get("TRUSTED_SIGNER", "")
    if signer and not re.fullmatch(r"[0-9a-f]{64}", signer):
        errors.append("invalidFormat:LUHM_BETA_SIGNER_SHA256")
    return errors


def main():
    errors = check(os.environ)
    if errors:
        print("BLOCKED_SIGNING_INPUTS " + ",".join(errors), file=sys.stderr)
        print("Configure owner-held signing inputs through the approved protected signing workflow; never paste keys into chat.", file=sys.stderr)
        return 2
    print("SIGNING_INPUTS_PRESENT_ONLY: key validity, environment protection, APK and device remain unverified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
