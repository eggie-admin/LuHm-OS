#!/usr/bin/env bash
# Strict GCE VM configuration. Dry-run by default, no project billed without gates.
set -Eeuo pipefail
MODE="${1:---dry-run}"
[[ "$MODE" == "--dry-run" || "$MODE" == "--apply" ]] || { echo "usage: $0 [--dry-run|--apply]" >&2; exit 2; }
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="${GOOGLE_CLOUD_PROJECT:-PROJECT_NOT_SET}"
ZONE="${GCP_ZONE:-us-central1-a}"
VM="luhm-web-strict-01"
NETWORK="${GCP_NETWORK:-NETWORK_NOT_SET}"
SUBNET="${GCP_SUBNET:-SUBNET_NOT_SET}"
[[ "$ZONE" == "us-central1-a" || "$ZONE" == "us-east1-b" || "$ZONE" == "us-west1-a" ]] || { echo RED_ZONE_NOT_IN_FREE_TIER_REGION >&2; exit 3; }
ARGS=(compute instances create "$VM" "--project=$PROJECT" "--zone=$ZONE" "--machine-type=e2-micro"
  "--image-family=debian-12" "--image-project=debian-cloud"
  "--boot-disk-type=pd-standard" "--boot-disk-size=30GB"
  "--network-interface=network=$NETWORK,subnet=$SUBNET,no-address"
  "--no-service-account" "--shielded-secure-boot" "--shielded-vtpm"
  "--shielded-integrity-monitoring" "--maintenance-policy=MIGRATE"
  "--metadata=enable-oslogin=TRUE,block-project-ssh-keys=TRUE,serial-port-enable=FALSE"
  "--metadata-from-file=startup-script=$HERE/install-web.sh"
  "--tags=luhm-private-web")
if [[ "$MODE" == "--dry-run" ]]; then
  printf '%s\n' "SOURCE_ONLY_DRY_RUN: gcloud ${ARGS[*]}"
  echo 'NO_PROVIDER_CALLS=TRUE; NO_VM_CREATED=TRUE; NO_NS_OR_BETA_CHANGE=TRUE'
  exit 0
fi
[[ "${ALLOW_VM_COSTS:-NO}" == YES && "${BILLING_ACCOUNT_VERIFIED:-NO}" == YES &&
   "${GOOGLE_IAM_VERIFIED:-NO}" == YES && "${GCP_QUOTA_VERIFIED:-NO}" == YES &&
   "${PRIVATE_APT_EGRESS_VERIFIED:-NO}" == YES ]] || {
  echo 'RED_MISSING_COST_BILLING_IAM_QUOTA_OR_PRIVATE_NAT_GATE' >&2; exit 4; }
[[ "$PROJECT" != PROJECT_NOT_SET && "$NETWORK" != NETWORK_NOT_SET && "$SUBNET" != SUBNET_NOT_SET && -n "${EXPECTED_GOOGLE_ACCOUNT:-}" ]] || {
  echo 'RED_MISSING_EXACT_ACCOUNT_PROJECT_VPC_SUBNET' >&2; exit 5; }
command -v gcloud >/dev/null || { echo 'RED_GCLOUD_UNAVAILABLE' >&2; exit 6; }
[[ "$(gcloud config get-value account 2>/dev/null)" == "$EXPECTED_GOOGLE_ACCOUNT" ]] || {
  echo 'RED_WRONG_GOOGLE_IDENTITY' >&2; exit 7; }
[[ "$(gcloud billing projects describe "$PROJECT" --format='value(billingEnabled)' 2>/dev/null)" == True ]] || {
  echo 'RED_PROJECT_BILLING_NOT_ENABLED_OR_NOT_AUTHORIZED' >&2; exit 8; }
if gcloud compute instances describe "$VM" "--project=$PROJECT" "--zone=$ZONE" --format='value(name)' >/dev/null 2>&1; then
  echo 'RED_REFUSE_OVERWRITE_EXISTING_VM' >&2; exit 9
fi
# No firewall rules, Cloud DNS zones, NAT gateways or public ingress created here.
gcloud "${ARGS[@]}"
echo 'INSTANCE_REQUEST_SENT_PRIVATE_ONLY; VERIFY_BOOTSTRAP_VIA_IAP_AND_DNS_SEPARATELY'
