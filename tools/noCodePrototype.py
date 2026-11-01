#!/usr/bin/env python3
"""Local no-code card prototype. No model calls, microphone access or tool execution."""
import argparse
import hashlib
import json
import os
import stat
from pathlib import Path
from typedSqlStub import openStub, addEvent, putText, putBoolean, orderedEvents

CHANNELS = ('chat', 'voiceTranscript', 'assetNote', 'deviceObservation')
SOURCES = ('professorForeground', 'ambientCabin', 'otherSpeaker', 'mediaPlayback', 'unknown')
BLOCKS = {
    'storyboardDraft': {'title': 'Storyboard draft', 'inputs': ['brief'], 'output': 'editableShotList'},
    'assetReview': {'title': 'Asset review', 'inputs': ['assetReference'], 'output': 'provenanceChecklist'},
    'gameSceneDraft': {'title': 'Game scene draft', 'inputs': ['sceneBrief'], 'output': 'sceneSpecification'},
    'deviceCheck': {'title': 'Device check', 'inputs': ['observation'], 'output': 'deviceTestChecklist'},
}

def compileCards(packet):
    """Compile explicitly selected blocks; never infer commands from transcript text."""
    if type(packet) is not dict or set(packet) != {'taskId', 'sourceRef', 'scopeId', 'events'}:
        raise ValueError('invalid packet fields')
    events = packet['events']
    if type(events) is not list or not 1 <= len(events) <= 64:
        raise ValueError('requires 1..64 events')
    cards = []
    with openStub() as db:
        for seq, event in enumerate(events):
            if type(event) is not dict or set(event) != {'eventId', 'channel', 'sourceClass', 'text', 'block'}:
                raise ValueError('invalid event fields')
            channel, source = event['channel'], event['sourceClass']
            if channel not in CHANNELS or source not in SOURCES:
                raise ValueError('unknown input class')
            raw, block = event['text'], event['block']
            if type(raw) is not str or not raw.strip() or len(raw) > 8192:
                raise ValueError('text must contain 1..8192 characters')
            if block is not None and (type(block) is not str or block not in BLOCKS):
                raise ValueError('unknown workflow block')
            # A supplied source label is not speaker authentication or permission.
            draftEligible = channel in ('chat', 'voiceTranscript') and source == 'professorForeground'
            state = 'NEEDS_SELECTION' if draftEligible else 'CONTEXT_ONLY'
            selected = BLOCKS[block] if draftEligible and block else None
            if selected:
                state = 'DRAFT_REVIEW'
            addEvent(db, event['eventId'], packet['taskId'], packet['sourceRef'],
                     packet['scopeId'], 'lum', seq, 1, '1970-01-01T00:00:00Z')
            putText(db, event['eventId'], 'rawText', raw)
            putText(db, event['eventId'], 'channel', channel)
            putBoolean(db, event['eventId'], 'executionAllowed', False)
            cards.append({'eventId': event['eventId'], 'channel': channel,
                          'sourceClass': source, 'rawText': raw, 'state': state,
                          'selectedBlock': block if selected else None,
                          'template': selected, 'executionAllowed': False})
        observed = orderedEvents(db, packet['taskId'], packet['sourceRef'], packet['scopeId'])
    canonical = json.dumps(packet, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    return {'schema': 'luhmOs.noCodePrototype.v1', 'taskId': packet['taskId'],
            'sourceRef': packet['sourceRef'], 'scopeId': packet['scopeId'],
            'inputSha256': hashlib.sha256(canonical.encode()).hexdigest(),
            'status': 'LOCAL_DRAFT_PROTOTYPE', 'eventCount': len(observed), 'cards': cards,
            'timestampPolicy': 'SYNTHETIC_EPOCH_FOR_LOCAL_FIXTURE_ONLY',
            'physicalSamsungProven': False, 'speechRecognitionProven': False,
            'executionAllowed': False, 'publicationAllowed': False}


MAX_DRAFT_BYTES = 1048576
DRAFT_SCHEMA = 'luhmOs.noCodeDraftSave.v1'

def saveDraft(packet, path):
    """Create-only private JSON draft. Never overwrite another revision."""
    receipt = compileCards(packet)
    record = {'schema': DRAFT_SCHEMA, 'packet': packet,
              'inputSha256': receipt['inputSha256']}
    data = (json.dumps(record, ensure_ascii=False, sort_keys=True,
                       separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')
    if len(data) > MAX_DRAFT_BYTES:
        raise ValueError('draft exceeds 1 MiB')
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0)
    fd = os.open(path, flags, 0o600)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
    except BaseException:
        Path(path).unlink(missing_ok=True)
        raise
    return receipt

def loadDraft(path):
    """Verify a bounded local draft and recompile its review-only cards."""
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
    fd = os.open(path, flags)
    with os.fdopen(fd, 'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError('draft must be a regular file')
        data = stream.read(MAX_DRAFT_BYTES + 1)
    if len(data) > MAX_DRAFT_BYTES:
        raise ValueError('draft exceeds 1 MiB')
    record = json.loads(data.decode('utf-8'))
    if type(record) is not dict or set(record) != {'schema', 'packet', 'inputSha256'}:
        raise ValueError('invalid saved draft')
    if record['schema'] != DRAFT_SCHEMA:
        raise ValueError('unsupported saved draft schema')
    receipt = compileCards(record['packet'])
    if record['inputSha256'] != receipt['inputSha256']:
        raise ValueError('saved draft hash mismatch')
    return receipt

def demoPacket():
    return {'taskId': 'premonitionPrototype', 'sourceRef': 'f0cb6ee54066b490c0e80efc2c96200fec76ee2d',
            'scopeId': 'localCardDraft', 'events': [
                {'eventId': 'chatBrief', 'channel': 'chat', 'sourceClass': 'professorForeground',
                 'text': 'Plan a three-shot introduction to my original game world.', 'block': 'storyboardDraft'},
                {'eventId': 'voiceBrief', 'channel': 'voiceTranscript', 'sourceClass': 'professorForeground',
                 'text': 'Draft one room with a character interaction.', 'block': 'gameSceneDraft'},
                {'eventId': 'assetContext', 'channel': 'assetNote', 'sourceClass': 'unknown',
                 'text': 'Original artwork reference; rights review still required.', 'block': None},
                {'eventId': 'deviceContext', 'channel': 'deviceObservation', 'sourceClass': 'unknown',
                 'text': 'Samsung memory and frame-time measurements not yet collected.', 'block': None}]}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--demo', action='store_true')
    group.add_argument('--input', type=Path)
    group.add_argument('--load', type=Path)
    parser.add_argument('--save', type=Path, help='create a new private draft; never overwrite')
    args = parser.parse_args()
    if args.save and args.load:
        parser.error('--save cannot be combined with --load')
    if args.input and args.input.stat().st_size > MAX_DRAFT_BYTES:
        parser.error('packet exceeds 1 MiB')
    try:
        if args.load:
            receipt = loadDraft(args.load)
        else:
            packet = demoPacket() if args.demo else json.loads(args.input.read_text(encoding='utf-8'))
            receipt = saveDraft(packet, args.save) if args.save else compileCards(packet)
        print(json.dumps(receipt, indent=2, ensure_ascii=False, allow_nan=False))
    except (ValueError, TypeError, KeyError, OSError, UnicodeError) as exc:
        parser.exit(2, f'Invalid prototype input: {exc}\n')
