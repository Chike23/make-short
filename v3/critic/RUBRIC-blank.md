# RUBRIC (blank): score a Short against a reference clip

Use: an independent critic (a fresh subagent that did NOT build the film) fills the Score and Evidence columns. The builder never scores its own film (builders rate about 2 points too high). Nothing in this file is pre-filled: every score comes from this round's frames.

Method: first read `critic/audit.md` (`python audit.py`: measured gaps against `references/reference-style.md`) and verify its FAIL lines. Then extract frames at 4 fps (360x640) from the reference and from our render into `critic/fr_ref/` and `critic/fr_our/`; make matched 1 fps sheets (reference on top, ours below); compute lapvar (Laplacian variance) and frame-to-frame step with numpy. Items marked "eye" are counted by looking at strips. Verify every critic claim at full resolution before acting on it (lesson 28).

| # | Criterion | 10/10 means | Test you can run | Score /10 | Evidence (frames, numbers) |
|---|---|---|---|---|---|
| 1 | Character acting | Squash/stretch, lean, anticipation, reaction hold 0.4-0.8 s, mouth flaps on dialogue | Per character shot, count distinct pose/expression changes per second on 4 fps strips (eye). Target >= 2/s speaking; hold >= 0.4 s after each gag | | |
| 2 | Framing mix | Screen time by size like the reference: EWS 19%, WS 17%, FS 27%, MS 13%, MCU 8%, CU 5%, INS 11%; faces 30-40% of the frame only in CU/MCU | Code the size per second (or read audit.md); compare with reference-style.md section 3 | | |
| 3 | Sharpness | Beat frames sharp; motion blur only on fast camera moves; no whips (the reference has none) | lapvar per frame; median, and fraction < 0.35 x median; flagged frames must not be within 0.3 s of a cue word | | |
| 4 | Beat on screen | The noun/verb of each narration line is visible and big at its word +-0.25 s | For each line: frame at the cue word, visible and >= 25% of the frame? hits / lines | | |
| 5 | World richness | About 9 locations per minute (7-13), 3-4 revisited; painted textures, inked geometry, 6-12 props per frame | Count locations; props in 3 random frames per 10 s; lapvar | | |
| 6 | Grade | Moods inside the measured bands (night bright and blue-saturated, interiors dimmer); warm and cool blocks; indigo shadows, never black | audit.md mood lines + signalstats SAT/YAVG per shot + eye on sheets | | |
| 7 | Comedy timing | Gag visible, then a 0.5-1 s hold on the reaction | At each gag frame: seconds before camera/shot change; is the face visible | | |
| 8 | Edit and camera | A picture shot every 4.3 s (3.1-5.1), none over 8.6 s; 8-frame crossfades, 0-2 cuts, no whips; the camera moving on 79-96% of frames, changing size about every 1.35 s inside its moves | audit.md edit/size/motion lines; strips across each transition (no dip to black) | | |
| 9 | Captions | Line centre at 70.2% height (cap top 1321, baseline 1376 at 1080), cap height 54 px, 75% one-word cards, no pop-in, a caption on every frame, on the word | audit.md caption lines; full-res crop vs a reference crop; offset vs word start | | |
| 10 | Sound sync | Impacts/pops/whooshes within +-2 frames | Waveform peaks vs impact frames; missing hits | | |

Overall = unweighted mean: ____ / 10. Pass bar: criteria 1-4 each >= 7 and mean >= 8.

## Numeric targets (fill in from the reference for THIS Short)
- Screen time by size within the reference ranges (reference-style.md section 3); faces 30-40% of the frame only in CU/MCU.
- lapvar median >= (reference median x 0.75); blur only on declared whips.
- every narration line has its noun/verb visible at >= 25% frame area at +-0.25 s.
- Speaking shots >= 2 pose/expression changes per second; 2-4 frame anticipation before each hit; 3-frame squash on impact; 12-24 frame reaction hold after each gag.
- About 9 locations per minute (scale down for a 15 s Short: >= 3 locations, >= 8 props per wide); flat ground < 25% of frame.
- Picture shot every 3.1-5.1 s; >= 79% of transitions are crossfades; no whips; still camera on <= 21% of frames.
- Captions: cap height 51-57 px at 1080 wide, baseline 1370-1382 px, centre x 534-546 px, no entry animation, 73-79% one-word cards, 3.35-3.9 narration words per second.

## Critic report format (critique-rNN.md)
Score table (above), then "Top 3 fixes" each naming a FRAME RANGE (never a shot id; ids change), the criterion, and the evidence image path. Under 400 words.
