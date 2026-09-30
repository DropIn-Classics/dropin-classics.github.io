# dropin-classics.github.io

The website of DropIn Classics: classic DOS games made to run natively
on today's computers, each port a native compatibility implementation
requiring an installed copy of its game. The page says what the
organisation aims for and what each released port gives the player.

- `template.html`: the page, with `{{PORTS}}` where the ports go.
- `ports/*.json`: one record per port (docs/PORT-RECORD.md).
- `style.css`, `favicon.svg`: the look.
- `index.html`: made by `tools/build.py`, served by GitHub Pages.
- `tools/check.py`: what must hold before a commit; `tools/hooks/` its hook.
- `AGENTS.md`: the rules for changing any of this.

## Use

    git config core.hooksPath tools/hooks   # once per clone
    python3 tools/build.py                  # index.html from the template and records
    python3 tools/check.py                  # all ok?
    python3 tools/check.py --online         # and the records match GitHub's releases?

Python 3, standard library only.

## Publishing

The repository is `DropIn-Classics/dropin-classics.github.io`; GitHub
Pages serves `main`'s root (Settings > Pages: deploy from a branch,
`main`, `/ (root)`). `.nojekyll` makes it serve the files as they are.
