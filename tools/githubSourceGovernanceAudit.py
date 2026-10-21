#!/usr/bin/env python3
"""Offline GitHub source governance contract checks. No GitHub admin access implied."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def load(name):
    return json.loads((ROOT / "doctrine" / name).read_text(encoding="utf-8"))

def main():
    gov = load("githubSourceHardeningV1.json")
    truth = load("currentSourceTruthV3.json")
    quarantine = load("companyWideOperationalQuarantineV1.json")
    mutation = load("featureMutationPipelineV1.json")
    assert gov["repository"] == truth["canonicalRepository"]
    assert gov["sourceLaw"] == truth["sourceLaw"]
    assert quarantine["state"] == "QUARANTINED"
    assert quarantine["activeTaskWorkersAllowed"] is False
    assert gov["invariants"]["companyQuarantine"] == quarantine["state"]
    assert mutation["mutationControls"]["autoMerge"] is False
    assert mutation["mutationControls"]["autoDeployProduction"] is False
    assert mutation["mutationControls"]["requireExact40Sha"] is True
    for name in ("automaticMerge","automaticDeploy","automaticStableRelease","automaticProductionSigning","secretInRepo"):
        assert gov["invariants"][name] is False, name
    assert gov["settingsVerified"] is False
    assert gov["settingsChanged"] is False
    assert gov["productionDeployed"] is False
    print("GREEN_GITHUB_SOURCE_GOVERNANCE_CONTRACT")
    print("NOT_PROOF_OF_BRANCH_RULESETS_OR_WORKFLOW_PERMISSIONS")
if __name__ == "__main__":
    main()
