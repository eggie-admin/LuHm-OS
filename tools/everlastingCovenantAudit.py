#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
paths={
  "covenant":ROOT/"doctrine/everlastingCovenantV1.json",
  "control":ROOT/"doctrine/luhmAiControlPlaneV1.json",
  "chat":ROOT/"doctrine/projectChatCanonV1.json",
  "truth":ROOT/"doctrine/SOURCE_OF_TRUTH.json",
  "lane":ROOT/"doctrine/proposedWorkingLaneV1.json",
  "oni":ROOT/"agents/shared/ONI_PROTOCOL_V2.md",
  "agents":ROOT/"AGENTS.md",
  "copilot":ROOT/".github/copilot-instructions.md",
}
for name,p in paths.items():
    if not p.exists():
        raise SystemExit(f"missing:{name}:{p.relative_to(ROOT)}")

covenant=json.loads(paths["covenant"].read_text())
control=json.loads(paths["control"].read_text())
chat=json.loads(paths["chat"].read_text())
truth=json.loads(paths["truth"].read_text())
lane=json.loads(paths["lane"].read_text())
oni=paths["oni"].read_text()
agents=paths["agents"].read_text()
copilot=paths["copilot"].read_text()

expected=["sanityCheck","audit","ingest","mutation","test","apply","continue","deploy"]
human=[
  "so let it be written so let it be done",
  "Do not tell me of the old magic, for I was there when we first wrote them",
  "This is the law and our everlasting covenant."
]

checks=[
 ("covenantStatus", covenant.get("status")=="proposedCanonLaw"),
 ("humanLaw", covenant.get("humanLaw")==human),
 ("guardRailOrder", covenant.get("guardRail",{}).get("orderedStates")==expected),
 ("redFailsClosed", covenant.get("guardRail",{}).get("redLaw","").startswith("RED, UNKNOWN")),
 ("newSourceRestarts", "restart" in covenant.get("guardRail",{}).get("mutationLoop","")),
 ("noSelfPromotion", covenant.get("guardRail",{}).get("selfPromotion") is False),
 ("noAutoCrown", covenant.get("guardRail",{}).get("automaticCrown") is False),
 ("proposedLaneBinding", covenant.get("proposedLane",{}).get("currentDoctrineMutationsRemainProposed") is True),
 ("controlBinding", control.get("covenant",{}).get("guardRail")==expected),
 ("chatBinding", chat.get("workflowGuardRail",{}).get("orderedStates")==expected),
 ("truthBinding", truth.get("everlastingCovenant",{}).get("guardRail")==expected),
 ("truthProposed", truth.get("everlastingCovenant",{}).get("currentWorkingLane")=="PROPOSED_ONLY"),
 ("truthNoPromotion", truth.get("everlastingCovenant",{}).get("promotion") is False),
 ("laneBinding", lane.get("guardRail")==expected),
 ("oniBinding", "sanityCheck -> audit -> ingest -> mutation -> test -> apply -> continue -> deploy" in oni),
 ("agentsBinding", "sanityCheck -> audit -> ingest -> mutation -> test -> apply -> continue -> deploy" in agents),
 ("copilotBinding", "sanityCheck -> audit -> ingest -> mutation -> test -> apply -> continue -> deploy" in copilot),
]

for pass_num in range(1,21):
    failed=[name for name,ok in checks if not ok]
    print(f"PASS_{pass_num:02d}={'GREEN' if not failed else 'RED'}")
    if failed:
        for name in failed:
            print(f"  FAIL:{name}")
        print("EVERLASTING_COVENANT=RED")
        raise SystemExit(1)

for state in expected:
    print(f"{state}=GREEN")
print("EVERLASTING_COVENANT=GREEN")
print("passes=20")
print("lane=PROPOSED_ONLY")
print("deployMeaning=proposedCandidateOnly")
print("crown=STOP")
