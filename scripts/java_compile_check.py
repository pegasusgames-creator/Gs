#!/usr/bin/env python3
"""java_compile_check.py — compile every app's Java without the Android SDK.

Builds each <App>/android/app/src/main/java/** with javac against:
  * the real Android framework classes (Robolectric android-all, API 35,
    downloaded once to ~/.cache/pegasus/ from Maven Central's Google Cloud
    mirror, falling back to repo1.maven.org), and
  * scripts/java_stubs/ — signature stubs of the Google SDKs the wrappers
    call (AdMob, UMP, Billing 8, Play Games v2, Tasks, Firebase, androidx),
  * a generated R class holding every R.<type>.<name> the app's Java uses.

Catches syntax errors, typos, wrong types / arity and illegal trailing
commas before a Gradle build — e.g. the 2026-06 trailing-comma break of all
8 AdMob apps. It does NOT replace a real ./gradlew build (resources,
manifest merge, R8); run that before uploading.

Usage:  python3 scripts/java_compile_check.py [App ...]   (default: all apps)
Needs:  a JDK (javac) on PATH.
"""
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SKIP = {"_template", "_release", "docs", "scripts", "release_aabs", "BLOCKED_APPS",
        "__pycache__", ".git", ".idea", "node_modules"}
JAR = "android-all-15-robolectric-12650502.jar"
URLS = [
    "https://maven-central.storage-download.googleapis.com/maven2/org/robolectric/android-all/15-robolectric-12650502/" + JAR,
    "https://repo1.maven.org/maven2/org/robolectric/android-all/15-robolectric-12650502/" + JAR,
]
CACHE = Path.home() / ".cache" / "pegasus"
STUBS = BASE / "scripts" / "java_stubs"


def framework_jar() -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    jar = CACHE / JAR
    if jar.exists() and jar.stat().st_size > 100_000_000:
        return jar
    for url in URLS:
        try:
            print(f"  downloading {JAR} (~185 MB, once) …")
            tmp = jar.with_suffix(".part")
            with urllib.request.urlopen(url, timeout=600) as r, open(tmp, "wb") as f:
                shutil.copyfileobj(r, f)
            if tmp.stat().st_size > 100_000_000:
                tmp.rename(jar)
                return jar
        except Exception as e:  # noqa: BLE001 — try the next mirror
            print(f"  ! {url.split('/')[2]}: {e}")
    raise SystemExit("could not download the Android framework jar")


def stub_classes(jar: Path) -> Path:
    srcs = sorted(STUBS.rglob("*.java"))
    digest = hashlib.sha1(b"".join(p.read_bytes() for p in srcs)).hexdigest()[:12]
    out = CACHE / f"stubs-{digest}"
    if not out.exists():
        tmp = Path(tempfile.mkdtemp(prefix="stubs-", dir=CACHE))
        r = subprocess.run(["javac", "-nowarn", "-proc:none", "-d", str(tmp), "-cp", str(jar), *map(str, srcs)],
                           capture_output=True, text=True)
        if r.returncode:
            raise SystemExit("stub compile failed:\n" + r.stdout + r.stderr)
        tmp.rename(out)
    return out


def check_app(app: str, cp: str):
    jroot = BASE / app / "android/app/src/main/java"
    files = sorted(jroot.rglob("*.java")) if jroot.is_dir() else []
    if not files:
        return app, None, ""
    pkg = re.search(r"^package\s+([\w.]+);", files[0].read_text(encoding="utf-8"), re.M)
    refs = {}
    for f in files:
        for t, n in re.findall(r"\bR\.(\w+)\.(\w+)", f.read_text(encoding="utf-8", errors="replace")):
            refs.setdefault(t, set()).add(n)
    with tempfile.TemporaryDirectory() as tmp:
        rj = Path(tmp) / "R.java"
        body = "".join(f"public static final class {t} {{ " + " ".join(f"public static final int {n}=0;" for n in sorted(ns)) + " } "
                       for t, ns in sorted(refs.items()))
        rj.write_text(f"package {pkg.group(1) if pkg else 'r'};\npublic final class R {{ {body}}}\n", encoding="utf-8")
        r = subprocess.run(["javac", "-nowarn", "-proc:none", "-encoding", "UTF-8", "-d", str(Path(tmp) / "out"),
                            "-cp", cp, *map(str, files), str(rj)], capture_output=True, text=True)
    errs = [l for l in (r.stdout + r.stderr).splitlines() if ": error:" in l]
    return app, r.returncode == 0, "\n".join(errs[:6])


def main() -> int:
    if not shutil.which("javac"):
        raise SystemExit("javac not found — install a JDK 17+ (Android Studio's bundled JBR works) and put it on PATH")
    apps = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not apps:
        apps = sorted(d.name for d in BASE.iterdir()
                      if d.is_dir() and d.name not in SKIP and not d.name.startswith(".") and (d / "android").is_dir())
    jar = framework_jar()
    cp = f"{jar}{':' if sys.platform != 'win32' else ';'}{stub_classes(jar)}"
    bad = 0
    with ThreadPoolExecutor(max_workers=6) as ex:
        for app, ok, errs in ex.map(lambda a: check_app(a, cp), apps):
            if ok is None:
                continue
            if not ok:
                bad += 1
                print(f"  ✗ {app}\n" + "\n".join("      " + e for e in errs.splitlines()))
    print(f"java compile check: {len(apps) - bad}/{len(apps)} OK" + (f", {bad} failing" if bad else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
