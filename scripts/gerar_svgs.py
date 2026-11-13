"""Gera os elementos da identidade "Kickoff 2026 — Together we fit" em SVG.

Uso:  python3 scripts/gerar_svgs.py   (saída em ./svg)

Os textos ficam como <text> com fontes do Google Fonts (Archivo Black,
DM Serif Display, DM Sans), que o Figma já tem, então continuam editáveis.
"""
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "svg"

# ---------- Paleta ----------
BLUE = "#0017C8"
BLUE_LIGHT = "#7B95F2"
RED = "#FB2D0B"
YELLOW = "#E3ED06"
PINK = "#EE6FCB"
BLACK = "#050505"
CREAM = "#FDEDD8"
PAPER = "#FBF6EE"
PHOTO = "#D8D1C4"

DISPLAY = "'Archivo Black', 'Arial Black', sans-serif"
SERIF = "'DM Serif Display', Georgia, serif"
SANS = "'DM Sans', Helvetica, Arial, sans-serif"

rng = random.Random(2026)


def _grain_png(seed, light, dark, size=720):
    """Textura de risografia sem emenda: pontos claros (papel aparecendo) com densidade
    irregular e pontos escuros (tinta acumulada). light/dark = (fração, alpha)."""
    import base64, io
    import numpy as np
    from PIL import Image
    r = np.random.default_rng(seed)

    def wrap_blur(a, k):
        out = a.copy()
        for dx in range(-k, k + 1):
            for dy in range(-k, k + 1):
                if dx or dy:
                    out += np.roll(np.roll(a, dx, 0), dy, 1)
        return out / (2 * k + 1) ** 2

    fine = wrap_blur(r.random((size, size)), 1)
    low = r.random((size // 24, size // 24))
    low = np.kron(low, np.ones((24, 24)))
    low = wrap_blur(wrap_blur(low, 6), 6)
    low = (low - low.min()) / (low.max() - low.min() + 1e-9)
    out = np.zeros((size, size, 4), np.uint8)
    if light[0]:
        th = np.quantile(fine, 1 - light[0])
        m = fine + (low - 0.5) * 0.05 >= th
        out[m] = (255, 251, 244, light[1])
    if dark[0]:
        th = np.quantile(fine, dark[0])
        m = fine - (low - 0.5) * 0.04 <= th
        out[m] = (25, 12, 30, dark[1])
    buf = io.BytesIO()
    Image.fromarray(out).save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


_GRAINS = {}
GRAIN_SPECS = {"grain": (11, (0.13, 120), (0.025, 45)),      # formas de cor
               "grain-soft": (13, (0.06, 90), (0.0, 0)),     # cores do lockup
               "grain-bg": (12, (0.0, 0), (0.015, 18))}      # papel de fundo


def _grain_defs(body):
    out = []
    for gid, (seed, light, dark) in GRAIN_SPECS.items():
        if f"url(#{gid})" not in body:
            continue
        if gid not in _GRAINS:
            _GRAINS[gid] = _grain_png(seed, light, dark)
        out.append(f'<pattern id="{gid}" patternUnits="userSpaceOnUse" width="360" height="360">'
                   f'<image width="360" height="360" href="data:image/png;base64,{_GRAINS[gid]}"/></pattern>')
    return f"<defs>{''.join(out)}</defs>" if out else ""


def svg(w, h, body, bg=None, texture=True):
    bgrect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    if bg and texture:
        bgrect += f'<rect width="{w}" height="{h}" fill="url(#grain-bg)"/>'
    bgrect = _grain_defs(bgrect + body) + bgrect
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">{bgrect}{body}</svg>\n'
    )


def save(name, content):
    (OUT / name).write_text(content, encoding="utf-8")
    print("ok", name)


def fmt(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def _edge(x1, y1, x2, y2, jag, step):
    L = math.hypot(x2 - x1, y2 - y1)
    n = max(2, int(L / step))
    nx, ny = -(y2 - y1) / L, (x2 - x1) / L
    pts = []
    for i in range(n):
        t = i / n
        d = rng.uniform(-jag, jag) if 0 < i else 0
        pts.append((x1 + (x2 - x1) * t + nx * d, y1 + (y2 - y1) * t + ny * d))
    return pts


FIBER = "#F6F3F4"  # miolo branco do papel rasgado (da arte do lockup)


def _noise(L, s):
    """Ruído de borda em unidades absolutas: ondulação + pequenas fibras (como no lockup)."""
    comps = [(rng.uniform(90, 170), 2.4), (rng.uniform(28, 48), 0.9), (rng.uniform(9, 14), 0.35)]
    ph = [rng.uniform(0, 6.28) for _ in comps]
    def f(u):
        v = sum(a * math.sin(6.28 * u / wl + p) for (wl, a), p in zip(comps, ph))
        return s * (v + rng.uniform(-0.4, 0.4))
    return f


def _fiber_profile(L, e):
    """Largura da fibra branca: varia devagar, às vezes some."""
    wl, ph = rng.uniform(120, 260), rng.uniform(0, 6.28)
    wl2, ph2 = rng.uniform(40, 70), rng.uniform(0, 6.28)
    return lambda u: e * max(0.0, 0.45 + 0.5 * math.sin(6.28 * u / wl + ph)
                             + 0.25 * math.sin(6.28 * u / wl2 + ph2))


def _torn_edge(p0, p1, s, out_n, fiber_e=0.0, step=4):
    """Pontos de p0 a p1 com borda rasgada; fiber_e>0 empurra para fora (normal out_n)."""
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    n = max(3, int(L / step))
    nz = _noise(L, s)
    fp0 = _fiber_profile(L, fiber_e or 1.0)
    fp = fp0 if fiber_e else (lambda u: 0)
    pts = []
    for i in range(n + 1):
        t = i / n
        u = t * L
        taper = min(1.0, t * L / 6, (1 - t) * L / 6)
        d = nz(u) * taper + fp(u) * taper
        pts.append((p0[0] + (p1[0] - p0[0]) * t + out_n[0] * d,
                    p0[1] + (p1[1] - p0[1]) * t + out_n[1] * d))
    return pts


def _fiber_width(w, h):
    return max(3.0, min(11.0, min(w, h) * 0.055))


BLEND = "multiply"


def _riso(poly_pts, fill, tr="", idattr="", opacity=None):
    pts = fmt(poly_pts)
    op = f";opacity:{opacity}" if opacity else ""
    blend = f' style="mix-blend-mode:{BLEND}{op}"' if BLEND else (f' opacity="{opacity}"' if opacity else "")
    return (f'<g{idattr}{tr}{blend}><polygon points="{pts}" fill="{fill}"/>'
            f'<polygon points="{pts}" fill="url(#grain)"/></g>')


def torn_rect(x, y, w, h, fill, rot=0, jag=3, step=16, name=None, opacity=None, fiber=True, paper=False):
    """Forma de cor. Padrão: corte limpo + grão de risografia + multiply.
    paper=True: tira de papel rasgado com fibra branca (para textos e fotos)."""
    if not paper:
        tr = f' transform="rotate({rot} {x + w / 2:.1f} {y + h / 2:.1f})"' if rot else ""
        idattr = f' id="{name}"' if name else ""
        return _riso([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], fill, tr, idattr, opacity)
    return _paper_rect(x, y, w, h, fill, rot, name, opacity, fiber)


def _paper_rect(x, y, w, h, fill, rot=0, name=None, opacity=None, fiber=True):
    """Pedaço de papel rasgado no padrão do lockup: quadrilátero levemente torto,
    topo/base rasgados com ondulação irregular, fibra branca de largura variável
    em uma ou nas duas bordas rasgadas, laterais em corte reto."""
    s = max(0.45, min(1.3, min(w, h) / 150))
    e = _fiber_width(w, h)
    k = min(w, h) * 0.035
    c = [(x + rng.uniform(-k, k), y + rng.uniform(-k, k)),
         (x + w + rng.uniform(-k, k), y + rng.uniform(-k, k)),
         (x + w + rng.uniform(-k, k), y + h + rng.uniform(-k, k)),
         (x + rng.uniform(-k, k), y + h + rng.uniform(-k, k))]
    ft, fb = rng.random() < 0.75, rng.random() < 0.6
    if not (ft or fb):
        ft = True
    seed = rng.random()

    def shape(ext):
        r = random.Random(seed)  # mesma forma-base para cor e fibra
        st = rng.getstate()
        rng.seed(r.random())
        top = _torn_edge(c[0], c[1], s, (0, -1), e if (ext and ft) else 0)
        rng.seed(r.random())
        bot = _torn_edge(c[2], c[3], s, (0, 1), e if (ext and fb) else 0)
        rng.setstate(st)
        return top + bot

    parts = []
    if fiber:
        parts.append(f'<polygon points="{fmt(shape(True))}" fill="{FIBER}"/>')
    parts.append(f'<polygon points="{fmt(shape(False))}" fill="{fill}"/>')
    tr = f' transform="rotate({rot} {x + w / 2:.1f} {y + h / 2:.1f})"' if rot else ""
    op = f' opacity="{opacity}"' if opacity else ""
    idattr = f' id="{name}"' if name else ""
    return f'<g{idattr}{tr}{op}>{"".join(parts)}</g>'


def torn_arc(cx, cy, r, fill, a0=0, a1=360, jag=2.5, rot=0, name=None, fiber=True, paper=False):
    """Círculo/semicírculo. Padrão: corte limpo + grão + multiply."""
    if not paper:
        n = max(48, int(abs(a1 - a0) / 2))
        pts = [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
                cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
        tr = f' transform="rotate({rot} {cx} {cy})"' if rot else ""
        idattr = f' id="{name}"' if name else ""
        return _riso(pts, fill, tr, idattr)
    return _paper_arc(cx, cy, r, fill, a0, a1, rot, name, fiber)


def _paper_arc(cx, cy, r, fill, a0=0, a1=360, rot=0, name=None, fiber=True):
    """Círculo (ou semicírculo) de papel rasgado no padrão do lockup."""
    full = abs(a1 - a0) >= 360
    L = math.radians(abs(a1 - a0)) * r
    n = max(40, int(L / 4))
    e = _fiber_width(r, r)
    s = max(0.45, min(1.3, r / 120))
    seed = rng.random()

    def shape(ext):
        st = rng.getstate()
        rng.seed(seed)
        nz = _noise(L, s)
        fp = _fiber_profile(L, e)
        pts = []
        for i in range(n + 1):
            t = i / n
            u = t * L
            a = math.radians(a0 + (a1 - a0) * t)
            k = 1.0 if full else min(1.0, t * L / 10, (1 - t) * L / 10)
            rr = r + nz(u) * k + (fp(u) * k if ext else 0)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        rng.setstate(st)
        return pts

    parts = []
    if fiber:
        parts.append(f'<polygon points="{fmt(shape(True))}" fill="{FIBER}"/>')
    parts.append(f'<polygon points="{fmt(shape(False))}" fill="{fill}"/>')
    tr = f' transform="rotate({rot} {cx} {cy})"' if rot else ""
    idattr = f' id="{name}"' if name else ""
    return f'<g{idattr}>{"".join(parts)}</g>' if not rot else f'<g{idattr}{tr}>{"".join(parts)}</g>'


def arcs(cx, cy, r0, n, gap, color=BLUE, width=6, a0=180, a1=270, name="arcos"):
    """Arcos concêntricos."""
    out = []
    for i in range(n):
        r = r0 + i * gap
        s = math.radians(a0)
        e = math.radians(a1)
        x1, y1 = cx + r * math.cos(s), cy + r * math.sin(s)
        x2, y2 = cx + r * math.cos(e), cy + r * math.sin(e)
        large = 1 if (a1 - a0) % 360 > 180 else 0
        out.append(
            f'<path d="M{x1:.1f},{y1:.1f} A{r},{r} 0 {large} 1 {x2:.1f},{y2:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{width * 1.25:.1f}" stroke-linecap="butt"/>'
        )
    return f'<g id="{name}">{"".join(out)}</g>'


def starburst(cx, cy, r_in, r_out, n=16, color=BLACK, width=3, name="explosao"):
    out = []
    r_in = 0
    width = max(1.5, width * 0.8)
    for i in range(n):
        a = 2 * math.pi * i / n + rng.uniform(-0.02, 0.02)
        ro = r_out * rng.uniform(0.96, 1.0)
        out.append(
            f'<line x1="{cx + r_in * math.cos(a):.1f}" y1="{cy + r_in * math.sin(a):.1f}" '
            f'x2="{cx + ro * math.cos(a):.1f}" y2="{cy + ro * math.sin(a):.1f}" '
            f'stroke="{color}" stroke-width="{width}" stroke-linecap="butt"/>'
        )
    return f'<g id="{name}">{"".join(out)}</g>'


def dots(x, y, w, h, gap=14, r=2.6, color=BLACK, name="textura-pontos"):
    out = []
    row = 0
    yy = y
    while yy <= y + h:
        xx = x + (gap / 2 if row % 2 else 0)
        while xx <= x + w:
            out.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="{r}"/>')
            xx += gap
        yy += gap
        row += 1
    return f'<g id="{name}" fill="{color}">{"".join(out)}</g>'


def text(x, y, s, size, family=SANS, fill=BLACK, weight=None, italic=False,
         anchor="start", rot=0, ls=None):
    s = s.replace("&", "&amp;")
    attrs = [f'x="{x}"', f'y="{y}"', f'font-family="{family}"', f'font-size="{size}"',
             f'fill="{fill}"', f'text-anchor="{anchor}"']
    if weight:
        attrs.append(f'font-weight="{weight}"')
    if italic:
        attrs.append('font-style="italic"')
    if ls is not None:
        attrs.append(f'letter-spacing="{ls}"')
    if rot:
        attrs.append(f'transform="rotate({rot} {x} {y})"')
    return f'<text {" ".join(attrs)}>{s}</text>'


def g(body, x=0, y=0, scale=1, rot=0, name=None):
    tr = f"translate({x} {y})"
    if rot:
        tr += f" rotate({rot})"
    if scale != 1:
        tr += f" scale({scale})"
    idattr = f' id="{name}"' if name else ""
    return f'<g{idattr} transform="{tr}">{body}</g>'


def clipped(w, h, body, cid, rx=0):
    """Agrupa body dentro de uma máscara retangular (vira mask no Figma)."""
    return (f'<clipPath id="{cid}"><rect width="{w}" height="{h}" rx="{rx}"/></clipPath>'
            f'<g clip-path="url(#{cid})">{body}</g>')


def logo(x, y, size=40, color=BLACK, inner=None):
    """Logo Sizebay: símbolo (mesmo de gerar_logo.py) + nome."""
    from gerar_logo import MARK
    k = size * 0.95 / 92
    mark = (f'<g fill="{color}" transform="translate(0 {-size * 0.82:.1f}) scale({k:.4f})">'
            + "".join(f'<path d="{d}"/>' for d in MARK) + "</g>")
    word = text(100 * k + size * 0.22, 0, "Sizebay", size, SANS, color, weight=700, ls=-1)
    return g(mark + word, x, y, name="logo-sizebay")


# ---------- Lettering do título ----------
_LOCKUP = None
LOCKUP_BOX = (302, 144, 2910, 1568)  # área útil no viewBox do SVG vetorizado


def title_lockup(width=800):
    """Lockup oficial vetorizado (svg/logo/kickoff2026-lockup-papel.svg), ~800 x 431."""
    global _LOCKUP
    if _LOCKUP is None:
        src = (OUT / "logo" / "kickoff2026-lockup-papel.svg").read_text()
        inner = src.split(">", 1)[1].rsplit("</svg>", 1)[0]
        import re as _re
        def _gr(m):
            p = m.group(0)
            if 'papel-borda' in p or 'creme-texto' in p or 'preto' in p:
                return p
            return p + _re.sub(r'fill="#[0-9A-Fa-f]{6}"', 'fill="url(#grain-soft)"', p).replace('data-camada="', 'data-camada="grao-', 1)
        _LOCKUP = _re.sub(r"<path [^>]*/>", _gr, inner)
    bx, by, bw, bh = LOCKUP_BOX
    k = width / bw
    return (f'<g id="lockup-kickoff-2026" transform="scale({k:.5f}) translate({-bx} {-by})">'
            f'{_LOCKUP}</g>')


def tagline(size=40):
    """'Alone we fit well. / Together, we fit perfectly.' em tira de papel."""
    w = size * 14.5
    b = torn_rect(0, 0, w, size * 3.2, PAPER, jag=4, rot=-1, paper=True)
    b += text(size * 0.8, size * 1.35, "Alone we fit well.", size, SANS, BLACK)
    b += torn_rect(size * 0.6, size * 1.85, size * 12.6, size * 1.1, YELLOW, jag=2, paper=True, fiber=False)
    b += text(size * 0.8, size * 2.65, "Together, we fit perfectly.", size, SANS, BLACK, weight=700)
    return b


def photo(x, y, w, h, label, rot=0):
    return g(torn_rect(0, 0, w, h, PHOTO, jag=5, paper=True)
             + text(w / 2, h / 2, label, 28, SANS, "#8A8275", weight=700, anchor="middle"),
             x, y, rot=rot, name=label.lower().replace(" ", "-"))


# ---------- Arquivos ----------
def paleta():
    W, H = 1600, 900
    b = [text(80, 110, "KICKOFF 2026 — PALETA & TIPOGRAFIA", 40, DISPLAY, BLACK)]
    cores = [("Azul Cobalto", BLUE), ("Azul Claro", BLUE_LIGHT), ("Vermelho", RED),
             ("Amarelo Limão", YELLOW), ("Rosa", PINK), ("Preto", BLACK), ("Creme", CREAM)]
    for i, (n, c) in enumerate(cores):
        x = 80 + i * 205
        b.append(g(f'<rect width="180" height="180" rx="16" fill="{c}" stroke="#00000022"/>'
                   + text(0, 220, n, 22, SANS, BLACK, weight=700)
                   + text(0, 250, c, 20, SANS, "#555"), x, 160, name=f"cor-{n.lower().replace(' ', '-')}"))
    b.append(text(80, 520, "Aa", 120, DISPLAY, BLACK))
    b.append(text(280, 470, "Display / Títulos", 26, SANS, BLACK, weight=700))
    b.append(text(280, 510, "Archivo Black — TOGETHER, FIT, KICKOFF 2026", 24, SANS, "#555"))
    b.append(text(80, 680, "Aa", 120, SERIF, BLACK, italic=True))
    b.append(text(280, 630, "Destaque / “we”", 26, SANS, BLACK, weight=700))
    b.append(text(280, 670, "DM Serif Display Italic", 24, SANS, "#555"))
    b.append(text(80, 840, "Aa", 120, SANS, BLACK))
    b.append(text(280, 790, "Apoio / Textos", 26, SANS, BLACK, weight=700))
    b.append(text(280, 830, "DM Sans Regular & Bold", 24, SANS, "#555"))
    save("01-paleta-tipografia.svg", svg(W, H, "".join(b), PAPER))


def elementos():
    W, H = 1600, 1000
    b = [text(80, 90, "ELEMENTOS DA IDENTIDADE", 36, DISPLAY, BLACK)]
    b.append(torn_rect(80, 140, 300, 170, "#E9E4DA", jag=6, rot=-3, name="papel-rasgado", paper=True))
    b.append(starburst(560, 225, 14, 95, 18, BLACK, 3))
    b.append(arcs(860, 330, 60, 6, 18, BLUE, 6, 180, 300))
    b.append(dots(1180, 140, 300, 170, 15, 3))
    b.append(torn_rect(80, 430, 220, 150, BLUE, rot=-4, name="recorte-azul"))
    b.append(torn_rect(360, 450, 230, 130, RED, rot=3, name="recorte-vermelho"))
    b.append(torn_rect(650, 440, 240, 140, YELLOW, rot=-2, name="recorte-amarelo"))
    b.append(torn_rect(950, 455, 280, 110, PINK, rot=2, name="recorte-rosa"))
    b.append(torn_rect(1290, 440, 220, 140, BLUE_LIGHT, rot=-3, name="recorte-azul-claro"))
    b.append(torn_arc(230, 860, 150, RED, 180, 360, name="semicirculo-vermelho"))
    b.append(torn_arc(560, 780, 110, YELLOW, name="circulo-amarelo"))
    b.append(torn_arc(860, 780, 110, RED, name="circulo-vermelho"))
    b.append(arcs(1260, 920, 50, 7, 18, BLUE, 6, 200, 340, name="arcos-2"))
    save("02-elementos-graficos.svg", svg(W, H, "".join(b), PAPER))


def lettering():
    W, H = 900, 520
    save("03-lettering-titulo.svg", svg(W, H, g(title_lockup(), 50, 40, name="lockup-together-we-fit")))
    save("03b-lema.svg", svg(640, 150, g(tagline(40), 10, 10, name="lema")))


def key_visual():
    W, H = 1920, 1080
    b = []
    b.append(arcs(1050, 300, 120, 6, 22, BLUE, 7, 160, 340, name="arcos-topo"))
    b.append(torn_arc(1250, 120, 190, YELLOW, name="circulo-amarelo"))
    b.append(torn_rect(60, 260, 260, 420, BLUE, rot=-6))
    b.append(torn_rect(300, 120, 230, 360, RED, rot=4))
    b.append(torn_rect(1500, 160, 260, 380, BLUE, rot=5))
    b.append(torn_rect(1700, 520, 200, 260, YELLOW, rot=-4))
    for i, (x, y, w, h, r) in enumerate([(70, 140, 300, 560, -3), (360, 90, 300, 540, 2),
                                         (650, 60, 300, 520, -1), (940, 80, 300, 540, 2),
                                         (1230, 120, 300, 560, -2), (1520, 140, 330, 600, 3)]):
        b.append(photo(x, y, w, h, f"FOTO {i + 1}", r))
    b.append(starburst(270, 900, 18, 120, 18))
    b.append(starburst(140, 90, 12, 70, 16))
    b.append(torn_rect(170, 940, 180, 120, YELLOW, rot=-8))
    b.append(torn_rect(380, 960, 120, 90, BLUE, rot=10))
    b.append(torn_arc(1660, 900, 130, RED, name="circulo-vermelho"))
    b.append(arcs(1880, 760, 80, 6, 20, BLUE, 7, 120, 250, name="arcos-direita"))
    b.append(logo(1640, 90, 44))
    b.append(g(title_lockup(), 520, 400, 1.1, name="lockup"))
    b.append(g(tagline(40), 640, 900, name="lema"))
    save("04-key-visual-16x9.svg", svg(W, H, "".join(b), CREAM))


def telao():
    W, H = 3840, 1080
    b = [f'<rect width="760" height="{H}" fill="{BLUE}"/>', logo(200, 560, 80, CREAM, BLUE),
         arcs(760, 1080, 120, 7, 26, CREAM, 8, 270, 360, name="arcos-painel")]
    b.append(torn_rect(720, 760, 240, 260, RED, rot=-6))
    for i in range(6):
        b.append(photo(900 + i * 330, 90 + (i % 2) * 40, 320, 860, f"FOTO {i + 1}", (-2, 2)[i % 2]))
    b.append(torn_arc(1450, 160, 170, YELLOW))
    b.append(arcs(1300, 240, 90, 6, 22, BLUE, 7, 160, 330, name="arcos-topo"))
    b.append(starburst(2700, 140, 16, 100))
    b.append(g(title_lockup(), 2900, 200, 1.1, name="lockup"))
    b.append(g(tagline(34), 3150, 760, name="lema"))
    b.append(arcs(3840, 1080, 100, 7, 24, BLUE, 7, 180, 270, name="arcos-canto"))
    save("05-telao-palco-32x9.svg", svg(W, H, "".join(b), CREAM))


def cracha():
    W, H = 600, 900
    slot = f'<rect x="250" y="40" width="100" height="22" rx="11" fill="#00000033"/>'
    f = [f'<rect width="{W}" height="{H}" rx="40" fill="{PAPER}"/>', slot, logo(50, 130, 36)]
    f.append(starburst(510, 120, 8, 50, 14, BLACK, 2))
    f.append(torn_rect(430, 160, 130, 120, PINK, rot=6))
    f.append(g(title_lockup(), 40, 210, 0.64, name="lockup"))
    f.append(text(60, 650, "Ana Prado", 56, SANS, BLACK, weight=700))
    f.append(text(60, 700, "Produto", 34, SANS, "#333"))
    f.append(torn_rect(-20, 780, 220, 140, BLUE, rot=-4))
    f.append(torn_arc(560, 860, 120, RED, 180, 360))
    f.append(arcs(600, 900, 60, 4, 18, BLUE, 5, 180, 270))
    save("06-cracha-frente.svg", svg(W, H, clipped(W, H, "".join(f), "cf", 40)))

    v = [f'<rect width="{W}" height="{H}" rx="40" fill="{BLUE}"/>', slot]
    v.append(arcs(0, 330, 60, 6, 22, CREAM, 5, 270, 360, name="arcos"))
    v.append(starburst(450, 260, 12, 90, 16, CREAM, 3))
    v.append(text(70, 500, "Together", 76, SANS, CREAM))
    v.append(text(110, 590, "we fit", 76, SANS, CREAM))
    v.append(torn_rect(-20, 700, 300, 230, PINK, rot=-3))
    v.append(torn_arc(470, 790, 160, YELLOW))
    v.append(torn_rect(250, 760, 180, 150, YELLOW, rot=8, opacity=0.9))
    save("07-cracha-verso.svg", svg(W, H, clipped(W, H, "".join(v), "cv", 40)))


def estampa():
    W, H = 1200, 1200
    b = [torn_rect(200, 180, 420, 400, BLUE, rot=-5),
         torn_arc(560, 330, 200, RED, 180, 360),
         torn_rect(620, 260, 300, 260, PINK, rot=4, opacity=0.85),
         starburst(960, 300, 16, 130, 18),
         g(title_lockup(), 200, 470, 0.95, name="lockup"),
         torn_rect(780, 860, 220, 170, YELLOW, rot=-6),
         torn_rect(260, 900, 160, 120, BLUE, rot=8),
         starburst(250, 980, 10, 70, 14)]
    save("08-estampa-camiseta-ecobag.svg", svg(W, H, "".join(b)))


def banners():
    BW, BH, gap = 400, 1400, 60
    W = 4 * BW + 5 * gap
    b = []
    x = gap
    # 1 — creme com logo
    b.append(g(clipped(BW, BH, f'<rect width="{BW}" height="{BH}" fill="{PAPER}"/>'
               + torn_rect(-20, -20, 300, 360, YELLOW, rot=-6) + torn_rect(160, 120, 220, 300, BLUE, rot=8)
               + logo(90, 700, 50) + arcs(0, BH, 80, 7, 24, BLUE, 6, 270, 360)
               + torn_rect(220, 1100, 200, 320, RED, rot=-4), "cb1"), x, 60, name="banner-1-logo"))
    x += BW + gap
    b.append(g(clipped(BW, BH, f'<rect width="{BW}" height="{BH}" fill="{BLUE}"/>'
               + text(275, 1180, "TOGETHER", 150, DISPLAY, CREAM, rot=-90)
               + torn_arc(380, 1350, 130, PINK) + torn_arc(40, 60, 100, RED), "cb2"), x, 60, name="banner-2-together"))
    x += BW + gap
    b.append(g(clipped(BW, BH, f'<rect width="{BW}" height="{BH}" fill="{RED}"/>'
               + text(200, 760, "we", 230, SERIF, CREAM, italic=True, anchor="middle")
               + torn_rect(250, 1180, 200, 260, BLUE, rot=6), "cb3"), x, 60, name="banner-3-we"))
    x += BW + gap
    b.append(g(clipped(BW, BH, f'<rect width="{BW}" height="{BH}" fill="{YELLOW}"/>'
               + text(200, 760, "FIT", 170, DISPLAY, BLACK, anchor="middle")
               + starburst(200, 1150, 14, 120, 18) + torn_rect(-40, -20, 200, 180, PINK, rot=-8), "cb4"),
               x, 60, name="banner-4-fit"))
    save("09-banners-verticais.svg", svg(W, BH + 120, "".join(b)))


def parede():
    W, H = 2400, 1200
    b = [torn_rect(-40, -30, 520, 420, RED, rot=-5),
         torn_rect(260, -40, 380, 300, BLUE, rot=8),
         torn_arc(380, 820, 260, YELLOW, 90, 270),
         torn_rect(-40, 900, 300, 330, BLUE, rot=4),
         arcs(560, 1200, 120, 7, 28, BLUE, 8, 180, 300, name="arcos"),
         starburst(2050, 330, 24, 230, 20, BLACK, 5),
         torn_rect(2200, 700, 260, 520, YELLOW, rot=-3),
         g(tagline(90), 900, 360, name="lema")]
    save("10-parede-lounge.svg", svg(W, H, "".join(b), PAPER))


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    paleta(); elementos(); lettering(); key_visual(); telao()
    cracha(); estampa(); banners(); parede()
