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
    'agentMesh': [
        'agents/*',
        'scripts/agentMeshRuntime.py',
        'tools/lumTaskRouter.py',
        'tools/doctorOniAudit.py',
        'tools/petIconManifestAudit.py',
        'tests/testAgentMeshV2.py',
        'tests/agentMeshSmoke.py',
        'doctrine/AGENT_MESH_V2.json',
        'doctrine/LUM_ORCHESTRATOR_V2.json',
        'doctrine/SOURCE_LAYOUT_V1.json',
        'doctrine/CREATIVE_MEDIA_PIPELINE_V1.json',
    ],
    'petUi': ['assets/pet/*'],
    'buildAndGates': ['tools/*','tests/*','scripts/build*','.github/*','doctrine/*','project.godot','export_presets.cfg','.gitignore'],
    'documentation': ['manual/*','docs/*','*.md'],
}

# These paths are build/gate-adjacent but have a bounded contract suite. They do not
# force a whole Android/game rebuild unless another changed path crosses that boundary.
TARGETED_CONTRACT_PATHS = [
    'agents/*',
    'scripts/agentMeshRuntime.py',
    'tools/lumTaskRouter.py',
    'tools/doctorOniAudit.py',
    'tools/petIconManifestAudit.py',
    'tests/testAgentMeshV2.py',
    'tests/agentMeshSmoke.py',
    'tests/buildPlanV2Smoke.py',
    'doctrine/AGENT_MESH_V2.json',
    'doctrine/LUM_ORCHESTRATOR_V2.json',
    'doctrine/SOURCE_LAYOUT_V1.json',
    'doctrine/CREATIVE_MEDIA_PIPELINE_V1.json',
    'assets/pet/README.md',
    'assets/pet/oni/*.md',
    'assets/pet/oni/*.json',
]
BUILD_GATE_PATTERNS = MODULES['buildAndGates']
PET_BINARY_SUFFIXES = ('.png', '.apng', '.webp', '.svg', '.gif')


def matches_any(path, patterns):
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def classify(paths):
    modules = set()
    unknown = []
    for path in paths:
        matches = {name for name, patterns in MODULES.items() if matches_any(path, patterns)}
        if not matches:
            unknown.append(path)
        modules.update(matches)

    broad_gate_paths = [path for path in paths if matches_any(path, BUILD_GATE_PATTERNS)]
    unbounded_gate_paths = [path for path in broad_gate_paths if not matches_any(path, TARGETED_CONTRACT_PATHS)]
    shipping_pet_binaries = [
        path for path in paths
        if path.startswith('assets/pet/') and path.lower().endswith(PET_BINARY_SUFFIXES)
    ]
    targeted_contract_validation = bool(
        not unknown
        and not unbounded_gate_paths
        and not shipping_pet_binaries
        and ({'agentMesh', 'petUi'} & modules)
    )
    full_revalidation = bool(unknown or unbounded_gate_paths or shipping_pet_binaries)

    return {
        'affected_modules': sorted(modules),
        'unknown_paths': unknown,
        'full_revalidation': full_revalidation,
        'targeted_contract_validation': targeted_contract_validation,
        'unbounded_gate_paths': unbounded_gate_paths,
        'shipping_pet_binaries': shipping_pet_binaries,
        'native_reuse': 'ONLY_MATCHING_INPUT_FINGERPRINT_AND_OUTPUT_HASHES',
        'final_apk': 'REPACKAGE_SIGN_AND_AUDIT_FOR_ANY_ANDROID_CHANGE',
        'device_proof': 'REQUIRED_FOR_CHANGED_APK',
        'pet_asset_rule': 'METADATA_ONLY_TARGETED; SHIPPING_BINARY_REQUIRES_RUNTIME_IMPORT_PROOF',
        'changed_paths': paths,
    }


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--base', required=True)
    args = p.parse_args()
    base = subprocess.check_output(['git','rev-parse','--verify',args.base+'^{commit}'], cwd=ROOT, text=True).strip()
    paths = subprocess.check_output(['git','diff','--name-only','-z',base,'HEAD'], cwd=ROOT).decode().split('\0')
    print(json.dumps({'base':base, **classify(list(filter(None, paths)))}, indent=2))
