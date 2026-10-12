import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
SRC=ROOT/'tools'/'yumeVertexVeoQueue.py'
MANIFEST=ROOT/'media'/'yumeVideo'/'canonLockedVeoShotsV1.json'
spec=importlib.util.spec_from_file_location('queue',SRC)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
manifest=module.load_manifest(MANIFEST)
assert len(manifest['shots']) == 4
assert {s['id'] for s in manifest['shots']} == {'lum','urd','belldandy','skuld'}
prompts=[]
for shot in manifest['shots']:
  body=module.make_request(manifest,shot)
  assert len(body['instances'])==1
  assert body['parameters']['durationSeconds']==6
  assert body['parameters']['aspectRatio']=='9:16'
  assert 'storageUri' not in body['parameters']
  assert body['parameters']['personGeneration']=='allow_adult'
  assert shot['id'] in body['instances'][0]['prompt']
  prompts.append(body['instances'][0]['prompt'])
assert len(set(prompts))==4
with tempfile.TemporaryDirectory() as tmp:
  output=pathlib.Path(tmp)/'plan.json'
  dry=subprocess.run([sys.executable,str(SRC),'--manifest',str(MANIFEST),'--shot','urd','--output',str(output)],capture_output=True,text=True)
  assert dry.returncode==0,dry.stderr
  assert json.loads(output.read_text())['status']=='DRY_RUN_NO_NETWORK_NO_CHARGE'
  forbidden=subprocess.run([sys.executable,str(SRC),'--manifest',str(MANIFEST),'--submit','--shot','urd'],capture_output=True,text=True)
  assert forbidden.returncode!=0
  assert 'CROWN_STOP' in forbidden.stderr
print('SOURCE_DRY_RUN_AND_CROWN_STOP_OK: 4 distinct shots; no network; no spend')
