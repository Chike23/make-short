# Acting: making cut-out characters fluid, lively and watchable

The characters are flat 2D cut-out puppets (`kit/lady2d.py` on `kit/flat2d.py`) standing in 3D sets. They are lit by the set's lights, cast a soft shadow, and always turn to face the camera. They never talk: no lip-sync and no breathing. They act the story out.

## The rules
1. **On twos.** A new pose every 2 frames, like the reference. `finish()` steps every character curve, except the root's travel across the set (x/y). The camera, the world and the travel stay on ones: stepping the travel made her size pulse as the camera tracked her.
2. **One big readable move per beat.** Use `big(R, f, spec, ...)`:
   - **Anticipation.** 4–8 frames: a small squash and a counter-move the other way.
   - **Move.** It overshoots the target by 10–20%.
   - **Hold** (optional). Keeps the peak for a beat.
   - **Settle.** 8–14 frames onto the target.
   - **Face and eyes.** The face lands with the move, and the eyes lead by 3 frames (`look=`).
   - **Easing.** All Bezier eases, never BACK: BACK easing popped on twos.
3. **Eyes first.** `L.look(R, f - 3, dx, dz)` before every turn or reaction.
4. **Faces per beat**, one clear emotion: `L.face(R, f, eyes, mouth, brows)`.
   - eyes: open, wide, closed, happy
   - mouth: smile, grin, O, frown, flat
   - brows: neutral, worried, determined, surprised, happy
   - **Strain:** eyes closed + frown + determined brows. A closed-eye grin reads as laughing.
5. **Blinks.** `finish()` adds them every 2–4 s at irregular times, never within 8 frames of a face change, and always back to the face she had.
6. **Holds never freeze.** `life()` adds a slow irregular drift on the head and torso. It is not breathing.
7. **Impacts.** A 3-frame hit-stop (the pose holds) before the recoil. Add a sound effect on the impact frame, not on the word.
8. **Travel in every shot.** `L.walk`, `L.jog`, `L.travel`, a climb (`_stairs_climb` in the example), stepping back from a shock, crossing to another character.
   - Walks are front-facing cycles (`step` 8–11, bob 0.02); a jog has a shorter step (5–6) and a bigger bob.
   - Give the path a curve, not a straight line across the frame.
9. **Reactions are on screen.** Every reaction word (the shock, the pride, the eye-roll) must be in frame at its word. Use a two-shot key or an MCU on it. In the example the judge caught "it wasn't a pill?!" happening off screen.
10. **After every gag, a reaction** of at least half a second on a face.

## Props
- **In hand.** `hold_prop(R, obj, side, offset)` keeps a prop upright (COPY_ROTATION to the root) however the arm turns. Without that, the jar ended up lying sideways.
- **Beside the face, not over it.** The doctor's note covered her face until it moved to `ik_sr (0.22, 1.34)`.
- **Swaps.** `swap(a, b, f)` swaps two props on a frame (a sealed jar for an open one).
- **Labels.** In-world text uses `sets_lib.text` (outlined by default). Dumbbells come from `sets_lib.dumbbell(name, kg, colour)`.

## Staging that reads in 9:16
- **Faces.** Keep faces out of the caption band (66–74% down the frame); `checks.py` warns.
- **Depth.** Put characters at different depths. A person in front and one behind reads better than a line-up.
- **Sitting.** For a sofa or a desk, sink the character into the seat (the example's `SIT = -0.55` in the sofa) and allow the overlap in `FILM['allow']`.
- **Clipping.** A cut-out must not pass through set objects (a rail across her chest, a table through her legs). `checks.py` finds every overlap and suggests the smallest move that clears it, for example "move june 0.3 m left". Apply the move to her start position or walk path, then run the check again.
- **Stairs.** Put the camera on the upper treads looking down the flight, so the handrail never crosses her body.

## Cast helpers (kit/shotkit.py)
| Helper | What it does |
|---|---|
| `cast(name, at, pal, style, face, f0, f1)` | builds a character at (x, y[, z]); style 'lady' or 'man' |
| `big(R, f, spec, antic, move, over, settle, squash, hold, face, look)` | one big move by the rules above |
| `antic(R, f)` | a small squash before a move |
| `hop(R, f, h)` | a happy hop: anticipation, up, squash on landing, settle |
| `tremble(R, f0, f1, joint)` | a shaking limb (strain) |
| `muscles(R, f0, f1, sx, sz)` and `pulse(R, f, k)` | X-ray muscles grow or shrink, and pulse (use `L.xray(R, f0, f1)` to show the X-ray) |
| `L.pose(R, f0, f1, spec)` | a pose between two frames |
| `L.walk / L.jog / L.travel` | travel along a path, riding a ground function |
| `hold_prop`, `swap`, `hide_until` | props |

**Pose spec keys:**
- `arm_sl` / `arm_sr` = (outward, elbow, wrist) in degrees, or `ik_sl` / `ik_sr` = a hand target (x, z) in rest coordinates.
- `head`, `torso`, `hips` = tilt in degrees.
- `lift` = root height; `squash` = (sx, sz).
- `front_sl` / `front_sr` = the arm in front of the face.
- Screen-left (`sl`) is the character's right arm.
