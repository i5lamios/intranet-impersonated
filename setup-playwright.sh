#!/usr/bin/env bash
# Install Playwright (Python) from PyPI wheels into ./pwlib on hosts WITHOUT pip. Uses the system Chromium.
# Afterwards run:  PYTHONPATH=./pwlib python3 asme.py ...
# If pip exists, simply:  pip install playwright   (and use the system chromium via CHROMIUM=...)
set -euo pipefail
cd "$(dirname "$0")"
PYTAG="cp$(python3 -c 'import sys;print(f"{sys.version_info[0]}{sys.version_info[1]}")')"
mkdir -p pwlib .wheels
for pkg in playwright greenlet pyee typing_extensions; do
  python3 - "$pkg" "$PYTAG" <<'PY'
import json, sys, urllib.request, platform
pkg, tag = sys.argv[1:]
d = json.load(urllib.request.urlopen(f"https://pypi.org/pypi/{pkg}/json"))
arch = platform.machine()
def ok(f):
    n = f["filename"]
    if not n.endswith(".whl"): return False
    if pkg == "playwright": return "manylinux" in n and arch in n          # py3-none-manylinux...
    if pkg == "greenlet":   return tag in n and "manylinux" in n and arch in n
    return "none-any" in n
f = next(f for f in reversed(d["urls"]) if ok(f))
urllib.request.urlretrieve(f["url"], f".wheels/{f['filename']}")
print("fetched", f["filename"])
PY
done
for w in .wheels/*.whl; do unzip -qo "$w" -d pwlib; done
echo "done. Browser: use system chromium (apt install chromium) - do NOT run 'playwright install'."
