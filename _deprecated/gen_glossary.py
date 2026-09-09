# -*- coding: utf-8 -*-
import json, re, html

d = json.load(open('data/iqan_full_text.json'))
def clean(t): return re.sub(r'(\S)\d{1,3}(?=\s|$|[.,;:!?”"’\')\]])', r'\1', t)
FULL = {n: clean(d[str(n)]) for n in range(1, 291)}

def refs(term, limit=5):
    """Paragraphs where the term appears, so citations are never invented."""
    # Allow a plural: the text says "Imáms", "divines", "luminaries".
    pat = r'\b' + re.escape(term) + r's?\b'
    hits = [n for n, t in FULL.items() if re.search(pat, t, re.I)]
    return hits[:limit], len(hits)

def ref_html(term, limit=5):
    hits, total = refs(term, limit)
    if not hits: return ''
    s = ' · '.join('¶%d' % n for n in hits)
    if total > len(hits): s += ' · +%d more' % (total - len(hits))
    return '<span class="g-ref">%s</span>' % s

SECTIONS = [
 ("Reading the older English",
  "Shoghi Effendi's translation keeps the cadence of the Persian by using a deliberately older English. "
  "These are the words most likely to stop a reader who has not met them before.",
  [
  ("behooveth", "Is fitting for, is incumbent upon. <em>It behooveth us</em> means <em>we ought to</em>."),
  ("hearken", "To listen, especially with attention and obedience."),
  ("cavil", "To raise petty or unfair objections. Bahá'u'lláh uses it repeatedly for the objections of the learned who quibble rather than seek."),
  ("naught", "Nothing. <em>Brought to naught</em> means reduced to nothing."),
  ("methinks", "It seems to me."),
  ("wherefore", "For which reason; therefore. Sometimes also <em>why</em>."),
  ("whoso", "Whoever."),
  ("fain", "Gladly, willingly — or, with <em>would</em>, <em>eager to</em>."),
  ("nigh", "Near."),
  ("verily", "Truly, in truth. A marker of solemn assertion rather than an ordinary intensifier."),
  ("yea", "Yes — and often <em>indeed</em>, introducing a stronger restatement of what was just said."),
  ("nay", "No — and often <em>rather</em>, correcting what precedes it: not this, but this."),
  ("abstruse", "Hard to understand; obscure. Used of the verses whose meaning is veiled."),
  ("effulgent", "Radiant, shining brilliantly."),
  ("abase", "To bring low, to humble."),
  ("ere", "Before."),
  ]),

 ("Words for the Manifestation of God",
  "The Book turns on the idea that God is unknowable in essence and is made known through Messengers. "
  "A large part of its vocabulary names those Messengers under different figures.",
  [
  ("Manifestation", "A Manifestation of God — one of the Messengers through whom God is revealed. The central term of the Book. Each has a twofold station: one of essential unity with the others, one of individual distinction."),
  ("Daystar", "The sun; a title for the Manifestation, whose rising and setting Bahá'u'lláh uses as the governing image of revelation."),
  ("dayspring", "The place or moment of dawn; the point from which the light of revelation breaks."),
  ("Quintessence", "The purest essence of a thing."),
  ("luminaries", "Lights — used both of the Prophets and, in the symbolic reading of scripture, of the divines of a former dispensation."),
  ("dispensation", "The period of one Manifestation's revelation and law, from its rise until the next."),
  ("concourse", "An assembly. <em>The concourse on high</em> is the company of the heavenly host."),
  ]),

 ("The learned, and their objections",
  "Much of the Book is addressed to a single problem: why the religious learned of every age have been "
  "the first to reject the Messenger of their own time.",
  [
  ("divines", "Religious scholars and clergy. In this Book almost always the learned of Islám who opposed the Báb — and, before them, the scribes and doctors who opposed each earlier Prophet."),
  ("doctors", "Teachers of religious law — the same class as the divines, in the older English sense of <em>doctor</em> as <em>learned authority</em>."),
  ("veils of glory", "Bahá'u'lláh's term for the very titles and doctrines that ought to reveal the truth but which people turn into barriers — <em>Seal of the Prophets</em> being his chief example."),
  ]),

 ("Terms from Islám",
  "The Book was revealed for a Muslim reader and argues from the Qur'án and the traditions of the Imáms throughout.",
  [
  ("Qá’im", "<em>He who shall arise.</em> In Shí'ah Islám, the Promised One expected at the end of the age — identified in this Book with the Báb. The uncle's questions were largely about the traditions concerning His advent."),
  ("Mihdí", "<em>The rightly guided one.</em> Another title of the same Promised One."),
  ("Imám", "For Shí'ah Muslims, one of the twelve rightful successors of Muḥammad, beginning with ‘Alí. Their recorded sayings are the <em>traditions</em> the Book so often cites."),
  ("Qiblih", "The direction faced in prayer. Its change from Jerusalem to Mecca is used as the type case of a divine command altered to test the faithful."),
  ("Ka‘bih", "The sanctuary at Mecca toward which Muslims pray."),
  ("Súrah", "A chapter of the Qur'án."),
  ("Ṣiráṭ", "The bridge over hell, finer than a hair and sharper than a sword, which the soul must cross — interpreted here in a spiritual sense."),
  ("Kawthar", "A river or fountain of paradise; abundance."),
  ("Salsabíl", "A fountain of paradise named in the Qur'án."),
  ("Zaqqúm", "The bitter tree of hell named in the Qur'án — the opposite of the fruits of paradise."),
  ("Sadratu’l-Muntahá", "<em>The Tree beyond which there is no passing.</em> The limit of created understanding; a title for the Manifestation of God."),
  ("Urvatu’l-Vuthqá", "<em>The Sure Handle</em> — the firm hold spoken of in the Qur'án, that will not break for whoever grasps it."),
  ("Mullá", "A Muslim cleric or scholar."),
  ("Siyyid", "A descendant of Muḥammad."),
  ("Baní-Háshim", "The clan of Háshim, the family of Muḥammad."),
  ]),

 ("The Báb and the Bayán",
  "",
  [
  ("Bayán", "<em>Exposition.</em> The Báb's principal Book. Bahá'u'lláh notes that the Báb foretold that the Promised One would complete its unfinished text — which the Íqán does."),
  ("Point of the Bayán", "A title of the Báb."),
  ("Mustagháth", "<em>He Who is invoked.</em> A name whose numerical value the Báb used to indicate the time of the next Manifestation."),
  ]),

 ("Symbolic terms the Book unfolds",
  "These are not obscure words so much as familiar ones that Bahá'u'lláh argues have been misread. "
  "Each is given a spiritual rather than a literal meaning.",
  [
  ("Seal of the Prophets", "A title of Muḥammad, taken by many to mean that no Messenger could follow Him. Bahá'u'lláh treats the literal reading as the greatest of the <em>veils of glory</em>."),
  ("Day of Resurrection", "Not the raising of bodies from graves, but the rising of a new Manifestation and the spiritual quickening — or death — of those who meet Him."),
  ("Day of Judgment", "The same Day, considered as the moment at which souls are divided by their response to the Manifestation."),
  ("City of God", "The Revelation of each age, renewed at fixed intervals for the guidance of mankind."),
  ("Guarded Tablet", "The heavenly record in which all things are inscribed."),
  ("Riḍván", "<em>Paradise</em>, and also <em>good pleasure</em> — the garden of God's acceptance. Later the name of the festival marking Bahá'u'lláh's declaration, a year after this Book was revealed."),
  ]),

 ("Places",
  "",
  [
  ("Sinai", "The mountain where Moses was addressed by God."),
  ("Ḥijáz", "The western region of Arabia containing Mecca and Medina."),
  ("Mecca", "The city of Muḥammad's birth and the direction of Muslim prayer."),
  ("Medina", "The city to which Muḥammad emigrated."),
  ("Karbilá", "The plain in ‘Iráq where Imám Ḥusayn was martyred."),
  ("Kúfih", "A city of ‘Iráq closely associated with Imám ‘Alí."),
  ("Zawrá", "Baghdád — the city in which this Book was revealed."),
  ]),
]

parts = []
for title, blurb, entries in SECTIONS:
    parts.append('<section class="gloss-section">')
    parts.append('<h2>%s</h2>' % html.escape(title))
    if blurb: parts.append('<p class="gloss-blurb">%s</p>' % blurb)
    parts.append('<dl>')
    for term, definition in entries:
        parts.append('  <dt>%s %s</dt>' % (html.escape(term), ref_html(term)))
        parts.append('  <dd>%s</dd>' % definition)
    parts.append('</dl>')
    parts.append('</section>')

body = '\n'.join(parts)
page = '''---
title: "Glossary"
subtitle: "Words and terms in the Kitáb-i-Íqán that may be unfamiliar"
toc: true
toc-depth: 2
---

::: {.lead}
The Íqán is a translated nineteenth-century Persian text arguing from the Qur'án and from Islamic
tradition, in an English deliberately older than our own. Three kinds of word tend to stop a reader:
archaic English, terms from Islám, and ordinary words being used in a special sense.
:::

Paragraph numbers show where each term appears; every reference here was taken from the text rather
than from memory. Click a number on a week page to read the passage on bahai.org.

```{=html}
%s
```

::: {.source-note}
Missing something? [Tell me what stopped you](ask.qmd) and I will add it.
:::
''' % body

open('glossary.qmd', 'w').write(page)
n_entries = sum(len(e) for _,_,e in SECTIONS)
print('wrote glossary.qmd — %d sections, %d entries' % (len(SECTIONS), n_entries))
