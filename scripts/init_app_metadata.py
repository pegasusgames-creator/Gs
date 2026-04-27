#!/usr/bin/env python3
"""
init_app_metadata.py
Scaffolds the metadata/ and store/ folder structure for one or more apps.

Creates empty placeholder files so the author (or Claude) knows exactly
what to fill in. Will NOT overwrite existing files — safe to re-run.

Usage:
  python3 init_app_metadata.py BallSortPuzzle              # scaffold one app
  python3 init_app_metadata.py BallSort WaterSort          # scaffold several
  python3 init_app_metadata.py --all                       # scaffold all apps
  python3 init_app_metadata.py --all --dry-run             # preview what would be created

What gets created per app (only files that don't already exist):

  <app>/store/
      icon_512_playstore.png.TODO          (placeholder sentinel — replace with real 512x512 PNG)
      feature_graphic_1024x500.png.TODO    (placeholder sentinel — replace with real 1024x500 PNG)
      icon_1024_appstore.png.TODO          (placeholder sentinel — replace with real 1024x1024 PNG)
      screenshots/phone/.gitkeep
      screenshots/iphone_6_9/.gitkeep

  <app>/metadata/en-US/
      title.txt                  (template, <=30 chars)
      short_description.txt      (template, <=80 chars — Google)
      subtitle.txt               (template, <=30 chars — Apple)
      full_description.txt       (template, <=4000 chars)
      keywords.txt               (template, <=100 chars — Apple)
      promotional_text.txt       (template, <=170 chars — Apple)
      release_notes.txt          (template, <=500 chars)

  <app>/metadata/
      app_info.json              (required keys, values marked TODO)
      privacy.json
      content_rating.json
      iaps.json
      review_notes.json

After scaffolding, run `pre_publish_check.py <app>` — it will report every
file that still has TODO placeholders.
"""

import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {"_template", "_release", "__pycache__", ".git", ".idea", "node_modules"}


# ---------- per-app content templates ---------------------------------------

def humanize(app):
    """Turn 'BallSortPuzzle' -> 'Ball Sort Puzzle'."""
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", app)
    s = re.sub(r"(?<=[A-Za-z])(?=[0-9])|(?<=[0-9])(?=[A-Za-z])", " ", s)
    return s

def pkg_name(app):
    return "com.pegasusgames." + re.sub(r"[^a-z0-9]", "", app.lower())

TEXT_TEMPLATES = {
    "title.txt": "{app_human}\n",

    "short_description.txt":
        "TODO hook for {app_human}\n",

    "subtitle.txt":
        "TODO subtitle\n",

    "full_description.txt":
        "TODO: Write a unique full description for {app_human}.\n"
        "\n"
        "Do NOT copy another app's description and rename it.\n"
        "\n"
        "Suggested structure:\n"
        "  - 2-3 sentence hook describing what the player does\n"
        "  - 5-8 bullet points of features\n"
        "  - Closing line inviting the player to try it\n"
        "\n"
        "Avoid prohibited language — see CLAUDE.md for the full list.\n",

    "keywords.txt":
        "TODO,apple,keywords,comma,separated,no,spaces\n",

    "promotional_text.txt":
        "TODO Apple promotional text. Editable without new version.\n",

    "release_notes.txt":
        "Initial release.\n",
}

def app_info_template(app):
    return {
        "category_google":         "TODO_SET_GOOGLE_CATEGORY",
        "category_apple_primary":  "TODO_SET_APPLE_CATEGORY",
        "category_apple_subcategory": "",
        "contains_ads":            True,
        "contains_iap":            True,
        "target_audience_min_age": 13,
        "support_url":             "https://pegasusgames-creator.github.io/",
        "marketing_url":           "https://pegasusgames-creator.github.io/",
        "copyright":               "© 2026 Pegasus Games",
    }

def privacy_template(app):
    return {
        "privacy_policy_url": "https://pegasusgames-creator.github.io/privacy.html",
        "google_data_safety": {
            "data_collected": ["device_ids", "app_interactions", "crash_logs"],
            "data_shared":    ["advertising_id"],
            "encrypted_in_transit":      True,
            "user_can_request_deletion": True,
        },
        "apple_privacy_labels": {
            "data_used_to_track_you":  ["device_id", "advertising_data"],
            "data_linked_to_you":      [],
            "data_not_linked_to_you":  ["crash_data", "performance_data", "product_interaction"],
        },
    }

def content_rating_template(app):
    return {
        "iarc_answers": {
            "violence":               "none",
            "sexual_content":         "none",
            "profanity":              "none",
            "drugs_alcohol":          "none",
            "gambling_mechanics":     "none",
            "user_generated_content": False,
            "shares_user_location":   False,
            "allows_user_interaction": False,
            "digital_purchases":      True,
        },
        "expected_google_rating": "Everyone",
        "apple_age_rating":       "4+",
    }

def iaps_template(app):
    return {
        "one_time_products": [
            {"id": "remove_ads",         "title": "Remove Ads",   "price_usd": 2.99},
            {"id": "coins_small",        "title": "100 Coins",    "price_usd": 0.99},
            {"id": "coins_large",        "title": "500 Coins",    "price_usd": 2.99},
            {"id": "five_lives",         "title": "5 Lives",      "price_usd": 0.99},
            {"id": "unlimited_lives_1h",      "title": "1hr Unlimited",      "price_usd": 0.99},
            {"id": "unlimited_lives_forever", "title": "Unlimited Lives",    "price_usd": 4.99},
            {"id": "hint_pack",          "title": "Hint Pack",    "price_usd": 1.99},
            {"id": "starter_pack",       "title": "Starter Pack", "price_usd": 0.99},
        ],
        "subscriptions": [
            {"id": "season_pass_monthly", "title": "Season Pass",
             "price_usd": 1.99, "billing_period": "P1M", "grace_period_days": 3},
        ],
    }

def review_notes_template(app):
    human = humanize(app)
    return {
        "google_review_notes": f"No login required. All features of {human} accessible from the main menu.",
        "apple_review_notes":  f"No login required. To test IAPs, use the shop button in {human}.",
        "demo_account_required": False,
        "demo_username": "",
        "demo_password": "",
        "uses_third_party_content": False,
    }


# ---------- scaffold logic ---------------------------------------------------

def list_apps():
    apps = []
    for name in sorted(os.listdir(BASE)):
        if name in SKIP_DIRS or name.startswith("."):
            continue
        path = os.path.join(BASE, name)
        if not os.path.isdir(path):
            continue
        if not os.path.exists(os.path.join(path, "android")):
            continue
        apps.append(name)
    return apps

def write_if_missing(path, content, dry_run, created):
    if os.path.exists(path):
        return
    if dry_run:
        created.append(path)
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    created.append(path)

def write_json_if_missing(path, data, dry_run, created):
    if os.path.exists(path):
        return
    if dry_run:
        created.append(path)
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    created.append(path)

def mkdir_if_missing(path, dry_run, created):
    if os.path.isdir(path):
        return
    if dry_run:
        created.append(path + "/")
        return
    os.makedirs(path, exist_ok=True)
    # keep empty dirs in git
    keep = os.path.join(path, ".gitkeep")
    with open(keep, "w"):
        pass
    created.append(path + "/")

def scaffold_app(app, dry_run=False):
    created = []
    app_root = os.path.join(BASE, app)
    app_human = humanize(app)

    # store/ image placeholders (".TODO" suffix so they don't accidentally ship)
    for fname in ["icon_512_playstore.png", "feature_graphic_1024x500.png",
                  "icon_1024_appstore.png"]:
        todo_path = os.path.join(app_root, "store", fname + ".TODO")
        real_path = os.path.join(app_root, "store", fname)
        if not os.path.exists(real_path):
            write_if_missing(todo_path,
                f"# Replace this file with the real {fname}\n"
                f"# See CLAUDE.md § 'Per-app required folder structure' for dimensions.\n",
                dry_run, created)

    # screenshot folders
    for sub in ["phone", "iphone_6_9"]:
        mkdir_if_missing(os.path.join(app_root, "store", "screenshots", sub), dry_run, created)
    for sub in ["tablet_7", "tablet_10"]:  # optional
        # don't force-create these, skip
        pass

    # metadata/en-US text files
    for fname, tmpl in TEXT_TEMPLATES.items():
        path = os.path.join(app_root, "metadata", "en-US", fname)
        write_if_missing(path, tmpl.format(app_human=app_human), dry_run, created)

    # metadata/ json files
    write_json_if_missing(os.path.join(app_root, "metadata", "app_info.json"),
                          app_info_template(app), dry_run, created)
    write_json_if_missing(os.path.join(app_root, "metadata", "privacy.json"),
                          privacy_template(app), dry_run, created)
    write_json_if_missing(os.path.join(app_root, "metadata", "content_rating.json"),
                          content_rating_template(app), dry_run, created)
    write_json_if_missing(os.path.join(app_root, "metadata", "iaps.json"),
                          iaps_template(app), dry_run, created)
    write_json_if_missing(os.path.join(app_root, "metadata", "review_notes.json"),
                          review_notes_template(app), dry_run, created)

    return created


# ---------- main -------------------------------------------------------------

def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    do_all  = "--all" in args
    args = [a for a in args if not a.startswith("--")]

    if do_all:
        apps = list_apps()
    else:
        apps = args

    if not apps:
        print("Usage: init_app_metadata.py <AppName> [AppName ...] | --all [--dry-run]",
              file=sys.stderr)
        sys.exit(1)

    total_created = 0
    for app in apps:
        if not os.path.isdir(os.path.join(BASE, app, "android")):
            print(f"! Skipping {app}: no android/ directory")
            continue
        created = scaffold_app(app, dry_run=dry_run)
        if created:
            verb = "Would create" if dry_run else "Created"
            print(f"\n{app}: {verb} {len(created)} file(s)/dir(s):")
            for p in created:
                print(f"   + {os.path.relpath(p, BASE)}")
            total_created += len(created)
        else:
            print(f"{app}: already fully scaffolded")

    summary = "Would create" if dry_run else "Created"
    print(f"\n{summary} {total_created} item(s) total across {len(apps)} app(s).")
    if dry_run:
        print("(dry-run — nothing was written)")


if __name__ == "__main__":
    main()
