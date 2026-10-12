#!/usr/bin/env python3
"""Python 3 typed local-only SQLite adapter; never starts a public database server."""
from __future__ import annotations
import json, math, re, sqlite3
from decimal import Decimal, InvalidOperation
from pathlib import Path

SQL = Path(__file__).resolve().parents[1] / 'host/api/typedLanesV1.sql'
NAME = re.compile(r'^[a-z][A-Za-z0-9]{0,79}$')
SHA = re.compile(r'^[0-9a-f]{40}$')

def boundedName(value):
    if type(value) is not str or not NAME.fullmatch(value): raise ValueError('invalid camelHump identity')
    return value

def int64(value):
    if type(value) is not int or not -(2**63) <= value < 2**63: raise ValueError('requires signed int64, not bool')
    return value

def openStub(path=':memory:'):
    db=sqlite3.connect(path, timeout=3.0)
    db.row_factory=sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.execute('PRAGMA busy_timeout=3000')
    if path != ':memory:': db.execute('PRAGMA journal_mode=WAL')
    db.executescript(SQL.read_text(encoding='utf8'))
    return db

def addEvent(db,eventId,taskId,sourceRef,scopeId,workerId,sequenceId,eighthNote,observedAt):
    for v in (eventId,taskId,scopeId,workerId): boundedName(v)
    if not isinstance(sourceRef,str) or not SHA.fullmatch(sourceRef): raise ValueError('source ref not exact')
    int64(sequenceId)
    if type(eighthNote) is not int or not 1<=eighthNote<=8: raise ValueError('invalid eighth note')
    if type(observedAt) is not str or not observedAt.endswith('Z') or len(observedAt)>40: raise ValueError('UTC time required')
    db.execute('INSERT INTO streamEvent VALUES(?,?,?,?,?,?,?,?,NULL)',(eventId,taskId,sourceRef,scopeId,workerId,sequenceId,eighthNote,observedAt))

def putNumeric(db,eventId,fieldName,kind,value,scale=6):
    fieldName=boundedName(fieldName)
    if kind=='integer':
        row=(eventId,fieldName,'integer',int64(value),None,None,None)
    elif kind=='float':
        if type(value) is not float or not math.isfinite(value): raise ValueError('finite binary float required')
        row=(eventId,fieldName,'float',None,value,None,None)
    elif kind=='fixed':
        if type(value) is not str or type(scale) is not int or not 0<=scale<=9: raise ValueError('fixed uses decimal string and scale 0..9')
        try:
            num=Decimal(value)
            scaled=num*(10**scale)
            if not num.is_finite() or scaled!=scaled.to_integral_value(): raise ValueError('cannot represent exactly')
            raw=int64(int(scaled))
        except (InvalidOperation, OverflowError) as exc: raise ValueError('bad decimal') from exc
        row=(eventId,fieldName,'fixed',None,None,raw,scale)
    else: raise ValueError('unknown kind')
    db.execute('INSERT INTO numericStream VALUES(?,?,?,?,?,?,?)',row)

def putText(db,eventId,fieldName,value):
    if type(value) is not str or len(value)>16384: raise ValueError('text too large')
    db.execute('INSERT INTO textStream VALUES(?,?,?)',(eventId,boundedName(fieldName),value))

def putBoolean(db,eventId,fieldName,value):
    if value is not None and type(value) is not bool: raise ValueError('strict true false or None')
    db.execute('INSERT INTO booleanStream VALUES(?,?,?)',(eventId,boundedName(fieldName),None if value is None else int(value)))

def putManifest(db,eventId,manifest):
    if type(manifest) is not dict: raise ValueError('manifest object required')
    row=db.execute('SELECT taskId,sourceRef,scopeId FROM streamEvent WHERE eventId=?',(eventId,)).fetchone()
    if row is None or manifest.get('schema')!='luhmOs.aiTaskManifest.v2': raise ValueError('manifest schema or event missing')
    if any(manifest.get(k)!=row[k] for k in ('taskId','sourceRef','scopeId')): raise ValueError('manifest identity mismatch')
    authority=manifest.get('authority')
    if type(authority) is not dict or any(authority.get(k) is not False for k in ('mutation','green','crown')): raise ValueError('no authority from manifest')
    packed=json.dumps(manifest,sort_keys=True,separators=(',',':'),allow_nan=False,ensure_ascii=False)
    db.execute('INSERT INTO aiManifestStream(eventId,manifestJson,manifestSchema,providerId,capabilityId) VALUES(?,?,?,?,?)',
        (eventId,packed,manifest['schema'],boundedName(manifest.get('providerId')),boundedName(manifest.get('capabilityId'))))

def orderedEvents(db,taskId,sourceRef,scopeId,limit=100):
    if type(limit) is not int or not 1<=limit<=500: raise ValueError('bad limit')
    return [dict(x) for x in db.execute('SELECT * FROM streamEvent WHERE taskId=? AND sourceRef=? AND scopeId=? ORDER BY sequenceId,eventId LIMIT ?',
         (taskId,sourceRef,scopeId,limit))]

if __name__=='__main__':
    with openStub() as db:
        names=[r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        print(json.dumps({'status':'LOCAL_STUB_SCHEMA_READY','tables':names,'liveRemoteSql':False,'crown':'STOP'}))