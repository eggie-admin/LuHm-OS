#!/usr/bin/env bash
set -u
umask 077

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE_DIR="${KAI_STATE_DIR:-$HOME/.local/state/kai9000}"
RECEIPT_DIR="$STATE_DIR/receipts"
SNAPSHOT_DIR="$STATE_DIR/snapshots"
KAI_HEALTH_URL="${KAI_HEALTH_URL:-http://127.0.0.1:8000/health}"
STAMP="$(date +%Y%m%dT%H%M%S%z)"
RUN_DIR="$RECEIPT_DIR/$STAMP"
mkdir -p "$RUN_DIR" "$SNAPSHOT_DIR"

pass=0
fail=0
amber=0
results=()
record() {
  local name="$1" status="$2" note="$3"
  results+=("$name|$status|$note")
  case "$status" in
    GREEN) pass=$((pass+1));;
    RED) fail=$((fail+1));;
    *) amber=$((amber+1));;
  esac
  printf '%-28s %-6s %s\n' "$name" "$status" "$note"
}

printf 'KAI 9000 // WITCHING HOUR DOCTOR\n'
printf 'receipt: %s\n\n' "$RUN_DIR"

# Evidence capture. Probe failures are recorded, not hidden.
if command -v termux-info >/dev/null 2>&1; then termux-info >"$RUN_DIR/termux-info.txt" 2>&1; else printf 'termux-info unavailable\n' >"$RUN_DIR/termux-info.txt"; fi
if command -v dpkg-query >/dev/null 2>&1; then dpkg-query -W -f='${binary:Package}\t${Version}\n' >"$RUN_DIR/packages.tsv" 2>&1; else : >"$RUN_DIR/packages.tsv"; fi
{
  for f in "${PREFIX:-}/etc/apt/sources.list" "${PREFIX:-}/etc/apt/sources.list.d"/*.list; do
    [ -f "$f" ] || continue
    printf '### %s\n' "$f"
    cat "$f"
  done
} >"$RUN_DIR/apt-sources.txt" 2>&1

if command -v ss >/dev/null 2>&1; then ss -ltnp >"$RUN_DIR/listeners.txt" 2>&1; elif command -v netstat >/dev/null 2>&1; then netstat -ltn >"$RUN_DIR/listeners.txt" 2>&1; else printf 'listener tool unavailable\n' >"$RUN_DIR/listeners.txt"; fi

if command -v ollama >/dev/null 2>&1; then ollama --version >"$RUN_DIR/ollama-version.txt" 2>&1; else printf 'ollama unavailable\n' >"$RUN_DIR/ollama-version.txt"; fi
if command -v curl >/dev/null 2>&1; then
  curl -fsS --max-time 3 http://127.0.0.1:11434/api/version >"$RUN_DIR/ollama-api-version.json" 2>"$RUN_DIR/ollama-api-version.err" || true
  curl -fsS --max-time 5 http://127.0.0.1:11434/api/tags >"$RUN_DIR/ollama-models.json" 2>"$RUN_DIR/ollama-models.err" || true
  curl -fsS --max-time 3 "$KAI_HEALTH_URL" >"$RUN_DIR/kai-health.json" 2>"$RUN_DIR/kai-health.err" || true
else
  printf 'curl unavailable\n' >"$RUN_DIR/ollama-api-version.err"
  printf 'curl unavailable\n' >"$RUN_DIR/kai-health.err"
fi

ps -A -o pid=,args= 2>/dev/null | grep -E '[X]vnc|[t]igervnc|[v]ncserver|[w]ebsockify|[k]ai|[o]llama' >"$RUN_DIR/processes.txt" || true
if command -v getenforce >/dev/null 2>&1; then getenforce >"$RUN_DIR/selinux.txt" 2>&1 || true; else printf 'not observable\n' >"$RUN_DIR/selinux.txt"; fi
if command -v sv >/dev/null 2>&1 && [ -d "${PREFIX:-}/var/service" ]; then
  for svc in "${PREFIX:-}/var/service"/*; do [ -e "$svc" ] && sv status "$svc"; done >"$RUN_DIR/runit.txt" 2>&1 || true
else
  printf 'runit inactive or unavailable\n' >"$RUN_DIR/runit.txt"
fi

# Pass 1: source authority.
if [ -s "$ROOT/manifest.json" ] && grep -q 'KAI9000_WITCHING_HOUR_FORGE' "$ROOT/manifest.json"; then
  record source_authority GREEN 'forge manifest present'
else
  record source_authority RED 'forge manifest missing or wrong'
fi

# Pass 2 + 3: project scope and runtime separation are static contract checks.
if grep -q '"target_project": "KAI 9000"' "$ROOT/manifest.json" && grep -q '"merge_into_luhm_os": false' "$ROOT/manifest.json"; then
  record project_scope GREEN 'KAI 9000 only; quarantine preserved'
else
  record project_scope RED 'scope contract drift'
fi
if grep -q '"termux_execution_bridge_in_android_runtime": false' "$ROOT/manifest.json"; then
  record runtime_separation GREEN 'Termux remains outside native Android runtime'
else
  record runtime_separation RED 'runtime boundary drift'
fi

# Pass 4: package/source identity.
if command -v termux-info >/dev/null 2>&1 && [ -s "$RUN_DIR/packages.tsv" ]; then
  if grep -Eqi 'root(-|[[:space:]])?repo|packages\.termux\.dev/apt/termux-root' "$RUN_DIR/apt-sources.txt"; then
    record termux_package_source RED 'root repository detected'
  else
    record termux_package_source GREEN 'Termux identity + package manifest captured; no root repo detected'
  fi
else
  record termux_package_source AMBER 'Termux/package identity incomplete'
fi

# Pass 5: network binding. Ollama must be active and loopback-only. VNC may be off.
listeners="$(cat "$RUN_DIR/listeners.txt")"
if printf '%s\n' "$listeners" | grep -Eq '(^|[[:space:]])(0\.0\.0\.0|\*|\[::\]|::):?(11434|5901|6080)([[:space:]]|$)'; then
  record network_binding RED 'public Ollama/VNC/websockify listener detected'
elif [ -s "$RUN_DIR/ollama-api-version.json" ] && printf '%s\n' "$listeners" | grep -Eq '127\.0\.0\.1:11434|\[::1\]:11434'; then
  if printf '%s\n' "$listeners" | grep -Eq ':5901([[:space:]]|$)' && ! printf '%s\n' "$listeners" | grep -Eq '127\.0\.0\.1:5901|\[::1\]:5901'; then
    record network_binding RED 'VNC active without loopback proof'
  else
    record network_binding GREEN 'Ollama loopback proven; VNC is off or loopback-only'
  fi
else
  record network_binding AMBER 'Ollama loopback listener/API not yet proven'
fi

# Pass 6: privilege boundary.
uid="$(id -u 2>/dev/null || printf unknown)"
selinux="$(tr -d '\r\n' <"$RUN_DIR/selinux.txt")"
if [ "$uid" = '0' ]; then
  record privilege_boundary RED 'running as root'
elif [ "$selinux" = 'Disabled' ]; then
  record privilege_boundary RED 'SELinux disabled'
else
  record privilege_boundary GREEN "non-root; SELinux=${selinux:-unknown}"
fi

# Pass 7: headless service health.
if [ -s "$RUN_DIR/ollama-api-version.json" ] && [ -s "$RUN_DIR/kai-health.json" ]; then
  record headless_service_health GREEN 'Ollama API and KAI health responded without GUI dependency'
else
  record headless_service_health AMBER 'Ollama API and/or KAI health not responding'
fi

# Pass 8: update/rollback requires a local snapshot receipt. No upgrade is performed here.
latest_snapshot="$(find "$SNAPSHOT_DIR" -maxdepth 1 -type f -name 'snapshot-*.sha256' -print 2>/dev/null | sort | tail -n 1)"
if [ -n "$latest_snapshot" ] && [ -s "$latest_snapshot" ]; then
  cp "$latest_snapshot" "$RUN_DIR/latest-snapshot.sha256"
  record update_and_rollback GREEN 'local rollback snapshot receipt present'
else
  record update_and_rollback AMBER 'run forge snapshot --crown after this probe'
fi

# Pass 9: receipts and hashes.
(
  cd "$RUN_DIR"
  sha256sum termux-info.txt packages.tsv apt-sources.txt listeners.txt ollama-version.txt processes.txt selinux.txt runit.txt 2>/dev/null || true
  [ -f ollama-api-version.json ] && sha256sum ollama-api-version.json || true
  [ -f ollama-models.json ] && sha256sum ollama-models.json || true
  [ -f kai-health.json ] && sha256sum kai-health.json || true
) >"$RUN_DIR/evidence.sha256"
if [ -s "$RUN_DIR/evidence.sha256" ]; then
  record receipts_and_hashes GREEN 'evidence hash receipt generated'
else
  record receipts_and_hashes RED 'could not hash evidence'
fi

# Pass 10: deterministic seal. This seals evidence only; it does not promote runtime authority.
status='AMBER'
if [ "$fail" -gt 0 ]; then status='RED'; elif [ "$amber" -eq 0 ]; then status='GREEN'; fi
{
  printf 'schema=kai9000.witching-hour.receipt.v1\n'
  printf 'timestamp=%s\n' "$STAMP"
  printf 'status=%s\n' "$status"
  printf 'green=%s\nred=%s\namber=%s\n' "$pass" "$fail" "$amber"
  printf 'human_promotion_required=true\n'
  for row in "${results[@]}"; do printf 'pass=%s\n' "$row"; done
} >"$RUN_DIR/receipt.env"
sha256sum "$RUN_DIR/receipt.env" >"$RUN_DIR/receipt.sha256"
record seal_and_save GREEN "evidence sealed locally; runtime result=$status"

printf '\nWITCHING HOUR RESULT: %s\n' "$status"
printf 'Evidence: %s\n' "$RUN_DIR"
case "$status" in
  GREEN) printf 'All runtime evidence gates are proven. Human promotion is still separate.\n'; exit 0;;
  AMBER) printf 'Proof is incomplete. No mutation or promotion was inferred.\n'; exit 2;;
  RED) printf 'Hard gate failed. Fail closed.\n'; exit 1;;
esac
