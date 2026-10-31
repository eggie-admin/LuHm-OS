#!/usr/bin/env python3
"""Pure source reconciliation of 16 unification threads and established grids."""
import argparse,json,subprocess,hashlib,re
from pathlib import Path
from collections import Counter
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.crownEscalationMatrix import assess as crown
from tools.freeFirstWorkspaceAudit import assess as free
ROOT=Path(__file__).resolve().parents[1]
def inspect(sha):
  p=json.loads((ROOT/'doctrine/cathedralUnificationV1.json').read_text())
  errors=[]
  def ck(v,name):
    if not v:errors.append(name)
  ck(p['schema']=='luhmOs.cathedralUnification.v1' and p['status']=='PROPOSED_SOURCE_ONLY','SCHEMA')
  ck(p['sourceStreams']==['openAi','github','googleAi','sidecars'],'STREAMS')
  ck(p['executionTiers']==['thinClient','localStudio','githubWorkspace','remoteSidecar'],'TIERS')
  ck(len(p['layers'])==4 and [len(l['threads']) for l in p['layers']]==[4]*4,'FOUR_LAYERS')
  threads=[x for l in p['layers'] for x in l['threads']]
  ck(len(set(x[0] for x in threads))==16,'THREAD_UNIQUE')
  for label,path in threads:
    ck(not Path(path).is_absolute() and '..' not in Path(path).parts and
       (ROOT/path).is_file() and (ROOT/path).resolve().is_relative_to(ROOT.resolve()),'PATH_'+label)
  sec=p['security']
  for k in ('driveRead','driveWrite','automaticPaidApi','automaticMerge','automaticDeploy','remoteProxyActivated','samsungRuntimeProven','cloudflareBuildVerified','publicRelease'):
    ck(sec.get(k) is False,'FALSE_GREEN_'+k)
  ck(sec['driveParentAndSevenChildrenAnyoneWriter'] is True and sec['crown']=='STOP','DRIVE_ACL')
  ck(p['sourceProvenance']['pr460Ingested'] is False and p['vendor']['licenseClearance'] is False,'DONOR_LICENSING')
  x=crown(ROOT,json.loads((ROOT/'doctrine/crownEscalationMatrixV1.json').read_text()),sha)
  y=free(json.loads((ROOT/'doctrine/freeFirstFourSourceWorkspaceV1.json').read_text()))
  ck(not x['sourceErrors'] and x['level4x4']['evaluated']==16 and x['level8x8']['evaluated']==64 and x['level16x16']['evaluated']==256,'MATRIX_336')
  ck(not y['policyErrors'] and y['total']==96,'MATRIX_96')
  return {'schema':'luhmOs.unificationSnapshot.v1','sourceRef':sha,'status':'PASS_SOURCE_ONLY' if not errors else 'RED_SOURCE',
      'errors':sorted(set(errors)),'threads':16,'sourceGrid':336,'freeFirstGrid':96,
      'matrix4x4':x['level4x4']['counts'],'matrix8x8':x['level8x8']['counts'],
      'matrix16x16':x['level16x16']['counts'],'crown':'STOP','runtimeVerified':False,'driveAclSafe':False,
      'manifestSha256':hashlib.sha256((ROOT/'doctrine/cathedralUnificationV1.json').read_bytes()).hexdigest()}
def main():
 a=argparse.ArgumentParser();a.add_argument('--source-ref',required=True);a.add_argument('--output',required=True);z=a.parse_args()
 if not re.fullmatch('[a-f0-9]{40}',z.source_ref):raise SystemExit('EXACT_SHA')
 h=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
 if h.returncode or h.stdout.strip()!=z.source_ref:raise SystemExit('CHECKOUT_MISMATCH')
 out=inspect(z.source_ref);dst=Path(z.output);dst.parent.mkdir(parents=True,exist_ok=True)
 dst.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:out[k] for k in ('sourceRef','status','errors','threads','sourceGrid','freeFirstGrid','crown')},indent=2))
 if out['errors']:raise SystemExit(2)
if __name__=='__main__':main()
