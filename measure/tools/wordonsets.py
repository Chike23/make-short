import cv2, numpy as np, json
N = {'r1': 2919, 'r2': 2534, 'r3': 2694, 'r4': 2600, 'r5': 3240, 'r6': 2216}
res = {}
for r, n in N.items():
    prev = None; ons = []; cardstarts = []; empty_prev = True
    for f in range(n):
        im = cv2.imread(f'{r}/frames/f_{f + 1:05d}.jpg')[190:340].astype(np.int16)
        mn = im.min(2); mx = im.max(2)
        wh = ((mn > 215) & (mx - mn < 30)).astype(np.uint8)
        wh = cv2.dilate(wh, np.ones((3, 3), np.uint8))
        anytext = wh.sum() + (((mn > 95) & (mx < 175) & (mx - mn < 22)).sum()) > 250
        if prev is not None:
            new = (wh & (1 - prev)).sum()
            if new > 180 and (not ons or f - ons[-1] >= 3): ons.append(f)
        if anytext and empty_prev: cardstarts.append(f)
        empty_prev = not anytext
        prev = wh
    ons = np.array(ons); gaps = np.diff(ons) / 30
    res[r] = dict(words=len(ons), words_per_s=round(len(ons) / (n / 30), 2), median_gap_s=round(float(np.median(gaps)), 3),
                  cards=len(cardstarts), words_per_card=round(len(ons) / max(1, len(cardstarts)), 2), cards_per_s=round(len(cardstarts) / (n / 30), 2))
    print(r, res[r])
json.dump(res, open('word_summary.json', 'w'), indent=1)
