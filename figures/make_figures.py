import math, os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

S = 3
# Everything in both figures is set in the paper's own faces, so the figures and the
# text around them read as one piece of type. pdffonts on the manuscript reports
# LMRoman10, LMRoman10-Bold and LMMathItalic10; these OTFs ship with the TeX
# distribution that builds the PDF, so ask kpsewhich where they are. LM_FONT_DIR
# overrides that lookup for a machine without TeX on PATH: point it at the
# opentype/public directory that holds lm/ and lm-math/.
LM_FONT_DIR = os.environ.get("LM_FONT_DIR", "").strip()

def texfont(name, sub):
    """Path to a Latin Modern OTF: $LM_FONT_DIR first, then kpsewhich, else None."""
    if LM_FONT_DIR:
        p = os.path.join(LM_FONT_DIR, sub.lstrip("/"), name)
        if os.path.exists(p):
            return p
    exe = shutil.which("kpsewhich")
    if exe:
        try:
            found = subprocess.run([exe, name], capture_output=True, text=True,
                                   timeout=20).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            found = ""
        if found and os.path.exists(found):
            return found
    return None

def lm(sub, name):
    return texfont(name, sub)

FR = lm("/lm/lmroman10-regular.otf", "lmroman10-regular.otf")          # text
FB = lm("/lm/lmroman10-bold.otf", "lmroman10-bold.otf")                # node labels
FI = lm("/lm/lmroman10-italic.otf", "lmroman10-italic.otf")            # glosses
LMI = lm("/lm-math/latinmodern-math.otf", "latinmodern-math.otf")      # math italic, Greek
MISSING = [name for name, path in (("lmroman10-regular.otf", FR), ("lmroman10-bold.otf", FB),
                                  ("lmroman10-italic.otf", FI), ("latinmodern-math.otf", LMI))
           if not path]
if MISSING:
    raise SystemExit("missing Latin Modern font(s): " + ", ".join(MISSING) +
                     "\n  They ship with any TeX distribution. Put kpsewhich on PATH, or set" +
                     "\n  LM_FONT_DIR to the opentype/public directory holding lm/ and lm-math/.")

def mi(ch):
    """Math-italic Latin letter from Latin Modern Math (ASCII maps to upright)."""
    if ch.isupper(): return chr(0x1D434 + ord(ch) - 65)
    return chr(0x1D44E + ord(ch) - 97)
_cache = {}
def F(path, size):
    k = (path, size)
    if k not in _cache: _cache[k] = ImageFont.truetype(path, int(size * S))
    return _cache[k]

INK = (25, 25, 30); GREY = (105, 105, 112); LIGHT = (222, 222, 226)
NAVY = (38, 62, 108); RUST = (168, 76, 32)

def textrun(dr, cx, cy, segs, fill=INK, align="center"):
    """One line of text in mixed faces, at unscaled image coordinates. A segment is
    (text, font path, size, rise in px); 'left' starts the line at cx, 'center' centres it."""
    widths = [dr.textlength(t, font=F(p, s)) for t, p, s, _ in segs]
    x = cx * S - sum(widths) / 2 if align == "center" else cx * S
    for (t, p, s, rise), w in zip(segs, widths):
        dr.text((x, cy * S + rise * S), t, font=F(p, s), fill=fill, anchor="lm")
        x += w

# ---------- Figure 1: the operational cycle ----------
W, H = 1800, 1150
img = Image.new("RGB", (W*S, H*S), "white"); d = ImageDraw.Draw(img)
cx, cy, rx, ry = 900, 585, 620, 410
names = ["Observe", "Store", "Compress", "Retrieve", "Reconstruct", "Re-store"]
angs  = [90, 30, -30, -90, -150, 150]
pts = [(cx + rx*math.cos(math.radians(a)), cy - ry*math.sin(math.radians(a))) for a in angs]

BW, BH = 342, 98          # node box; arrows stop at its edge, not a fixed inset
PAD = 10                  # px of clear space between the box edge and the arrow

def edge_inset(ux, uy, bw=BW, bh=BH):
    """Distance from a box centre to its own edge along the ray (ux, uy)."""
    tx = bw / 2 / abs(ux) if ux else float("inf")
    ty = bh / 2 / abs(uy) if uy else float("inf")
    return min(tx, ty)

def arrow(p0, p1, color, w, head=24, pad=PAD, bw=BW, bh=BH):
    dx, dy = p1[0]-p0[0], p1[1]-p0[1]; L = math.hypot(dx, dy); ux, uy = dx/L, dy/L
    s0 = edge_inset(ux, uy, bw, bh) + pad
    s1 = edge_inset(-ux, -uy, bw, bh) + pad
    a = (p0[0]+ux*s0, p0[1]+uy*s0); b = (p1[0]-ux*s1, p1[1]-uy*s1)
    d.line([a[0]*S, a[1]*S, b[0]*S, b[1]*S], fill=color, width=int(w*S))
    px, py = -uy, ux
    q1 = (b[0]-head*ux+head*0.5*px, b[1]-head*uy+head*0.5*py)
    q2 = (b[0]-head*ux-head*0.5*px, b[1]-head*uy-head*0.5*py)
    d.polygon([(b[0]*S, b[1]*S), (q1[0]*S, q1[1]*S), (q2[0]*S, q2[1]*S)], fill=color)

for i in range(6):
    j = (i+1) % 6
    accent = (i == 5)                      # Re-store -> Observe
    arrow(pts[i], pts[j], RUST if accent else INK, 8.0 if accent else 4.0, 30 if accent else 22)

for (x, y), nm in zip(pts, names):
    accent = nm == "Re-store"
    d.rounded_rectangle([(x-BW/2)*S, (y-BH/2)*S, (x+BW/2)*S, (y+BH/2)*S], radius=14*S,
                        fill="white", outline=RUST if accent else INK, width=int((4 if accent else 2.5)*S))
    d.text((x*S, y*S), nm, font=F(FB, 40), fill=RUST if accent else INK, anchor="mm")

textrun(d, cx, cy-38, [(mi("S"), LMI, 54, 0), (mi("n"), LMI, 32, 17), ("+1", FR, 32, 17),
                (" = ", FR, 54, 0), (mi("R"), LMI, 54, 0), ("(", FR, 54, 0),
                (mi("C"), LMI, 54, 0), ("(", FR, 54, 0), (mi("S"), LMI, 54, 0),
                (mi("n"), LMI, 32, 17), ("), ", FR, 54, 0), (mi("P"), LMI, 54, 0),
                (")", FR, 54, 0)])
d.text((cx*S, (cy+42)*S), "re-storage writes the reconstruction back",
       font=F(FI, 31), fill=GREY, anchor="mm")
d.text((cx*S, (cy+84)*S), "and is what closes the loop", font=F(FI, 31), fill=GREY, anchor="mm")
img.resize((W, H), Image.LANCZOS).save("figures/fig1-cycle.png", dpi=(300, 300))

# ---------- Figure 2: drift over cycles, simulated ----------
P = [0.10, 0.35, 0.35, 0.20]
S0 = [0.94, 0.02, 0.02, 0.02]
K = 12

def simulate(k, alpha, beta):
    s = list(S0); traj = [s[0]]; td = None; to = None
    rt = [max(S0[1:])]
    for n in range(1, K+1):
        keep = sorted(range(len(s)), key=lambda i: -s[i])[:k]
        c = [s[i] if i in keep else 0.0 for i in range(len(s))]
        tot = sum(c); c = [v/tot for v in c]
        q = [(c[i]**alpha) * (P[i]**beta) for i in range(len(P))]
        tot = sum(q); s = [v/tot for v in q]
        traj.append(s[0])
        rt.append(max(s[1:]))
        if td is None and s[0] < 0.5: td = n
        if to is None and max(s[1:]) > s[0]: to = n
    return traj, td, to, rt

arms = [(15, 4, 0.80, 1.50, RUST), (60, 4, 0.80, 0.30, NAVY)]
res = []
for Wb, k, al, be, col in arms:
    traj, td, to, rt = simulate(k, al, be)
    res.append((Wb, k, al, be, col, traj, td, to, rt))
    print(f"W={Wb} k={k} alpha={al} beta={be}  T_d={td}  T_o={to}  final m={traj[-1]:.3f}")
    print("   traj:", " ".join(f"{v:.2f}" for v in traj))

Wp, Hp = 1700, 1150
img2 = Image.new("RGB", (Wp*S, Hp*S), "white"); d2 = ImageDraw.Draw(img2)
x0, x1, y0, y1 = 210, 1560, 960, 150
def X(n): return x0 + (n / K) * (x1 - x0)
def Y(v): return y0 - v * (y0 - y1)

d2.rectangle([x0*S, Y(0.5)*S, x1*S, y0*S], fill=(246, 246, 248))
for gv in (0, 0.25, 0.5, 0.75, 1.0):
    d2.line([x0*S, Y(gv)*S, x1*S, Y(gv)*S], fill=LIGHT if gv != 0.5 else (150,150,156), width=int((2 if gv==0.5 else 1.4)*S))
    d2.text(((x0-24)*S, Y(gv)*S), f"{gv:g}", font=F(FR, 30), fill=INK, anchor="rm")
for n in range(0, K+1, 2):
    d2.line([X(n)*S, y0*S, X(n)*S, (y0+12)*S], fill=INK, width=int(2*S))
    d2.text((X(n)*S, (y0+40)*S), str(n), font=F(FR, 30), fill=INK, anchor="mm")
d2.line([x0*S, y0*S, x1*S, y0*S], fill=INK, width=int(2.5*S))
d2.line([x0*S, y0*S, x0*S, y1*S], fill=INK, width=int(2.5*S))
d2.text(((x0+x1)/2*S, (y0+96)*S), "cycle n", font=F(FR, 34), fill=INK, anchor="mm")

# Figure 2 is placed at 90% text width (1700 px over 5.84 in = 291 ppi), so a size
# in px renders at 72/291 pt. The floor below keeps every subscript at or above 7 pt.
FT, FS = 38, 29          # landmark label base / subscript, 9.4 pt and 7.2 pt

def tlabel(sub, val, col, cx, cy, align='center'):
    """One T with a subscript landmark, T_d = 2, centred on cx unless align is left."""
    textrun(d2, cx, cy, [('T', FB, FT, 0), (sub, FB, FS, 15), (f' = {val}', FB, FT, 0)],
            col, align)

for Wb, k, al, be, col, traj, td, to, rt in res:
    faint = tuple(int(c + (255 - c) * 0.50) for c in col)
    rpts = [(X(n)*S, Y(v)*S) for n, v in enumerate(rt)]
    d2.line(rpts, fill=faint, width=int(3.2*S), joint='curve')
    pts2 = [(X(n)*S, Y(v)*S) for n, v in enumerate(traj)]
    d2.line(pts2, fill=col, width=int(5.5*S), joint="curve")
    for px, py in pts2:
        if Wb == 15:
            d2.polygon([(px, py - 12.5*S), (px - 10.8*S, py + 9*S), (px + 10.8*S, py + 9*S)], fill=col)
        else:
            d2.ellipse([px-9*S, py-9*S, px+9*S, py+9*S], fill="white", outline=col, width=int(3.2*S))
    if td and to != td:
        d2.line([X(td)*S, y0*S, X(td)*S, Y(0.5)*S], fill=col, width=int(2.4*S))
        tlabel('d', td, col, X(td), Y(0.5) - 44)
        top = Y(traj[to]) * S
        yy = y0 * S
        while yy > top:
            d2.line([X(to)*S, yy, X(to)*S, max(top, yy - 15*S)], fill=col, width=int(2.0*S))
            yy -= 26 * S
        px, py = X(to)*S, top
        d2.rectangle([px - 12*S, py - 12*S, px + 12*S, py + 12*S],
                     fill='white', outline=col, width=int(3.0*S))
        tlabel('o', to, col, X(to) + 22, Y(traj[to]) - 42, 'left')
    elif td:
        d2.line([X(td)*S, y0*S, X(td)*S, Y(0.5)*S], fill=col, width=int(2.4*S))
        # Both landmarks land on the same cycle of this arm, so one stem carries two
        # labels. A single "T_d = T_o = 2" runs to about 165 px and would cross this arm's
        # own curve, which passes x 357-390 at label height; two short labels stack in
        # the band left of the stem, clear of the axis on the other side.
        tlabel('d', td, col, X(td) - 210, Y(0.5) + 130, 'left')
        tlabel('o', to, col, X(td) - 210, Y(0.5) + 178, 'left')
d2.text(((x1-26)*S, (Y(0.5)+34)*S), "one-half threshold", font=F(FI, 31), fill=(120,120,126), anchor="rm")

lx, ly = 1010, 210
d2.rounded_rectangle([lx*S, ly*S, (lx+520)*S, (ly+150)*S], radius=10*S, fill="white", outline=LIGHT, width=int(2*S))
for i, (Wb, _k, _al, be, col, *_rest) in enumerate(res):
    yy = ly + 42 + i*56
    d2.line([(lx+28)*S, yy*S, (lx+92)*S, yy*S], fill=col, width=int(5*S))
    if Wb == 15:
        d2.polygon([((lx+60)*S, (yy-11)*S), ((lx+49.5)*S, (yy+8)*S), ((lx+70.5)*S, (yy+8)*S)], fill=col)
    else:
        d2.ellipse([(lx+51)*S, (yy-9)*S, (lx+69)*S, (yy+9)*S], fill="white", outline=col, width=int(3*S))
    # β is absent from Latin Modern Roman, so it comes from the math font.
    textrun(d2, lx + 116, yy, [(f"W = {Wb}  (", FR, 32, 0), ("β", LMI, 32, 0),
                               (f" = {be:g})", FR, 32, 0)], INK, 'left')

# The gloss lines start left of the legend box. Latin Modern sets the stem line 780 px
# wide, so x=780 ends it flush with the plot's right edge instead of overhanging it.
_ax = 780
_ly2 = (ly + 234) * S
d2.line([_ax*S, _ly2, (_ax+64)*S, _ly2], fill=(160,160,166), width=int(3.2*S))
d2.text(((_ax+96)*S, _ly2), "faint line: the leading rival's mass",
        font=F(FI, 31), fill=GREY, anchor='lm')
_ly = (ly + 196) * S; _x = _ax * S
for _t in ("solid stem: majority loss", "      dashed stem: rival overtakes"):
    d2.text((_x, _ly), _t, font=F(FI, 31), fill=GREY, anchor='lm')
    _x += d2.textlength(_t, font=F(FI, 31))
d2.text(((x0+x1)/2*S, 60*S), "Retained mass of the original state", font=F(FR, 34), fill=INK, anchor="mm")
img2.resize((Wp, Hp), Image.LANCZOS).save("figures/fig2-drift.png", dpi=(300, 300))
print("wrote figures/fig1-cycle.png and figures/fig2-drift.png")

# Regenerate the HTML preview so it can never lag behind the PNGs.
# Guarded: a missing Pillow, font or permission problem must not lose the figures.
if "--no-preview" not in sys.argv:
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import make_preview
        make_preview.main()
    except Exception as exc:
        print(f"warning: preview step skipped ({type(exc).__name__}: {exc})")
        print("         the figure PNGs are written; rerun `python figures/make_preview.py` to retry")
