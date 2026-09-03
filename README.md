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

## Citing a quote

Sources appear in the right margin beside the quote, using ordinary Markdown footnotes.
`index.qmd` sets `reference-location: margin` in its front matter; below 992px the note drops
inline under the quote instead.

```markdown
> The Íqán is the most important book written on the spiritual significance of the Cause.[^light]

[^light]: *The Light of Divine Guidance*, vol. 1, p. 37. [bahai.org](https://www.bahai.org/...)
```

Put the definition at the end of the file. The link is optional — a citation with no URL renders
fine, which is how the letters written on Shoghi Effendi's behalf are handled.

Because it is plain footnote syntax, switching the whole page to numbered footnotes at the page
foot is a one-line change: drop `reference-location: margin`. Adding `footnotes-hover: true`
shows each source in a popup on hover.

Quotes with no source yet simply carry no marker.

## Connecting the question form

`ask.qmd` holds a form styled to match the site. It is **not connected yet** — until it is, it
tells submitters so rather than posting into the void.

To turn it on:

1. Create a free form at <https://formspree.io>. It gives you an endpoint like
   `https://formspree.io/f/xayzwbqd`.
2. In `ask.qmd`, replace `YOUR_FORM_ID` with the part after `/f/`. It appears once, in the
   form's `action`.
3. `quarto render`, then push.

Fields are `name` (optional), `reference` (optional) and `question` (required). There is a
hidden `_gotcha` honeypot that catches most bots, and `_subject` sets the email subject.

With JavaScript the form submits in place and shows a confirmation without leaving the page.
Without it, the form posts normally and lands on Formspree's own confirmation page — so it
works either way.

Formspree's free tier caps monthly submissions (around 50 at the time of writing). If the study
outgrows that, the same markup works with Basin or Getform by changing only the `action`.

## Adding a week's materials

Each session row on the schedule links to two things:

- `slides/week-NN.qmd` — the deck, opened in presentation mode
- `weeks/week-NN.qmd` — the handout page

Both already exist as stubs for every week. Edit them in place; no schedule changes needed.
Decks inherit their reveal.js config from `slides/_metadata.yml`, so a week's deck only needs a
title and content.

To offer a week's deck as a PDF download, add its name to the list in
`.github/workflows/publish.yml` (`for name in intro; do`) and in `make-slides-pdf.sh`.

## Adding a deck

Drop a new `.qmd` in `slides/` with `format: revealjs` and `theme: [default, custom.scss]`.
`quarto render` and `make-slides-pdf.sh` both pick it up automatically.
