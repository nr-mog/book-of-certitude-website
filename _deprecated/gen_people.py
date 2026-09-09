# -*- coding: utf-8 -*-
import json, re, html

d = json.load(open('data/iqan_full_text.json'))
def clean(t): return re.sub(r'(\S)\d{1,3}(?=\s|$|[.,;:!?”"’\')\]])', r'\1', t)
FULL = {n: clean(d[str(n)]) for n in range(1, 291)}

def find(*pats, limit=6):
    hits = []
    for n, t in FULL.items():
        if any(re.search(p, t, re.I) for p in pats):
            hits.append(n)
    return hits[:limit], len(hits)

def ref_html(pats, limit=6):
    if not pats: return '<span class="p-ref">not named directly</span>'
    hits, total = find(*pats, limit=limit)
    if not hits: return '<span class="p-ref">not named directly</span>'
    s = ' · '.join('¶%d' % n for n in hits)
    if total > len(hits): s += ' · +%d more' % (total - len(hits))
    return '<span class="p-ref">%s</span>' % s

# (name, role, patterns for citation, biography)
GROUPS = [
("The Manifestations of God",
 "The Book's central argument is that these are one succession, differing in station and mission but "
 "not in essence — and that each was denied in His own day by the learned of the age.",
[
 ("Noah", "Prophet of God", [r'Noah'],
  "Preached to His people for nine hundred and fifty years, and was mocked throughout. Bahá'u'lláh "
  "opens His survey of rejected Messengers with Him: the number who believed dwindled rather than grew, "
  "and He was derided by those He came to save."),
 ("Húd", "Prophet of God", [r'Húd'],
  "An Arabian Prophet sent to the tribe of ‘Ád, named in the Qur'án, which has a chapter bearing His name. "
  "The Íqán points the reader to that Súrah as sufficient in itself for anyone with understanding."),
 ("Ṣáliḥ", "Prophet of God", [r'Ṣáliḥ'],
  "An Arabian Prophet sent to the tribe of Thamúd, who called them to God for many years and was answered "
  "with scorn — his people demanding signs and then rejecting the sign when it came."),
 ("Abraham", "The Friend of God", [r'Abraham'],
  "Called <em>Khalílu'lláh</em>, the Friend of God. Before His birth Nimrod dreamed a dream that troubled "
  "him; the soothsayers foretold a child who would overturn the kingdom. Abraham was cast into the fire and "
  "delivered from it — the Book's image of a Prophet whose apparent defeat is His victory."),
 ("Moses", "Prophet of God", [r'\bMoses\b'],
  "Slew a man of the Egyptians, fled to Midian, and was called from the Burning Bush on Sinai. He confronted "
  "Pharaoh with a single companion and was met with the charge of imposture. His changing of no law, and His "
  "rejection by the very people who awaited deliverance, are used throughout the Book as a pattern."),
 ("Jesus", "The Son of Mary", [r'\bJesus\b'],
  "The Íqán devotes its longest sustained passage to the Gospel prophecies attributed to Him — the darkening "
  "of the sun, the falling of the stars, the coming of the Son of Man in the clouds — and reads each "
  "symbolically rather than literally. Bahá'u'lláh also defends the purity of His mother against the "
  "calumnies of her age."),
 ("Muḥammad", "The Apostle of God", [r'Muḥammad(?!\s+‘?Alí)'],
  "The Prophet of Islám, more often named in this Book than any other figure. The Íqán treats the opposition "
  "He met from the Jewish and Arab learned of Ḥijáz, the changing of the Qiblih as a test, and above all the "
  "title <em>Seal of the Prophets</em> — which Bahá'u'lláh argues has been made into a veil rather than a "
  "revelation."),
 ("The Báb", "The Primal Point", [r'\bBáb\b', r'Point of the Bayán', r'Primal Point'],
  "‘Alí-Muḥammad of Shíráz, who declared in 1844 that He was the Qá'im awaited by Shí'ah Islám. The last "
  "third of the Book is given to the proofs of His Revelation: the verses that streamed from Him, His "
  "constancy though young and unsupported, and the heroism of those who died for Him. He foretold that the "
  "Promised One would complete His unfinished Bayán — which this Book does."),
 ("Bahá'u'lláh", "The author of the Book", [],
  "Mírzá Ḥusayn-‘Alí Núrí, who revealed the Íqán in Baghdád in 1862, a year before declaring His Mission in "
  "the Garden of Riḍván. He does not name Himself in it — He writes as <em>this servant</em> — and the Book "
  "was revealed under a station known to Him but not yet proclaimed."),
]),

("Figures of the Bible and the Qur'án",
 "Named in passing as the Book argues from scripture the reader already accepts.",
[
 ("Mary", "Mother of Jesus", [r'\bMary\b'],
  "The Íqán upholds her purity and innocence against the accusations levelled at her, and treats those "
  "accusations as an instance of the general rule that the world abases whom God exalts."),
 ("Yaḥyá, son of Zachariah", "John the Baptist", [r'Yaḥyá,? son of Zachariah', r'\bZachariah\b'],
  "Gave the tidings of the coming of Jesus. In the Book He is the sign in the invisible heaven — the herald "
  "whose announcement was itself the proof, had people been willing to receive it."),
 ("Joseph", "Son of Jacob", [r'\bJoseph\b'],
  "Cited for the verse in which his father perceives his fragrance from a great distance — an image of "
  "recognition by the heart rather than by the eye."),
 ("Pharaoh", "Ruler of Egypt", [r'Pharaoh'],
  "The opponent of Moses, and in the Book the type of worldly power set against divine authority: possessed "
  "of every outward advantage and undone by them."),
 ("Nimrod", "King in the days of Abraham", [r'Nimrod'],
  "Troubled by a dream foretelling a child who would overthrow him, and the one who cast Abraham into the "
  "fire."),
 ("Sámirí", "Maker of the golden calf", [r'Sámirí'],
  "The Qur'ánic figure who led Israel into worshipping the calf while Moses was on the mountain. Bahá'u'lláh "
  "uses him for those who abandon the Moses of knowledge and cling to the Sámirí of ignorance."),
]),

("Islám: the family and companions of Muḥammad",
 "",
[
 ("‘Alí", "Commander of the Faithful, first Imám", [r'‘Alí,? the Commander', r'\bCommander of the Faithful\b'],
  "Cousin and son-in-law of Muḥammad, first of the twelve Imáms. The Book relates the story of two men of "
  "Kúfih who came to Him, and quotes His sayings among the traditions it expounds."),
 ("Ḥusayn", "Son of ‘Alí, third Imám", [r'Ḥusayn, son of ‘Alí', r'Imám Ḥusayn'],
  "Martyred at Karbilá. Bahá'u'lláh calls Him a warrior than whom none on earth was more excellent or nearer "
  "to God, and uses His outward defeat and enduring spiritual sovereignty to show what <em>sovereignty</em> "
  "means when scripture ascribes it to a Manifestation."),
 ("Fáṭimih", "Daughter of Muḥammad", [r'Fáṭimih'],
  "Wife of ‘Alí and mother of Ḥusayn. The <em>Tablet of Fáṭimih</em>, a text of Shí'ah tradition, is cited "
  "for what it records of the character of the Qá'im."),
 ("Ḥamzih", "Prince of Martyrs", [r'Ḥamzih'],
  "Uncle of Muḥammad, killed at the battle of Uḥud. A Qur'ánic verse revealed concerning him and Abú-Jahl is "
  "cited on the difference between the living and the dead in the spiritual sense."),
 ("Salmán", "Formerly Rúz-bih", [r'Salmán', r'Rúz-bih'],
  "A Persian who left his home in search of the truth, passed through the hands of successive masters, and "
  "was honoured by serving them until he found Muḥammad. The Book holds him up as the seeker who persevered."),
 ("Abú-Jahl", "Opponent of Muḥammad", [r'Abú-Jahl'],
  "One of the fiercest adversaries of Muḥammad in Mecca, set against Ḥamzih in the verse the Book cites."),
 ("Naḍr-Ibn-i-Ḥárith and ‘Abdu'lláh-i-Ubayy", "Adversaries", [r'Naḍr', r'Ubayy'],
  "Named among the divines and their associates who inflicted suffering on Muḥammad — evidence, in the Book's "
  "argument, that the learned of an age are reliably the first to oppose it."),
 ("Ibn-i-Ṣúríyá", "A Jewish scholar of Medina", [r'Ibn-i-Ṣúríyá'],
  "Subject of a story the Book tells about recognizing a prophecy and then declining to act on the "
  "recognition."),
]),

("The Imáms and the traditions",
 "Shí'ah tradition records the sayings of the Imáms. The uncle's questions rested on these, and much of the "
 "Book's latter half examines them.",
[
 ("Ja‘far-i-Ṣádiq", "The sixth Imám", [r'Ṣádiq'],
  "Asked by Mufaḍḍal for the sign of the Manifestation, He answered: <em>In the year sixty, His Cause shall "
  "be made manifest, and His Name shall be proclaimed.</em> The Báb declared in 1260 of the Muslim calendar."),
 ("Mufaḍḍal", "Companion of Ṣádiq", [r'Mufaḍḍal'],
  "The questioner in that tradition."),
 ("Jábir", "Transmitter of tradition", [r'Jábir'],
  "Named in connection with the tradition recorded in the <em>Káfí</em> concerning the character of the Qá'im."),
 ("The Twelfth Imám", "The Qá'im, the Mihdí", [r'Qá’im', r'Mihdí'],
  "In Shí'ah belief the Imám who went into concealment and would one day return. The eldest uncle of the Báb "
  "could not reconcile the traditions about Him with his Nephew's claim, and it was that difficulty which "
  "occasioned this Book."),
]),

("The Báb's disciples",
 "In a single passage the Book names the foremost of those who gave their lives, and says their number was "
 "well-nigh four hundred.",
[
 ("Shaykh Aḥmad and Siyyid Káẓim", "The twin resplendent lights", [r'Aḥmad and Káẓim'],
  "Shaykh Aḥmad-i-Aḥsá'í and Siyyid Káẓim-i-Rashtí, whose teaching in the decades before 1844 prepared their "
  "students to expect the Promised One imminently. Bahá'u'lláh calls them twin lights and invokes God's "
  "blessing on their resting-places."),
 ("Mullá Ḥusayn", "The first to believe", [r'Mullá Ḥusayn'],
  "The first to recognize the Báb. Of him the Book says that but for him God would not have been established "
  "upon the seat of His mercy."),
 ("Siyyid Yaḥyá", "Vaḥíd", [r'Siyyid Yaḥyá'],
  "Sent by the Sháh to investigate the Báb's claim and converted by the encounter. The Book calls him the "
  "unique and peerless figure of his age."),
 ("The martyrs named with them", "Well-nigh four hundred", [r'Zanjání', r'Bastámí', r'Bárfurúshí'],
  "Mullá Muḥammad ‘Alíy-i-Zanjání, Mullá ‘Alíy-i-Bastámí, Mullá Sa‘íd-i-Bárfurúshí, Mullá "
  "Ni‘matu'lláh-i-Mázindarání, Mullá Yúsuf-i-Ardibílí, Mullá Mihdíy-i-Khu'í, Siyyid Ḥusayn-i-Turshízí, Mullá "
  "Mihdíy-i-Kandí, Mullá Báqir, Mullá ‘Abdu'l-Kháliq-i-Yazdí and Mullá ‘Alíy-i-Baraqání — named in one "
  "sustained sentence, with the note that their names are inscribed on the Guarded Tablet of God."),
]),

("The reader for whom it was written",
 "",
[
 ("Ḥájí Mírzá Siyyid Muḥammad", "Khál-i-Akbar, the Greater Uncle of the Báb", [],
  "The eldest maternal uncle of the Báb, who admired his Nephew but could not accept Him as the Promised One "
  "because certain traditions seemed unfulfilled. He travelled to Baghdád, put his questions to Bahá'u'lláh "
  "in writing, and received this Book in reply within two days and two nights. He is not named in the text — "
  "he is the <em>brother</em> and <em>friend</em> the Book addresses throughout. He attained certitude, and "
  "later recognized Bahá'u'lláh as well."),
]),
]

parts = []
for title, blurb, people in GROUPS:
    parts.append('<section class="people-section">')
    parts.append('<h2>%s</h2>' % html.escape(title))
    if blurb: parts.append('<p class="gloss-blurb">%s</p>' % blurb)
    for name, role, pats, bio in people:
        parts.append('<details class="person">')
        parts.append('  <summary><span class="p-name">%s</span><span class="p-role">%s</span></summary>'
                     % (html.escape(name), html.escape(role)))
        parts.append('  <div class="p-body"><p>%s</p><p class="p-refs">%s</p></div>' % (bio, ref_html(pats)))
        parts.append('</details>')
    parts.append('</section>')

page = '''---
title: "People"
subtitle: "Everyone the Book names, or leans on without naming"
toc: true
toc-depth: 2
---

::: {.lead}
The Íqán argues from history. It moves through the Prophets in succession, then through the family and
companions of Muḥammad, the Imáms whose recorded sayings its reader accepted, and finally the disciples
of the Báb. Many are named once and assumed to be known.
:::

Each entry is closed to begin with — open the ones you want. Paragraph numbers show where the person
appears in the text.

```{=html}
%s
```

::: {.source-note}
Someone missing? [Let me know](ask.qmd).
:::
''' % '\n'.join(parts)

open('people.qmd','w').write(page)
print('wrote people.qmd — %d groups, %d people' % (len(GROUPS), sum(len(p) for _,_,p in GROUPS)))
