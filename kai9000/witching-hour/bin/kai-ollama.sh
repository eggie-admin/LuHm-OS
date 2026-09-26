#!/usr/bin/env bash
set -euo pipefail

if [ "${1:-}" != "--crown" ]; then
  echo 'Starting a service is Crown-gated. Re-run with: kai-ollama.sh --crown'
  exit 64
fi
if ! command -v ollama >/dev/null 2>&1; then
  echo 'ollama not installed; no package mutation performed'
  exit 69
fi

export OLLAMA_HOST='127.0.0.1:11434'
export OLLAMA_KEEP_ALIVE="${OLLAMA_KEEP_ALIVE:-2m}"
export OLLAMA_DEBUG='false'

echo 'KAI 9000 // Ollama foreground service'
echo "bind=$OLLAMA_HOST keep_alive=$OLLAMA_KEEP_ALIVE"
echo 'Ctrl-C stops it. No background enablement is performed.'
exec ollama serve
