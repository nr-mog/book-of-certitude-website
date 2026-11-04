# -*- coding: utf-8 -*-
"""Generate wordfreq.qmd, how often each word occurs in the Kitáb-i-Íqán.

Counts come from data/iqan_full_text.json, the English text keyed by paragraph
number. Footnote markers are digits glued to the preceding word ("God8"), so
all digits are dropped before splitting. Words are lowercased; apostrophes and
internal hyphens stay part of the word (Bahá’u’lláh, loving-kindness), while
the em dash separates words. Verses the book quotes are counted with the rest.

Part One is paragraphs 1–101, Part Two 102–290.

Run from the site directory:  python3 tools/gen_wordfreq.py
"""
import json
import re
from collections import Counter

TEXT = json.load(open('data/iqan_full_text.json'))
PART_TWO = 102

# Modern English function words. The archaic forms (hath, thee, unto, ye) are
# left out on purpose: they are part of the book's voice and good quiz material.
COMMON = set('''
a about above after again against all am an and any are as at be because been
before being below between both but by can could did do does doing down during
each few for from further had has have having he her here hers herself him
himself his how i if in into is it its itself just me more most my myself no
nor not now of off on once only or other our ours ourselves out over own same
she should so some such than that the their theirs them themselves then there
these they this those through to too under until up upon very was we were what
when where which while who whom whose why will with would you your yours
yourself yourselves
'''.split())

WORD = re.compile(r"[^\W\d_]+(?:[’'-][^\W\d_]+)*")


def words(text):
    return WORD.findall(re.sub(r'\d+', ' ', text).replace('⁠', '').lower())


def count():
    total, part1, part2, paras = Counter(), Counter(), Counter(), Counter()
    for num, text in TEXT.items():
        ws = words(text)
        total.update(ws)
        (part1 if int(num) < PART_TWO else part2).update(ws)
        paras.update(set(ws))
    rows = [[w, n, part1[w], part2[w], paras[w], w in COMMON]
            for w, n in sorted(total.items(), key=lambda kv: (-kv[1], kv[0]))]
    return rows, sum(total.values())


def page(rows, n_words):
    data = json.dumps(rows, ensure_ascii=False, separators=(',', ':'))
    return f'''---
title: "Word Frequencies in the Kitáb-i-Íqán"
toc: false
page-layout: full
---

<!-- This page is generated. Edit tools/gen_wordfreq.py and re-run it, not this file. -->

::: {{.lead .lead-sm}}
How often does each word appear in the Book of Certitude? The English text has **{n_words:,} words**, of which **{len(rows):,}** are different. Counts include the verses Bahá'u'lláh quotes, and treat *sun* and *suns* as different words. Common English words like *the* and *of* are hidden at first; archaic forms like *hath* and *unto* are always shown.
:::

```{{=html}}
<div class="wf" id="wf">
  <div class="wf-controls">
    <input type="search" id="wf-search" placeholder="Find a word…" aria-label="Find a word">
    <label><input type="checkbox" id="wf-common"> Show common words</label>
    <label>Show top
      <select id="wf-top"><option>25</option><option selected>50</option><option>100</option></select>
    </label>
  </div>
  <div class="wf-chart" id="wf-chart" role="list"></div>
  <div class="wf-tip" id="wf-tip" role="tooltip" hidden></div>
  <h2 class="anchored">Every word</h2>
  <p class="wf-note" id="wf-count"></p>
  <table class="wf-table">
    <thead><tr><th>Rank</th><th>Word</th><th>Total</th><th>Part One</th><th>Part Two</th><th>Paragraphs</th></tr></thead>
    <tbody id="wf-rows"></tbody>
  </table>
</div>
<style>
.wf {{ --wf-bar: var(--bs-link-color); --wf-faint: color-mix(in srgb, var(--bs-body-color) 55%, transparent); }}
.wf-controls {{ display: flex; flex-wrap: wrap; gap: .75rem 1.5rem; align-items: center; margin: 1rem 0 1.5rem; font-size: .95rem; }}
.wf-controls input[type=search] {{ flex: 1 1 14rem; max-width: 20rem; padding: .35rem .6rem; border: 1px solid var(--wf-faint); border-radius: 4px; background: transparent; color: inherit; }}
.wf-controls select {{ background: transparent; color: inherit; border: 1px solid var(--wf-faint); border-radius: 4px; }}
.wf-chart {{ display: grid; grid-template-columns: max-content 1fr max-content; gap: 2px .75rem; align-items: center; }}
.wf-label {{ text-align: right; font-size: .95rem; }}
.wf-track {{ position: relative; height: 1.1rem; }}
.wf-bar {{ height: 100%; background: var(--wf-bar); border-radius: 0 4px 4px 0; min-width: 2px; }}
.wf-row:hover .wf-bar, .wf-row:focus .wf-bar {{ filter: brightness(1.15); }}
.wf-row {{ display: contents; cursor: default; }}
.wf-val {{ font-variant-numeric: tabular-nums; font-size: .85rem; color: var(--wf-faint); }}
.wf-tip {{ position: fixed; z-index: 10; pointer-events: none; padding: .4rem .6rem; border-radius: 4px; font-size: .85rem; line-height: 1.4; background: var(--bs-body-bg); color: var(--bs-body-color); border: 1px solid var(--wf-faint); box-shadow: 0 2px 8px rgba(0,0,0,.15); }}
.wf-note {{ color: var(--wf-faint); font-size: .9rem; }}
.wf-table {{ width: 100%; max-width: 40rem; font-size: .95rem; font-variant-numeric: tabular-nums; }}
.wf-table th, .wf-table td {{ padding: .2rem .6rem; border-bottom: 1px solid color-mix(in srgb, var(--bs-body-color) 12%, transparent); }}
.wf-table th:not(:nth-child(2)), .wf-table td:not(:nth-child(2)) {{ text-align: right; }}
</style>
<script>
(() => {{
  const ROWS = {data};  // [word, total, part one, part two, paragraphs, common]
  const $ = id => document.getElementById(id);
  const chart = $('wf-chart'), tip = $('wf-tip'), body = $('wf-rows');
  const rank = new Map(ROWS.map((r, i) => [r[0], i + 1]));
  const fmt = n => n.toLocaleString();

  function visible() {{
    const q = $('wf-search').value.trim().toLowerCase();
    const common = $('wf-common').checked;
    return ROWS.filter(r => (common || !r[5]) && (!q || r[0].includes(q)));
  }}

  function tipHTML(r) {{
    return `<strong>${{r[0]}}</strong> — ${{fmt(r[1])}} times<br>` +
      `Part One ${{fmt(r[2])}} · Part Two ${{fmt(r[3])}}<br>` +
      `in ${{fmt(r[4])}} of 290 paragraphs · rank ${{rank.get(r[0])}} overall`;
  }}

  function draw() {{
    const rows = visible();
    const top = rows.slice(0, +$('wf-top').value);
    const max = top.length ? top[0][1] : 1;
    chart.innerHTML = top.map((r, i) =>
      `<div class="wf-row" role="listitem" tabindex="0" data-i="${{i}}">` +
      `<span class="wf-label">${{r[0]}}</span>` +
      `<span class="wf-track"><span class="wf-bar" style="display:block;width:${{100 * r[1] / max}}%"></span></span>` +
      `<span class="wf-val">${{fmt(r[1])}}</span></div>`).join('');
    chart.querySelectorAll('.wf-row').forEach(el => {{
      const r = top[el.dataset.i];
      const show = e => {{
        tip.innerHTML = tipHTML(r); tip.hidden = false;
        const box = (e.clientX ? null : el.querySelector('.wf-bar').getBoundingClientRect());
        const x = e.clientX ?? box.right, y = e.clientY ?? box.top;
        tip.style.left = Math.min(x + 14, innerWidth - tip.offsetWidth - 8) + 'px';
        tip.style.top = (y + 14) + 'px';
      }};
      el.addEventListener('mousemove', show);
      el.addEventListener('focus', show);
      el.addEventListener('mouseleave', () => tip.hidden = true);
      el.addEventListener('blur', () => tip.hidden = true);
    }});
    body.innerHTML = rows.map(r =>
      `<tr><td>${{rank.get(r[0])}}</td><td>${{r[0]}}</td><td>${{fmt(r[1])}}</td>` +
      `<td>${{fmt(r[2])}}</td><td>${{fmt(r[3])}}</td><td>${{fmt(r[4])}}</td></tr>`).join('');
    $('wf-count').textContent = `${{fmt(rows.length)}} words shown. Rank counts every word, common ones included.`;
  }}

  ['wf-search', 'wf-common', 'wf-top'].forEach(id => $(id).addEventListener('input', draw));
  draw();
}})();
</script>
```
'''


if __name__ == '__main__':
    rows, n_words = count()
    open('wordfreq.qmd', 'w').write(page(rows, n_words))
    print(f'{n_words} words, {len(rows)} distinct')
