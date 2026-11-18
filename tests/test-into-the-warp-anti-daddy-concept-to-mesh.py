"""Anti-Daddy three-era C-to-M provenance, status and publication firewall."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
m=json.loads((root/"media/pirate-daddy-film/into-the-warp-anti-daddy-concept-to-mesh-v1.json").read_text())
seal=json.loads((root/"media/pirate-daddy-film/into-the-warp-anti-daddy-character-seal-v1.json").read_text())
assert m["schema"]=="luhmOs.intoTheWarpAntiDaddyConceptToMesh.v1"
assert m["character"]=="antiDaddy" and seal["characterId"]=="antiDaddy"
assert [x["ageEra"] for x in m["variants"]]==["20s","30s","40s"]
assert len({x["sha256"] for x in m["variants"]})==3
assert all(len(x["sha256"])==64 for x in m["variants"])
assert m["sharedVerifiedFacts"]["jointCount"]==22
assert len(m["sharedVerifiedFacts"]["animationClips"])==4
assert m["sharedVerifiedFacts"]["actualThirdPartySephirothMeshCopied"] is False
assert m["sharedVerifiedFacts"]["actualBlenderkitMarketplaceMeshDownloaded"] is False
assert m["acceptanceGates"]["Godot4ImportRuntime"]=="UNVERIFIED"
assert m["acceptanceGates"]["ChatGPTSiteMcpWidgetRegistered"]=="NOT_DONE"
assert m["acceptanceGates"]["publicDistribution"]=="STOP"
assert m["privateMeshesUploadedToPublicRepo"] is False
assert m["priorScreenplayModified"] is False
assert {x["fileName"] for x in m["candidateOutputs"]}=={"antiDaddyThreeEras_ModelShowcase.png","antiDaddyThreeEras_InteractiveGLB.html","antiDaddyGodot4ThreeEras_v1.zip","antiDaddyThreeEras_CompleteTestKit.zip"}
print("GREEN_ANTI_DADDY_CONCEPT_TO_MESH_RECEIPT_SOURCE_ONLY")
