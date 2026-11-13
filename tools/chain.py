"""chain.py: build, preview or render every shot of the film in the background, in parallel chains.

Runs on the computer with Blender (macOS: /Applications/Blender.app; else set BLENDER=/path/to/blender).
    python3 tools/chain.py check             build every shot + run the checks only (no pictures): about 1 min a shot
    python3 tools/chain.py stills            + 3 preview stills per shot (start, middle, end) -> stills/stills_S01/ ...
    python3 tools/chain.py preview           + a 360x640 preview clip of every shot -> preview/S01_0001-0124.mp4 ...
    python3 tools/chain.py render            + the final 720x1280 clips              -> render/...
    python3 tools/chain.py render S06 S08    only these shots
    options: --chains 2 (parallel Blender processes; 2 suits a 16 GB Mac), --out DIR
It snapshots film.py, kit/ and the voice timing into OUT/_code first, so you can keep editing while it runs
(editing a file a running chain reads broke a render once). Progress: python3 tools/status.py OUT
Each chain logs to OUT/chainN.log: BUILT, CHECK, STILLS, RENDERED and EXIT lines per shot, ALL_DONE at the end.
"""
import json, os, shutil, subprocess, sys, time

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def blender():
    for b in (os.environ.get('BLENDER'), '/Applications/Blender.app/Contents/MacOS/Blender', shutil.which('blender'),
              shutil.which('Blender')):
        if b and os.path.exists(b): return b
    sys.exit('chain.py: Blender not found. Install Blender 5 or set BLENDER=/path/to/blender.')


def plan(bl):
    fp = os.path.join(P, 'plan', 'film.json')
    if not os.path.exists(fp) or os.path.getmtime(fp) < os.path.getmtime(os.path.join(P, 'film.py')):
        subprocess.run([bl, '-b', '--factory-startup', '--python', os.path.join(P, 'film.py'), '--', 'plan'],
                       cwd=P, capture_output=True, text=True, env=dict(os.environ, MAKESHORT_PROJECT=P))
    if not os.path.exists(fp): sys.exit('chain.py: film.py -- plan failed; run it by hand to see the error.')
    return json.load(open(fp))


def main():
    a = sys.argv[1:]
    if not a or a[0] not in ('check', 'stills', 'preview', 'render'): sys.exit(__doc__)
    mode = a[0]; n = 2; out = None; ids = []
    i = 1
    while i < len(a):
        if a[i] == '--chains': n = int(a[i + 1]); i += 2
        elif a[i] == '--out': out = os.path.abspath(a[i + 1]); i += 2
        else: ids.append(a[i].upper()); i += 1
    out = out or os.path.join(P, {'check': 'checks_run', 'stills': 'stills', 'preview': 'preview', 'render': 'render'}[mode])
    bl = blender(); film = plan(bl)
    shots = [s for s in film['shots'] if not ids or s['id'] in ids]
    os.makedirs(out, exist_ok=True)
    code = os.path.join(out, '_code', time.strftime('%Y%m%d-%H%M%S'))           # a frozen copy of the code
    shutil.copytree(os.path.join(P, 'kit'), os.path.join(code, 'kit'), ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copy(os.path.join(P, 'film.py'), code)
    os.makedirs(os.path.join(code, 'voice'), exist_ok=True)
    shutil.copy(os.path.join(P, 'voice', 'voice-timing.json'), os.path.join(code, 'voice'))
    chains = [[] for _ in range(n)]; load = [0] * n                              # longest shots first, to the lightest chain
    for s in sorted(shots, key=lambda s: -(s['f1'] - s['f0'])):
        k = load.index(min(load)); chains[k].append(s['id']); load[k] += s['f1'] - s['f0'] + 1
    flag = {'check': [], 'stills': ['preview'], 'preview': ['preview', 'render'], 'render': ['render']}[mode]
    byid = {s['id']: s for s in shots}
    for k, ch in enumerate(chains):
        if not ch: continue
        log = os.path.join(out, f'chain{k + 1}.log'); sh = os.path.join(out, f'chain{k + 1}.sh')
        lines = [f'export MAKESHORT_PROJECT="{P}"', f'echo "START {" ".join(ch)}" > "{log}"']
        for sid in ch:
            fr = [] if mode != 'stills' else [byid[sid]['f0'] + 10, (byid[sid]['f0'] + byid[sid]['f1']) // 2, byid[sid]['f1'] - 6]
            lines.append(f'"{bl}" -b --python "{code}/film.py" -- {sid} "{out}" {" ".join(flag + [str(x) for x in fr])} >> "{log}" 2>&1; '
                         f'echo "EXIT {sid} $?" >> "{log}"; rm -f "{out}/job_{sid}.blend" "{out}/job_{sid}.blend1"')
        lines.append(f'echo ALL_DONE >> "{log}"')
        open(sh, 'w').write('\n'.join(lines) + '\n')
        subprocess.Popen(['/bin/sh', sh], cwd=P, start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f'chain {k + 1}: {" ".join(ch)} ({load[k]} frames)')
    sec = {'check': 1.1, 'stills': 1.2, 'preview': 1.8, 'render': 3.5}[mode]                   # rough seconds a frame on an M1, 2 chains
    eta = max(load) * sec + 30 * max(len(c) for c in chains)
    print(f'log: {out}/chainN.log   about {eta / 60:.0f} min (done around {time.strftime("%H:%M", time.localtime(time.time() + eta))})')


if __name__ == '__main__':
    main()
