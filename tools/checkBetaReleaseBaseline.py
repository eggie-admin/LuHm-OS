#!/usr/bin/env python3
"""Fail-closed Android beta upgrade floor. No private key access or network.

This verifies a human-reviewed source baseline against the pinned Actions
signer. It cannot substitute for observing prior distribution/device state.
"""
import argparse
import json
import re
from pathlib import Path

PACKAGE = "art.eggiebagelface.luhmos.beta"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def fail(reason):
    raise ValueError("RED_BETA_RELEASE_BASELINE:" + reason)


def check(record, next_code, expected_signer):
    if not isinstance(record, dict) or record.get("schema") != "luhmOs.androidBetaReleaseBaseline.v1":
        fail("schema")
    if record.get("applicationId") != PACKAGE:
        fail("package_identity")
    if type(next_code) is not int or not 1 <= next_code <= 2100000000:
        fail("next_version_code")
    if not isinstance(expected_signer, str) or not HEX64.fullmatch(expected_signer):
        fail("pinned_signer")
    status = record.get("status")
    ref = record.get("evidenceRef")
    if not isinstance(ref, str) or len(ref.strip()) < 12:
        fail("owner_evidence_ref_required")

    if status == "VERIFIED_FIRST_BETA":
        if record.get("initialReleaseApproved") is not True:
            fail("first_beta_owner_approval")
        if any(record.get(field) is not None for field in (
            "previousVersionCode", "previousSignerCertificateSha256", "previousApkSha256"
        )):
            fail("first_beta_must_have_no_prior_identity")
    elif status == "VERIFIED_PREVIOUS_BETA":
        if record.get("initialReleaseApproved") is not False:
            fail("prior_beta_cannot_use_first_release")
        prev = record.get("previousVersionCode")
        if type(prev) is not int or prev < 1 or next_code <= prev:
            fail("non_monotonic_version")
        if record.get("previousSignerCertificateSha256") != expected_signer:
            fail("signer_mismatch_previous_release")
        old_hash = record.get("previousApkSha256")
        if not isinstance(old_hash, str) or not HEX64.fullmatch(old_hash):
            fail("prior_apk_hash_missing")
    else:
        fail("unverified_release_history")

    return {"applicationId": PACKAGE, "nextVersionCode": next_code,
            "historyStatus": status, "evidenceRef": ref}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--baseline", default="doctrine/androidBetaReleaseBaselineV1.json")
    p.add_argument("--next-version-code", type=int, required=True)
    p.add_argument("--expected-signer", required=True)
    args = p.parse_args()
    baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    try:
        receipt = check(baseline, args.next_version_code, args.expected_signer)
    except ValueError as exc:
        p.exit(2, str(exc) + "\n")
    print(json.dumps(receipt, sort_keys=True))
    print("GREEN_BETA_RELEASE_BASELINE_SOURCE_CHECK_NOT_DEVICE_PROOF")


if __name__ == "__main__":
    main()
