#!/usr/bin/env python3
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
errors=[]

def need(ok,msg):
    if not ok:
        errors.append(msg)

def load(rel):
    return json.loads((root/rel).read_text(encoding="utf-8"))

arch=load("doctrine/jqueryFourLayerArchitectureV1.json")
rhythm=load("doctrine/fourBeatInteractionRhythmV1.json")
kernel=load("doctrine/escalationKernelV1.json")
router=load("doctrine/humanCenteredIntentRouterV2.json")
truth=load("doctrine/currentSourceTruthV3.json")
control=load("doctrine/luhmAiControlPlaneV1.json")

need(arch.get("schema")=="luhmOs.jqueryFourLayerArchitecture.v1","architecture schema drift")
need(arch.get("historicalClaim") is False,"jQuery metaphor promoted to historical claim")
need([x.get("tier") for x in arch.get("layers",[])]==[0,1,2,3],"architecture layer numbering drift")
need([x.get("id") for x in arch.get("layers",[])]==[
    "coreLibrary","pluginExtension","classWidgetOrganization","stubAdapterBoundary"
],"architecture layer order drift")
need("stubAdapterBoundaryRemainsThin" in arch.get("laws",[]),"stub boundary law missing")

need(rhythm.get("schema")=="luhmOs.fourBeatInteractionRhythm.v1","rhythm schema drift")
need(rhythm.get("meter")=="4/4","meter drift")
need([x.get("beat") for x in rhythm.get("measure",[])]==[1,2,3,4],"beat numbering drift")
need([x.get("id") for x in rhythm.get("measure",[])]==["hear","resolve","act","verify"],"beat order drift")
need(rhythm.get("turnaround",{}).get("BLOCKED")=="escalateOneTierIfAllowed","blocked turnaround drift")
need(rhythm.get("turnaround",{}).get("GREEN")=="closeOrDeEscalate","green turnaround drift")
need(rhythm.get("learningLaw",{}).get("hiddenModelWeightTraining") is False,"hidden model training claim")
need("covertEmotionClassification" in rhythm.get("interactionSignals",{}).get("forbiddenInferences",[]),"covert emotion guard missing")
need("authorityFromToneAlone" in rhythm.get("interactionSignals",{}).get("forbiddenInferences",[]),"tone authority guard missing")

need(kernel.get("architectureMetaphor")=="doctrine/jqueryFourLayerArchitectureV1.json","kernel architecture pointer missing")
need(kernel.get("interactionRhythm")=="doctrine/fourBeatInteractionRhythmV1.json","kernel rhythm pointer missing")
matrix=kernel.get("fourByFourModel",{})
need(matrix.get("horizontalBeats")==["hear","resolve","act","verify"],"kernel horizontal rhythm drift")
need(matrix.get("verticalTiers")==[0,1,2,3],"kernel vertical tier drift")

need(router.get("interactionRhythm")=="doctrine/fourBeatInteractionRhythmV1.json","router rhythm pointer missing")
need(router.get("routingMeasure")==["hear","resolve","act","verify"],"router measure drift")
need(router.get("rhythmLaw",{}).get("toneAloneMayGrantAuthority") is False,"router tone authority leak")

ar=truth.get("architectureRhythm",{})
need(ar.get("fourLayerArchitecture")=="doctrine/jqueryFourLayerArchitectureV1.json","source truth architecture pointer missing")
need(ar.get("fourBeatInteraction")=="doctrine/fourBeatInteractionRhythmV1.json","source truth rhythm pointer missing")
need(ar.get("matrix")=="4x4","source truth matrix drift")
need(ar.get("hiddenPsychologicalProfiling") is False,"source truth profiling leak")

need(control.get("inherits",{}).get("jqueryFourLayerArchitecture")=="doctrine/jqueryFourLayerArchitectureV1.json","control architecture pointer missing")
need(control.get("inherits",{}).get("fourBeatInteractionRhythm")=="doctrine/fourBeatInteractionRhythmV1.json","control rhythm pointer missing")
need(control.get("interactionRhythm",{}).get("meter")=="4/4","control meter drift")
need(control.get("invariants",{}).get("noCovertPsychologicalProfiling") is True,"control profiling invariant missing")

print(json.dumps({
  "schema":"luhmOs.architectureRhythmAudit.v1",
  "status":"GREEN_ARCHITECTURE_RHYTHM_CANDIDATE" if not errors else "RED_ARCHITECTURE_RHYTHM_CANDIDATE",
  "architectureLayers":4,
  "interactionBeats":4,
  "matrix":"4x4",
  "errors":errors,
  "crownStatus":"STOP"
},indent=2))
raise SystemExit(1 if errors else 0)
