---
name: make-short
description: Guided maker for animated YouTube Shorts and Instagram Reels (9:16, about 60 s) in the cut-out style - flat 2D characters acting in lit 3D worlds, made in Blender - with narration, one-word captions and a camera that moves like the measured reference channel. Typing /make-short starts a step-by-step guide for complete beginners - idea, style, story, script, voice, shot plan, automatic checks, a whole-film preview judged by an agent, the final render, a measured verification, and publishing. It can also learn a new animation style from two example videos (look only; the camera and pacing stay). Never uploads without the user's explicit go. Use for "/make-short" (with or without an idea), "/make-short resume", "make an animated short about ...", "turn this into a Short / Reel", "make a new style from these videos".
---

# make-short: the guide

You take the user from an idea to a finished vertical video, **one question at a time**. Assume they have never made an animation, don't use the terminal and don't read code. You run every command. They answer questions, look at pictures and videos, and record their voice if they want to.

**Names used here:**
- **SKILL** is this skill's folder ("Base directory for this skill").
- **P** is the project folder, `~/shorts/<slug>`.

**Read before building** (each is short):
- `references/spec.md`: the targets and house rules (always).
- `references/workflow.md`: the build-check-preview-render loop.
- `references/planning.md`: story to shot plan to film.py.
- `references/acting.md` and `references/world-and-light.md`: how characters move and how places look.
- `references/style-change.md`: only for a new style.
- `references/setup.md`: the first run on a computer.
- `references/troubleshooting.md`: when something breaks.

The worked example of everything is `example/june-and-the-jar/` (`film.py`, `story.md`, `voice/`).

## How to ask
- **AskUserQuestion.** One question per call, with 2–4 options. Put the recommended option first and add "(Recommended)" to its label. The user can always type their own answer. Without that tool, ask in one plain line with numbered options.
- **Say where you are.** Start each question with one line, for example "Step 5 of 14: the story".
- **Skip what's answered.** Skip a question when the user's message or `P/brief.json` already answers it, and say the answer in one line ("Style: the default cut-out look, from your message").
- **Save as you go.** After every answer, update `P/brief.json` and tick the step in `P/progress.md`. Before P exists, hold the answers and write them when you make P.
- **The user's controls.** **"stop"** saves the progress. **"back"** asks the previous question again. **"resume"** (or `/make-short resume`) continues from `progress.md`.
- **Keep it short.** Between questions, write at most 5 short lines in plain words. Never show stack traces or code: fix the error, and say what happened in one line.

## Rules, always
- **Posting.** Nothing is uploaded or posted unless the user types **go** (step 14).
- **API keys.** Never ask for, print or open an API key. If the user pastes one in the chat, don't use it: tell them to replace that key and save the new one in the key file themselves (step 6).
- **Copying.** A reference **style** may be copied: its look, never its characters, names, logos or stories.
- **Facts.** Facts, and health facts above all, come from sources you checked, listed in `story.md`. Explain, never prescribe.
- **Look before you show.** Look at every still, contact sheet and video yourself (read the PNG) before you show it. Numbers passing is not the same as looking right.
- **Never self-score.** Only a fresh judge or verifier agent scores.
- **Time.** Quote clock times (`date`) at 1.5× your estimate. Rendering loads the GPU, so ask before rendering if the user is screen-recording or editing.
- **Showing things.** On macOS, show a picture or video with `open "<file>"`, plus one line saying what it shows.
- **Honest claims.** Never say "one prompt", "one click" or "fully automatic". It is true to say: the user approved the story and the plan, and Claude wrote the shots and the code.

## The guide (14 steps)

### 1. Start
- **Unfinished projects.** Look for `~/shorts/*/progress.md` without `DONE`. If there are any, ask "Carry on with <slug> (stopped at <step>)?": **Carry on** / **Start a new Short**.
- **First run on this computer** (no `SKILL/.checked`): follow `references/setup.md`. On macOS, run `bash SKILL/setup-mac.sh`. Tell the user only what is missing and what you are installing. Write `SKILL/.checked` when it passes.
- **First Short ever.** Offer "Want to see how it works on the example first? (a 30 min preview)":
  - **Yes, preview the example** runs `python3 SKILL/tools/new_project.py june-example --example`, then steps 8–9 of `workflow.md` on it. Show the preview, then come back to step 2.
  - **No, start mine** (Recommended if they already have an idea).

### 2. Idea
Ask "What is this Short about?":
- **I have an idea**: they type it.
- **Give me 3 ideas**: ask their niche in one line if it's unknown, then offer 3 one-line ideas, each with its hook fact.
- **Make it from something I paste**: an article, notes or a fact; you pull the idea out.

Confirm the idea in one line.

### 3. Style
Ask "Which look?":
- **The cut-out look** (Recommended). Flat 2D characters with soft shading, acting in warm, lit 3D places. The example's look.
- **A saved style**: list the folders in `SKILL/styles/` other than `default`, each with its one-line description from `style.json`.
- **A new style from two example videos**: follow `references/style-change.md`. It takes about 1–2 hours with a test and your approval. Only the look changes; the camera, pacing and captions stay the same.

Make P: `python3 SKILL/tools/new_project.py <slug> [--style <name>]`. Write the answers so far into `P/brief.json`.

### 4. Story
Ask "Do you need a story?":
- **Yes, write it for me** (Recommended).
- **I have a story or outline**: shape it to the formula, keeping their content.
- **I already have the full script**: it becomes the narration, and step 5 only checks its length.

Write `P/story.md` (template in P) by `references/planning.md` sections 1–2:
- sources first;
- the logline;
- 14–16 beats for 60 s, each with a place and an action you can see.

Show the logline, the beats and the sources, then ask "Approve the story?": **Approve** / **Change something**. Loop until approved, then write the approval time into story.md.

### 5. Narration script
Write the numbered narration under `## Narration` at 3.75 words a second (60 s ≈ 225 words, 30 s ≈ 110), following the formula: hook, "You see,", middle, payoff. Show it, then ask **Approve** / **Change something**. If the user wrote it, check its length and say if it runs long or short.

### 6. Voice
Ask "Who reads it?":
- **AI voice (ElevenLabs)** (Recommended for the reference sound).
  - Tell them the character count first.
  - The key stays out of the chat. They put one line, `ELEVENLABS_API_KEY=...`, in a plain-text file `~/.make-short-keys`. In TextEdit, use Format > Make Plain Text.
  - Ask for a voice ID from their ElevenLabs voice library. It isn't secret, and `brief.json` keeps it.
  - Run `ELEVENLABS_ENV_FILE=~/.make-short-keys node voice/take.mjs <voiceId> voice`, then `python3 voice/fit_pace.py`.
- **I'll record it (free)**.
  - Show a read sheet with the numbered lines. Tips: a quiet room; a phone or Mac voice memo is fine; one calm take at a steady pace, about <N> s in total.
  - They attach the file or save it in `P/voice/`.
  - Convert it to `voice/voice.mp3`, time it with Whisper and run `voice/whisper-to-timing.mjs` (`planning.md` section 3).
- **I already have the audio**: as for a recording.

Read `voice/voice-timing.json` against the script, and fix mis-heard lines. From here on, the timing is locked.

### 7. Shot plan
Write the plan by `planning.md` section 4: one row per shot, with the cut word, the place and mood, the action and travel, and the sizes the camera lands on.
- **Keep the size budget:** wides (EWS + WS) about a third, FS about a quarter, MS at most a fifth, MCU and CU only for big reactions.
- **Name the music and endings choice in one line:** the starter track and ending on the payoff, unless they want otherwise. Sound effects on impacts are on by default.

Show the plan as a short table in plain words, with the clock time the preview will be ready. Ask "Looks right?": **Yes, build it** (Recommended) / **Change something**.

### 8. Build and check (no pictures yet)
Write `P/film.py` from the plan (`planning.md` section 5; copy patterns from the example), and `P/voice/cues.json` for the sound effects and 1–3 callouts (`planning.md` section 6). Then follow `workflow.md` steps 1–2:
1. `python3 tools/chain.py check`, then `python3 tools/plan_check.py`.
2. Fix every FAIL yourself: sizes, whips, blocked camera, clipping (apply the suggested moves), missing outlines.
3. Re-check the changed shots.

Tell the user in at most 3 lines what the checks found and fixed.

### 9. Preview and judge
Follow `workflow.md` steps 3–5:
1. `chain.py preview`, then `assemble.py preview`, then `finish.mjs`.
2. Make contact sheets and look at them yourself.
3. Start a fresh judge agent with `agents/judge.md`.

Open `out/preview.mp4` for the user. Give the judge's scores and top fixes in plain words, then ask:
- **Fix these and render the final** (Recommended): about <N> min, done around <HH:MM>.
- **Fix these and preview again**.
- **Render as it is**.
- **Change something myself**: they say what.

### 10. Fix
Apply the fixes (`workflow.md` step 6). Re-check the changed shots, and look at 2–3 preview stills of each changed moment.

### 11. Final render
1. `python3 tools/chain.py render`. Tell the user the finish time.
2. Every 15–20 minutes, run `tools/status.py`, make a contact sheet of each finished clip and look at it. Post one progress line.
3. Re-render a broken shot alone.

### 12. Finish and verify
1. Follow `workflow.md` steps 8–9: colour check and post-grade, assemble, captions and sound, `audit.py`.
2. Start a fresh verifier agent with `agents/verifier.md`.
3. Fix at once everything that needs no re-render (grade, callouts, captions, sound). List the rest for the user.

### 13. Final check
Open `out/short-final.mp4` and ask "Happy with it?":
- **Yes, finish**.
- **Change something**: fix it, and re-render only the shots it touches.
- **One more fix round**: fix the verifier's re-render items, then steps 11–12 for those shots.

Copy the final to the place the user wants. Archive it in `P/out/rounds/`.

### 14. Publish and wrap up
Ask "What now?":
- **Write the title, description and hashtags; I'll upload** (Recommended). Write:
  - 3 titles that start with a verb;
  - a description with the facts and their sources (and credits for any CC-BY assets);
  - hashtags: `#Shorts` for YouTube, 3–5 topic tags for Reels.
  Save them in `P/upload-checklist.md` and show them.
- **Post it for me (private first)**: only with a posting connection the user has set up. Do a dry run first, show the exact post, and post only after they type **go**.
- **Nothing, I'm done.**

Then add new lessons to `SKILL/references/lessons.md` (what broke, what fixed it). Add `DONE` to `progress.md`, and give the final file's location in one line.

## Templates
- `P/brief.json` (new_project.py writes it; add any extra answers, keep the keys): slug, idea, style, length_s, story_approved, script_approved, voice, music, ending, plan_approved, preview_approved, final_file.
- `P/progress.md`: 14 ticks (1 start, 2 idea, 3 style, 4 story, 5 script, 6 voice, 7 plan, 8 build + checks, 9 preview + judge, 10 fixes, 11 final render, 12 verify + quick fixes, 13 final check, 14 publish), and a line "Stopped at: <step and what is next>".
