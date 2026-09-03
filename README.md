# Kitáb-i-Íqán Study — site

A Quarto website for the fourteen-week study. Prose pages and reveal.js slides come from
the same Markdown source, so the presentation and the site never drift apart.

```
index.qmd            home
schedule.qmd         the fourteen sessions
slides/intro.qmd     "Why we study the Íqán" — reveal.js deck
styles.scss          site theme
slides/custom.scss   slide theme
make-slides-pdf.sh   optional local PDF export
```

## Working on it

```bash
quarto preview
```

Live-reloads as you edit. To build once into `_site/`:

```bash
quarto render
```

## Presenting

Open the slides page and press **F** for fullscreen. Useful keys:

| Key | Does |
|---|---|
| `→` / `←` | next / previous slide |
| `F` | fullscreen |
| `S` | speaker view (notes + timer + next slide) |
| `O` | slide overview grid |
| `B` | blank the screen |
| `?` | all shortcuts |

## Publishing to GitHub Pages

1. Create an empty repo on github.com (no README, no .gitignore).
2. In this folder:

   ```bash
   git init && git add -A && git commit -m "Iqán study site"
   git branch -M main
   git remote add origin https://github.com/YOURNAME/YOURREPO.git
   git push -u origin main
   ```

3. In the repo: **Settings → Pages → Build and deployment → Source → GitHub Actions**.
4. Uncomment `site-url` in `_quarto.yml` and set it to your Pages URL.

Every push to `main` then runs `.github/workflows/publish.yml`, which renders the site,
exports the slides to `slides/intro.pdf`, and deploys. **The PDF download link only works
once this has run** — it is generated during the build, not committed.

The PDF step is marked `continue-on-error`, so if the export breaks the site still
deploys and only the PDF link goes missing. Check the run's log if the link 404s.

## Exporting the slide PDF locally

Optional; the Action already does this on every push.

```bash
./make-slides-pdf.sh
```

This drives the real deck through reveal.js's `?print-pdf` stylesheet, so the PDF matches
the web slides exactly. It needs a Chromium, which `decktape` downloads on first run
(~170 MB). Output lands in `_site/slides/`.

If you would rather not install that: open
`http://localhost:PORT/slides/intro.html?print-pdf` in a browser and use ⌘P → Save as PDF.

## Adding quotes to the home page

Two styles, depending on who is speaking.

**A Central Figure** — wrap in `.scripture`. The framing prose steps down in size and the
quotations step up and turn semibold, so the quoted words carry the section. No attribution
line: the heading already names the author. Add as many `>` blocks as you like.

```markdown
### From the letters of Shoghi Effendi

::: {.scripture}
Optional framing sentence, set smaller and quieter than body text.

> First quotation.

> Second quotation.
:::
```

**Personal accounts** — wrap in `.accounts`. Quotations stay italic at close to body size and
each one carries a name, since these come from many different voices.

```markdown
::: {.accounts}
Optional framing prose, at normal body size.

> The account.
>
> [Name of the person]{.attrib}
:::
```

**A long passage** — wrap in `.passage`. Same gold rule and size as `.scripture` but normal
weight, for quotations running more than a few lines. `summary.qmd` uses it.

`index.qmd` has a commented-out template of the accounts form just below the Personal accounts
section.

## Adding a deck

Drop a new `.qmd` in `slides/` with `format: revealjs` and `theme: [default, custom.scss]`.
`quarto render` and `make-slides-pdf.sh` both pick it up automatically.
