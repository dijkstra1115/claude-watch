#!/usr/bin/env bash
# Print a one-line claude-watch status only when remediation is needed.
# Silent on `ready`.
set -e

RAW=$(python3 "${CLAUDE_PLUGIN_DIR:-$(dirname "$0")/../..}/scripts/setup.py" --check --json 2>/dev/null || true)
[ -z "$RAW" ] && exit 0

STATUS=$(printf '%s' "$RAW" | python3 -c 'import json,sys; print(json.load(sys.stdin)["status"])' 2>/dev/null || echo "")
case "$STATUS" in
  ready|"") exit 0 ;;
  needs_install) echo "[claude-watch] Run /claude-watch setup to install ffmpeg/yt-dlp." ;;
esac
