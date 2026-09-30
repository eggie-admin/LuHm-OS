#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, subprocess, sys

BASE = pathlib.Path.home()/".luhm/candidates/roleplay-v3"

def load(rel):
    return json.loads((BASE/rel).read_text(encoding="utf-8"))

def main():
    cmd = sys.argv[1] if len(sys.argv)>1 else "status"
    if cmd=="status":
        rp=load("doctrine/CODING_ROLEPLAY_SYSTEM_V3.json")
        print(json.dumps({
          "status":"LOCAL_CANDIDATE_INSTALLED",
          "canonicalBase":rp["canonicalBase"],
          "authority":"Professor",
          "crownStatus":"STOP",
          "note":"Skill/logic deployment only; this does not claim autonomous background agents are running."
        }, indent=2)); return 0
    if cmd=="roster":
        control=load("doctrine/ONI_MESH_CONTROL_PLANE_V2.json")
        print(json.dumps({
          "boss":control["boss"],
          "roles":control["roles"],
          "maxParallelSupportWorkers":control["topology"]["maxParallelSupportWorkers"],
          "greenAuthority":False
        }, indent=2)); return 0
    if cmd=="route":
        args=sys.argv[2:] or ["read"]
        return subprocess.call([sys.executable, str(BASE/"tools/lumTaskRouter.py"), *args])
    if cmd=="doctor":
        return subprocess.call([sys.executable, str(BASE/"tools/luhmRoleplayAudit.py")])
    if cmd=="roleplay":
        rp=load("doctrine/CODING_ROLEPLAY_SYSTEM_V3.json")
        print(json.dumps(rp["roleplayVocabulary"], indent=2)); return 0
    print("usage: luhm [status|roster|route <kind> [flags]|doctor|roleplay]", file=sys.stderr)
    return 2

if __name__=="__main__":
    raise SystemExit(main())
