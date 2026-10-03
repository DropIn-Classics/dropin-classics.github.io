"""Writes the generated pages from template.html, ports/ and posts/.

    python3 tools/build.py          # writes index.html, blog.html, posts/*.html
    python3 tools/build.py --stdout # prints index.html instead (tools/check.py uses this)

Each ports/SLUG.json is one port (fields: see docs/PORT-RECORD.md). The
ports are listed newest release first.

Each posts/YYYY-MM-DD-slug.md is one blog entry (see docs/BLOG.md): the
first line is `# Title`, the rest simple markdown. Entries are listed
newest first on blog.html, each with its own posts/slug.html page.

Python 3, standard library only.
"""

import html
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "posts"
POST_NAME = re.compile(r"(\d{4})-(\d{2})-(\d{2})-([a-z0-9-]+)\.md")


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


# --- the blog ----------------------------------------------------------

def md_inline(text):
    """Inline markdown: `code`, [text](url), **bold**, *italic*."""
    t = html.escape(text, quote=True)
    t = re.sub(r"`([^`]+?)`", r"<code>\1</code>", t)
    t = re.sub(r"\[([^\]]+?)\]\(([^)\s]+?)\)",
               lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', t)
    t = re.sub(r"\*\*([^*]+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*([^*]+?)\*", r"<em>\1</em>", t)
    return t


def md_plain(text):
    """Inline markdown stripped to plain words (for the lede)."""
    t = re.sub(r"\[([^\]]+?)\]\(([^)\s]+?)\)", r"\1", text)
    return re.sub(r"[*`]", "", text if t == text else t)


def md_to_html(md, name):
    """The markdown a post may hold: ## and ### headings, paragraphs,
    - and 1. lists, > quotes, --- rules, fenced code. No pictures: the
    site holds no game pictures, so posts hold no pictures at all."""
    if "![" in md:
        raise ValueError(f"{name}: pictures are not used on this site")
    blocks = []
    lines = md.split("\n")
    i = 0
    fence = None
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            if fence is None:
                fence = []
            else:
                blocks.append(("code", "\n".join(fence)))
                fence = None
            i += 1
            continue
        if fence is not None:
            fence.append(line)
            i += 1
            continue
        s = line.strip()
        if not s:
            i += 1
            continue
        if re.fullmatch(r"-{3,}", s):
            blocks.append(("hr",))
            i += 1
            continue
        m = re.match(r"(#{2,3})\s+(.*)", s)
        if m:
            if not m.group(2).strip():
                raise ValueError(f"{name}: empty heading")
            blocks.append(("h", len(m.group(1)), m.group(2).strip()))
            i += 1
            continue
        if s.startswith("#"):
            raise ValueError(f"{name}: only ## and ### headings inside a post")
        if s.startswith(">"):
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].strip())
                i += 1
            blocks.append(("quote", " ".join(q for q in quote if q)))
            continue
        if re.match(r"[-*]\s+\S", s):
            items = []
            while i < len(lines) and re.match(r"[-*]\s+\S", lines[i].strip()):
                items.append(re.sub(r"^[-*]\s+", "", lines[i].strip()))
                i += 1
            blocks.append(("ul", items))
            continue
        if re.match(r"\d+\.\s+\S", s):
            items = []
            while i < len(lines) and re.match(r"\d+\.\s+\S", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            blocks.append(("ol", items))
            continue
        para = []
        while i < len(lines) and lines[i].strip():
            if re.match(r"(#{1,3}\s|>|[-*]\s+\S|\d+\.\s+\S|```|---\s*$)",
                        lines[i].strip()):
                break
            para.append(lines[i].strip())
            i += 1
        blocks.append(("p", " ".join(para)))
    if fence is not None:
        raise ValueError(f"{name}: unclosed code block")
    out = []
    for b in blocks:
        kind = b[0]
        if kind == "p":
            out.append(f"<p>{md_inline(b[1])}</p>")
        elif kind == "h":
            out.append(f"<h{b[1]}>{md_inline(b[2])}</h{b[1]}>")
        elif kind == "ul":
            items = "".join(f"<li>{md_inline(x)}</li>" for x in b[1])
            out.append(f"<ul>{items}</ul>")
        elif kind == "ol":
            items = "".join(f"<li>{md_inline(x)}</li>" for x in b[1])
            out.append(f"<ol>{items}</ol>")
        elif kind == "quote":
            out.append(f"<blockquote><p>{md_inline(b[1])}</p></blockquote>")
        elif kind == "code":
            out.append(f"<pre><code>{html.escape(b[1], quote=True)}</code></pre>")
        elif kind == "hr":
            out.append("<hr>")
    return "\n".join(out)


def parse_post(path):
    """Reads one posts/YYYY-MM-DD-slug.md file; raises ValueError."""
    m = POST_NAME.fullmatch(path.name)
    if not m:
        raise ValueError("file name must be YYYY-MM-DD-slug.md")
    iso = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    try:
        date.fromisoformat(iso)
    except ValueError:
        raise ValueError(f"{iso} is not a real date")
    slug = m.group(4)
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    first = next((n for n, line in enumerate(lines) if line.strip()), None)
    if first is None or not lines[first].startswith("# "):
        raise ValueError('the first line must be "# Title"')
    if lines[first].startswith("##"):
        raise ValueError('the first line must be "# Title"')
    title = lines[first][2:].strip()
    if not title:
        raise ValueError("empty title")
    if len(title) > 120:
        raise ValueError("title longer than 120 characters")
    body_md = "\n".join(lines[first + 1:]).strip()
    if not body_md:
        raise ValueError("empty body")
    body_html = md_to_html(body_md, path.name)
    paras = re.findall(r"<p>(.*?)</p>", body_html, re.S)
    if not paras:
        raise ValueError("at least one plain paragraph is needed for the listing")
    lede = html.unescape(re.sub(r"<[^>]+>", "", paras[0]))
    if len(lede) > 300:
        raise ValueError("the first paragraph is longer than 300 characters")
    return {"slug": slug, "date": iso, "title": title,
            "lede": lede, "body": body_html}


def load_posts():
    posts = []
    if POSTS_DIR.is_dir():
        for path in sorted(POSTS_DIR.glob("*.md")):
            posts.append(parse_post(path))
    seen = set()
    for p in posts:
        if p["slug"] in seen:
            raise ValueError(f"{p['slug']}: two posts share this name part")
        seen.add(p["slug"])
    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    return posts


def template_parts():
    """The header and footer shared by every page, from template.html."""
    template = (ROOT / "template.html").read_text(encoding="utf-8")
    header = re.search(r'<header class="top">.*?</header>', template, re.S).group(0)
    footer = re.search(r'<footer class="foot">.*?</footer>', template, re.S).group(0)
    return header, footer


def sub_header(prefix, current):
    """The template's header, with links working from a page at prefix
    ('' for the root, '../' for posts/); current gets aria-current."""
    header, _ = template_parts()
    header = header.replace('href="#"', 'href="PREFIXindex.html"')
    header = re.sub(r'href="#', 'href="PREFIXindex.html#', header)
    header = header.replace("PREFIX", prefix)
    header = header.replace('href="doskit.html"', 'href="PREFIXdoskit.html"')
    header = header.replace('href="blog.html"', 'href="PREFIXblog.html"')
    header = header.replace("PREFIX", prefix)
    marker = f'<a href="{prefix}{current}.html">'
    header = header.replace(marker, marker[:-1] + ' aria-current="page">', 1)
    return header


def page_head(title, desc, prefix=""):
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{prefix}style.css">"""


def render_blog(posts):
    header, footer = template_parts()
    header = sub_header("", "blog")
    items = "\n".join(
        f"""    <li class="post-item">
      <p class="post-meta">{e(long_date(p['date']))}</p>
      <h3><a href="posts/{e(p['slug'])}.html">{e(p['title'])}</a></h3>
      <p class="lede">{e(p['lede'])}</p>
    </li>""" for p in posts)
    return f"""<!doctype html>
<html lang="en">
<head>
{page_head("Blog · DropIn Classics",
           "Notes on the DropIn Classics ports: new releases and playing notes.")}
</head>
<body>

{header}

<main>

<section class="hero">
  <div class="wrap">
    <p class="eyebrow">Notes on the ports</p>
    <h1>Blog.<br><span>What changed for you.</span></h1>
    <p class="lead">Short notes in plain words: when a port has a new release
      and what it gives you, and small playing notes worth knowing.</p>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <h2>All notes</h2>
    <p class="section-lead">Newest first. Each note takes a minute to read.</p>
    <ul class="posts">
{items}
    </ul>
  </div>
</section>

</main>

{footer}

</body>
</html>
"""


def render_post(post, posts):
    idx = [p["slug"] for p in posts].index(post["slug"])
    newer = posts[idx - 1] if idx > 0 else None
    older = posts[idx + 1] if idx + 1 < len(posts) else None
    header, footer = template_parts()
    header = sub_header("../", "blog")
    links = ['<a class="back" href="../blog.html">&larr; All notes</a>']
    if newer:
        links.append(f'<a href="{e(newer["slug"])}.html">&larr; Newer: {e(newer["title"])}</a>')
    if older:
        links.append(f'<a href="{e(older["slug"])}.html">Older: {e(older["title"])} &rarr;</a>')
    nav = "\n      ".join(links)
    return f"""<!doctype html>
<html lang="en">
<head>
{page_head(post["title"] + " · DropIn Classics", post["lede"], "../")}
</head>
<body>

{header}

<main>

<section class="section post">
  <div class="wrap narrow">
    <p class="post-meta">{e(long_date(post["date"]))}</p>
    <h1>{e(post["title"])}</h1>
    <div class="prose">
{post["body"]}
    </div>
    <nav class="post-nav">
      {nav}
    </nav>
  </div>
</section>

</main>

{footer}

</body>
</html>
"""


def main():
    if "--stdout" in sys.argv:
        sys.stdout.write(render())
        return
    (ROOT / "index.html").write_text(render(), encoding="utf-8")
    posts = load_posts()
    (ROOT / "blog.html").write_text(render_blog(posts), encoding="utf-8")
    want = {p["slug"] + ".html" for p in posts}
    for stale in sorted(POSTS_DIR.glob("*.html")):
        if stale.name not in want:
            stale.unlink()
    for p in posts:
        (POSTS_DIR / (p["slug"] + ".html")).write_text(
            render_post(p, posts), encoding="utf-8")
    written = ["index.html", "blog.html"] + sorted(f"posts/{n}" for n in want)
    print("written: " + ", ".join(written))


if __name__ == "__main__":
    main()
