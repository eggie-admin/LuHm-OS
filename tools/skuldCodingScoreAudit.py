#!/usr/bin/env python3
"""Source-only Skuld coding-score cross-contract audit with negative controls."""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def validate(score, sources, skill):
    errors = []
    def check(ok, label):
        if not ok:
            errors.append(label)

    arch, kernel, rhythm, eighth, typed, package, intent, roleplay, staff = (
        sources[name] for name in ("composition", "escalation", "rhythm",
        "eighthNotes", "oldMagic", "newMagic", "humanIntent", "humanRoleplay", "staff"))
    check(score.get("schema") == "luhmOs.skuldCodingScore.v1", "scoreSchema")
    check(score.get("status") == "PROPOSED_SOURCE_ONLY" and
          score.get("crownStatus") == "STOP" and
          score.get("promotion") is False, "proposalCannotSelfPromote")
    check(score.get("owner") == "skuldResearch" and
          score.get("orchestrator") == "lum", "staffOwnership")
    expectedLayers = [layer["id"] for layer in arch["layers"]]
    expectedTiers = [tier["id"] for tier in kernel["tierSemantics"]]
    expectedBeats = [beat["id"] for beat in rhythm["measure"]]
    counts = score.get("distinctFourCounts", {})
    check(len(expectedLayers) == 4 and
          counts.get("compositionLayers") == expectedLayers, "compositionLayerDrift")
    check(len(expectedTiers) == 4 and
          counts.get("escalationTiers") == expectedTiers, "escalationTierDrift")
    check(rhythm.get("meter") == "4/4" and
          counts.get("beats") == expectedBeats, "rhythmDrift")
    check([note["note"] for note in eighth["notes"]] == list(range(1, 9)),
          "eighthSourceDrift")
    check(len(typed.get("lanes", [])) == 4 and
          score["magicFamilies"]["oldMagic"]["bindings"] ==
          [lane["id"] for lane in typed["lanes"]], "typedSqlDrift")
    check(typed.get("runtimeDatabase") is False and
          score["magicFamilies"]["oldMagic"]["databaseRuntimeProven"] is False,
          "sqlRuntimeClaim")
    check(package["apkLifecycle"]["npmInstallsApk"] is False and
          package["jquery"]["installCommand"] == "npm ci --ignore-scripts" and
          score["magicFamilies"]["newMagic"]["installationProven"] is False,
          "packageBoundary")
    check(intent["rhythmLaw"]["toneAloneMayGrantAuthority"] is False and
          roleplay["bubbleLaw"]["roleplayCannotRewriteEvidence"] is True and
          score["magicFamilies"]["humanMagic"]["independentHostProof"] is False,
          "humanPresentationBoundary")
    check(staff["activationLaw"]["maxParallelSupportWorkers"] == 3 and
          staff["activationLaw"]["oneMutableSourceLane"] is True,
          "workerBudgetDrift")
    check("## Skuld coding score research handoff" in skill and
          "doctrine/skuldCodingScoreV1.json" in skill,
          "skillBindingMissing")
    meter = score.get("meter", {})
    notes = score.get("sixteenthNotes", [])
    check(meter.get("signature") == "4/4" and
          meter.get("eighthCount") == 8 and
          meter.get("proposedSixteenthCount") == 16 and
          meter.get("sixteenthStatus") == "NEW_PROPOSAL_NOT_EXISTING_CANON" and
          meter.get("sixteenthsPerEighth") == 2 and
          meter.get("sixteenthsPerBeat") == 4, "sixteenthProposalBoundary")
    check(meter.get("taskIdentity") == ["taskId", "sourceRef", "scopeId"],
          "taskIdentityDrift")
    check(len(notes) == 16 and
          [n.get("sixteenth") for n in notes] == list(range(1, 17)), "sixteenthCount")
    for index, note in enumerate(notes):
        parent = index // 2
        if parent >= len(eighth["notes"]):
            break
        check(note.get("eighthNote") == parent + 1 and
              note.get("beat") == eighth["notes"][parent]["beat"] and
              note.get("inheritsParentEighth") is True and
              note.get("authorityFromNote") is False,
              "noteMapping" + str(index + 1))
    handoff = score.get("handoff", {})
    check(handoff.get("oneMutableSourceLane") is True and
          handoff.get("maxParallelSupportWorkers") == 3 and
          handoff.get("hiddenAsyncExecution") is False and
          handoff.get("recursiveRecruitment") is False and
          handoff.get("visibleArtifactOrBlockerRequired") is True and
          handoff.get("installRequiresSeparateExactApproval") is True,
          "handoffSafety")
    claim = score.get("currentClaim", {})
    check(claim.get("sixteenthNoteCanon") == "NOT_PROMOTED" and
          claim.get("actualArtifact") == "NOT_BUILT" and
          claim.get("liveWorkers") == "NOT_PROVEN" and
          claim.get("milestone") == "NOT_COMPLETE", "falseRuntimeClaim")
    check(score.get("mergeAuthority") is False and
          score.get("deployAuthority") is False and
          score.get("publicationAuthority") is False, "authorityLeak")
    for sourceName, sourcePath in score.get("provenance", {}).items():
        check(isinstance(sourcePath, str) and sourcePath and
              (ROOT / sourcePath).is_file(), "missingSource:" + sourceName)
    return errors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    score = load("doctrine/skuldCodingScoreV1.json")
    sources = {key: load(path) for key, path in score["provenance"].items()
               if key in {"composition", "escalation", "rhythm", "eighthNotes",
                          "oldMagic", "newMagic", "humanIntent", "humanRoleplay", "staff"}}
    skill = (ROOT / "agents/skuldResearchOni/SKILL.md").read_text(encoding="utf-8")
    errors = validate(score, sources, skill)
    negative = {}
    if args.self_test and not errors:
        cases = [
            ("silentCanon", ("meter", "sixteenthStatus"), "CANONICAL"),
            ("falseSql", ("magicFamilies", "oldMagic", "databaseRuntimeProven"), True),
            ("elevatedCrown", ("crownStatus",), "GREEN"),
            ("workerOverrun", ("handoff", "maxParallelSupportWorkers"), 99),
            ("fakeRuntime", ("currentClaim", "actualArtifact"), "BUILT")
        ]
        for label, path, value in cases:
            broken = copy.deepcopy(score)
            field = broken
            for key in path[:-1]:
                field = field[key]
            field[path[-1]] = value
            negative[label] = bool(validate(broken, sources, skill))
            if not negative[label]:
                errors.append("negativeControlFailed:" + label)
    print(json.dumps({
        "schema": "luhmOs.skuldCodingScoreAudit.v1",
        "status": "GREEN_SOURCE_CANDIDATE_ONLY" if not errors else "RED_SOURCE_CANDIDATE",
        "validatedContract": "doctrine/skuldCodingScoreV1.json",
        "eighthNoteCanon": 8,
        "sixteenthNoteStatus": "PROPOSAL_NOT_PROMOTED",
        "runtimeProof": False,
        "negativeControls": negative,
        "errors": errors,
        "crownStatus": "STOP"
    }, indent=2))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
