"""style.py: the LOOK layer. A style card changes how characters and worlds look; it never touches the camera, the
edit, the shot sizes, the captions or the pacing (those stay on references/spec.md).

shotkit loads P/style/style.json at start-up (if there is one) and applies it before any shot is built:

{
 "name": "default",
 "character": {
   "builder": "character.py",                  optional: a new cut-out builder in P/style/ (same rig as lady2d)
   "palettes": {"PAL": {"skin": "#eab896", ...}, "SON": {...}, "MY_NEW": {...}},   lady2d palettes to change/add
   "shading": {"shadow": [0.58, 0.55, 0.8], "mid": [...], "lit": [...], "steps": [...], "tint": 0.35, "self_em": 0.14},
   "head_scale": 1.0,                           bigger heads for a chibi style (scales the head joint)
   "body_scale": [1.0, 1.0]                     width and height of the whole figure
 },
 "world": {
   "remap": {"#ecd6b2": "#f3e2c4", ...},        every set colour (walls, floors, props) swapped hex for hex
   "rick_look": {"world_ink": false, "depth_ink": 1.0, "smooth": true},   outlines on sets, depth lines, smooth light
   "kuwahara": 1                                painterly filter size (0 = off)
 },
 "grade": {
   "moods": {"kitchen": {"sat": 1.1, "gain": [0.9, 0.8, 0.75]}, ...},     changes to look.MOODS entries
   "rick_mood": {"gain_mult": [0.97, 0.9, 0.9], "sat_mult": 1.1, "lift": [1.0, 0.98, 1.05]}
 },
 "bands": {"interior": [67, 88, 139, 19, 25, 35], ...}   colour targets for color_check / audit (critic/targets.json)
}
"""
import json, os, sys, importlib.util

CARD = {}


def _hex(h): return h.lower() if isinstance(h, str) else h


def apply(card, folder):
    import flat2d as F, lady2d as L, world3d as W, look
    global CARD
    CARD = card
    ch = card.get('character', {})
    for name, pal in ch.get('palettes', {}).items():
        base = getattr(L, name, None)
        setattr(L, name, dict(base or L.PAL, **pal))
    if 'shading' in ch: F.LIT.update({k: tuple(v) if isinstance(v, list) else v for k, v in ch['shading'].items()})
    if ch.get('builder'):
        spec = importlib.util.spec_from_file_location('style_character', os.path.join(folder, ch['builder']))
        mod = importlib.util.module_from_spec(spec); sys.modules['style_character'] = mod; spec.loader.exec_module(mod)
        L.build = mod.build
        for fn in ('face', 'pose', 'look', 'blink', 'xray', 'hold', 'blob_shadow', 'face_camera', 'walk', 'jog', 'travel', 'cycle'):
            if hasattr(mod, fn): setattr(L, fn, getattr(mod, fn))
    hs, bs = ch.get('head_scale', 1.0), ch.get('body_scale', [1.0, 1.0])
    if hs != 1.0 or bs != [1.0, 1.0]:
        _build = L.build
        def build(*a, **k):
            R = _build(*a, **k)
            R['j']['head'].scale = (hs, hs, hs)
            R['j']['hips'].scale = (bs[0], 1.0, bs[1])
            return R
        L.build = build
    wo = card.get('world', {})
    remap = {_hex(k): _hex(v) for k, v in wo.get('remap', {}).items()}
    if remap:
        _toon, _emit = W.toon, W.emit
        W.toon = lambda name, hexrgb, tex=None, ink=False: _toon(name, remap.get(_hex(hexrgb), hexrgb), tex, ink)
        W.emit = lambda name, hexrgb, strength=1.0: _emit(name, remap.get(_hex(hexrgb), hexrgb), strength)
    if 'rick_look' in wo:
        _rl = W.rick_look
        W.rick_look = lambda keep=('lady',), **k: _rl(keep=keep, **dict(k, **wo['rick_look']))
    if 'kuwahara' in wo:
        _kw = W.set_kuwahara
        W.set_kuwahara = lambda size, frames: _kw(wo['kuwahara'], frames)
    gr = card.get('grade', {})
    for m, ch_ in gr.get('moods', {}).items():
        if m in look.MOODS: look.MOODS[m].update({k: tuple(v) if isinstance(v, list) else v for k, v in ch_.items()})
    return card


def load(project):
    """Apply P/style/style.json when it exists. Returns the card ({} for the default look)."""
    fp = os.path.join(project, 'style', 'style.json')
    if not os.path.exists(fp): return {}
    return apply(json.load(open(fp)), os.path.dirname(fp))
