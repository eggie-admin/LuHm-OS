#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))
edu=load("doctrine/yumeArtEducationV1.json")
yume=load("doctrine/yumeCreativePipelineV1.json")
work=load("doctrine/yumeArtistWorkstationV1.json")
truth=load("doctrine/currentSourceTruthV3.json")
checks=[
 ("schema",edu.get("schema")=="luhmOs.yumeArtEducation.v1"),
 ("status",edu.get("status")=="PROPOSED_TRAINING_CONTRACT"),
 ("professor",edu.get("authority")=="Professor"),
 ("owner",edu.get("owner")=="yume"),
 ("fineTrack",edu.get("fineArtTrack",{}).get("role")=="meaningFormAndVisualLanguage"),
 ("commercialTrack",edu.get("commercialArtTrack",{}).get("role")=="reproductionProductionAndDelivery"),
 ("contrast","contrast" in edu.get("fineArtTrack",{}).get("coreStudy",[])),
 ("punk","punkAndPostPunkVisualLanguages" in edu.get("fineArtTrack",{}).get("visualTraditions",[])),
 ("comics","comicBookAndSequentialArt" in edu.get("fineArtTrack",{}).get("visualTraditions",[])),
 ("print","prepress" in edu.get("commercialArtTrack",{}).get("print",[])),
 ("vector","vectorAssetProduction" in edu.get("commercialArtTrack",{}).get("staticDigital",[])),
 ("video","ffmpegAssemblyAndVerification" in edu.get("commercialArtTrack",{}).get("videoAndMotion",[])),
 ("godot","godotImportPlanning" in edu.get("commercialArtTrack",{}).get("threeDAndInteractive",[])),
 ("preserveSketch","professor_sketch_may_be_low_fidelity_but_must_be_preserved_as_source" in edu.get("dualTrackLaw",[])),
 ("noSilentReplace","neither_track_may_silently_replace_professor_authorship" in edu.get("dualTrackLaw",[])),
 ("montBlancUnknown",edu.get("referenceNotes",{}).get("montBlanc",{}).get("status")=="USER_SPOKEN_REFERENCE_UNRESOLVED"),
 ("professional",edu.get("professionalStandard",{}).get("editableMasterSeparatedFromDeliveryDerivative") is True),
 ("yumeBound",yume.get("artEducation")=="doctrine/yumeArtEducationV1.json"),
 ("workBound",work.get("trainingContract")=="doctrine/yumeArtEducationV1.json"),
 ("truthBound",truth.get("creativeLayer",{}).get("yumeArtEducation")=="doctrine/yumeArtEducationV1.json"),
 ("crown",edu.get("crownStatus")=="STOP")
]
failed=[n for n,o in checks if not o]
for i,(n,o) in enumerate(checks,1): print(f"{'PASS' if o else 'FAIL'} {i:02d}/{len(checks)} {n}")
if failed: raise SystemExit("YUME_ART_EDUCATION_AUDIT=RED failed="+",".join(failed))
print("YUME_ART_EDUCATION_AUDIT=GREEN")
print(f"passes={len(checks)}/{len(checks)}")
print("crown=STOP")
