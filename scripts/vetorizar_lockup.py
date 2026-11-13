"""Vetoriza o lockup 'KICKOFF 2026 / TOGETHER we FIT' a partir da arte de referência.

Reduz a imagem às 6 cores da arte (mantendo as fibras brancas do papel rasgado)
e traça com vtracer em camadas empilhadas.
Uso:  pip install vtracer numpy pillow && python3 scripts/vetorizar_lockup.py
"""
import re
import tempfile
from pathlib import Path

import numpy as np
import vtracer
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "lockup-referencia.webp"
OUT = ROOT / "svg" / "logo"
SCALE = 2

PAL = {  # cor da arte -> nome da camada
    "#FDEDD8": "creme-texto",
    "#E3ED06": "amarelo",
    "#0017C8": "azul",
    "#FB2D0B": "vermelho",
    "#050505": "preto",
    "#F6F3F4": "papel-borda",
}


def hex2rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def quantize(path):
    im = Image.open(path).convert("RGBA")
    im = im.resize((im.width * SCALE, im.height * SCALE), Image.LANCZOS)
    a = np.asarray(im).astype(float)
    pal = np.array([hex2rgb(h) for h in PAL], float)
    idx = ((a[..., None, :3] - pal[None, None]) ** 2).sum(-1).argmin(-1)
    out = np.zeros(a.shape, np.uint8)
    out[..., :3] = pal[idx].astype(np.uint8)
    out[..., 3] = np.where(a[..., 3] > 128, 255, 0)
    return Image.fromarray(out), im.size


def nearest(hexcol):
    c = np.array(hex2rgb(hexcol), float)
    return min(PAL, key=lambda h: ((np.array(hex2rgb(h)) - c) ** 2).sum())


def main():
    q, (w, h) = quantize(SRC)
    with tempfile.TemporaryDirectory() as td:
        qp, sp = Path(td) / "q.png", Path(td) / "t.svg"
        q.save(qp)
        vtracer.convert_image_to_svg_py(
            str(qp), str(sp), colormode="color", hierarchical="stacked", mode="spline",
            filter_speckle=6, color_precision=8, layer_difference=6, corner_threshold=60,
            length_threshold=4.0, max_iterations=10, splice_threshold=45, path_precision=2)
        raw = sp.read_text()
    paths = re.findall(r"<path [^>]*/>", raw)
    body = []
    for p in paths:
        col = nearest(re.search(r'fill="(#[0-9A-Fa-f]{6})"', p).group(1))
        p = re.sub(r'fill="#[0-9A-Fa-f]{6}"', f'fill="{col}"', p)
        body.append(p.replace("<path ", f'<path data-camada="{PAL[col]}" ', 1))
    W, H = w // SCALE, h // SCALE
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {w} {h}"><g id="kickoff-2026-together-we-fit">{"".join(body)}</g></svg>\n')
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "kickoff2026-lockup-papel.svg").write_text(svg)
    print("ok", len(body), "formas")


if __name__ == "__main__":
    main()
