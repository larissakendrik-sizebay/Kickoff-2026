# Kickoff 2026 — Together we fit

Elementos da identidade visual em SVG, prontos para arrastar no Figma (viram camadas editáveis).

| Arquivo | Conteúdo |
|---|---|
| `svg/01-paleta-tipografia.svg` | Paleta (hex) e tipografia |
| `svg/02-elementos-graficos.svg` | Papel rasgado com fibra branca na borda, recortes coloridos, explosão, arcos, textura de pontos, círculos |
| `svg/03-lettering-titulo.svg` | Lockup KICKOFF 2026 / TOGETHER / we FIT |
| `svg/03b-lema.svg` | "Alone we fit well. Together, we fit perfectly." |
| `svg/04-key-visual-16x9.svg` | Key visual 1920×1080 |
| `svg/05-telao-palco-32x9.svg` | Telão do palco 3840×1080 |
| `svg/06-cracha-frente.svg` / `07-cracha-verso.svg` | Crachá 600×900 |
| `svg/08-estampa-camiseta-ecobag.svg` | Arte para camiseta / ecobag / brindes |
| `svg/09-banners-verticais.svg` | 4 banners suspensos |
| `svg/10-parede-lounge.svg` | Parede do lounge com o lema |

**Fontes (Google Fonts, já disponíveis no Figma):** Archivo Black (display), DM Serif Display Italic ("we"), DM Sans (apoio).

**Cores (da arte do lockup):** Azul `#0017C8` · Vermelho `#FB2D0B` · Amarelo `#E3ED06` · Preto `#050505` · Creme `#FDEDD8` · Fibra do papel `#F6F3F4` · Apoio: Rosa `#EE6FCB`, Azul claro `#7B95F2`

**Logo:** `svg/logo/` — logo Sizebay (preto, branco, azul), símbolo isolado e prancha de aplicações. Recriado em vetor a partir do board; confira com o arquivo oficial da marca antes de imprimir.

**Lockup oficial em papel:** `svg/logo/kickoff2026-lockup-papel.svg` — vetorização fiel da arte de referência (`assets/lockup-referencia.webp`), com bordas rasgadas e fibras de papel. Regerar com `python3 scripts/vetorizar_lockup.py` (requer `vtracer`).

**Apresentação de key visual:** `Kickoff2026-KeyVisual.pdf` e slides 1920×1080 em `svg/apresentacao/` (capa, conceito, logo, cores, tipografia, elementos, construção, palco, espaço, peças, encerramento).

**A substituir:** áreas cinza "FOTO 1…6" pelas fotos dos modelos.

Para regenerar: `pip install fonttools`, depois `python3 scripts/gerar_logo.py`, `python3 scripts/gerar_svgs.py` e `python3 scripts/gerar_apresentacao.py`.
