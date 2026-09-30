# Working on the DropIn Classics website

This repository is the website of the DropIn Classics organisation,
served by GitHub Pages from `main` at https://dropin-classics.github.io.
It is kept up to date by agents; this file is the rules. README.md says
what is here, docs/PORT-RECORD.md what a port's record holds.

## Rules

1. `index.html` is generated: change `template.html` (the page) or
   `ports/*.json` (the ports), then run `python3 tools/build.py`. Never
   edit `index.html` by hand.
2. `python3 tools/check.py` must say `all ok` before every commit (the
   hook runs it; `git config core.hooksPath tools/hooks` once per clone).
   Do not skip it (`--no-verify`). When a port's record changed, also run
   `python3 tools/check.py --online`.
3. Work on `main`, commit in small steps with messages like the ones in
   `git log` (what changed and why, in plain words; English). Push only
   when the user asks: a push publishes the site.
4. Write in English, for players, not developers: what a port gives the
   person playing, in plain words. No build details, addresses or tool
   names on the page.
5. Say only what is true of the released port. Every sentence in a
   record's `brings` must be backed by the port's repository (its
   README, port/README.md or the players' README.txt) for its latest
   release; a feature still being worked on is not listed. Numbers,
   versions and dates are copied from the port's repository or from
   GitHub, not from memory.
6. The organisation is one person: the page speaks in the first person
   singular ("I", "me"), never "we", "our" or "us". It is open about
   who does what: the reverse engineering, the porting and the checks
   against the original are done entirely by AI agents (Claude); the
   person chooses the games, sets the goals and tests the ports by
   playing them. Never say or imply that the person wrote the code
   ("my code", "I wrote"). `tools/check.py` refuses the plural and
   those phrases.
7. Version-control history is never rewritten.

## Provenance (permanent)

Every port is a native compatibility implementation requiring an
installed copy of its game: it contains only our code, and the player's
installed release (GOG.com) supplies the game's data at run time.

1. Each port's `provenance` says so in these words ("A native
   compatibility implementation requiring an installed copy of GAME").
   The page never calls a port "standalone", "completely native" or
   "fully native", and never says or implies that it contains or
   replaces the game or its data.
2. No game data on the site: no screenshots, pictures, music, sound,
   logos, box art or bytes of any game file. The site is text, CSS and
   our own SVG (`favicon.svg`); `tools/check.py` refuses other kinds of
   files.
3. No names of other games' ports that are not released in the
   organisation, and no references to Pinball Fantasies, pfemu or
   pfnative anywhere in the repository.
4. The footer's statement stays: independent project, not affiliated
   with GOG.com or the games' makers; the games and their names belong
   to their owners.

## When a port is released or updated

A port is listed once its repository is public in
https://github.com/DropIn-Classics and has a release with `latest.json`.

- **New release of a listed port:** in `ports/SLUG.json` set
  `latest.version` and `latest.date` (the release's date, from GitHub)
  and `latest.note` (one or two sentences from the release's notes, the
  annotated tag's message, for players). Review `brings`: add what the
  release gives the player, change what it changed. Old releases are not
  listed; the page shows only the newest.
- **New port:** add `ports/SLUG.json` (docs/PORT-RECORD.md), 3 to 8
  `brings` entries, most important to the player first.
- Then `tools/build.py`, `tools/check.py --online`, look at the page
  (below), commit.

## Design

A plain, well-made website: the page's look is set in `style.css` and
`template.html`; keep it. Do not bring in a retro/DOS look, frameworks,
JavaScript, web fonts, trackers, analytics or anything loaded from
another host (`tools/check.py` refuses scripts and outside resources).
Light and dark follow the system (`prefers-color-scheme`). The page must
work at phone width (375 px) without sideways scrolling.

Look at the page before committing a change to it: open `index.html` in
a browser, or take pictures headless, e.g.

    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless \
        --screenshot=/tmp/site.png --window-size=1280,2400 index.html

For phone width, headless Chrome will not make a window narrower than
about 500 px: put the page in a 375 px wide `<iframe>` in a scratch page
outside the repository, open it with `--allow-file-access-from-files`
and take its picture. Say in the commit or to the user what
was not looked at.
