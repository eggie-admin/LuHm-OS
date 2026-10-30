# Certificate authority / ACME hold

Cloudflare remains public authoritative. BIND9 stays local/private. Certbot's Cloudflare DNS-01 plugin is optional, not installed or run in this mutation.

A future owner-authorized issuance would use a zone-scoped Cloudflare API token with only DNS edit permissions, saved outside Git at owner-readable mode 0600, e.g. /etc/letsencrypt/cloudflare.ini; the token must never be pasted into logs. Issue/renew only after exact hostname, live ownership, user approval, privacy policy and Cloudflare DNSSEC review. Verify propagation and renewal separately. Do not use a global Cloudflare API key.

Never call certbot --nginx on the headless private-only BIND example or expose the internal vm.luhm.test test namespace as a public zone. Certificates are independent of the app login or Base64 envelope.
