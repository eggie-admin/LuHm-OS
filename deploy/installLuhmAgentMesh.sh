#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${LUHM_AGENT_ENV_FILE:-/home/eggie/.secrets/luhm-agent.env}"
UNIT_NAME="luhm-agent-mesh.service"
UNIT_SRC="$ROOT/deploy/systemd/luhm-agent-mesh.service.example"
UNIT_DST="/etc/systemd/system/$UNIT_NAME"
VENV="$ROOT/.venv"
LOCK="$ROOT/agents/requirements.lock"
RECEIPT="${LUHM_AGENT_RECEIPT:-/mnt/lum/logs/luhm-agent-host-receipt.json}"

show_plan() {
  cat <<EOF
LuHm Agent Mesh host deployment plan
  source:   $ROOT
  venv:     $VENV
  lock:     $LOCK
  env:      $ENV_FILE  (must already exist; never read or printed by installer)
  unit:     $UNIT_DST
  receipt:  $RECEIPT

No changes were made. Re-run with --apply only after Crown review.
A live OpenAI request is NOT performed by this installer.
EOF
}

if [[ "${1:-}" != "--apply" ]]; then
  show_plan
  exit 0
fi

[[ -f "$ENV_FILE" && ! -L "$ENV_FILE" ]] || { echo 'RED: external agent env file missing or symlinked' >&2; exit 1; }
[[ "$(stat -c '%a' "$ENV_FILE")" == "600" ]] || { echo 'RED: agent env file must be mode 600' >&2; exit 1; }
[[ "$(stat -c '%a' "$(dirname "$ENV_FILE")")" == "700" ]] || { echo 'RED: agent secret directory must be mode 700' >&2; exit 1; }
[[ -f "$UNIT_SRC" ]] || { echo 'RED: systemd source unit missing' >&2; exit 1; }
[[ -f "$LOCK" ]] || { echo 'RED: pinned dependency lock missing' >&2; exit 1; }

python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install --disable-pip-version-check --no-deps -r "$LOCK"
"$VENV/bin/python" -m pip check
"$VENV/bin/python" "$ROOT/agents/luhm_mesh.py" --self-test

TMP_UNIT="$(mktemp)"
trap 'rm -f "$TMP_UNIT"' EXIT
sed "s#/mnt/ai/repo/hydraCore#$ROOT#g" "$UNIT_SRC" > "$TMP_UNIT"

sudo install -D -m 0644 "$TMP_UNIT" "$UNIT_DST"
sudo install -d -o "$(id -un)" -g "$(id -gn)" -m 0750 "$(dirname "$RECEIPT")"
sudo systemctl daemon-reload
sudo systemctl enable "$UNIT_NAME"
sudo systemctl restart "$UNIT_NAME"

"$VENV/bin/python" "$ROOT/tools/agentHostReceipt.py" \
  --env-file "$ENV_FILE" \
  --unit "$UNIT_NAME" \
  --receipt "$RECEIPT" \
  --allow-pending-live

cat <<EOF
HOST SOURCE DEPLOYMENT COMPLETE: AMBER
Live provider smoke remains a separate Crown action:
  $VENV/bin/python $ROOT/tools/agentHostReceipt.py --env-file $ENV_FILE --unit $UNIT_NAME --receipt $RECEIPT --live-smoke
EOF
