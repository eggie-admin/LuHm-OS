#!/usr/bin/env bash
# Attested development shell. Verify GitHub provenance before execution.
set -euo pipefail
umask 077
if [ "$(id -u)" -eq 0 ]; then echo RED_ROOT_FORBIDDEN >&2; exit 3; fi
HERE="$(cd "$(dirname "$0")" && pwd)"
MANIFEST="$HERE/manifest.json"
if [ ! -f "$MANIFEST" ] || [ -L "$MANIFEST" ]; then echo RED_MANIFEST_MISSING >&2; exit 3; fi
EXPECTED="$(python3 -c 'import json,re,sys; d=json.load(open(sys.argv[1])); s=d.get("sourceRef",""); assert d.get("schema")=="luhmOs.machineDevShellPackage.v1" and re.fullmatch("[0-9a-f]{40}",s) and d.get("crownStatus")=="STOP"; print(s)' "$MANIFEST")"
ROOT="$(git rev-parse --show-toplevel)"
ACTUAL="$(git -C "$ROOT" rev-parse HEAD)"
if [ "$ACTUAL" != "$EXPECTED" ]; then echo RED_SOURCE_REF_MISMATCH >&2; exit 3; fi
if [ ! -f "$ROOT/host/api/typedLanesV1.sql" ]; then echo RED_SQL_CANON_MISSING >&2; exit 3; fi
CMD=help
if [ "$#" -gt 0 ]; then CMD="$1"; shift; fi
case "$CMD" in
  help)
    [ "$#" -eq 0 ] || exit 2
    echo 'LuHm-OS Machine Development Shell'
    echo 'Commands: help | status | tests | sql-snapshot NEW_DIR | container-check'
    echo 'Owner GPG unverified; signed GitHub provenance must be verified externally first.'
    ;;
  status)
    [ "$#" -eq 0 ] || exit 2
    python3 "$ROOT/tools/machineHarnessSeal.py" --source-ref "$EXPECTED"
    ;;
  tests)
    [ "$#" -eq 0 ] || exit 2
    (cd "$ROOT" && python3 -m unittest -v tests.testMachineHarnessSeal tests.testMachineToHumanWizard tests.testTypedSqlStub)
    ;;
  sql-snapshot)
    [ "$#" -eq 1 ] || { echo 'usage: sql-snapshot NEW_DIRECTORY' >&2; exit 2; }
    OUT="$1"
    if [ -e "$OUT" ] || [ -L "$OUT" ]; then echo RED_OUTPUT_EXISTS >&2; exit 3; fi
    mkdir -m 700 -- "$OUT"
    (cd "$ROOT" && python3 tools/canonHexLedger.py --source-ref "$EXPECTED" --all-scales --db "$OUT/canon-hex.db" --report "$OUT/canon-hex.json")
    ;;
  container-check)
    [ "$#" -eq 0 ] || exit 2
    (cd "$ROOT" && LUHM_SOURCE_REF="$EXPECTED" docker compose -f machine-harness/compose.yaml config --quiet)
    ;;
  *) echo RED_UNSUPPORTED_COMMAND >&2; exit 2;;
esac
