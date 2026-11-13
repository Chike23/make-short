# Worlds and light: the default look

This is how the default style builds its places and lights them, from frame studies of the reference. A new style changes the colours and materials (`style-change.md`), but keeps the method.

## What the reference worlds look like
- **Sets.** Smoothly lit 3D sets. The light rolls softly across surfaces with no cel steps, and the sets have **no outlines**: only the characters are drawn with lines.
- **Light.** One strong sun or key that casts clear shadows. Warm key against a cool fill. The shadows are indigo, never black.
- **Air.** Haze towards a bright horizon outdoors, and shallow depth of field on medium and close shots.
- **Camera.** A low, wide camera with leading lines (a street, a path, a stair flight) on the wides.
- **Surfaces.** Plain colours with a little fine detail (tile grout, slab lines, window frames). Noisy textures sparkle in motion: the verifier flagged the grass, foliage and water in the park.
- **Furniture.** Recognisable, slightly simplified furniture, which is what Poly Haven gives once it is repainted.

`W.rick_look()` turns the kit's toon world into this look:
- it smooths the shading ramps;
- it switches the set outlines off;
- it lightens the depth lines (`depth_ink=1.0`).

`finish()` calls it, and adds depth of field focused on the subject (`fstop` 1.6 by default; 4–6 when a prop must stay sharp).

## The sets in the kit
| Set | Function | Notes |
|---|---|---|
| Kitchen | `S6.kitchen()` | warm morning; counter, window over the sink, Poly Haven kettle, microwave, table, plant, clock |
| Bathroom | `S6.bathroom()` | cool tiles with grout; the camera is the mirror, so the character faces it |
| High street | `S6.street()` | runs towards the camera; shops on the left, lamps along the kerb; ground +0.12 on the pavement |
| Stairwell | `S6.stairs(night)` | rises towards the camera; the landing is at the top; night = blue paint + a warm lamp pool |
| Doctor's room | `S6.doctor()` | desk (the laptop sits in the back corner, off the sightline), shelves, blinds, couch |
| Living room | `W.living_room()` | sofa, lamp, window; `SOFA`/`SIT` in the example |
| Gym | `W.gym()` | rack, benches, mats, ceiling light strips, extras |
| Park | `W.park(mood)` | paths, steps, trees, terrace; dusk mood for sunsets |

**A new place** gets a function in `kit/sets_lib.py`:
- simple boxes and cylinders for the architecture (`W.box`, `W.cyl`, `W.toon` materials);
- Poly Haven props (`W.furniture('<asset_id>', loc, rot, scale)`), downloaded on first use into `~/shorts/_assets/polyhaven`;
- it returns `dict(spot=..., ground=<function x, y -> floor height>)`;
- a `LIGHT['<set>']` rig and a `look.MOODS['<set>']` grade.

Conventions:
- the camera looks towards +y;
- floors sit at z 0;
- characters stand near x 0.

## Light rigs (`sets_lib.LIGHT`, used by `shotkit.light(key, f0, f1)`)
- **The key.** One hard key (`key_size` at most 0.45) on the camera side, high, warm (`key_color` about (1.0, 0.85, 0.65)), casting the shadows. Interiors use 400–900 W.
- **The fill.** About a third of the key (`fill_mult` 0.45 of the rig's default), cool.
- **Ambient.** Interiors keep the world light low (`wstr` 0.25 in the mood), or the key's shadows wash out.
- **Outdoors.** The sun (`shadow='LOOK_Sun'`) at 1.6× strength, and haze to a bright horizon.
- **Night.** Blue paint, a cool key, and a warm practical lamp pool. Night is saturated blue, not dark: YAVG about 85, SATAVG about 45. Pushing saturation past about 1.0 in the mood clipped to pure electric blue (luma 14%, saturation 93%). The fix that landed in the band was `sat 0.9, gain (0.72, 0.75, 0.9)`, plus a post-grade of +40% saturation.
- **Test a light change** without editing code: `SHOT_LIGHT='{"key_mult":1.3,"fill_mult":0.6}' blender -b --python film.py -- S06 tmp preview 560`.

## The grade
`rick_mood(m)` puts the reference grade on top of each set's mood:
- gain × (0.97, 0.9, 0.9), the red push (night is exempt);
- saturation × 1.1;
- shadows lifted towards indigo (lift (1.0, 0.98, 1.05)).

Each set's mood is in `look.MOODS` (`kit/sets_lib.py`). Bands per mood are in `spec.md`. To tune a mood without editing code: `SETS_TUNE='{"hall_night":{"sat":0.9}}'`.

After a render:
1. `tools/color_check.py` measures every shot against its band and writes a ready post-grade (`grade_fix.suggested.json`).
2. `tools/grade_fix.py` applies it without re-rendering.
3. Move the same change into the mood, so the next film starts in band.

## Known gaps to fix next
- The park's grass, foliage and water still use noisy painted textures that sparkle. Swap them for plain colours plus a few large shapes.
- The reference's red push is a* +18; the June film measured about +10. The teal shirt and green walls pull it down. A new film can lean wardrobe and walls towards the reference's palette roles: indigo shadows, rust red-brown, orange or tan, mid blue (#618AD2), and a pale pink or cream highlight.
