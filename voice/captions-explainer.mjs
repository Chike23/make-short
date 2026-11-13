// captions-explainer.mjs: captions + callouts for the "anatomy explainer" look (references/styles/anatomy-explainer.md)
// Used by finish.mjs when voice/cues.json has "captionStyle": "explainer". Writes ASS for libass, 1080x1920.
//
// Captions (measured on the 6 reference reels at 30 fps):
//  - a short phrase card (2-4 words, up to 2 lines) near the TOP of the frame, centred, sentence case; Inter stands in for
//    the reference's geometric sans (cap height 52 px at 1080, first baseline at y 384, second line 82 px lower)
//  - words appear as they are spoken and the line re-centres as each one arrives; a word enters blurred and is sharp one frame later
//  - the word being spoken is white Bold; earlier words in the card are warm grey Regular; 2 empty frames between cards
//  - "key words" (cues.json keyWords: word stems) stay white Bold inside a blue text-selection box with two round handles
//  - house rule (user, 2026-11): every word and callout has a black outline (5 px at 1080) over the soft dark shadow, so
//    it reads on any background; no pop or scale animation
// Callouts (cues.json "overlays"): stat (big number + small label), note (small grey footnote), tag (CAPS label + leader line),
//  counter (small label over a big number, for example "age" / "30", with a thin rule under it)
import fs from 'node:fs'; import path from 'node:path';

const here = path.dirname(new URL(import.meta.url).pathname.replace(/^\/(\w:)/, '$1'));
export const FONTS_DIR = path.join(here, 'fonts');
const M = JSON.parse(fs.readFileSync(path.join(FONTS_DIR, 'inter-metrics.json'), 'utf8'));

const DEF = {            // measured on the 6 reference reels at 30 fps (references/styles/anatomy-explainer.md section 3)
  size: 87,              // Inter at 87 = cap height 52 px at 1080 wide (reference: 35 px at 720)
  scaleX: 95,            // Inter is about 5% wider than the reference's geometric sans
  lineCentreY: 352,      // first baseline at y 384 of 1920 (reference: 256 of 1280); checked side by side
  lineGap: 0.95,         // second line 82 px lower (reference: 55 px at 720)
  maxWords: 4, maxLineWidth: 640, maxCardSecs: 2.4, pauseBreak: 0.35,
  cardGap: 2,            // frames of empty caption between cards
  blurIn: true,          // each word enters blurred and sharpens in one frame
  white: 'FFFFFF', grey: '74706C', blue: '3D7BFF', boxFillAlpha: 0xC8,   // RGB hex; alpha 00 = opaque, FF = invisible
  shadow: true,
  outline: 5,            // black outline on every word and callout (px at 1080); 0 = the reference's shadow only
};

const bgr = rgb => `&H${rgb.slice(4, 6)}${rgb.slice(2, 4)}${rgb.slice(0, 2)}&`;
const hex2 = n => n.toString(16).toUpperCase().padStart(2, '0');
const ts = s => { s = Math.max(0, s); const h = Math.floor(s / 3600), m = Math.floor(s / 60) % 60, x = (s % 60).toFixed(2).padStart(5, '0'); return `${h}:${String(m).padStart(2, '0')}:${x}`; };
// libass sizes Inter so that (winAscent + winDescent) = font size, so 1 em = size * upm / (ascent + descent)
export function textWidth(str, size, weight = 'regular') {
  const f = M[weight], em = size * f.upm / (f.ascent + f.descent);
  let u = 0; for (const ch of str) u += f.adv[ch] ?? f.adv['n'];
  return u / f.upm * em;
}
const clean = w => w.replace(/["“”]/g, '');
const endsPhrase = w => /[.,!?;:…—]["”’)]*$/.test(w);

// ------------------------------------------------------------------ phrase cards
function cards(words, o) {
  const out = []; let cur = [];
  const flush = () => { if (cur.length) out.push(cur); cur = []; };
  for (let i = 0; i < words.length; i++) {
    const w = words[i], prev = cur[cur.length - 1];
    if (prev && (w.line !== prev.line || w.start - prev.end > o.pauseBreak || cur.length >= o.maxWords ||
        w.end - cur[0].start > o.maxCardSecs)) flush();
    cur.push(w);
    if (endsPhrase(w.w)) flush();
  }
  flush();
  return out;
}

// split a card into at most 2 centred lines; each word gets a slot (the mean of its Regular and Bold widths)
function layout(card, o, isKey) {
  const sx = (o.scaleX ?? 100) / 100;
  const space = textWidth(' ', o.size, 'regular') * sx;
  // key words get room for their selection box (box padding plus a small gap) so it never touches the next word
  const slot = w => isKey(w) ? textWidth(clean(w.w), o.size, 'bold') * sx + o.size * 0.5
    : (textWidth(clean(w.w), o.size, 'regular') + textWidth(clean(w.w), o.size, 'bold')) / 2 * sx;
  const lines = [[]]; let width = 0;
  for (const w of card) {
    const add = slot(w) + (lines[lines.length - 1].length ? space : 0);
    if (lines[lines.length - 1].length && width + add > o.maxLineWidth && lines.length < 2) { lines.push([]); width = 0; }
    lines[lines.length - 1].push(w); width += slot(w) + (lines[lines.length - 1].length > 1 ? space : 0);
  }
  const placed = [];
  lines.forEach((ln, li) => {
    const total = ln.reduce((a, w, i) => a + slot(w) + (i ? space : 0), 0);
    let x = 540 - total / 2;
    const y = o.lineCentreY + li * o.size * o.lineGap;
    for (const w of ln) { const s = slot(w); placed.push({ ...w, cx: x + s / 2, cy: y }); x += s + space; }
  });
  return placed;
}

function rect(x, y, w, h) { return `m ${x.toFixed(1)} ${y.toFixed(1)} l ${(x + w).toFixed(1)} ${y.toFixed(1)} ${(x + w).toFixed(1)} ${(y + h).toFixed(1)} ${x.toFixed(1)} ${(y + h).toFixed(1)}`; }
function circle(cx, cy, r) {
  const k = 0.5523 * r, f = v => v.toFixed(1);
  return `m ${f(cx)} ${f(cy - r)} b ${f(cx + k)} ${f(cy - r)} ${f(cx + r)} ${f(cy - k)} ${f(cx + r)} ${f(cy)} b ${f(cx + r)} ${f(cy + k)} ${f(cx + k)} ${f(cy + r)} ${f(cx)} ${f(cy + r)} ` +
    `b ${f(cx - k)} ${f(cy + r)} ${f(cx - r)} ${f(cy + k)} ${f(cx - r)} ${f(cy)} b ${f(cx - r)} ${f(cy - k)} ${f(cx - k)} ${f(cy - r)} ${f(cx)} ${f(cy - r)}`;
}

// ------------------------------------------------------------------ callouts
function when(spec, words, fallback) {
  if (spec == null) return fallback;
  if (typeof spec === 'number') return spec;
  const [line, stem] = String(spec).split(':');
  const w = words.find(x => x.line === Number(line) && x.w.replace(/[^\p{L}\p{N}']/gu, '').toLowerCase().startsWith(stem.toLowerCase()));
  if (!w) throw new Error(`overlay time "${spec}": word not found (use "line:wordStem" or seconds)`);
  return w.start;
}
export function overlays(list, words, o = DEF) {
  const ev = [];
  const ol = o.outline ?? 5, font = o.calloutFont ?? 'Inter';
  // every callout text: a soft dark shadow layer, then the text itself with a black outline (house rule)
  const push = (t, tags, text) => {
    if (ol) ev.push(`Dialogue: 4,${t},X,,0,0,0,,{${tags}\\c&H000000&\\3c&H000000&\\bord${ol * 2}\\shad0\\blur5\\alpha&H50&}${text}`);
    ev.push(`Dialogue: 5,${t},X,,0,0,0,,{${tags}\\bord${ol}\\3c&H000000&\\shad0}${text}`);
  };
  const line = (t, shape, colour) =>     // rules and leader lines get the outline too
    ev.push(`Dialogue: 5,${t},X,,0,0,0,,{\\an7\\pos(0,0)\\p1\\bord${ol ? Math.max(2, ol / 2) : 0}\\3c&H000000&\\shad0\\c${bgr(colour)}}${shape}{\\p0}`);
  for (const ov of list || []) {
    const a = when(ov.at, words, 0), b = when(ov.until, words, a + 3);
    const t = `${ts(a)},${ts(b)}`, x = ov.x ?? 70, y = ov.y ?? 1060;
    if (ov.type === 'stat') {          // "1%" with "of body weight, lost as water" under it, left aligned
      push(t, `\\an1\\pos(${x},${y})\\fn${font}\\b1\\fs${ov.size ?? 190}\\c${bgr(o.white)}`, ov.text);
      if (ov.label) push(t, `\\an7\\pos(${x + 6},${y + 14})\\fn${font}\\b0\\fs${ov.labelSize ?? 40}\\c${bgr(ov.labelColour ?? 'D8D8D8')}`, ov.label);
    } else if (ov.type === 'counter') { // small "age" over a big "30", with a thin rule under it, right aligned
      push(t, `\\an3\\pos(${x},${y - (ov.size ?? 150) * 0.95})\\fn${font}\\b0\\fs${ov.labelSize ?? 36}\\c${bgr('C8C8C8')}`, ov.label ?? '');
      push(t, `\\an3\\pos(${x},${y})\\fn${font}\\b${ov.bold === false ? 0 : 1}\\fs${ov.size ?? 150}\\c${bgr(o.white)}`, ov.text);
      const w = ov.ruleWidth ?? 190;
      line(t, rect(x - w, y + 18, w, 3), 'C8C8C8');
    } else if (ov.type === 'note') {   // small grey footnote, bottom left: "Body water shown in magenta"
      push(t, `\\an1\\pos(${ov.x ?? 70},${ov.y ?? 1560})\\fn${font}\\b0\\fs${ov.size ?? 30}\\c${bgr(ov.colour ?? 'B4B4B4')}`, ov.text);
    } else if (ov.type === 'tag') {    // "FOREARM FLEXORS": caps, letter-spaced, optional leader line to [x2, y2]
      push(t, `\\an1\\pos(${x},${y})\\fn${font}\\b1\\fsp4\\fs${ov.size ?? 34}\\c${bgr(o.white)}`, String(ov.text).toUpperCase());
      if (ov.to) {
        const [x2, y2] = ov.to, dx = x2 - x, dy = y2 - (y - 50), len = Math.hypot(dx, dy) || 1, nx = -dy / len * 1.5, ny = dx / len * 1.5;
        line(t, `m ${x + nx} ${y - 50 + ny} l ${x2 + nx} ${y2 + ny} ${x2 - nx} ${y2 - ny} ${x - nx} ${y - 50 - ny}`, o.white);
      }
    } else throw new Error(`unknown overlay type ${ov.type} (stat, counter, note, tag)`);
  }
  return ev;
}

// ------------------------------------------------------------------ build
export function buildExplainerAss(words, T, CF = {}) {
  const o = { ...DEF, ...(CF.explainer || {}) };
  const keys = (CF.keyWords || []).map(k => k.toLowerCase());
  const isKey = w => keys.some(k => w.w.replace(/[^\p{L}\p{N}']/gu, '').toLowerCase().startsWith(k));
  const ev = [];
  const all = cards(words, o);
  all.forEach((card, ci) => {
    const next = all[ci + 1]?.[0].start;
    const cardEnd = next != null ? Math.max(card[card.length - 1].end, next - o.cardGap / 30) : Math.min(card[card.length - 1].end + 0.6, T.duration + 0.4);
    // time cuts: every word start and end inside the card
    const cuts = [...new Set(card.flatMap(w => [w.start, Math.min(w.end, cardEnd)]).concat([cardEnd]))].filter(t => t <= cardEnd).sort((a, b) => a - b);
    for (let k = 0; k + 1 < cuts.length; k++) {
      const a = cuts[k], b = cuts[k + 1]; if (b - a < 0.005) continue;
      const visible = card.filter(w => w.start <= a + 1e-6);         // the line re-centres as words arrive
      if (!visible.length) continue;
      for (const w of layout(visible, o, isKey)) {
        const active = a >= w.start - 1e-6 && a < w.end - 1e-6, key = isKey(w), lit = active || key;
        const entering = o.blurIn && Math.abs(a - w.start) < 1e-6;
        const enter = entering ? '\\blur7\\alpha&H70&\\t(0,33,\\blur0\\alpha&H00&)' : '';
        const style = `\\an5\\pos(${w.cx.toFixed(1)},${w.cy.toFixed(1)})\\fnInter\\fs${o.size}\\fscx${o.scaleX ?? 100}\\b${lit ? 1 : 0}\\c${bgr(lit ? o.white : o.grey)}`;
        if (o.shadow) ev.push(`Dialogue: 0,${ts(a)},${ts(b)},X,,0,0,0,,{${style}\\c&H000000&\\alpha&H70&\\bord6\\3c&H000000&\\3a&H90&\\blur10}${clean(w.w)}`);
        ev.push(`Dialogue: 2,${ts(a)},${ts(b)},X,,0,0,0,,{${style}\\bord${o.outline ?? 0}\\3c&H000000&\\shad0${enter}}${clean(w.w)}`);
        if (key) {
          const bw = textWidth(clean(w.w), o.size, 'bold') * (o.scaleX ?? 100) / 100 + o.size * 0.3, bh = o.size * 0.98;
          const bx = w.cx - bw / 2, by = w.cy - bh / 2 - o.size * 0.02;
          ev.push(`Dialogue: 1,${ts(a)},${ts(b)},X,,0,0,0,,{\\an7\\pos(0,0)\\p1\\bord0\\shad0\\c${bgr(o.blue)}\\alpha&H${hex2(o.boxFillAlpha)}&}${rect(bx, by, bw, bh)}{\\p0}`);
          ev.push(`Dialogue: 3,${ts(a)},${ts(b)},X,,0,0,0,,{\\an7\\pos(0,0)\\p1\\bord3\\shad0\\1a&HFF&\\3c${bgr(o.blue)}}${rect(bx, by, bw, bh)}{\\p0}`);
          const r = o.size * 0.1;
          ev.push(`Dialogue: 3,${ts(a)},${ts(b)},X,,0,0,0,,{\\an7\\pos(0,0)\\p1\\bord2\\shad0\\c${bgr(o.blue)}\\3c${bgr('FFFFFF')}}${circle(bx, by, r)} ${circle(bx + bw, by + bh, r)}{\\p0}`);
        }
      }
    }
  });
  ev.push(...overlays(CF.overlays, words, o));
  return `[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\n` +
    `Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n` +
    `Style: X,Inter,${o.size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1\n\n` +
    `[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n${ev.join('\n')}\n`;
}

// Preview without a voice: node captions-explainer.mjs <timing.json> [cues.json] [out.ass]
if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(new URL(import.meta.url).pathname.replace(/^\/(\w:)/, '$1'))) {
  const T = JSON.parse(fs.readFileSync(process.argv[2], 'utf8').replace(/^﻿/, ''));
  const CF = process.argv[3] ? JSON.parse(fs.readFileSync(process.argv[3], 'utf8')) : {};
  const words = T.lines.flatMap(l => l.words.map(w => ({ ...w, line: l.line })));
  const out = process.argv[4] || path.join(here, 'captions.ass');
  fs.writeFileSync(out, buildExplainerAss(words, T, CF));
  console.log('wrote', out);
}
