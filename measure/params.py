"""Pool all four analyses into parameters: per-video values, pooled distributions, normalised-time profiles."""
import json, numpy as np, pandas as pd
import sys
KEYS = [d.rstrip('/') for d in sys.argv[1:]]   # usage: python3 params.py refdir1 refdir2 ...  -> params.json in the cwd
BASE = '.'
V = {}; shots = []; cards = []; holds = []; frames = []
for k in KEYS:
    A = json.load(open(f'{k}/analysis.json')); S = A['summary']; V[k] = S
    for s in A['shots']:
        s = dict(s); s['ref'] = k; shots.append(s)
    c = pd.read_csv(f'{k}/caption_cards.csv'); c['ref'] = k; cards.append(c)
    pf = pd.read_csv(f'{k}/per_frame_full.csv'); pf['ref'] = k; pf['tn'] = pf.frame / len(pf); frames.append(pf)
    size = pf.shot_size.values; run = 1
    for i in range(1, len(size)):
        if size[i] == size[i - 1]: run += 1
        else: holds.append((k, size[i - 1], run)); run = 1
    holds.append((k, size[-1], run))
shots = pd.DataFrame(shots); cards = pd.concat(cards); pf = pd.concat(frames)
holds = pd.DataFrame(holds, columns=['ref', 'size', 'frames'])

def q(x, ps=(10, 25, 50, 75, 90)): return {f'p{p}': float(np.percentile(x, p)) for p in ps}
def mmm(key, f=lambda S, k: S[k]):
    vals = [f(V[r], key) for r in KEYS]
    return dict(values=dict(zip(KEYS, vals)), min=float(np.min(vals)), median=float(np.median(vals)), max=float(np.max(vals)))

P = {}
for key in ['duration', 'shots', 'asl', 'shot_len_median', 'shot_len_min', 'shot_len_max', 'dissolves', 'hard_cuts', 'hidden_cuts',
            'size_changes', 'size_changes_inside', 'size_changes_at_cuts', 'size_changes_per_sec', 'size_hold_mean', 'locations',
            'location_changes', 'luma_mean', 'luma_min', 'luma_max', 'p5', 'p95', 'contrast_sd', 'pct_black', 'pct_white',
            'luma_top', 'luma_mid', 'luma_bot', 'sat', 'colourfulness', 'a', 'b', 'warm_frames_pct', 'luma_sd_across_frames']:
    P[key] = mmm(key)
P['transitions_per_min'] = mmm(None, lambda S, k: S['transitions'] / S['duration'] * 60)
P['dissolve_share'] = mmm(None, lambda S, k: S['dissolves'] / max(1, S['transitions']) * 100)
P['location_visit_s'] = mmm(None, lambda S, k: S['duration'] / (S['location_changes'] + 1))
for z in ['EWS', 'WS', 'FS', 'MS', 'MCU', 'CU', 'INS']:
    P[f'time_{z}'] = mmm(None, lambda S, k, z=z: S['size_secs'].get(z, 0) / S['duration'] * 100)
for key in ['cards', 'words', 'median_card_frames', 'line_centre_y_px', 'cap_top_px', 'baseline_px', 'descender_px', 'cap_height_px',
            'xheight_px', 'centre_x_px', 'med_w_px', 'max_w_px']:
    P['cap_' + key] = mmm(key, lambda S, k: S['captions'][k])
P['cap_words_per_s'] = mmm(None, lambda S, k: S['captions']['words'] / S['duration'])
P['cap_cards_per_s'] = mmm(None, lambda S, k: S['captions']['cards'] / S['duration'])
P['cap_one_word_pct'] = mmm(None, lambda S, k: S['captions']['one_word_cards'] / S['captions']['cards'] * 100)
P['cap_frames_pct'] = mmm(None, lambda S, k: S['captions']['frames_with_caption'] / S['frames'] * 100)
# revisits
rev = {}
for r in KEYS:
    A = json.load(open(f'{r}/analysis.json'))
    seq = []
    for a, b, l in A['loc_spans']:
        if not seq or seq[-1] != l: seq.append(l)
    rev[r] = dict(sequence=seq, revisited=len([l for l in set(seq) if seq.count(l) > 1]), visits=len(seq))
P['locations_revisited'] = dict(values={r: rev[r]['revisited'] for r in KEYS}, min=min(v['revisited'] for v in rev.values()),
                                median=float(np.median([v['revisited'] for v in rev.values()])), max=max(v['revisited'] for v in rev.values()))
D = dict(
    shot_secs=q(shots.secs), shot_count=len(shots),
    first_shot_secs={r: float(shots[shots.ref == r].secs.iloc[0]) for r in KEYS},
    last_shot_secs={r: float(shots[shots.ref == r].secs.iloc[-1]) for r in KEYS},
    first_sizes={r: shots[shots.ref == r].sizes.iloc[0] for r in KEYS},
    last_sizes={r: shots[shots.ref == r].sizes.iloc[-1] for r in KEYS},
    transitions=shots[shots.transition_in != 'Start'].transition_in.value_counts().to_dict(),
    dissolve_frames=q([x for x in shots[shots.transition_in.str.startswith('Dissolve')].transition_frames.dropna()]),
    dissolve_frames_all=sorted(int(x) for x in shots[shots.transition_in.str.startswith('Dissolve')].transition_frames.dropna()),
    hold_frames=q(holds.frames), hold_by_size={z: q(g.frames, (25, 50, 75)) for z, g in holds.groupby('size')},
    shot_luma=q(shots.luma_mean), shot_sat=q(shots.sat), shot_colf=q(shots.colourfulness), shot_b=q(shots.b),
    card_frames=q(cards.frames), card_words=cards.words.value_counts().sort_index().to_dict(),
    card_frames_by_words={int(w): q(g.frames, (25, 50, 75)) for w, g in cards.groupby('words')},
    rev=rev,
)
# size-transition pairs (what follows what)
pairs = []
for r in KEYS:
    s = pf[pf.ref == r].shot_size.values
    for i in range(1, len(s)):
        if s[i] != s[i - 1]: pairs.append(f'{s[i - 1]}→{s[i]}')
D['size_pairs'] = pd.Series(pairs).value_counts().head(12).to_dict()
order = ['EWS', 'WS', 'FS', 'MS', 'MCU', 'CU', 'INS']
steps = [abs(order.index(p.split('→')[1]) - order.index(p.split('→')[0])) for p in pairs if p.split('→')[0] in order[:6] and p.split('→')[1] in order[:6]]
D['size_step_sizes'] = pd.Series(steps).value_counts().sort_index().to_dict()
# normalised-time profiles (tenths of runtime)
pf['dec'] = np.minimum((pf.tn * 10).astype(int), 9)
prof = pf.groupby(['ref', 'dec']).agg(luma=('luma_mean', 'mean'), sat=('sat_mean', 'mean'), b=('b', 'mean')).reset_index()
prof['luma'] /= 2.55
D['profile'] = {r: prof[prof.ref == r][['luma', 'sat', 'b']].round(2).to_dict('list') for r in KEYS}
json.dump(dict(P=P, D=D), open('params.json', 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
for k, v in P.items():
    print(f"{k:28s} " + ' '.join(f"{r}={v['values'][r]:.2f}" if isinstance(v['values'][r], (int, float)) else f"{r}={v['values'][r]}" for r in KEYS)
          + f"  | min {v['min']:.2f} med {v['median']:.2f} max {v['max']:.2f}")
print(json.dumps({k: v for k, v in D.items() if k not in ('profile',)}, indent=1, default=str))
print(json.dumps(D['profile'], default=str))
