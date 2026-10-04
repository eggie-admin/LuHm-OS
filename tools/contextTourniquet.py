#!/usr/bin/env python3
import json, sys
from pathlib import Path

ALLOWED = {"PROVEN","SOURCE_DERIVED","OBSERVED","INFERENCE","PROPOSAL","MEMORY_ONLY","UNKNOWN","CONTRADICTED"}
REQUIRED = {"sourceRef","objective","confirmedFacts","evidenceRefs","pendingDecisions","conflicts","proposedMutations","executionAuthorized"}

def clamp(checkpoint):
    missing = sorted(REQUIRED - checkpoint.keys())
    if missing:
        raise SystemExit("RED_CONTEXT_TOURNIQUET missing=" + ",".join(missing))
    if checkpoint["executionAuthorized"] is not False:
        raise SystemExit("RED_CONTEXT_TOURNIQUET checkpoint cannot self-authorize execution")
    for fact in checkpoint["confirmedFacts"]:
        if fact.get("class") not in ALLOWED:
            raise SystemExit("RED_CONTEXT_TOURNIQUET invalid claim class")
        if fact.get("class") in {"PROVEN","SOURCE_DERIVED","OBSERVED"} and not fact.get("evidenceRefs"):
            raise SystemExit("RED_CONTEXT_TOURNIQUET factual claim lacks evidence")
    return {
        "schema":"luhmOs.contextCheckpoint.v1",
        "sourceRef":checkpoint["sourceRef"],
        "objective":checkpoint["objective"],
        "confirmedFacts":checkpoint["confirmedFacts"],
        "evidenceRefs":checkpoint["evidenceRefs"],
        "pendingDecisions":checkpoint["pendingDecisions"],
        "conflicts":checkpoint["conflicts"],
        "proposedMutations":checkpoint["proposedMutations"],
        "executionAuthorized":False,
        "crownStatus":"stop"
    }

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: contextTourniquet.py checkpoint.json")
    data=json.loads(Path(sys.argv[1]).read_text())
    print(json.dumps(clamp(data),indent=2,sort_keys=True))
