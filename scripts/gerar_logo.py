"""Gera o logo Sizebay (símbolo + nome em contornos) em SVG.

Recriação vetorial a partir do board do Kickoff 2026. O nome usa DM Sans Bold
convertida em curvas (fonts/DMSans-Bold.ttf, licença OFL).
Uso:  pip install fonttools && python3 scripts/gerar_logo.py
"""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "svg" / "logo"
FONT = ROOT / "fonts" / "DMSans-Bold.ttf"

BLACK, CREAM, BLUE, YELLOW = "#050505", "#FDEDD8", "#0017C8", "#E3ED06"

# Símbolo: três formas (topo, círculo, gota) numa caixa 100 x 92.
MARK = [
    # forma superior
    "M20,44 C7,44 1,35 3,24 C5,10 19,2 38,2 L76,2 C93,2 100,12 98,24 "
    "C96,37 87,44 74,44 L66,44 L71,33 L60,44 Z",
    # círculo inferior esquerdo
    "M26,50 A20,20 0 1 1 25.9,50 Z",
    # forma inferior direita
    "M58,50 L84,50 C95,50 100,58 99,68 C98,82 88,91 73,91 L61,91 "
    "C54,91 50,86 51,80 Z",
]
MARK_W, MARK_H = 100, 92


def mark_svg(fill, x=0, y=0, s=1):
    paths = "".join(f'<path d="{d}"/>' for d in MARK)
    return f'<g id="simbolo" fill="{fill}" transform="translate({x} {y}) scale({s})">{paths}</g>'


def word_paths(text, cap_h, tracking=-0.02):
    f = TTFont(FONT)
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f["hmtx"]
    upm = f["head"].unitsPerEm
    cap = f["OS/2"].sCapHeight or 700
    k = cap_h / cap
    x, out = 0.0, []
    for ch in text:
        name = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[name].draw(TransformPen(pen, (k, 0, 0, -k, x, 0)))
        out.append(f'<path d="{pen.getCommands()}"/>')
        x += (hmtx[name][0] + tracking * upm) * k
    return "".join(out), x - tracking * upm * k


def logo_svg(fill, bg=None, pad=0):
    mh = 92                      # altura do símbolo
    cap = 66                     # altura da maiúscula
    gap = 20
    words, ww = word_paths("Sizebay", cap)
    base = mh - 6                # linha de base próxima ao pé do símbolo
    W = MARK_W + gap + ww + 2 * pad
    H = mh + 22 + 2 * pad        # espaço para descendente do "y"
    bgr = f'<rect width="{W:.0f}" height="{H:.0f}" fill="{bg}"/>' if bg else ""
    body = (mark_svg(fill, pad, pad)
            + f'<g id="sizebay" fill="{fill}" transform="translate({pad + MARK_W + gap} {pad + base})">{words}</g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" '
            f'viewBox="0 0 {W:.0f} {H:.0f}">{bgr}<g id="logo-sizebay">{body}</g></svg>\n'), W, H


def symbol_svg(fill):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{MARK_W}" height="{MARK_H}" '
            f'viewBox="0 0 {MARK_W} {MARK_H}">{mark_svg(fill)}</svg>\n')


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for nome, cor in [("preto", BLACK), ("branco", CREAM), ("azul", BLUE)]:
        (OUT / f"sizebay-logo-{nome}.svg").write_text(logo_svg(cor)[0])
        (OUT / f"sizebay-simbolo-{nome}.svg").write_text(symbol_svg(cor))
    # prancha de aplicações
    tiles = [(CREAM, BLACK), (BLUE, CREAM), (BLACK, CREAM), (YELLOW, BLACK)]
    body, _, h = "", 0, 0
    for i, (bg, fg) in enumerate(tiles):
        svg, w, h = logo_svg(fg, None, 0)
        inner = svg.split(">", 1)[1].rsplit("</svg>", 1)[0]
        x, y = (i % 2) * 900, (i // 2) * 420
        body += (f'<rect x="{x}" y="{y}" width="900" height="420" fill="{bg}"/>'
                 f'<g transform="translate({x + 450 - w * 1.4 / 2:.0f} {y + 210 - h * 1.4 / 2:.0f}) scale(1.4)">{inner}</g>')
        body += (f'<g transform="translate({x + 40} {y + 40}) scale(0.5)">{mark_svg(fg)}</g>')
    (OUT / "sizebay-logo-aplicacoes.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="840" viewBox="0 0 1800 840">{body}</svg>\n')
    print("ok")
