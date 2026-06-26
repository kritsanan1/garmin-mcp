#!/usr/bin/env bash
# run.sh — Start the Garmin MCP Server
# Usage: ./run.sh [--port 8422]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f .env ]; then
  set -a
  source .env
  set +a
else
  echo "⚠️  No .env file found. Copy .env.example → .env and fill in your credentials."
  exit 1
fi

if [ -z "${GARMIN_EMAIL:-}" ] || [ -z "${GARMIN_PASSWORD:-}" ]; then
  echo "❌  GARMIN_EMAIL and GARMIN_PASSWORD must be set in .env"
  exit 1
fi

if ! command -v python3 &>/dev/null; then
  echo "❌  python3 not found. Install Python 3.10+ and try again."
  exit 1
fi

if ! python3 -c "import garminconnect, mcp" 2>/dev/null; then
  echo "📦  Installing dependencies…"
  if command -v uv &>/dev/null; then
    uv pip install -r requirements.txt
  else
    pip3 install -r requirements.txt --quiet
  fi
fi

PORT="${GARMIN_MCP_PORT:-8422}"
export GARMIN_MCP_PORT="$PORT"

echo ""
echo "🏃 Garmin MCP Server"
echo "   Port    : $PORT"
echo "   Email   : $GARMIN_EMAIL"
echo ""

exec python3 server.py
