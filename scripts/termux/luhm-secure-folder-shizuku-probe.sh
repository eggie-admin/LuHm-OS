#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail
IFS=$'\n\t'
umask 077

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
LUHM_HOME="${HOME}/.luhm"
RECEIPTS="${LUHM_HOME}/receipts"
mkdir -p "$RECEIPTS"
OUT="${1:-$RECEIPTS/secure-folder-shizuku-probe-${STAMP}.json}"

note(){ printf ':: %s\n' "$*" >&2; }

[[ "${PREFIX:-}" == *"termux"* || "${PREFIX:-}" == *"/com.termux/"* ]] || {
  printf 'RED_NOT_TERMUX\n' >&2
  exit 1
}

UID_NOW="$(id -u)"
ANDROID_USER_ID=$(( UID_NOW / 100000 ))
TERMUX_PACKAGE="${LUHM_TERMUX_PACKAGE:-com.termux}"

RISH_PATH=""
for p in \
  "$(command -v rish 2>/dev/null || true)" \
  "${PREFIX:-}/bin/rish" \
  "${HOME}/bin/rish" \
  "${HOME}/.local/bin/rish" \
  "${HOME}/rish"; do
  if [[ -n "$p" && -f "$p" ]]; then
    RISH_PATH="$p"
    break
  fi
done

RISH_AVAILABLE=false
RISH_ID_RC=127
RISH_ID=""
RISH_USERS_RC=127
RISH_USERS=""
RISH_HOME_RC=127
RISH_HOME=""
RISH_ERROR="rish not found"

run_rish(){
  local command_text="$1"
  if command -v timeout >/dev/null 2>&1; then
    RISH_PRESERVE_ENV=0 RISH_APPLICATION_ID="$TERMUX_PACKAGE" \
      timeout 12s "$RISH_PATH" -c "$command_text"
  else
    RISH_PRESERVE_ENV=0 RISH_APPLICATION_ID="$TERMUX_PACKAGE" \
      "$RISH_PATH" -c "$command_text"
  fi
}

if [[ -n "$RISH_PATH" ]]; then
  RISH_ERROR=""
  set +e
  RISH_ID="$(run_rish 'id' 2>&1)"
  RISH_ID_RC=$?
  if [[ "$RISH_ID_RC" -eq 0 ]]; then
    RISH_AVAILABLE=true
  else
    RISH_ERROR="$RISH_ID"
  fi

  RISH_USERS="$(run_rish 'cmd user list' 2>&1)"
  RISH_USERS_RC=$?

  RISH_HOME="$(run_rish "ls -ld '$HOME'" 2>&1)"
  RISH_HOME_RC=$?
  set -e
fi

PROFILE_CLASS="PRIMARY_USER"
if [[ "$ANDROID_USER_ID" -ne 0 ]]; then
  PROFILE_CLASS="SECONDARY_OR_CONTAINER_USER"
fi

SHIZUKU_SCOPE="UNAVAILABLE"
if [[ "$RISH_AVAILABLE" == true ]]; then
  SHIZUKU_SCOPE="BOUNDED_ADB_SHELL_AVAILABLE"
fi

python - "$OUT" \
  "$UID_NOW" "$ANDROID_USER_ID" "$PROFILE_CLASS" "$PREFIX" "$HOME" \
  "$TERMUX_PACKAGE" "$RISH_PATH" "$RISH_AVAILABLE" "$RISH_ID_RC" "$RISH_ID" \
  "$RISH_USERS_RC" "$RISH_USERS" "$RISH_HOME_RC" "$RISH_HOME" "$RISH_ERROR" "$SHIZUKU_SCOPE" <<'PY'
import json, pathlib, sys
(
 out, uid_now, user_id, profile_class, prefix, home, package, rish_path,
 rish_available, rish_id_rc, rish_id, users_rc, users, home_rc, home_probe,
 rish_error, shizuku_scope
) = sys.argv[1:]
payload = {
  "schema": "luhm-os.secure-folder-shizuku-probe.v1",
  "status": "GREEN_DIAGNOSTIC_CAPTURED",
  "profile": {
    "uid": int(uid_now),
    "androidUserId": int(user_id),
    "classification": profile_class,
    "secureFolderConfirmed": False,
    "note": "A nonzero Android user ID is evidence of a secondary/container profile, not by itself proof that the profile is Samsung Secure Folder."
  },
  "termux": {
    "prefix": prefix,
    "home": home,
    "package": package,
    "privateFilesOwnedByTermux": True
  },
  "shizuku": {
    "rishPath": rish_path or "MISSING",
    "rishAvailable": rish_available == "true",
    "scope": shizuku_scope,
    "id": {"rc": int(rish_id_rc), "output": rish_id[:4096]},
    "userList": {"rc": int(users_rc), "output": users[:8192]},
    "termuxHomeProbe": {"rc": int(home_rc), "output": home_probe[:4096]},
    "error": rish_error[:4096],
    "preserveEnv": False
  },
  "authority": {
    "rootClaim": False,
    "knoxBypassClaim": False,
    "crossProfileAccessClaim": False,
    "mutationAuthority": False,
    "publicationAuthority": False,
    "productionSigningAuthority": False,
    "crownStatus": "STOP"
  }
}
path = pathlib.Path(out)
path.write_text(json.dumps(payload, indent=2) + "\n")
print(path)
PY

note "Probe receipt: $OUT"
if [[ "$RISH_AVAILABLE" == true ]]; then
  note "Shizuku/rish probe succeeded as a bounded remote Android shell."
else
  note "Shizuku/rish unavailable from this Termux copy. LuHm bootstrap may still continue in experimental profile mode."
fi
