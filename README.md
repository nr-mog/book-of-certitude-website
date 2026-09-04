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

## The question form

`ask.qmd` holds a form styled to match the site, posting to Formspree. It is connected and
live. To point it at a different form, change the `action` attribute in `ask.qmd` — that is the
only place the endpoint appears.

Fields are `name` (optional), `reference` (optional) and `question` (required). There is a
hidden `_gotcha` honeypot that catches most bots, and `_subject` sets the email subject.

With JavaScript the form submits in place and shows a confirmation without leaving the page.
Without it, the form posts normally and lands on Formspree's own confirmation page — so it
works either way.

Formspree's free tier caps monthly submissions (around 50 at the time of writing). If the study
outgrows that, the same markup works with Basin or Getform by changing only the `action`.

## Personal notes

Readers can write a note against any paragraph. Notes are stored in `localStorage` under
`iqan:note:<paragraph>`, so nothing is transmitted and no accounts are involved. The code lives
in `_includes/notes.html`, injected site-wide via `include-after-body`.

Two data files drive it:

- `data/weeks.json` — which paragraphs each session covers. **Set weeks 12 and 13** here once
  you have redistributed 240-290; a week with `from: null` shows a "not set yet" message instead
  of note boxes.
- `data/paragraphs.json` — optional paragraph text under a `text` key, e.g. `{"27": "..."}`.
  Any paragraph given text renders it above its note box; paragraphs without text show just the
  number and the box.

`data/paragraphs.json` ships empty on purpose. bahai.org's terms of use permit quotation with
attribution but not republishing full texts, so the translation is not bundled here. To include
it, write to termsofuse@bahai.org; if permission is granted, filling in that file lights up
inline text with no code changes.

### The text

`data/iqan_full_text.json` is a flat `{ "27": "…" }` map of all 290 paragraphs. It drives three
things: the passage shown above each note box, the passage embedded in the AI prompt, and the
paragraph references on the Glossary and People pages.

The source carries footnote reference markers from the print edition (`truth."15`, `God8`,
`oppression19`). Every digit run in the Book is one of these — numbers are spelled out in words —
so `clean()` in `_includes/notes.html` strips them for display and for the prompt. The guard
requires the digits to follow a non-space character, so a genuine numeral like "in 1862" would
survive.

### The Read page

`read.qmd` renders all 290 paragraphs from `data/iqan_full_text.json`, using the same note
component as the week pages. Passages are set upright, not italic — this is the text itself, not
a quotation.

### Footnotes

`data/footnotes.json` holds all 186 footnotes of the published text. The markers embedded in the
source (`truth."15`, `God8`) are turned into clickable superscripts by `renderTextHTML()` in
`_includes/notes.html`, which escapes the text first and inserts the `<sup>` elements second —
never the other way round. Clicking one opens a small popover; Escape or a click outside closes it.

Eight footnotes (38, 39, 109, 118, 126, 127, 134, 153) have no marker in the text file — those
references were lost when the text was extracted, so they cannot be linked. Every marker that is
present does resolve to a footnote.

### The Save button

Note rows carry a Save button that is enabled by editing and disabled by pressing. It is an
affordance, not the persistence mechanism: the debounced autosave has already stored the note by
the time the button can be pressed. That is deliberate and is commented in the source. The button
is honest about the outcome — the note really is saved — just not about which code saved it. If
autosave is ever removed, this button must be made real first.

### Glossary and People

`glossary.qmd` and `people.qmd` are generated, not hand-written — the scripts that produced them
compute every paragraph reference from the text rather than trusting memory, so a citation cannot
drift. To add an entry, edit the data structure at the top of the generator and re-run it. Both
pages are plain Quarto after generation, so small edits can also be made in place.

The People page uses `<details>`, so entries start collapsed with no JavaScript involved.

### Paragraph links

`data/paragraph-links.json` maps each paragraph to its anchor on bahai.org, so every paragraph
number on the week pages and the My notes page links to that passage in the official text.

The map was derived by walking body paragraphs in document order across pages 2-9 of the Íqán
in the Bahá'í Reference Library, skipping the unnumbered opening invocation. The count came to
exactly 290, and paragraphs 1, 2, 213, 214 and 290 were checked against the study materials
before the file was written. Page 10 is endnotes and is excluded.

If bahai.org ever restructures those pages the anchors will drift; the paragraph number falls
back to plain text when a link is missing, so nothing breaks visibly.

### Adding a note from the My notes page

The Add a note form takes a paragraph number (1-290) and text. If that paragraph already has a
note, the new text is appended rather than replacing it - the same rule the JSON import follows.

### Submit note as a question

Each note row can send its text to the Ask form, with `reference` set to the paragraph number.
The handover uses `sessionStorage`, not a query string: notes are private, and a URL would put
their contents into browser history.

### Ask AI about this paragraph

Each paragraph row has a button that copies a study prompt to the clipboard, then offers Claude,
ChatGPT and Gemini as places to paste it. No API key, no proxy, no cost — each reader uses their
own account.

Clipboard rather than a deep link, deliberately. `claude://claude.ai/new?q=` needs the desktop
app installed; the mobile `claude://` scheme opens the Code tab and requires Claude Code access;
and `https://claude.ai/new?q=` is not a documented parameter and has been reported broken. Since
most of the group reads on phones, a deep link would fail for most of them. Copying works
everywhere and with any assistant.

The prompt is built in `buildPrompt()` in `_includes/notes.html`. It asks for definitions,
allusions and context, and explicitly tells the model to flag contested meanings rather than
settle them, noting that authoritative interpretation belongs only to ʻAbdu'l-Bahá and Shoghi
Effendi. Edit that function to change what gets asked. If `data/paragraphs.json` has text for
the paragraph it is included in the prompt; otherwise the prompt points at bahai.org.

### The storage caveat

`localStorage` is not durable. Clearing browser data wipes it, it does not sync between devices,
and iOS Safari can evict script-writable storage after about seven days without a visit. The
`notes.qmd` page says this plainly and offers Markdown and JSON export. Markdown is for reading
and printing; JSON is the one that can be restored. Restoring appends to any note already
present at that paragraph rather than overwriting it.

If notes ever need to survive properly, the next step is a passphrase-keyed encrypted backup to
a Cloudflare Worker — still no accounts, but durable. The storage layer is already isolated
behind `load`/`save`/`allNotes`, so that change would not touch the rendering code.

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
