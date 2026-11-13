"""sets_lib.py: the ready-made sets and props for cut-out Shorts, in the painted-3D look of world3d.py.

Library first: furniture and props come from Poly Haven (world3d.furniture, repainted, then rick_look smooths the
set's shading). Rooms, counters, stairs, tiles and building fronts are simple shapes. Conventions: the camera looks
towards +y, floors at z 0, characters stand near x 0. Every set returns a dict of spots and a ground function.

    kitchen()             warm kitchen: counter, window over the sink, kettle, microwave, table; jar() is the pickle jar
    bathroom()            cool tiled bathroom; the camera is the mirror, so the character faces it
    street()              a high street running towards the camera: shops and flats on the left, lamps along the kerb
    stairs(night=False)   a stairwell rising TOWARDS the camera; the landing is at the top, near the camera
    doctor()              a GP's room: desk, shelves, blinds, examination couch
    world3d.living_room(), world3d.gym(), world3d.park(mood)   the other three sets
Props: jar(), bag(), dumbbell(name, kg, colour), text() (always with a black outline: house rule).
LIGHT[key] holds the light rig for each set (shotkit.light(key, f0, f1)); look.MOODS holds their grades.
New sets follow the same pattern: simple shapes plus library props, a LIGHT entry, a mood, and a ground function.
"""
import bpy, math, os, random
from mathutils import Vector
import world3d as W
import look

R_ = math.radians


def text(name, body, loc, size, hexcol, rot=(90, 0, 0), extrude=0.0, align='CENTER', emit=1.0, c='WORLD',
         outline=0.06, outline_hex='#000000'):
    """In-world text (a label, a sign, a note). House rule: every piece of text has a black outline. The outline is a
    twin named <name>_ol just behind the text, its glyphs grown by `outline` x size (0 turns it off: don't)."""
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = body; cu.size = size; cu.align_x = align; cu.align_y = 'CENTER'
    cu.extrude = extrude
    o = bpy.data.objects.new(name, cu); W.coll(c).objects.link(o)
    o.location = loc; o.rotation_euler = tuple(R_(a) for a in rot)
    o.data.materials.append(W.emit(name + '_m', hexcol, emit) if emit else W.toon(name + '_m', hexcol))
    if outline:
        oc = bpy.data.curves.new(name + '_ol', 'FONT'); oc.body = body; oc.size = size; oc.align_x = align
        oc.align_y = 'CENTER'; oc.extrude = extrude; oc.offset = size * outline
        ol = bpy.data.objects.new(name + '_ol', oc); W.coll(c).objects.link(ol)
        ol.parent = o; ol.location = (0.0, 0.0, -max(0.0006, size * 0.02)); o['outline'] = ol.name
        ol.data.materials.append(W.emit(name + '_olm', outline_hex, 1.0))
    return o


def bag(name):
    """A paper shopping bag (box + handle). Origin at the handle, so it hangs from a hand."""
    e = bpy.data.objects.new(name, None); W.coll('WORLD').objects.link(e)
    b = W.box(f'{name}_b', (0.2, 0.11, 0.24), (0, 0, -0.17), W.toon(f'{name}_paper', '#c99a62'), ink=0.006)
    h = W.box(f'{name}_h', (0.12, 0.012, 0.012), (0, 0, -0.04), W.toon(f'{name}_hd', '#7a4a2a'), ink=0.003)
    g = W.box(f'{name}_g', (0.08, 0.02, 0.06), (0, -0.056, -0.15), W.toon(f'{name}_lbl', '#4f6fb0'), ink=0)
    for o in (b, h, g): o.parent = e
    return e


def dumbbell(name, kg, col, scale=1.0):
    """A dumbbell with coloured plates and its weight printed on the end (outlined text)."""
    e = W.dumbbell(name, (0, 0, 0), (0, 0, 0), scale)
    for o in e.children:
        if 'plate' in o.name: o.data.materials[0] = W.toon(f'{name}_iron', col)
    t = text(f'{name}_kg', f'{kg}kg', (0.0, -0.05, 0.0), 0.035, '#ffffff', rot=(90, 0, 0), emit=1.2)
    t.parent = e; t.location = (0.09, -0.052, 0.0)
    return e


def jar(name='jar'):
    """The pickle jar: pale green glass with pickles, red lid, cream label. Origin at its base."""
    e = bpy.data.objects.new(name, None); W.coll('WORLD').objects.link(e)
    parts = [W.cyl(f'{name}_glass', 0.055, 0.15, (0, 0, 0.075), W.toon(f'{name}_glass', '#a9c98a'), ink=0.003),
             W.cyl(f'{name}_lid', 0.058, 0.03, (0, 0, 0.165), W.toon(f'{name}_lid', '#c8402f'), ink=0.003),
             W.cyl(f'{name}_label', 0.0565, 0.06, (0, 0, 0.07), W.toon(f'{name}_label', '#f1e6c8'), ink=0)]
    for p in parts: p.parent = e
    return e


def _window(name, x0, x1, z0, z1, y, frame_hex='#f4ece0', sky=('#fff1d6', '#bfe0f5', '#6fa6e0'), depth=1.4, mull=True):
    fr = W.toon(f'{name}_fr', frame_hex); t = 0.07
    for n, s, l in ((f'{name}_l', (t, 0.14, z1 - z0 + t), (x0, y, (z0 + z1) / 2)), (f'{name}_r', (t, 0.14, z1 - z0 + t), (x1, y, (z0 + z1) / 2)),
                    (f'{name}_t', (x1 - x0 + t, 0.14, t), ((x0 + x1) / 2, y, z1)), (f'{name}_b', (x1 - x0 + 0.2, 0.26, t), ((x0 + x1) / 2, y - 0.05, z0))):
        W.box(n, s, l, fr, ink=0.004)
    if mull:
        W.box(f'{name}_mv', (0.04, 0.06, z1 - z0), ((x0 + x1) / 2, y, (z0 + z1) / 2), fr, ink=0.003)
    W.box(f'{name}_sky', (x1 - x0 + 3, 0.05, z1 - z0 + 3), ((x0 + x1) / 2, y + depth, (z0 + z1) / 2),
          W.sky_mat(f'{name}_skym', [(0.0, sky[0]), (0.45, sky[1]), (1.0, sky[2])]), ink=0)


def grout(name, xspans, y, z0, z1, step, hexcol):
    """Tile joints as thin strips on a wall at y (facing -y): real geometry, so tiles read and the camera's motion shows."""
    m = W.toon(name, hexcol); k = 0
    for x0, x1 in xspans:
        z = z0
        while z <= z1 + 1e-6:
            W.box(f'{name}_h{k}', (x1 - x0, 0.006, 0.008), ((x0 + x1) / 2, y, z), m, ink=0); z += step; k += 1
        x = x0
        while x <= x1 + 1e-6:
            W.box(f'{name}_v{k}', (0.008, 0.006, z1 - z0), (x, y, (z0 + z1) / 2), m, ink=0); x += step; k += 1


def floor_grid(name, xr, yr, step, hexcol, z=0.0):
    m = W.toon(name, hexcol); k = 0
    x = xr[0]
    while x <= xr[1]:
        W.box(f'{name}_x{k}', (0.01, yr[1] - yr[0], 0.004), (x, (yr[0] + yr[1]) / 2, z + 0.002), m, ink=0); x += step; k += 1
    y = yr[0]
    while y <= yr[1]:
        W.box(f'{name}_y{k}', (xr[1] - xr[0], 0.01, 0.004), ((xr[0] + xr[1]) / 2, y, z + 0.002), m, ink=0); y += step; k += 1


# ---------------------------------------------------------------- kitchen (warm morning)
def kitchen():
    wall = W.toon('k_wall', '#ecd6b2'); tile = W.toon('k_tile', '#f6eedc'); floor = W.toon('k_floor', '#c9a27e', 'wood_deck.png')
    cab = W.toon('k_cab', '#86b39c'); top = W.toon('k_top', '#ede4d4'); line = W.toon('k_line', '#456e5d')
    W.box('floor', (12, 10, 0.1), (0, -1.0, -0.05), floor, ink=0)
    W.box('ceiling', (12, 10, 0.1), (0, -1.0, 3.0), W.toon('k_ceil', '#efe2cc'), ink=0)
    for n, s, l in (('wall_l', (5.6, 0.2, 3.0), (-2.5, 2.3, 1.5)), ('wall_r', (4.6, 0.2, 3.0), (3.7, 2.3, 1.5)),
                    ('wall_b', (1.4, 0.2, 1.25), (0.9, 2.3, 0.625)), ('wall_t', (1.4, 0.2, 0.75), (0.9, 2.3, 2.625))):
        W.box(n, s, l, wall, ink=0)
    W.box('wall_side', (0.2, 9, 3.0), (-4.2, -1.8, 1.5), W.toon('k_wall2', '#dcc09a'), ink=0)
    _window('kwin', 0.2, 1.6, 1.25, 2.25, 2.25)
    for k, (x, y) in enumerate(((0.4, 3.4), (1.5, 3.2), (2.4, 3.6))):                       # garden hedge outside
        W.box(f'hedge{k}', (1.6, 0.6, 1.4 + 0.3 * k), (x, y + 0.6, 0.7), W.emit(f'hedge{k}', '#6fa864', 1.0), ink=0)
    W.box('splash_l', (4.6, 0.04, 0.34), (-2.0, 2.19, 1.1), tile, ink=0); W.box('splash_r', (3.1, 0.04, 0.34), (3.15, 2.19, 1.1), tile, ink=0)
    grout(f'k_grout', [(-4.3, 0.3), (1.6, 4.7)], 2.165, 0.93, 1.27, 0.15, '#c9b99c')
    W.box('base_cab', (7.6, 0.62, 0.88), (0.2, 1.9, 0.44), cab, ink=0)
    W.box('worktop', (7.7, 0.68, 0.05), (0.2, 1.88, 0.905), top, ink=0)
    for k in range(9): W.box(f'cab_door{k}', (0.02, 0.01, 0.72), (-3.2 + k * 0.8, 1.585, 0.46), line, ink=0)
    for k in range(9): W.box(f'cab_knob{k}', (0.12, 0.02, 0.02), (-3.0 + k * 0.8, 1.58, 0.78), W.toon('k_knob', '#d9c27a'), ink=0)
    W.box('wall_cab_l', (3.2, 0.36, 0.72), (-1.8, 2.03, 2.07), cab, ink=0)
    W.box('wall_cab_r', (2.2, 0.36, 0.72), (2.75, 2.03, 2.07), cab, ink=0)
    for k in range(4): W.box(f'wcab_line{k}', (0.02, 0.01, 0.62), (-2.6 + k * 0.8, 1.845, 2.07), line, ink=0)
    W.box('sink', (0.7, 0.45, 0.06), (0.9, 1.86, 0.91), W.toon('k_sink', '#b9c0c6'), ink=0)
    W.cyl('tap', 0.015, 0.3, (0.9, 2.05, 1.05), W.toon('k_tap', '#c9cdd2'), ink=0.003)
    W.furniture('vintage_microwave', (-2.4, 1.95, 0.93), 0, 1.0)
    W.furniture('vintage_electric_kettle', (-1.35, 1.92, 0.93), 15, 1.0)
    W.furniture('wooden_cutting_board', (-0.7, 2.0, 0.93), 0, 1.0)
    W.furniture('bananas', (1.9, 1.9, 0.93), 30, 1.0)
    W.furniture('jug_01', (2.5, 1.95, 0.93), 0, 1.0)
    W.furniture('potted_plant_02', (1.25, 2.2, 1.29), 0, 0.5)
    W.furniture('wall_clock', (3.4, 2.19, 2.05), 0, 1.0)
    W.furniture('dining_table', (2.3, -0.9, 0), 90, 1.0)
    W.furniture('dining_chair_02', (2.9, -0.5, 0), -100, 1.0)
    for k, (x, h) in enumerate(((-3.0, 0.22), (-2.75, 0.18), (-0.25, 0.25))):                # jars and tins on the counter
        W.cyl(f'tin{k}', 0.06, h, (x, 2.0, 0.93 + h / 2), W.toon(f'tin{k}', ('#c86b4a', '#e0b84a', '#7a9cc8')[k]), ink=0.003)
    return dict(spot=(0.0, 0.55), ground=None)


# ---------------------------------------------------------------- bathroom (cool)
def bathroom():
    t_hi = W.toon('b_tile', '#dcecf0'); t_lo = W.toon('b_tile2', '#5f9fb0')
    floor = W.toon('b_floor', '#e4ddd2'); white = W.toon('b_white', '#f4f2ee'); chrome = W.toon('b_chrome', '#c9d2d8')
    W.box('floor', (10, 8, 0.1), (0, -1.0, -0.05), floor, ink=0)
    W.box('ceiling', (10, 8, 0.1), (0, -1.0, 2.8), W.toon('b_ceil', '#eef3f4'), ink=0)
    W.box('wall_back_hi', (8, 0.2, 1.7), (0, 2.1, 1.95), t_hi, ink=0); W.box('wall_back_lo', (8, 0.2, 1.1), (0, 2.1, 0.55), t_lo, ink=0)
    W.box('wall_back_rail', (8, 0.08, 0.05), (0, 1.98, 1.1), white, ink=0)
    W.box('wall_left_lo', (0.2, 8, 1.1), (-2.3, -1.6, 0.55), t_lo, ink=0)
    for n, s, l in (('wl_a', (0.2, 3.0, 1.7), (-2.3, -1.6, 1.95)), ('wl_b', (0.2, 2.2, 1.7), (-2.3, 1.0, 1.95)),
                    ('wl_c', (0.2, 0.8, 0.45), (-2.3, -0.5 + 0.1, 2.575)), ('wl_d', (0.2, 0.8, 0.35), (-2.3, -0.5 + 0.1, 1.275))):
        W.box(n, s, l, t_hi, ink=0)
    W.box('frosted', (0.04, 0.8, 0.95), (-2.22, -0.4, 1.9), W.emit('frosted', '#eef6ff', 1.6), ink=0.004)
    W.box('wall_right', (0.2, 8, 2.8), (2.6, -1.6, 1.4), t_hi, ink=0)
    # bath along the back wall, left
    W.box('bath', (1.75, 0.78, 0.56), (-1.2, 1.58, 0.28), white, ink=0.006)
    W.box('bath_in', (1.55, 0.6, 0.05), (-1.2, 1.58, 0.545), W.toon('b_water', '#9fd0de'), ink=0)
    W.cyl('bath_tap', 0.018, 0.25, (-1.95, 1.9, 0.68), chrome, ink=0.003)
    W.furniture('rubber_duck_toy', (-0.55, 1.3, 0.56), -30, 0.8, tint='#f2c14e')
    grout('b_grout', [(-4.0, 4.0)], 1.995, 0.0, 2.8, 0.25, '#9fb8c0')
    floor_grid('b_fgrid', (-4, 4), (-4, 2), 0.45, '#cfc6b8')
    # door and towel rail on the right
    W.box('door', (0.9, 0.06, 2.05), (1.75, 1.98, 1.025), W.toon('b_door', '#f1ebe1'), ink=0.006)
    W.cyl('door_knob', 0.03, 0.05, (1.42, 1.93, 1.0), chrome, ink=0, rot=(R_(90), 0, 0))
    W.box('towel_rail', (0.7, 0.05, 0.03), (0.75, 1.96, 1.35), chrome, ink=0.003)
    W.box('towel', (0.5, 0.05, 0.62), (0.75, 1.94, 1.06), W.toon('b_towel', '#e8857a'), ink=0.006)
    W.box('shelf', (0.8, 0.18, 0.03), (-0.2, 1.92, 1.6), white, ink=0.003)
    for k, (x, h, c) in enumerate(((-0.45, 0.2, '#7fc4a0'), (-0.25, 0.16, '#f2c14e'), (-0.05, 0.22, '#c86b8a'), (0.12, 0.14, '#9fb7e8'))):
        W.cyl(f'bottle{k}', 0.035, h, (x, 1.92, 1.615 + h / 2), W.toon(f'bottle{k}', c), ink=0.003)
    W.furniture('potted_plant_02', (2.2, 1.5, 0), 0, 0.9)
    # the basin in the foreground (between June and the camera-mirror)
    W.cyl('basin_ped', 0.11, 0.78, (0.0, -0.35, 0.39), white, ink=0.006, r2=0.08)
    W.box('basin', (0.62, 0.42, 0.14), (0.0, -0.32, 0.84), white, ink=0.006)
    W.cyl('cup', 0.035, 0.1, (0.22, -0.3, 0.96), W.toon('b_cup', '#5f9fb0'), ink=0.003)
    return dict(spot=(0.0, 0.25), ground=None)


# ---------------------------------------------------------------- high street (runs towards the camera)
def street(mood='day'):
    import sets as S
    c = W.coll('WORLD'); o = (0, 0, 0)
    S.sky(c, o, False)
    stone = W.toon('st_pave', '#c9c2b6'); kerb = W.toon('st_kerb', '#d8d2c6'); road = W.toon('st_road', '#4a4e57', 'dirt.png')
    W.box('pavement', (3.4, 80, 0.12), (0.2, 20, 0.06), stone, ink=0)
    floor_grid('st_slabs', (-1.5, 1.85), (-8, 48), 0.6, '#a9a296', z=0.12)
    W.box('kerb', (0.18, 80, 0.14), (1.95, 20, 0.07), kerb, ink=0)
    W.box('road', (8, 80, 0.05), (6.0, 20, 0.0), road, ink=0)
    for k in range(14): W.box(f'roadline{k}', (0.12, 2.2, 0.01), (6.0, -4 + k * 6, 0.03), W.toon('st_line', '#f2efe6'), ink=0)
    W.box('far_pave', (3.0, 80, 0.12), (11.5, 20, 0.06), stone, ink=0)
    rnd = random.Random(7)
    pal = ['#c8705a', '#e2c79a', '#8fa9c9', '#d9a066', '#b5c49a', '#e8d7c0', '#a8645a', '#9cb8b0']
    awn = ['#c0392b', '#2e7d6b', '#f0b429', '#3d6fb6', '#8e44ad']
    y = -6.0; k = 0
    while y < 60:                                               # left side: shops with flats above, facing +x
        w = rnd.uniform(5.0, 7.5); h = rnd.uniform(7.5, 12.0); col = pal[k % len(pal)]
        W.box(f'bld{k}', (6, w - 0.08, h), (-4.5, y + w / 2, h / 2), W.toon(f'bld{k}', col), ink=0)
        W.box(f'shop{k}', (0.1, w - 0.9, 2.3), (-1.47, y + w / 2, 1.35), W.emit(f'shopwin{k}', '#f6e7c8', 1.15), ink=0.006)
        W.box(f'shopframe{k}', (0.14, w - 0.6, 0.18), (-1.45, y + w / 2, 2.6), W.toon(f'sf{k}', '#2f3440'), ink=0)
        a = W.box(f'awning{k}', (1.1, w - 0.7, 0.06), (-0.95, y + w / 2, 2.95), W.toon(f'awn{k}', awn[k % len(awn)]), ink=0.006)
        a.rotation_euler = (0, R_(-14), 0)
        for r in range(int((h - 3.6) // 1.7)):                  # flat windows
            for q in range(int((w - 1.0) // 1.6)):
                W.box(f'win{k}_{r}_{q}', (0.08, 0.8, 1.0), (-1.48, y + 0.9 + q * 1.6 + 0.4, 4.0 + r * 1.7),
                      W.toon('st_win', '#3e4f6a'), ink=0)
        y += w; k += 1
    y = -6.0; k = 0
    while y < 60:                                               # far side of the road, facing -x
        w = rnd.uniform(6.0, 9.0); h = rnd.uniform(6.0, 10.0)
        W.box(f'bldR{k}', (6, w - 0.1, h), (16.0, y + w / 2, h / 2), W.toon(f'bldR{k}', pal[(k + 3) % len(pal)]), ink=0)
        for r in range(int((h - 1.5) // 1.8)):
            for q in range(int((w - 1.0) // 1.8)):
                W.box(f'winR{k}_{r}_{q}', (0.08, 0.9, 1.0), (12.97, y + 1.0 + q * 1.8 + 0.45, 1.6 + r * 1.8), W.toon('st_win', '#3e4f6a'), ink=0)
        y += w; k += 1
    for k, yy in enumerate((-2.0, 6.0, 14.0, 22.0, 30.0, 38.0)):
        W.furniture('street_lamp_02', (1.65, yy, 0.12), 90, 1.0)
    W.furniture('fire_hydrant', (1.45, 3.0, 0.12), 0, 1.0)
    W.furniture('metal_trash_can', (1.5, 9.5, 0.12), 0, 1.0)
    for yy in (1.0, 11.0, 19.0): W.furniture('planter_box_01', (1.4, yy, 0.12), 90, 1.0)
    for k, yy in enumerate((9.0, 17.0, 27.0)):                   # street trees in the pavement (clear of her end mark)
        S.tree(c, f'stree{k}', (1.35, yy, 0.12), 4.2, 40 + k)
    return dict(spot=(0.2, 0.0), ground=lambda x, y: 0.12 if x < 1.9 else 0.0)


# ---------------------------------------------------------------- stairwell rising towards the camera
STEP_N, RISE, GOING, STAIR_Y0 = 14, 0.185, 0.27, 4.0          # bottom step at y 4.0 (z 0), climbing towards -y
LANDING_Z = STEP_N * RISE                                   # 2.59


def stairs_ground(x, y):
    if y >= STAIR_Y0: return 0.0
    k = int((STAIR_Y0 - y) // GOING) + 1
    return min(k, STEP_N) * RISE


def stairs(night=False):
    wall = W.toon('h_wall', '#e2d2b0' if not night else '#5b6fc0'); carpet = W.toon('h_carpet', '#8f3b3b')
    wood = W.toon('h_wood', '#7a5236', 'wood_dark.png'); white = W.toon('h_white', '#f2ece2' if not night else '#b4bfe6'); carpet = W.toon('h_carpet', '#a24a44')
    W.box('hall_floor', (7, 19, 0.1), (1.0, 4.0, -0.05), W.toon('h_floor', '#a87a52', 'wood_deck.png'), ink=0)
    W.box('wall_far_right', (0.2, 19, 6.5), (3.2, 4.0, 3.25), wall, ink=0)
    W.box('wall_back_hall', (7, 0.2, 6.5), (1.0, -4.6, 3.25), wall, ink=0)
    for k in range(STEP_N):                                      # treads with a carpet runner and white risers
        y1 = STAIR_Y0 - k * GOING; z = (k + 1) * RISE
        W.box(f'step{k}', (1.5, GOING, z), (0.0, y1 - GOING / 2, z / 2), white, ink=0)
        W.box(f'runner{k}', (0.9, GOING - 0.06, 0.012), (0.0, y1 - GOING / 2 + 0.03, z + 0.006), carpet, ink=0)   # white tread stripe at each nose
        W.box(f'nose{k}', (1.52, 0.06, 0.04), (0.0, y1 - GOING + 0.03, z - 0.02), white, ink=0)
    W.box('landing', (1.5, 2.6, LANDING_Z), (0.0, STAIR_Y0 - STEP_N * GOING - 1.3, LANDING_Z / 2), white, ink=0)
    W.box('landing_carpet', (1.5, 2.6, 0.012), (0.0, STAIR_Y0 - STEP_N * GOING - 1.3, LANDING_Z + 0.006), carpet, ink=0)
    W.box('wall_left', (0.2, 16, 6.5), (-0.85, 3.0, 2.6), wall, ink=0)
    for k in range(6):                                           # landing banister along its open side
        W.box(f'lspindle{k}', (0.035, 0.035, 0.9), (0.72, 0.1 - k * 0.45, LANDING_Z + 0.45), white, ink=0.003)
    W.box('lrail', (0.07, 2.6, 0.06), (0.72, -1.1, LANDING_Z + 0.92), wood, ink=0.004)
    W.box('skirt_l', (0.04, 16, 0.12), (-0.74, 3.0, 0.06), white, ink=0)
    W.box('ceiling', (7, 19, 0.1), (1.0, 4.0, LANDING_Z + 2.6), W.toon('h_ceil', '#efe6d6' if not night else '#3f4f8f'), ink=0)
    # banister on the right: posts and a sloped handrail
    W.box('newel', (0.1, 0.1, 1.15), (0.68, STAIR_Y0 - 0.05, 0.575), wood, ink=0.006)
    for k in range(0, STEP_N, 2):
        y1 = STAIR_Y0 - (k + 0.5) * GOING; z = (k + 1) * RISE
        W.box(f'spindle{k}', (0.035, 0.035, 0.9), (0.68, y1, z + 0.45), white, ink=0.003)
    rail = W.box('handrail', (0.07, math.hypot(STEP_N * GOING, LANDING_Z), 0.06), (0.68, STAIR_Y0 - STEP_N * GOING / 2, LANDING_Z / 2 + 0.92),
                 wood, ink=0.004)
    rail.rotation_euler = (-math.atan2(LANDING_Z, STEP_N * GOING), 0, 0)    # rises towards -y, with the stairs
    # front door at the bottom of the hall, coat hooks, pictures stepping up the wall
    W.box('front_door', (1.0, 0.08, 2.1), (0.0, 7.2, 1.05), W.toon('h_door', '#3d5a80'), ink=0.006)
    W.box('door_glass', (0.5, 0.04, 0.6), (0.0, 7.15, 1.6), W.emit('h_door_glass', '#f6e7c8' if not night else '#2b3a66', 1.2), ink=0)
    for k, yy in enumerate((3.2, 2.2, 1.2)):
        W.furniture(('hanging_picture_frame_01', 'hanging_picture_frame_02', 'hanging_picture_frame_03')[k],
                    (-0.74, yy, stairs_ground(0, yy) + 1.55), -90, 1.0)
    # landing window on the left wall (moonlight at night) and a small table with a lamp
    W.box('landing_win', (0.05, 0.8, 1.0), (-0.73, -0.9, LANDING_Z + 1.5),
          W.emit('h_win', '#dfeefc' if not night else '#5d7fd8', 1.4 if not night else 0.9), ink=0.006)
    W.furniture('side_table_01', (0.75, -1.4, LANDING_Z), 0, 0.8)
    W.cyl('lamp_shade', 0.12, 0.18, (0.75, -1.4, LANDING_Z + 0.68), W.emit('h_lamp', '#ffd9a0', 2.0 if night else 1.0), r2=0.08, ink=0.004)
    return dict(spot=(0.0, STAIR_Y0 + 0.4), ground=stairs_ground)


# ---------------------------------------------------------------- the GP's room (cool daylight)
def doctor():
    wall = W.toon('d_wall', '#cfe3d6'); floor = W.toon('d_floor', '#c3ccd2'); white = W.toon('d_white', '#f3f1ec')
    W.box('floor', (10, 8, 0.1), (0, -1.0, -0.05), floor, ink=0)
    W.box('ceiling', (10, 8, 0.1), (0, -1.0, 2.9), W.toon('d_ceil', '#f0f2ef'), ink=0)
    for n, s, l in (('wall_l', (3.6, 0.2, 2.9), (-2.6, 2.4, 1.45)), ('wall_r', (4.0, 0.2, 2.9), (2.9, 2.4, 1.45)),
                    ('wall_b', (1.8, 0.2, 0.95), (0.1, 2.4, 0.475)), ('wall_t', (1.8, 0.2, 0.55), (0.1, 2.4, 2.625))):
        W.box(n, s, l, wall, ink=0)
    _window('dwin', -0.8, 1.0, 0.95, 2.35, 2.35, frame_hex='#f4f4f0', sky=('#f4fbff', '#cfe6f7', '#8fbbe8'), mull=False)
    for k in range(9):                                           # venetian blinds, half drawn
        W.box(f'blind{k}', (1.8, 0.03, 0.035), (0.1, 2.28, 2.3 - k * 0.075), W.toon('d_blind', '#f6f4ee'), ink=0)
    desk = W.toon('d_desk', '#d8b892'); steel = W.toon('d_steel', '#7d8794')     # a plain desk (the library's
    W.box('desk_top', (1.5, 0.75, 0.05), (0.35, 1.0, 0.75), desk, ink=0)                            # one is too big to stage around)
    W.box('desk_front', (1.46, 0.03, 0.5), (0.35, 0.64, 0.48), desk, ink=0)
    for x in (-0.36, 1.06): W.box(f'desk_leg{x}', (0.05, 0.7, 0.72), (x, 1.0, 0.36), steel, ink=0)
    W.furniture('classic_laptop', (1.02, 1.12, 0.775), 200, 1.0)                    # back corner: clear of the MCU sightline
    W.furniture('clipboard', (0.0, 0.85, 0.775), 10, 1.0)
    W.furniture('desk_lamp_arm_01', (-0.2, 1.2, 0.775), 30, 1.0)
    shelf = W.toon('d_shelf', '#e9e4da')                             # a simple wall shelf (the library's steel rack is huge)
    for z in (1.1, 1.5): W.box(f'dshelf{z}', (0.9, 0.28, 0.03), (2.2, 2.15, z), shelf, ink=0)
    for k, (x, c_) in enumerate(((1.9, '#7fa7c8'), (2.1, '#e07a5f'), (2.35, '#f2c14e'))):
        W.box(f'dbox{k}', (0.16, 0.2, 0.22), (x, 2.12, 1.235), W.toon(f'dbox{k}', c_), ink=0.004)
    W.furniture('wall_clock', (-1.7, 2.29, 2.1), 0, 1.0)
    W.furniture('potted_plant_04', (-2.3, 1.6, 0), 0, 1.0)
    W.box('couch', (0.75, 1.9, 0.6), (-2.2, 0.2, 0.3), W.toon('d_couch', '#7fa7c8'), ink=0.006)
    W.box('couch_paper', (0.6, 1.7, 0.02), (-2.2, 0.2, 0.61), white, ink=0)
    W.box('poster', (0.55, 0.03, 0.8), (-1.2, 2.29, 1.65), white, ink=0.004)
    W.box('poster_art', (0.42, 0.02, 0.62), (-1.2, 2.27, 1.65), W.toon('d_poster', '#e07a5f'), ink=0)
    return dict(spot=(-0.75, 0.15), doc=(0.45, 1.45), ground=None)


# ---------------------------------------------------------------- light rigs (world3d.light keywords) per set
look.MOODS['kitchen'] = dict(look.MOODS['living'], top=(0.46, 0.40, 0.36), hor=(0.72, 0.58, 0.46), sat=1.05, wstr=0.25,
                             gain=(0.84, 0.72, 0.68), lift=(0.92, 0.9, 0.96), gam=1.0)
look.MOODS['bath'] = dict(look.MOODS['living'], top=(0.46, 0.52, 0.6), hor=(0.62, 0.7, 0.76), sat=1.04, wstr=0.25,
                          gain=(0.77, 0.75, 0.84), lift=(0.9, 0.93, 1.0), gam=1.0)
look.MOODS['hall'] = dict(look.MOODS['living'], top=(0.42, 0.38, 0.36), hor=(0.6, 0.52, 0.46), sat=0.95, wstr=0.25,
                          gain=(0.86, 0.75, 0.73), lift=(0.9, 0.9, 0.96), gam=1.0)
look.MOODS['hall_night'] = dict(look.MOODS['living'], top=(0.05, 0.07, 0.16), hor=(0.08, 0.1, 0.2), wstr=0.4,
                                fill=((0.45, 0.55, 1.0), 12.0), lamp=((1.0, 0.7, 0.42), 140.0), sat=0.9,
                                gain=(0.72, 0.75, 0.9), lift=(0.9, 0.92, 1.04), gam=1.0, vig=0.5)
look.MOODS['clinic'] = dict(look.MOODS['gym'], sat=1.3, gain=(0.82, 0.84, 0.88))     # interior band: YAVG <= 139
look.MOODS['street'] = dict(look.MOODS['day'], sat=1.05, gain=(0.92, 0.88, 0.82))
look.MOODS['living_eve'] = dict(look.MOODS['living'], lamp=((1.0, 0.7, 0.42), 140.0))
if os.environ.get('SETS_TUNE'):   # grade tuning for the set moods above: SETS_TUNE='{"hall_night":{"sat":0.8}}'
    import json as _json
    for _m, _d in _json.loads(os.environ['SETS_TUNE']).items():
        if _m in look.MOODS: look.MOODS[_m].update({k: (tuple(v) if isinstance(v, list) else v) for k, v in _d.items()})

LIGHT = {
    'kitchen': dict(mood='kitchen', lamp_at=(0, 0, -10), key_at=(-3.2, -1.6, 2.7), key_to=(0.0, 0.5, 1.0), key_energy=520,
                    key_color=(1.0, 0.86, 0.68), key_size=1.6, window=(0.9, 2.1, 1.75), window_energy=140, shadow='key'),
    'bath': dict(mood='bath', lamp_at=(0, 0, -10), key_at=(-2.1, -0.4, 1.9), key_to=(0.0, 0.25, 1.2), key_energy=420,
                 key_color=(0.88, 0.94, 1.0), key_size=1.0, window=None, shadow='key'),
    'street': dict(mood='street', lamp_at=(0, 40, -5), key_energy=0, window=None, shadow='LOOK_Sun'),
    'hall': dict(mood='hall', lamp_at=(0.75, -1.4, LANDING_Z + 0.7), key_at=(-0.65, -0.9, LANDING_Z + 1.5), key_to=(0.4, 2.0, 1.2),
                 key_energy=900, key_color=(1.0, 0.84, 0.62), key_size=0.35, window=None, shadow='key'),
    'hall_night': dict(mood='hall_night', lamp_at=(0.75, -1.4, LANDING_Z + 0.75), key_at=(-0.55, 1.4, LANDING_Z + 2.0),
                       key_to=(0.0, -0.3, LANDING_Z + 0.6), key_energy=320, key_color=(0.55, 0.68, 1.0), key_size=0.5, window=None, shadow='key'),
    'living': dict(mood='living'),
    'living_eve': dict(mood='living_eve', key_energy=160, key_color=(1.0, 0.75, 0.5), window_energy=40),
    'gym': dict(mood='gym', lamp_at=(0, 0, -10), key_at=(-2.4, -2.9, 3.2), key_to=(0.2, 0.5, 0.9), key_energy=900,
                key_color=(1.0, 0.84, 0.66), window=None, shadow='key'),          # warm, high, from the camera side
    'park_dusk': dict(mood='park_dusk', lamp_at=(0, 40, -5), key_energy=0, window=None, shadow='LOOK_Sun'),
    'clinic': dict(mood='clinic', lamp_at=(0, 0, -10), key_at=(0.1, 2.0, 2.0), key_to=(-0.4, 0.2, 1.1), key_energy=380,
                   key_color=(0.95, 0.98, 1.0), key_size=1.8, window=None, shadow='key'),
}
