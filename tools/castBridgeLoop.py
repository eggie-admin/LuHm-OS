#!/usr/bin/env python3
"""Bounded source-audit tick. Never merges, signs, deploys or grants CAST."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

try:
    from .escalationKernel import plan
except ImportError:
    from escalationKernel import plan

ROOT = Path(__file__).resolve().parents[1]
LADDERS = (
    ('machine', 'tools/escalationKernelAudit.py'),
    ('humanMachine', 'tools/architectureRhythmAudit.py'),
    ('humanHuman', 'tools/continuity-release-lifecycle-audit.py'),
    ('automatedStudio', 'tools/gameplayVerticalSliceAudit.py'),
)
CANON = ('currentSourceTruthV3.json', 'everlastingCovenantV1.json',
         'escalationKernelV1.json', 'milestoneTaskQueueV1.json')


def tick(source, previous, run, source_now):
    """Injected runner permits deterministic failure/recovery tests.

    Previous state controls retry budgets only, never supplies GREEN proof.
    A blocked ladder does not prevent independent source audits.
    """
    if len(source) != 40 or any(c not in '0123456789abcdef' for c in source):
        raise ValueError('exact source required')
    if previous.get('sourceRef') != source:
        previous = {}
    rows = []
    old = {r['ladder']: r for r in previous.get('checks', [])}
    for ladder, script in LADDERS:
        prior = old.get(ladder, {})
        tier = prior.get('tier', 0)
        failures = prior.get('failures', 0)
        if type(tier) is not int or not 0 <= tier <= 3 or type(failures) is not int or not 0 <= failures <= 3:
            raise ValueError('invalid retry state')
        row = {'ladder': ladder, 'tier': tier, 'failures': failures}
        rows.append(row)
        if source_now() != source:
            row.update(status='AMBER', nextAction='restartAtNewSource')
            break
        if failures >= 3:
            row.update(status='BLOCKED', nextAction='diagnoseAndPrepareBoundedRepair')
            continue
        result = run(script)
        row.update(result)
        if result['status'] != 'GREEN':
            failures += 1
            escalation = plan('technology', tier, 'blocked')
            row.update(failures=failures, tier=escalation['nextTier'],
                       nextAction='diagnoseAndPrepareBoundedRepair' if failures >= 3 else 'retryNextTick')
            continue
        row.update(failures=0, tier=plan('technology', tier, 'green')['nextTier'],
                   nextAction='sourceCheckComplete')
        continue
    stable = source_now() == source
    all_green = stable and len(rows) == 4 and all(r['status'] == 'GREEN' for r in rows)
    return {'schema': 'luhmOs.castBridgeLoop.v1', 'sourceRef': source,
            'checks': rows, 'sourceStable': stable,
            'testingSourceStatus': 'GREEN' if all_green else 'AMBER',
            'proposedStatus': 'AMBER_MISSING_BUILD_AND_RUNTIME_PROOF',
            'requiredExternalProof': ['testingArtifact', 'reproducibleProposedArtifact',
                'ownerSigning', 'samsungLaunchSaveResumeUpgrade', 'playInternalInstall'],
            'castStatus': 'WAIT_FOR_PROFESSOR', 'releaseAuthorized': False}


def head():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()


def execute(script):
    try:
        p = subprocess.run([sys.executable, script], cwd=ROOT, capture_output=True,
                           text=True, timeout=180)
        return {'status': 'GREEN' if p.returncode == 0 else 'RED',
                'exitCode': p.returncode, 'outputTail': (p.stdout + p.stderr)[-3000:]}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'status': 'RED', 'error': type(exc).__name__}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--state', default='build/castBridgeLoop/state.json')
    args = parser.parse_args()
    # A modified worktree cannot produce exact-commit evidence.
    dirty = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=normal'], cwd=ROOT, text=True)
    if dirty.strip():
        raise SystemExit('STOP: commit candidate before collecting exact-source evidence')
    digests = {}
    for name in CANON:
        p = ROOT / 'doctrine' / name
        json.loads(p.read_text())
        digests[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    state = Path(args.state)
    previous = json.loads(state.read_text()) if state.exists() else {}
    receipt = tick(head(), previous, execute, head)
    receipt['canonSha256'] = digests
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))
    return 0 if receipt['testingSourceStatus'] == 'GREEN' else 1


if __name__ == '__main__':
    raise SystemExit(main())
