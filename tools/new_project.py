"""new_project.py: make a project folder for a new Short (or a copy of the example to learn from).

    python3 SKILL/tools/new_project.py <slug>                         -> ~/shorts/<slug>
    python3 SKILL/tools/new_project.py <slug> --example               -> a copy of "June and the jar"
    python3 SKILL/tools/new_project.py <slug> --style <name>          -> uses SKILL/styles/<name> (a saved style)
    options: --root DIR (default ~/shorts; keep it out of iCloud Drive and OneDrive)
The project is self-contained: kit/ (the Blender code), tools/, voice/ (voice, captions, sound effects), film.py,
story.md, brief.json, progress.md, and empty plan/ checks/ preview/ render/ out/ critic/ folders.
"""
import json, os, shutil, sys

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
a = sys.argv[1:]
if not a or a[0].startswith('-'): sys.exit(__doc__)
slug = a[0]; root = os.path.expanduser('~/shorts'); example = '--example' in a; style = None
if '--root' in a: root = os.path.expanduser(a[a.index('--root') + 1])
if '--style' in a: style = a[a.index('--style') + 1]
P = os.path.join(root, slug)
if os.path.exists(os.path.join(P, 'film.py')): sys.exit(f'{P} already has a film.py: pick another name, or carry on with it.')
os.makedirs(P, exist_ok=True)
ign = shutil.ignore_patterns('__pycache__', '*.pyc')
for d in ('kit', 'tools'):
    shutil.copytree(os.path.join(SKILL, d), os.path.join(P, d), dirs_exist_ok=True, ignore=ign)
shutil.copytree(os.path.join(SKILL, 'voice'), os.path.join(P, 'voice'), dirs_exist_ok=True, ignore=ign)
for d in ('plan', 'checks', 'preview', 'render', 'out', 'critic', 'style'): os.makedirs(os.path.join(P, d), exist_ok=True)
if style and style != 'default':
    shutil.copytree(os.path.join(SKILL, 'styles', style), os.path.join(P, 'style'), dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('frames', 'sheet_*.png'))
if example:
    ex = os.path.join(SKILL, 'example', 'june-and-the-jar')
    for f in ('film.py', 'story.md', 'grade_fix.json'): shutil.copy(os.path.join(ex, f), P)
    for f in os.listdir(os.path.join(ex, 'voice')): shutil.copy(os.path.join(ex, 'voice', f), os.path.join(P, 'voice'))
else:
    shutil.copy(os.path.join(SKILL, 'template', 'film.py'), P)
    shutil.copy(os.path.join(SKILL, 'template', 'story.md'), P)
    shutil.copy(os.path.join(SKILL, 'template', 'cues.json'), os.path.join(P, 'voice', 'cues.json'))
brief = os.path.join(P, 'brief.json')
if not os.path.exists(brief):
    json.dump({'slug': slug, 'idea': '', 'style': style or 'default', 'length_s': 60, 'story_approved': '',
               'script_approved': '', 'voice': '', 'music': 'starter', 'ending': '', 'plan_approved': '',
               'preview_approved': '', 'final_file': ''}, open(brief, 'w'), indent=1)
prog = os.path.join(P, 'progress.md')
if not os.path.exists(prog):
    open(prog, 'w').write(f'# {slug}\n- [ ] 1 start  - [ ] 2 idea  - [ ] 3 style  - [ ] 4 story  - [ ] 5 script  - [ ] 6 voice\n'
                          '- [ ] 7 plan  - [ ] 8 build + checks  - [ ] 9 preview + judge  - [ ] 10 fixes  - [ ] 11 final render\n'
                          '- [ ] 12 verify + quick fixes  - [ ] 13 final check  - [ ] 14 publish\nStopped at: 1 start\n')
print(P)
