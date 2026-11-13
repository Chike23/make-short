"""status.py: how far the render chains are.   python3 tools/status.py [render|preview|checks_run|DIR]
One line per chain: shots done, the shot in progress and its last frame, errors; then every CHECK line."""
import glob, os, re, sys

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = sys.argv[1] if len(sys.argv) > 1 else 'render'
d = d if os.path.isabs(d) else os.path.join(P, d)
logs = sorted(glob.glob(os.path.join(d, 'chain*.log')))
if not logs: sys.exit(f'no chain logs in {d}')
checks, all_done = [], True
for lg in logs:
    t = open(lg, errors='replace').read()
    done = re.findall(r'^EXIT (S\d+) (\d+)', t, re.M); built = re.findall(r'^BUILT (S\d+)', t, re.M)
    cur = built[-1] if built and (not done or done[-1][0] != built[-1]) else None
    fr = re.findall(r'Append frame (\d+)|Video append frame (\d+)', t)
    last = next((x for x in (fr[-1] if fr else ()) if x), '')
    errs = [l for l in t.splitlines() if 'Traceback' in l or l.startswith(('Error', 'KeyError', 'NameError'))]
    bad = [s for s, c in done if c != '0']
    fin = 'ALL_DONE' in t; all_done &= fin
    print(f"{os.path.basename(lg)}: done {' '.join(s for s, _ in done) or '-'}"
          + (f" | now {cur} frame {last}" if cur and not fin else '') + (' | ALL_DONE' if fin else '')
          + (f" | FAILED {' '.join(bad)}" if bad else '') + (f" | {len(errs)} error lines" if errs else ''))
    checks += [l for l in t.splitlines() if l.startswith('CHECK')]
for c in checks: print(' ', c)
print('ALL_DONE' if all_done else 'running')
