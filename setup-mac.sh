#!/bin/bash
# One-time macOS setup for the make-short skill. Safe to re-run: every step checks first and skips what is there.
#   bash ~/.claude/skills/make-short/setup-mac.sh            # core setup
#   bash ~/.claude/skills/make-short/setup-mac.sh --whisper  # + local transcription, for recording your own voice
# Touches only: Homebrew packages, ~/.venvs/shorts, ~/shorts/_assets and one block in ~/.zshrc.

WHISPER=0
for a in "$@"; do case "$a" in --whisper) WHISPER=1;; esac; done
SKILL="$(cd "$(dirname "$0")" && pwd)"
VENV="${SHORTS_VENV:-$HOME/.venvs/shorts}"
OK=""; BAD=""
ok()  { echo "  ok   $1"; OK="$OK\n  ok   $1"; }
bad() { echo "  MISSING  $1"; BAD="$BAD\n  MISSING  $1"; }
step(){ echo; echo "== $1"; }
[ "$(uname -s)" = Darwin ] || { echo "setup-mac.sh is for macOS. Elsewhere follow references/setup.md."; exit 1; }

step "Homebrew"
BREW="$(command -v brew)"
for c in /opt/homebrew/bin/brew /usr/local/bin/brew; do [ -z "$BREW" ] && [ -x "$c" ] && BREW="$c"; done
[ -n "$BREW" ] || { echo "Homebrew is not installed. Install it from https://brew.sh (one command), then run this again."; exit 1; }
eval "$("$BREW" shellenv)"; ok "brew"

step "ffmpeg, node, python"
need() { if command -v "$2" >/dev/null 2>&1; then ok "$2"; else echo "  installing $1 ..."; "$BREW" install "$1" && ok "$2 (installed)" || bad "$2 (brew install $1 failed)"; fi; }
need ffmpeg ffmpeg; need node node
BP="$("$BREW" --prefix)/bin/python3"
[ -x "$BP" ] && ok "python3" || { "$BREW" install python && ok "python3 (installed)" || bad "python3"; }

step "Blender 5"
BL="$(ls -d /Applications/Blender*.app/Contents/MacOS/Blender "$HOME"/Applications/Blender*.app/Contents/MacOS/Blender 2>/dev/null | sort | tail -1)"
if [ -z "$BL" ]; then bad "Blender (download the macOS .dmg from https://www.blender.org/download/ and drag it to Applications)"
else BV="$("$BL" --version 2>/dev/null | head -1)"; case "$BV" in "Blender 5."*|"Blender 6."*) ok "$BV";; *) bad "Blender 5.x (found ${BV:-an unknown version})";; esac; fi

step "Python packages (venv at $VENV)"
[ -x "$VENV/bin/python" ] || "$BP" -m venv "$VENV"
PKGS="numpy pillow opencv-python"; [ "$WHISPER" = 1 ] && PKGS="$PKGS openai-whisper"
"$VENV/bin/python" -m pip install -q --upgrade pip && "$VENV/bin/python" -m pip install -q $PKGS && ok "packages: $PKGS" || bad "pip install $PKGS"

step "Shell profile (~/.zshrc)"
if grep -q "# make-short (setup-mac.sh)" "$HOME/.zshrc" 2>/dev/null; then ok "~/.zshrc block already there"
else
  { echo ""; echo "# make-short (setup-mac.sh)"; echo "export PYTHON=\"$VENV/bin/python\""; echo "export PATH=\"$VENV/bin:\$PATH\""; } >> "$HOME/.zshrc" \
    && ok "PYTHON and the venv added to ~/.zshrc (new Terminal windows pick it up)"
fi
export PYTHON="$VENV/bin/python"; export PATH="$VENV/bin:$PATH"

step "Assets and textures (~/shorts/_assets)"
mkdir -p "$HOME/shorts/_assets/polyhaven"
"$VENV/bin/python" "$SKILL/kit/sets.py" >/dev/null 2>&1 && ok "painted textures generated" || bad "texture generation (python kit/sets.py)"

step "Blender add-on: Camera Shakify (handheld camera shake)"
if [ -n "$BL" ]; then
  R="$("$BL" -b --python-expr "import addon_utils,sys
ok=False
for m in ('bl_ext.user_default.camera_shakify','camera_shakify'):
    try: addon_utils.enable(m, default_set=True, persistent=True); ok=True; break
    except Exception: pass
print('SHAKIFY', ok)" 2>/dev/null | grep SHAKIFY)"
  case "$R" in *True*) ok "Camera Shakify";; *) bad "Camera Shakify: in Blender, Edit > Preferences > Get Extensions, search 'Camera Shakify', Install (the kit falls back to a simple shake without it)";; esac
fi

step "Fonts and Claude Code"
ls "/System/Library/Fonts/Supplemental/Arial Black.ttf" /Library/Fonts/Arial\ Black.ttf "$HOME/Library/Fonts/Arial Black.ttf" >/dev/null 2>&1 \
  && ok "Arial Black (captions)" || echo "  note  no Arial Black: captions use the bundled Inter instead"
command -v claude >/dev/null 2>&1 || [ -x "$HOME/.local/bin/claude" ] && ok "Claude Code" || bad "Claude Code (https://docs.claude.com/en/docs/claude-code)"

step "Smoke test"
[ -n "$BL" ] && "$BL" -b --factory-startup --python-expr "import bpy; print('BLENDER_OK')" 2>/dev/null | grep -q BLENDER_OK \
  && ok "Blender runs in the background" || bad "Blender background run (open Blender once by hand so macOS allows it, then re-run)"
node --check "$SKILL/voice/finish.mjs" && "$VENV/bin/python" -c "import ast,sys; [ast.parse(open(f).read()) for f in sys.argv[1:]]" "$SKILL"/kit/*.py "$SKILL"/tools/*.py \
  && ok "the skill's scripts parse"

echo; echo "================ summary"; printf "%b\n" "$OK"
if [ -n "$BAD" ]; then printf "%b\n" "$BAD"; echo; echo "Fix the MISSING lines, then run this again."; exit 1; fi
echo; echo "All set. Open Claude Code and type /make-short"
