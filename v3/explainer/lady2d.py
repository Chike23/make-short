"""lady2d.py: the anatomy-explainer lead as a flat 2D cut-out puppet (flat2d.py), front view.

A woman around 60: short grey hair, teal tee, dark trousers, light trainers. Swappable eyes (open, wide, closed,
happy) and mouths (smile, grin, O, frown, flat); brows and pupils move. Everything below the head has an X-ray layer
(navy body, bones, red muscles with glow), faded in with xray(). Screen-left arm = her right arm ("sl").

    R = build('lady')
    pose(R, 20, 28, {'arm_sl': (90, 100, 0), 'head': -6}, interp='BACK')
    face(R, 30, eyes='wide', mouth='O', brows='surprised')
"""
import bpy, math
import flat2d as F

PAL = dict(skin='#eab896', skin_sh='#d49a78', hair='#dedad5', hair_sh='#b9b2ac', top='#2fa39a', top_sh='#23867f',
           trousers='#3b3b4c', shoe='#f1ede6', eye='#ffffff', pupil='#2b2220', mouth='#6b2a2c', tongue='#e3746c',
           teeth='#ffffff', brow='#9a918a', blush='#f2958a', nose='#d99c7c',
           ghost='#1b2a50', bone='#f4efe4', muscle='#ff5468', glow='#ff6b7d')

SH, EL, WR = (0.2, 1.385), (0.2, 1.11), (0.2, 0.855)        # shoulder, elbow, wrist (x mirrored per side)
L1, L2 = SH[1] - EL[1], EL[1] - WR[1]


def _arc_pts(cx, cz, w, h, t, n=10):
    """A curved stroke (crescent): w wide, bowing by h (h>0 bows up), t thick."""
    top = [(cx - w / 2 + w * i / n, cz + h * math.sin(math.pi * i / n) + t / 2) for i in range(n + 1)]
    bot = [(cx + w / 2 - w * i / n, cz + h * math.sin(math.pi * (n - i) / n) - t / 2) for i in range(n + 1)]
    return top + bot


def build(name='lady', at=(0.0, 0.0), pal=PAL):
    P = pal; R = {'name': name, 'xray': [], 'muscles': [], 'halos': [], 'rings': []}
    J = R['j'] = {}
    root = J['root'] = F.joint(f'{name}_root', None, (0, 0)); root.location = (at[0], 0, at[1])
    hips = J['hips'] = F.joint(f'{name}_hips', root, (0, 0.93))
    torso = J['torso'] = F.joint(f'{name}_torso', hips, (0, 0.95))
    head = J['head'] = F.joint(f'{name}_head', torso, (0, 1.47))

    def ghost(o, parent, depth):                    # navy X-ray copy of a body shape, just in front of it
        g = F.copy_shape(o, o.name + '_x', P['ghost'], parent, depth, alpha=0.0)
        R['xray'].append(g); return g

    def xr(o):                                      # X-ray parts glow like a screen: flat, unlit
        o.color = (1, 1, 1, 0); R['xray'].append(o)
        if not o.name.endswith(('_halo_sl', '_halo_sr')): o.data.materials[0] = F.flat(o['hex'])
        return o

    # ---- legs and hips
    for s, sx in (('sl', -1), ('sr', 1)):
        th = J[f'thigh_{s}'] = F.joint(f'{name}_thigh_{s}', hips, (0.095 * sx, 0.93))
        kn = J[f'shin_{s}'] = F.joint(f'{name}_shin_{s}', th, (0.095 * sx, 0.5))
        a = F.limb(f'{name}_thigh_{s}', (0.095 * sx, 0.95), (0.095 * sx, 0.5), 0.17, 0.13, P['trousers'], th, 0.010)
        b = F.limb(f'{name}_shinp_{s}', (0.095 * sx, 0.52), (0.095 * sx, 0.1), 0.13, 0.11, P['trousers'], kn, 0.011)
        c = F.ellipse(f'{name}_shoe_{s}', 0.11 * sx, 0.05, 0.075, 0.045, P['shoe'], kn, 0.009)
        ghost(a, th, 0.0088); ghost(b, kn, 0.0098); ghost(c, kn, 0.0078)
        xr(F.limb(f'{name}_femur_{s}', (0.09 * sx, 0.9), (0.095 * sx, 0.53), 0.03, 0.026, P['bone'], th, 0.0076))
        xr(F.limb(f'{name}_tibia_{s}', (0.095 * sx, 0.48), (0.095 * sx, 0.12), 0.026, 0.022, P['bone'], kn, 0.0086))
        qj = J[f'quad_{s}'] = F.joint(f'{name}_quadj_{s}', th, (0.097 * sx, 0.72))
        R['muscles'].append(xr(F.ellipse(f'{name}_quad_{s}', 0.097 * sx, 0.72, 0.05, 0.15, P['muscle'], qj, 0.0072)))
    band = F.rrect(f'{name}_waist', -0.2, 0.86, 0.2, 0.97, 0.05, P['trousers'], hips, 0.009)
    ghost(band, hips, 0.0076)
    for sx in (-1, 1):
        xr(F.ellipse(f'{name}_pelvis_{sx}', 0.07 * sx, 0.92, 0.075, 0.045, P['bone'], hips, 0.0070))

    # ---- torso (tee), neck, collar
    tee_pts = [(-0.205, 0.87), (-0.215, 1.05), (-0.225, 1.30), (-0.205, 1.41), (-0.12, 1.445), (0, 1.44),
               (0.12, 1.445), (0.205, 1.41), (0.225, 1.30), (0.215, 1.05), (0.205, 0.87), (0, 0.86)]
    tee = F.shape(f'{name}_tee', tee_pts, P['top'], torso, 0.0)
    F.shape(f'{name}_tee_sh', [(0.12, 0.872), (0.205, 0.87), (0.215, 1.05), (0.222, 1.30), (0.2, 1.40), (0.16, 1.425),
                               (0.17, 1.2), (0.15, 1.0)], P['top_sh'], torso, -0.0005)
    neck = F.rrect(f'{name}_neck', -0.045, 1.38, 0.045, 1.52, 0.03, P['skin'], torso, 0.002)
    F.ellipse(f'{name}_collar', 0, 1.445, 0.062, 0.03, P['skin'], torso, -0.001)
    ghost(tee, torso, -0.0015); ghost(neck, torso, 0.0015)
    for i in range(10):                                         # spine
        z = 0.98 + i * 0.045
        xr(F.rrect(f'{name}_vert{i}', -0.017, z, 0.017, z + 0.032, 0.008, P['bone'], torso, -0.0025))
    for i in range(5):                                          # ribs and clavicles
        z = 1.36 - i * 0.047; w = 0.165 - i * 0.008
        for sx in (-1, 1):
            xr(F.limb(f'{name}_rib{i}_{sx}', (0.022 * sx, z), (w * sx, z - 0.03), 0.017, 0.013, P['bone'], torso, -0.0024))
    for sx in (-1, 1):
        xr(F.limb(f'{name}_clav_{sx}', (0.03 * sx, 1.425), (0.17 * sx, 1.43), 0.016, 0.014, P['bone'], torso, -0.0024))

    # ---- arms
    for s, sx in (('sl', -1), ('sr', 1)):
        S, E, W = (SH[0] * sx, SH[1]), (EL[0] * sx, EL[1]), (WR[0] * sx, WR[1])
        sh = J[f'arm_{s}'] = F.joint(f'{name}_arm_{s}', torso, S)
        el = J[f'fore_{s}'] = F.joint(f'{name}_fore_{s}', sh, E)
        wr = J[f'hand_{s}'] = F.joint(f'{name}_hand_{s}', el, W)
        up = F.limb(f'{name}_upper_{s}', S, E, 0.078, 0.07, P['skin'], sh, -0.004)
        sl = F.rrect(f'{name}_sleeve_{s}', S[0] - 0.058, 1.235, S[0] + 0.058, 1.43, 0.045, P['top'], sh, -0.006)
        fo = F.limb(f'{name}_forearm_{s}', E, W, 0.068, 0.058, P['skin'], el, -0.005)
        ha = F.ellipse(f'{name}_handp_{s}', W[0], 0.80, 0.042, 0.055, P['skin'], wr, -0.007)
        tb = F.limb(f'{name}_thumb_{s}', (W[0] - 0.028 * sx, 0.845), (W[0] - 0.045 * sx, 0.80), 0.03, 0.026, P['skin_sh'], wr, -0.0068)
        for o, par, d in ((up, sh, -0.0052), (sl, sh, -0.0072), (fo, el, -0.0062), (ha, wr, -0.0082), (tb, wr, -0.0080)):
            ghost(o, par, d)
        xr(F.limb(f'{name}_humerus_{s}', (S[0], S[1] - 0.02), (E[0], E[1] + 0.015), 0.024, 0.022, P['bone'], sh, -0.0085))
        for k, ox in enumerate((-0.012, 0.012)):
            xr(F.limb(f'{name}_radius{k}_{s}', (E[0] + ox, E[1] - 0.02), (W[0] + ox * 0.8, W[1] + 0.02), 0.014, 0.013, P['bone'], el, -0.0086))
        bj = J[f'bicep_{s}'] = F.joint(f'{name}_bicepj_{s}', sh, (S[0], 1.255))
        R['halos'].append(xr(F.glow(f'{name}_halo_{s}', S[0], 1.255, 0.1, 0.18, P['glow'], bj, -0.0090, power=1.3)))
        R['muscles'].append(xr(F.ellipse(f'{name}_bicep_{s}', S[0], 1.255, 0.033, 0.088, P['muscle'], bj, -0.0095)))
        fj = J[f'forem_{s}'] = F.joint(f'{name}_foremj_{s}', el, (E[0], 0.99))
        R['muscles'].append(xr(F.ellipse(f'{name}_forem_{s}', E[0], 0.99, 0.026, 0.075, P['muscle'], fj, -0.0092)))
        for k in range(3):                                      # pulse rings ("muscle is listening")
            rj = J[f'ring{k}_{s}'] = F.joint(f'{name}_ringj{k}_{s}', sh, (S[0], 1.255))
            rg = F.ring(f'{name}_ring{k}_{s}', S[0], 1.255, 0.07, 0.009, P['glow'], rj, -0.0097, alpha=0.0, mat=F.flat(P['glow']))
            rj.scale = (0.01, 0.01, 0.01); R['rings'].append((rj, rg))

    # ---- head
    for sx in (-1, 1):
        F.ellipse(f'{name}_ear_{sx}', 0.135 * sx, 1.62, 0.026, 0.04, P['skin_sh'], head, -0.008)
    F.shape(f'{name}_hair_back', F.ellipse_pts(0, 1.665, 0.168, 0.18, 12), P['hair_sh'], head, -0.007)
    F.shape(f'{name}_face', [(0, 1.80), (0.1, 1.775), (0.136, 1.70), (0.135, 1.61), (0.115, 1.53), (0.065, 1.478),
                             (0, 1.465), (-0.065, 1.478), (-0.115, 1.53), (-0.135, 1.61), (-0.136, 1.70), (-0.1, 1.775)],
            P['skin'], head, -0.010)
    F.shape(f'{name}_hair', [(-0.152, 1.60), (-0.158, 1.69), (-0.13, 1.785), (-0.06, 1.84), (0.03, 1.848), (0.11, 1.81),
                             (0.155, 1.73), (0.158, 1.62), (0.142, 1.60), (0.13, 1.675), (0.09, 1.722), (0.02, 1.733),
                             (-0.05, 1.716), (-0.11, 1.682), (-0.137, 1.635)], P['hair'], head, -0.018)
    F.shape(f'{name}_hair_hl', [(-0.07, 1.80), (-0.01, 1.828), (0.06, 1.815), (0.0, 1.805)], '#f3f0ec', head, -0.0185)
    F.ellipse(f'{name}_nose', 0, 1.598, 0.016, 0.024, P['nose'], head, -0.012)
    for sx in (-1, 1):
        F.ellipse(f'{name}_blush_{sx}', 0.085 * sx, 1.585, 0.026, 0.014, P['blush'], head, -0.011, alpha=0.45)
    # eyes: four drawings each, pupils on a look joint
    R['eyes'] = {k: [] for k in ('open', 'wide', 'closed', 'happy')}
    for s, sx in (('sl', -1), ('sr', 1)):
        cx, cz = 0.052 * sx, 1.635
        lk = J[f'look_{s}'] = F.joint(f'{name}_look_{s}', head, (cx, cz))
        R['eyes']['open'] += [F.ellipse(f'{name}_eyew_{s}', cx, cz, 0.028, 0.024, P['eye'], head, -0.012),
                              F.ellipse(f'{name}_pupil_{s}', cx, cz, 0.0145, 0.0145, P['pupil'], lk, -0.013),
                              F.ellipse(f'{name}_hl_{s}', cx + 0.005, cz + 0.006, 0.005, 0.005, P['eye'], lk, -0.014)]
        R['eyes']['wide'] += [F.ellipse(f'{name}_eyeW_{s}', cx, cz + 0.004, 0.034, 0.034, P['eye'], head, -0.012),
                              F.ellipse(f'{name}_pupilW_{s}', cx, cz + 0.004, 0.011, 0.011, P['pupil'], lk, -0.013)]
        R['eyes']['closed'].append(F.shape(f'{name}_eyeC_{s}', _arc_pts(cx, cz - 0.004, 0.05, -0.01, 0.008), P['pupil'], head, -0.012))
        R['eyes']['happy'].append(F.shape(f'{name}_eyeH_{s}', _arc_pts(cx, cz - 0.006, 0.048, 0.016, 0.009), P['pupil'], head, -0.012))
        bj = J[f'brow_{s}'] = F.joint(f'{name}_brow_{s}', head, (cx, 1.69))
        inner, outer = (cx - 0.028 * sx, 1.692), (cx + 0.028 * sx, 1.687)      # inner end a touch higher
        F.limb(f'{name}_brow_{s}', outer, inner, 0.012, 0.014, P['brow'], bj, -0.013)
    # mouths
    mj = J['mouth'] = F.joint(f'{name}_mouthj', head, (0, 1.54))
    M = R['mouth'] = {}
    M['smile'] = [F.shape(f'{name}_m_smile', [(-0.042, 1.548), (-0.02, 1.53), (0, 1.524), (0.02, 1.53), (0.042, 1.548),
                                              (0.03, 1.544), (0, 1.535), (-0.03, 1.544)], P['mouth'], mj, -0.012)]
    M['grin'] = [F.shape(f'{name}_m_grin', [(-0.048, 1.553), (0.048, 1.553), (0.035, 1.528), (0, 1.512), (-0.035, 1.528)], P['mouth'], mj, -0.012),
                 F.shape(f'{name}_m_teeth', [(-0.04, 1.551), (0.04, 1.551), (0.033, 1.541), (-0.033, 1.541)], P['teeth'], mj, -0.013, smooth=False),
                 F.ellipse(f'{name}_m_tongue', 0, 1.522, 0.02, 0.008, P['tongue'], mj, -0.013)]
    M['O'] = [F.ellipse(f'{name}_m_O', 0, 1.535, 0.024, 0.032, P['mouth'], mj, -0.012),
              F.ellipse(f'{name}_m_Otongue', 0, 1.516, 0.014, 0.009, P['tongue'], mj, -0.013)]
    M['frown'] = [F.shape(f'{name}_m_frown', _arc_pts(0, 1.528, 0.07, 0.016, 0.009), P['mouth'], mj, -0.012)]
    M['flat'] = [F.limb(f'{name}_m_flat', (-0.03, 1.538), (0.03, 1.536), 0.011, 0.011, P['mouth'], mj, -0.012)]
    R['eyes_all'] = [o for v in R['eyes'].values() for o in v]
    R['mouth_all'] = [o for v in M.values() for o in v]
    face(R, 1, eyes='open', mouth='smile', brows='neutral')
    return R


# ------------------------------------------------------------------ animation helpers
SIDES = {'sl': 1, 'sr': -1}            # outward-positive angle -> joint angle sign


def _target(R, spec):
    """spec -> {joint: (path, index, value)}"""
    J = R['j']; out = {}
    for s, sg in SIDES.items():
        if f'arm_{s}' in spec:
            up, fore, hand = spec[f'arm_{s}']
            out[J[f'arm_{s}']] = math.radians(up * sg); out[J[f'fore_{s}']] = math.radians(fore * sg)
            out[J[f'hand_{s}']] = math.radians(hand * sg)
        if f'ik_{s}' in spec:
            t = spec[f'ik_{s}']; S = (SH[0] * (-1 if s == 'sl' else 1), SH[1])
            u, f = F.ik2(S, L1, L2, t, outward=-1 if s == 'sl' else 1)
            out[J[f'arm_{s}']] = math.radians(u); out[J[f'fore_{s}']] = math.radians(f)
            out[J[f'hand_{s}']] = math.radians(spec.get(f'hand_{s}', 0))
    for k in ('head', 'torso', 'hips'):
        if k in spec: out[J[k]] = math.radians(spec[k])
    return out


def pose(R, f0, f1, spec, interp='BEZIER', easing='AUTO'):
    """Move to a pose between f0 and f1. spec: arm_sl/arm_sr = (outward, elbow, wrist) degrees, or ik_sl/ik_sr =
    hand target (x, z) in rest coordinates; head/torso/hips = tilt degrees; lift = root height; squash = (sx, sz)."""
    for j, v in _target(R, spec).items():
        F.key(j, 'rotation_euler', F.now(j, 'rotation_euler', f0, 1), f0, interp, easing, 1)
        F.key(j, 'rotation_euler', v, f1, 'BEZIER', 'AUTO', 1)
    root, hips = R['j']['root'], R['j']['hips']
    for s in SIDES:                                  # bring an arm in front of the face (hand to cheek or ear)
        if f'front_{s}' in spec:
            j = R['j'][f'arm_{s}']
            F.key(j, 'location', F.now(j, 'location', f0, 1), f0, 'CONSTANT', 'AUTO', 1)
            F.key(j, 'location', -0.03 if spec[f'front_{s}'] else 0.0, f0 + 1, 'CONSTANT', 'AUTO', 1)
    if 'lift' in spec:
        F.key(root, 'location', F.now(root, 'location', f0, 2), f0, interp, easing, 2)
        F.key(root, 'location', spec['lift'], f1, 'BEZIER', 'AUTO', 2)
    if 'squash' in spec:                              # squash/stretch from the feet, so they stay on the floor
        sx, sz = spec['squash']
        for i, v in ((0, sx), (2, sz)):
            F.key(root, 'scale', F.now(root, 'scale', f0, i), f0, interp, easing, i)
            F.key(root, 'scale', v, f1, 'BEZIER', 'AUTO', i)


BROWS = {'neutral': (0, 0.0), 'worried': (-15, 0.008), 'determined': (14, -0.007), 'surprised': (-5, 0.022), 'happy': (-4, 0.01)}


def face(R, frame, eyes=None, mouth=None, brows=None, ramp=3):
    if eyes: F.show_only(R['eyes_all'], R['eyes'][eyes], frame)
    if mouth: F.show_only(R['mouth_all'], R['mouth'][mouth], frame)
    if brows:
        rot, dz = BROWS[brows]
        for s, sg in SIDES.items():
            j = R['j'][f'brow_{s}']; rest_z = j['pivot'][1] - R['j']['head']['pivot'][1]
            F.key(j, 'rotation_euler', F.now(j, 'rotation_euler', max(1, frame - ramp), 1), max(1, frame - ramp), 'BEZIER', 'AUTO', 1)
            F.key(j, 'rotation_euler', math.radians(rot * sg), frame, 'BEZIER', 'AUTO', 1)
            F.key(j, 'location', F.now(j, 'location', max(1, frame - ramp), 2), max(1, frame - ramp), 'BEZIER', 'AUTO', 2)
            F.key(j, 'location', rest_z + dz, frame, 'BEZIER', 'AUTO', 2)


def look(R, frame, dx=0.0, dz=0.0, ramp=4):
    for s in SIDES:
        j = R['j'][f'look_{s}']; hp = R['j']['head']['pivot']
        rx, rz = j['pivot'][0] - hp[0], j['pivot'][1] - hp[1]
        for i, v in ((0, rx + dx), (2, rz + dz)):
            F.key(j, 'location', F.now(j, 'location', max(1, frame - ramp), i), max(1, frame - ramp), 'BEZIER', 'AUTO', i)
            F.key(j, 'location', v, frame, 'BEZIER', 'AUTO', i)


def blink(R, frame, back='open'):
    face(R, frame, eyes='closed'); face(R, frame + 3, eyes=back)


def xray(R, f0, f1, on=True):
    for o in R['xray']:
        if o in R['halos']: continue
        F.key_alpha(o, f1, 1.0 if on else 0.0, f0=f0)


def sway(R, f0, f1, deg=1.2, period=60):
    """A gentle weight shift from the feet (not breathing), so she is never frozen."""
    j = R['j']['root']; f = f0; k = 0
    while f <= f1:
        F.key(j, 'rotation_euler', math.radians(deg if k % 2 else -deg), f, 'BEZIER', 'AUTO', 1); f += period // 2; k += 1


CASTERS = ('tee', 'neck', 'face', 'hair', 'hair_back', 'waist', 'thigh_sl', 'thigh_sr', 'shinp_sl', 'shinp_sr', 'shoe_sl',
           'shoe_sr', 'upper_sl', 'upper_sr', 'sleeve_sl', 'sleeve_sr', 'forearm_sl', 'forearm_sr', 'handp_sl', 'handp_sr')


def shadows(R, behind=0.04):
    """In a 3D world: her drawn shapes cast no shadows (no self-shadowing between the paper layers); invisible copies
    of her silhouette, just behind her, cast her shadow on the floor and walls and follow every pose."""
    name = R['name']
    for o in bpy.data.objects:
        if o.name.startswith(name + '_') and o.type == 'CURVE': o.visible_shadow = False
    R['casters'] = []
    for n in CASTERS:
        nm = f'{name}_{n}'                           # joints can share a name with a shape: take the shape
        o = next((x for x in bpy.data.objects if x.type == 'CURVE' and (x.name == nm or x.name.startswith(nm + '.'))), None)
        if o is None: continue
        c = F.copy_shape(o, o.name + '_cast', '#000000', o.parent, o.location[1] + behind)
        c.visible_camera = False; c.visible_shadow = True
        for a in ('visible_diffuse', 'visible_glossy', 'visible_transmission', 'visible_volume_scatter'):
            try: setattr(c, a, False)
            except Exception: pass
        R['casters'].append(c)
    return R['casters']


def blob_shadow(R, rx=0.46, ry=0.2, at=(0.1, 0.12), color='#2a1626', alpha=0.55, frames=None):
    """Soft drop shadow on the floor under her (a 2D character in a 3D world): a dark radial blur, slightly behind and
    to the side of her feet. It shrinks and fades as she leaves the ground (root height), so hops read."""
    o = F.glow(f"{R['name']}_blob", 0, 0, rx, ry, color, None, 0.0, power=1.2, alpha=alpha)
    o.rotation_euler = (0, 0, 0); o.location = (at[0], at[1], 0.026)
    o.visible_shadow = False
    if frames:
        sc = bpy.context.scene; root = R['j']['root']
        for f in range(frames[0], frames[1] + 1):
            sc.frame_set(f); h = max(0.0, root.location[2])
            k = max(0.55, 1 - 3.0 * h)
            F.key(o, 'scale', (k, k, 1), f, 'LINEAR'); F.key(o, 'color', alpha * k, f, 'LINEAR', 'AUTO', 3)
    return o


def face_camera(R, cam):
    """House rule: 2D characters are always head-on to the camera. As the camera moves, the whole puppet turns
    (about the vertical axis only) to face it on every frame."""
    c = R['j']['root'].constraints.new('LOCKED_TRACK')
    c.name = 'face_camera'; c.target = cam; c.track_axis = 'TRACK_NEGATIVE_Y'; c.lock_axis = 'LOCK_Z'
    return c
