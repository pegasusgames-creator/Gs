#!/usr/bin/env python3
"""check_dinosaurapp_facts.py - factual gate for the kids app DinosaurApp (Dinosaur World).

The app teaches children dinosaur facts (length, weight, diet, period, where the
fossils were found), a "How big?" size compare and games built from them, so a
wrong table row is a wrong fact taught to a child. This gate parses the app's
DINO_ROWS / PERIODS / SIZE_REF tables out of game.html and checks them against
REFERENCE below, written from standard palaeontology references (not derived
from the app).

BLOCKS on:
  * a creature in the app with no reference entry (or a reference creature missing),
    duplicate ids, fewer than 30 true dinosaurs
  * PERIODS out of order (Permian < Triassic < Jurassic < Cretaceous) or with
    boundaries off the real dates (Permian 299-252, Triassic 252-201,
    Jurassic 201-145, Cretaceous 145-66 million years ago; 4 Ma tolerance)
  * a period that differs from the reference, or an anachronism (a dinosaur in
    the Permian, a creature outside the periods it truly lived in, e.g. T. rex in
    the Jurassic)
  * diet / length / weight outside the reference range, a fossil continent (or
    "also found in" continent) the reference does not list
  * the size-compare ratios (bus|child|house per row) that do not equal
    length / SIZE_REF, SIZE_REF off the real objects (school bus 10-13 m, child
    1.0-1.4 m, house 8-12 m wide), or a sizeNote string (13 locales) naming other numbers
  * a non-dinosaur (Pteranodon, Quetzalcoatlus, Elasmosaurus, Mosasaurus,
    Dimetrodon) kind-labelled "dino", a kind label that does not say "not a
    dinosaur", or any app / store text calling one of them (or a pterosaur,
    plesiosaur, "sea/flying dinosaur") a dinosaur
  * a name list that is not 13 entries, an English name differing from the
    reference, or a name in the wrong script (ar / hi / ja / uk / zh)
  * a creature with no SVG art config, missing per_* / cont_* / diet_* / kind_*
    strings or key drift in any of the 13 locales
  * any claim of real roar recordings (the roars are made up and made by the app)

Standalone: python3 scripts/check_dinosaurapp_facts.py [App ...]
With no args, or with DinosaurApp among the args, checks the app; with other
apps only it prints a skip line and exits 0 (pre_publish_check passes every app).
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
APP = "DinosaurApp"
HTML = BASE / APP / "android/app/src/main/assets/game.html"
META = BASE / APP / "metadata"
LANGS = ["en", "ar", "de", "es", "fr", "hi", "id", "it", "ja", "pt", "tr", "uk", "zh"]
CONTS = {"north_america", "south_america", "europe", "africa", "asia", "australia", "antarctica"}
PERIOD_REF = {"per": (299, 252), "tri": (252, 201), "jur": (201, 145), "cre": (145, 66)}
PERIOD_SEQ = ["per", "tri", "jur", "cre"]
SIZE_REF_RANGE = {"bus": (10, 13), "child": (1.0, 1.4), "house": (8, 12)}
NA, SA, EU, AF, AS, AU, AN = ("north_america", "south_america", "europe", "africa", "asia", "australia", "antarctica")

# id: (English name, kind, {periods lived}, {acceptable diets}, (len/wingspan m min, max), (kg min, max), {continents with fossils})
REFERENCE = {
    "eoraptor": ("Eoraptor", "dino", {"tri"}, {"both"}, (0.8, 1.8), (5, 15), {SA}),
    "herrerasaurus": ("Herrerasaurus", "dino", {"tri"}, {"meat"}, (3, 6), (150, 400), {SA}),
    "coelophysis": ("Coelophysis", "dino", {"tri"}, {"meat"}, (2, 3.5), (10, 40), {NA}),
    "plateosaurus": ("Plateosaurus", "dino", {"tri"}, {"plants", "both"}, (5, 10), (600, 4000), {EU}),
    "dilophosaurus": ("Dilophosaurus", "dino", {"jur"}, {"meat"}, (5.5, 7.5), (300, 600), {NA}),
    "cryolophosaurus": ("Cryolophosaurus", "dino", {"jur"}, {"meat"}, (5.5, 7), (300, 600), {AN}),
    "compsognathus": ("Compsognathus", "dino", {"jur"}, {"meat"}, (0.7, 1.4), (2, 4), {EU}),
    "allosaurus": ("Allosaurus", "dino", {"jur"}, {"meat"}, (8, 12), (1500, 3500), {NA, EU}),
    "ceratosaurus": ("Ceratosaurus", "dino", {"jur"}, {"meat"}, (5, 7), (500, 1100), {NA, EU, AF}),
    "stegosaurus": ("Stegosaurus", "dino", {"jur"}, {"plants"}, (6.5, 9.5), (2500, 7000), {NA, EU}),
    "kentrosaurus": ("Kentrosaurus", "dino", {"jur"}, {"plants"}, (4, 5), (700, 1600), {AF}),
    "diplodocus": ("Diplodocus", "dino", {"jur"}, {"plants"}, (22, 27), (10000, 25000), {NA}),
    "apatosaurus": ("Apatosaurus", "dino", {"jur"}, {"plants"}, (20, 25), (16000, 25000), {NA}),
    "brachiosaurus": ("Brachiosaurus", "dino", {"jur"}, {"plants"}, (18, 26), (28000, 58000), {NA, AF}),
    "tyrannosaurus": ("Tyrannosaurus", "dino", {"cre"}, {"meat"}, (11, 13.5), (6000, 9500), {NA}),
    "triceratops": ("Triceratops", "dino", {"cre"}, {"plants"}, (7, 9.5), (5000, 12000), {NA}),
    "velociraptor": ("Velociraptor", "dino", {"cre"}, {"meat"}, (1.5, 2.2), (10, 25), {AS}),
    "spinosaurus": ("Spinosaurus", "dino", {"cre"}, {"meat"}, (12, 16), (4000, 10000), {AF}),
    "ankylosaurus": ("Ankylosaurus", "dino", {"cre"}, {"plants"}, (5, 8), (4500, 8500), {NA}),
    "parasaurolophus": ("Parasaurolophus", "dino", {"cre"}, {"plants"}, (8.5, 10.5), (2500, 5500), {NA}),
    "iguanodon": ("Iguanodon", "dino", {"cre"}, {"plants"}, (8, 11), (2500, 5000), {EU, AS, NA, AF}),
    "pachycephalosaurus": ("Pachycephalosaurus", "dino", {"cre"}, {"plants", "both"}, (4, 5), (300, 600), {NA}),
    "carnotaurus": ("Carnotaurus", "dino", {"cre"}, {"meat"}, (7, 8.5), (1200, 2200), {SA}),
    "giganotosaurus": ("Giganotosaurus", "dino", {"cre"}, {"meat"}, (11, 13.5), (4000, 14000), {SA}),
    "argentinosaurus": ("Argentinosaurus", "dino", {"cre"}, {"plants"}, (28, 40), (60000, 100000), {SA}),
    "therizinosaurus": ("Therizinosaurus", "dino", {"cre"}, {"plants", "both"}, (9, 11), (3000, 6000), {AS}),
    "protoceratops": ("Protoceratops", "dino", {"cre"}, {"plants"}, (1.7, 2.7), (120, 220), {AS}),
    "oviraptor": ("Oviraptor", "dino", {"cre"}, {"both"}, (1.5, 2.2), (20, 40), {AS}),
    "deinonychus": ("Deinonychus", "dino", {"cre"}, {"meat"}, (3, 3.6), (50, 100), {NA}),
    "edmontosaurus": ("Edmontosaurus", "dino", {"cre"}, {"plants"}, (9, 13), (3000, 4500), {NA}),
    "styracosaurus": ("Styracosaurus", "dino", {"cre"}, {"plants"}, (5, 6), (1800, 3000), {NA}),
    "microraptor": ("Microraptor", "dino", {"cre"}, {"meat"}, (0.6, 1.0), (0.5, 1.5), {AS}),
    "muttaburrasaurus": ("Muttaburrasaurus", "dino", {"cre"}, {"plants"}, (7, 8.5), (2500, 3500), {AU}),
    "baryonyx": ("Baryonyx", "dino", {"cre"}, {"meat"}, (7.5, 10), (1000, 2000), {EU}),
    # NOT dinosaurs (wingspan for the pterosaurs)
    "pteranodon": ("Pteranodon", "flying", {"cre"}, {"meat"}, (5, 7), (15, 50), {NA}),
    "quetzalcoatlus": ("Quetzalcoatlus", "flying", {"cre"}, {"meat"}, (9, 11), (150, 250), {NA}),
    "elasmosaurus": ("Elasmosaurus", "sea", {"cre"}, {"meat"}, (9, 11), (1500, 3000), {NA}),
    "mosasaurus": ("Mosasaurus", "sea", {"cre"}, {"meat"}, (10, 17), (5000, 20000), {EU, NA}),
    "dimetrodon": ("Dimetrodon", "syn", {"per"}, {"meat"}, (2, 4), (150, 300), {NA}),
}
NOT_DINOS = [k for k, v in REFERENCE.items() if v[1] != "dino"]
NOT_DINO_WORDS = [REFERENCE[k][0] for k in NOT_DINOS] + ["pterosaur", "pterodactyl", "plesiosaur", "mosasaur"]
SCRIPTS = {"ar": r"[؀-ۿ]", "hi": r"[ऀ-ॿ]", "ja": r"[぀-ヿ一-鿿]", "uk": r"[Ѐ-ӿ]", "zh": r"[一-鿿]"}
ROW = re.compile(r"^\s*\['(\w+)','(\w+)','(\w+)','(\w+)',([\d.]+),(\d+),'(\w+)','([\w,]*)','([01])','([\d.|]+)','([^']*)'\],?\s*$", re.M)
REAL_CLAIM = re.compile(r"(?<!not )(?<!no )(?<!nicht )\breal[- ](?:dinosaur[- ])?(?:roars?|sounds?|recordings?)\b|\brecorded (?:dinosaur )?(?:roars?|sounds?)\b|\bauthentic roars?\b", re.I)


def sentences(text):
    return re.split(r"(?<=[.!?])\s+|\n+", text)


def dino_claim(sentence):
    """True if the sentence calls a non-dinosaur a dinosaur (negations are fine)."""
    s = sentence.lower()
    if not any(w.lower() in s for w in NOT_DINO_WORDS) and not re.search(r"\b(flying|sea|swimming|marine) dinosaurs?\b", s):
        return False
    if not re.search(r"dinosaur", s):
        return False
    return not re.search(r"\b(not|no|isn't|wasn't|aren't|weren't|never|before)\b", s)


def check() -> list:
    bad = []
    if not HTML.exists():
        return [f"{APP}: game.html missing"]
    s = HTML.read_text(encoding="utf-8")

    # periods
    m = re.search(r"const PERIOD_ORDER = \[([^\]]*)\]", s)
    order = re.findall(r"'(\w+)'", m.group(1)) if m else []
    if order != PERIOD_SEQ:
        bad.append(f"PERIOD_ORDER {order} must be {PERIOD_SEQ} (oldest first)")
    pm = re.search(r"const PERIODS = \{([^}]*)\}", s)
    periods = {k: (int(a), int(b)) for k, a, b in re.findall(r"(\w+): \[(\d+), (\d+)\]", pm.group(1))} if pm else {}
    for k, (ra, rb) in PERIOD_REF.items():
        a, b = periods.get(k, (None, None))
        if a is None or abs(a - ra) > 4 or abs(b - rb) > 4:
            bad.append(f"period {k}: app has {periods.get(k)}, reference is {ra}-{rb} million years ago")

    # size references
    sm = re.search(r"const SIZE_REF = \{([^}]*)\}", s)
    size = {k: float(v) for k, v in re.findall(r"(\w+): ([\d.]+)", sm.group(1))} if sm else {}
    for k, (lo, hi) in SIZE_REF_RANGE.items():
        if not (lo <= size.get(k, -1) <= hi):
            bad.append(f"SIZE_REF {k} = {size.get(k)} m is outside the real range {lo}-{hi} m")

    rows = ROW.findall(s)
    ids = [r[0] for r in rows]
    for i in sorted({i for i in ids if ids.count(i) > 1}):
        bad.append(f"duplicate id {i}")
    for i in REFERENCE:
        if i not in ids:
            bad.append(f"reference creature {i} missing from the app")
    if sum(1 for r in rows if r[1] == "dino") < 30:
        bad.append(f"only {sum(1 for r in rows if r[1] == 'dino')} dinosaurs parsed (need 30+)")
    cfg = set(re.findall(r"^ (\w+):\['(?:thero|sauro|ornith|quad|flyer|plesio|mosa|dime)'", s, re.M))

    for aid, kind, per, diet, mm, kg, cont, alt, free, ratios, names in rows:
        ref = REFERENCE.get(aid)
        if not ref:
            bad.append(f"{aid}: no reference entry (add it to scripts/check_dinosaurapp_facts.py with a trusted source)")
            continue
        ename, rkind, rper, rdiet, (lmin, lmax), (wmin, wmax), rconts = ref
        mm, kg = float(mm), int(kg)
        if kind != rkind:
            bad.append(f"{aid}: kind '{kind}' but the reference says '{rkind}'" + (" - a non-dinosaur must not be kind 'dino'" if kind == "dino" else ""))
        if per not in PERIOD_REF:
            bad.append(f"{aid}: unknown period {per!r}")
        elif per not in rper:
            bad.append(f"{aid}: anachronism - listed in the {per} period but it lived in {sorted(rper)}")
        if kind == "dino" and per == "per":
            bad.append(f"{aid}: a dinosaur cannot be in the Permian (dinosaurs appear in the Triassic)")
        if diet not in rdiet:
            bad.append(f"{aid}: diet '{diet}' but the reference says {sorted(rdiet)}")
        if not (lmin <= mm <= lmax):
            bad.append(f"{aid}: length {mm} m outside the reference range {lmin}-{lmax} m")
        if not (wmin <= kg <= wmax):
            bad.append(f"{aid}: weight {kg} kg outside the reference range {wmin}-{wmax} kg")
        for c in [cont] + [x for x in alt.split(",") if x]:
            if c not in CONTS:
                bad.append(f"{aid}: unknown continent {c!r}")
            elif c not in rconts:
                bad.append(f"{aid}: fossils are not known from {c} (reference: {sorted(rconts)})")
        # size-compare ratios
        try:
            rb, rc, rh = [float(x) for x in ratios.split("|")]
            for label, got, ref_m in (("bus", rb, size.get("bus", 12)), ("child", rc, size.get("child", 1.2)), ("house", rh, size.get("house", 10))):
                want = mm / ref_m
                if abs(got - want) > max(0.06, 0.03 * want):
                    bad.append(f"{aid}: size slider shows x{got} {label}s but {mm} m / {ref_m} m = x{want:.2f}")
        except ValueError:
            bad.append(f"{aid}: malformed ratios {ratios!r}")
        # names
        nl = names.split("|")
        if len(nl) != 13 or any(not n.strip() for n in nl):
            bad.append(f"{aid}: needs 13 non-empty names")
        else:
            if nl[0] != ename:
                bad.append(f"{aid}: English name {nl[0]!r} != reference {ename!r}")
            for lang, rx in SCRIPTS.items():
                if not re.search(rx, nl[LANGS.index(lang)]):
                    bad.append(f"{aid}: {lang} name {nl[LANGS.index(lang)]!r} is not in the {lang} script")
        if aid not in cfg:
            bad.append(f"{aid}: no SVG art config in CFG")

    # strings
    mm_ = re.search(r"const CONTENT_I18N = \{\n(.*?)\n\};", s, re.S)
    i18n = {}
    if mm_:
        for line in mm_.group(1).splitlines():
            lm = re.match(r"^\s*(\w+): (\{.*\}),?$", line)
            if lm:
                try:
                    i18n[lm.group(1)] = json.loads(lm.group(2))
                except ValueError:
                    bad.append(f"CONTENT_I18N {lm.group(1)} is not valid JSON")
    if sorted(i18n) != sorted(LANGS):
        bad.append(f"CONTENT_I18N locales {sorted(i18n)} != the 13 portfolio locales")
    en = i18n.get("en", {})
    need = [f"per_{p}" for p in PERIOD_SEQ] + [f"cont_{c}" for c in CONTS] + ["diet_plants", "diet_meat", "diet_both", "kind_dino", "kind_flying", "kind_sea", "kind_syn", "ks_flying", "ks_sea", "ks_syn", "sizeNote"]
    for k in need:
        if k not in en:
            bad.append(f"en string {k} missing")
    for l in LANGS:
        if l in i18n and set(i18n[l]) != set(en):
            bad.append(f"{l}: string keys differ from en ({sorted(set(i18n[l]) ^ set(en))[:4]})")
    for k in ("kind_flying", "kind_sea", "kind_syn"):
        if k in en and not re.search(r"not a dinosaur", en[k], re.I):
            bad.append(f"en {k} must say 'not a dinosaur': {en[k]!r}")
    for k in ("ks_flying", "ks_sea", "ks_syn"):
        if k in en and not re.search(r"not a dinosaur", en[k], re.I):
            bad.append(f"en {k} must say 'not a dinosaur': {en[k]!r}")
    if en.get("kind_dino", "").lower() != "dinosaur":
        bad.append("en kind_dino must be 'Dinosaur'")
    if "flying" in en.get("kind_flying", "").lower() and "reptile" not in en.get("kind_flying", "").lower():
        bad.append("kind_flying must call pterosaurs 'flying reptile'")
    # the sizeNote must quote the real reference sizes in every locale
    for l, d in i18n.items():
        nums = [float(x.replace(",", ".")) for x in re.findall(r"\d+(?:[.,]\d+)?", d.get("sizeNote", ""))]
        for k in ("bus", "child", "house"):
            want = size.get(k)
            if want is not None and not any(abs(n - want) < 0.01 for n in nums):
                bad.append(f"{l}: sizeNote does not state the {k} size {want} m (has {nums})")

    # honesty: roars + not-a-dinosaur wording across the app and store text
    corpus = [("game.html strings", " ".join(v for d in i18n.values() for v in d.values() if isinstance(v, str)))]
    en_text = [v for v in en.values() if isinstance(v, str)]
    if META.exists():
        for f in sorted(META.rglob("*.txt")) + sorted(META.glob("*.md")) + sorted(META.glob("*.json")):
            try:
                corpus.append((str(f.relative_to(BASE)), f.read_text(encoding="utf-8")))
            except OSError:
                pass
    for name, text in corpus:
        if REAL_CLAIM.search(text):
            bad.append(f"{name}: claims real roar recordings - the roars are made up and made by the app")
    for name, text in [("en strings", "\n".join(en_text))] + [(n, t) for n, t in corpus if "en-US" in n or n.endswith(".md")]:
        for sent in sentences(text):
            if dino_claim(sent):
                bad.append(f"{name}: calls a non-dinosaur a dinosaur: {sent.strip()[:90]!r}")
    if not re.search(r"made[- ]up|made by the app", en.get("roarNote", "") + en.get("ageNote", ""), re.I):
        bad.append("the roars must be labelled as made up / made by the app (roarNote / ageNote)")
    return bad


def main() -> int:
    apps = [a for a in sys.argv[1:] if not a.startswith("-")]
    if apps and APP not in apps:
        print(f"check_dinosaurapp_facts: skip ({APP} not in run)")
        return 0
    bad = check()
    for b in bad:
        print(f"  BLOCK {APP}: {b}")
    print(f"check_dinosaurapp_facts: {'FAIL' if bad else 'OK'} ({len(bad)} blocker(s))")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
