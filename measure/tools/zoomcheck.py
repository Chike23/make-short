import cv2, numpy as np, json, sys
N = {'r1': 2919, 'r2': 2534, 'r3': 2694, 'r4': 2600, 'r5': 3240, 'r6': 2216}
orb = cv2.ORB_create(1500); bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
out = {}
for r, n in N.items():
    tr = json.load(open(f'{r}/transitions.json')); edges = sorted(o['a'] for o in tr if o['kind'] != 'in-shot change')
    def near_edge(f): return any(abs(f - e) < 20 for e in edges)
    zin = zout = pan = still = tot = 0; rates = []
    for f in range(30, n - 15, 15):
        if near_edge(f) or near_edge(f + 15): continue
        a = cv2.imread(f'{r}/frames/f_{f + 1:05d}.jpg', 0)[330:1280]; b = cv2.imread(f'{r}/frames/f_{f + 16:05d}.jpg', 0)[330:1280]   # skip caption band
        ka, da = orb.detectAndCompute(a, None); kb, db = orb.detectAndCompute(b, None)
        if da is None or db is None or len(ka) < 30 or len(kb) < 30: continue
        m = sorted(bf.match(da, db), key=lambda x: x.distance)[:300]
        if len(m) < 20: continue
        pa = np.float32([ka[x.queryIdx].pt for x in m]); pb = np.float32([kb[x.trainIdx].pt for x in m])
        M, inl = cv2.estimateAffinePartial2D(pa, pb, method=cv2.RANSAC, ransacReprojThreshold=2.0)
        if M is None or inl.sum() < 15: continue
        s = float(np.hypot(M[0, 0], M[1, 0])); t = float(np.hypot(M[0, 2], M[1, 2]))
        tot += 1; rates.append((s - 1) * 100 / 15)          # % zoom per frame
        if s > 1.003: zin += 1
        elif s < 0.997: zout += 1
        elif t > 3: pan += 1
        else: still += 1
    out[r] = dict(windows=tot, zoom_in_pct=round(100 * zin / tot), zoom_out_pct=round(100 * zout / tot), pan_pct=round(100 * pan / tot), still_pct=round(100 * still / tot),
                  median_zoom_in_pct_per_s=round(float(np.median([x for x in rates if x > 0.02]) * 30), 2) if any(x > 0.02 for x in rates) else 0)
    print(r, out[r])
json.dump(out, open('zoom_summary.json', 'w'), indent=1)
