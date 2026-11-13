# kit: the Blender code (copied into every project as P/kit)

| Module | What it does |
|---|---|
| `shotkit.py` | the film toolkit: timing from words (`wf`), shot ranges, `setup`, `light`, `cast`, the acting helpers (`big`, `antic`, `hop`, `tremble`, `muscles`, `pulse`), the camera grammar (`camera`), `finish` (checks, look, depth of field) and the runner (`run`) |
| `checks.py` | the pre-render checks: camera (blocked, lens against, inside, framing), clipping with a suggested move, outlines on text, camera motion |
| `lady2d.py` | the cut-out character: build, palettes (PAL, SON, DOCTOR, YOUNG_MAN), pose, face, look, blink, X-ray, hold, walk, jog, travel, shadows, face_camera |
| `flat2d.py` | the 2D shape and key-framing layer under lady2d: shapes, the lit cel material (`LIT`), keys, IK, camera baking |
| `sets_lib.py` | sets (kitchen, bathroom, street, stairs, doctor), props (jar, bag, dumbbell), outlined text, light rigs (`LIGHT`) and moods |
| `world3d.py` | the painted 3D world: boxes and materials, Poly Haven furniture, the living room, gym and park, light, the reference look (`rick_look`) |
| `look.py` | render settings, toon materials, moods (`MOODS`) and the compositor grade |
| `sets.py` | sky, terrain, trees and the painted textures (run it with python to generate them) |
| `props_lib.py` | Poly Haven downloads and placement |
| `camera_rig.py` | Camera Shakify shake |
| `style.py` | applies a style card (`P/style/style.json`) |
| `style_test.py` | four test stills of a style (cast, day wide, night, close-up) |
| `paths.py` | where shared assets live (`MAKESHORT_ASSETS`, default `~/shorts/_assets`) |

**The rig contract** (a new style's character builder must keep it, or the acting helpers and checks break):
- `build(name, at, pal, style)` returns `R` with these joints in `R['j']`: `root`, `hips`, `torso`, `head`, and `thigh_*`, `shin_*`, `arm_*`, `fore_*`, `hand_*` (`*` = `sl`, `sr`). The X-ray muscles also need `bicep_*`, `forem_*` and `quad_*`.
- `R` also holds `eyes` (a dict of name to objects), `eyes_all`, `mouth_all`, `xray`, `muscles`, `halos`, `rings` and `name`.
- Every object name starts with `<name>_`.
- Module functions: `face`, `pose`, `look`, `blink`, `xray`, `hold`, `blob_shadow`, `face_camera`, `walk`, `jog`, `travel`, `shadows`.
