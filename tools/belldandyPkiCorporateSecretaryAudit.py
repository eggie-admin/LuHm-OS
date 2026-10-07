#!/usr/bin/env python3
import json
from pathlib import Path

rootPath = Path(__file__).resolve().parents[1]
errorList = []

def need(conditionValue, messageValue):
    if not conditionValue:
        errorList.append(messageValue)

pkiDoc = json.loads((rootPath / "doctrine/belldandyPkiCorporateSecretaryV1.json").read_text(encoding="utf-8"))
corporateDoc = json.loads((rootPath / "doctrine/corporateEscalationProfileV1.json").read_text(encoding="utf-8"))
cloudflareDoc = json.loads((rootPath / "doctrine/cloudflareAirTrafficControllerV1.json").read_text(encoding="utf-8"))
belldandySkill = (rootPath / "agents/belldandyQualityOni/SKILL.md").read_text(encoding="utf-8")
lumSkill = (rootPath / "agents/lum/SKILL.md").read_text(encoding="utf-8")
urdSkill = (rootPath / "agents/urdMutationOni/SKILL.md").read_text(encoding="utf-8")
skuldSkill = (rootPath / "agents/skuldResearchOni/SKILL.md").read_text(encoding="utf-8")
runtimeAudit = (rootPath / "tools/certbotWorkspaceSymlinkAudit.py").read_text(encoding="utf-8")

need(pkiDoc.get("owner") == "belldandySecretary", "Belldandy PKI owner drift")
need(pkiDoc.get("training", {}).get("externalCertificationClaim") is False, "external certification claim must remain false")
need(pkiDoc.get("letsEncryptBoundary", {}).get("caHasSubscriberPrivateKey") is False, "Let's Encrypt private-key custody drift")
need(pkiDoc.get("cloudflareBoundary", {}).get("preferredProxiedOriginMode") == "FullStrict", "Cloudflare strict TLS preference missing")
need(pkiDoc.get("googleGuardBoundary", {}).get("role") == "identityAndSessionGuard", "Google Guard boundary missing")

routeValue = pkiDoc.get("escalation", {}).get("caseRoute", [])
need(routeValue == ["lum", "urdDoctorGoddess", "belldandySecretary", "skuldResearch", "lum"], "cabinet PKI escalation route drift")
need(pkiDoc.get("escalation", {}).get("isAuthorityHierarchy") is False, "escalation must not become authority hierarchy")

certbotDoc = pkiDoc.get("certbotCompatibility", {})
need(certbotDoc.get("serviceCertificatePath") == "/etc/letsencrypt/live/<certName>/fullchain.pem", "Certbot fullchain live path drift")
need(certbotDoc.get("servicePrivateKeyPath") == "/etc/letsencrypt/live/<certName>/privkey.pem", "Certbot private-key live path drift")
need(certbotDoc.get("privateKeyContentsMayBeReadByAudit") is False, "runtime audit may read private-key contents")
need(certbotDoc.get("noAssumedCronJob") is True, "legacy cron compatibility became an assumption")

secretOnly = set(pkiDoc.get("pkiMaterial", {}).get("secretReferenceOnly", []))
for requiredName in ("privkeyPem", "acmeAccountKey", "apiToken", "dnsApiToken", "refreshToken", "clientSecret", "tunnelCredential"):
    need(requiredName in secretOnly, f"secret-reference class missing: {requiredName}")

serializedDoc = json.dumps(pkiDoc)
need("-----BEGIN PRIVATE KEY-----" not in serializedDoc, "private PEM bytes found in doctrine")
need("-----BEGIN OPENSSH PRIVATE KEY-----" not in serializedDoc, "SSH private PEM bytes found in doctrine")

corporateRoute = corporateDoc.get("cabinetCaseEscalation", {}).get("route", [])
need(corporateRoute == routeValue, "corporate escalation profile route mismatch")
need(cloudflareDoc.get("tlsLaw", {}).get("preferredProxyEncryptionMode") == "FullStrict", "Cloudflare doctrine missing FullStrict")
need(cloudflareDoc.get("recordsDesk", {}).get("owner") == "belldandySecretary", "Cloudflare records desk not bound to Belldandy")

for phraseValue in ("PKI and corporate secretary desk", "belldandyPkiCorporateSecretaryV1.json"):
    need(phraseValue in belldandySkill, f"Belldandy skill missing: {phraseValue}")
need("Lum -> Urd -> Belldandy -> Skuld -> Lum" in lumSkill, "Lum escalation phrase missing")
need("Belldandy PKI handoff" in urdSkill, "Urd PKI handoff missing")
need("Belldandy PKI upstream escalation" in skuldSkill, "Skuld PKI escalation missing")
need("read_bytes" not in runtimeAudit and "read_text" not in runtimeAudit, "Certbot runtime audit may read certificate/key contents")
need("is_symlink" in runtimeAudit, "Certbot runtime audit does not verify symlink state")

print(json.dumps({
    "schema": "luhmOs.belldandyPkiCorporateSecretaryAudit.v1",
    "status": "GREEN_BELLDANDY_PKI_CANDIDATE" if not errorList else "RED_BELLDANDY_PKI_CANDIDATE",
    "errors": errorList,
    "liveMutation": False,
    "secretValuesRead": False,
    "crownStatus": "STOP"
}, indent=2))
raise SystemExit(1 if errorList else 0)
