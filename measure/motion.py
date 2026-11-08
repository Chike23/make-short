"""Camera motion on every frame: Farneback optical flow on the 90x160 small frames (median px/frame, scaled to 720 wide).
usage: python3 motion.py refdir1 [refdir2 ...]   (each refdir needs small.npz from `pipeline.py small`)"""
import sys, json, numpy as np, cv2
for d in [x.rstrip('/') for x in sys.argv[1:]]:
    g = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in np.load(f'{d}/small.npz')['small']]
    mag = []
    for i in range(1, len(g)):
        fl = cv2.calcOpticalFlowFarneback(g[i - 1], g[i], None, 0.5, 3, 9, 3, 5, 1.1, 0)
        mag.append(float(np.median(np.hypot(fl[..., 0], fl[..., 1]))) * 720 / 90)
    m = np.array(mag)
    out = dict(median_px_per_frame_720=float(np.median(m)), still_pct=float((m < 0.5).mean() * 100),
               slow_pct=float((m < 2).mean() * 100), fast_pct=float((m > 10).mean() * 100), p90=float(np.percentile(m, 90)))
    json.dump(dict(out, per_frame=[None] + mag), open(f'{d}/motion.json', 'w'))
    print(d, {k: round(v, 2) for k, v in out.items()})
