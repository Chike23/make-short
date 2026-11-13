import cv2, numpy as np, json
N = {'r1': 2919, 'r2': 2534, 'r3': 2694, 'r4': 2600, 'r5': 3240, 'r6': 2216}
res = {}
for r, n in N.items():
    box = cap = 0; tot = 0; boxed_runs = 0; prev_box = False
    for f in range(0, n, 2):
        im = cv2.imread(f'{r}/frames/f_{f + 1:05d}.jpg')[190:330].astype(int)
        B, G, R = im[..., 0], im[..., 1], im[..., 2]
        blue = ((B > 180) & (R < 110) & (B - R > 100)).sum()
        mn = im.min(2); mx = im.max(2)
        white = ((mn > 215) & (mx - mn < 30)).sum(); grey = ((mn > 95) & (mx < 175) & (mx - mn < 22)).sum()
        hb = blue > 120; hc = (white + grey) > 250
        box += hb; cap += hc; tot += 1
        if hb and not prev_box: boxed_runs += 1
        prev_box = hb
    res[r] = dict(caption_frames_pct=round(100 * cap / tot, 1), box_frames_pct=round(100 * box / tot, 1), boxes_per_min=round(boxed_runs / (n / 30) * 60, 1))
    print(r, res[r])
json.dump(res, open('cap_summary.json', 'w'), indent=1)
