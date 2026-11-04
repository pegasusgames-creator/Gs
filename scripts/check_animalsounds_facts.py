#!/usr/bin/env python3
"""check_animalsounds_facts.py - factual gate for the kids app AnimalSounds.

Animal Sounds shows facts to children (where each animal lives, what it eats)
and plays a "Where does it live?" quiz built from them, so a wrong table row is
a wrong answer taught to a child. This gate parses the app's ANIMAL_ROWS table
out of game.html and checks it against REFERENCE below, a table written from
standard zoology references (not derived from the app).

BLOCKS on:
  * an animal in the app with no reference entry (or a reference animal missing
    from the app), duplicate ids, fewer than 40 animals
  * diet != reference (plants / meat / both, where "meat" = eats other animals
    incl. insects and fish)
  * primary habitat not in the reference set of habitats where the animal truly
    lives, or an "also lives in" habitat outside that set, or an unknown habitat id
  * a name list that is not exactly 13 entries, an empty name, an English name
    differing from the reference, or a name in the wrong script (ar / hi / ja /
    uk / zh)
  * an animal with no SVG art entry or no synthesized-sound recipe
  * missing hab_* / live_* / diet_* strings (or key drift) in any of the 13 locales
  * any claim of "real recordings" of animal sounds in the app or its store
    metadata (the sounds are synthesized; only a negated mention is allowed)

Standalone: python3 scripts/check_animalsounds_facts.py [App ...]
With no args, or with AnimalSounds among the args, checks the app; with other
apps only it prints a skip line and exits 0 (pre_publish_check passes every app).
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
APP = "AnimalSounds"
HTML = BASE / APP / "android/app/src/main/assets/game.html"
LANGS = ["en", "ar", "de", "es", "fr", "hi", "id", "it", "ja", "pt", "tr", "uk", "zh"]
HABS = ["farm", "home", "meadow", "forest", "jungle", "savanna", "ocean", "polar", "desert", "wetland"]
DIETS = ["plants", "meat", "both"]

# id: (English name, habitats where it genuinely lives, diet)
REFERENCE = {
    "cow": ("cow", {"farm"}, "plants"),
    "pig": ("pig", {"farm"}, "both"),
    "sheep": ("sheep", {"farm", "meadow"}, "plants"),
    "horse": ("horse", {"farm", "meadow"}, "plants"),
    "hen": ("hen", {"farm"}, "both"),
    "rooster": ("rooster", {"farm"}, "both"),
    "duck": ("duck", {"farm", "wetland"}, "both"),
    "goat": ("goat", {"farm", "forest"}, "plants"),
    "donkey": ("donkey", {"farm", "desert"}, "plants"),
    "turkey": ("turkey", {"farm", "forest"}, "both"),
    "dog": ("dog", {"home", "farm"}, "both"),
    "cat": ("cat", {"home", "farm"}, "meat"),
    "bee": ("bee", {"meadow", "forest", "farm"}, "plants"),
    "cricket": ("cricket", {"meadow", "forest", "farm"}, "both"),
    "mouse": ("mouse", {"meadow", "home", "farm", "forest"}, "both"),
    "bird": ("bird", {"meadow", "forest"}, "both"),
    "crow": ("crow", {"forest", "meadow", "farm"}, "both"),
    "wolf": ("wolf", {"forest", "polar"}, "meat"),
    "fox": ("fox", {"forest", "meadow", "desert", "polar"}, "both"),
    "bear": ("bear", {"forest", "polar"}, "both"),
    "deer": ("deer", {"forest", "meadow"}, "plants"),
    "owl": ("owl", {"forest", "meadow"}, "meat"),
    "monkey": ("monkey", {"jungle", "forest", "savanna"}, "both"),
    "gorilla": ("gorilla", {"jungle", "forest"}, "plants"),
    "tiger": ("tiger", {"jungle", "forest"}, "meat"),
    "parrot": ("parrot", {"jungle", "forest"}, "plants"),
    "snake": ("snake", {"jungle", "desert", "forest", "meadow", "wetland", "savanna"}, "meat"),
    "lion": ("lion", {"savanna"}, "meat"),
    "elephant": ("elephant", {"savanna", "jungle", "forest"}, "plants"),
    "zebra": ("zebra", {"savanna", "meadow"}, "plants"),
    "hyena": ("hyena", {"savanna", "desert"}, "meat"),
    "whale": ("whale", {"ocean", "polar"}, "meat"),
    "dolphin": ("dolphin", {"ocean"}, "meat"),
    "seal": ("seal", {"ocean", "polar"}, "meat"),
    "seagull": ("seagull", {"ocean", "wetland"}, "both"),
    "penguin": ("penguin", {"polar", "ocean"}, "meat"),
    "polarbear": ("polar bear", {"polar"}, "meat"),
    "walrus": ("walrus", {"polar", "ocean"}, "meat"),
    "camel": ("camel", {"desert"}, "plants"),
    "coyote": ("coyote", {"desert", "meadow", "forest"}, "both"),
    "frog": ("frog", {"wetland", "meadow", "forest", "jungle"}, "meat"),
    "crocodile": ("crocodile", {"wetland", "jungle", "savanna"}, "meat"),
    "hippo": ("hippo", {"wetland", "savanna"}, "plants"),
    "goose": ("goose", {"wetland", "farm", "meadow"}, "plants"),
}

SCRIPTS = {  # language -> regex every name must match at least one char of
    "ar": r"[؀-ۿ]", "hi": r"[ऀ-ॿ]", "ja": r"[぀-ヿ一-鿿]",
    "uk": r"[Ѐ-ӿ]", "zh": r"[一-鿿]",
}
ROW = re.compile(r"^\s*\['(\w+)','(\w+)','([\w,]*)','(\w+)','([^']*)','([^']*)'\],?\s*$", re.M)
REAL_CLAIM = re.compile(r"(?<!not )(?<!no )(?<!nicht )\breal[- ](?:animal[- ])?(?:sounds?|recordings?)\b|\brecorded (?:animal )?sounds\b", re.I)


def check() -> list:
    bad = []
    if not HTML.exists():
        return [f"{APP}: game.html missing"]
    s = HTML.read_text(encoding="utf-8")
    rows = ROW.findall(s)
    ids = [r[0] for r in rows]
    if len(rows) < 40:
        bad.append(f"only {len(rows)} animals parsed from ANIMAL_ROWS (need 40+)")
    for i in sorted({i for i in ids if ids.count(i) > 1}):
        bad.append(f"duplicate animal id {i}")
    for i in REFERENCE:
        if i not in ids:
            bad.append(f"reference animal {i} missing from the app")
    art = set(re.findall(r"^  (\w+): `", s, re.M))
    rec = set(re.findall(r"^  (\w+): ", s.split("const RECIPES = {")[1].split("\n};")[0], re.M)) if "const RECIPES = {" in s else set()
    for aid, hab, alt, diet, word, names in rows:
        ref = REFERENCE.get(aid)
        if not ref:
            bad.append(f"{aid}: no reference entry (add it to scripts/check_animalsounds_facts.py with a trusted source)")
            continue
        ename, rhabs, rdiet = ref
        if diet not in DIETS:
            bad.append(f"{aid}: unknown diet {diet!r}")
        elif diet != rdiet:
            bad.append(f"{aid}: diet {diet!r} but reference says {rdiet!r}")
        for h in [hab] + [x for x in alt.split(",") if x]:
            if h not in HABS:
                bad.append(f"{aid}: unknown habitat {h!r}")
            elif h not in rhabs:
                bad.append(f"{aid}: habitat {h!r} is not where it lives (reference: {sorted(rhabs)})")
        nl = names.split("|")
        if len(nl) != 13 or not all(x.strip() for x in nl):
            bad.append(f"{aid}: needs 13 non-empty names, got {len(nl)}")
            continue
        if nl[0] != ename:
            bad.append(f"{aid}: English name {nl[0]!r} != reference {ename!r}")
        for lg, rx in SCRIPTS.items():
            if not re.search(rx, nl[LANGS.index(lg)]):
                bad.append(f"{aid}: {lg} name {nl[LANGS.index(lg)]!r} is not in the {lg} script")
        if aid not in art:
            bad.append(f"{aid}: no SVG art entry")
        if aid not in rec:
            bad.append(f"{aid}: no synthesized-sound recipe")
    # strings: hab_* / live_* / diet_* present in every locale, key parity with en
    m = re.search(r"const CONTENT_I18N = \{(.*?)\n\};", s, re.S)
    if not m:
        bad.append("CONTENT_I18N not found")
    else:
        blocks = {lg: set(re.findall(r'(?:^|, )(\w+):"', body)) for lg, body in re.findall(r"^  (\w+): \{ (.*?) \},?$", m.group(1), re.M)}
        need = {f"hab_{h}" for h in HABS} | {f"live_{h}" for h in HABS} | {f"diet_{d}" for d in DIETS}
        for lg in LANGS:
            if lg not in blocks:
                bad.append(f"locale {lg} missing from CONTENT_I18N")
                continue
            for k in sorted(need - blocks[lg]):
                bad.append(f"locale {lg}: missing string {k}")
            if lg != "en" and "en" in blocks and blocks[lg] != blocks["en"]:
                bad.append(f"locale {lg}: key drift vs en ({sorted(blocks[lg] ^ blocks['en'])[:4]})")
    # honesty: sounds are synthesized, never "real recordings"
    texts = [s] + [p.read_text(encoding="utf-8") for p in (BASE / APP / "metadata").rglob("*.txt")]
    for t in texts:
        mm = REAL_CLAIM.search(t)
        if mm:
            bad.append(f"claims real recordings: ...{t[max(0, mm.start() - 30):mm.end() + 20]!r}")
            break
    return bad


def main() -> int:
    apps = [a for a in sys.argv[1:] if not a.startswith("--")]
    if apps and APP not in apps:
        print(f"animalsounds facts: skipped (not checking {APP})")
        return 0
    bad = check()
    for b in bad:
        print("  ✗", b)
    if bad:
        print(f"animalsounds facts: {len(bad)} blocker(s)")
        return 1
    print(f"animalsounds facts: OK ({len(REFERENCE)} animals verified against the reference table)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
