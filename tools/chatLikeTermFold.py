#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sys
from collections import OrderedDict
from pathlib import Path

def stable_hash(value):
    raw=json.dumps(value,sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(raw).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("manifest", type=Path)
    args=ap.parse_args()
    data=json.loads(args.manifest.read_text())
    ops=data.get("operations",[])
    groups=OrderedDict()
    seen=set()
    for op in ops:
        exact=stable_hash(op)
        if exact in seen:
            continue
        seen.add(exact)
        key=(
            op.get("sourceRef"),op.get("scopeId"),op.get("operationFamily"),
            op.get("repository"),op.get("baseRef"),op.get("toolClass"),
            op.get("proofKind"),op.get("authorityClass")
        )
        groups.setdefault(key,[]).append(op)
    out=[]
    for key,members in groups.items():
        targets=[m.get("targetId") or m.get("targetRef") or m.get("displayLabel") for m in members]
        out.append({
            "semanticClassId":stable_hash(key)[:16],
            "sourceRef":key[0],"scopeId":key[1],"operationFamily":key[2],
            "repository":key[3],"baseRef":key[4],"toolClass":key[5],
            "proofKind":key[6],"authorityClass":key[7],
            "memberCount":len(members),
            "targets":targets,
            "targetSetHash":stable_hash(targets),
            "providerEscalationBudget":1,
            "individualItemProgress":False
        })
    print(json.dumps({
        "schema":"luhmOs.chatLikeTermFoldResult.v1",
        "inputCount":len(ops),
        "dedupedCount":sum(len(v) for v in groups.values()),
        "semanticClassCount":len(out),
        "groups":out,
        "greenAuthority":False,
        "crownAuthority":False
    },indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
