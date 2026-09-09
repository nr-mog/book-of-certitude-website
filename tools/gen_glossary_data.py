# -*- coding: utf-8 -*-
"""Build data/glossary.json and data/glossary-hits.json.

Source: the "Glossary and Notes" back matter of the published Kitáb-i-Íqán,
transcribed at
https://bahai-library.com/writings/bahaullah/iqan/iq-glos.htm
A copy of that page is kept in tools/sources/ so this is reproducible offline.

Two files come out of it:

  data/glossary.json       {slug: {term, def}} - the entries, verbatim.
  data/glossary-hits.json  {paragraph: [[start, end, slug], ...]} - where each
                           term occurs, as offsets into the raw paragraph text.

Computing the hits here, once, is deliberate: the Read page is static HTML and
the week pages are built by JavaScript, and both must mark the same words. Two
implementations of the matching rule would drift, so instead they share one
precomputed answer.

Run from the site directory:  python3 tools/gen_glossary_data.py
"""
import html
import json
import re
import unicodedata

SRC = 'tools/sources/iq-glos.html'

# The glossary's transliteration is not always the text's. Where they differ,
# the text's spelling is what has to be matched; each of these was checked
# against data/iqan_full_text.json rather than guessed.
ALIASES = {
    'Al-Medina': ['Medina'],
    'Súrih': ['Súrah'],
    "Rik'ats": ["Rak'ats"],
    'Cain and Abel': ['Abel and Cain'],
    'Nudbih, Prayer of': ['Prayer of Nudbih', 'Nudbih'],
    'Taff (land of)': ['Taff'],
    'Siyyid Yahyá, surnamed Vahíd': ['Siyyid Yahyá'],
    "Mullá 'Abd'l-Kháliq-i-Yazdí": ["Mullá 'Abdu'l-Kháliq-i-Yazdí"],
    "Mullá N'imatu'lláh-i-Mázindarání": ["Mullá Ni'matu'lláh-i-Mázindarání"],
    'Alif, Lám, Mím': ['Alif. Lám. Mím'],
}

# Single letters and bare words that would fire on unrelated text.
NO_MATCH = {'Há'}

APOS = "'‘’ʻʼ`´"


def fold(s):
    """Diacritic- and apostrophe-insensitive, length-preserving per character."""
    out = []
    for ch in s:
        if ch in APOS:
            out.append("'")
            continue
        d = unicodedata.normalize('NFD', ch)
        d = ''.join(c for c in d if not unicodedata.combining(c)).lower()
        # Keep the mapping one-to-one so offsets stay usable.
        out.append(d[0] if d else ' ')
    return ''.join(out)


def parse_entries(path):
    raw = open(path, encoding='iso-8859-1').read()
    raw = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', raw, flags=re.S)
    raw = re.sub(r'<br[^>]*>', ' ', raw)
    raw = re.sub(r'</?p[^>]*>', '\n\n', raw)
    raw = re.sub(r'<[^>]+>', '', raw)
    text = html.unescape(raw).replace('\xa0', ' ')

    text = text[text.index('GLOSSARY AND NOTES') + len('GLOSSARY AND NOTES'):]
    cut = text.find('Back to:')
    if cut > 0:
        text = text[:cut]

    paras = [re.sub(r'\s+', ' ', p).strip() for p in text.split('\n\n')]
    paras = [p for p in paras if p and p not in ('Back to Top', 'x', 'X')
             and not re.fullmatch(r'Page \d+', p)]
    paras = [re.sub(r'\s*(\[Index\]|Page \d+)\s*$', '', p).strip() for p in paras]

    entries = []
    for p in paras:
        m = re.match(r'^([^:]{1,60}):\s*(.*)$', p)
        if m:
            entries.append([m.group(1).strip(), m.group(2).strip()])
        elif entries:
            # A definition broken across a printed page break.
            entries[-1][1] = (entries[-1][1] + ' ' + p).strip()
    return entries


def clean_term(t):
    t = t.strip().strip('"').strip()
    t = re.sub(r"^['`‘’]+(?=['`‘’]\w)", '', t)  # stray '`Abdu'lláh
    return t.strip()


def clean_def(d):
    d = re.sub(r'"\s*"', '" "', d)          # "glory,""Splendor," in the source
    d = re.sub(r'\s+([,.;:])', r'\1', d)    # stray spaces before punctuation
    return re.sub(r'\s+', ' ', d).strip()


def slugify(t):
    s = unicodedata.normalize('NFD', t)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^A-Za-z0-9]+", '-', s).strip('-').lower()
    return s


def pattern(term):
    parts = [re.escape(fold(p)) for p in re.split(r"[\s\-.]+", term) if p]
    if not parts:
        return None
    body = r'[\s\-.]+'.join(parts)
    # Digits may follow: footnote markers sit flush against the word ("Zaqqúm144").
    # A possessive is allowed ("Leviathan's") but no other apostrophe, or "Bahá"
    # would match inside "Bahá'u'lláh".
    return re.compile(r"(?<![a-z0-9'])" + body + r"s?(?:'s)?(?![a-z'])")


def main():
    entries = parse_entries(SRC)
    gloss, matchers = {}, []
    for term, defn in entries:
        term = clean_term(term)
        slug = slugify(term)
        if not slug:
            continue
        gloss[slug] = {'term': term, 'def': clean_def(defn)}
        if term in NO_MATCH:
            continue
        for variant in [term] + ALIASES.get(term, []):
            pat = pattern(variant)
            if pat:
                matchers.append((len(variant), pat, slug))
    # Longest first, so "Mullá Báqir" wins over any shorter term inside it.
    matchers.sort(key=lambda x: -x[0])

    text = json.load(open('data/iqan_full_text.json'))
    hits, total = {}, 0
    for num, raw in text.items():
        folded = fold(raw)
        found, seen = [], set()
        for _, pat, slug in matchers:
            if slug in seen:
                continue
            m = pat.search(folded)          # first occurrence in this paragraph
            if m:
                end = m.end()
                if folded[m.start():end].endswith("'s"):
                    end -= 2                # underline the word, not the possessive
                found.append([m.start(), end, slug])
                seen.add(slug)
        # Longest span first where two start together, so "'Abdu'lláh-i-Ubayy"
        # is not shadowed by the "'Abdu'lláh" entry sitting inside it.
        found.sort(key=lambda s: (s[0], -s[1]))
        kept = []
        for span in found:                  # drop any that overlap an earlier one
            if not kept or span[0] >= kept[-1][1]:
                kept.append(span)
        if kept:
            hits[num] = kept
            total += len(kept)

    json.dump({'source': {
        'title': 'Glossary and Notes, from the published Kitáb-i-Íqán',
        'url': 'https://bahai-library.com/writings/bahaullah/iqan/iq-glos.htm'},
        'entries': gloss},
        open('data/glossary.json', 'w'), ensure_ascii=False, indent=1, sort_keys=True)
    json.dump(hits, open('data/glossary-hits.json', 'w'),
              ensure_ascii=False, separators=(',', ':'), sort_keys=True)

    unused = sorted(s for s in gloss if not any(s == k[2] for k in matchers)
                    or not any(s == sp[2] for v in hits.values() for sp in v))
    print('glossary.json: %d entries' % len(gloss))
    print('glossary-hits.json: %d marks across %d paragraphs' % (total, len(hits)))
    print('entries never matched (%d): %s' % (len(unused), ', '.join(unused)))


if __name__ == '__main__':
    main()
