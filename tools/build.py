"""Writes index.html from template.html and the ports' records in ports/.

    python3 tools/build.py          # writes index.html
    python3 tools/build.py --stdout # prints it instead (tools/check.py uses this)

Each ports/SLUG.json is one port (fields: see docs/PORT-RECORD.md). The
ports are listed newest release first.
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


def render_port(p):
    repo = p["repo"]
    chips = "".join(f"<li>{e(x)}</li>" for x in p["platforms"])
    brings = "\n".join(
        f"      <li><h4>{e(b['title'])}</h4><p>{e(b['text'])}</p></li>"
        for b in p["brings"])
    latest = p["latest"]
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
          <a class="button" href="{e(repo)}/releases/latest">Download</a>
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
    out = render()
    if "--stdout" in sys.argv:
        sys.stdout.write(out)
    else:
        (ROOT / "index.html").write_text(out, encoding="utf-8")
        print("index.html written")


if __name__ == "__main__":
    main()
