# make-short: animated YouTube Shorts with Claude

A free Claude Code skill. Type `/make-short <your idea>` and Claude writes a short story, makes the voice (your own recording, or ElevenLabs), builds 2D bean characters in a 3D Blender world with code, renders a 9:16 Short with sound and captions, then a fresh critic agent scores it so you can fix the weak moments.

Made for the NoCodeHack video "make animated Shorts with Claude". You review the result before anything is posted; the skill never uploads on its own.

## Install
Prerequisites (Blender 5.x, Node.js, Python 3, ffmpeg, Git Bash) and the full steps are in [INSTALL.md](INSTALL.md). Short version, in PowerShell from the folder that contains `make-short`:
```
Copy-Item -Recurse -Force .\make-short "$env:USERPROFILE\.claude\skills\make-short"
```
Reopen Claude Code, then type `/make-short a 15 second Short about <your topic>`.

## Keys
None are needed for the free route (record your own voice). For an AI voice, set `ELEVENLABS_API_KEY` in your own terminal, never in the chat. Auto-posting (optional) uses your own Blotato key the same way.

## License
MIT (see LICENSE). Bundled third-party files: see THIRD-PARTY.md.
