// finish.mjs: silent render + voice + SFX on words + ducked music + one-word captions -> out/short-final.mp4
//   node finish.mjs [silent.mp4] [voice.mp3] [timing.json]
//   defaults: ../out/short-silent.mp4, voice/voice.mp3, voice/voice-timing.json (take.mjs output or your own recording, see SKILL.md)
//   sound cues come from voice/cues.json: {"cues":[[sfx,line,wordStem,offsetS]],"impact":{sfx:frame},"hits":[[sfx,frame,vol]],"capUp":[[f0,f1]]}
import fs from 'node:fs'; import path from 'node:path'; import { execFileSync } from 'node:child_process';
import { buildExplainerAss, overlays, FONTS_DIR } from './captions-explainer.mjs';
const here = path.dirname(new URL(import.meta.url).pathname.replace(/^\/(\w:)/, '$1'));
const root = path.join(here, '..');
const silent = process.argv[2] || path.join(root, 'out', 'short-silent.mp4');
const VID_DUR = Number(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', silent], { encoding: 'utf8' }).trim());
const T = JSON.parse(fs.readFileSync(path.resolve(process.argv[4] || path.join(here, 'voice-timing.json')), 'utf8').replace(/^\uFEFF/, ''));
const words = T.lines.flatMap(l => l.words.map(w => ({ ...w, line: l.line })));

// SFX on the word they belong to: [sfx, line, word stem, offset s]
const CF = fs.existsSync(path.join(here, 'cues.json')) ? JSON.parse(fs.readFileSync(path.join(here, 'cues.json'), 'utf8')) : {};
const CUES = CF.cues || [];
const at = (line, stem) => words.find(w => w.line === line && w.w.replace(/[^\w]/g, '').toLowerCase().startsWith(stem.toLowerCase()));
// verified on-screen impact frames from the animator win over word timing (30 fps)
const IMPACT = CF.impact || {};   // clang/ding +4: critic r4 measured the star 4 f after
const sfx = CUES.map(([n, line, stem, off]) => {
  if (IMPACT[n] != null) return { n, t: IMPACT[n] / 30 };
  const w = at(line, stem); if (!w) throw new Error(`cue word not found: ${stem} (line ${line})`); return { n, t: Math.max(0, w.start + off) };
});
// hits with a visible impact but no cue word: [sfx, frame, volume]  (hook hammer swings)
for (const [n, f, v] of (CF.hits || [])) sfx.push({ n, t: f / 30, v });
// a whoosh on every whip cut in the shot list (starts 3 frames before the cut)
const shotsFile = path.join(path.dirname(silent), '..', 'shots.json');
if (fs.existsSync(shotsFile)) for (const s of JSON.parse(fs.readFileSync(shotsFile, 'utf8')))
  if (s.transition_in === 'whip' && !sfx.some(x => Math.abs(x.t - s.f_in / 30) < 0.25)) sfx.push({ n: 'whoosh', t: Math.max(0, (s.f_in - 3) / 30), v: 0.35 });

// captions measured on the reference (references/reference-style.md section 6), at 1080x1920:
//  - one centred line, cap top 1321 px, baseline 1376 px (line centre 70.2% of the height), cap height 54 px
//  - near-white fill, black outline, soft dark shadow all round; NO pop/scale/fade: a card replaces the last on one frame
//    (Outline 5 plus a shadow layer of Outline 10, \blur5, 69% opaque black, matched the reference edge profile best after a 720p upload)
//  - original case AND punctuation kept; 75% one-word cards, 22% two-word; a pair always contains a word of <= 3 letters
//    and never crosses punctuation; cards hold until the next card (a caption on every frame)
// Arial Black at 108 has a 54-55 px cap height in libass. CAP_Y = the \pos y of the text box bottom (baseline + descender);
// after a render, `python audit.py` measures the real cap top/baseline: move CAP_Y by (1376 - measured baseline).
// Font: Arial Black (macOS/Windows system font). Where it is missing (Linux), libass would silently fall back to a thin
// font, so use Inter Black at 84 placed 7 px higher (audit.py: cap height 54, baseline 1376, as Arial Black 108 at 1400).
// cues.json captionFont / captionSize / captionY win.
const hasFont = f => { try { return execFileSync('fc-list', [':family'], { encoding: 'utf8' }).includes(f); } catch { return true; } };
const CAP_FONT = CF.captionFont ?? (hasFont('Arial Black') ? 'Arial Black' : 'Inter Black');
const CAP_SIZE = CF.captionSize ?? (CAP_FONT === 'Arial Black' ? 108 : 84);
const CAP_Y = CF.captionY ?? (CAP_FONT === 'Arial Black' ? 1400 : 1393);
if (!CF.captionFont && CAP_FONT !== 'Arial Black') console.log(`captions: Arial Black not installed here, using ${CAP_FONT} ${CAP_SIZE}`);
const ONE_WORD = CF.oneWordShare ?? 0.75;
const ts = s => { const h = Math.floor(s / 3600), m = Math.floor(s / 60) % 60, x = (s % 60).toFixed(2).padStart(5, '0'); return `${h}:${String(m).padStart(2, '0')}:${x}`; };
const clean = w => w.replace(/["“”]/g, '');
const bare = w => w.replace(/[^\p{L}\p{N}']/gu, '');
// candidate pairs: same line, no punctuation after the first word, one of the two words has <= 3 letters
const cand = [];
for (let i = 0; i + 1 < words.length; i++) {
  const w = words[i], n = words[i + 1];
  if (n.line !== w.line || /[.,!?;:…—]["”’)]*$/.test(w.w)) continue;
  if (Math.min(bare(w.w).length, bare(n.w).length) > 3) continue;
  cand.push({ i, span: n.end - w.start });
}
// take the tightest-spoken pairs until one-word cards fall to the target share: pairs = (1 - s) / (2 - s) of the words
const want = Math.round(words.length * (1 - ONE_WORD) / (2 - ONE_WORD));
const paired = new Set();
for (const c of cand.sort((x, y) => x.span - y.span)) {
  if (paired.size / 2 >= want) break;
  if (paired.has(c.i) || paired.has(c.i + 1)) continue;
  paired.add(c.i); paired.add(c.i + 1);
}
const groups = [];
for (let i = 0; i < words.length; i++) {
  const w = words[i];
  if (paired.has(i) && paired.has(i + 1) && words[i + 1].line === w.line && !/[.,!?;:…—]["”’)]*$/.test(w.w)) {
    groups.push({ start: w.start, end: words[i + 1].end, text: `${clean(w.w)} ${clean(words[i + 1].w)}` }); i++;
  } else groups.push({ start: w.start, end: w.end, text: clean(w.w) });
}
// shots where a hero prop sits in the caption band: the reference never moves its captions, so use this only as a last resort
const CAP_UP = CF.capUp || [];
const ev = [];
groups.forEach((w, i) => {
  const end = groups[i + 1]?.start ?? Math.max(w.end + 0.4, VID_DUR);   // hold until the next card; the last one holds to the end of the picture
  const y = CAP_UP.some(([a, b]) => w.start * 30 >= a && w.start * 30 < b) ? CAP_Y - 620 : CAP_Y;
  const pos = `\\an2\\pos(540,${y})`;
  ev.push(`Dialogue: 0,${ts(w.start)},${ts(end)},S,,0,0,0,,{${pos}\\blur5}${w.text}`);   // soft shadow layer
  ev.push(`Dialogue: 1,${ts(w.start)},${ts(end)},W,,0,0,0,,{${pos}}${w.text}`);           // the caption
});
// "captionStyle": "explainer" in cues.json = the anatomy-explainer look (top phrase cards, key-word box, callouts): captions-explainer.mjs
const EXPLAINER = CF.captionStyle === 'explainer';
// callouts ("overlays" in cues.json: stat, counter, note, tag) work in both looks, always with a black outline
if (!EXPLAINER) ev.push(...overlays(CF.overlays, words, { white: 'F9F9F9', outline: 5, ...(CF.callouts || {}) }));
const ass = EXPLAINER ? buildExplainerAss(words, T, CF) : `[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n` +
  `Style: W,${CAP_FONT},${CAP_SIZE},&H00F9F9F9,&H00F9F9F9,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,5,0,2,60,60,0,1\n` +
  `Style: S,${CAP_FONT},${CAP_SIZE},&H50000000,&H50000000,&H50000000,&H00000000,0,0,0,0,100,100,0,0,1,10,0,2,60,60,0,1\n` +
  `Style: X,Inter,80,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1\n\n` +
  `[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n${ev.join('\n')}\n`;
fs.writeFileSync(path.join(here, 'captions.ass'), ass);

const out = path.join(root, 'out'); fs.mkdirSync(out, { recursive: true });
const dst = path.join(out, path.basename(silent).includes('preview') ? 'preview.mp4' : 'short-final.mp4');   // a preview stays a preview
const inputs = ['-i', silent, '-i', path.resolve(process.argv[3] || path.join(here, 'voice.mp3')), '-i', path.join(here, 'sfx', 'music.mp3'), ...sfx.flatMap(s => ['-i', path.join(here, 'sfx', `${s.n}.mp3`)])];
const sfxChains = sfx.map((s, i) => `[${i + 3}:a]volume=${s.v ?? 0.55},adelay=${Math.round(s.t * 1000)}|${Math.round(s.t * 1000)}[s${i}]`);
const subs = path.join(here, 'captions.ass').replace(/\\/g, '/').replace(/:/g, '\\:');
const esc = p => p.replace(/\\/g, '/').replace(/:/g, '\\:');
const fc = [
  `[0:v]subtitles='${subs}':fontsdir='${esc(FONTS_DIR)}'[v]`,   // Inter (callouts, explainer) ships in voice/fonts; Arial Black / Inter Black are system fonts
  `[1:a]asplit=2[vo][key]`,
  `[2:a]volume=0.30,afade=t=out:st=${(T.duration).toFixed(2)}:d=1.0[mu]`,
  `[mu][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[duck]`,
  ...sfxChains,
  `[vo][duck]${sfx.map((_, i) => `[s${i}]`).join('')}amix=inputs=${sfx.length + 2}:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9[a]`,
].join(';');
execFileSync('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error', ...inputs, '-filter_complex', fc, '-map', '[v]', '-map', '[a]',
  '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', dst], { stdio: 'inherit' });
console.log(EXPLAINER ? `wrote ${dst}  (${sfx.length} sfx, explainer captions from ${words.length} words, ${(CF.overlays || []).length} callouts)`
  : `wrote ${dst}  (${sfx.length} sfx, ${groups.length} captions from ${words.length} words, ${Math.round(100 * groups.filter(g => !g.text.includes(' ')).length / groups.length)}% one-word)`);
