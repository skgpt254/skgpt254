#!/usr/bin/env python3
"""
Generate the profile hero banner — banner.svg (light) and banner-dark.svg.

Portrait is a halftone dot-matrix built from the real photo (same spirit
as the arifhaxn reference, tuned for actual recognizability: unsharp mask
+ contrast boost before sampling, 120-column grid so glasses/facial
structure survive). It's real vector circles, not a raster image, and the
whole cluster breathes (scales gently, forever) so there's genuine
ongoing motion, not a one-shot transition that finishes before anyone
notices. Facts row and link row were deliberately removed earlier —
those live as real clickable badges in README.md instead, since links
and interaction inside an SVG do nothing once it's embedded via <img>.

Usage:
    python3 generate_banner.py
"""
import os
import math
import html

from PIL import Image, ImageOps, ImageEnhance, ImageFilter

# ---------------------------------------------------------------- CONFIG ---
CONFIG = {
    "name": "Sandesh Kumar Gupta",
    "role": "Security Engineer — Systems, Offensive Security & Applied ML",
    "bio": [
        "Pre-final year CS undergraduate at GLA University, building",
        "kernel-level defenses, network detection engines, and ML-driven security tooling.",
    ],
    "github_handle": "github.com/skgpt254",
    "photo": "../../assets/portrait_source.jpg",
    "out_light": "../../banner.svg",
    "out_dark": "../../banner-dark.svg",
}

# ----------------------------------------------------------------- THEME ---
THEMES = {
    "light": dict(ink="#1C1B18", muted="#6E6B63", line="#DEDACD", accent="#0E6E63"),
    "dark":  dict(ink="#F3F1EC", muted="#A8A399", line="#3B372F", accent="#2DD9B5"),
}

SERIF = "Georgia,'Iowan Old Style','Palatino Linotype',serif"
MONO  = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

W, H = 1180, 450
MARGIN = 56

def esc(s):
    return html.escape(str(s), quote=True)

# ------------------------------------------------------------- PORTRAIT ---
def halftone_circles(path, cols, out_w, out_h, crop_frac,
                      gamma=1.0, max_r_ratio=0.62, min_r=0.25):
    """Grayscale photo -> vector halftone dots. crop_frac = (left, top, right,
    bottom) as fractions of the source image, applied before sampling."""
    im = Image.open(path).convert("L")
    im = ImageOps.exif_transpose(im)
    w, h = im.size
    l, t, r, b = crop_frac
    im = im.crop((int(w * l), int(h * t), int(w * r), int(h * b)))
    im = im.filter(ImageFilter.UnsharpMask(radius=3, percent=180, threshold=2))
    im = ImageOps.autocontrast(im, cutoff=0.3)
    im = ImageEnhance.Contrast(im).enhance(1.25)

    cell = out_w / cols
    rows = round(out_h / cell)
    small = im.resize((cols, rows), Image.LANCZOS)
    px = small.load()
    r_max = cell * max_r_ratio / 2

    circles = []
    for y in range(rows):
        for x in range(cols):
            v = px[x, y] / 255.0
            dark = (1 - v) ** gamma
            rad = dark * r_max
            if rad < min_r:
                continue
            cx = x * cell + cell / 2
            cy = y * cell + cell / 2
            circles.append((round(cx, 1), round(cy, 1), round(rad, 2)))
    return circles

# --------------------------------------------------------------- BUILD ---
def build(cfg, theme_name):
    t = THEMES[theme_name]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    photo_path = os.path.normpath(os.path.join(base_dir, cfg["photo"]))

    portrait_w, portrait_h = 264, 318
    px, py = MARGIN, 96
    accent, ink, muted, line = t["accent"], t["ink"], t["muted"], t["line"]

    circles = halftone_circles(photo_path, cols=120, out_w=portrait_w, out_h=portrait_h,
                                crop_frac=(0.07, 0.015, 0.93, 1.0))

    text_x = px + portrait_w + 44

    s = []
    a = s.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
      f'width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
      f'aria-label="{esc(cfg["name"])} — {esc(cfg["role"])}">')
    # no background rect — transparent, sits directly on GitHub's page

    # ---- header: monogram with a continuously rotating ring ----
    ring_cx, ring_cy, ring_r = MARGIN + 18, 52, 18
    circumference = 2 * math.pi * ring_r
    dash = circumference * 0.72
    gap = circumference - dash
    a(f'<g>'
      f'<animateTransform attributeName="transform" type="rotate" '
      f'from="0 {ring_cx} {ring_cy}" to="360 {ring_cx} {ring_cy}" dur="6s" repeatCount="indefinite"/>'
      f'<circle cx="{ring_cx}" cy="{ring_cy}" r="{ring_r}" fill="none" stroke="{accent}" '
      f'stroke-width="1.6" stroke-linecap="round" '
      f'stroke-dasharray="{dash:.1f} {gap:.1f}"/></g>')
    initials = "".join(w[0] for w in cfg["name"].split()[:2]).upper()
    a(f'<text x="{ring_cx}" y="57" text-anchor="middle" font-family="{SERIF}" font-weight="700" '
      f'font-size="14" fill="{ink}">{esc(initials)}</text>')
    a(f'<text x="{W-MARGIN}" y="57" text-anchor="end" font-family="{MONO}" font-size="12.5" '
      f'fill="{muted}">{esc(cfg["github_handle"])}</text>')
    a(f'<line x1="{MARGIN}" y1="84" x2="{W-MARGIN}" y2="84" stroke="{line}"/>')

    # ---- portrait: halftone dot-matrix, whole cluster breathing forever ----
    cx_center, cy_center = px + portrait_w / 2, py + portrait_h / 2
    dots = "".join(f'<circle cx="{px+cx:.1f}" cy="{py+cy:.1f}" r="{r}" fill="{accent}"/>'
                    for cx, cy, r in circles)
    a(f'<g transform="translate({cx_center:.1f},{cy_center:.1f})">'
      f'<g><animateTransform attributeName="transform" type="scale" '
      f'values="1;1.035;1" dur="5s" repeatCount="indefinite" calcMode="spline" '
      f'keySplines="0.4 0 0.6 1;0.4 0 0.6 1" keyTimes="0;0.5;1"/>'
      f'<g transform="translate({-cx_center:.1f},{-cy_center:.1f})">{dots}</g>'
      f'</g></g>')

    # ---- name / role / rule — vertically balanced alongside the portrait ---
    name_y = py + 80
    a(f'<text x="{text_x}" y="{name_y}" font-family="{SERIF}" font-weight="700" font-size="40" '
      f'fill="{ink}">{esc(cfg["name"])}</text>')
    a(f'<text x="{text_x}" y="{name_y+27}" font-family="{MONO}" font-size="14.5" '
      f'fill="{muted}">{esc(cfg["role"])}</text>')
    rule_y = name_y + 61
    a(f'<line x1="{text_x}" y1="{rule_y}" x2="{text_x+64}" y2="{rule_y}" stroke="{accent}" stroke-width="2.5">'
      f'<animate attributeName="x2" from="{text_x}" to="{text_x+64}" '
      f'dur="0.7s" begin="0.2s" fill="freeze" calcMode="spline" keySplines="0.3 0 0.2 1" keyTimes="0;1"/></line>')

    # ---- bio ----
    bio_y = rule_y + 30
    for i, line_txt in enumerate(cfg["bio"]):
        a(f'<text x="{text_x}" y="{bio_y + i*20}" font-family="{SERIF}" font-size="15.5" '
          f'fill="{ink}" opacity="0.9">{esc(line_txt)}</text>')

    a('</svg>')
    return "".join(s)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for theme_name, out_key in (("light", "out_light"), ("dark", "out_dark")):
        svg = build(CONFIG, theme_name)
        out_path = os.path.normpath(os.path.join(base_dir, CONFIG[out_key]))
        with open(out_path, "w") as f:
            f.write(svg)
        print(f"wrote {out_path} ({len(svg)//1024} KB)")
