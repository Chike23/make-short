import subprocess, json, re, sys, os, csv
D = os.path.dirname(os.path.abspath(__file__)); G = D + '/gate'
shots = json.load(open(D + '/shots.json'))
proj = {}
if os.path.exists(G + '/proj.txt'):
    for l in open(G + '/proj.txt'):
        m = re.match(r'PROJ (s\d+) (.*)', l)
        if m: proj[m.group(1)] = eval(m.group(2))
# YAVG low/high, SATAVG low/high per mood = p10..p90 of 738 reference frames measured exactly like this
# (signalstats on 1080x1920 RGB stills), from references/reference-style.md section 5. Night is NOT dark (median 85)
# and is the most saturated mood (blue); interiors are dimmer and less saturated than day. Old values were 1 fps guesses.
BAND = {'day': (99, 146, 22, 44), 'dusk': (114, 153, 18, 35), 'interior': (67, 139, 19, 35), 'night': (69, 118, 29, 61)}
ALIAS = {'night_in': 'night', 'night_card': 'night', 'night_warm': 'night', 'day_in': 'day', 'day_hot': 'day',
         'interior_in': 'interior', 'interior_lid': 'interior'}
band = lambda m: BAND.get(m) or BAND.get(ALIAS.get(m, ''), BAND['day'])
rows = []; npass = 0
for s in shots:
    f = f"{G}/{s['id']}.png"
    if not os.path.exists(f): continue  # partial run: gate.sh s01 s05
    o = subprocess.run(['ffmpeg', '-i', f, '-vf', 'signalstats,metadata=print', '-f', 'null', '-'], capture_output=True, text=True).stderr
    v = {k: float(re.search(k + r'=([\d.]+)', o).group(1)) for k in ('SATAVG', 'YAVG', 'YLOW', 'YHIGH')}
    ylo, yhi, slo, shi = band(s['mood'])
    why = []
    tol = 8 if s['size'] in ('MACRO',) else 5
    if not (ylo - tol <= v['YAVG'] <= yhi + tol * 2): why.append('Y')
    if not (slo - 4 <= v['SATAVG'] <= shi + 6): why.append('SAT')
    if v['YHIGH'] > 232: why.append('blown')
    for (t, x0, x1, y0, y1) in proj.get(s['id'], []):
        if t.startswith('p:') or t in ('tree', 'crate', 'fire', 'tent_table'): continue
        if x0 < 0.02 or x1 > 0.98 or y0 < 0.1 or y1 > 0.97: why.append('crop:' + t)
    rows.append([s['id'], s['mood'], s['size'], v['SATAVG'], v['YAVG'], v['YLOW'], v['YHIGH'], 'PASS' if not why else 'FAIL ' + ','.join(why)])
    npass += not why
with open(G + '/gate.csv', 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['shot', 'mood', 'size', 'SATAVG', 'YAVG', 'YLOW', 'YHIGH', 'result']); w.writerows(rows)
for r in rows:
    if r[-1] != 'PASS': print(r[0], r[1], r[2], 'S%.0f Y%.0f hi%.0f' % (r[3], r[4], r[6]), r[-1])
print('PASS', npass, '/', len(rows))
