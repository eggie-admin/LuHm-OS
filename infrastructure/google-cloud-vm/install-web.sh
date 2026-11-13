#!/usr/bin/env bash
# Idempotent startup script for an approved *private* GCE VM. No provider credentials.
set -Eeuo pipefail
export DEBIAN_FRONTEND=noninteractive
exec 9>/run/lock/luhm-web-install.lock
flock -x 9
if ! command -v nginx >/dev/null 2>&1; then
  # Requires a verified existing outbound package route, e.g. approved Cloud NAT.
  timeout 120 apt-get update -qq
  timeout 120 apt-get install -y -qq --no-install-recommends nginx curl ca-certificates
fi
install -d -m 0755 -o root -g root /srv/luhm-web
cat > /srv/luhm-web/index.html <<'HTML'
<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>LuHm-OS | Private VM Proof</title>
<style>body{margin:0;background:#111322;color:#e8f4ff;font:16px system-ui;padding:24px}
main{max-width:720px;margin:auto;padding:22px;border:1px solid #7e81bc;border-radius:16px}
h1{color:#c8a7ff}p{line-height:1.5}</style></head>
<body><main><h1>LuHm-OS • Crown Cathedral</h1>
<p>Private NGINX bootstrap is responding.</p>
<p>This page does not mean the ChatGPT Site, Google AI provider, public beta,
or physical-device gates are verified.</p><p>CROWN: STOP</p></main></body></html>
HTML
printf 'ok\n' > /srv/luhm-web/healthz
chmod 0644 /srv/luhm-web/index.html /srv/luhm-web/healthz
rm -f /etc/nginx/sites-enabled/default
cat > /etc/nginx/conf.d/luhm-private-web.conf <<'NGINX'
server {
    listen 127.0.0.1:8080;
    server_name _;
    root /srv/luhm-web;
    index index.html;
    autoindex off;
    server_tokens off;
    add_header X-Content-Type-Options nosniff always;
    add_header Referrer-Policy no-referrer always;
    add_header Content-Security-Policy "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'" always;
    location = /healthz { default_type text/plain; }
    location / { try_files $uri $uri/ =404; }
}
NGINX
nginx -t
systemctl enable --now nginx
systemctl reload nginx
curl --fail --silent --show-error --max-time 5 http://127.0.0.1:8080/healthz | grep -Fxq 'ok'
printf '%s\n' 'LUHM_PRIVATE_WEB_BOOTSTRAP_GREEN_LOCAL_ONLY'
