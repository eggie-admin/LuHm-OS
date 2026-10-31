#!/usr/bin/env python3
"""No-execution, no-cloud 4x4 foundation and 6x6 proof-plan audit for Termux."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / 'doctrine/rootlessCast36V1.json'


def verify(doc):
    errors = []
    def need(ok, code):
        if not ok: errors.append(code)
    need(doc.get('schema') == 'luhmOs.rootlessCast36.v1' and doc.get('state') == 'PROPOSED_SOURCE_ONLY', 'SCHEMA')
    need(doc.get('authority') == 'Professor' and doc.get('repo') == 'eggie-admin/LuHm-OS' and doc.get('crown') == 'STOP', 'CANON')
    foundation = doc.get('foundation', {})
    rows = foundation.get('rows', [])
    columns = foundation.get('columns', [])
    cells = foundation.get('cells', [])
    need(len(rows) == 4 and len(set(rows)) == 4 and len(columns) == 4 and len(set(columns)) == 4, 'FOUR_BY_FOUR')
    need(len(cells) == 16 and {(c.get('row'),c.get('column')) for c in cells} == {(r,c) for r in rows for c in columns}, 'FOUNDATION_COVERAGE')
    need(all(c.get('status') == 'PROPOSED_ONLY' for c in cells), 'FAKE_FOUNDATION_PROOF')
    expansion = doc.get('expansion', {})
    groups = expansion.get('groups', {})
    gates = expansion.get('gates', [])
    need(len(groups) == 6 and all(len(set(x)) == 6 for x in groups.values()) and sum(map(len,groups.values())) == 36, 'SIX_BY_SIX')
    need(expansion.get('total') == 36 and len(gates) == 36 and
         len({g.get('id') for g in gates}) == 36 and
         {(g.get('lane'), g.get('id')) for g in gates} == {(group,k) for group,values in groups.items() for k in values}, 'GATE_SET')
    need(expansion.get('hardwareProven') == 0 and all(g.get('state') == 'CONTRACT_NOT_DEVICE_PROOF' for g in gates), 'FAKE_RUNTIME_GREEN')
    local = doc.get('rootless', {})
    need(local.get('mode') == 'PythonStdlibLoopback' and local.get('host') == '127.0.0.1' and local.get('port') == 8787, 'LOOPBACK_CONTRACT')
    need(local.get('pythonDependencies') == [] and local.get('termuxScript') == 'tools/termuxRootlessCast.sh', 'NONSTANDARD_PYTHON_DEPS')
    for k in ('cloudApisCalled','appInstallAutomated','nativeApkBuilt','requiresRoot','deviceTested'):
        need(local.get(k) is False, 'ROOTLESS_FALSE_PROOF_' + k)
    storage = doc.get('storage', {})
    need(storage.get('engine') == 'SQLite3' and storage.get('layer') == 'UNPRIVILEGED_TERMUX_USER_DATA' and storage.get('wal') is True and storage.get('preparedStatements') is True, 'SQLITE_USERSpace')
    need(storage.get('firmwareWrite') is False and storage.get('migrationReviewed') is False, 'SQLITE_FIRMWARE_OR_FALSE_MIGRATION')
    engines = doc.get('engineChain', {})
    need(engines.get('unreal') == 'FUTURE_FINAL_FORM_EULA_HOLD' and engines.get('godot') == 'NATIVE_ANDROID_RUNTIME_CANDIDATE' and engines.get('python') == 'PRIMARY_LOCAL_CONTROLLER', 'ENGINE_BOUNDARY')
    ai = doc.get('aiBenchmarkLaw', {})
    need(ai.get('runs') == 0 and ai.get('crossVendorScoreClaims') is False and ai.get('relianceOnOpenAiEvalsApiDeprecated') is False and ai.get('noProviderAutoCalls') is True, 'AI_BENCHMARK_TRUTH')
    need(len(ai.get('referenceFrameworks', [])) >= 5 and len(ai.get('localEvalAxes',[])) == 6, 'AI_BENCHMARK_BREADTH')
    persona = doc.get('persona', {})
    need(persona.get('kind') == 'ORIGINAL_ADULT_GOTH_ONI_PROXY' and persona.get('pluginAuthorityClaim') is False and persona.get('realAvatarRigProven') is False, 'AVATAR_REALITY')
    release = doc.get('release', {})
    need(release.get('signedApkWorkflow') == '.github/workflows/samsung-lite-signed-beta.yml' and release.get('ownerKeystoreRequired') is True, 'APK_SIGNING_GATES')
    for k in ('registeredNativeInstallVerified','merge','publish','signAutomatically'):
        need(release.get(k) is False, 'RELEASE_BOUNDARY_' + k)
    return sorted(set(errors))


def inspect_sources():
    errors = []
    expected = [
        'tools/rootlessCastCockpit.py', 'tools/termuxRootlessCast.sh',
        'tests/testRootlessCastCockpit.py', 'tests/testRootlessCast36.py',
        'frontEnd/rootlessCockpit/index.html', 'frontEnd/rootlessCockpit/app.css',
        'frontEnd/rootlessCockpit/app.js', 'frontEnd/rootlessCockpit/manifest.webmanifest',
        'frontEnd/rootlessCockpit/icon.svg', '.github/workflows/samsung-lite-signed-beta.yml',
    ]
    for path in expected:
        if not (ROOT/path).is_file():
            errors.append('MISSING_FILE:'+path)
    rootless = (ROOT/'tools/termuxRootlessCast.sh').read_text(encoding='utf-8')
    if re.search(r'\bsu\s+-c\b|\bpm\s+install\b|\badb\s+install\b|\bgh\s+workflow\s+run\b', rootless):
        errors.append('ROOTLESS_SCRIPT_HAS_INSTALL_OR_PRIVILEGED_SIDE_EFFECT')
    source = (ROOT/'tools/rootlessCastCockpit.py').read_text(encoding='utf-8')
    for anchor in ('ThreadingHTTPServer(("127.0.0.1", port)', 'PRAGMA journal_mode=WAL',
                   'BEGIN IMMEDIATE', 'Content-Security-Policy', 'CROSS_ORIGIN_DENIED',
                   'SELECT node,affinity,revision,history FROM story_state WHERE id=1'):
        if anchor not in source:
            errors.append('MISSING_SECURITY_CONTROL:'+anchor)
    workflow = (ROOT/'.github/workflows/samsung-lite-signed-beta.yml').read_text(encoding='utf-8')
    if 'Owner-held beta keystore' not in workflow or 'Verify exact APK identity and signer' not in workflow:
        errors.append('SIGNED_BETA_WORKFLOW_DRIFT')
    return sorted(set(errors))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source-ref', required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if not re.fullmatch('[a-f0-9]{40}', args.source_ref):
        raise SystemExit('EXACT_SHA_REQUIRED')
    state = subprocess.run(['git','rev-parse','HEAD'], cwd=ROOT,capture_output=True,text=True)
    if state.returncode or state.stdout.strip() != args.source_ref:
        raise SystemExit('EXACT_CHECKOUT_MISMATCH')
    doc = json.loads(POLICY.read_text(encoding='utf-8'))
    errors = verify(doc) + inspect_sources()
    receipt = {'schema':'luhmOs.rootlessCast36Receipt.v1','sourceRef':args.source_ref,
       'status':'PASS_SOURCE_ONLY_CROWN_STOP' if not errors else 'FAIL_SOURCE','errors':sorted(set(errors)),
       'foundationCells':16,'proposedGates':36,'nativeApksBuiltByThisAudit':0,
       'androidDeviceTestsExecuted':0,'modelComparisonsExecuted':0,'sqlFirmwareModifications':0,
       'crown':'STOP','manifestSha256':hashlib.sha256(POLICY.read_bytes()).hexdigest()}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,indent=2))
    if errors:raise SystemExit(2)

if __name__ == '__main__':main()
