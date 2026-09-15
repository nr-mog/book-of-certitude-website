# -*- coding: utf-8 -*-
"""Print the HTML for selected paragraphs, for pasting into a week handout.

The markup matches the Read page: footnote markers and glossary terms are
rendered as the same elements, so the popovers wired up in _includes/notes.html
work here too without any extra code.

No ids are emitted. The notes block further down a week page already uses
id="pN" for every paragraph of that week, and a second element with the same
id would break the anchor links from the schedule.

Usage, from the site directory:

    python3 tools/gen_passages.py 1 2
    python3 tools/gen_passages.py 8 13
"""
import html
import json
import re
import sys

TEXT = json.load(open('data/iqan_full_text.json'))
FOOTNOTES = json.load(open('data/footnotes.json'))['notes']
GLHITS = json.load(open('data/glossary-hits.json'))


def render_text(raw, n):
    """Identical rule to render_text() in tools/gen_read.py."""
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
        if start < last:
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


def main(numbers):
    print('```{=html}')
    for n in numbers:
        print('<div class="passage">'
              '<a class="passage-num" href="../read.html#p%d">&para;%d</a>'
              '<div class="passage-text">%s</div>'
              '</div>' % (n, n, render_text(TEXT[str(n)], n)))
    print('```')


if __name__ == '__main__':
    main([int(a) for a in sys.argv[1:]])
