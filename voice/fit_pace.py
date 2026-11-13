"""fit_pace.py: bring an ElevenLabs take to the reference pace (3.75 words/s) without changing pitch.
1) long pauses (> 0.22 s of silence) are shortened to 0.16 s; 2) the rest is a gentle atempo.
Word times in the timing JSON are remapped through the same edits. Run in the project folder, after take.mjs:
    python3 voice/fit_pace.py [target_wps]     (the original take is kept in voice/raw/)"""
import json, os, shutil, subprocess, sys, numpy as np
if not os.path.exists('voice/raw/voice.mp3'):          # first run: keep the original take in voice/raw/
    os.makedirs('voice/raw', exist_ok=True)
    for f in ('voice.mp3', 'voice-timing.json'): shutil.move(os.path.join('voice', f), os.path.join('voice/raw', f))
SR = 44100; TARGET = float(sys.argv[1]) if len(sys.argv) > 1 else 3.75
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', 'voice/raw/voice.mp3', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
a = np.frombuffer(raw, np.float32).copy()
hop = SR // 100; n = len(a) // hop
env = np.sqrt(np.array([np.mean(a[i * hop:(i + 1) * hop] ** 2) for i in range(n)]))
thr = max(env.max() * 0.02, np.percentile(env, 20) * 1.5)
sil = env < thr
keep = np.ones(n, bool); runs = []; i = 0
while i < n:
    if sil[i]:
        j = i
        while j < n and sil[j]: j += 1
        if (j - i) > 22 and i > 5:                       # > 0.22 s pause (not the lead-in)
            cut0 = i + 8; cut1 = j - 8                     # keep 80 ms each side = 0.16 s
            keep[cut0:cut1] = False; runs.append((cut0 / 100, cut1 / 100))
        i = j
    else: i += 1
# time map old -> trimmed
def tmap(t):
    return t - sum(min(max(t - s, 0), e - s) for s, e in runs)
segs = []; i = 0
while i < n:
    if keep[i]:
        j = i
        while j < n and keep[j]: j += 1
        segs.append(a[i * hop:j * hop]); i = j
    else: i += 1
b = np.concatenate(segs + [a[n * hop:]])
T = json.load(open('voice/raw/voice-timing.json'))
nw = sum(len(l['words']) for l in T['lines'])
last = tmap(T['lines'][-1]['words'][-1]['end'])
first = tmap(T['lines'][0]['words'][0]['start'])
tempo = max(1.0, (nw / TARGET) and (last - first) / (nw / TARGET))
open('/tmp/trim.f32', 'wb').write(b.astype(np.float32).tobytes())
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '/tmp/trim.f32',
                '-af', f'atempo={tempo:.4f}', '-c:a', 'libmp3lame', '-b:a', '160k', 'voice/voice.mp3'], check=True)
for l in T['lines']:
    for w in l['words']:
        w['start'] = round(tmap(w['start']) / tempo, 3); w['end'] = round(tmap(w['end']) / tempo, 3)
    l['start'] = l['words'][0]['start']; l['end'] = l['words'][-1]['end']
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', 'voice/voice.mp3'], capture_output=True, text=True).stdout)
T['duration'] = round(T['lines'][-1]['end'], 3); T['fit'] = dict(pauses_cut=len(runs), cut_s=round(sum(e - s for s, e in runs), 2), atempo=round(tempo, 4))
json.dump(T, open('voice/voice-timing.json', 'w'), indent=1)
span = T['lines'][-1]['end'] - T['lines'][0]['start']
print(f'pauses cut {len(runs)} ({T["fit"]["cut_s"]} s), atempo {tempo:.3f}, audio {dur:.2f} s, narration {span:.2f} s, {nw / span:.2f} words/s')
