# A blog entry

One file per entry, `posts/YYYY-MM-DD-slug.md`: the date the entry is
written and a short name part, e.g. `posts/2026-10-03-what-this-blog-is-for.md`.
`tools/build.py` makes `blog.html` (all entries, newest first) and one
`posts/slug.html` page per entry from them; `tools/check.py` checks the
form. Never edit the built pages by hand.

The file's first line is the title:

    # What this blog is for

The rest is the entry in simple markdown: paragraphs separated by blank
lines, `##` and `###` headings, `-` and `1.` lists, `> ` quotes, `---`
rules, `` `code` `` and fenced code blocks, `[text](url)` links,
`*italic*` and `**bold**`. The first paragraph shows on `blog.html`,
so keep it to one or two sentences saying what the entry gives the
reader. There are no pictures anywhere on the site, so entries hold no
pictures either.

AGENTS.md says what may be written: English, for players, in the first
person singular, nothing that is not true, no game data of any kind.
