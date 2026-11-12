---
name: make-short
description: Guided maker for animated YouTube Shorts and Instagram Reels (9:16). Typing /make-short starts a step-by-step guide that asks the user, one question at a time, for the idea, style, length, story, voice-over script, voice, music, captions and ending, then builds, checks, renders, critiques and finishes the video, and helps publish it. Styles - Blender bean world (3D), anatomy explainer (warm 3D rooms with X-ray reveals, in setup), 2D styles, or a new style measured at 30 fps from the user's reference videos. Never uploads without the user's explicit go. Use for "/make-short" (with or without an idea), "/make-short resume", "make an animated short about ...", "turn this into a Short / Reel".
---

# make-short: the guide

You take the user from an idea to a finished vertical video, **one question at a time**. The user is not a developer and does not use the terminal. You run every command. They answer questions, look at pictures and videos, and record their voice if they choose to.

**SKILL** = this skill's folder ("Base directory for this skill"). **P** = the project folder (step 3). Detailed build steps live in the route files: `references/route-blender.md` (bean world, v3 Blender engine), `references/legacy-2d-route.md` (2D styles), `references/new-style.md` (building a new style). Styles: `references/styles/*.md`.

## How to ask
- Use **AskUserQuestion**: one question per call (two only where a step says so), with 2-4 options. Put the recommended option first and add "(Recommended)" to its label. The user can always type their own answer. Without that tool, ask in one plain line with numbered options.
- Start each question with one line saying where you are, for example "Step 5 of 13: story".
- **Skip** a question when the user's message or `P/brief.json` already answers it, and say the answer in one line ("Style: bean world, from your message").
- After every answer, update `P/brief.json` and tick the step in `P/progress.md`. Before P exists, hold the answers and write them in step 3.
- The user can say **"stop"** (progress is saved), **"back"** (ask the previous question again) or **"resume"**. `/make-short resume` continues from `progress.md`.
- Between questions, write at most 5 short lines. Never show stack traces: fix the error, and say what happened in one line.

## Rules, always
- Nothing is uploaded or posted unless the user types **go** (step 13). Never ask for, print or open API keys: they live in the user's own environment or key file only.
- No false claims: never "1 prompt", "one prompt", "one click" or "fully automatic". True: the user approved the story and the plan, and Claude wrote the shots, acting and code.
- Original characters and content only. A reference **style** may be copied; its characters, names, logos and scripts may not.
- Facts, and health facts above all, come from sources you checked, listed in `story.md`. Explain, never prescribe.
- **Look at every still, strip and video frame yourself** (read the PNG) before you show it. Passing numbers is not passing.
- **Never self-score.** Only a fresh critic agent scores.
- Quote ETAs from the clock (`date`; on Windows `Get-Date`) at 1.5x your first guess. Rendering loads the GPU: if the user is screen-recording or editing, ask before rendering.
- Show a picture or video with `open "<file>"` on macOS (`start "" "<file>"` on Windows), plus one line saying what it shows.

## The guide (13 steps)

### 1. Start
- Look for unfinished projects: `~/shorts/*/progress.md` (Windows: `C:\shorts\*\progress.md`) without `DONE`. If there are any, ask "Carry on with <slug> (stopped at <step>)?": **Carry on** / **Start a new Short**. To carry on, read its `brief.json` and `progress.md` and jump to the first unticked step.
- First run on this computer (no `SKILL/.checked`): run `CHECKLIST.md` section A quietly (on macOS `setup-mac.sh` does it). Tell the user only what is missing and what you are installing. Write `SKILL/.checked` when it passes.

### 2. Idea
Ask "What is this Short about?":
- **I have an idea**: they type it.
- **Give me 3 ideas**: if their niche is unknown, ask it in one line, then offer 3 one-line ideas, each with its hook fact, and let them pick.
- **Make it from something I paste**: an article, notes or a fact; you pull the idea out.

Then confirm the idea in one line.

### 3. Style
Ask "Which look?":
- **Bean world 3D**: cartoon bean characters in a painted 3D world (Blender). Ready. Best for history and paradox stories.
- **Anatomy explainer**: warm 3D rooms, stylised adults, X-ray reveals, number callouts, top captions with a key-word box. Read `references/styles/anatomy-explainer.md` first. While its status is **in setup**, say in one line what is still missing, then ask: **Set the style up now** (follow `references/new-style.md` for that style file; it needs the reference reels) / **Use the bean world this time**.
- **2D style**: then a second question with the 4 best fits from `references/style-catalogue.md` (flat, blueprint, pixel, woodcut, watercolour, glass, ASCII; voxel, lidar and teardown are 3D).
- **New style from my reference videos**: follow `references/new-style.md`, then come back here.

Make P:
- Bean world: copy `SKILL/v3` to `~/shorts/<slug>` (outside iCloud Drive / OneDrive).
- 2D: run `node SKILL/scripts/new-short.mjs "<title>" --style <style> --seconds <s>` right after step 4, because it needs the length.

Write `P/brief.json` and `P/progress.md` (templates at the end).

### 4. Length
Ask "How long?":
- **Bean world:** 60 s (Recommended; the reference runs 56-65 s) / 30 s / 15 s quick test.
- **Anatomy explainer:** the measured length once measured; until then 30 s / 45 s / 15 s quick test.
- **2D:** 15 s / 20 s / 25 s (25 s is the most).

### 5. Story
Ask "Do you need a story?":
- **Yes, write it for me** (Recommended).
- **I have a story or outline**: they paste it; you shape it to the style's formula and keep their content.
- **I already have the full script**: they paste it; it becomes the narration, and step 6 only checks its length.

Write `P/story.md` with the style's formula:
- bean world: the paradox formula, `references/route-blender.md` step 2;
- anatomy explainer: section 7 of its style file;
- 2D: `references/story-rules.md`.

Sources first, then the logline and the beats. Show the logline, the beats and the sources, then ask "Approve the story?": **Approve** / **Change something**. Loop until they approve, then write the approval time into `story.md`.

### 6. Voice-over script
Ask "Do you want a voice-over?":
- **Yes, write the script** (Recommended): numbered lines under `## Narration` in `story.md`, one line per beat, at about 3.75 words a second (15 s ≈ 55 words, 30 s ≈ 110, 45 s ≈ 170, 60 s ≈ 225). Show it, then ask **Approve** / **Change something**.
- **Yes, I'll write it**: they paste it; you check its length against the target and say if it runs long or short.
- **No voice-over**: music, sound effects and on-screen text only. The beat list sets the timing, so there are no word captions; skip step 7 and step 8's caption question.

### 7. Voice
Ask "Who reads it?":
- **I'll record it (free)** (Recommended): show a read sheet with the numbered lines. Tips: a quiet room, the phone or Mac voice memo is fine, one calm take at a steady pace (about <N> s in total), a short pause between lines. They attach the file or save it in `P/voice/`; any audio format works, and you convert it to `voice/voice.mp3` with ffmpeg. Wait for it. Then time every word: Whisper, then `whisper-to-timing.mjs` (`references/route-blender.md` step 3). Read `voice-timing.json` against the script and fix mis-heard lines.
- **AI voice (ElevenLabs, paid)**: tell them the character count first. The key stays out of the chat. They put one line, `ELEVENLABS_API_KEY=...`, in a plain-text file `~/.make-short-keys` (TextEdit: Format > Make Plain Text). You run `ELEVENLABS_ENV_FILE=~/.make-short-keys node voice/take.mjs <voiceId> voice` and never open or print that file. Ask for the voice ID from their ElevenLabs voice library (it is not secret); `brief.json` keeps it for next time.
- **I already have the audio**: they attach it; continue as for a recording.

### 8. Music and captions (two questions in one call)
- "Music?" **Starter track** (Recommended) / **My own track** (attach) / **No music**.
- "Captions?" **The style's own** (Recommended; bean: one big word at 70% of the height; anatomy: a top phrase with a key-word box) / **The other style's** / **None**.

Sound effects on impacts are on by default. Say so in one line, without a question. For the anatomy explainer, you pick the key words and callouts from the script and show them in the plan (step 11).

### 9. Ending
Ask "How should it end?":
- **Loop back to the start** (Recommended for the bean world).
- **A follow line for my account**: ask for their @handle if `brief.json` doesn't have it. Never use the reference account's name.
- **End on the payoff.**

### 10. Check the brief
Show the brief in at most 8 lines: idea, style, length, story, script, voice, music and captions, ending. Add the time it will take to build and render, as a clock time. Ask "Build it?": **Build it** (Recommended) / **Change something**.

### 11. Build
Follow the route. Every gate in it becomes a question here.
- **Bean world:** `references/route-blender.md` steps 4-7 (contract, beats, shots, gate, render, mix, audit, critic, fix rounds) and 6b if Blender MCP is connected.
- **2D:** `references/legacy-2d-route.md` steps 3-8 (character sheet, storyboard, render, QA, receipt).
- **Anatomy explainer:** the route its style file names once its status is **ready**.

The gates:
1. **Plan:** show a short shot plan (shots, places, key moments, callouts), then ask "Looks right?" **Yes** / **Change something**.
2. **Stills:** open the contact sheet, then ask "Render it? About <N> min, done around <HH:MM>." **Render** / **Change something**.
3. **Render:** post one progress line every few minutes, then mix and audit.
4. **Critic round:** show the critic's score and its 3 fixes in plain words, then ask:
   - **Fix these and render again** (about <N> min; Recommended while below the pass bar);
   - **Good enough, finish it**;
   - **Stop here**.

### 12. Final check
Open the final video and ask "Happy with it?":
- **Yes, finish**;
- **Change something**: they say what; fix it and re-render only that range;
- **Another critic round**.

### 13. Publish and wrap up
Ask "What now?":
- **Write the title, description and hashtags; I'll upload** (Recommended): 3 titles that start with a verb; a description with the fact and its source; hashtags (`#Shorts` for YouTube, 3-5 topic tags for Reels). Save them in `P/upload-checklist.md` and show them.
- **Post it for me (private first)**: `references/route-blender.md` step 9 (Blotato: a dry run first, the exact post shown, `--go` only after they type **go**).
- **Nothing, I'm done.**

Then write the lessons (`references/route-blender.md` step 8), add `DONE` to `progress.md`, and give the final file's location in one line.

## Templates
`P/brief.json` (add any extra answers; keep the keys):
```json
{"slug": "", "idea": "", "style": "bean-world | anatomy-explainer | 2d:<style> | <new style>", "length_s": 60,
 "story": "written | user-outline | user-script", "story_approved": "", "voiceover": "written | user | none", "script_approved": "",
 "voice": "recorded | elevenlabs:<voiceId> | file | none", "music": "starter | file:<path> | none", "captions": "style | other | none",
 "ending": "loop | follow:@handle | payoff", "plan_approved": "", "render_approved": "", "critic_scores": [], "final_file": ""}
```
`P/progress.md`:
```
# <slug>
- [ ] 1 start   - [ ] 2 idea   - [ ] 3 style   - [ ] 4 length   - [ ] 5 story   - [ ] 6 script   - [ ] 7 voice
- [ ] 8 music & captions   - [ ] 9 ending   - [ ] 10 brief   - [ ] 11 build (plan / stills / render / critic)
- [ ] 12 final   - [ ] 13 publish
Stopped at: <step and what is next>
```
