# Setup: the first run on a computer

The user doesn't need to know any of this. Run it for them, and tell them only what is missing and what you are installing.

## What the skill needs
| Need | Why | How (macOS: `bash SKILL/setup-mac.sh` does all of it) |
|---|---|---|
| Blender 5.x | builds and renders every shot, in the background | the .dmg from blender.org, dragged to Applications; open it once by hand so macOS allows it |
| ffmpeg | joins clips, adds sound and captions, measures colour | `brew install ffmpeg` |
| Node.js 22+ | voice (ElevenLabs), captions and the final mix | `brew install node` |
| Python 3 with numpy, pillow, opencv-python | the tools, the checks, the textures | a venv at `~/.venvs/shorts`; `PYTHON` points at it |
| Camera Shakify (Blender extension) | the handheld shake on every camera | Blender > Edit > Preferences > Get Extensions > "Camera Shakify" > Install. Without it the kit uses a simpler noise shake |
| Internet, the first time | Poly Haven furniture downloads into `~/shorts/_assets/polyhaven` | automatic |
| Arial Black (optional) | the caption font | ships with macOS; without it, captions use the bundled Inter |
| Whisper (optional) | timing your own voice recording | `setup-mac.sh --whisper` |
| ElevenLabs account (optional) | the AI narrator | the user's own key in `~/.make-short-keys` (step 6 of the guide) |
| Blender MCP (optional) | quick looks at a shot in the open Blender | not needed for building or rendering: all renders run in the background |

Memory: two render chains in parallel suit 16 GB. With 8 GB, use `--chains 1` (twice as long).

## Folders
- **The skill.** `~/.claude/skills/make-short` (SKILL).
- **Projects.** `~/shorts/<slug>` (P). Keep it out of iCloud Drive and OneDrive, because syncing fights with renders.
- **Shared assets.** `~/shorts/_assets/`: textures in `tex/` (generated once), Poly Haven downloads in `polyhaven/`. Set `MAKESHORT_ASSETS` to move it.

## Check it worked
1. `bash SKILL/setup-mac.sh` ends with "All set".
2. Make a test project: `python3 SKILL/tools/new_project.py smoke --example`, then `cd ~/shorts/smoke`.
3. Build and check one shot (about 1 minute): `/Applications/Blender.app/Contents/MacOS/Blender -b --python film.py -- S03 smoke_out preview 300`. Expect a `BUILT S03` line, `CHECK` lines and `smoke_out/stills_S03/still_0300.png`. Look at the still: a high street, June walking with shopping bags.
4. Write `SKILL/.checked`.

## Windows and Linux
- **The kit runs anywhere Blender 5 runs.** Install the same tools by hand: Blender, ffmpeg, Node, and Python with numpy, pillow and opencv-python.
- **Set the paths.** Set `BLENDER` to the Blender executable, and `PYTHON` to the Python with pillow.
- **Projects.** Keep them outside OneDrive, for example `C:\shorts\<slug>`.
- **Untested.** `chain.py` starts its chains with `/bin/sh`; on Windows, run it inside Git Bash or WSL.
