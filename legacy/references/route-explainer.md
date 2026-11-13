# Route: anatomy explainer (Blender stills + the shot builder)

Followed from the guide in `SKILL.md` (step "Build") for the anatomy-explainer style, once `references/styles/anatomy-explainer.md` says **ready**. The guide has already settled the idea, length, story, script, voice, music, captions and ending in `P/brief.json`: do not ask again. The approvals (plan, stills, render) still stop and wait, through the guide's question format.

**The choice made for this style (12 Nov 2026): Blender makes the pictures, and the lead is animated.** The first test with stills and 2D zooms felt lifeless. Each shot is rendered as a short clip with its own camera move, plus an X-ray pass. `explainer/compose.py` joins the clips with the measured transitions and adds the layers.

## House rules (set by the user, 12 Nov 2026; they override the measured reference)
- **Library first.** Never build a character, motion, prop, room or effect from scratch when a library has it. Scratch is the fallback, and only for what no library covers. The libraries:
  - character, clothes, hair, facial expressions: **MPFB2** (MakeHuman for Blender, CC0 assets; `faceunits01` pack for expressions);
  - motion: **Mixamo** (free with an Adobe account; exercises, reactions, gestures) and **Quaternius Universal Animation Library 1 and 2** (CC0);
  - clips onto the lead: the **Retarget** add-on (Blender Extensions, Mixamo preset);
  - camera: **Camera Shakify** (recorded handheld shake) on top of every camera move;
  - rooms and props: **Poly Haven** (CC0) first;
  - X-ray anatomy: **CC-BY models from Sketchfab** (credit only). List every CC-BY asset in `P/credits.md` and paste it into the video description.
- **She doesn't talk.** No lip-sync and no breathing layer. She reacts and acts to fit the story: one reaction or action per narration beat (shocked at a bad number, nods at good news, starts the exercise when the voice names it, celebrates the result). Blinks and a facial expression per beat are fine.
- **Lively.** No idle hold longer than about 1.5 s. Prefer big, readable mocap moves over small gestures.
- **The camera moves on every frame.** Every shot has a move (push in, pull out, arc, pan, tilt or dolly), plus handheld shake from Camera Shakify. Never locked off. Punch in on the key word of a line.
- **2D characters in a 3D world (being tested, 12 Nov 2026).** The lead is a flat cut-out puppet (`explainer/lady2d.py` on `explainer/flat2d.py`), lit by the room (`flat2d.MODE = 'lit'`), with a soft drop shadow (`lady2d.blob_shadow`). The room is 3D in the skill's own toon look (`explainer/world3d.py` on `v3/lib/look.py`: cel shading, ink lines, painterly grade), with Poly Haven furniture repainted toon. Example: `explainer/scene_2d10.py`.
- **Characters are always head-on to the camera.** As the camera moves, they turn about the vertical axis to face it on every frame (`lady2d.face_camera`). Keep camera moves within about 15° of her front, so the turn never shows.
- **Render speed:** no world fog (it was most of the frame time) and shadows on the key light only. That's about 1.5-3 s a frame at 720x1280, 12 samples, scaled to 1080x1920 afterwards.

## 0. Project
- Copy `SKILL/v3` to `~/shorts/<slug>` (P), and `SKILL/references/styles/anatomy-explainer.targets.json` to `P/critic/targets.json`.
- Blender runs on the user's computer. Drive it through the Blender MCP (`execute_blender_code`). If it can't connect, ask the user to open Blender and start the MCP add-on's server.

## 1. Shot plan (after the voice is timed)
Write `explainer/shots.json` (format: `v3/explainer/README.md`). Aim for the measured edit:
- a new picture about every 3.9 s (most 1-8 s); several narration lines can share a shot;
- transitions: mostly `crossfade`, then `push_up` / `push_down` and `cut`, some `fade`, the odd `dip`;
- camera: moving in every shot (house rule above); vary the move between neighbouring shots, and punch in on key words;
- the lead: one action or reaction per narration beat (house rule above), named in the plan next to the line it answers;
- shot content: about 45% the lead in a room (normal or X-ray), 35% props and infographics on the dark stage, 15% medical close-ups, the phone call to action at the end;
- an X-ray reveal is a layer that fades in on the word that names it ("bones", "muscle");
- a stat moment is a `dim` layer plus a `stat` or `counter` callout in `voice/cues.json`.

Also write `voice/cues.json`:
- `"captionStyle": "explainer"`;
- `keyWords`: one key word in most phrases, the term being taught;
- `overlays`: stat, counter, note, tag; plus small source credits as `note`s next to the image they belong to.

Show the plan in plain words and ask "Looks right?".

## 2. Render the shots in Blender (clips; stills for props)
Library setup, once per computer (all into `assets/libs`, then installed in Blender):
- extensions: MPFB2, Camera Shakify, Retarget (`bpy.ops.extensions.package_install_files`);
- MPFB packs: `makehuman_system_assets`, `shirts01`, `pants01`, `shoes01`, `faceunits01` (`bpy.ops.mpfb.load_pack`). Use the `files.makehumancommunity.org` mirror: `files2` crawls at about 15 KB/s.

Building blocks:
- `explainer/lead_mpfb.py`: the lead from MPFB (`build_lead()`), facial expressions per beat (`express()`), blinks.
- `explainer/props_lib.py`: Poly Haven models (`get_polyhaven()`, `place()`, `furnish_living_room()`).
- `explainer/camera_rig.py`: a moving camera per shot (`shot_cam()`: push, pull, orbit, crane, pan, punch-ins, Camera Shakify shake). Call `prep_for_background()` before saving render jobs.
- Mixamo clips on the lead (MPFB's documented route): export her once with `bpy.ops.mpfb.reduced_doll()` plus an FBX export, then upload that FBX to Mixamo. Download each clip **without skin**, FBX, 30 fps, "In Place" where offered. Import it, then snap it onto her with `bpy.ops.mpfb.map_mixamo()` (MPFB's "snap to mixamo") and bake.

- Follow `explainer/scene_anim14.py`: `build()`, then `save_jobs()`, then `launch()`. Background renders run at about 1.1 s a frame at 720x1280. Poll `renders/anim/render.log` until `ALL_DONE`, then stage the clips.
- Pick a library clip for each beat: a reaction for a surprising fact, the real exercise clip when the voice names it, a celebration for the payoff. Search Mixamo first, then Quaternius.
- For a motion no library has, film it on a phone, then convert it with Rokoko Vision (free, single camera). Hand-keyed motion is the last resort.

### Stills (props, stage shots)
- Build or reuse the sets and the lead from the Blender kit for this style (see the style file, section 6). Every render: 1350x2400, EEVEE.
- For each shot, render to `P/renders/`:
  - `<id>.png`: the base;
  - `<id>_<layer>.png` (RGBA, transparent background): each layer pass from **the same camera**, for example the X-ray organs with the body hidden or ghosted.
- Keep the scene code in `P/explainer/scene.py` (source of truth) and run it through the MCP. Changes made only in the open .blend are lost.
- Long jobs: render shot by shot (one MCP call per shot or a few shots). A single frame is quick, but a 25-shot batch in one call can time out.

## 3. Gate
1. `python3 explainer/compose.py --stills` writes one still from the middle of each shot and one at each transition.
2. Look at every still yourself:
   - the subject is readable and the key prop is big;
   - the X-ray layer lines up with the body;
   - nothing important sits in the top 20% (the captions' band) or behind the callouts.
3. Show the contact sheet and ask "Render it? (about N min)".

## 4. Render, mix, check
1. `python3 explainer/compose.py`, then `node voice/finish.mjs`: `out/short-v3-final.mp4`.
2. `python3 audit.py`: it uses `critic/targets.json` (this style's numbers). Fix every FAIL that isn't a deliberate choice.
3. Then the critic and fix rounds as in `references/route-blender.md` steps 6.3-7. The critic compares against frames of the reference reels. The fixes are edits to `shots.json`, `cues.json` or the scene code, then a re-render of only the affected stills.
