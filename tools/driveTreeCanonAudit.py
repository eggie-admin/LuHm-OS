#!/usr/bin/env python3
"""Deterministic source-truth checks for observed Google Drive top-level tree."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def read(name):
    return json.loads((ROOT / "doctrine" / name).read_text(encoding="utf-8"))
def main():
    audit = read("driveTreeCanonAuditV1.json")
    truth = read("currentSourceTruthV3.json")
    quarantine = read("companyWideOperationalQuarantineV1.json")
    assert audit["sourceRepository"] == truth["canonicalRepository"]
    assert audit["status"] == "VERIFIED_TOP_LEVEL_METADATA_ONLY"
    assert audit["projectFolder"]["verifiedImmediateChildren"] == len(audit["projectChildren"]) == 15
    assert audit["root"]["verifiedImmediateChildren"] == len(audit["root"]["items"]) == 4
    ids = [x["id"] for x in audit["projectChildren"]]
    assert len(set(ids)) == len(ids)
    assert audit["projectFolder"]["id"] in [x["id"] for x in audit["root"]["items"]]
    assert not set(ids).intersection(x["id"] for x in audit["root"]["items"])
    assert quarantine["state"] == audit["invariants"]["companyQuarantine"] == "QUARANTINED"
    assert quarantine["activeTaskWorkersAllowed"] is False
    assert audit["invariants"]["githubCanonical"] is True
    assert audit["invariants"]["driveFolderLocationDoesNotPromoteCanon"] is True
    for key in ("filesDeleted", "productionDeployment", "agentExecution"):
        assert audit["invariants"][key] is False
    assert "Per-file sharing ACL and inherited access changes after folder moves" in audit["notVerified"]
    assert audit["crownStatus"] == "STOP"
    print("GREEN_DRIVE_TREE_SOURCE_CANON_AUDIT: metadata and doctrine only")
    print("NOT_LIVE_ACL_OR_RECURSIVE_CONTENT_VERIFICATION")
if __name__ == "__main__":
    main()
