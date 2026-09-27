#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.buildPlan import classify

agent_skill = classify(['agents/yumeArtOni/SKILL.md'])
assert 'agentMesh' in agent_skill['affected_modules']
assert agent_skill['targeted_contract_validation'] is True
assert agent_skill['full_revalidation'] is False

agent_doctrine = classify(['doctrine/AGENT_MESH_V2.json'])
assert 'agentMesh' in agent_doctrine['affected_modules']
assert 'buildAndGates' in agent_doctrine['affected_modules']
assert agent_doctrine['targeted_contract_validation'] is True
assert agent_doctrine['full_revalidation'] is False

pet_manifest = classify(['assets/pet/oni/manifest.json'])
assert 'petUi' in pet_manifest['affected_modules']
assert pet_manifest['targeted_contract_validation'] is True
assert pet_manifest['full_revalidation'] is False

pet_binary = classify(['assets/pet/oni/yume/yume_idle_v1.png'])
assert 'petUi' in pet_binary['affected_modules']
assert pet_binary['shipping_pet_binaries'] == ['assets/pet/oni/yume/yume_idle_v1.png']
assert pet_binary['full_revalidation'] is True
assert pet_binary['targeted_contract_validation'] is False

gate_code = classify(['tools/candidateGate.py'])
assert gate_code['unbounded_gate_paths'] == ['tools/candidateGate.py']
assert gate_code['full_revalidation'] is True

unknown = classify(['haunted/toaster.bin'])
assert unknown['unknown_paths'] == ['haunted/toaster.bin']
assert unknown['full_revalidation'] is True

print('BUILD_PLAN_V2_SMOKE=PASS')
