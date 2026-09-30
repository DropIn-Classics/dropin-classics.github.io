# A port's record

One file per port, `ports/SLUG.json`, SLUG being the repository's name
in DropIn-Classics. `tools/check.py` checks the form; AGENTS.md says
what may be written in it.

| field | what it holds |
|---|---|
| `slug` | the repository's name, the same as the file's |
| `game` | the game's name as the player knows it (the GOG release's name) |
| `original` | platform, medium and year of the original, e.g. `DOS, CD-ROM, 1994` |
| `requires` | what the player must own, e.g. `Pinball Dreams Deluxe from GOG.com` (no full stop; the page adds one) |
| `provenance` | "A native compatibility implementation requiring an installed copy of GAME", and in the same sentence where the game's data comes from |
| `repo` | `https://github.com/DropIn-Classics/SLUG` |
| `latest.version` | the newest release's tag, `vX.Y` |
| `latest.date` | its date on GitHub, `YYYY-MM-DD` |
| `latest.note` | one or two sentences, for players, from the release's notes |
| `platforms` | where the released packages run, as the player would say it |
| `brings` | 3 to 8 entries `{"title", "text"}`: what the port gives the player, most important first; a title of a few words, a text of one to three sentences |

The page has a button per system, each linking to
`REPO/releases/latest/download/SLUG-windows-x64.zip`, `SLUG-macos.zip`
and `SLUG-linux-x64.tar.gz` (the names doskit's RELEASE.md gives every
port's packages), so the buttons are right even before the record is
updated; the version shown is the record's. `tools/check.py --online`
checks that the latest release has these files.
