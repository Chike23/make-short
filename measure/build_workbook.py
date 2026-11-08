"""Combined workbook: Comparison (one row per video + parameter rows), per-shot table per video, per-frame data per video."""
import json, sys, numpy as np, pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L

# usage: python3 build_workbook.py out.xlsx refdir1 [refdir2 ...]
OUT = sys.argv[1]
DIRS = [d.rstrip('/') for d in sys.argv[2:]]
KEYS = DIRS
BASE = ''
AR = 'Arial'
hdr_font = Font(name=AR, bold=True, color='FFFFFF', size=10); hdr_fill = PatternFill('solid', fgColor='2B2B2B')
body = Font(name=AR, size=10); bold = Font(name=AR, size=10, bold=True); note = Font(name=AR, size=9, color='52514E')
live = PatternFill('solid', fgColor='F2F2F0'); param_fill = PatternFill('solid', fgColor='FFF4CC')
thin = Side(style='thin', color='D9D9D9')
SIZES = ['EWS', 'WS', 'FS', 'MS', 'MCU', 'CU', 'INS']

def hexfill(c, hx):
    hx = hx.lstrip('#'); c.fill = PatternFill('solid', fgColor=hx)
    lum = 0.2126 * int(hx[0:2], 16) + 0.7152 * int(hx[2:4], 16) + 0.0722 * int(hx[4:6], 16)
    c.font = Font(name=AR, size=9, color='000000' if lum > 140 else 'FFFFFF')

def header(ws, row, names, height=58):
    for j, h in enumerate(names, 1):
        c = ws.cell(row, j, h); c.font = hdr_font; c.fill = hdr_fill
        c.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
    ws.row_dimensions[row].height = height

wb = Workbook(); comp = wb.active; comp.title = 'Comparison'
info = {}

for idx, key in enumerate(KEYS, 1):
    d = key
    A = json.load(open(f'{d}/analysis.json')); S, SH = A['summary'], A['shots']
    pf = pd.read_csv(f'{d}/per_frame_full.csv'); cards = pd.read_csv(f'{d}/caption_cards.csv'); N = len(pf)
    tag = f'R{idx}'
    # ---------- per-frame tab ----------
    fs = wb.create_sheet(f'{tag} frames')
    size = pf.shot_size.values; starts = set(s['start'] for s in SH)
    chg = np.r_[0, (size[1:] != size[:-1]).astype(int)]
    cap_text = [''] * N; new_card = [0] * N; bx = [[None] * 4 for _ in range(N)]
    for _, r in cards.iterrows():
        new_card[int(r.start)] = 1
        for i in range(int(r.start), int(r.end) + 1):
            cap_text[i] = r.text; bx[i] = [r.x0, r.y0, r.x1, r.y1]
    cols = ['Frame', 'Time (s)', 'Shot', 'Shot size', 'Size change within shot (1=yes)', 'Size change at cut (1=yes)', 'Location',
            'Mean luma (%)', 'Luma p5 (%)', 'Luma p95 (%)', 'Luma SD (%)', 'Near-black px (%)', 'Near-white px (%)', 'Mean saturation (%)',
            'Colourfulness', 'Hue (°)', 'Hue weight', 'L*', 'a*', 'b*', 'Mean R', 'Mean G', 'Mean B', 'Caption on screen',
            'New caption card (1=yes)', 'Caption left x (px)', 'Caption top y (px)', 'Caption right x (px)', 'Caption bottom y (px)']
    header(fs, 1, cols, 42)
    fmts = ['0', '0.000', '0', '@', '0', '0', '0'] + ['0.00'] * 7 + ['0.0', '0.0', '0.000', '0.00', '0.00', '0.00', '0.0', '0.0', '0.0', '@', '0', '0', '0', '0', '0']
    for i in range(N):
        r = i + 2; row = pf.iloc[i]
        vals = [i, f'=A{r}/30', int(row.shot), row.shot_size, int(chg[i] and i not in starts), int(chg[i] and i in starts), int(row.location),
                row.luma_mean / 2.55, row.luma_p5 / 2.55, row.luma_p95 / 2.55, row.luma_std / 2.55, row.pct_black, row.pct_white, row.sat_mean,
                row.colourfulness, row.hue_deg, row.hue_strength, row.L, row.a, row.b, row.R, row.G, row.B, cap_text[i], new_card[i], *bx[i]]
        for j, v in enumerate(vals, 1):
            if isinstance(v, (float, np.floating)):
                v = None if np.isnan(v) else round(float(v), 4)
            c = fs.cell(r, j, v); c.font = body; c.number_format = fmts[j - 1]
    fs.freeze_panes = 'B2'
    for j in range(1, len(cols) + 1): fs.column_dimensions[L(j)].width = 11
    fs.column_dimensions['X'].width = 16
    last = N + 1
    def rng(col): return f"'{tag} frames'!${col}${2}:${col}${last}"
    R_ = {k: rng(c) for k, c in zip(['shot', 'size', 'wchg', 'cchg', 'loc', 'luma', 'p5', 'p95', 'sd', 'blk', 'wht', 'sat', 'colf', 'hue', 'hw', 'L', 'a', 'b',
                                     'R', 'G', 'B', 'text', 'newc', 'x0', 'y0', 'x1', 'y1'],
                                    ['C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'AA', 'AB', 'AC'])}
    # ---------- per-shot tab ----------
    ws = wb.create_sheet(f'{tag} shots')
    ws['A1'] = f"{tag} · {S['title']} — measured shot by shot"; ws['A1'].font = Font(name=AR, size=14, bold=True)
    ws['A2'] = f"720×1280 · 30 fps · {N} frames · {N / 30:.2f} s. Grey cells are formulas over the '{tag} frames' tab."; ws['A2'].font = note
    H = 4
    heads = ['Shot', 'First frame', 'Last frame', 'Frames', 'Starts at (s)', 'Duration (s)', 'Transition into shot', 'Transition length (frames)',
             'Location(s)', 'Location name(s)', 'Shot sizes, in order', 'Shot-size changes inside shot', 'Shot size changes at the cut',
             'Mean brightness (%)', 'Darkest frame (%)', 'Brightest frame (%)', 'Luma p5 (%)', 'Luma p95 (%)', 'Contrast: luma SD (%)',
             'Near-black px (%)', 'Near-white px (%)', 'Mean saturation (%)', 'Colourfulness', 'Mean hue (°)', 'L*', 'a* (+red / −green)',
             'b* (+warm / −cool)', 'Average colour', 'Palette 1', 'Palette 2', 'Palette 3', 'Palette 4', 'Caption cards starting',
             'Caption centre x (% of width)', 'Caption box top (% of height)', 'Caption box bottom (% of height)']
    header(ws, H, heads)
    r0 = H + 1
    for k, s in enumerate(SH):
        r = r0 + k
        tin = s['transition_in'] + (f" (frames {s['transition_span']})" if s['transition_span'] else '')
        v = {1: s['shot'], 2: s['start'], 3: s['end'], 4: f'=C{r}-B{r}+1', 5: f'=B{r}/30', 6: f'=D{r}/30', 7: tin,
             8: (s['transition_frames'] if s['transition_in'] != 'Start' else '—'),
             9: 'L' + str(s['locations']).replace(' → ', ' → L'), 10: s['location_names'], 11: s['sizes'],
             12: f"=SUMIFS({R_['wchg']},{R_['shot']},A{r})", 13: f"=IF(SUMIFS({R_['cchg']},{R_['shot']},A{r})>0,\"Yes\",\"No\")",
             14: f"=AVERAGEIFS({R_['luma']},{R_['shot']},A{r})", 15: f"=_xlfn.MINIFS({R_['luma']},{R_['shot']},A{r})",
             16: f"=_xlfn.MAXIFS({R_['luma']},{R_['shot']},A{r})", 17: f"=AVERAGEIFS({R_['p5']},{R_['shot']},A{r})",
             18: f"=AVERAGEIFS({R_['p95']},{R_['shot']},A{r})", 19: f"=AVERAGEIFS({R_['sd']},{R_['shot']},A{r})",
             20: f"=AVERAGEIFS({R_['blk']},{R_['shot']},A{r})", 21: f"=AVERAGEIFS({R_['wht']},{R_['shot']},A{r})",
             22: f"=AVERAGEIFS({R_['sat']},{R_['shot']},A{r})", 23: f"=AVERAGEIFS({R_['colf']},{R_['shot']},A{r})",
             24: f"=MOD(DEGREES(ATAN2(SUMPRODUCT(({R_['shot']}=A{r})*{R_['hw']}*COS(RADIANS({R_['hue']}))),SUMPRODUCT(({R_['shot']}=A{r})*{R_['hw']}*SIN(RADIANS({R_['hue']}))))),360)",
             25: f"=AVERAGEIFS({R_['L']},{R_['shot']},A{r})", 26: f"=AVERAGEIFS({R_['a']},{R_['shot']},A{r})", 27: f"=AVERAGEIFS({R_['b']},{R_['shot']},A{r})",
             28: s['avg_rgb'], 33: f"=COUNTIFS({R_['newc']},1,{R_['shot']},A{r})",
             34: f"=IFERROR((AVERAGEIFS({R_['x0']},{R_['shot']},A{r})+AVERAGEIFS({R_['x1']},{R_['shot']},A{r}))/2/720*100,\"\")",
             35: f"=IFERROR(AVERAGEIFS({R_['y0']},{R_['shot']},A{r})/1280*100,\"\")", 36: f"=IFERROR(AVERAGEIFS({R_['y1']},{R_['shot']},A{r})/1280*100,\"\")"}
        for j in range(29, 33):
            hx, sh = s['palette'][j - 29]; v[j] = f'{hx} · {sh * 100:.0f}%'
        for j, val in v.items():
            c = ws.cell(r, j, val); c.font = body; c.border = Border(bottom=thin)
            c.alignment = Alignment(vertical='center', wrap_text=j in (7, 10, 11))
            if isinstance(val, str) and val.startswith('='): c.fill = live
        hexfill(ws.cell(r, 28), s['avg_rgb'])
        for j in range(29, 33): hexfill(ws.cell(r, j), s['palette'][j - 29][0])
        ws.row_dimensions[r].height = 44
    rt = r0 + len(SH); fr_, lr_ = r0, rt - 1
    tot = {1: 'Whole video', 2: f'=MIN(B{fr_}:B{lr_})', 3: f'=MAX(C{fr_}:C{lr_})', 4: f'=SUM(D{fr_}:D{lr_})', 6: f'=SUM(F{fr_}:F{lr_})',
           7: f'=COUNTIF(G{fr_}:G{lr_},"Dissolve*")&" dissolves, "&COUNTIF(G{fr_}:G{lr_},"Hard cut")&" hard cuts, "&COUNTIF(G{fr_}:G{lr_},"Hidden cut*")&" hidden cuts"',
           8: f'=IFERROR(AVERAGEIF(G{fr_}:G{lr_},"Dissolve*",H{fr_}:H{lr_}),"")',
           9: f"=SUMPRODUCT(1/COUNTIF({R_['loc']},{R_['loc']}))&\" distinct · \"&SUMPRODUCT(--('{tag} frames'!$G$3:$G${last}<>'{tag} frames'!$G$2:$G${last - 1}))&\" location changes\"",
           11: f'=L{rt}+M{rt}&" size changes in total"', 12: f'=SUM(L{fr_}:L{lr_})', 13: f'=COUNTIF(M{fr_}:M{lr_},"Yes")',
           14: f"=AVERAGE({R_['luma']})", 15: f"=MIN({R_['luma']})", 16: f"=MAX({R_['luma']})", 17: f"=AVERAGE({R_['p5']})", 18: f"=AVERAGE({R_['p95']})",
           19: f"=AVERAGE({R_['sd']})", 20: f"=AVERAGE({R_['blk']})", 21: f"=AVERAGE({R_['wht']})", 22: f"=AVERAGE({R_['sat']})", 23: f"=AVERAGE({R_['colf']})",
           24: f"=MOD(DEGREES(ATAN2(SUMPRODUCT({R_['hw']}*COS(RADIANS({R_['hue']}))),SUMPRODUCT({R_['hw']}*SIN(RADIANS({R_['hue']}))))),360)",
           25: f"=AVERAGE({R_['L']})", 26: f"=AVERAGE({R_['a']})", 27: f"=AVERAGE({R_['b']})", 28: S['avg_rgb'], 33: f'=SUM(AG{fr_}:AG{lr_})',
           34: f"=(AVERAGE({R_['x0']})+AVERAGE({R_['x1']}))/2/720*100", 35: f"=AVERAGE({R_['y0']})/1280*100", 36: f"=AVERAGE({R_['y1']})/1280*100"}
    for j in range(29, 33):
        hx, sh = S['palette'][j - 29]; tot[j] = f'{hx} · {sh * 100:.0f}%'
    for j, val in tot.items():
        c = ws.cell(rt, j, val); c.font = bold; c.alignment = Alignment(vertical='center', wrap_text=j in (7, 9, 11))
        c.border = Border(top=Side(style='medium', color='2B2B2B'))
        if isinstance(val, str) and val.startswith('='): c.fill = live
    hexfill(ws.cell(rt, 28), S['avg_rgb'])
    for j in range(29, 33): hexfill(ws.cell(rt, j), S['palette'][j - 29][0])
    ws.row_dimensions[rt].height = 58
    fmt = {4: '0', 5: '0.00', 6: '0.00', 8: '0', 12: '0', 14: '0.0', 15: '0.0', 16: '0.0', 17: '0.0', 18: '0.0', 19: '0.0', 20: '0.00', 21: '0.00',
           22: '0.0', 23: '0.0', 24: '0', 25: '0.0', 26: '+0.0;-0.0;0.0', 27: '+0.0;-0.0;0.0', 33: '0', 34: '0.0', 35: '0.0', 36: '0.0'}
    for r in range(r0, rt + 1):
        for j, f in fmt.items(): ws.cell(r, j).number_format = f
    ws.cell(rt, 8).number_format = '0.0'
    widths = {1: 12, 7: 26, 8: 11, 9: 16, 10: 34, 11: 34, 28: 11, 29: 15, 30: 15, 31: 15, 32: 15}
    for j in range(1, len(heads) + 1): ws.column_dimensions[L(j)].width = widths.get(j, 10)
    ws.freeze_panes = ws.cell(r0, 2)
    if S.get('notes'):
        c = ws.cell(rt + 2, 1, 'Notes: ' + S['notes']); c.font = note; c.alignment = Alignment(wrap_text=True, vertical='top')
        ws.merge_cells(start_row=rt + 2, start_column=1, end_row=rt + 2, end_column=16); ws.row_dimensions[rt + 2].height = 44
    info[key] = dict(tag=tag, S=S, N=N, rt=rt, r0=r0, R=R_, cards=cards, last=last)

# ---------- Comparison ----------
comp['A1'] = 'Four reference shorts — measured side by side, with the parameters for new videos'; comp['A1'].font = Font(name=AR, size=14, bold=True)
comp['A2'] = ('Rows R1–R4 are formulas over each video\'s tabs. Yellow rows are the parameters: target = median of the four; '
              'allowed range = lowest to highest of the four.'); comp['A2'].font = note
metrics = [  # (header, formula builder(info) -> str, number format)
    ('Video', lambda I: I['S']['title'], '@'),
    ('Duration (s)', lambda I: f"='{I['tag']} shots'!F{I['rt']}", '0.0'),
    ('Shots', lambda I: f"=COUNT('{I['tag']} shots'!A{I['r0']}:A{I['rt'] - 1})", '0'),
    ('Average shot (s)', lambda I: f"='{I['tag']} shots'!F{I['rt']}/COUNT('{I['tag']} shots'!A{I['r0']}:A{I['rt'] - 1})", '0.00'),
    ('Median shot (s)', lambda I: f"=MEDIAN('{I['tag']} shots'!F{I['r0']}:F{I['rt'] - 1})", '0.00'),
    ('Shortest shot (s)', lambda I: f"=MIN('{I['tag']} shots'!F{I['r0']}:F{I['rt'] - 1})", '0.00'),
    ('Longest shot (s)', lambda I: f"=MAX('{I['tag']} shots'!F{I['r0']}:F{I['rt'] - 1})", '0.00'),
    ('Dissolves', lambda I: f"=COUNTIF('{I['tag']} shots'!G{I['r0']}:G{I['rt'] - 1},\"Dissolve*\")", '0'),
    ('Hard cuts', lambda I: f"=COUNTIF('{I['tag']} shots'!G{I['r0']}:G{I['rt'] - 1},\"Hard cut\")", '0'),
    ('Hidden cuts', lambda I: f"=COUNTIF('{I['tag']} shots'!G{I['r0']}:G{I['rt'] - 1},\"Hidden cut*\")", '0'),
    ('Dissolve share of transitions (%)', lambda I: f"=IFERROR(COUNTIF('{I['tag']} shots'!G{I['r0']}:G{I['rt'] - 1},\"Dissolve*\")/(COUNT('{I['tag']} shots'!A{I['r0']}:A{I['rt'] - 1})-1)*100,0)", '0'),
    ('Mean dissolve length (frames)', lambda I: f"=IFERROR(AVERAGEIF('{I['tag']} shots'!G{I['r0']}:G{I['rt'] - 1},\"Dissolve*\",'{I['tag']} shots'!H{I['r0']}:H{I['rt'] - 1}),\"\")", '0.0'),
    ('Shot-size changes', lambda I: f"='{I['tag']} shots'!L{I['rt']}+'{I['tag']} shots'!M{I['rt']}", '0'),
    ('… of which inside camera moves', lambda I: f"='{I['tag']} shots'!L{I['rt']}", '0'),
    ('Size changes per second', lambda I: f"=('{I['tag']} shots'!L{I['rt']}+'{I['tag']} shots'!M{I['rt']})/'{I['tag']} shots'!F{I['rt']}", '0.00'),
    ('Average hold per shot size (s)', lambda I: f"='{I['tag']} shots'!F{I['rt']}/('{I['tag']} shots'!L{I['rt']}+'{I['tag']} shots'!M{I['rt']}+1)", '0.00'),
] + [(f'Time in {z} (%)', (lambda z: (lambda I: f"=COUNTIF({I['R']['size']},\"{z}\")/COUNT({I['R']['shot']})*100"))(z), '0') for z in SIZES] + [
    ('Locations', lambda I: f"=SUMPRODUCT(1/COUNTIF({I['R']['loc']},{I['R']['loc']}))", '0'),
    ('Location changes', lambda I: f"=SUMPRODUCT(--('{I['tag']} frames'!$G$3:$G${I['last']}<>'{I['tag']} frames'!$G$2:$G${I['last'] - 1}))", '0'),
    ('Seconds per location visit', lambda I: f"='{I['tag']} shots'!F{I['rt']}/(SUMPRODUCT(--('{I['tag']} frames'!$G$3:$G${I['last']}<>'{I['tag']} frames'!$G$2:$G${I['last'] - 1}))+1)", '0.0'),
    ('Mean brightness (%)', lambda I: f"=AVERAGE({I['R']['luma']})", '0.0'),
    ('Darkest frame (%)', lambda I: f"=MIN({I['R']['luma']})", '0.0'),
    ('Brightest frame (%)', lambda I: f"=MAX({I['R']['luma']})", '0.0'),
    ('Luma p5 (%)', lambda I: f"=AVERAGE({I['R']['p5']})", '0.0'),
    ('Luma p95 (%)', lambda I: f"=AVERAGE({I['R']['p95']})", '0.0'),
    ('Contrast: luma SD (%)', lambda I: f"=AVERAGE({I['R']['sd']})", '0.0'),
    ('Near-black px (%)', lambda I: f"=AVERAGE({I['R']['blk']})", '0.00'),
    ('Near-white px (%)', lambda I: f"=AVERAGE({I['R']['wht']})", '0.00'),
    ('Mean saturation (%)', lambda I: f"=AVERAGE({I['R']['sat']})", '0.0'),
    ('Colourfulness', lambda I: f"=AVERAGE({I['R']['colf']})", '0.0'),
    ('a* (+red)', lambda I: f"=AVERAGE({I['R']['a']})", '+0.0;-0.0'),
    ('b* (+warm)', lambda I: f"=AVERAGE({I['R']['b']})", '+0.0;-0.0'),
    ('Warm frames (%)', lambda I: f"=COUNTIF({I['R']['b']},\">0\")/COUNT({I['R']['b']})*100", '0'),
    ('Caption cards', lambda I: f"=SUM({I['R']['newc']})", '0'),
    ('Caption words', lambda I: int(I['cards'].words.sum()), '0'),
    ('Words per second', lambda I: f"={int(I['cards'].words.sum())}/'{I['tag']} shots'!F{I['rt']}", '0.00'),
    ('One-word cards (%)', lambda I: round(float((I['cards'].words == 1).mean() * 100), 2), '0'),
    ('Median card (frames)', lambda I: float(I['cards'].frames.median()), '0'),
    ('Frames with a caption (%)', lambda I: f"=COUNTIF({I['R']['text']},\"?*\")/COUNT({I['R']['shot']})*100", '0'),
    ('Caption line centre (% from top)', lambda I: round(I['S']['captions']['line_centre_y_px'] / 12.8, 2), '0.0'),
    ('Caption cap height (% of height)', lambda I: round(I['S']['captions']['cap_height_px'] / 12.8, 2), '0.00'),
    ('Caption centre x (% of width)', lambda I: f"=(AVERAGE({I['R']['x0']})+AVERAGE({I['R']['x1']}))/2/720*100", '0.0'),
]
H = 4
header(comp, H, ['Ref'] + [m[0] for m in metrics], 70)
first = H + 1
for k, key in enumerate(KEYS):
    I = info[key]; r = first + k
    c = comp.cell(r, 1, I['tag']); c.font = bold
    for j, (h, fn, f) in enumerate(metrics, 2):
        v = fn(I); c = comp.cell(r, j, v); c.font = body; c.number_format = f
        if isinstance(v, str) and v.startswith('='): c.fill = live
lastv = first + len(KEYS) - 1
labels = [('Lowest', 'MIN'), ('Median = target', 'MEDIAN'), ('Highest', 'MAX')]
for k, (lab, fn) in enumerate(labels):
    r = lastv + 1 + k
    c = comp.cell(r, 1, lab); c.font = bold; c.fill = param_fill
    for j in range(3, len(metrics) + 2):
        col = L(j); f = metrics[j - 2][2]
        c = comp.cell(r, j, f'={fn}({col}{first}:{col}{lastv})'); c.font = bold if fn == 'MEDIAN' else body; c.fill = param_fill; c.number_format = f
    comp.cell(r, 2, '(parameters)' if fn == 'MEDIAN' else '').font = note
    for j in range(1, len(metrics) + 2):
        comp.cell(r, j).border = Border(top=Side(style='medium', color='2B2B2B')) if k == 0 else Border()
comp.column_dimensions['A'].width = 16; comp.column_dimensions['B'].width = 30
for j in range(3, len(metrics) + 2): comp.column_dimensions[L(j)].width = 11
for r in range(first, lastv + 4): comp.row_dimensions[r].height = 22
comp.freeze_panes = comp.cell(first, 3)
nr = lastv + 6
notes = [
    'How each number was measured',
    'Every frame was decoded (BT.709, limited to full range) and measured. Cuts, dissolves and hidden cuts were found by viewing every frame plus frame-difference signals; a shot starts at the first frame where the incoming picture dominates (blend weight < 0.5). Dissolve length = frames with blend weight between 0.1 and 0.9.',
    'Shot size was coded by eye per frame range on the main character: EWS no/tiny figure · WS whole figure, small · FS whole figure, large · MS knees/waist up · MCU chest up · CU head or close body · INS object detail. Boundaries ±3 frames. Most size changes happen inside continuous camera moves.',
    'Location = a distinct set (same background geometry); revisits keep their number. Brightness = BT.709 luma as % of full scale. Saturation = mean HSV S. Colourfulness = Hasler–Süsstrunk M. a*/b* = CIELAB means (b* > 0 = warm).',
    'Captions: white glyphs with a black outline, detected on every frame, grouped into cards, read by OCR and corrected by eye. Line centre = midpoint of cap top and baseline.',
]
for k, t in enumerate(notes):
    c = comp.cell(nr + k, 1, t); c.font = bold if k == 0 else note; c.alignment = Alignment(wrap_text=True, vertical='top')
    comp.merge_cells(start_row=nr + k, start_column=1, end_row=nr + k, end_column=14); comp.row_dimensions[nr + k].height = 16 if k == 0 else 34
wb.move_sheet('Comparison', offset=-wb.index(comp))
# order: Comparison, R1 shots, R2 shots..., then frames tabs
order = ['Comparison'] + [f'R{i} shots' for i in range(1, len(KEYS) + 1)] + [f'R{i} frames' for i in range(1, len(KEYS) + 1)]
wb._sheets = [wb[n] for n in order]
wb.save(OUT); print(OUT, len(metrics), 'metrics')
