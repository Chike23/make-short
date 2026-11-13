# Workflow: from an approved plan to the finished video, fast

The order is built so that problems are caught when they are cheap:
1. Checks that take seconds, before any picture.
2. One quick low-quality preview of the whole film, judged once by an agent.
3. One final render, then a measured check with fixes that need no re-render.

Shot-by-shot test renders judged one batch at a time were slower: five rounds took an evening. A problem found only in the final render (a blocked camera, a wrong grade) costs a full-quality re-render of that shot.

Every command runs in the project folder P (`cd ~/shorts/<slug>`). `chain.py` finds Blender by itself: on macOS at `/Applications/Blender.app`; elsewhere set `BLENDER=/path/to/blender`. Where this file says `blender -b ...`, macOS means `/Applications/Blender.app/Contents/MacOS/Blender -b ...`.

| Step | Command | Time on an M1 (60 s film) |
|---|---|---|
| 1. Build every shot + checks | `python3 tools/chain.py check` | ~10 min |
| 2. Film-level check | `python3 tools/plan_check.py` | seconds |
| 3. Whole-film preview | `python3 tools/chain.py preview` | ~25–35 min |
| 4. Assemble + captions | `python3 tools/assemble.py preview` then `node voice/finish.mjs out/preview-silent.mp4` | 2 min |
| 5. Judge (one pass) | the judge agent, `agents/judge.md` | ~15 min |
| 6. Fix, re-check changed shots | `python3 tools/chain.py check S04 S08` | minutes |
| 7. Final render | `python3 tools/chain.py render` | ~1.5 h, unattended |
| 8. Assemble, colour, captions | `assemble.py`, `color_check.py`, `grade_fix.py`, `finish.mjs` | 5 min |
| 9. Verify + quick fixes | `tools/audit.py` + the verifier agent, `agents/verifier.md` | ~15 min |

## 1. Build every shot and run the checks (no pictures)
- **Run.** `python3 tools/chain.py check` builds each shot in a background Blender. Each shot runs `checks.py` and writes `checks/Sxx.json`.
- **Progress.** `python3 tools/status.py checks_run` shows progress and every CHECK line.
- **Errors.** A shot that fails to build shows a Traceback in `checks_run/chainN.log`. Fix it and run that shot again: `chain.py check S05`.

## 2. Check the whole film against the spec
- **Run.** `python3 tools/plan_check.py` adds up the edit, the shot-size mix, the camera motion and every shot check. It writes `checks/plan_check.md`.
- **Fix every FAIL before rendering:**
  - **MS over 20%, or wides under 25%.** Re-plan sizes: open places on EWS or WS, and keep MS for passing through (`planning.md`).
  - **A whip, or "camera keys too close".** Space the keys or drop one. A key needs about 33 frames per frame-height of change.
  - **Lens against, inside or blocked.** Move the camera key (`az`, `el`, `dx`, `cam=`) or move the prop.
  - **Clipping.** Each event carries a suggested move. For example "move june 0.3 m left (dx -0.3, dy 0.0)": shift her start or walk path by that much. If the overlap is on purpose (sitting in a sofa), add it to `FILM['allow']`.
  - **Text without outline.** Make the text with `sets_lib.text` (it outlines by default).
- **WARNs.** Framing warnings and motion slightly out of range: look at them in the preview, and leave deliberate ones.
- **After fixing.** Re-run only the changed shots (`chain.py check S03 S08`), then `plan_check.py`.

## 3. Preview the whole film
- **Run.** `python3 tools/chain.py preview` renders every shot at 360×640 with 6 samples, into `preview/`.
- **Two chains.** It runs two Blender processes in parallel (`--chains 2`), which suits 16 GB of memory.
- **Your edits are safe.** The code is frozen into `preview/_code/` first, so you can keep working while it runs.

## 4. Assemble and caption the preview
- **Commands:**
  - `python3 tools/assemble.py preview` writes `out/preview-silent.mp4`.
  - `node voice/finish.mjs out/preview-silent.mp4` adds the voice, captions and sound effects, and writes `out/preview.mp4`.
  - `python3 tools/color_check.py preview` gives a first colour table.
- **Look yourself.** Make contact sheets with `bash tools/sheet.sh preview/S03_0290-0417.mp4 10 critic/S03.png` and look at every one before the judge does.

## 5. One judge pass
- **Start a fresh agent** with `agents/judge.md`. It gets the preview, the contact sheets, `checks/*.json`, `checks/plan_check.md`, `story.md` and `film.py`.
- **What it scores:**
  - fluid movement
  - energy and charisma
  - staging and clipping (it confirms each clipping event and its position fix)
  - the camera grammar (fast move, slow drift)
  - framing, light and colour, and readability
- **What it returns.** A ranked fix list in the terms of `film.py`, for example "S08: key at `wn + 3` az -12 → -20" or "S16: start June at x -0.2 instead of 0.1".
- **Never self-score.** Only a fresh agent scores, so the work isn't grading itself.
- **Show the user.** Show the preview and the judge's top fixes in plain words, then ask:
  - **Fix and render the final** (Recommended);
  - **Fix and preview again**;
  - **Render as is**.

## 6. Fix
- **Apply every fix.** Re-run `chain.py check` on the changed shots, then `plan_check.py`.
- **When to preview again.** For a changed moment, render 2–3 preview stills only: `blender -b --python film.py -- S08 tmp preview 790 820`. Run a full preview again only if the user asks or more than a third of the shots changed.

## 7. Final render
- **Run.** `python3 tools/chain.py render` renders 720×1280 at 12 samples into `render/`. That is about 3.5 s a frame with two chains on an M1, so about 1.5 h for 60 s.
- **Tell the user** the clock time it will finish (`date`, then 1.5× your estimate). Ask before rendering if they are screen-recording or editing: rendering loads the GPU.
- **Poll.** Run `python3 tools/status.py` every 15–20 minutes. Make a contact sheet of each clip as it lands and look at it.
- **A broken shot** is fixed and re-rendered alone: `chain.py render S08`.

## 8. Assemble, colour and captions
1. `python3 tools/color_check.py render` writes `grade_fix.suggested.json` for shots outside their mood band. Review it, copy the lines you agree with into `grade_fix.json`, and run `python3 tools/grade_fix.py`. That gives `render_graded/`, with no re-render.
2. `python3 tools/make_shots.py render_graded`, then `python3 tools/assemble.py render_graded`, then `node voice/finish.mjs out/short-silent.mp4` writes `out/short-final.mp4`.
3. Carry each grade fix back into that set's mood in `kit/sets_lib.py` (`look.MOODS`), so the next film starts right.

## 9. Verify
1. `python3 tools/audit.py` checks the finished video against the spec and writes `critic/audit.md`.
2. Start a fresh verifier agent with `agents/verifier.md`. It measures the video against `spec.md` and the house rules, and returns the 5 most important fixes.
3. **Fix now** whatever needs no re-render:
   - grade: `grade_fix.json`
   - caption and callout positions or timing: `voice/cues.json`
   - sound effects
   Re-run step 8.
4. **List the rest** for the user as "needs a re-render". Re-render only if they ask.
5. Add what you learned to `SKILL/references/lessons.md`.

## Rules that keep it fast and safe
- **Background renders only.** The Blender MCP call times out at about 80 s, so every render runs through `chain.py` (`blender -b`). Use the MCP only for quick looks at a shot in the open Blender.
- **Never edit a file a running chain reads.** `chain.py` freezes the code into `_code/` for this reason.
- **Two chains, not more,** on a 16 GB Mac.
- **Look at every still and sheet yourself** before showing it. Numbers passing is not the same as looking right.
- **Archive every round** (`out/rounds/`), so earlier versions survive.
