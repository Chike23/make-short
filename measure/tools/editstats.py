import json, numpy as np
FPS = 30
N = {'r1': 2919, 'r2': 2534, 'r3': 2694, 'r4': 2600, 'r5': 3240, 'r6': 2216}      # r6: first version only
REAL_SLOW = {'r1': [1146, 2043], 'r2': [293, 673, 1333, 1385], 'r3': [1007], 'r4': [1787], 'r5': [2490, 3012, 3166], 'r6': [937, 1892]}
TYPE = {'dissolve': 'crossfade', 'dip through dark': 'dip/fade through dark', 'hard cut': 'cut (1-2 frames)',
        'other (push / wipe / motion)': 'vertical slide/push', 'slow change (check)': 'slow crossfade/fade'}
allshots, alltypes, spans, summary = [], {}, [], {}
for r, n in N.items():
    t = [o for o in json.load(open(f'{r}/transitions.json')) if o['a'] < n]
    t = [o for o in t if o['kind'] != 'in-shot change' and (not o['kind'].startswith('slow') or o['a'] in REAL_SLOW[r])]
    starts = sorted(o['a'] for o in t)
    edges = [0] + starts + [n]
    shots = np.diff(edges) / FPS
    allshots += list(shots)
    for o in t:
        k = TYPE[o['kind']]; alltypes[k] = alltypes.get(k, 0) + 1
        if o['kind'] == 'dissolve' and o['span_frames']: spans.append(o['span_frames'])
    summary[r] = dict(secs=round(n / FPS, 1), transitions=len(t), shots=len(shots), mean_shot=round(float(shots.mean()), 2),
                      median_shot=round(float(np.median(shots)), 2), longest=round(float(shots.max()), 1), per_min=round(len(t) / (n / FPS) * 60, 1))
for r, s in summary.items(): print(r, s)
a = np.array(allshots); tot = sum(alltypes.values())
print('ALL shots', len(a), 'mean %.2f median %.2f p10 %.2f p90 %.2f max %.1f' % (a.mean(), np.median(a), np.percentile(a, 10), np.percentile(a, 90), a.max()))
print('per-video mean shot range', min(s['mean_shot'] for s in summary.values()), max(s['mean_shot'] for s in summary.values()))
print('types', {k: f'{v} ({100*v/tot:.0f}%)' for k, v in sorted(alltypes.items(), key=lambda x: -x[1])})
print('dissolve span frames: median', np.median(spans), 'p10-p90', np.percentile(spans, 10), np.percentile(spans, 90))
json.dump(dict(summary=summary, types=alltypes, shot_mean=float(a.mean()), shot_median=float(np.median(a))), open('edit_summary.json', 'w'), indent=1)
