#!/usr/bin/env python3
"""Read-only brand projection audit; never creates/mutates SQL or assets."""
from pathlib import Path
import hashlib, json, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
p=json.loads((ROOT/'doctrine/brandHexVectorProjectionV1.json').read_text(encoding='utf-8'))
svgfile=ROOT/p['masterVector']['source']
replica=ROOT/p['masterVector']['existingPluginCopy']
html=(ROOT/'frontEnd/prototypes/brandVector1048/index.html').read_text(encoding='utf-8')
def check(ok,label):
    if not ok: raise AssertionError('RED_BRAND_VECTOR_'+label)
    print('PASS_'+label)
check(p['schema']=='luhmOs.brandHexVectorProjection.v1','SCHEMA')
check(p['status']=='SOURCE_CANDIDATE_REVIEW_ONLY' and p['gate']=={'candidateOnly':True,'professorFinalApprovalPending':True,'mergeToMain':False,'deploy':False,'crown':'STOP'},'CROWN_LOCK')
check(p['brandMachineId']=='luhmOs' and p['existingBrandRegistry']=='doctrine/organizationBrandRegistryV1.json','SINGLE_BRAND_IDENTITY')
brand=json.loads((ROOT/p['existingBrandRegistry']).read_text(encoding='utf-8'))
check(brand['publicBrands']['luhmOs']['displayName']==p['displayName'],'EXISTING_BRAND_NAME')
check(p['displayName'].encode('utf-8').hex().upper()==p['displayNameUtf8Hex'],'HEX_NAME')
check(p['presentation']['workingArtboardPx']==[1048,1048] and p['presentation']['workingArtboardHex']==['0x0418','0x0418'] and int('0418',16)==1048,'1048_SIZE')
check(p['presentation']['nesReference']=='visual-inspiration-only' and p['presentation']['tileSizeMandate'] is None and p['presentation']['indexedColorLimit'] is None,'NO_NES_LOCK')
check(p['presentation']['rasterMaster'] is False and p['presentation']['output']=='scaleExistingSVGWithoutRasterizing','VECTOR_MASTER')
check(svgfile.is_file() and replica.is_file() and svgfile.read_bytes()==replica.read_bytes(),'NO_DUPLICATE_DRIFT')
check(hashlib.sha256(svgfile.read_bytes()).hexdigest()==p['masterVector']['sha256'],'VECTOR_DIGEST')
root=ET.fromstring(svgfile.read_bytes())
check(root.tag=='{http://www.w3.org/2000/svg}svg' and root.get('viewBox')=='0 0 512 512','SVG_VIEWBOX')
check(not any(e.tag.rsplit('}',1)[-1] in {'script','foreignObject','iframe'} or any(a.lower().startswith('on') or a.lower().endswith('href') for a in e.attrib) for e in root.iter()),'SAFE_SVG')
colors={attr.lower() for e in root.iter() for attr in [e.attrib.get('fill','')] if attr.startswith('#')}
check(colors=={entry['css'] for entry in p['observedColorTokens'].values()},'EXACT_OBSERVED_PALETTE')
check(all(entry['css'][1:].upper()==entry['rgbHex'][2:] for entry in p['observedColorTokens'].values()),'HEX_RGB_CONSISTENCY')
check(p['sql']['newDatabase'] is False and p['sql']['migrationPerformed'] is False and p['sql']['schemaMutation'] is False,'ONE_SQL_NO_MIGRATION')
check(p['bridge']['opcode']=='0xC1' and p['bridge']['noBuildDispatch'] and p['bridge']['noAgentQuarantineChange'],'BRIDGE_STILL_GATED')
check('1048px' in html and '../../../publicationSite/logo.svg' in html and '<script' not in html.lower() and '<iframe' not in html.lower(),'SINGLE_SOURCE_PREVIEW')
print('GREEN_BRAND_HEX_VECTOR_1048_SOURCE_ONLY')
