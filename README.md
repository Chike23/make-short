# make-short

A Claude Code skill that makes animated YouTube Shorts and Instagram Reels (9:16, about 60 s). Flat 2D cut-out characters act out a narrated story in lit 3D worlds, made in Blender. The camera, edit, shot sizes, captions and pacing are measured frame by frame from a successful reference channel.

Type **/make-short** in Claude Code and it walks you through everything, one question at a time: idea, look, story, script, voice, shot plan, checks, a preview with an agent's review, the final render, a measured check, and the title and description. You don't need to know animation, Blender or the terminal.

## What a film gets
- **Characters that act.**
  - Drawn on twos, with anticipation, overshoot and settle on every big move, and a reaction on every beat.
  - They travel in every shot and always turn to face the camera.
  - No lip-sync: they act it out.
- **A camera with a grammar.** A quick, eased move to each new framing, then a very slow drift the same way (a push-in or a pan) until the next one. It never whips and never sits dead.
- **The reference's edit.**
  - About 4 s shots joined by 8-frame dissolves.
  - 7–13 places.
  - A shot-size mix led by wide and full shots.
  - One-word captions with black outlines at exactly the reference's size and place.
  - Narration at 3.75 words a second.
- **Worlds and light.** Warm, smoothly lit sets with Poly Haven furniture, one strong key light with real shadows, indigo shadows, haze, and shallow depth of field.

## How it stays fast and right
1. **Checks before any picture** (seconds). Every shot is built in the background and checked:
   - the camera blocked or pressed against something;
   - a character passing through furniture, with the exact move that fixes it;
   - text without an outline;
   - the camera's speed frame by frame;
   - the whole film's shot-size mix against the spec.
2. **One quick preview of the whole film** (about 30 min), reviewed once by an independent judge agent for fluid movement, energy, charisma, staging, camera, light and readability.
3. **One final render** (about 1.5 h on an M1, unattended). Then a verifier agent measures it against the spec. Colour, caption and callout fixes are applied without re-rendering.

## New styles
Give it two example videos in a style you like. It measures their look, writes a style card, rebuilds the characters' colours and shading and the worlds' materials and grade, and shows you a side-by-side test. The camera, pacing, captions and acting stay the same. Styles are saved and can be reused.

## What's in the folder
| Folder | What |
|---|---|
| `SKILL.md` | the guide Claude follows |
| `references/` | the spec (`spec.md`) and how to work: workflow, planning, acting, worlds and light, style change, setup, troubleshooting, lessons, the measured reference |
| `agents/` | briefs for the judge, the verifier and the style analyst |
| `kit/` | the Blender code: characters (`lady2d.py`), sets (`sets_lib.py`, `world3d.py`), the shot toolkit and camera grammar (`shotkit.py`), the checks (`checks.py`), styles (`style.py`) |
| `tools/` | new projects, render chains, plan and colour checks, post-grade, assembly, audit, style measurement |
| `voice/` | ElevenLabs takes, pace fitting, Whisper timing, captions, sound effects and the final mix |
| `example/june-and-the-jar/` | a complete 62 s film to learn from: story, film.py, voice and timing |
| `styles/` | saved looks (`default` is the house look) |
| `template/` | the starting film.py, story.md and cues.json |
| `measure/` | tools that measured the reference videos frame by frame |
| `legacy/` | the older routes (bean world, browser 2D styles, the MPFB explainer), kept for reference |

Install: see `INSTALL.md`.
