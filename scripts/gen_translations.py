#!/usr/bin/env python3
"""
gen_translations.py — generate Play Store listing translations for all 11 locales.

Reads <AppName>/metadata/en-US/ as source of truth, produces matching
folders for the other 10 locales using LLM translation.

Usage:
    python3 gen_translations.py <AppName>            # generate all missing locales
    python3 gen_translations.py <AppName> --update   # regenerate locales whose English source is newer
    python3 gen_translations.py <AppName> --kids     # Kids mode: only 4 minimum locales, headers added
    python3 gen_translations.py <AppName> --dry-run  # show what would be generated, don't write

Requires: ANTHROPIC_API_KEY environment variable, or substitute openai
client by editing the LLM_CALL function below.

This script does NOT translate the title — title.txt is copied verbatim
from en-US to each locale (per TRANSLATIONS.md §3).
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Lazy import — only needed if actually calling the API
try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

REPO_ROOT = Path(__file__).resolve().parent.parent if (Path(__file__).resolve().parent.name == "scripts") else Path(__file__).resolve().parent

# The 11 supported locales. Order is alphabetical by code (matches how
# Play Console sorts in the listing UI).
LOCALES = [
    ("en-US", "English",       "United States",      None),  # baseline
    ("ar",    "Arabic",        "MENA region",        "ar"),
    ("de-DE", "German",        "Germany",            "de"),
    ("es-419", "Spanish",      "Latin America",      "es"),
    ("fr-FR", "French",        "France",             "fr"),
    ("hi-IN", "Hindi",         "India",              "hi"),
    ("id",    "Indonesian",    "Indonesia",          "id"),  # Play Console: id, not id-ID
    ("it-IT", "Italian",       "Italy",              "it"),
    ("ja-JP", "Japanese",      "Japan",              "ja"),
    ("pt-BR", "Portuguese",    "Brazil",             "pt"),
    ("tr-TR", "Turkish",       "Turkey",             "tr"),
    ("uk",    "Ukrainian",     "Ukraine",            "uk"),  # Play Console: uk, not uk-UA
    ("zh-CN", "Chinese",       "Mainland China",     "zh"),
]

# Subset for Kids program apps (TRANSLATIONS.md §5)
KIDS_LOCALES = ["en-US", "es-419", "pt-BR", "fr-FR"]

# Per-Play-Store field character limits. These apply in the TARGET
# language, not English. Some translations grow 30-50% so the script
# must validate and refuse to write overflowing files.
FIELD_LIMITS = {
    "title.txt":             30,
    "subtitle.txt":          30,
    "short_description.txt": 80,
    "full_description.txt":  4000,
    "keywords.txt":          100,
    "release_notes.txt":     500,
    "promotional_text.txt":  170,  # iOS only but generated for parity
}

# Fields to translate. Order matters (subtitle before description for
# context). Title is NOT in this list — it stays English.
FIELDS = [
    "subtitle.txt",
    "short_description.txt",
    "full_description.txt",
    "keywords.txt",
    "release_notes.txt",
    "promotional_text.txt",
]

# Banned phrases (per QUALITY_PLAYBOOK.md §7.2). Enforced post-translation.
# Translations must not introduce these even if the LLM thinks they're
# more idiomatic.
BANNED_PHRASES_BY_LANG = {
    "en": ["#1", "best", "top rated", "download now", "install now", "% off"],
    "de": ["nr. 1", "beste", "jetzt herunterladen", "jetzt installieren"],
    "es": ["#1", "el mejor", "descarga ahora", "instala ahora"],
    "fr": ["n°1", "le meilleur", "télécharge maintenant"],
    "pt": ["nº 1", "o melhor", "baixe agora", "instale agora"],
    "uk": ["№1", "найкращий", "завантажуйте зараз"],
    "ar": ["#1", "الأفضل", "حمّل الآن", "ثبّت الآن"],
    "zh": ["#1", "最佳", "立即下载", "立即安装"],
    # ... extend as needed
}


# ---------- LLM call --------------------------------------------------------

def llm_translate(english_text, target_locale, target_lang_name, field_name,
                  char_limit, app_voice="V1 (neutral functional)",
                  is_kids=False):
    """Translate one field via the Claude API (preferred) or, if
    ANTHROPIC_API_KEY is absent, the OpenAI API. Returns the translated
    string, or None if no provider is available / the call fails."""
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    provider = None
    if HAS_ANTHROPIC and anthropic_key:
        provider = "anthropic"
    elif HAS_OPENAI and openai_key:
        provider = "openai"
    if provider is None:
        print(f"  WARNING: no LLM provider available (need ANTHROPIC_API_KEY "
              f"or OPENAI_API_KEY + the matching SDK). Skipping {target_locale}.")
        return None

    kids_constraint = ""
    if is_kids:
        kids_constraint = (
            "\nThis is a Kids program app. Translation MUST be appropriate "
            "for ages under 13. No emoji. No slang that adults use casually "
            "but is inappropriate for children in the target language. "
            "Use warm, encouraging, educational voice consistently."
        )

    prompt = f"""Translate this Google Play Store listing field from English to {target_lang_name} ({target_locale}).

Field: {field_name}
Character limit: {char_limit} (HARD LIMIT — exceeding will fail validation)
App voice / tone: {app_voice}
{kids_constraint}

Rules:
- Do NOT add Play Store banned phrases: "#1", "best", "top rated", "download now", "install now", "% off" (and equivalents in target language)
- Preserve newlines and bullet structure if present
- For keywords.txt: produce target-language search terms, NOT a translation of the English keywords. Comma-separated.
- For full_description.txt: keep paragraph and bullet structure exact
- The translation must fit in {char_limit} characters in {target_lang_name}. If a literal translation overflows, paraphrase to fit.

ONLY OUTPUT THE TRANSLATED TEXT. No explanation, no quote marks, no preamble.

ENGLISH TEXT:
{english_text}"""

    try:
        if provider == "anthropic":
            client = Anthropic(api_key=anthropic_key)
            response = client.messages.create(
                model="claude-sonnet-4-5",  # fast and good enough for short marketing copy
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            translated = response.content[0].text.strip()
        else:  # openai
            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # fast + cheap; fine for short marketing copy
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            translated = (response.choices[0].message.content or "").strip()
        # Strip surrounding quotes / code fences if the LLM added them
        if translated.startswith("```"):
            translated = translated.strip("`")
            if "\n" in translated:
                translated = translated.split("\n", 1)[1]
        if len(translated) >= 2 and translated[0] == '"' and translated[-1] == '"':
            translated = translated[1:-1]
        return translated.strip()
    except Exception as e:
        print(f"  WARNING: API call failed for {target_locale}/{field_name}: {e}")
        return None


# ---------- validation ------------------------------------------------------

def validate_translation(text, field_name, target_lang_short):
    """Returns (ok, message). If not ok, message describes the problem."""
    limit = FIELD_LIMITS.get(field_name)
    if limit and len(text) > limit:
        return False, f"exceeds {limit} chars (got {len(text)})"

    banned = BANNED_PHRASES_BY_LANG.get(target_lang_short, [])
    text_lower = text.lower()
    for phrase in banned:
        if phrase.lower() in text_lower:
            return False, f"contains banned phrase: {phrase!r}"

    return True, "ok"


# ---------- main ------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("app_name")
    ap.add_argument("--update", action="store_true",
                    help="regenerate locales whose English source is newer")
    ap.add_argument("--kids", action="store_true",
                    help="Kids mode: only 4 minimum locales, headers added")
    ap.add_argument("--dry-run", action="store_true",
                    help="show what would be generated, don't write")
    args = ap.parse_args()

    app_dir = REPO_ROOT / args.app_name
    if not app_dir.is_dir():
        print(f"ERROR: app directory not found: {app_dir}")
        sys.exit(1)

    en_dir = app_dir / "metadata" / "en-US"
    if not en_dir.is_dir():
        print(f"ERROR: source locale en-US not found at {en_dir}")
        sys.exit(1)

    # Determine if Kids app — read from app_info.json
    is_kids = args.kids
    app_info_path = app_dir / "metadata" / "app_info.json"
    if app_info_path.exists():
        try:
            info = json.loads(app_info_path.read_text())
            if info.get("kids_program") is True:
                is_kids = True
                print(f"Detected Kids app from app_info.json — using Kids mode")
        except json.JSONDecodeError:
            pass

    # Determine voice from app_themes.py if available
    app_voice = "V1 (neutral functional)"
    try:
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        sys.path.insert(0, str(REPO_ROOT))
        from app_themes import THEMES
        if args.app_name in THEMES:
            v = THEMES[args.app_name].get("voice", "V1")
            voice_descriptions = {
                "V1": "V1 (neutral functional)",
                "V2": "V2 (encouraging coach — supportive, warm)",
                "V3": "V3 (playful narrator — gentle theatrical humor)",
                "V4": "V4 (snarky / dry — minor sarcasm, hardcore audience)",
                "V5": "V5 (calm / zen — quiet, meditative)",
                "V6": "V6 (enthusiastic arcade — all caps celebrations)",
                "V7": "V7 (educational warm — kids appropriate)",
                "V8": "V8 (direct minimal — no fluff)",
            }
            app_voice = voice_descriptions.get(v, app_voice)
    except ImportError:
        pass

    if is_kids:
        # Kids voice override per TRANSLATIONS.md §5
        app_voice = "V7 (educational warm — kids appropriate, no slang)"

    target_locales = KIDS_LOCALES if is_kids else [code for code, _, _, _ in LOCALES]
    target_locales = [c for c in target_locales if c != "en-US"]

    print(f"Generating translations for {args.app_name}")
    print(f"  Source: {en_dir}")
    print(f"  Locales: {len(target_locales)}")
    print(f"  Voice: {app_voice}")
    print(f"  Kids mode: {is_kids}")
    print()

    # Read English source for each field
    english = {}
    for field in FIELDS:
        path = en_dir / field
        if path.exists():
            english[field] = path.read_text().strip()

    if not english:
        print(f"ERROR: no source files found in {en_dir}")
        sys.exit(1)

    print(f"  Source fields: {', '.join(english.keys())}")
    print()

    # Find locale info
    locales_lookup = {code: (name, region, short)
                      for code, name, region, short in LOCALES}

    total_written = 0
    total_skipped = 0
    total_failed = 0

    for locale in target_locales:
        name, region, short = locales_lookup[locale]
        print(f"[{locale}] {name}")
        locale_dir = app_dir / "metadata" / locale

        if args.dry_run:
            print(f"  would write to: {locale_dir}")
            continue

        locale_dir.mkdir(parents=True, exist_ok=True)

        # title.txt: copy English verbatim per TRANSLATIONS.md §3
        en_title = (en_dir / "title.txt")
        if en_title.exists():
            (locale_dir / "title.txt").write_text(en_title.read_text())

        for field in FIELDS:
            if field not in english:
                continue
            out_path = locale_dir / field

            # Skip if exists and not --update
            if out_path.exists() and not args.update:
                # Check freshness if --update would be relevant
                en_path = en_dir / field
                if out_path.stat().st_mtime >= en_path.stat().st_mtime:
                    print(f"  {field:30s} skip (exists, up to date)")
                    total_skipped += 1
                    continue

            char_limit = FIELD_LIMITS.get(field, 4000)
            translated = llm_translate(
                english[field], locale, name, field, char_limit,
                app_voice=app_voice, is_kids=is_kids,
            )

            if translated is None:
                print(f"  {field:30s} FAIL (LLM call failed)")
                total_failed += 1
                continue

            # Validate
            ok, msg = validate_translation(translated, field, short)
            if not ok:
                print(f"  {field:30s} FAIL ({msg})")
                # Write the bad translation to a .rejected file so the user
                # can edit it down rather than starting from scratch
                rejected_path = out_path.with_suffix(out_path.suffix + ".rejected")
                rejected_path.write_text(translated)
                print(f"    saved as {rejected_path.name} for manual editing")
                total_failed += 1
                continue

            # Add Kids header if Kids mode
            content = translated
            if is_kids and field in ("full_description.txt", "short_description.txt"):
                content = (
                    "# KIDS APP — REVIEW BY NATIVE SPEAKER BEFORE SHIPPING\n"
                    "# Remove this header line after review\n\n"
                    + content
                )

            out_path.write_text(content)
            print(f"  {field:30s} ok ({len(translated)} chars)")
            total_written += 1

    print()
    print(f"Done. Written: {total_written}, Skipped: {total_skipped}, Failed: {total_failed}")
    if total_failed > 0:
        print()
        print(f"Some fields failed validation. Look for .rejected files in")
        print(f"each locale folder; edit them down to character limit and")
        print(f"rename to remove the .rejected suffix.")
        sys.exit(1)


if __name__ == "__main__":
    main()
