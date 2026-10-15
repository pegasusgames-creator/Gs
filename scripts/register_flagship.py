#!/usr/bin/env python3
"""register_flagship.py — record a newly finished app in the shared registries.

A rebuilt app only touches its own folder; the shared registries are updated
here, in one place, so parallel builders never race on them:

  * scripts/wire_growth_core.py  CFG[App]  <- the app's own GROWTH_CFG
    (only for apps that carry the game growth stack)
  * scripts/reinject_all_shims.py DEFAULT_APPS  += App   (game track)
  * scripts/pre_publish_check.py gate list += its content gate (--gate)
  * scripts/pre_publish_check.py BLOCKED_APPS -= App   (placeholder rewritten)
  * scripts/app_themes.py         THEMES[App] <- --archetype (a dict literal)
  * scripts/check_growth_features.py PRE_RELEASE += package (no app may
    cross-promote an unreleased app; remove it the day it goes live)

Usage:
  python3 scripts/register_flagship.py App [--gate scripts/check_x.py "label"]
      [--archetype-file entry.txt] [--dry-run]
  python3 scripts/register_flagship.py App --json App/test/register.json
      (builder hand-off: {"gate": [script, label], "app_theme": {...}};
       RGB lists become tuples)
"""
import argparse
import ast
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
S = BASE / "scripts"


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def pkg_of(app: str) -> str:
    m = re.search(r'applicationId\s+"([^"]+)"', read(BASE / app / "android/app/build.gradle"))
    return m.group(1)


def growth_cfg(app: str):
    m = re.search(r"<script data-growth-config>window\.GROWTH_CFG=(\{.*?\});</script>",
                  read(BASE / app / "android/app/src/main/assets/game.html"))
    return json.loads(m.group(1)) if m else None


def py_literal(v) -> str:
    if isinstance(v, dict):
        return "dict(" + ", ".join(f"{k}={py_literal(x)}" for k, x in v.items()) + ")"
    if isinstance(v, bool):
        return "True" if v else "False"
    return json.dumps(v, ensure_ascii=False)


def upd_wire(app: str, cfg: dict, s: str) -> str:
    c = {k: v for k, v in cfg.items() if k != "app"}
    entry = f'    "{app}":'.ljust(22) + " " + py_literal(c) + ",\n"
    pat = re.compile(r'^    "%s":.*?(?=^    "[A-Za-z]|^\}$)' % re.escape(app), re.M | re.S)
    if pat.search(s):
        return pat.sub(lambda _: entry, s, count=1)
    i = s.index("\n}\n\nCFG_RE")
    return s[:i] + "\n" + entry.rstrip("\n") + s[i:]


def upd_reinject(app: str, s: str) -> str:
    m = re.search(r"DEFAULT_APPS = \[(.*?)\]", s, re.S)
    if f'"{app}"' in m.group(1):
        return s
    return s[:m.end(1)] + f', "{app}"' + s[m.end(1):]


def upd_gate(gate: str, label: str, s: str) -> str:
    name = Path(gate).name
    if f"'{name}'" in s:
        return s
    anchor = "        ('check_trademarks.py', 'no third-party game/franchise trademarks in listing text'),\n"
    if anchor not in s:
        raise SystemExit("pre_publish_check.py gate-list anchor not found")
    return s.replace(anchor, anchor + f"        ('{name}', {label!r}),\n", 1)


def upd_blocked(app: str, s: str) -> str:
    m = re.search(r"BLOCKED_APPS = \{(.*?)\n\}", s, re.S)
    body = m.group(1)
    nb = re.sub(r'\s*"%s",' % re.escape(app), "", body)
    return s if nb == body else s[:m.start(1)] + nb + s[m.end(1):]


def upd_themes(app: str, literal: str, s: str) -> str:
    d = ast.literal_eval(literal.strip().rstrip(","))
    if not isinstance(d, dict):
        raise SystemExit("--archetype-file must hold a dict literal")
    if "layout_archetype" not in d and isinstance(next(iter(d.values()), None), dict):
        d = d.get(app) or next(iter(d.values()))
    body = "    " + json.dumps(app) + ": {\n" + "".join(
        f"        {json.dumps(k)}: {v!r},\n" for k, v in d.items()) + "    },\n"
    pat = re.compile(r'^    "%s": \{.*?^    \},\n' % re.escape(app), re.M | re.S)
    if pat.search(s):
        return pat.sub(lambda _: body, s, count=1)
    i = s.index("\n}\n", s.index("THEMES"))
    return s[:i + 1] + body + s[i + 1:]


def upd_prerelease(pkg: str, s: str) -> str:
    m = re.search(r"PRE_RELEASE = \{(.*?)\n\}", s, re.S)
    if f'"{pkg}"' in m.group(1):
        return s
    return s[:m.end(1)] + f'\n    "{pkg}",' + s[m.end(1):]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("app")
    ap.add_argument("--gate", nargs=2, metavar=("SCRIPT", "LABEL"))
    ap.add_argument("--archetype-file")
    ap.add_argument("--json", help="builder hand-off file with gate + app_theme")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    theme_literal = None
    if a.json:
        h = json.loads(Path(a.json).read_text(encoding="utf-8"))
        if h.get("gate") and not a.gate:
            a.gate = list(h["gate"])
        if h.get("app_theme"):
            t = {k: tuple(v) if isinstance(v, list) else v for k, v in h["app_theme"].items()}
            theme_literal = repr(t)
    app = a.app
    if not (BASE / app / "android").is_dir():
        raise SystemExit(f"{app}: not an app folder")
    edits = {}
    cfg = growth_cfg(app)
    if cfg:
        p = S / "wire_growth_core.py"
        edits[p] = upd_wire(app, cfg, edits.get(p, read(p)))
        p = S / "reinject_all_shims.py"
        edits[p] = upd_reinject(app, read(p))
    p = S / "pre_publish_check.py"
    s = upd_blocked(app, read(p))
    if a.gate:
        if not (BASE / a.gate[0]).exists():
            raise SystemExit(f"{a.gate[0]} does not exist")
        s = upd_gate(a.gate[0], a.gate[1], s)
    edits[p] = s
    if a.archetype_file:
        theme_literal = Path(a.archetype_file).read_text(encoding="utf-8")
    if theme_literal:
        p = S / "app_themes.py"
        edits[p] = upd_themes(app, theme_literal, read(p))
    p = S / "check_growth_features.py"
    edits[p] = upd_prerelease(pkg_of(app), read(p))
    for p, s in edits.items():
        if s != read(p):
            print(f"  {'would update' if a.dry_run else 'update'} {p.relative_to(BASE)}")
            if not a.dry_run:
                p.write_text(s, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
