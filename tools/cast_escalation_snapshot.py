#!/usr/bin/env python3
"""CAST stage assessment: source gates cannot become runtime proof."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
GATE=ROOT/"doctrine/cast500ExitDevelopmentGateV1.json"
TRUTH=ROOT/"doctrine/currentSourceTruthV3.json"

def assess(root=ROOT):
    gate=json.loads((root/"doctrine/cast500ExitDevelopmentGateV1.json").read_text())
    truth=json.loads((root/"doctrine/currentSourceTruthV3.json").read_text())
    if gate.get("schema")!="luhmOs.cast500ExitDevelopmentGate.v1" or truth.get("schema")!="luhmOs.currentSourceTruth.v3":
        raise ValueError("INVALID_CANON_SCHEMA")
    proof=gate["promotionProof"]
    phases=gate["releasePhases"]
    missing={name:[key for key in cfg.get("requires",[]) if proof.get(key) is not True]
             for name,cfg in phases.items() if isinstance(cfg,dict)}
    return {"schema":"luhmOs.castEscalationSnapshot.v1",
            "source":"CANDIDATE_ONLY","canonicalRepository":truth["canonicalRepository"],
            "currentSourcePromotion":truth.get("promotion") is True,
            "phases":{name:{"eligible":len(keys)==0 and truth.get("promotion") is True,
                            "missingEvidence":keys} for name,keys in missing.items()},
            "automaticMerge":False,"automaticDeploy":False,"automaticPublish":False,
            "nextAction":"RUN_EXACT_HEAD_CI_AND_RECONCILE_RECEIPTS"}
if __name__=="__main__":
    print(json.dumps(assess(),indent=2,sort_keys=True))
