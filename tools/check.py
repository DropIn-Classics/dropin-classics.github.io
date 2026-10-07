"""What must hold before a commit; prints `all ok` or what is wrong.

    python3 tools/check.py           # the repository by itself
    python3 tools/check.py --online  # also each port's latest release on GitHub

The hook (tools/hooks/pre-commit) runs the first form. --online fetches
each port's latest.json (the file the ports' update check reads) and
compares its version with the record's; run it when a record changes.
"""

import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.dont_write_bytecode = True  # importing build must not leave a tools/__pycache__
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402

ROOT = build.ROOT
ORG = "https://github.com/DropIn-Classics/"
PROVENANCE = "native compatibility implementation requiring an installed copy of"
FIELDS = {"slug": str, "game": str, "original": str, "requires": str,
          "provenance": str, "repo": str, "latest": dict, "platforms": list,
          "brings": list}
# Words that misstate what a port is, and names that do not belong here.
FORBIDDEN = ["standalone", "stand-alone", "completely native", "fully native",
             "contains the game", "my code", "i wrote", "written by me",
             "pinball fantasies", "pfemu", "pfnative"]
# Files allowed to name the forbidden words (to forbid them).
FORBIDDEN_EXEMPT = {"AGENTS.md", "tools/check.py"}
# The only kinds of file the site is made of: no pictures, sound or
# programs, so nothing of a game can end up here.
ALLOWED_SUFFIXES = {".html", ".css", ".svg", ".json", ".md", ".py", ""}
ALLOWED_SVG = {"favicon.svg"}


def tracked_files():
    out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [f for f in out.splitlines() if (ROOT / f).is_file()]


def check_record(name, p, errors):
    for field, kind in FIELDS.items():
        if not isinstance(p.get(field), kind) or not p.get(field):
            errors.append(f"{name}: {field} missing or not a {kind.__name__}")
    if errors:
        return
    if name != p["slug"] + ".json":
        errors.append(f"{name}: file name is not slug + .json")
    if p["repo"] != ORG + p["slug"]:
        errors.append(f"{name}: repo must be {ORG}{p['slug']}")
    if "package" in p and (not isinstance(p["package"], str) or not p["package"] or
                         re.search(r"[/\\ ]", p["package"])):
        errors.append(f"{name}: package must be a plain slug when given")
    if PROVENANCE not in p["provenance"]:
        errors.append(f"{name}: provenance must say '{PROVENANCE} ...'")
    latest = p["latest"]
    if not re.fullmatch(r"v\d+\.\d+", latest.get("version", "")):
        errors.append(f"{name}: latest.version must be vX.Y")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", latest.get("date", "")):
        errors.append(f"{name}: latest.date must be YYYY-MM-DD")
    if not latest.get("note"):
        errors.append(f"{name}: latest.note missing")
    if not 3 <= len(p["brings"]) <= 8:
        errors.append(f"{name}: brings must have 3 to 8 entries")
    for b in p["brings"]:
        if set(b) != {"title", "text"} or not b["title"] or not b["text"]:
            errors.append(f"{name}: each brings entry needs exactly title and text")


def check_online(p, errors):
    url = f"{p['repo']}/releases/latest/download/latest.json"
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            data = json.load(r)
            version = data["version"]
    except Exception as exc:  # any failure is reported, not raised
        errors.append(f"{p['slug']}: {url}: {exc}")
        return
    files = {pkg.get("file") for pkg in data.get("packages", {}).values()}
    pkg = p.get("package", p["slug"])
    for _, suffix in build.PACKAGES:
        if pkg + suffix not in files:
            errors.append(f"{p['slug']}: {pkg + suffix} not in the latest release")
    if version != p["latest"]["version"]:
        errors.append(f"{p['slug']}: GitHub's latest is {version}, the record says "
                      f"{p['latest']['version']}")


def main():
    errors = []
    files = tracked_files()

    ports = []
    for path in sorted((ROOT / "ports").glob("*.json")):
        try:
            p = json.loads(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            errors.append(f"{path.name}: {exc}")
            continue
        check_record(path.name, p, errors)
        ports.append(p)
    if not ports:
        errors.append("ports/: no records")

    for f in files:
        suffix = Path(f).suffix
        if suffix not in ALLOWED_SUFFIXES or (suffix == ".svg" and f not in ALLOWED_SVG):
            errors.append(f"{f}: not a kind of file the site is made of")
        if f in FORBIDDEN_EXEMPT or suffix not in {".html", ".css", ".json", ".md", ".py"}:
            continue
        text = (ROOT / f).read_text(encoding="utf-8").lower()
        for word in FORBIDDEN:
            if word in text:
                errors.append(f"{f}: '{word}'")

    if not errors:
        page = build.render()
        index = ROOT / "index.html"
        if not index.exists() or index.read_text(encoding="utf-8") != page:
            errors.append("index.html is not what tools/build.py writes (run it)")
        # The home page is built; doskit.html is written by hand.
        pages = {"index.html": page}
        for f in files:
            if f.endswith(".html") and "/" not in f and f not in pages:
                pages[f] = (ROOT / f).read_text(encoding="utf-8")
        for name, html in pages.items():
            # Nothing loaded from elsewhere: no scripts, no outside
            # stylesheets, fonts or pictures.
            if re.search(r"<script", html, re.I):
                errors.append(f"{name}: <script>")
            for m in re.finditer(r'<(link|img|iframe|source|video|audio)\b[^>]*\b(?:href|src)="(https?:)?//',
                                 html, re.I):
                errors.append(f"{name}: loads from elsewhere: {m.group(0)}")
            text = re.sub(r"<[^>]+>", " ", html)
            for m in re.finditer(r"\b(we|we're|we've|our|ours|us|ourselves)\b", text, re.I):
                errors.append(f"{name}: '{m.group(0)}' (the page says I, not we)")
        doskit_repo = "https://github.com/DropIn-Classics/doskit"
        if doskit_repo not in pages.get("doskit.html", ""):
            errors.append("doskit.html: no link to doskit's public repository")
        css = (ROOT / "style.css").read_text(encoding="utf-8")
        if re.search(r"@import|url\(\s*['\"]?(https?:)?//", css):
            errors.append("style.css: loads from elsewhere")

    if "--online" in sys.argv and not errors:
        for p in ports:
            check_online(p, errors)

    for err in errors:
        print(err)
    print("all ok" if not errors else f"{len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
