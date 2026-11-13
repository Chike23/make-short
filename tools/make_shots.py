"""make_shots.py: the edit (shots.json, for audit.py) from the rendered clips and their camera size keys.
    python3 tools/make_shots.py [render]      -> shots.json in the project folder
Places and moods come from plan/film.json (written by film.py -- plan)."""
import json, os, re, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = sys.argv[1] if len(sys.argv) > 1 else 'render'
d = d if os.path.isabs(d) else os.path.join(P, d)
film = {s['id']: s for s in json.load(open(os.path.join(P, 'plan', 'film.json')))['shots']}
clips = sorted(f for f in os.listdir(d) if re.match(r'S\d\d_\d{4}-\d{4}\.mp4$', f))
out = []
for i, f in enumerate(clips):
    sid = f[:3]; a, b = map(int, re.findall(r'(\d{4})-(\d{4})', f)[0])
    f_in = a - 1                                                 # 0-based first frame of the shot
    f_out = int(re.findall(r'(\d{4})-(\d{4})', clips[i + 1])[0][0]) - 1 if i + 1 < len(clips) else b
    kp = os.path.join(d, f'{sid}_camkeys.json')
    keys = [k for k in (json.load(open(kp)) if os.path.exists(kp) else []) if k.get('size')]
    # a size counts from the middle of the camera move into it
    cam = [{'f': max(f_in, k['f'] - 1 - k.get('move', 0) // 2), 'size': k['size']} for k in keys if k['f'] - 1 < f_out]
    first = [k for k in cam if k['f'] <= f_in]
    cam = ([{'f': f_in, 'size': first[-1]['size']}] if first else []) + [k for k in cam if k['f'] > f_in]
    s = film.get(sid, {})
    out.append({'id': sid, 'f_in': f_in, 'f_out': f_out, 'transition_in': 'cut' if i == 0 else 'dissolve',
                'size': cam[0]['size'] if cam else 'FS', 'set': s.get('loc', ''), 'loc': s.get('loc', ''),
                'mood': s.get('mood', 'interior'), 'camera': cam})
json.dump(out, open(os.path.join(P, 'shots.json'), 'w'), indent=1)
os.makedirs(os.path.join(d, 'pre_dissolve'), exist_ok=True)      # tells audit.py the dissolves are real crossfades
print(f'shots.json: {len(out)} shots, {sum(len(s["camera"]) for s in out)} camera size keys, ends at frame {out[-1]["f_out"]}')
