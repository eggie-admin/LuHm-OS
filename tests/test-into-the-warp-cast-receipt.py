#!/usr/bin/env python3
"""Hard post-deploy media receipt gate. No external writes or secrets."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/"media/pirate-daddy-film/into-the-warp-cast-receipt-20261015.json"
r=json.loads(p.read_text())
assert r["schema"]=="luhm.into-the-warp.cast-receipt.v1"
assert r["status"]=="CANDIDATE_SOURCE_MERGED_NOT_PUBLIC_RELEASE"
assert r["sealedScript"]["modify"] is False
assert r["sealedScript"]["sha256"]=="6f6054e86f6f6dd74ffc9355a34f86d2ff4c3822f1c8c4f2d20b8a701b38f9ef"
assert r["studio"]["belldandyLoreShot"]=="401" and r["studio"]["closingCodexIsSameRecord"]
assert r["studio"]["audioDeferred"]
assert [p["pass"] for p in r["passes"]]==list(range(100,1100,100))
assert r["repository"]["merges"][0]["pullRequest"]==285
assert r["repository"]["merges"][1]["pullRequest"]==286
assert r["artifact"]["sourceRef"]!=r["render"]["deployedSourceRef"]
assert r["artifact"]["sizeBytes"]==10107
assert r["artifact"]["readbackSha256Verified"] is True
assert len(r["artifact"]["sha256"])==64
assert r["artifact"]["driveAnyoneWithLinkReader"] is True
assert r["ownerVault"]["roleVisibility"]=="OWNER_ONLY_CONFIRMED"
assert r["render"]["providerReportedStatus"]=="live"
assert r["render"]["aiFfmpegPersistentWorker"]=="NOT_DEPLOYED"
assert r["render"]["publicHttpProbe"]!="PROVEN"
assert r["proofIsNotPublication"] and not r["authority"]["automaticPublication"]
raw=p.read_text()
for forbidden in ("drive.google.com/file/d/","drive.google.com/drive/folders/","1FW3_UD-syQtas8tjTG1kn_wcruInzlyz"):
    assert forbidden not in raw
print("INTO_THE_WARP_CAST_RECEIPT_GREEN_SOURCE_ONLY")
