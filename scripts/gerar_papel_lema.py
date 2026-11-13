"""Tira de papel rasgado com o lema "Alone we fit well. / Together, we fit perfectly."

Mesmo tratamento do lockup: borda rasgada irregular com fibra branca de largura
variável, papel bege com textura de amassado, marca-texto amarelo e texto em
contornos (DM Sans Medium/ExtraBold, OFL).
Uso:  python3 scripts/gerar_papel_lema.py  ->  svg/papel-lema.svg (+ papel-lema-texto-editavel.svg)
"""
import base64
import io
import math
import random
from pathlib import Path

import numpy as np
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image

import gerar_svgs as G

ROOT = Path(__file__).resolve().parent.parent
W, H = 900, 330
PAPER = "#FCEBD5"
FIBER = "#FFFDF8"
INK = "#111111"
HIGHLIGHT = "#E8E41C"

# contorno do papel (sentido horário), inspirado na referência
ANCHORS = [(88, 122), (175, 82), (300, 60), (480, 46), (640, 60), (760, 70), (835, 100),
           (845, 180), (838, 252), (640, 266), (450, 262), (250, 272), (60, 264), (48, 190)]
FIBER_ON = {0: 7, 1: 6, 2: 6, 3: 5, 4: 6, 5: 6, 6: 3, 7: 0, 8: 5, 9: 7, 10: 6, 11: 7, 12: 2, 13: 3}


def outline(fiber):
    cx = sum(p[0] for p in ANCHORS) / len(ANCHORS)
    cy = sum(p[1] for p in ANCHORS) / len(ANCHORS)
    pts = []
    for i, p0 in enumerate(ANCHORS):
        p1 = ANCHORS[(i + 1) % len(ANCHORS)]
        mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(dx, dy)
        nx, ny = -dy / L, dx / L
        if nx * (mx - cx) + ny * (my - cy) < 0:
            nx, ny = -nx, -ny
        st = G.rng.getstate()
        G.rng.seed(1000 + i)  # mesma borda-base para papel e fibra
        e = FIBER_ON[i] if fiber else 0
        seg = G._torn_edge(p0, p1, 0.55, (nx, ny), e, step=3)
        G.rng.setstate(st)
        pts += seg[:-1]
    return pts


def texture_png(size=600, seed=7):
    """Papel amassado: manchas suaves claras/escuras + fibras finas (sem emenda)."""
    r = np.random.default_rng(seed)

    def blur(a, k):
        out = a.copy()
        for dx in range(-k, k + 1):
            for dy in range(-k, k + 1):
                if dx or dy:
                    out += np.roll(np.roll(a, dx, 0), dy, 1)
        return out / (2 * k + 1) ** 2

    low = np.kron(r.random((size // 30, size // 30)), np.ones((30, 30)))
    low = blur(blur(blur(low, 8), 8), 8)
    low = (low - low.mean()) / (low.std() + 1e-9)
    mid = np.kron(r.random((size // 8, size // 8)), np.ones((8, 8)))
    mid = blur(blur(mid, 3), 3)
    mid = (mid - mid.mean()) / (mid.std() + 1e-9)
    v = low * 0.7 + mid * 0.3
    out = np.zeros((size, size, 4), np.uint8)
    light, dark = v > 0, v <= 0
    out[light] = (255, 255, 255, 0)
    out[..., 3] = np.clip(np.abs(v) * 9, 0, 26).astype(np.uint8)
    out[dark, :3] = (150, 110, 70)
    out[light, :3] = (255, 255, 255)
    fine = blur(r.random((size, size)), 1)
    m = fine > np.quantile(fine, 0.985)
    out[m] = (160, 120, 80, 22)
    buf = io.BytesIO()
    Image.fromarray(out).save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def glyph_paths(font_file, text, size, x, y, tracking=0.0):
    f = TTFont(ROOT / "fonts" / font_file)
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f["hmtx"]
    k = size / f["head"].unitsPerEm
    out, cx = [], x
    for ch in text:
        name = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[name].draw(TransformPen(pen, (k, 0, 0, -k, cx, y)))
        if pen.getCommands():
            out.append(f'<path d="{pen.getCommands()}"/>')
        cx += hmtx[name][0] * k + tracking
    return "".join(out), cx - x


def highlighter(x0, x1, y0, y1):
    rnd = random.Random(5)
    top = [(x0 + (x1 - x0) * t / 40, y0 + rnd.uniform(-0.8, 0.8)) for t in range(41)]
    right = [(x1 + rnd.uniform(-2, 3), y0 + (y1 - y0) * t / 4) for t in range(1, 4)]
    bot = [(x1 - (x1 - x0) * t / 40, y1 + rnd.uniform(-0.8, 0.8)) for t in range(41)]
    left = [(x0 + rnd.uniform(-3, 2), y1 - (y1 - y0) * t / 4) for t in range(1, 4)]
    return (f'<polygon id="marca-texto" points="{G.fmt(top + right + bot + left)}" '
            f'fill="{HIGHLIGHT}" opacity="0.92"/>')


def build(editable):
    tex = texture_png()
    defs = (f'<defs><pattern id="papel-amassado" patternUnits="userSpaceOnUse" width="600" height="600">'
            f'<image width="600" height="600" href="data:image/png;base64,{tex}"/></pattern></defs>')
    paper_pts, fiber_pts = G.fmt(outline(False)), G.fmt(outline(True))
    b = [f'<g id="papel"><polygon id="fibra" points="{fiber_pts}" fill="{FIBER}"/>'
         f'<polygon id="papel-bege" points="{paper_pts}" fill="{PAPER}"/>'
         f'<polygon id="textura-amassado" points="{paper_pts}" fill="url(#papel-amassado)"/></g>']
    t = ['<g id="texto" transform="rotate(-1.6 450 175)">', highlighter(150, 764, 196, 224)]
    if editable:
        t.append(f'<text x="236" y="146" font-family="DM Sans" font-weight="500" font-size="51" fill="{INK}" '
                 f'letter-spacing="-1.6">Alone we fit well.</text>')
        t.append(f'<text x="160" y="205" font-family="DM Sans" font-weight="800" font-size="53" '
                 f'fill="{INK}" letter-spacing="-2.4">Together, we fit perfectly.</text>')
    else:
        l1, w1 = glyph_paths("DMSans-Medium.ttf", "Alone we fit well.", 51, 0, 0, -1.6)
        l2, w2 = glyph_paths("DMSans-ExtraBold.ttf", "Together, we fit perfectly.", 53, 0, 0, -2.4)
        t.append(f'<g id="linha-1" fill="{INK}" transform="translate({427 - w1 / 2:.1f} 146)">{l1}</g>')
        t.append(f'<g id="linha-2" fill="{INK}" transform="translate({453 - w2 / 2:.1f} 204)">{l2}</g>')
    t.append("</g>")
    body = defs + "".join(b) + "".join(t)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W * 2}" height="{H * 2}" '
            f'viewBox="0 0 {W} {H}">{body}</svg>\n')


if __name__ == "__main__":
    (G.OUT / "papel-lema.svg").write_text(build(False))
    (G.OUT / "papel-lema-texto-editavel.svg").write_text(build(True))
    print("ok")
