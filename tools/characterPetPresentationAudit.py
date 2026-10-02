#!/usr/bin/env python3
import json
from pathlib import Path
pet=json.loads(Path("doctrine/characterPetPresentationV1.json").read_text())
canon=json.loads(Path(pet["canonicalCharacterSource"]).read_text())
assets=json.loads(Path(pet["assetSource"]).read_text())
art=json.loads(Path(pet["artMutationSource"]).read_text())
assert pet["authority"]=="Professor"
assert canon["authority"]=="Professor"
assert set(pet["characters"])==set(canon["characters"])==set(assets["characters"])
assert all(canon["characters"][x].get("adult") is True or canon["characters"][x].get("minimumAge",0)>=18 for x in pet["characters"])
assert pet["identityLaw"]["canonFieldsMayNotBeOverriddenByPetLayer"] is True
assert pet["identityLaw"]["protectedReferenceMayNotBecomeRuntimeAsset"] is True
assert pet["identityLaw"]["crossCharacterContaminationAllowed"] is False
assert art["crossCharacterContaminationAllowed"] is False
assert art["runtimeProofRequiresExactHash"] is True
assert pet["exactHashRuntimeProofRequired"] is True
req=set(pet["petSystem"]["requiredVisualFamilies"])
assert req <= set(assets["requiredFamilies"])
laws=set(pet["petSystem"]["runtimeLaw"])
for x in ("petThoughtDoesNotEqualAgentAuthority","petBubbleDoesNotEstablishGreen","petPresentationCannotCrownCastMergeDeployOrPublish"):
    assert x in laws
assert pet["assetPromotion"]=="candidateAsset -> approvedArt -> runtimeImportProven -> cast"
print("CHARACTER PET PRESENTATION GREEN")
