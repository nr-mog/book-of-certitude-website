# -*- coding: utf-8 -*-
"""Build the sequential outline on the Summary page from tools/sources/outline.txt.

The source is plain lines, one entry per line:

    PART ONE
    - Detachment as the condition of the journey | 1–2
      - A sub-topic | 2

Two-space indent marks a sub-topic; the text after " | " is the paragraph
reference (a number, an en-dash range, or a comma list). Each reference links
to the Read page at its first paragraph.

The block is written into summary.qmd between the OUTLINE markers, so the rest
of that page is hand-edited as usual. Re-run after editing the source:

    python3 tools/gen_outline.py && quarto render summary.qmd
"""
import html
import re

SRC = 'tools/sources/outline.txt'
PAGE = 'summary.qmd'
START, END = '<!-- OUTLINE:START -->', '<!-- OUTLINE:END -->'


def ref_html(ref):
    first = re.match(r'\d+', ref).group(0)
    return '<a class="ol-ref" href="read.html#p%s">%s</a>' % (first, html.escape(ref))


def main():
    out = ['```{=html}', '<div class="seq-outline">']
    for line in open(SRC, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line.strip():
            continue
        if line.startswith('PART '):
            out.append('<h3 class="ol-part">%s</h3>' % html.escape(line.title()))
            continue
        level = 2 if line.startswith('  -') else 1
        text, _, ref = line.strip()[2:].rpartition(' | ')
        out.append('<div class="ol-row ol-l%d"><span class="ol-text">%s</span>%s</div>'
                   % (level, html.escape(text), ref_html(ref.strip())))
    out += ['</div>', '```']
    block = '\n'.join(out)

    page = open(PAGE, encoding='utf-8').read()
    a, b = page.index(START) + len(START), page.index(END)
    open(PAGE, 'w', encoding='utf-8').write(page[:a] + '\n' + block + '\n' + page[b:])


if __name__ == '__main__':
    main()
