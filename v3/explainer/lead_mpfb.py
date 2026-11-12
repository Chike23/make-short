"""lead_mpfb.py: the lead, built from libraries instead of by hand (house rule: library first).

Body, eyes, brows, lashes, teeth, hair, clothes and skin come from MPFB2 (MakeHuman for Blender) and its CC0 asset
packs. The rig is MPFB's Mixamo rig, so Mixamo clips play on her after retargeting. Facial expressions are the
ARKit face units from the `faceunits01` pack, as shape keys `!ex-<unit>` that can be keyframed.

Needs in Blender: the MPFB extension, and the packs makehuman_system_assets, shirts01, pants01, shoes01, faceunits01
(install with bpy.ops.mpfb.load_pack(filepath=...)). See references/route-explainer.md, "House rules".

    from lead_mpfb import build_lead, express, blinks
    rig, body = build_lead()                 # LEAD below; pass your own dict for another character
    express(body, 'shocked', 120)            # ease into an expression around frame 120
"""
import bpy
from bl_ext.user_default.mpfb.services.humanservice import HumanService
from bl_ext.user_default.mpfb.services.assetservice import AssetService
from bl_ext.user_default.mpfb.services.targetservice import TargetService
from bl_ext.user_default.mpfb.services.faceservice import FaceService

# The anatomy-explainer lead: a woman around 60, grey bob, teal tee, dark trousers, light trainers.
LEAD = {
    'name': 'lead',
    'macro': {'gender': 0.0, 'age': 0.78, 'muscle': 0.42, 'weight': 0.62, 'height': 0.6, 'proportions': 0.55,
              'race': {'asian': 0.05, 'caucasian': 0.85, 'african': 0.10}},
    'skin': 'Middleage caucasian female',
    'parts': [('eyes', 'High-poly', 'Eyes'), ('eyebrows', 'Eyebrow001', 'Eyebrows'), ('eyelashes', 'Eyelashes02', 'Eyelashes'),
              ('teeth', 'Teeth base', 'Teeth'), ('tongue', 'Tongue01', 'Tongue'), ('hair', 'Short02', 'Hair')],
    'clothes': [('Toigo basic tucked t-shirt', '#2e8b88'), ('Toigo wool pants', '#34343f'), ('Shoes01', None)],
    'hair_rgb': '#b9b4b0',
    'rig': 'mixamo',
}

# Expressions as ARKit face-unit weights (0-1). Add more as the stories need them.
EXPRESSIONS = {
    'neutral':    {},
    'smile':      {'mouthSmileLeft': 0.6, 'mouthSmileRight': 0.6, 'cheekSquintLeft': 0.3, 'cheekSquintRight': 0.3},
    'big_smile':  {'mouthSmileLeft': 0.9, 'mouthSmileRight': 0.9, 'cheekSquintLeft': 0.6, 'cheekSquintRight': 0.6,
                   'jawOpen': 0.2, 'browInnerUp': 0.2},
    'shocked':    {'jawOpen': 0.45, 'eyeWideLeft': 0.8, 'eyeWideRight': 0.8, 'browInnerUp': 0.8,
                   'browOuterUpLeft': 0.7, 'browOuterUpRight': 0.7, 'mouthFunnel': 0.3},
    'worried':    {'browInnerUp': 0.8, 'browDownLeft': 0.2, 'browDownRight': 0.2, 'mouthFrownLeft': 0.5,
                   'mouthFrownRight': 0.5, 'mouthPressLeft': 0.3, 'mouthPressRight': 0.3},
    'determined': {'browDownLeft': 0.6, 'browDownRight': 0.6, 'mouthPressLeft': 0.5, 'mouthPressRight': 0.5,
                   'jawForward': 0.2, 'noseSneerLeft': 0.15, 'noseSneerRight': 0.15},
    'effort':     {'browDownLeft': 0.7, 'browDownRight': 0.7, 'eyeSquintLeft': 0.6, 'eyeSquintRight': 0.6,
                   'mouthStretchLeft': 0.5, 'mouthStretchRight': 0.5, 'jawOpen': 0.1},
    'proud':      {'mouthSmileLeft': 0.7, 'mouthSmileRight': 0.7, 'browOuterUpLeft': 0.3, 'browOuterUpRight': 0.3,
                   'jawForward': 0.1, 'cheekSquintLeft': 0.3, 'cheekSquintRight': 0.3},
}


def _asset(kind, label):
    return AssetService.get_asset_list(kind)[label]['full_path']


def _flat(name, hexrgb, rough=0.7):
    h = hexrgb.lstrip('#'); rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    rgb = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value = (*rgb, 1); p.inputs['Roughness'].default_value = rough
    return m


def recolor(obj, hexrgb):
    """Swap a library asset's material for a flat colour (keeps the asset's shape and rigging)."""
    m = _flat(f'{obj.name}_mat', hexrgb)
    obj.data.materials.clear(); obj.data.materials.append(m)


def build_lead(spec=LEAD):
    macro = TargetService.get_default_macro_info_dict(); macro.update(spec['macro'])
    body = HumanService.create_human(macro_detail_dict=macro, scale=0.1, feet_on_ground=True)
    body.name = f"{spec['name']}_body"
    rig = HumanService.add_builtin_rig(body, spec['rig']); rig.name = f"{spec['name']}_rig"
    for kind, label, atype in spec['parts']:
        o = HumanService.add_mhclo_asset(_asset(kind, label), body, asset_type=atype, subdiv_levels=0)
        if kind == 'hair' and spec.get('hair_rgb'): recolor(o, spec['hair_rgb'])
    for label, rgb in spec['clothes']:
        o = HumanService.add_mhclo_asset(_asset('clothes', label), body, asset_type='Clothes', subdiv_levels=0)
        if rgb: recolor(o, rgb)
    HumanService.set_character_skin(_asset('skins', spec['skin']), body, skin_type='MAKESKIN')
    units = sorted({u for e in EXPRESSIONS.values() for u in e} | {'eyeBlinkLeft', 'eyeBlinkRight'})
    FaceService.set_expression(body, {u: 0.0 for u in units})      # loads every face unit used here as a shape key
    return rig, body


def _key(body, unit, value, frame):
    kb = body.data.shape_keys.key_blocks.get(f'!ex-{unit}')
    if kb is None: return
    kb.value = value; kb.keyframe_insert('value', frame=frame)


def express(body, name, frame, ramp=5, hold=None):
    """Ease every expression unit from its current keyed value into `name` over `ramp` frames ending at `frame`."""
    target = EXPRESSIONS[name]
    units = {u for e in EXPRESSIONS.values() for u in e}
    for u in units:
        kb = body.data.shape_keys.key_blocks.get(f'!ex-{u}')
        if kb is None: continue
        bpy.context.scene.frame_set(frame - ramp)
        _key(body, u, kb.value, frame - ramp)
        _key(body, u, target.get(u, 0.0), frame)
        if hold: _key(body, u, target.get(u, 0.0), frame + hold)


def blinks(body, frames, dur=4):
    for f in frames:
        for u in ('eyeBlinkLeft', 'eyeBlinkRight'):
            _key(body, u, 0.0, f); _key(body, u, 1.0, f + dur // 2); _key(body, u, 0.0, f + dur)
