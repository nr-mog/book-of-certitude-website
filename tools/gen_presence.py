# -*- coding: utf-8 -*-
"""Generate presence.qmd, the Qur'anic verses on attaining the Divine Presence.

The verses live in tools/sources/quran-presence.json: the Uthmani Arabic text
(Tanzil, via alquran.cloud) and Rodwell's 1861 English from the Project
Gutenberg edition, with his footnote markers removed. Rodwell orders the suras
by his own chronology and does not number the verses, so each was placed by
hand against the standard numbering.

Each entry marks the word for the meeting and what is met: `arabic_marks` as
[first word, word count] over the space-separated Arabic, `english_marks` as
phrases, each marked at its first occurrence in the English.

Run from the site directory:  python3 tools/gen_presence.py
"""
import html
import json

VERSES = json.load(open('tools/sources/quran-presence.json'))


def mark_arabic(text, marks):
    words = [html.escape(w) for w in text.split()]
    for first, count in sorted(marks, reverse=True):
        last = first + count - 1
        words[first] = '<mark>' + words[first]
        words[last] = words[last] + '</mark>'
    return ' '.join(words)


def mark_english(text, phrases):
    # Marked before escaping would put the tags through html.escape, so find
    # each phrase in the raw text and assemble the pieces in order.
    spans = sorted((text.index(p), text.index(p) + len(p)) for p in phrases)
    out, last = [], 0
    for start, end in spans:
        out.append(html.escape(text[last:start], quote=False))
        out.append('<mark>' + html.escape(text[start:end], quote=False) + '</mark>')
        last = end
    out.append(html.escape(text[last:], quote=False))
    return ''.join(out)


def figure(v):
    s, n = v['ref'].split(':')
    note = f'<p class="verse-note">{html.escape(v["note"], quote=False)}</p>' if 'note' in v else ''
    return (
        f'<figure class="verse" id="q{s}-{n}">'
        f'<figcaption><span class="verse-sura">{v["sura"]} ({v["rodwell_sura"]})</span>'
        f'<span class="verse-ref">{v["ref"]}</span></figcaption>'
        f'<div class="verse-text">'
        f'<p class="verse-arabic" lang="ar" dir="rtl">{mark_arabic(v["arabic"], v["arabic_marks"])}</p>'
        f'<blockquote><p>{mark_english(v["rodwell"], v["english_marks"])}</p></blockquote>'
        f'{note}</div></figure>'
    )


def section(key):
    rows = [v for v in VERSES if v['section'] == key]
    rows.sort(key=lambda v: tuple(int(x) for x in v['ref'].split(':')))
    return len(rows), '```{=html}\n<div class="verse-list">\n' + '\n'.join(map(figure, rows)) + '\n</div>\n```'


n_presence, presence = section('presence')
n_seal, seal = section('seal')

page = f'''---
title: "References to Attaining the Divine Presence in the Qur'án"
toc: false
page-layout: full
include-in-header:
  - text: |
      <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap">
---

<!-- This page is generated. Edit tools/gen_presence.py and tools/sources/quran-presence.json and re-run it, not this file. -->

::: {{.lead .lead-sm}}
Bahá'u'lláh writes that no theme "hath been more emphatically asserted in the holy scriptures" than "attainment unto the Divine Presence". The seal of the prophets is mentioned once in the Qur'án, by contrast there are at least {n_presence} references to attaining the divine presence. In each verse the meeting, and what is met, are highlighted.
:::

```{{=html}}
<label class="verse-toggle"><input type="checkbox" id="show-arabic"> Show Arabic</label>
```

## {n_presence} References to Attaining the Divine Presence {{#presence}}

{presence}

## {n_seal} Reference{"s" if n_seal != 1 else ""} to the Seal of the Prophets {{#seal}}

{seal}

::: {{.source-note}}
Arabic: the Uthmani text, from Tanzil. English: J. M. Rodwell, *The Koran* (1861), from the [Project Gutenberg edition](https://www.gutenberg.org/ebooks/2800), with his footnote markers removed. The sura names in brackets are Rodwell's. Where Rodwell divides a verse in two (23:33, 32:10), both parts are given.

[Back to Week 7](weeks/week-07.qmd) · [Back to the schedule](schedule.qmd)
:::
'''

open('presence.qmd', 'w').write(page)
