"""Reorganiza as formas do SVG exportado do Figma (assets/arte-principal-figma.svg)
no layout da ecobag. Só reposiciona, gira e escala as formas originais; arcos e
retângulos aparecem duplicados (cópias das mesmas formas).
Uso:  python3 scripts/reorganizar_ecobag.py  ->  svg/ecobag-kickoff2026.svg
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "arte-principal-figma.svg"
OUT = ROOT / "svg" / "ecobag-kickoff2026.svg"
VB = (40, 170, 1120, 1090)  # área de impressão da ecobag

s = SRC.read_text()
body, defs = s.split("<defs", 1)
body = body.split(">", 1)[1]  # tira a tag <svg>
defs = "<defs" + defs.rsplit("</svg>", 1)[0]
els = re.findall(r"<mask\b.*?</mask>|<g\b.*?</g>|<path\b[^>]*/>", body, re.S)
arcs, rect1, rect2 = els[0:6], els[6:8], els[8:10]
red, yellow, mask, orange, pink = els[10:12], els[12:14], els[14], els[15], els[16]
burst, lockup = els[17:33], els[33:]


def grp(name, parts, tr):
    return f'<g id="{name}" transform="{tr}">{"".join(parts)}</g>'


def recolor(parts, color):
    return [re.sub(r'fill="#[0-9A-Fa-f]{6}"', f'fill="{color}"', p) for p in parts]


RED_T = "translate(552 610) scale(1.27) translate(-545 -316)"
YEL_T = "translate(805 414) scale(1.07) translate(-749.5 -146)"

mask = re.sub(r'\sx="[^"]*" y="[^"]*" width="[^"]*" height="[^"]*"',
              ' x="-3000" y="-3000" width="8000" height="8000"', mask, count=1)
mask = mask.replace("<path ", f'<path transform="{RED_T}" ', 1)
orange = orange.replace("<path ", f'<path transform="{YEL_T}" ')

out = [
    grp("arcos-esquerda", arcs, "translate(145 652) rotate(135.5) scale(1.5) translate(-762.2 -647.3)"),
    grp("retangulo-azul", rect1, "translate(402 544) rotate(15) scale(1.34 1) rotate(-9.5) translate(-396 -336)"),
    grp("circulo-vermelho", red, RED_T),
    grp("circulo-amarelo", yellow, YEL_T),
    mask, orange,
    grp("retangulo-rosa", [pink], "translate(790 478) rotate(16.5) scale(1.52 1.14) rotate(-20.8) translate(-708.9 -182.2)"),
    grp("explosao", burst, "translate(962 370) scale(1.5) translate(-216 -801)"),
    grp("retangulo-amarelo", recolor(rect2, "#D4D72C"), "translate(45 950) rotate(29) scale(1.16) translate(-259.6 -558.6)"),
    grp("retangulo-azul-canto", rect2, "translate(634 1258) rotate(-10.5) scale(2) translate(-259.6 -558.6)"),
    grp("arcos-direita", arcs, "translate(765 1215) rotate(178.3) scale(1.6) translate(-762.2 -647.3)"),
    grp("lockup", lockup, "translate(588 760) translate(-486 -486)"),
]
logo = (ROOT / "svg" / "logo" / "sizebay-logo-preto.svg").read_text()
lw, lh = (float(v) for v in re.search(r'width="([\d.]+)" height="([\d.]+)"', logo).groups())
k = 290 / lw
inner = logo.split(">", 1)[1].rsplit("</svg>", 1)[0]
out.append(f'<g id="logo-sizebay" transform="translate({600 - 145} {1085 - lh * k / 2:.1f}) scale({k:.4f})">{inner}</g>')

x, y, w, h = VB
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
       f'width="{w * 2}" height="{h * 2}" viewBox="{x} {y} {w} {h}" fill="none">'
       f'<clipPath id="area-impressao"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="24"/></clipPath>'
       f'<g clip-path="url(#area-impressao)">{"".join(out)}</g>{defs}</svg>\n')
OUT.write_text(svg)
print("ok", len(els), "elementos")
