#!/usr/bin/env python3
"""Explain affected modules against a verified Git base; never waive final gates."""
import argparse
import fnmatch
import json
from pathlib import Path
import subprocess
ROOT = Path(__file__).resolve().parents[1]
MODULES = {
    'presentation': ['scripts/game/lumFocus.gd','scripts/game/finalCoffeeHouseOverlay.gd'],
    'worldAndRig': ['scripts/game/*','scripts/main.gd','scenes/*','cutscenes/*','assets/*'],
    'nativeWebglass': ['native/*','addons/*','cockpit/*'],
    'hostAi': ['host/*','scripts/agentMeshRuntime.py'],
    'buildAndGates': ['tools/*','tests/*','scripts/build*','.github/*','doctrine/*','project.godot','export_presets.cfg','.gitignore'],
    'documentation': ['manual/*','docs/*','*.md'],
}
def classify(paths):
    modules = set()
    unknown = []
    for path in paths:
        matches = {name for name, patterns in MODULES.items() if any(fnmatch.fnmatchcase(path,p) for p in patterns)}
        if not matches:
            unknown.append(path)
        modules.update(matches)
    if unknown:
        modules.add('fullRevalidation')
    return {'affected_modules':sorted(modules),'unknown_paths':unknown,'full_revalidation': bool(unknown or 'buildAndGates' in modules),
            'native_reuse':'ONLY_MATCHING_INPUT_FINGERPRINT_AND_OUTPUT_HASHES',
            'final_apk':'REPACKAGE_SIGN_AND_AUDIT_FOR_ANY_ANDROID_CHANGE',
            'device_proof':'REQUIRED_FOR_CHANGED_APK','changed_paths':paths}
if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--base',required=True);args=p.parse_args()
    base=subprocess.check_output(['git','rev-parse','--verify',args.base+'^{commit}'],cwd=ROOT,text=True).strip()
    paths=subprocess.check_output(['git','diff','--name-only','-z',base,'HEAD'],cwd=ROOT).decode().split('\0')
    print(json.dumps({'base':base,**classify(list(filter(None,paths)))},indent=2))
