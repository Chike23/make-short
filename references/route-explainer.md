# Route: anatomy explainer (Blender stills + the shot builder)

Followed from the guide in `SKILL.md` (step "Build") for the anatomy-explainer style, once `references/styles/anatomy-explainer.md` says **ready**. The guide has already settled the idea, length, story, script, voice, music, captions and ending in `P/brief.json`: do not ask again. The approvals (plan, stills, render) still stop and wait, through the guide's question format.

**The choice made for this style (12 Nov 2026): Blender makes the pictures, and the lead is animated.** The first test with stills and 2D zooms felt lifeless. So the lead is now rigged on the free Quaternius animation library (`explainer/rig.py`). She plays its clips (talking gestures, idle, walk, sit) plus layered actions (arm curls), and she blinks and moves her mouth with the voice. Each shot is rendered as a short clip with its own camera move, plus an X-ray pass. `explainer/compose.py` joins the clips with the measured transitions and adds the layers. Props and infographic shots can still be stills with a slow zoom.

## 0. Project
- Copy `SKILL/v3` to `~/shorts/<slug>` (P), and `SKILL/references/styles/anatomy-explainer.targets.json` to `P/critic/targets.json`.
- Blender runs on the user's computer. Drive it through the Blender MCP (`execute_blender_code`). If it can't connect, ask the user to open Blender and start the MCP add-on's server.

## 1. Shot plan (after the voice is timed)
Write `explainer/shots.json` (format: `v3/explainer/README.md`). Aim for the measured edit:
- a new picture about every 3.9 s (most 1-8 s); several narration lines can share a shot;
- transitions: mostly `crossfade`, then `push_up` / `push_down` and `cut`, some `fade`, the odd `dip`;
- camera: about half the shots locked off; the rest push in (2-6% a second) or pull out a little;
- shot content: about 45% the lead in a room (normal or X-ray), 35% props and infographics on the dark stage, 15% medical close-ups, the phone call to action at the end;
- an X-ray reveal is a layer that fades in on the word that names it ("bones", "muscle");
- a stat moment is a `dim` layer plus a `stat` or `counter` callout in `voice/cues.json`.

Also write `voice/cues.json`:
- `"captionStyle": "explainer"`;
- `keyWords`: one key word in most phrases, the term being taught;
- `overlays`: stat, counter, note, tag; plus small source credits as `note`s next to the image they belong to.

Show the plan in plain words and ask "Looks right?".

## 2. Render the shots in Blender (clips; stills for props)
- Follow `explainer/scene_anim14.py`: `build()`, then `save_jobs()`, then `launch()`. Background renders run at about 1.1 s a frame at 720x1280. Poll `renders/anim/render.log` until `ALL_DONE`, then stage the clips.
- Pick a clip per shot to match what she says: `Idle_Talking_Loop` while she explains, `Idle_Loop` plus `curl()` for an exercise, `Walk_Loop` to enter.
- For a motion the library lacks, film it on a phone, then convert it with Rokoko Vision (free, single camera). Or layer an action on top, as `curl()` does.

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
