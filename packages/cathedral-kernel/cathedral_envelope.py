"""Canonical zero-cost source-only envelope; no IO other than shared local JSON contract."""
from dataclasses import dataclass
from pathlib import Path
import json
import re

C=json.loads((Path(__file__).parent/'contract.v1.json').read_text(encoding='utf8'))
H=re.compile(r'[0-9a-f]{64}\Z'); S=re.compile(r'[0-9a-f]{40}\Z')
I=re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z')

def normalize_envelope(v):
    if not isinstance(v,dict) or set(v)!=set(C['fields']):raise ValueError('FIELDS')
    if v['schema']!=C['schema']:raise ValueError('SCHEMA')
    if not isinstance(v['sourceRef'],str) or S.fullmatch(v['sourceRef']) is None:raise ValueError('SHA')
    if not all(isinstance(v[k],str) and I.fullmatch(v[k]) for k in ('taskId','scopeId')):raise ValueError('ID')
    if v['origin'] not in C['origins'] or v['tier'] not in C['tiers'] or v['operation'] not in C['operations']:raise ValueError('ROUTE')
    if type(v['costUsd']) is not int or v['costUsd']!=0 or v['approval'] is not False or v['crown']!='STOP':raise ValueError('AUTHORITY')
    hs=v['hashes']
    if not isinstance(hs,list) or len(hs)>C['maxHashes'] or any(not isinstance(h,str) or H.fullmatch(h) is None for h in hs):raise ValueError('HASH_ARRAY')
    if len(set(hs))!=len(hs):raise ValueError('DUPLICATE_HASH')
    return {k:sorted(hs) if k=='hashes' else v[k] for k in C['fields']}

@dataclass(frozen=True)
class CathedralEnvelope:
    """Store immutable validated JSON bytes, not a caller-mutable dict."""
    canonical_json: str
    def __init__(self,value):
        validated=normalize_envelope(value)
        object.__setattr__(self,'canonical_json',json.dumps(validated,separators=(',',':'),ensure_ascii=False))
    def canonical(self):
        return self.canonical_json
    def to_dict(self):
        return json.loads(self.canonical_json)

def source_snapshot(value):
    return {'canonical':CathedralEnvelope(value).canonical(),'sourceOnly':True,'executable':False}
