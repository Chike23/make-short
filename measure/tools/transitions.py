"""Classify cut candidates: scene change or not, and how (hard cut / dissolve / dip through dark / push-through).
Uses small.npz (90x160 frames). Writes transitions.json in the reel folder."""
import sys, json, numpy as np, cv2
d = sys.argv[1]
z = np.load(f'{d}/small.npz'); sm = z['small'].astype(np.float32); hs = z['hists']
N = len(sm)
band = json.load(open(f'{d}/caption_band.json'))
mask = np.ones(160, bool); mask[int((band['y_centre'] - 50) / 8): int((band['y_centre'] + 50) / 8) + 1] = False
mask[:int(330 / 8)] = False                       # captions + labels live in the top band
g = sm[:, mask]
lines = open(f'{d}/log_small.txt').read().splitlines()[2:]
fr = sorted({int(l.split()[1]) for l in lines if l.strip() and l.split()[0].isdigit()})
cl = []
for f in fr:
    if cl and f - cl[-1][1] <= 6: cl[-1][1] = f
    else: cl.append([f, f])
luma = g.mean(axis=(1, 2, 3))
out = []
for a, b in cl:
    A, B = max(a - 3, 0), min(b + 3, N - 1)
    hd = cv2.compareHist(hs[A], hs[B], cv2.HISTCMP_BHATTACHARYYA)
    pix = np.abs(g[A] - g[B]).mean()
    mids = list(range(A + 1, B))
    # dissolve fit per middle frame: F = al*A + (1-al)*B
    al, res = [], []
    for m in mids:
        x = (g[A] - g[B]).ravel(); y = (g[m] - g[B]).ravel()
        k = float(np.clip((x * y).sum() / ((x * x).sum() + 1e-6), -0.5, 1.5))
        al.append(k); res.append(float(np.abs(y - k * x).mean()))
    dark = [m for m in mids if luma[m] < 0.6 * min(luma[A], luma[B]) and luma[m] < 40]
    blend = [m for m, k, r in zip(mids, al, res) if 0.1 < k < 0.9 and r < 0.35 * pix + 3]
    scene = (hd > 0.45 and pix > 20) or pix > 25
    if not scene: kind = 'in-shot change'
    elif dark: kind = 'dip through dark'
    elif len(blend) >= 1: kind = 'dissolve'
    elif b - a <= 1: kind = 'hard cut'
    else: kind = 'other (push / wipe / motion)'
    span = [min(dark + blend), max(dark + blend)] if (dark or blend) else None
    out.append(dict(a=a, b=b, kind=kind, span=span, span_frames=(span[1] - span[0] + 1) if span else 0,
                    hist=round(float(hd), 2), pix=round(float(pix), 1)))
# slow changes the spike detector misses: big histogram change over 15 frames, away from every cluster
D = np.array([cv2.compareHist(hs[i], hs[min(i + 15, N - 1)], cv2.HISTCMP_BHATTACHARYYA) for i in range(N)])
near = np.zeros(N, bool)
for a, b in cl: near[max(0, a - 20):min(N, b + 20)] = True
slow = []
i = 0
while i < N - 15:
    if D[i] > 0.45 and not near[i] and not near[min(i + 15, N - 1)]:
        j = i + int(np.argmax(D[i:i + 15])); slow.append(j); i = j + 30
    else: i += 1
for j in slow: out.append(dict(a=j, b=j + 15, kind='slow change (check)', span=[j, j + 15], span_frames=16, hist=round(float(D[j]), 2), pix=0))
out.sort(key=lambda o: o['a'])
json.dump(out, open(f'{d}/transitions.json', 'w'), indent=1)
for o in out: print(f"{o['a']:5d}-{o['b']:<5d} {o['kind']:28s} span={o['span']} hist={o['hist']} pix={o['pix']}")
