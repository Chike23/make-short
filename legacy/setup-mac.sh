#!/bin/bash
# One-time macOS setup for the make-short skill (Blender route, v3).
# Safe to re-run: every step checks first and skips what is already there.
#   bash ~/.claude/skills/make-short/setup-mac.sh             # core setup
#   bash ~/.claude/skills/make-short/setup-mac.sh --whisper   # + local transcription (large download)
#   bash ~/.claude/skills/make-short/setup-mac.sh --ocr       # + tesseract, for measure/ caption OCR
# Written for macOS's bash 3.2. Touches only: Homebrew packages, ~/.venvs/shorts, and one block in ~/.zshrc.

WHISPER=0; OCR=0
for a in "$@"; do case "$a" in --whisper) WHISPER=1;; --ocr) OCR=1;; esac; done
SKILL="$(cd "$(dirname "$0")" && pwd)"
VENV="${SHORTS_VENV:-$HOME/.venvs/shorts}"
OK=""; BAD=""
ok()  { echo "  ok   $1"; OK="$OK\n  ok   $1"; }
bad() { echo "  MISSING  $1"; BAD="$BAD\n  MISSING  $1"; }
step(){ echo; echo "== $1"; }

[ "$(uname -s)" = Darwin ] || { echo "setup-mac.sh is for macOS. On Windows follow INSTALL.md."; exit 1; }

step "Homebrew"
BREW="$(command -v brew)"
for c in /opt/homebrew/bin/brew /usr/local/bin/brew "$HOME/.homebrew/bin/brew"; do [ -z "$BREW" ] && [ -x "$c" ] && BREW="$c"; done
if [ -z "$BREW" ]; then
  echo "Homebrew is not installed. Install it from https://brew.sh (one command), then run this script again."; exit 1
fi
eval "$("$BREW" shellenv)"
ok "brew ($BREW)"

step "Command-line tools (ffmpeg, node, python, gh)"
need() {  # need <formula> <command>
  if command -v "$2" >/dev/null 2>&1; then ok "$2 ($(command -v "$2"))"
  else echo "  installing $1 ..."; "$BREW" install "$1" && ok "$2 (installed)" || bad "$2 (brew install $1 failed)"; fi
}
need ffmpeg ffmpeg
command -v ffprobe >/dev/null 2>&1 && ok "ffprobe" || bad "ffprobe (comes with ffmpeg)"
NVM_NODE="$(ls -d "$HOME"/.nvm/versions/node/*/bin/node 2>/dev/null | tail -1)"
if ! command -v node >/dev/null 2>&1 && [ -n "$NVM_NODE" ]; then export PATH="$(dirname "$NVM_NODE"):$PATH"; fi
need node node
BP="$("$BREW" --prefix)/bin/python3"   # Homebrew's Python, not the old /usr/bin one
if [ -x "$BP" ]; then ok "python3 ($BP)"; else echo "  installing python ..."; "$BREW" install python && ok "python3 (installed)" || bad "python3 (brew install python failed)"; fi
need gh gh
[ "$OCR" = 1 ] && need tesseract tesseract

step "Blender 5.x"
BL="$(ls -d /Applications/Blender*.app/Contents/MacOS/Blender "$HOME"/Applications/Blender*.app/Contents/MacOS/Blender 2>/dev/null | sort | tail -1)"
if [ -z "$BL" ]; then
  bad "Blender (download the macOS .dmg from https://www.blender.org/download/ and drag it to Applications)"
else
  BV="$("$BL" --version 2>/dev/null | head -1)"
  case "$BV" in
    "Blender 5."*|"Blender 6."*) ok "$BV ($BL)";;
    *) bad "Blender 5.x (found: ${BV:-unknown version} at $BL; the v3 route needs 5.x)";;
  esac
fi

step "Python packages (venv at $VENV)"
PY3="$BP"; [ -x "$PY3" ] || PY3="$(command -v python3)"
[ -x "$VENV/bin/python" ] || "$PY3" -m venv "$VENV"
if [ -x "$VENV/bin/python" ]; then
  "$VENV/bin/python" -m pip install -q --upgrade pip
  PKGS="numpy pillow opencv-python pandas openpyxl pytesseract"
  [ "$WHISPER" = 1 ] && PKGS="$PKGS openai-whisper"
  "$VENV/bin/python" -m pip install -q $PKGS && ok "venv packages: $PKGS" || bad "pip install ($PKGS)"
  "$VENV/bin/python" -c "import numpy, cv2, PIL, openpyxl" 2>/dev/null && ok "python imports (numpy, cv2, PIL, openpyxl)" || bad "python imports"
else
  bad "venv ($PY3 -m venv $VENV failed)"
fi

step "Shell profile (~/.zshrc)"
RC="$HOME/.zshrc"
if grep -q "# make-short (setup-mac.sh)" "$RC" 2>/dev/null; then ok "~/.zshrc already has the make-short block"
else
  {
    echo ""
    echo "# make-short (setup-mac.sh)"
    echo "export PYTHON=\"$VENV/bin/python\""
    echo "export PATH=\"\$PATH:$VENV/bin\"   # whisper and the venv tools, after the system ones"
  } >> "$RC" && ok "added PYTHON and the venv to ~/.zshrc (open a new Terminal window to pick it up)"
fi
export PYTHON="$VENV/bin/python"

step "Fonts and Claude Code"
if [ -f "/System/Library/Fonts/Supplemental/Arial Black.ttf" ] || [ -f "/Library/Fonts/Arial Black.ttf" ] || [ -f "$HOME/Library/Fonts/Arial Black.ttf" ]
then ok "Arial Black (captions)"; else bad "Arial Black font (captions need it; it normally ships with macOS)"; fi
if command -v claude >/dev/null 2>&1 || [ -x "$HOME/.local/bin/claude" ] || [ -x "$HOME/.claude/local/claude" ]
then ok "Claude Code"; else bad "Claude Code (the skill runs inside Claude Code: see https://docs.claude.com/en/docs/claude-code)"; fi

step "Smoke test"
if [ -n "$BL" ]; then
  "$BL" -b --factory-startup --python-expr "import bpy; print('BLENDER_OK', bpy.app.version_string)" 2>/dev/null | grep -q BLENDER_OK \
    && ok "Blender runs headless" || bad "Blender headless run (open Blender once by hand so macOS allows it, then re-run)"
fi
fail=0; for f in "$SKILL"/v3/*.sh; do bash -n "$f" || fail=1; done; [ $fail = 0 ] && ok "v3 scripts parse" || bad "v3 script syntax"
command -v node >/dev/null 2>&1 && node --check "$SKILL/v3/voice/finish.mjs" && node --check "$SKILL/v3/shots/validate.js" && ok "node scripts parse"
[ -x "$VENV/bin/python" ] && "$VENV/bin/python" -c "import ast,sys; [ast.parse(open(f).read()) for f in sys.argv[1:]]" \
  "$SKILL"/v3/scene.py "$SKILL"/v3/audit.py "$SKILL"/v3/dissolve.py "$SKILL"/v3/gate.py && ok "python scripts parse"

echo; echo "================ summary"
printf "%b\n" "$OK"
if [ -n "$BAD" ]; then printf "%b\n" "$BAD"; echo; echo "Fix the MISSING lines above, then run this script again."; exit 1; fi
echo
echo "All set. Open a NEW Terminal window, start Claude Code (claude), and say:"
echo "  Use the make-short skill. Run CHECKLIST.md section D on this Mac: one test shot with a camera push"
echo "  and a crossfade. Show me the key stills and the audit result."
