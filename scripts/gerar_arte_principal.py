"""Arte principal do Kickoff 2026 (composição do lockup com formas risográficas).

Formas geométricas com corte limpo e grão de risografia; sobreposições de cor
desenhadas como formas próprias (amarelo sobre vermelho = laranja), arcos com
ponta reta, explosão de raios finos e o lockup vetorizado com grão nas cores.
Uso:  python3 scripts/gerar_arte_principal.py   (saída: svg/arte-principal-kickoff2026.svg)
"""
import math

import gerar_svgs as G

W, H = 1312, 1200
BG = "#FDF6ED"
BLUE = "#0A2FE6"
RED = "#F5330E"
YELLOW = "#E9EE0D"
ORANGE = "#FF800A"
PINK = "#F639C2"
INK = "#0A0B06"


def rot_rect(x, y, w, h, deg):
    """Retângulo com canto superior esquerdo em (x, y), girado deg graus em torno desse canto."""
    a = math.radians(deg)
    ux, uy = math.cos(a), math.sin(a)
    vx, vy = -math.sin(a), math.cos(a)
    return [(x, y), (x + w * ux, y + w * uy),
            (x + w * ux + h * vx, y + w * uy + h * vy), (x + h * vx, y + h * vy)]


def circle_pts(cx, cy, r, n=120):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def shape(pts, fill, name, opacity=None):
    p = G.fmt(pts)
    op = f' opacity="{opacity}"' if opacity else ""
    return (f'<g id="{name}"{op}><polygon points="{p}" fill="{fill}"/>'
            f'<polygon points="{p}" fill="url(#grain)"/></g>')


def arc_lines(cx, cy, radii, a0, a1, color, width, name):
    out = []
    for r in radii:
        s, e = math.radians(a0), math.radians(a1)
        x1, y1 = cx + r * math.cos(s), cy + r * math.sin(s)
        x2, y2 = cx + r * math.cos(e), cy + r * math.sin(e)
        large = 1 if (a1 - a0) % 360 > 180 else 0
        out.append(f'<path d="M{x1:.1f},{y1:.1f} A{r},{r} 0 {large} 1 {x2:.1f},{y2:.1f}" '
                   f'fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="butt"/>')
    return f'<g id="{name}">{"".join(out)}</g>'


def burst(cx, cy, r, n, color, width, name="explosao"):
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n + 0.09
        rr = r * (0.94 + 0.06 * ((i * 7) % 5) / 4)
        out.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + rr * math.cos(a):.1f}" y2="{cy + rr * math.sin(a):.1f}" '
                   f'stroke="{color}" stroke-width="{width}" stroke-linecap="butt"/>')
    return f'<g id="{name}">{"".join(out)}</g>'


def main():
    b = []
    # arcos superiores (passam por trás do retângulo azul)
    clip = G.fmt([(0, 0), (482, 0), (470, 78), (360, 760), (0, 760)])
    b.append(f'<clipPath id="clip-arcos"><polygon points="{clip}"/></clipPath>')
    b.append('<g clip-path="url(#clip-arcos)">'
             + arc_lines(480, 250, [218, 191, 164, 137, 110, 83], 95, 232, BLUE, 7, "arcos-topo") + "</g>")
    # retângulos azuis
    b.append(shape(rot_rect(470, 78, 255, 640, 9.5), BLUE, "retangulo-azul-topo"))
    b.append(shape(rot_rect(375, 690, 330, 450, -14), BLUE, "retangulo-azul-base"))
    # círculo vermelho, círculo amarelo e a sobreposição laranja
    red_c, yel_c = (728, 390, 231), (980, 180, 148)
    b.append(shape(circle_pts(*red_c), RED, "circulo-vermelho"))
    b.append(shape(circle_pts(*yel_c), YELLOW, "circulo-amarelo"))
    b.append(f'<clipPath id="clip-vermelho"><polygon points="{G.fmt(circle_pts(*red_c))}"/></clipPath>')
    b.append(f'<g id="sobreposicao-laranja" clip-path="url(#clip-vermelho)">'
             + shape(circle_pts(*yel_c), ORANGE, "laranja") + "</g>")
    # retângulo rosa (levemente translúcido sobre o amarelo)
    b.append(shape(rot_rect(930, 225, 268, 330, 20.8), PINK, "retangulo-rosa", opacity=0.9))
    # arcos inferiores e explosão
    b.append(arc_lines(1050, 1350, [420, 395, 370, 345, 320, 295], 208, 277, BLUE, 7, "arcos-base"))
    b.append(burst(318, 1005, 138, 16, INK, 4))
    # lockup
    b.append(G.g(G.title_lockup(1010), 155, 318, name="lockup"))
    svg = G.svg(W, H, "".join(b), BG)
    svg = svg.replace(f'width="{W}" height="{H}"', f'width="{W * 2}" height="{H * 2}"', 1)
    (G.OUT / "arte-principal-kickoff2026.svg").write_text(svg)
    print("ok")


if __name__ == "__main__":
    main()
