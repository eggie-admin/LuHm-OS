#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail
IFS=$'\n\t'
umask 077

EXPECTED_MAIN="f22681b905bd5bc0cf84da5e3d1e865a855b5fc2"
EXPECTED_BASE="cb0f53c9dfc8aedf6852a77e60f41634f8d18bab"
CANDIDATE_BRANCH="candidate/coding-roleplay-v3-termux-20260930"
REPO_URL="https://github.com/eggie-admin/LuHm-OS.git"
LUHM_HOME="${HOME}/.luhm"
CANDIDATE="${LUHM_HOME}/candidates/roleplay-v3"
RECEIPTS="${LUHM_HOME}/receipts"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TMP="${TMPDIR:-$PREFIX/tmp}/luhm-roleplay-v3-${STAMP}"
SECURE_EXPERIMENT="${LUHM_SECURE_FOLDER_EXPERIMENT:-0}"

die() { printf 'RED: %s\n' "$*" >&2; exit 1; }
note() { printf ':: %s\n' "$*"; }

[[ "${PREFIX:-}" == *"termux"* || "${PREFIX:-}" == *"/com.termux/"* ]] || die "This installer is for Termux."

UID_NOW="$(id -u)"
ANDROID_USER_ID=$(( UID_NOW / 100000 ))
PROFILE_MODE="PRIMARY_USER"

if [[ "$ANDROID_USER_ID" -ne 0 ]]; then
  PROFILE_MODE="SECONDARY_OR_CONTAINER_USER"
  [[ "$SECURE_EXPERIMENT" == "1" ]] || die "Secondary/container Android user detected (userId=$ANDROID_USER_ID). Re-run with LUHM_SECURE_FOLDER_EXPERIMENT=1 only when you intentionally want the Secure Folder experimental lane."
  note "Secure Folder experimental lane enabled for androidUserId=$ANDROID_USER_ID."
fi

for cmd in git python jq; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    note "Installing missing dependency: $cmd"
    pkg install -y "$cmd"
  fi
done

mkdir -p "$LUHM_HOME/candidates" "$RECEIPTS" "$LUHM_HOME/backups"
rm -rf "$TMP"
mkdir -p "$TMP"

note "Fetching candidate and exact canonical base"
git clone --filter=blob:none --no-checkout "$REPO_URL" "$TMP/repo"
git -C "$TMP/repo" fetch --prune origin \
  "+refs/heads/main:refs/remotes/origin/main" \
  "+refs/heads/${CANDIDATE_BRANCH}:refs/remotes/origin/${CANDIDATE_BRANCH}"

REMOTE_MAIN="$(git -C "$TMP/repo" rev-parse refs/remotes/origin/main)"
[[ "$REMOTE_MAIN" == "$EXPECTED_MAIN" ]] || die "Canonical main moved: expected $EXPECTED_MAIN got $REMOTE_MAIN. Refuse stale install."

CANDIDATE_REF="refs/remotes/origin/${CANDIDATE_BRANCH}"
CANDIDATE_SHA="$(git -C "$TMP/repo" rev-parse "$CANDIDATE_REF")"
[[ "$CANDIDATE_SHA" == "$EXPECTED_BASE" ]] || die "Roleplay candidate moved: expected $EXPECTED_BASE got $CANDIDATE_SHA. Refuse unreviewed drift."

git -C "$TMP/repo" checkout --detach "$CANDIDATE_SHA"

for required in \
  agents/shared/ONI_PROTOCOL_V2.md \
  doctrine/CODING_ROLEPLAY_SYSTEM_V3.json \
  doctrine/TERMUX_OUTSIDE_SECURE_DEV_WORKFLOW_V1.json \
  doctrine/ONI_MESH_CONTROL_PLANE_V2.json \
  plugins/luhm-os/skills/luhm-agent-workflow/SKILL.md \
  plugins/luhm-os/skills/luhm-coding-roleplay/SKILL.md \
  tools/lumTaskRouter.py \
  tools/luhmRoleplayAudit.py \
  tools/luhmTermuxCli.py; do
  [[ -s "$TMP/repo/$required" ]] || die "Candidate missing $required"
done

if [[ -e "$CANDIDATE" ]]; then
  mv "$CANDIDATE" "$LUHM_HOME/backups/roleplay-v3-${STAMP}"
fi
mkdir -p "$CANDIDATE"

note "Deploying Oni skills and deterministic logic"
cp -a "$TMP/repo/agents" "$CANDIDATE/"
mkdir -p "$CANDIDATE/doctrine" "$CANDIDATE/tools" "$CANDIDATE/plugins/luhm-os"
cp "$TMP/repo/doctrine/CODING_ROLEPLAY_SYSTEM_V3.json" "$CANDIDATE/doctrine/"
cp "$TMP/repo/doctrine/TERMUX_OUTSIDE_SECURE_DEV_WORKFLOW_V1.json" "$CANDIDATE/doctrine/"
cp "$TMP/repo/doctrine/ONI_MESH_CONTROL_PLANE_V2.json" "$CANDIDATE/doctrine/"
cp -a "$TMP/repo/plugins/luhm-os/skills" "$CANDIDATE/plugins/luhm-os/"
cp "$TMP/repo/tools/lumTaskRouter.py" "$CANDIDATE/tools/"
cp "$TMP/repo/tools/luhmRoleplayAudit.py" "$CANDIDATE/tools/"
cp "$TMP/repo/tools/luhmTermuxCli.py" "$CANDIDATE/tools/"

cat > "$PREFIX/bin/luhm" <<'WRAP'
#!/data/data/com.termux/files/usr/bin/bash
exec python "$HOME/.luhm/candidates/roleplay-v3/tools/luhmTermuxCli.py" "$@"
WRAP
chmod 700 "$PREFIX/bin/luhm"

note "Running candidate audit"
python "$CANDIDATE/tools/luhmRoleplayAudit.py" | tee "$RECEIPTS/roleplay-audit-${STAMP}.json"

SHIZUKU_RECEIPT="NOT_RUN"
PROBE="${LUHM_SECURE_FOLDER_PROBE:-}"
if [[ "$SECURE_EXPERIMENT" == "1" && -n "$PROBE" && -x "$PROBE" ]]; then
  SHIZUKU_RECEIPT="$RECEIPTS/secure-folder-shizuku-probe-${STAMP}.json"
  "$PROBE" "$SHIZUKU_RECEIPT"
fi

python - "$CANDIDATE" "$RECEIPTS/install-${STAMP}.json" "$CANDIDATE_SHA" "$EXPECTED_MAIN" "$PROFILE_MODE" "$ANDROID_USER_ID" "$SECURE_EXPERIMENT" "$SHIZUKU_RECEIPT" <<'PY'
import hashlib, json, pathlib, sys
candidate=pathlib.Path(sys.argv[1])
out=pathlib.Path(sys.argv[2])
candidate_sha=sys.argv[3]
base=sys.argv[4]
profile_mode=sys.argv[5]
android_user_id=int(sys.argv[6])
secure_experiment=sys.argv[7] == "1"
shizuku_receipt=sys.argv[8]
files=[]
for p in sorted(x for x in candidate.rglob("*") if x.is_file()):
    files.append({"path":str(p.relative_to(candidate)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
receipt={
  "schema":"luhm-os.termux-roleplay-install-receipt.v2",
  "status":"GREEN_LOCAL_CANDIDATE_INSTALLED",
  "androidUserId":android_user_id,
  "profileMode":profile_mode,
  "secureFolderExperimentalMode":secure_experiment,
  "secureFolderConfirmed":False,
  "canonicalBase":base,
  "candidateSha":candidate_sha,
  "candidate":"roleplay-v3",
  "files":files,
  "shizukuProbeReceipt":shizuku_receipt,
  "authority":"Professor",
  "mutationAuthority":False,
  "releaseAuthority":False,
  "publicationAuthority":False,
  "productionSigningAuthority":False,
  "rootClaim":False,
  "knoxBypassClaim":False,
  "crossProfileAccessClaim":False,
  "autonomousDaemonClaim":False,
  "crownStatus":"STOP"
}
out.write_text(json.dumps(receipt,indent=2)+"\n")
print(out)
PY

rm -rf "$TMP"
note "Installed skill/logic candidate in $PROFILE_MODE. No push/merge/sign/publish/public exposure performed."
note "Try: luhm status ; luhm roster ; luhm route read --truth-sensitive ; luhm doctor ; luhm roleplay"
