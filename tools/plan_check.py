"""plan_check.py: the whole film against the spec BEFORE any picture is rendered (seconds, not hours).

Reads plan/film.json and checks/S??.json (written when the shots are built: tools/chain.py check) and compares the
edit, the shot-size mix, the camera motion and the shot checks with SKILL/references/spec.md.
    python3 tools/plan_check.py            -> PASS / WARN / FAIL lines, and checks/plan_check.md
FAIL = fix before rendering. WARN = look at it; a deliberate choice is fine. House rules (from the user):
  - wide shots follow the reference mix: EWS + WS at least 25% of screen time, MS at most 20%
  - short camera stops are fine as long as most of the film moves like the reference
  - every text object has a black outline
"""
import glob, json, os, statistics, sys

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 30
SIZES = ('EWS', 'WS', 'FS', 'MS', 'MCU', 'CU', 'INS')
TARGET = {'EWS': (19.0, 6.0, 36.9), 'WS': (16.9, 12.7, 24.7), 'FS': (26.7, 22.7, 31.1), 'MS': (13.0, 10.6, 16.9),
          'MCU': (8.3, 2.7, 20.2), 'CU': (5.2, 3.0, 9.7), 'INS': (11.0, 2.1, 19.6)}
film = json.load(open(os.path.join(P, 'plan', 'film.json')))
shots = film['shots']
rep = {s['id']: json.load(open(os.path.join(P, 'checks', f"{s['id']}.json")))
       for s in shots if os.path.exists(os.path.join(P, 'checks', f"{s['id']}.json"))}
rows = []
def row(level, what, val, target): rows.append((level, what, val, target))

# ---- edit
dur = (shots[-1]['f1'] - shots[0]['f0'] + 1) / FPS
lens = [(s['f1'] - s['f0'] + 1) / FPS for s in shots]
asl = dur / len(shots)
row('PASS' if 56 <= dur <= 65 else 'WARN', 'Length', f'{dur:.1f} s', '62 s (56-65)')
row('PASS' if 3.1 <= asl <= 5.1 else 'FAIL', 'Average shot', f'{asl:.2f} s ({len(shots)} shots)', '4.3 s (3.1-5.1)')
row('PASS' if max(lens) <= 8.6 else 'FAIL', 'Longest shot', f'{max(lens):.2f} s', '8.3 s, never over 8.6')
locs = [s['loc'] for s in shots]
nloc = len(set(locs)); changes = sum(a != b for a, b in zip(locs, locs[1:]))
row('PASS' if 7 <= nloc <= 13 else 'WARN', 'Places', f'{nloc} places, {changes} changes', '9 (7-13), 14 changes (6-15)')

# ---- shot sizes by screen time (a size counts from the middle of the move into it)
time_in = {k: 0 for k in SIZES}; nchange = 0; last = None
missing = [s['id'] for s in shots if s['id'] not in rep]
for s in shots:
    keys = [k for k in rep.get(s['id'], {}).get('sizes', []) if k.get('size')]
    if not keys: continue
    starts = [max(s['f0'], k['f'] - k.get('move', 0) // 2) for k in keys]
    starts[0] = s['f0']
    for i, k in enumerate(keys):
        a = max(s['f0'], starts[i]); b = min(s['f1'] + 1, starts[i + 1] if i + 1 < len(keys) else s['f1'] + 1)
        if b > a: time_in[k['size']] = time_in.get(k['size'], 0) + (b - a)
        if last is not None and k['size'] != last: nchange += 1
        last = k['size']
tot = sum(time_in.values()) or 1
share = {k: 100 * v / tot for k, v in time_in.items()}
for k in SIZES:
    t, lo, hi = TARGET[k]
    lvl = 'PASS' if lo <= share[k] <= hi else 'WARN'
    if k == 'MS' and share[k] > 20: lvl = 'FAIL'
    row(lvl, f'Screen time {k}', f'{share[k]:.1f}%', f'{t}% ({lo}-{hi})')
wide = share['EWS'] + share['WS']
row('PASS' if wide >= 25 else 'FAIL', 'Wides (EWS + WS)', f'{wide:.1f}%', '36% in the reference; at least 25% (house rule)')
cps = nchange / dur
row('PASS' if 0.51 <= cps <= 0.85 else 'WARN', 'Size changes per second', f'{cps:.2f}', '0.73 (0.51-0.78)')

# ---- camera motion (camera only; characters add their own motion in the real film)
per = []; whips = []; runs = []
for s in shots:
    mo = rep.get(s['id'], {}).get('motion') or {}
    pf = mo.get('per_frame', [])[: s['f1'] - s['f0'] + 1]
    per += pf; whips += mo.get('whip_frames', []); runs += [r for r in mo.get('still_runs', []) if r[0] <= s['f1']]
if per:
    med = statistics.median(per); still = 100 * sum(v < 0.5 for v in per) / len(per); fast = 100 * sum(v > 10 for v in per) / len(per)
    row('PASS' if 2.0 <= med <= 4.7 else 'WARN', 'Camera motion, median', f'{med:.2f} px/frame', '3.2 (2.9-4.7) incl. character motion; 2.0-4.7 camera only')
    row('PASS' if still <= 21 else 'WARN', 'Camera still frames', f'{still:.1f}%', '8% (4-21%); short stops are fine')
    row('PASS' if 12 <= fast <= 32 else 'WARN', 'Fast frames (> 10 px)', f'{fast:.1f}%', '20% (19-32%)')
    row('PASS' if not whips else 'FAIL', 'Whips (> 45 px/frame)', f'{len(whips)} frames {whips[:8]}', 'none: the reference never whips')
    longest = max((b - a + 1 for a, b in runs), default=0)
    row('PASS' if longest < 20 else 'WARN', 'Longest camera stop', f'{longest} frames', 'under 20 frames (0.7 s)')

# ---- shot checks
cam_probs = [(sid, k, v) for sid, r in rep.items() for k, v in r.get('camera', {}).items()]
hard = [c for c in cam_probs if c[1].startswith(('lens against', 'camera inside', 'blocked by'))]
row('PASS' if not hard else 'FAIL', 'Camera blocked or inside the set', f'{len(hard)}', 'none')
row('PASS' if not cam_probs else 'WARN', 'Framing warnings', f'{len(cam_probs)}', 'look at each one in the stills')
clips = [(sid, e) for sid, r in rep.items() for e in r.get('clipping', [])]
row('PASS' if not clips else 'FAIL', 'Characters through objects', f'{len(clips)}', 'none (or allow it in FILM["allow"])')
close = [(sid, n) for sid, r in rep.items() for n in r.get('camera_keys_too_close', [])]
row('PASS' if not close else 'WARN', 'Camera keys too close for a smooth move', f'{len(close)}', 'none: space the keys, or drop one')
outl = [(sid, n) for sid, r in rep.items() for n in r.get('outlines_missing', [])]
row('PASS' if not outl else 'FAIL', 'Text without a black outline', f'{len(outl)}', 'none (house rule)')
if missing: row('FAIL', 'Shots not built yet', ' '.join(missing), 'run tools/chain.py check')

# ---- report
md = ['# Plan check', '', '| | Check | This film | Target |', '|---|---|---|---|']
for r in rows:
    print(f'{r[0]:4}  {r[1]}: {r[2]}   [{r[3]}]'); md.append(f'| {r[0]} | {r[1]} | {r[2]} | {r[3]} |')
detail = []
for sid, k, v in cam_probs: detail.append(f"- {sid} camera: {k}, {v['frames']} frames ({v['from']}-{v['to']})")
for sid, e in clips:
    fx = e.get('fix'); tip = f"suggested fix: move {e['character']} {fx['metres']} m {fx['move']} (dx {fx['dx']}, dy {fx['dy']})" if fx else 'no simple move clears it: re-stage'
    detail.append(f"- {sid} clipping: {e['character']} through {e['object']}, frames {e['from']}-{e['to']} (worst {e['worst']}), parts {', '.join(e['parts'])}. {tip}")
for sid, n in outl: detail.append(f'- {sid} text without outline: {n}')
for sid, n in close: detail.append(f'- {sid} camera: {n}')
if detail:
    print('\n'.join(detail)); md += ['', '## Details', ''] + detail
os.makedirs(os.path.join(P, 'checks'), exist_ok=True)
open(os.path.join(P, 'checks', 'plan_check.md'), 'w').write('\n'.join(md) + '\n')
nfail = sum(r[0] == 'FAIL' for r in rows)
print(f'\n{nfail} FAIL, {sum(r[0] == "WARN" for r in rows)} WARN -> checks/plan_check.md')
sys.exit(1 if nfail else 0)
