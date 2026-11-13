import sys, json, os
from PIL import Image, ImageDraw
d, kinds, name = sys.argv[1], sys.argv[2].split(','), sys.argv[3]
t = [o for o in json.load(open(f'{d}/transitions.json')) if any(o['kind'].startswith(k) for k in kinds)]
N = len([x for x in os.listdir(f'{d}/frames') if x.endswith('.jpg')]); tw, th = 64, 114
rows = []
for o in t:
    if o['kind'].startswith('slow'): fs = list(range(o['a'], min(o['b'] + 1, N), 2))
    else: fs = list(range(max(o['a'] - 3, 0), min(o['b'] + 4, N)))[:13]
    rows.append((o, fs))
W = Image.new('RGB', (110 + 13 * (tw + 2), len(rows) * (th + 13)), 'white'); dr = ImageDraw.Draw(W)
for r, (o, fs) in enumerate(rows):
    y = r * (th + 13); dr.text((2, y + 40), f"{o['a']}-{o['b']}\n{o['kind'][:14]}", fill='black')
    for k, f in enumerate(fs):
        x = 110 + k * (tw + 2); W.paste(Image.open(f'{d}/frames/f_{f + 1:05d}.jpg').resize((tw, th)), (x, y)); dr.text((x + 2, y + th), str(f), fill='black')
W.save(name); print(name, len(rows))
