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
GLHITS = json.load(open('data/glossary-hits.json'))

# Same rule as the runtime: a run of 1-3 digits naming a known footnote is a
# marker. Glossary terms are marked from the offsets in data/glossary-hits.json,
# the same file the runtime reads, so both pages mark identical words.
# Assembled segment by segment so escaping never runs over a marker (HTML
# entities contain digits of their own).
def render_text(raw, n):
    marks = []
    for m in re.finditer(r'\d+', raw):
        num = m.group(0)
        if len(num) <= 3 and num in FOOTNOTES:
            marks.append((m.start(), m.end(), 'fn', num))
    for start, end, slug in GLHITS.get(str(n), []):
        marks.append((start, end, 'gl', slug))
    marks.sort()

    out, last = [], 0
    for start, end, kind, payload in marks:
        if start < last:                 # overlapping - keep the first
            continue
        out.append(html.escape(raw[last:start]))
        if kind == 'fn':
            out.append(
                '<sup class="fn-ref" data-fn="%s" role="button" tabindex="0" '
                'aria-label="Footnote %s">%s</sup>' % (payload, payload, payload))
        else:
            word = html.escape(raw[start:end])
            out.append(
                '<span class="gl-ref" data-gl="%s" role="button" tabindex="0" '
                'aria-label="Glossary: %s">%s</span>' % (payload, word, word))
        last = end
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
        % (n, num_html, render_text(TEXT[str(n)], n), n, n, TARGETS))

    for cls, label in STRUCTURE_AFTER.get(n, []):
        parts.append('<div class="struct %s">%s</div>' % (cls, html.escape(label)))

page = '''---
title: "Read"
subtitle: "Official translation into English by Shoghi Effendi. Copyright © Bahá'í International Community.
Text from the [Bahá'í Reference Library](https://www.bahai.org/library/authoritative-texts/bahaullah/kitab-i-iqan/)."
toc: false
page-layout: full
---

Other languages: 
- [Spanish](https://bahai.es/wp-content/uploads/2015/01/Kit%C3%A1b-i-Iqan.pdf)
- [Arabic/Persian](https://drive.google.com/file/d/18CDbfJAt_Z49cKO6MXn1j7y0pp8TWWkj/view?usp=sharing)

<!-- This page is generated. Edit tools/gen_read.py and re-run it, not this file. -->

Superscript numbers are the footnotes of the published text, and dotted words have a glossary
entry. Click either to read it.

```{=html}
<div id="read-text" class="paragraph-notes read-page" data-prerendered="true">
@@ROWS@@
</div>
```

::: {.source-note}
Glossary entries are the "Glossary and Notes" of the published Kitáb-i-Íqán, transcribed at
[bahai-library.com](https://bahai-library.com/writings/bahaullah/iqan/iq-glos.htm).
:::
'''.replace('@@ROWS@@', '\n'.join(parts))

open('read.qmd', 'w').write(page)
print('wrote read.qmd — %d paragraphs, %d bytes' % (290, len(page)))
