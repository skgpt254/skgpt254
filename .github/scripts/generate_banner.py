#!/usr/bin/env python3
"""
Generate the profile hero banner — banner.svg (light) and banner-dark.svg.

Transparent background, name/role/bio only (no facts row, no link row —
those live as real clickable badges in README.md instead, since links
inside an SVG do nothing once it's embedded via <img>). One continuous
animation (the ring around the monogram slowly rotates, forever) so
there's motion that's actually visible rather than a one-shot fade that
finishes before you notice it.

Usage:
    python3 generate_banner.py
"""
import base64
import io
import os
import math
import html

from PIL import Image, ImageOps, ImageEnhance

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
    "light": dict(
        ink="#1C1B18", muted="#6E6B63", line="#DEDACD", accent="#0E6E63",
        duo_shadow="#12312B", duo_highlight="#F7F5F0",
    ),
    "dark": dict(
        ink="#F3F1EC", muted="#A8A399", line="#3B372F", accent="#2DD9B5",
        duo_shadow="#0E211D", duo_highlight="#E8FBF5",
    ),
}

SERIF = "Georgia,'Iowan Old Style','Palatino Linotype',serif"
MONO  = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

W, H = 1180, 450
MARGIN = 56

def esc(s):
    return html.escape(str(s), quote=True)

# ------------------------------------------------------------- PORTRAIT ---
def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def duotone_portrait(path, shadow_hex, highlight_hex, disp_w, disp_h,
                      contrast=1.15, fade_from=0.62):
    scale = 2
    px_w, px_h = disp_w * scale, disp_h * scale
    target_ratio = disp_w / disp_h

    im = Image.open(path).convert("L")
    im = ImageOps.exif_transpose(im)
    w, h = im.size
    src_ratio = w / h
    if src_ratio > target_ratio:
        new_w = int(h * target_ratio)
        x0 = (w - new_w) // 2
        im = im.crop((x0, 0, x0 + new_w, h))
    else:
        new_h = int(w / target_ratio)
        im = im.crop((0, 0, w, new_h))

    im = ImageOps.autocontrast(im, cutoff=0.5)
    im = ImageEnhance.Contrast(im).enhance(contrast)
    im = im.resize((px_w, px_h), Image.LANCZOS)

    shadow, highlight = hex_to_rgb(shadow_hex), hex_to_rgb(highlight_hex)
    lut = {c: [round(shadow[c] + (highlight[c] - shadow[c]) * i / 255) for i in range(256)]
           for c in range(3)}
    r = im.point(lut[0]); g = im.point(lut[1]); b = im.point(lut[2])

    alpha = Image.new("L", (px_w, px_h), 255)
    fade_start = int(px_h * fade_from)
    apx = alpha.load()
    for y in range(fade_start, px_h):
        t = (y - fade_start) / max(1, (px_h - fade_start))
        v = round(255 * (1 - t))
        for x in range(px_w):
            apx[x, y] = v
    rgba = Image.merge("RGBA", (r, g, b, alpha))

    buf = io.BytesIO()
    rgba.save(buf, format="PNG", optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"

# --------------------------------------------------------------- BUILD ---
def build(cfg, theme_name):
    t = THEMES[theme_name]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    photo_path = os.path.normpath(os.path.join(base_dir, cfg["photo"]))

    portrait_w, portrait_h = 264, 318
    px, py = MARGIN, 96
    photo_uri = duotone_portrait(photo_path, t["duo_shadow"], t["duo_highlight"], portrait_w, portrait_h)

    text_x = px + portrait_w + 44

    s = []
    a = s.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
      f'width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
      f'aria-label="{esc(cfg["name"])} — {esc(cfg["role"])}">')
    # no background rect — transparent, sits directly on GitHub's page

    accent, ink, muted, line = t["accent"], t["ink"], t["muted"], t["line"]

    # ---- header: monogram with a continuously rotating ring (real, ----
    # ---- ongoing motion — not a one-shot transition) --------------------
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

    # ---- portrait, pop-in on load ----
    a(f'<g><animateTransform attributeName="transform" type="scale" additive="sum" '
      f'from="0.96" to="1" dur="0.5s" begin="0.05s" fill="freeze" '
      f'calcMode="spline" keySplines="0.2 0 0.2 1" keyTimes="0;1"/>'
      f'<animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="0.05s" fill="freeze"/>'
      f'<image x="{px}" y="{py}" width="{portrait_w}" height="{portrait_h}" '
      f'href="{photo_uri}" preserveAspectRatio="xMidYMid slice"/></g>')

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
