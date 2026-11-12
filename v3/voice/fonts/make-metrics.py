"""Writes inter-metrics.json (advance widths) for captions-explainer.mjs. Only needed if you change the fonts.
Run: python3 -I make-metrics.py   (needs fonttools: pip install fonttools)"""
import json
from fontTools.ttLib import TTFont

chars = [chr(c) for c in range(32, 127)] + list('‘’“”–—…%°×·éèàçñöüÉ')
out = {}
for key, f in (('regular', 'Inter-Regular.otf'), ('bold', 'Inter-Bold.otf')):
    t = TTFont(f); cmap = t.getBestCmap(); hm = t['hmtx']; o = t['OS/2']
    out[key] = dict(upm=t['head'].unitsPerEm, ascent=o.usWinAscent, descent=o.usWinDescent, cap=o.sCapHeight,
                    adv={c: hm[cmap[ord(c)]][0] for c in chars if ord(c) in cmap})
json.dump(out, open('inter-metrics.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('wrote inter-metrics.json', {k: len(v['adv']) for k, v in out.items()})
