#!/usr/bin/env bash
# Optional billable Compute Engine boot-disk snapshot. DRY RUN DEFAULT.
set -Eeuo pipefail
MODE="${1:---dry-run}"
[[ "$MODE" == "--dry-run" || "$MODE" == "--apply" ]] || exit 2
PROJECT="${GOOGLE_CLOUD_PROJECT:-PROJECT_NOT_SET}"
ZONE="${GCP_ZONE:-us-central1-a}"
VM="luhm-web-strict-01"
SNAPSHOT="luhm-web-strict-snapshot"
if [[ "$MODE" == "--dry-run" ]]; then
  echo "SOURCE_ONLY_DRY_RUN: gcloud compute disks snapshot $VM --project=$PROJECT --zone=$ZONE --snapshot-names=$SNAPSHOT"
  echo "NO_PROVIDER_CALLS=TRUE; NO_SNAPSHOT_CREATED=TRUE"
  exit 0
fi
[[ "${ALLOW_SNAPSHOT_COSTS:-NO}" == YES && "${GOOGLE_IAM_VERIFIED:-NO}" == YES &&
   "${VM_BOOT_PROOF:-NO}" == YES && "${EXACT_SOURCE_VERIFIED:-NO}" == YES &&
   "${BILLING_ACCOUNT_VERIFIED:-NO}" == YES &&
   "$PROJECT" != PROJECT_NOT_SET && -n "${EXPECTED_GOOGLE_ACCOUNT:-}" ]] || {
  echo RED_SNAPSHOT_COST_OR_IDENTITY_GATE >&2; exit 3; }
command -v gcloud >/dev/null || { echo RED_GCLOUD_UNAVAILABLE >&2; exit 4; }
[[ "$(gcloud config get-value account 2>/dev/null)" == "$EXPECTED_GOOGLE_ACCOUNT" ]] || {
  echo RED_WRONG_GOOGLE_ACCOUNT >&2; exit 5; }
gcloud compute instances describe "$VM" "--project=$PROJECT" "--zone=$ZONE" --format='value(name)' >/dev/null
gcloud compute disks snapshot "$VM" "--project=$PROJECT" "--zone=$ZONE" "--snapshot-names=$SNAPSHOT"
echo 'GCP_DISK_SNAPSHOT_REQUESTED; VERIFY_PROVIDER_RECEIPT_AND_COST'
