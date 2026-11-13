#!/usr/bin/env python3
"""Post-deploy smoke test, no login: load a URL headless and fail on any JS pageerror / failed script.
usage: smoke.py <url> [<url> ...]     (exit 1 on any error)
Why: one bad JS module can blank an entire intranet; screenshots of only the changed pages miss it."""
import os, shutil, sys
from playwright.sync_api import sync_playwright

browser = os.environ.get("CHROMIUM") or next((shutil.which(b) for b in ("chromium", "chromium-browser", "google-chrome") if shutil.which(b)), None)
bad = 0
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=browser, args=["--no-sandbox"])
    for url in sys.argv[1:]:
        pg = b.new_page(ignore_https_errors=True)
        errs = []
        pg.on("pageerror", lambda e: errs.append(f"pageerror: {e}"))
        pg.on("requestfailed", lambda r: r.resource_type == "script" and errs.append(f"script failed: {r.url}"))
        pg.goto(url, wait_until="networkidle", timeout=60000)
        print(("FAIL " if errs else "ok   ") + url)
        for e in errs:
            print("   ", e)
        bad += bool(errs)
    b.close()
sys.exit(1 if bad else 0)
