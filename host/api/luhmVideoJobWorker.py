#!/usr/bin/env python3
"""Crown-gated, resumable, SQL-backed Vertex video worker. Private candidates only.

Not a public HTTP endpoint. No network unless explicit submit/poll; no autonomous spend.
Google Cloud identity uses Application Default Credentials (workload identity preferred).
SQL URL is provided by the EXISTING approved database at runtime; SQLite is test-only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urlsplit, unquote

sourceRoot = Path(__file__).resolve().parents[2]
sourceManifest = sourceRoot / 'media' / 'yumeVideo' / 'canonLockedVeoShotsV1.json'
expectedModel = 'veo-3.1-fast-generate-001'
expectedRegion = 'us-central1'
shotIds = ('lum', 'urd', 'belldandy', 'skuld')
allowedStates = ('QUEUED', 'SUBMITTING', 'SUBMITTED', 'POLLING', 'CANDIDATE_READY', 'FAILED', 'UNKNOWN_OUTCOME')


def nowUtc():
    return datetime.now(timezone.utc).isoformat()


def sha256(blob):
    return hashlib.sha256(blob).hexdigest()


def validateManifest(path=sourceManifest):
    doc = json.loads(Path(path).read_text(encoding='utf-8'))
    if doc.get('schema') != 'luhmOs.yumeCanonLockedVeoShots.v1':
        raise ValueError('RED_MANIFEST_SCHEMA')
    if doc.get('model') != expectedModel or doc.get('location') != expectedRegion:
        raise ValueError('RED_UNPINNED_PROVIDER_MODEL')
    if doc.get('rights', {}).get('publicAllowed') is not False or doc.get('gates', {}).get('publication') != 'STOP':
        raise ValueError('RED_CROWN_AUTHORITY')
    if [x.get('id') for x in doc.get('shots', [])] != list(shotIds):
        raise ValueError('RED_CHARACTER_SET')
    if not re.fullmatch('[0-9a-f]{40}', doc.get('sourceRef', '')):
        raise ValueError('RED_SOURCE_REF')
    return doc


def buildRequest(doc, shotId, destination):
    shot = next((x for x in doc['shots'] if x['id'] == shotId), None)
    if shot is None:
        raise ValueError('RED_UNKNOWN_CHARACTER')
    if not destination.startswith('gs://') or not re.fullmatch(r'gs://[a-z0-9][a-z0-9._-]{2,221}/[A-Za-z0-9_./-]*', destination):
        raise ValueError('RED_GCS_OUTPUT_REQUIRED')
    consistent = doc['consistency']
    prompt = ' '.join([
        'Original adult fictional character ' + shot['id'] + ' in one six-second shot.',
        consistent['visualLanguage'], shot['characterIdentity'], shot['action'],
        'Camera: ' + shot['camera'], 'Palette: ' + shot['palette'],
        'Preserve distinct facial identity, wardrobe, and hair throughout. No text, logo, music or speech.',
    ])
    return {
        'instances': [{'prompt': prompt}],
        'parameters': {
            'aspectRatio': '9:16', 'resolution': '720p', 'durationSeconds': 6,
            'sampleCount': 1, 'personGeneration': 'allow_adult',
            'generateAudio': False, 'negativePrompt': ', '.join(consistent['forbidden']),
            'storageUri': destination.rstrip('/') + '/' + shotId + '/',
        },
    }


class VideoSqlStore:
    """DB-API SQL adapter; never creates a second production database."""
    def __init__(self, dbUrl, production=False):
        if not dbUrl:
            raise ValueError('RED_EXISTING_SQL_DSN_REQUIRED')
        self.postgres = dbUrl.startswith(('postgresql://', 'postgres://'))
        self.mysql = dbUrl.startswith(('mysql://', 'mariadb://'))
        self.sqlite = dbUrl.startswith('sqlite:///')
        if not (self.postgres or self.mysql or self.sqlite):
            raise ValueError('RED_UNSUPPORTED_EXISTING_SQL_SCHEME')
        if production and not (self.postgres or self.mysql):
            raise ValueError('RED_PERSISTENT_PRODUCTION_SQL_REQUIRED')
        self.dbUrl = dbUrl

    def connect(self):
        if self.postgres:
            try:
                import psycopg
                from psycopg.rows import dict_row
            except ImportError as error:
                raise RuntimeError('RED_PSYCOPG_DEPENDENCY_REQUIRED') from error
            return psycopg.connect(self.dbUrl, row_factory=dict_row)
        if self.mysql:
            try:
                import pymysql
            except ImportError as error:
                raise RuntimeError('RED_PYMYSQL_DEPENDENCY_REQUIRED') from error
            url = urlsplit(self.dbUrl)
            if not url.hostname or not url.path.strip('/'):
                raise ValueError('RED_SQL_DSN_INCOMPLETE')
            return pymysql.connect(host=url.hostname, port=url.port or 3306,
                     user=unquote(url.username or ''),password=unquote(url.password or ''),
                     database=unquote(url.path.lstrip('/')), cursorclass=pymysql.cursors.DictCursor,
                     ssl_verify_cert=True, ssl_verify_identity=True, autocommit=False)
        path = self.dbUrl[len('sqlite:///'):]
        if not path or path == ':memory:':
            raise ValueError('RED_NON_PERSISTENT_SQL')
        conn = sqlite3.connect(path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def statement(self, query):
        return query.replace('?', '%s') if (self.postgres or self.mysql) else query

    def execute(self, conn, query, params=()):
        if self.mysql:
            cursor = conn.cursor()
            cursor.execute(self.statement(query),params)
            return cursor
        return conn.execute(self.statement(query), params)

    def initialize(self):
        if self.sqlite:
            with self.connect() as conn:
                self.execute(conn, """CREATE TABLE IF NOT EXISTS yumeVideoJob (
                    taskId VARCHAR(80) PRIMARY KEY,sourceRef CHAR(40) NOT NULL,
                    shotId VARCHAR(20) NOT NULL,requestHash CHAR(64) NOT NULL,
                    state VARCHAR(40) NOT NULL,operationName VARCHAR(320),
                    resultUri VARCHAR(1500),createdAt VARCHAR(40) NOT NULL,
                    updatedAt VARCHAR(40) NOT NULL,attemptCount INTEGER NOT NULL DEFAULT 0,
                    failureCode VARCHAR(80))""")
                conn.commit()
        else:
            # Never silently migrate an existing Cloud/Postgres/MySQL database.
            # A reviewed DDL migration is required first.
            try:
                with self.connect() as conn:
                    self.execute(conn,'SELECT taskId FROM yumeVideoJob LIMIT 0')
            except Exception:
                raise RuntimeError('RED_EXISTING_SQL_CONNECTION_OR_SCHEMA_UNVERIFIED') from None


    def get(self, taskId):
        with self.connect() as conn:
            row = self.execute(conn, 'SELECT * FROM yumeVideoJob WHERE taskId=?', (taskId,)).fetchone()
            return dict(row) if row else None

    def enqueue(self, taskId, sourceRef, shotId, requestHash):
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{5,79}', taskId):
            raise ValueError('RED_TASK_ID')
        if shotId not in shotIds or not re.fullmatch('[0-9a-f]{40}', sourceRef):
            raise ValueError('RED_SOURCE_OR_SHOT')
        if type(requestHash) is not str or not re.fullmatch('[0-9a-f]{64}', requestHash):
            raise ValueError('RED_REQUEST_HASH')
        stamp = nowUtc()
        with self.connect() as conn:
            self.execute(conn, '''INSERT INTO yumeVideoJob
                (taskId,sourceRef,shotId,requestHash,state,createdAt,updatedAt)
                VALUES (?,?,?,?,'QUEUED',?,?) ''' +
                ('ON DUPLICATE KEY UPDATE taskId=taskId' if self.mysql else 'ON CONFLICT(taskId) DO NOTHING'),
                (taskId, sourceRef, shotId, requestHash, stamp, stamp))
            conn.commit()
        result = self.get(taskId)
        if (result['sourceRef'], result['shotId'], result['requestHash']) != (sourceRef, shotId, requestHash):
            raise ValueError('RED_IDEMPOTENCY_CONFLICT')
        return result

    def transition(self, taskId, fromState, toState, operationName=None, resultUri=None, failureCode=None, countAttempt=False):
        if toState not in allowedStates:
            raise ValueError('RED_STATE')
        with self.connect() as conn:
            cursor = self.execute(conn, '''UPDATE yumeVideoJob
                SET state=?,updatedAt=?,operationName=COALESCE(?,operationName),
                    resultUri=COALESCE(?,resultUri),failureCode=?,attemptCount=attemptCount+?
                WHERE taskId=? AND state=?''',
                (toState, nowUtc(), operationName, resultUri, failureCode, int(countAttempt), taskId, fromState))
            conn.commit()
            if cursor.rowcount != 1:
                raise ValueError('RED_STATE_CONFLICT_OR_REPLAY')
        return self.get(taskId)


def privateReceipt(row):
    # Never leak credentials or prompts into logs. Result URI is private metadata.
    return {k: row.get(k) for k in ('taskId','sourceRef','shotId','requestHash','state','operationName','resultUri','updatedAt','attemptCount','failureCode')}


def requireSubmitAuthority(costCeiling):
    if not 0.90 <= costCeiling <= 1.00:  # bounded one 6-second candidate; not an asserted vendor quote
        raise PermissionError('CROWN_STOP_COST_CEILING_ONE_SHOT')
    for key in ('LUHM_CROWN_VIDEO_COST_APPROVED','LUHM_GOOGLE_BILLING_CURRENT_CONFIRMED',
                'LUHM_VERTEX_API_READY','LUHM_VERTEX_IAM_READY','LUHM_VERTEX_QUOTA_READY'):
        if os.environ.get(key) != 'yes':
            raise PermissionError('CROWN_STOP_' + key)
    projectId = os.environ.get('GOOGLE_CLOUD_PROJECT','')
    if not re.fullmatch('[a-z][a-z0-9-]{5,29}', projectId):
        raise PermissionError('CROWN_STOP_PROJECT_ID')
    return projectId


class GoogleVertexProvider:
    """Headless ADC; no consumer Google API, no gcloud shell token or keys in source."""
    def __init__(self, projectId):
        if not re.fullmatch('[a-z][a-z0-9-]{5,29}',projectId):
            raise ValueError('RED_PROJECT_ID')
        self.projectId = projectId
        self.modelPath = f'projects/{projectId}/locations/{expectedRegion}/publishers/google/models/{expectedModel}'
        self.endpoint = f'https://{expectedRegion}-aiplatform.googleapis.com/v1/' + self.modelPath

    def post(self, suffix, payload):
        try:
            import google.auth
            from google.auth.transport.requests import Request as GoogleRequest
        except ImportError as error:
            raise RuntimeError('RED_GOOGLE_AUTH_DEPENDENCY_REQUIRED') from error
        credentials, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
        credentials.refresh(GoogleRequest())
        token = credentials.token
        if not token:
            raise RuntimeError('RED_GOOGLE_IDENTITY_NOT_AUTHENTICATED')
        # Only a hard-coded endpoint and project can receive credentials.
        request = Request(self.endpoint + suffix,
                          data=json.dumps(payload,separators=(',',':')).encode('utf-8'),
                          headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'}, method='POST')
        try:
            with urlopen(request,timeout=30) as response:
                return json.load(response)
        except HTTPError as error:
            raise RuntimeError('CLOUD_HTTP_' + str(error.code)) from None
        except (URLError,TimeoutError) as error:
            raise RuntimeError('CLOUD_OUTCOME_UNKNOWN') from None

    def submit(self, payload):
        result = self.post(':predictLongRunning',payload)
        name = result.get('name', '')
        if not name.startswith(self.modelPath + '/operations/'):
            raise RuntimeError('CLOUD_OUTCOME_UNKNOWN')
        return name

    def poll(self, operationName):
        if not re.fullmatch(re.escape(self.modelPath) + r'/operations/[A-Za-z0-9-]{8,120}', operationName):
            raise ValueError('RED_OPERATION_SCOPE')
        return self.post(':fetchPredictOperation', {'operationName':operationName})


def submitJob(store, taskId, manifest, provider, costCeiling, destination, allowNetwork=False):
    # User-facing CLI gates cannot be bypassed by SQL; tests may inject a fake provider.
    if not allowNetwork:
        raise PermissionError('CROWN_STOP_SUBMIT_OPT_IN_REQUIRED')
    requireSubmitAuthority(costCeiling)
    row = store.get(taskId)
    if not row or row['state'] != 'QUEUED' or row['sourceRef'] != manifest['sourceRef']:
        raise ValueError('RED_TASK_STATE_OR_SOURCE')
    request = buildRequest(manifest,row['shotId'],destination)
    h = sha256(json.dumps(request,sort_keys=True).encode())
    if row['requestHash'] != h:
        raise ValueError('RED_REQUEST_DRIFT')
    store.transition(taskId,'QUEUED','SUBMITTING',countAttempt=True)
    try:
        operation = provider.submit(request)
    except Exception:
        # A timeout may have been accepted and charged; NEVER auto-retry submission.
        return store.transition(taskId,'SUBMITTING','UNKNOWN_OUTCOME',failureCode='SUBMISSION_UNCERTAIN')
    return store.transition(taskId,'SUBMITTING','SUBMITTED',operationName=operation)


def pollJob(store, taskId, provider, allowNetwork=False):
    if not allowNetwork:
        raise PermissionError('CROWN_STOP_POLL_OPT_IN_REQUIRED')
    row = store.get(taskId)
    if not row or row['state'] not in ('SUBMITTED','POLLING') or not row['operationName']:
        raise ValueError('RED_POLL_JOB_STATE')
    # Atomic state claim prevents concurrent poll from changing status twice.
    if row['state'] == 'SUBMITTED':
        store.transition(taskId,'SUBMITTED','POLLING')
    try:
        response = provider.poll(row['operationName'])
        if response.get('name') != row['operationName']:
            raise ValueError('RED_PROVIDER_OPERATION_MISMATCH')
        if not response.get('done'):
            return store.get(taskId)
        if response.get('error'):
            return store.transition(taskId,'POLLING','FAILED',failureCode='PROVIDER_FAILED')
        videos = response.get('response',{}).get('videos',[])
        uri = videos[0].get('gcsUri','') if len(videos)==1 else ''
        if not re.fullmatch(r'gs://[a-z0-9][a-z0-9._-]{2,221}/[A-Za-z0-9_./-]+\.mp4',uri):
            return store.transition(taskId,'POLLING','FAILED',failureCode='RED_PROVIDER_ASSET_RECEIPT')
        return store.transition(taskId,'POLLING','CANDIDATE_READY',resultUri=uri)
    except Exception:
        # Poll is repeatable using same operation ID, unlike generation submission.
        return store.get(taskId)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Offline-first SQL/Vertex video lifecycle')
    parser.add_argument('action', choices=['doctor','enqueue','status','submit','poll'])
    parser.add_argument('--task-id', default='')
    parser.add_argument('--shot', choices=shotIds,default='lum')
    parser.add_argument('--manifest',type=Path,default=sourceManifest)
    parser.add_argument('--db-url',default=os.getenv('LUHM_EXISTING_SQL_DSN',''))
    parser.add_argument('--gcs-output',default=os.getenv('LUHM_VERTEX_GCS_OUTPUT',''))
    parser.add_argument('--approve-spend',action='store_true')
    parser.add_argument('--cost-ceiling-usd',type=float,default=0.0)
    args=parser.parse_args(argv)
    # Professor's OpenAI-first/GitHub-second correction: legacy Vertex may be
    # inspected offline, but never submitted or polled by this CLI.
    if args.action in ('submit', 'poll'):
        raise PermissionError('CROWN_STOP_VERTEX_DISABLED_OPENAI_FIRST_GITHUB_SECOND')
    doc=validateManifest(args.manifest)
    if args.action=='doctor':
        info={'status':'CHECK_ONLY_NO_NETWORK','sourceRef':doc['sourceRef'],
              'existingSqlConfigured':bool(args.db_url),'cloudProjectPresent':bool(os.getenv('GOOGLE_CLOUD_PROJECT')),
              'gcsOutputConfigured':bool(args.gcs_output),'billingProof':os.getenv('LUHM_GOOGLE_BILLING_CURRENT_CONFIRMED')=='yes',
              'vertexApiProof':os.getenv('LUHM_VERTEX_API_READY')=='yes',
              'readyToSpend':False,'productionVideoCount':0,'crown':'STOP'}
        print(json.dumps(info,indent=2));return 0
    store = VideoSqlStore(args.db_url,production=args.action in ('submit','poll'))
    store.initialize()
    if args.action=='enqueue':
        request = buildRequest(doc,args.shot,args.gcs_output)
        h=sha256(json.dumps(request,sort_keys=True).encode())
        row=store.enqueue(args.task_id,doc['sourceRef'],args.shot,h)
    elif args.action=='status':
        row=store.get(args.task_id)
        if row is None: raise ValueError('RED_TASK_NOT_FOUND')
    elif args.action=='submit':
        if not args.approve_spend: raise PermissionError('CROWN_STOP_APPROVE_SPEND_REQUIRED')
        project=requireSubmitAuthority(args.cost_ceiling_usd)
        row=submitJob(store,args.task_id,doc,GoogleVertexProvider(project),args.cost_ceiling_usd,args.gcs_output,allowNetwork=True)
    else:
        project=os.getenv('GOOGLE_CLOUD_PROJECT','')
        if not project: raise PermissionError('CROWN_STOP_GOOGLE_PROJECT_REQUIRED')
        row=pollJob(store,args.task_id,GoogleVertexProvider(project),allowNetwork=True)
    print(json.dumps({'schema':'luhmOs.videoJobReceipt.v1','result':privateReceipt(row),'publicationAuthority':False},indent=2))
    return 0

if __name__ == '__main__':
    try: sys.exit(main())
    except (ValueError, PermissionError, RuntimeError) as error:
        print(str(error),file=sys.stderr)
        sys.exit(2)
