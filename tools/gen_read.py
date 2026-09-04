# -*- coding: utf-8 -*-
"""Generate read.qmd with all 290 paragraphs as static HTML.

Rendering the passages at build time rather than with JavaScript is what lets
`read.html#p102` land directly: the browser resolves the anchor during its
first layout pass, exactly as it would for any ordinary heading. The runtime
script only attaches behaviour to what is already in the document.

Keep the markup here in step with `row()` in _includes/notes.html, which still
builds rows dynamically for the My notes page.

Run from the site directory:  python3 tools/gen_read.py
"""
import html
import json
import re

TEXT = json.load(open('data/iqan_full_text.json'))
FOOTNOTES = json.load(open('data/footnotes.json'))['notes']
LINKS = json.load(open('data/paragraph-links.json'))

# Same rule as the runtime: a run of 1-3 digits naming a known footnote is a
# marker. Assembled segment by segment so escaping never runs over a marker
# (HTML entities contain digits of their own).
def render_text(raw):
    out, last = [], 0
    for m in re.finditer(r'\d+', raw):
        num = m.group(0)
        out.append(html.escape(raw[last:m.start()]))
        if len(num) <= 3 and num in FOOTNOTES:
            out.append(
                '<sup class="fn-ref" data-fn="%s" role="button" tabindex="0" '
                'aria-label="Footnote %s">%s</sup>' % (num, num, num))
        else:
            out.append(html.escape(num))
        last = m.end()
    out.append(html.escape(raw[last:]))
    return ''.join(out)


STRUCTURE_BEFORE = {
    1:   [('part-label', 'Part One'),
          ('invocation', 'IN THE NAME OF OUR LORD, THE EXALTED, THE MOST HIGH.')],
    102: [('part-label', 'Part Two')],
}
STRUCTURE_AFTER = {
    101: [('part-end', 'END OF PART ONE')],
    290: [('part-end', 'END')],
}

TARGETS = (
    '<span class="ask-targets">'
    '<span class="ask-copied">Prompt copied — paste it into</span>'
    '<a href="https://claude.ai/new" target="_blank" rel="noopener">Claude</a>'
    '<a href="https://chatgpt.com/" target="_blank" rel="noopener">ChatGPT</a>'
    '<a href="https://gemini.google.com/app" target="_blank" rel="noopener">Gemini</a>'
    '</span>')

parts = []
for n in range(1, 291):
    for cls, label in STRUCTURE_BEFORE.get(n, []):
        parts.append('<div class="struct %s">%s</div>' % (cls, html.escape(label)))

    anchor = LINKS['links'].get(str(n))
    num_html = ('<a class="note-num" href="%s%s" target="_blank" rel="noopener" '
                'title="Read paragraph %d on bahai.org">%d</a>'
                % (LINKS['base'], anchor, n, n)) if anchor else \
               ('<span class="note-num">%d</span>' % n)

    parts.append(
        '<div class="note-row" id="p%d">'
        '<div class="note-main">'
        '<div class="note-head">%s</div>'
        '<div class="note-text">%s</div>'
        '</div>'
        '<aside class="note-side">'
        '<textarea class="note-input" rows="2" aria-label="Your note on paragraph %d" '
        'placeholder="Your note on paragraph %d…"></textarea>'
        '<div class="note-bar"><span class="note-saved"></span></div>'
        '<div class="note-ask">'
        '<button type="button" class="ask-btn send-btn">Send as question</button>'
        '<button type="button" class="ask-btn">Ask AI about this paragraph</button>'
        '%s'
        '</div>'
        '</aside>'
        '</div>'
        % (n, num_html, render_text(TEXT[str(n)]), n, n, TARGETS))

    for cls, label in STRUCTURE_AFTER.get(n, []):
        parts.append('<div class="struct %s">%s</div>' % (cls, html.escape(label)))

page = '''---
title: "Read"
subtitle: "The Kitáb-i-Íqán, paragraphs 1–290"
toc: false
page-layout: full
---

<!-- This page is generated. Edit tools/gen_read.py and re-run it, not this file. -->

::: {.lead}
The whole Book, with room to write beside it. Notes save as you type and stay in this browser —
keep a copy from the [My notes](notes.qmd) page.
:::

::: {.attribution}
The Kitáb-i-Íqán, translated by Shoghi Effendi. Copyright © Bahá'í International Community.
Text from the [Bahá'í Reference Library](https://www.bahai.org/library/authoritative-texts/bahaullah/kitab-i-iqan/).
:::

Superscript numbers are the footnotes of the published text; click one to read it. Paragraph
numbers link to the passage in the Bahá'í Reference Library.

```{=html}
<div id="read-text" class="paragraph-notes read-page" data-prerendered="true">
%s
</div>
```
''' % '\n'.join(parts)

open('read.qmd', 'w').write(page)
print('wrote read.qmd — %d paragraphs, %d bytes' % (290, len(page)))
