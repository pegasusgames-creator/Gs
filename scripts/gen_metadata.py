#!/usr/bin/env python3
"""
gen_metadata.py
Converts store/store-listing.txt → metadata/en-US/ text files.
Also updates metadata/app_info.json category fields.
Overwrites init_app_metadata.py TODO placeholders with real content.

Usage:
  python3 gen_metadata.py           # process all apps
  python3 gen_metadata.py App1 App2 # process specific apps
"""
import json, os, re, sys, textwrap

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {"_template", "_release", "__pycache__", ".git", ".idea", "node_modules"}


# ---------- category detection -----------------------------------------------

def detect_category(app):
    n = app.lower()
    if any(x in n for x in ['word', 'spell', 'anagram', 'boggle', 'hangman',
                              'cryptogram', 'ghost', 'phrase', 'wordle', 'phrasebook',
                              'wordconnect', 'wordladder', 'wordscramble', 'wordsearch']):
        return ('GAME_WORD', 'GAMES', 'WORD')
    if any(x in n for x in ['quiz', 'trivia', 'flag', 'capital', 'geography',
                              'history', 'foodquiz', 'animal', 'bible', 'harry',
                              'general', 'football', 'science', 'sports', 'logo',
                              'movie', 'emoji', 'dinosaur']):
        return ('GAME_TRIVIA', 'GAMES', 'TRIVIA')
    if any(x in n for x in ['puzzle', 'sort', 'merge', 'nonogram', 'pipe',
                              'minesweeper', 'sudoku', 'unblock', 'lights', 'knot',
                              'mahjong', 'jigsaw', 'sliding', 'pinpull', 'screw',
                              'binairo', 'connection', 'mastermind', 'numberlink',
                              'triple', 'sumplete', 'colorblock', 'colorfill',
                              'watersort', '2048', 'dotart', 'balloonpop',
                              'blockpuzzle', 'fruitmerge', 'fruitsort', 'numbermerge',
                              'yarnsort', 'zengarden']):
        return ('GAME_PUZZLE', 'GAMES', 'PUZZLE')
    if any(x in n for x in ['flappy', 'brickbreaker', 'bubblewrap', 'bubbleshooter',
                              'jumper', 'donttap', 'firework', 'kaleidoscope']):
        return ('GAME_ARCADE', 'GAMES', 'ARCADE')
    if any(x in n for x in ['piano', 'guitar', 'drum', 'metronome', 'bpm',
                              'music', 'ukulele', 'chord', 'musictheory']):
        return ('MUSIC_AND_AUDIO', 'MUSIC', '')
    if any(x in n for x in ['blood', 'bmi', 'breathing', 'fasting', 'period',
                              'sobriety', 'quit', 'eyerest', 'medication', 'mood',
                              'moodtracker', 'bloodpressure', 'bloodsugar']):
        return ('HEALTH_AND_FITNESS', 'HEALTH_FITNESS', '')
    if any(x in n for x in ['calculator', 'converter', 'timer', 'clock',
                              'budget', 'expense', 'loan', 'compound', 'percentage',
                              'gpa', 'tip', 'bill', 'currency', 'countdown',
                              'meeting', 'packing', 'grocery', 'chore', 'habit',
                              'checklist', 'password', 'qrcode', 'random', 'morse',
                              'numberbase', 'flashlight', 'aspect']):
        return ('TOOLS', 'UTILITIES', '')
    if any(x in n for x in ['abc', 'learn', 'kids', 'basicmath', 'multiplication',
                              'counting', 'phonetic', 'abclearn', 'kidspiano',
                              'kidsdrum', 'kidscolor']):
        return ('EDUCATION', 'EDUCATION', '')
    if any(x in n for x in ['cocktail', 'coffee', 'cooking', 'recipe', 'food',
                              'fishing', 'golf', 'darts', 'sport', 'scorecard']):
        return ('LIFESTYLE', 'LIFESTYLE', '')
    if any(x in n for x in ['decision', 'icebreaker', 'neverha', 'headsup',
                              'charadeapp', 'twotruths', 'bingo']):
        return ('ENTERTAINMENT', 'ENTERTAINMENT', '')
    if any(x in n for x in ['flashcard', 'flash', 'phrasebook']):
        return ('EDUCATION', 'EDUCATION', '')
    # generic games
    if any(x in n for x in ['game', 'quiz', 'card', 'memory', 'dice', 'coin',
                              'ball', 'number', 'tap', 'sort', 'match']):
        return ('GAME_CASUAL', 'GAMES', 'PUZZLE')
    return ('LIFESTYLE', 'LIFESTYLE', '')


# ---------- parse store-listing.txt ------------------------------------------

def parse_store_listing(path):
    with open(path, encoding='utf-8') as f:
        text = f.read()

    # Format 1 (most apps): ===...\nSECTION NAME\n===...\ncontent
    # Format 2 (WaterSort, Puzzle2048): SECTION NAME\ncontent\n\nNEXT SECTION
    # Format 3 (PipeConnect): SECTION NAME: content or SECTION NAME:\ncontent

    has_separators = bool(re.search(r'={10,}', text))

    def extract_sep(section_name):
        pattern = re.escape(section_name) + r'[^\n]*\n={10,}\n(.*?)(?=\n={10,}|\Z)'
        m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return m.group(1).strip() if m else ''

    # Build section dict for plain-format files using line-by-line parsing
    HEADER_RE = re.compile(
        r'^(APP NAME|SHORT DESC(?:RIPTION)?|FULL DESC(?:RIPTION)?|'
        r'FEATURES?|HOW TO PLAY|KEYWORDS?|TAGS?|'
        r"CATEGORY|CONTENT RATING|WHAT'S NEW|RELEASE NOTES?)"
        r'[^\n:]*:?\s*(.*)',
        re.IGNORECASE
    )
    _plain_sections = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = HEADER_RE.match(lines[i])
        if m:
            key = re.sub(r'[^a-z]', '_', m.group(1).strip().lower()).strip('_')
            inline = m.group(2).strip()
            # Collect lines until next header or double blank
            body_lines = [inline] if inline else []
            i += 1
            blank_count = 0
            while i < len(lines):
                if HEADER_RE.match(lines[i]):
                    break
                if lines[i].strip() == '':
                    blank_count += 1
                    if blank_count >= 2 and body_lines:
                        # peek: if next non-blank is a header, stop
                        j = i + 1
                        while j < len(lines) and lines[j].strip() == '':
                            j += 1
                        if j < len(lines) and HEADER_RE.match(lines[j]):
                            break
                    body_lines.append('')
                else:
                    blank_count = 0
                    body_lines.append(lines[i])
                i += 1
            _plain_sections[key] = '\n'.join(body_lines).strip()
        else:
            i += 1

    def extract_plain(section_name):
        key = re.sub(r'[^a-z]', '_', section_name.strip().lower()).strip('_')
        if key in _plain_sections:
            return _plain_sections[key]
        for k, v in _plain_sections.items():
            if key in k or k in key:
                return v
        return ''

    extract = extract_sep if has_separators else extract_plain

    app_name    = extract('APP NAME')
    short_desc  = extract('SHORT DESCRIPTION') or extract('SHORT DESC')
    full_desc   = extract('FULL DESCRIPTION') or extract('FULL DESC')
    release_notes = extract("WHAT'S NEW") or extract('RELEASE NOTES') or extract("WHAT’S NEW")
    tags        = extract('TAGS') or extract('KEYWORDS') or extract('TAGS / KEYWORDS')

    return {
        'app_name':      app_name,
        'short_desc':    short_desc,
        'full_desc':     full_desc,
        'release_notes': release_notes,
        'tags':          tags,
    }


# ---------- derive subtitle + promotional text + keywords --------------------

def make_subtitle(app_human, short_desc):
    """≤30 chars subtitle for Apple."""
    candidates = []
    # Try first clause of short_desc
    first_clause = re.split(r'[.!?|–—]', short_desc)[0].strip()
    if first_clause and len(first_clause) <= 30:
        candidates.append(first_clause)
    # Try truncated to last word boundary
    if short_desc:
        trunc = short_desc[:30].rsplit(' ', 1)[0].rstrip(',;:')
        if len(trunc) >= 10:
            candidates.append(trunc)
    # Fallback: "Fun [app] game for everyone"
    generic = f"Fun {app_human} for everyone"
    if len(generic) <= 30:
        candidates.append(generic)
    candidates.append(app_human[:30])
    return candidates[0]


def make_promo_text(full_desc):
    """≤170 chars promotional text for Apple."""
    # First sentence of full description
    first = re.split(r'(?<=[.!?])\s', full_desc.strip())[0]
    # Strip emoji and bullets for clean copy
    first = re.sub(r'[^\x00-\x7F]', '', first).strip()
    first = re.sub(r'\s+', ' ', first)
    if len(first) > 170:
        first = first[:167].rsplit(' ', 1)[0] + '...'
    return first or full_desc[:170]


def make_keywords(tags_str):
    """≤100 chars comma-sep keywords for Apple (no spaces between entries)."""
    raw = re.split(r'[,\n]', tags_str)
    words = [w.strip().lower() for w in raw if w.strip()]
    # Build string staying under 100 chars
    result = []
    total = 0
    for w in words:
        addition = len(w) + (1 if result else 0)
        if total + addition <= 100:
            result.append(w)
            total += addition
        else:
            break
    return ','.join(result)


def enforce_title_length(title):
    if len(title) <= 30:
        return title
    # Try removing subtitle parts after dash/colon
    t = re.split(r'\s*[–—:]\s*', title)[0].strip()
    if len(t) <= 30:
        return t
    return title[:30].rsplit(' ', 1)[0]


def clean_full_desc(desc):
    """Remove lines with prohibited marketing language."""
    PROHIBITED = [
        r'\bdownload\s+now\b', r'\binstall\s+now\b', r'\bplay\s+now\b',
        r'\btry\s+now\b', r'\bclick\s+here\b', r'\bdownload\s+free\b',
        r'\bget\s+it\s+free\b', r'\bdownload\s+today\b',
    ]
    pattern = re.compile('|'.join(PROHIBITED), re.IGNORECASE)
    lines = desc.split('\n')
    clean = [l for l in lines if not pattern.search(l)]
    return '\n'.join(clean).strip()


# ---------- write helpers ----------------------------------------------------

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    content = content.rstrip('\n') + '\n'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def update_app_info_json(path, app):
    if not os.path.exists(path):
        return
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    google_cat, apple_primary, apple_sub = detect_category(app)
    data['category_google'] = google_cat
    data['category_apple_primary'] = apple_primary
    if apple_sub:
        data['category_apple_subcategory'] = apple_sub
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')


# ---------- process one app --------------------------------------------------

def process_app(app):
    app_root  = os.path.join(BASE, app)
    listing   = os.path.join(app_root, 'store', 'store-listing.txt')
    meta_dir  = os.path.join(app_root, 'metadata', 'en-US')

    if not os.path.exists(listing):
        return f'{app}: no store-listing.txt'

    parsed = parse_store_listing(listing)
    app_name  = parsed['app_name'] or app
    short_desc = parsed['short_desc']
    full_desc  = clean_full_desc(parsed['full_desc'])
    release_notes = parsed['release_notes'] or 'Initial release.'
    tags      = parsed['tags']

    # Humanize app name for subtitle generation
    app_human = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', app)

    title = enforce_title_length(app_name)
    subtitle = make_subtitle(app_human, short_desc)
    short_desc_clean = short_desc[:80] if short_desc else f'Play {title} now!'
    promo_text = make_promo_text(full_desc)
    keywords = make_keywords(tags) if tags else app.lower()[:100]
    notes = release_notes[:500]
    full_desc_clean = full_desc[:4000]

    os.makedirs(meta_dir, exist_ok=True)
    write_file(os.path.join(meta_dir, 'title.txt'),             title)
    write_file(os.path.join(meta_dir, 'short_description.txt'), short_desc_clean)
    write_file(os.path.join(meta_dir, 'subtitle.txt'),          subtitle)
    write_file(os.path.join(meta_dir, 'full_description.txt'),  full_desc_clean)
    write_file(os.path.join(meta_dir, 'keywords.txt'),          keywords)
    write_file(os.path.join(meta_dir, 'promotional_text.txt'),  promo_text)
    write_file(os.path.join(meta_dir, 'release_notes.txt'),     notes)

    # Update category in app_info.json
    update_app_info_json(os.path.join(app_root, 'metadata', 'app_info.json'), app)

    return f'{app}: ok (title={title!r}, {len(full_desc_clean)}c desc)'


# ---------- main -------------------------------------------------------------

def list_apps():
    apps = []
    for name in sorted(os.listdir(BASE)):
        if name in SKIP_DIRS or name.startswith('.'):
            continue
        if not os.path.isdir(os.path.join(BASE, name)):
            continue
        if not os.path.exists(os.path.join(BASE, name, 'android')):
            continue
        apps.append(name)
    return apps


if __name__ == '__main__':
    target = sys.argv[1:] if len(sys.argv) > 1 else list_apps()
    for app in target:
        print(process_app(app))
    print('Done')
