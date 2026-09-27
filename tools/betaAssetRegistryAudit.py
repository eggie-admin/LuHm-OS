#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'assets/registry/BETA_ASSET_SOURCES_V1.json'
CAPMAP = ROOT / 'assets/registry/GODOT4_COMMUNITY_CAPABILITY_MAP_V1.json'
DOCTRINE = ROOT / 'doctrine/GODOT4_BETA_ENGINE_HARDENING_V1.json'
OUT = ROOT / 'build/beta-engine/asset-registry-audit.json'

def die(msg: str) -> None:
    raise SystemExit(f'BETA_ASSET_AUDIT_RED: {msg}')

registry = json.loads(REGISTRY.read_text(encoding='utf-8'))
capmap = json.loads(CAPMAP.read_text(encoding='utf-8'))
doctrine = json.loads(DOCTRINE.read_text(encoding='utf-8'))
if registry.get('schema') != 'luhm-os.beta-asset-sources.v1': die('wrong registry schema')
if registry.get('runtimeNetwork') is not False: die('runtime network must stay disabled')
if doctrine.get('status') != 'BETA_LANE_STAGED': die('beta doctrine not staged')
if capmap.get('referenceCount') != 20 or len(capmap.get('capabilities', [])) != 20: die('20-source community capability cathedral missing')
sources = registry.get('sources')
if not isinstance(sources, list) or len(sources) < 8: die('asset source registry incomplete')
keys = {s.get('key') for s in sources if isinstance(s, dict)}
required = {'repo-community-cc0','godot4-community-capability-cathedral','drive-original-vault','drive-character-physics-curated','drive-third-party-private-reference','chatgpt-library-asset-dungeon','lum-animated-state-contract','meshy-lum-runtime-donor'}
missing = sorted(required - keys)
if missing: die(f'missing source lanes: {missing}')
for source in sources:
    if not isinstance(source, dict): die('non-object source')
    rights = source.get('rights')
    package = source.get('package')
    if rights == 'PRIVATE_REFERENCE' and package is not False: die(f'private reference marked packageable: {source.get("key")}')
public_text = REGISTRY.read_text(encoding='utf-8') + CAPMAP.read_text(encoding='utf-8')
if 'drive.google.com/' in public_text or re.search(r'\b1[A-Za-z0-9_-]{20,}\b', public_text): die('private Drive locator leaked into public registry')
if re.search(r'\bfile_[0-9a-f]{20,}\b', public_text): die('ChatGPT Library locator leaked into public registry')
community = next(s for s in sources if s.get('key') == 'repo-community-cc0')
if int(community.get('expectedAssetCount', 0)) != 77: die('community runtime asset count contract drift')
rig = next(s for s in sources if s.get('key') == 'meshy-lum-runtime-donor').get('rigContract', {})
if int(rig.get('joints', 0)) != 24 or int(rig.get('requiredHumanoidRoles', 0)) != 22: die('LumRigV2 contract drift')
library = next(s for s in sources if s.get('key') == 'chatgpt-library-asset-dungeon')
if int(library.get('indexedAssetCount', 0)) != 28: die('ChatGPT Library asset index count drift')
for item in capmap.get('capabilities', []):
    if item.get('runtime') == 'noncommercial_reference_only' and item.get('license') == 'CC0': die('noncommercial classification contradiction')
result = {'status':'GREEN','source_count':len(sources),'community_runtime_expected':77,'community_capability_sources':20,'library_indexed':28,'lum_rig_joints':24,'lum_required_roles':22,'runtime_network':False,'private_reference_packaging':False}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print('BETA_ASSET_AUDIT=GREEN', json.dumps(result, sort_keys=True))
