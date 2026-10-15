#!/usr/bin/env python3
"""integrate_flagship.py — register a builder's finished app and verify it.

Runs, for each app:
  1. register_flagship.py App --json App/test/register.json  (shared registries)
  2. reinject_all_shims.py App      (family game shell only — byte-identical shims)
  3. the app's content gate, java_compile_check, runtime smoke / growth / IAP
     suites (growth only for apps carrying the game growth stack)
  4. pre_publish_check.py App  — prints the blocking lines only

and prints a compact summary. Nothing is committed.

Usage:
    python3 scripts/integrate_flagship.py App [App ...] [--no-register]
"""
import json
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
S = BASE / "scripts"


def run(cmd, timeout=1500):
    try:
        r = subprocess.run(cmd, cwd=BASE, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "timeout"


def tail(out: str, n: int = 4) -> str:
    lines = [l for l in out.strip().splitlines() if l.strip()]
    return " | ".join(lines[-n:])[:600]


def integrate(app: str, register: bool) -> dict:
    res = {}
    gh = BASE / app / "android/app/src/main/assets/game.html"
    html = gh.read_text(encoding="utf-8") if gh.exists() else ""
    game = 'data-growth-shim="CORE"' in html
    reg = BASE / app / "test/register.json"
    gate = None
    if reg.exists():
        h = json.loads(reg.read_text(encoding="utf-8"))
        gate = (h.get("gate") or [None])[0]
        if register:
            rc, out = run([sys.executable, str(S / "register_flagship.py"), app, "--json", str(reg)])
            res["register"] = "ok" if rc == 0 else tail(out)
    else:
        res["register"] = "no test/register.json"
    if game:
        rc, out = run([sys.executable, str(S / "reinject_all_shims.py"), app])
        res["reinject"] = "ok" if rc == 0 else tail(out)
    if gate:
        rc, out = run([sys.executable, str(BASE / gate), app])
        if rc != 0 and "usage" in out.lower():
            rc, out = run([sys.executable, str(BASE / gate)])
        res["gate"] = ("OK " if rc == 0 else "FAIL ") + tail(out, 2)
    rc, out = run([sys.executable, str(S / "java_compile_check.py"), app])
    res["java"] = ("OK " if rc == 0 else "FAIL ") + tail(out, 2)
    suites = ["smoke_all.js", "iap_grants.js"] + (["growth_behaviour.js"] if game else [])
    for js in suites:
        rc, out = run(["node", str(S / "runtime" / js), app])
        res[js] = ("OK" if rc == 0 else "FAIL ") + ("" if rc == 0 else tail(out, 6))
    for extra in ("runtime_check.js",):
        f = BASE / app / "test" / extra
        if f.exists():
            rc, out = run(["node", str(f)])
            res[extra] = ("OK" if rc == 0 else "FAIL ") + ("" if rc == 0 else tail(out, 6))
    rc, out = run([sys.executable, str(S / "pre_publish_check.py"), app])
    blockers = [re.sub(r"\x1b\[[0-9;]*m", "", l).strip() for l in out.splitlines()
                if "✗" in l or "BLOCK" in l.upper()]
    res["pre_publish"] = blockers[:60]
    return res


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    register = "--no-register" not in sys.argv
    if not args:
        print(__doc__)
        return 2
    for app in args:
        print(f"=== {app}")
        for k, v in integrate(app, register).items():
            if isinstance(v, list):
                print(f"  {k}: {len(v)} line(s)")
                for l in v:
                    print(f"     {l[:220]}")
            else:
                print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
