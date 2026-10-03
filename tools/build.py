"""Writes index.html from template.html and ports/.

    python3 tools/build.py          # writes index.html
    python3 tools/build.py --stdout # prints index.html instead (tools/check.py uses this)

Each ports/SLUG.json is one port (fields: see docs/PORT-RECORD.md). The
ports are listed newest release first.

Python 3, standard library only.
"""

import html
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_ports():
    ports = []
    for path in sorted((ROOT / "ports").glob("*.json")):
        with open(path, encoding="utf-8") as f:
            ports.append(json.load(f))
    ports.sort(key=lambda p: p["latest"]["date"], reverse=True)
    return ports


def e(text):
    return html.escape(text, quote=True)


def long_date(iso):
    d = date.fromisoformat(iso)
    return f"{d.strftime('%B')} {d.day}, {d.year}"


# every port's packages, named as doskit's docs/RELEASE.md says: (button,
# file name after the slug); releases/latest/download/ always serves the
# newest release's
PACKAGES = [
    ("Windows", "-windows-x64.zip"),
    ("macOS", "-macos.zip"),
    ("Linux / Steam Deck", "-linux-x64.tar.gz"),
]


def render_port(p):
    repo = p["repo"]
    chips = "".join(f"<li>{e(x)}</li>" for x in p["platforms"])
    brings = "\n".join(
        f"      <li><h4>{e(b['title'])}</h4><p>{e(b['text'])}</p></li>"
        for b in p["brings"])
    latest = p["latest"]
    downloads = "\n".join(
        f'            <a class="button" href="{e(repo)}/releases/latest/download/'
        f'{e(p["slug"] + suffix)}">{e(name)}</a>'
        for name, suffix in PACKAGES)
    return f"""    <article class="port" id="{e(p['slug'])}">
      <div class="port-head">
        <div>
          <h3>{e(p['game'])}</h3>
          <p class="port-meta">{e(p['slug'])} &middot; the original: {e(p['original'])}</p>
          <ul class="chips">{chips}</ul>
          <p class="provenance">{e(p['provenance'])}</p>
        </div>
        <aside class="release">
          <div class="label">Latest release</div>
          <div class="version">{e(latest['version'])}</div>
          <div class="date">{e(long_date(latest['date']))}</div>
          <p class="note">{e(latest['note'])}</p>
          <div class="downloads" aria-label="Download for">
{downloads}
          </div>
          <a class="source" href="{e(repo)}/releases/latest">All files on the release page</a>
          <a class="source" href="{e(repo)}">Source and how it was made</a>
        </aside>
      </div>
      <ul class="brings">
{brings}
      </ul>
      <p class="requires"><strong>You need:</strong> {e(p['requires'])}.</p>
    </article>"""


def render():
    template = (ROOT / "template.html").read_text(encoding="utf-8")
    ports = "\n".join(render_port(p) for p in load_ports())
    return template.replace("{{PORTS}}", ports)


def main():
    if "--stdout" in sys.argv:
        sys.stdout.write(render())
        return
    (ROOT / "index.html").write_text(render(), encoding="utf-8")
    print("written: index.html")


if __name__ == "__main__":
    main()
