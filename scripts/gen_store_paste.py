#!/usr/bin/env python3
"""
gen_store_paste.py — generate <App>/STORE_PASTE.md from per-locale metadata.

Reads <App>/metadata/<locale>/{release_notes,short_description,full_description,
subtitle,keywords,promotional_text}.txt for each of the 13 supported locales
and emits a single STORE_PASTE.md with one <locale>…</locale> block per
field per locale, ready to copy-paste into Play Console / App Store Connect.

Locale tags follow Play Console reality (NOT BCP-47 in all cases):
  - Indonesian: `id` (not `id-ID`)
  - Ukrainian:  `uk` (not `uk-UA`)
The pre_publish_check.py `check_store_paste_locale_tags` guard enforces
this — STORE_PASTE.md MUST NOT contain `uk-UA` or `id-ID` tags.

Usage:
  python3 scripts/gen_store_paste.py <AppName>
  python3 scripts/gen_store_paste.py <AppName> --force      # overwrite existing
  python3 scripts/gen_store_paste.py --all                  # every app

Will refuse to overwrite an existing STORE_PASTE.md unless --force is given.
"""

import argparse
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Play Console locale tags. KEEP this list in sync with TRANSLATIONS.md
# §1 (which is the source of truth) and pre_publish_check.py
# REQUIRED_LOCALES.
LOCALES = ['en-US', 'ar', 'de-DE', 'es-419', 'fr-FR', 'hi-IN', 'id',
           'it-IT', 'ja-JP', 'pt-BR', 'tr-TR', 'uk', 'zh-CN']

# Per-section: (heading, source_filename, char_limit, console_path)
SECTIONS = [
    ('RELEASE NOTES',     'release_notes.txt',     500,
        'Test and release → Production → release details'),
    ('SHORT DESCRIPTION', 'short_description.txt',  80,
        'Grow → Store presence → Main store listing → Short description'),
    ('FULL DESCRIPTION',  'full_description.txt',  4000,
        'Grow → Store presence → Main store listing → Full description'),
    ('SUBTITLE',          'subtitle.txt',           30,
        'Apple App Store Connect → App Information → Subtitle'),
    ('KEYWORDS',          'keywords.txt',          100,
        'Apple App Store Connect → Version → Keywords'),
    ('PROMOTIONAL TEXT',  'promotional_text.txt',  170,
        'Apple App Store Connect → Version → Promotional Text'),
]

HEADER = """\
# {app} — store paste sheet

One file with every translated string for every locale, wrapped in
`<locale>…</locale>` blocks. Open in Play Console / App Store Connect,
find the right field, and paste the matching block for each language.

The 13 locales (Play Console tags): {locale_list}

**Notes:**
- Indonesian uses tag `<id>` (not `id-ID`) — Play Console quirk.
- Ukrainian uses tag `<uk>` (not `uk-UA`) — Play Console quirk.
- Chinese uses `<zh-CN>` (Simplified). Arabic uses `<ar>` (RTL — Play
  Console renders right-to-left automatically when this locale is
  enabled).
- Title is intentionally English globally (per TRANSLATIONS.md §3) —
  not included here. Leave the title field blank for non-English
  locales; Play falls back to the default.

---
"""


def read_meta(app, locale, fname):
    path = os.path.join(REPO, app, 'metadata', locale, fname)
    if not os.path.isfile(path):
        return None
    return open(path, encoding='utf-8').read().rstrip()


def render_section(app, heading, fname, char_limit, console_path):
    out = [f'## {heading} (≤{char_limit} chars per locale)', '']
    out.append(f'_{console_path}_')
    out.append('')
    for loc in LOCALES:
        text = read_meta(app, loc, fname)
        out.append(f'<{loc}>')
        if text is not None:
            out.append(text)
        out.append(f'</{loc}>')
        out.append('')
    return '\n'.join(out).rstrip() + '\n'


def generate(app, force=False):
    target = os.path.join(REPO, app, 'STORE_PASTE.md')
    if os.path.exists(target) and not force:
        print(f"  exists, refusing to overwrite (pass --force to replace): {target}")
        return False
    if not os.path.isdir(os.path.join(REPO, app, 'metadata')):
        print(f"  skip: no metadata/ folder in {app}")
        return False
    parts = [HEADER.format(app=app, locale_list=', '.join(LOCALES)), '']
    for heading, fname, char_limit, console_path in SECTIONS:
        parts.append(render_section(app, heading, fname, char_limit, console_path))
        parts.append('---')
        parts.append('')
    body = '\n'.join(parts).rstrip() + '\n'
    with open(target, 'w', encoding='utf-8') as f:
        f.write(body)
    print(f"  wrote {target}")
    return True


def list_apps():
    SKIP = {'_template', '_release', 'docs', 'scripts', 'release_aabs',
            'BLOCKED_APPS', '__pycache__', '.git', '.idea', 'node_modules'}
    out = []
    for name in sorted(os.listdir(REPO)):
        if name in SKIP or name.startswith('.'):
            continue
        d = os.path.join(REPO, name)
        if not os.path.isdir(d):
            continue
        if os.path.isdir(os.path.join(d, 'metadata')):
            out.append(name)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('apps', nargs='*')
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--force', action='store_true')
    args = ap.parse_args()
    if args.all:
        apps = list_apps()
    elif args.apps:
        apps = args.apps
    else:
        ap.print_help()
        sys.exit(2)
    for app in apps:
        print(f'== {app} ==')
        generate(app, force=args.force)


if __name__ == '__main__':
    main()
