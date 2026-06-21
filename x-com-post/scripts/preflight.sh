#!/usr/bin/env bash
# Preflight checks before x.com automation.
# Usage: preflight.sh [Chrome profile] [read|post]
#   read — allow Chrome running if auto-connect works
#   post — require Chrome fully quit (default)

set -euo pipefail

PROFILE="${1:-Profile 1}"
MODE="${2:-post}"
CHROME_DIR="${HOME}/Library/Application Support/Google/Chrome"
COOKIES="${CHROME_DIR}/${PROFILE}/Cookies"

echo "== X.com preflight =="
echo "Profile: ${PROFILE}"
echo "Mode: ${MODE}"

if pgrep -x "Google Chrome" >/dev/null 2>&1; then
  if [[ "${MODE}" == "read" ]]; then
    if command -v agent-browser >/dev/null 2>&1 && agent-browser --auto-connect get url >/dev/null 2>&1; then
      echo "STATUS: OK — Chrome running, auto-connect available."
    else
      echo "STATUS: WARN — Chrome running but auto-connect failed. Try --profile or quit Chrome."
    fi
  else
    echo "STATUS: BLOCKED — Chrome is running. User must Cmd+Q before posting."
  fi
else
  echo "STATUS: OK — Chrome is not running."
fi

if [[ ! -f "${COOKIES}" ]]; then
  echo "COOKIES: MISSING — ${COOKIES} not found."
  exit 1
fi

python3 - <<PY
import sqlite3, shutil, tempfile, os, sys
src = os.path.expanduser("${COOKIES}")
tmp = tempfile.mktemp(suffix=".db")
shutil.copy2(src, tmp)
con = sqlite3.connect(tmp)
rows = con.execute(
    "SELECT host_key FROM cookies WHERE host_key LIKE '%x.com%' OR host_key LIKE '%twitter%' GROUP BY host_key"
).fetchall()
con.close()
os.remove(tmp)
hosts = [r[0] for r in rows]
if hosts:
    print("COOKIES: OK —", ", ".join(hosts))
else:
    print("COOKIES: NONE — user must log into X in this Chrome profile first.")
    sys.exit(2)
PY

if command -v agent-browser >/dev/null 2>&1; then
  echo ""
  echo "Available Chrome profiles:"
  agent-browser profiles 2>/dev/null || true
fi