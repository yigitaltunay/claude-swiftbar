#!/usr/bin/env bash
# Copy claude_usage.py into SwiftBar's plugin folder; seed .env from repo .env when present.
# Run from the repo root: ./install-plugin.sh
# Overwrite Plugins .env from repo: SYNC_ENV=1 ./install-plugin.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$ROOT/claude_usage.5m.py"
DEFAULT_PLUGINS="$HOME/Library/Application Support/SwiftBar/Plugins"

if [[ ! -f "$SRC" ]]; then
  echo "error: missing $SRC" >&2
  exit 1
fi

if PLUGINS=$(defaults read com.ameba.SwiftBar PluginDirectory 2>/dev/null); then
  :
else
  PLUGINS="$DEFAULT_PLUGINS"
fi

mkdir -p "$PLUGINS"
cp "$SRC" "$PLUGINS/"
chmod +x "$PLUGINS/claude_usage.5m.py"

if [[ -n "${SYNC_ENV:-}" ]]; then
  if [[ -f "$ROOT/.env" ]]; then
    cp "$ROOT/.env" "$PLUGINS/.env"
    echo "SYNC_ENV: copied $ROOT/.env → $PLUGINS/.env"
  else
    echo "SYNC_ENV set but $ROOT/.env not found — left $PLUGINS/.env as-is." >&2
  fi
elif [[ ! -f "$PLUGINS/.env" ]]; then
  if [[ -f "$ROOT/.env" ]]; then
    cp "$ROOT/.env" "$PLUGINS/.env"
    echo "Copied repo .env → $PLUGINS/.env"
  else
    cp "$ROOT/.env.example" "$PLUGINS/.env"
    echo "No repo .env — created $PLUGINS/.env from .env.example (fill in secrets)."
  fi
else
  echo "Left existing $PLUGINS/.env unchanged. Use SYNC_ENV=1 to overwrite from repo .env."
fi

echo "Installed claude_usage.5m.py → $PLUGINS"
echo "If you still have claude_usage.py or claude_pro_dashboard.py there, delete them to avoid duplicate SwiftBar entries."
