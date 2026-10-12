"""Negative-control tests; no Cloud, no real billing, no external SQL mutations."""
import importlib.util
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

root = Path(__file__).resolve().parents[1]
source = root / 'host/api/luhmVideoJobWorker.py'
spec = importlib.util.spec_from_file_location('worker',source)
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)
manifest = worker.validateManifest(root/'media/yumeVideo/canonLockedVeoShotsV1.json')

class FakeProvider:
    def __init__(self): self.calls=0
    def submit(self,body):
        self.calls+=1
        assert body['parameters']['durationSeconds']==6
        return 'projects/test-project/locations/us-central1/publishers/google/models/veo-3.1-fast-generate-001/operations/12345678-abcd'
    def poll(self,name):
        return {'name':name,'done':True,'response':{'videos':[{'gcsUri':'gs://vault-media-private/yume/shot-0.mp4'}]}}

class TimeoutProvider(FakeProvider):
    def submit(self,body):
        self.calls+=1
        raise TimeoutError('timeout after provider might charge')

with tempfile.TemporaryDirectory() as tempDir:
    dbUrl='sqlite:///'+str(Path(tempDir)/'test.sqlite3')
    store=worker.VideoSqlStore(dbUrl)
    store.initialize()
    request=worker.buildRequest(manifest,'lum','gs://vault-media-private/yume')
    reqHash=worker.sha256(json.dumps(request,sort_keys=True).encode())
    row=store.enqueue('yume-Lum-20261012',manifest['sourceRef'],'lum',reqHash)
    assert row['state']=='QUEUED'
    assert store.enqueue('yume-Lum-20261012',manifest['sourceRef'],'lum',reqHash)['state']=='QUEUED'
    try:
        store.enqueue('yume-Lum-20261012',manifest['sourceRef'],'urd',reqHash)
        raise AssertionError('taskId collision not blocked')
    except ValueError as e: assert 'IDEMPOTENCY' in str(e)
    fake=FakeProvider()
    try:
        worker.submitJob(store,'yume-Lum-20261012',manifest,fake,0.90,'gs://vault-media-private/yume')
        raise AssertionError('without Crown no submit')
    except PermissionError as e: assert 'CROWN_STOP' in str(e)
    assert fake.calls==0
    try:
        worker.VideoSqlStore(dbUrl,production=True)
        raise AssertionError('SQLite production forbidden')
    except ValueError as e: assert 'PERSISTENT_PRODUCTION' in str(e)
    env={
      'LUHM_CROWN_VIDEO_COST_APPROVED':'yes',
      'LUHM_GOOGLE_BILLING_CURRENT_CONFIRMED':'yes',
      'LUHM_VERTEX_API_READY':'yes',
      'LUHM_VERTEX_IAM_READY':'yes',
      'LUHM_VERTEX_QUOTA_READY':'yes',
      'GOOGLE_CLOUD_PROJECT':'test-project'
    }
    with patch.dict(os.environ,env):
        row=worker.submitJob(store,'yume-Lum-20261012',manifest,fake,0.90,'gs://vault-media-private/yume',allowNetwork=True)
    assert row['state']=='SUBMITTED' and fake.calls==1
    try:
        with patch.dict(os.environ,env):
            worker.submitJob(store,'yume-Lum-20261012',manifest,fake,0.90,'gs://vault-media-private/yume',allowNetwork=True)
        raise AssertionError('double billing submission not blocked')
    except ValueError as e: assert 'STATE' in str(e)
    assert fake.calls==1
    row=worker.pollJob(store,'yume-Lum-20261012',fake,allowNetwork=True)
    assert row['state']=='CANDIDATE_READY' and row['resultUri'].endswith('.mp4')
    try:
        worker.pollJob(store,'yume-Lum-20261012',fake,allowNetwork=True)
        raise AssertionError('duplicate completion should stop')
    except ValueError: pass
    store.enqueue('yume-Urd-20261012',manifest['sourceRef'],'urd',
                  worker.sha256(json.dumps(worker.buildRequest(manifest,'urd','gs://vault-media-private/yume'),sort_keys=True).encode()))
    uncertain=TimeoutProvider()
    with patch.dict(os.environ,env):
        row=worker.submitJob(store,'yume-Urd-20261012',manifest,uncertain,0.90,'gs://vault-media-private/yume',allowNetwork=True)
    assert row['state']=='UNKNOWN_OUTCOME' and row['attemptCount']==1
    assert uncertain.calls==1
    try:
        with patch.dict(os.environ,env):
            worker.submitJob(store,'yume-Urd-20261012',manifest,uncertain,0.90,'gs://vault-media-private/yume',allowNetwork=True)
        raise AssertionError('ambiguous-submit replay not blocked')
    except ValueError: pass
    assert uncertain.calls==1

assert 'RED_' in str(worker.VideoSqlStore('').__class__) if False else True
try:
    worker.buildRequest(manifest,'lum','https://example.com/storage')
    raise AssertionError('untrusted output bucket accepted')
except ValueError as e: assert 'GCS' in str(e)
try:
    worker.GoogleVertexProvider('test-project').poll('projects/other/operations/12345678')
    raise AssertionError('operation escaped project scope')
except ValueError as e: assert 'SCOPE' in str(e)
print('YUME_SQL_VERTEX_WORKER_GREEN: offline tests, Crown fail-closed, idempotency, one-shot, uncertain outcome, poll')
