# Install make-short

> **Claude Code only.** The skill runs Blender, Node and ffmpeg on your own computer, so it doesn't work as a claude.ai Skills upload. Install it in Claude Code.

## macOS: one command
You need Homebrew first (one command from https://brew.sh). Then, in Terminal:
```bash
git clone https://github.com/Chike23/make-short ~/.claude/skills/make-short && bash ~/.claude/skills/make-short/setup-mac.sh
```
The script:
- installs ffmpeg, Node and Python;
- checks Blender 5;
- makes the Python environment and the painted textures;
- turns on the Camera Shakify add-on;
- runs a background Blender test.

It is safe to run again. If Blender is missing, it tells you where to download it.

Then open Claude Code and type **/make-short**. The guide asks you one question at a time and does everything else.

## Update
```bash
cd ~/.claude/skills/make-short && git pull && bash setup-mac.sh
```

## Other systems
See `references/setup.md`: Windows and Linux need the same tools installed by hand.

## Keys
The only key is optional: an ElevenLabs key for the AI narrator. Put one line, `ELEVENLABS_API_KEY=...`, in a plain-text file `~/.make-short-keys`. Never paste a key into the chat. Without a key, record the narration yourself; the guide shows you how.
