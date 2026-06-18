#!/usr/bin/env python3
"""Scan every app's game.html for onclick= bare-function calls whose target
function is not defined in the file (dead handlers). Also flags duplicate
element ids (a duplicate-id can make the first handler unreachable)."""
import re, glob, os
from collections import Counter

BASE = "/home/user/Documents/Gs"
SKIP = ("_", ".")
# JS keywords / globals that may appear as bare-call-looking tokens
KEYWORDS = {"if", "for", "while", "return", "function", "switch", "catch",
            "typeof", "new", "void", "delete", "in", "of", "do", "else",
            "var", "let", "const", "true", "false", "null", "undefined",
            "this", "window", "document", "Math", "JSON", "Date", "Array",
            "Object", "String", "Number", "Boolean", "parseInt", "parseFloat",
            "setTimeout", "setInterval", "alert", "confirm", "console",
            "Android", "localStorage", "event"}

CALL = re.compile(r'(?<![.\w])([A-Za-z_$][\w$]*)\s*\(')
ONCLICK = re.compile(r'onclick\s*=\s*"([^"]*)"|onclick\s*=\s*\'([^\']*)\'')
DEFS = [
    lambda n: re.compile(r'function\s+' + re.escape(n) + r'\s*\('),
    lambda n: re.compile(r'window\.' + re.escape(n) + r'\s*='),
    lambda n: re.compile(r'(?:var|let|const)\s+' + re.escape(n) + r'\s*='),
    lambda n: re.compile(r'\b' + re.escape(n) + r'\s*[:=]\s*function'),
    lambda n: re.compile(r'\b' + re.escape(n) + r'\s*=\s*\([^)]*\)\s*=>'),
    lambda n: re.compile(r'\b' + re.escape(n) + r'\s*=>'),
]


def defined(name, html):
    return any(p(name).search(html) for p in DEFS)


def scan(html):
    called = set()
    for m in ONCLICK.finditer(html):
        expr = m.group(1) if m.group(1) is not None else m.group(2)
        for cm in CALL.finditer(expr):
            fn = cm.group(1)
            if fn not in KEYWORDS:
                called.add(fn)
    orphans = sorted(c for c in called if not defined(c, html))
    # duplicate ids
    ids = re.findall(r'\bid\s*=\s*"([^"]+)"', html)
    dup = sorted(k for k, v in Counter(ids).items() if v > 1)
    return orphans, dup

import sys as _sys

_IF_FUNC = re.compile(r"if\s*\([A-Za-z_$][\w$]*\)\s+function\s")

def syntax_botch(html):
    """Detect `if (x) function f(){}` — a function decl as an if-body, which
    is a SyntaxError in strict mode (aborts the whole script). Root cause of
    the 2026-06-18 Nonogram dead-menu (botched migrateSave injection)."""
    return [m.group(0)[:40] for m in _IF_FUNC.finditer(html)]


def gate_main():
    base = "/home/user/Documents/Gs"
    apps = _sys.argv[1:]
    if not apps or apps == ["--all"]:
        apps = sorted(d for d in os.listdir(base)
                      if os.path.isfile(os.path.join(base, d,
                         "android/app/src/main/assets/game.html"))
                      and not d.startswith(("_", ".")))
    fail = 0
    for app in apps:
        html = open(os.path.join(base, app,
                    "android/app/src/main/assets/game.html"),
                    encoding="utf-8").read()
        orphans, _dup = scan(html)
        botch = syntax_botch(html)
        for o in orphans:
            print(f"\u2717 {app}: onclick calls undefined fn '{o}()'"); fail = 1
        for b in botch:
            print(f"\u2717 {app}: JS syntax botch `{b}...` (if-body function "
                  f"decl) aborts the script"); fail = 1
    if not fail:
        print(f"[dead handlers] {len(apps)} app(s) clean")
    return fail


if __name__ == "__main__":
    _sys.exit(gate_main())
