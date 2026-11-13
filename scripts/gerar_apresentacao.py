"""Apresentação do key visual Kickoff 2026 — slides 1920x1080 em SVG.

Rode antes: gerar_logo.py e gerar_svgs.py (os slides reaproveitam os SVGs gerados).
Uso:  python3 scripts/gerar_apresentacao.py   (saída em ./svg/apresentacao)
"""
import re
from pathlib import Path

from gerar_svgs import (BLACK, BLUE, BLUE_LIGHT, CREAM, DISPLAY, PAPER, PINK, RED, SANS,
                        SERIF, YELLOW, arcs, clipped, dots, g, starburst, svg, tagline, text,
                        title_lockup, torn_arc, torn_rect)

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "svg"
OUT = SRC / "apresentacao"
W, H = 1920, 1080
TOTAL = 11
GREY = "#5A5650"


def embed(path, x, y, width, cid, rx=0):
    s = (SRC / path).read_text()
    m = re.search(r'width="([\d.]+)" height="([\d.]+)"', s)
    sw, sh = float(m.group(1)), float(m.group(2))
    inner = s.split(">", 1)[1].rsplit("</svg>", 1)[0]
    inner = re.sub(r'id="(c[bfv]\d?)"', lambda mm: f'id="{cid}-{mm.group(1)}"', inner)
    inner = re.sub(r'url\(#(c[bfv]\d?)\)', lambda mm: f'url(#{cid}-{mm.group(1)})', inner)
    k = width / sw
    return g(clipped(sw, sh, inner, cid, rx), x, y, k, name=cid), sh * k


def chrome(n, title=None, kicker=None, dark=False):
    fg = CREAM if dark else BLACK
    b = text(80, 70, "KICKOFF 2026 · KEY VISUAL", 18, SANS, fg, weight=700, ls=2)
    b += text(W - 80, 70, f"{n:02d} / {TOTAL:02d}", 18, SANS, fg, weight=700, anchor="end")
    if kicker:
        b += text(80, 170, kicker.upper(), 22, SANS, BLUE if not dark else YELLOW, weight=700, ls=3)
    if title:
        b += text(80, 250, title, 72, DISPLAY, fg)
    return b


def para(x, y, lines, size=28, color=GREY, lh=1.45, weight=None):
    return "".join(text(x, y + i * size * lh, l, size, SANS, color, weight=weight)
                   for i, l in enumerate(lines))


def save(n, name, body, bg=CREAM):
    (OUT / f"{n:02d}-{name}.svg").write_text(svg(W, H, body, bg))
    print("ok", n, name)


def s01_capa():
    body, _ = embed("04-key-visual-16x9.svg", 0, 0, W, "kv")
    save(1, "capa", body)


def s02_conceito():
    b = chrome(2, "Together we fit", "Conceito")
    b += para(80, 340, [
        "Sozinhos, a gente já encaixa bem. Juntos, o encaixe fica perfeito.",
        "",
        "Assim como a Sizebay encontra o caimento certo para cada pessoa,",
        "cada time encontra o seu lugar quando trabalha junto. A identidade",
        "do Kickoff 2026 traduz essa ideia em colagem: peças diferentes —",
        "cores, recortes, texturas e pessoas — que só fazem sentido juntas.",
    ], 30)
    b += text(80, 720, "PALAVRAS-CHAVE", 20, SANS, BLUE, weight=700, ls=3)
    for i, w in enumerate(["Coletivo", "Diversidade", "Encaixe", "Energia", "Moda"]):
        col = [BLUE, RED, YELLOW, PINK, BLUE_LIGHT][i]
        fg = BLACK if col in (YELLOW, PINK, BLUE_LIGHT) else CREAM
        b += g(torn_rect(0, 0, 230, 70, col, jag=2) + text(115, 46, w, 28, SANS, fg, weight=700, anchor="middle"),
               80 + i * 250, 750, rot=(-2, 2)[i % 2])
    b += g(tagline(44), 1180, 360, rot=-2, name="lema")
    b += starburst(1720, 760, 18, 130, 18)
    b += arcs(1920, 1080, 120, 6, 26, BLUE, 7, 180, 270)
    b += torn_arc(1350, 900, 110, RED)
    save(2, "conceito", b)


def s03_logo():
    b = chrome(3, "Assinaturas", "Logo & lockup")
    lk, _ = embed("logo/sizebay-logo-preto.svg", 80, 330, 640, "lg1")
    b += f'<rect x="60" y="300" width="700" height="260" rx="16" fill="{PAPER}"/>' + lk
    b += f'<rect x="60" y="590" width="340" height="180" rx="16" fill="{BLUE}"/>'
    b += embed("logo/sizebay-logo-branco.svg", 85, 640, 290, "lg2")[0]
    b += f'<rect x="420" y="590" width="340" height="180" rx="16" fill="{BLACK}"/>'
    b += embed("logo/sizebay-logo-branco.svg", 445, 640, 290, "lg3")[0]
    b += para(80, 830, ["Logo Sizebay: preto em fundos claros, creme sobre azul ou preto.",
                        "Área de respiro mínima = altura do círculo do símbolo."], 22)
    b += g(title_lockup(), 960, 330, 1.0, name="lockup")
    b += para(980, 830, ["Lockup do evento: lettering exclusivo em papel rasgado.",
                         "Use sempre o arquivo vetorizado, inteiro e sem redesenhar."], 22)
    save(3, "logo", b)


def s04_cores():
    b = chrome(4, "Paleta", "Cores")
    cores = [("Azul Cobalto", BLUE, "0, 23, 200", "Cor principal", 30, CREAM),
             ("Vermelho", RED, "251, 45, 11", "Energia", 18, CREAM),
             ("Amarelo Limão", YELLOW, "227, 237, 6", "Destaque", 18, BLACK),
             ("Rosa", PINK, "238, 111, 203", "Apoio", 8, BLACK),
             ("Azul Claro", BLUE_LIGHT, "123, 149, 242", "Apoio", 6, BLACK),
             ("Preto", BLACK, "5, 5, 5", "Texto", 10, CREAM),
             ("Creme", CREAM, "253, 237, 216", "Fundo", 0, BLACK)]
    x = 80
    for i, (n, c, rgb, uso, pct, fg) in enumerate(cores):
        w = 230
        b += g(torn_rect(0, 0, w, 420, c, jag=3)
               + text(24, 50, n, 26, SANS, fg, weight=700)
               + text(24, 330, c, 26, SANS, fg, weight=700)
               + text(24, 364, f"RGB {rgb}", 18, SANS, fg)
               + text(24, 394, uso, 18, SANS, fg), x + i * 252, 320, name=f"cor-{i}")
    b += text(80, 830, "PROPORÇÃO DE USO", 20, SANS, BLUE, weight=700, ls=3)
    x = 80
    for n, c, _, _, pct, _ in cores:
        if not pct:
            continue
        w = 1760 * pct / 90
        b += f'<rect x="{x:.0f}" y="860" width="{w:.0f}" height="60" fill="{c}"/>'
        b += text(x + 12, 950, f"{pct}%", 20, SANS, GREY, weight=700)
        x += w
    b += para(80, 1010, ["Creme é o fundo base em todas as peças; azul lidera, vermelho e amarelo dão o ritmo."], 20)
    save(4, "cores", b)


def s05_tipografia():
    b = chrome(5, "Tipografia", "Fontes")
    rows = [("Archivo Black", DISPLAY, False, "Display / Títulos",
             "TOGETHER WE FIT", "Caixa alta em títulos de apoio. O lockup é lettering exclusivo (arquivo vetorizado)."),
            ("DM Serif Display Italic", SERIF, True, "Destaque",
             "we", "Só para palavras de destaque, como o “we”. Nunca em textos longos."),
            ("DM Sans Regular & Bold", SANS, False, "Apoio / Textos",
             "Alone we fit well. Together, we fit perfectly.", "Textos corridos, legendas, crachás e sinalização.")]
    for i, (n, fam, it, uso, amostra, regra) in enumerate(rows):
        y = 330 + i * 240
        b += text(80, y + 90, "Aa", 130, fam, BLACK, italic=it)
        b += text(330, y + 10, f"{n} — {uso}", 24, SANS, BLUE, weight=700)
        b += text(330, y + 90, amostra, 64 if i < 2 else 44, fam, BLACK, italic=it)
        b += text(330, y + 140, regra, 22, SANS, GREY)
        b += f'<line x1="80" y1="{y + 185}" x2="1840" y2="{y + 185}" stroke="#00000022" stroke-width="2"/>'
    b += text(1840, 1030, "Todas gratuitas no Google Fonts e disponíveis no Figma.", 20, SANS, GREY, anchor="end")
    save(5, "tipografia", b)


def s06_elementos():
    b = chrome(6, "Elementos gráficos", "Kit de colagem")
    items = [
        (torn_rect(0, 0, 260, 160, "#E2DCCF", rot=-3), "Papel rasgado", "Base para textos e fotos"),
        (starburst(130, 80, 14, 85, 18), "Explosão", "Pontua energia e destaque"),
        (arcs(130, 160, 40, 6, 18, BLUE, 6, 180, 360), "Arcos", "Movimento, ondas de som"),
        (dots(10, 10, 240, 140, 15, 3), "Textura de pontos", "Retícula de impressão"),
    ]
    for i, (el, n, d) in enumerate(items):
        x = 80 + i * 450
        b += g(el, x, 320) + text(x, 540, n, 26, SANS, BLACK, weight=700) + text(x, 574, d, 20, SANS, GREY)
    row = [(BLUE, "rect"), (RED, "rect"), (YELLOW, "rect"), (PINK, "rect"), (RED, "half"), (YELLOW, "circle")]
    for i, (c, t) in enumerate(row):
        x = 80 + i * 300
        if t == "rect":
            el = torn_rect(0, 0, 240, 150, c, rot=(-4, 3)[i % 2])
        elif t == "half":
            el = torn_arc(120, 170, 120, c, 180, 360)
        else:
            el = torn_arc(120, 90, 85, c)
        b += g(el, x, 660)
    b += text(80, 900, "Recortes de papel colorido", 26, SANS, BLACK, weight=700)
    b += para(80, 940, ["Topo e base rasgados com fibra branca; laterais em corte reto. Gire entre −8° e +8°.",
                        "Combine no máximo 3 cores por área para manter a leitura."], 22)
    save(6, "elementos", b)


def s07_construcao():
    b = chrome(7, "Construção", "Como montar")
    b += g(title_lockup(), 80, 330, 0.95, name="lockup")
    labels = [(720, 365, "1  Tag KICKOFF 2026 em amarelo"), (860, 470, "2  TOGETHER no azul"),
              (330, 760, "3  “we” serifado no vermelho"), (720, 760, "4  FIT no amarelo")]
    for x, y, t in labels:
        b += f'<circle cx="{x - 20}" cy="{y - 8}" r="6" fill="{RED}"/>' + text(x, y, t, 22, SANS, BLACK, weight=700)
    b += text(1240, 330, "FAÇA", 24, SANS, BLUE, weight=700, ls=3)
    b += para(1240, 375, ["• Fundo creme com recortes saindo das bordas",
                          "• Pessoas em recorte, olhando para cima",
                          "• Lockup sobreposto às fotos, nunca isolado",
                          "• Lema em tira de papel com marca-texto amarelo",
                          "• Bordas rasgadas com a fibra branca do papel"], 24, BLACK)
    b += text(1240, 650, "EVITE", 24, SANS, RED, weight=700, ls=3)
    b += para(1240, 695, ["• Gradientes, sombras e efeitos 3D",
                          "• Bordas retas e perfeitas nos recortes",
                          "• Texto longo sobre amarelo ou rosa em fonte fina",
                          "• Mais de 3 cores fortes no mesmo bloco"], 24, BLACK)
    b += starburst(1780, 960, 14, 90, 16)
    save(7, "construcao", b)


def s08_palco():
    b = chrome(8, "Palco", "Aplicações · telão")
    kv, h1 = embed("05-telao-palco-32x9.svg", 80, 330, 1760, "tl")
    b += kv + text(80, 330 + h1 + 40, "Telão do palco · 3840 × 1080 (32:9)", 22, SANS, GREY, weight=700)
    b += para(80, 330 + h1 + 90, ["Painel azul com o logo à esquerda, fotos em sequência no centro e o lockup à direita."], 22)
    save(8, "palco", b)


def s09_espaco():
    b = chrome(9, "Espaço", "Aplicações · ambientação")
    bn, h2 = embed("09-banners-verticais.svg", 80, 320, 700, "bn")
    pw, h3 = embed("10-parede-lounge.svg", 860, 320, 980, "pw")
    b += bn + pw
    b += text(80, 320 + h2 + 40, "Banners suspensos · TOGETHER / we / FIT", 22, SANS, GREY, weight=700)
    b += text(860, 320 + h3 + 40, "Parede do lounge com o lema", 22, SANS, GREY, weight=700)
    save(9, "espaco", b)


def s09_pecas():
    b = chrome(10, "Peças", "Aplicações · crachá e brindes")
    f, _ = embed("06-cracha-frente.svg", 80, 300, 420, "cf", 40)
    v, _ = embed("07-cracha-verso.svg", 540, 300, 420, "cv", 40)
    b += f + v
    b += f'<rect x="1040" y="300" width="800" height="600" rx="24" fill="{PAPER}"/>'
    b += embed("08-estampa-camiseta-ecobag.svg", 1140, 300, 600, "es")[0]
    b += text(80, 960, "Crachá · frente e verso · 600 × 900", 20, SANS, GREY, weight=700)
    b += text(1040, 960, "Estampa para camiseta, ecobag e garrafa", 20, SANS, GREY, weight=700)
    save(10, "pecas", b)


def s10_fim():
    b = chrome(11, dark=True)
    b += torn_rect(-40, 760, 520, 360, RED, rot=-4)
    b += torn_arc(1700, 180, 220, YELLOW)
    b += arcs(1920, 1080, 120, 7, 28, CREAM, 8, 180, 270)
    b += starburst(1500, 820, 20, 140, 18, CREAM, 4)
    b += g(title_lockup(), 560, 300, 1.0, name="lockup")
    b += text(960, 860, "Alone we fit well. Together, we fit perfectly.", 40, SANS, CREAM, weight=700, anchor="middle")
    save(11, "encerramento", b, BLACK)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for f in (s01_capa, s02_conceito, s03_logo, s04_cores, s05_tipografia,
              s06_elementos, s07_construcao, s08_palco, s09_espaco, s09_pecas, s10_fim):
        f()
