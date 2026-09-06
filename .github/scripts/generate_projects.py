#!/usr/bin/env python3
"""
Generate the projects panel — projects.svg (light) and projects-dark.svg.

Transparent background (sits on GitHub's page in either theme), one of a
small rotating accent palette per card for a bit of personality, a
staggered pop-in on load, and a gentle pulse on the "updated recently"
dot. Still no external logo files — a lettermark per card instead.

IMPORTANT: any element that should be visible even where SMIL animation
isn't supported (some renderers, screenshot tools, older clients) must
default to its final, visible state and only use <animate> to add motion
on top — never a static opacity="0" that only animation removes.

Usage:
    python3 generate_projects.py merged.json out/
"""
import html
import json
import math
import sys
from datetime import datetime, timezone

THEMES = {
    "light": dict(panel_stroke="#DEDACD", ink="#1C1B18", muted="#6E6B63", line="#DEDACD"),
    "dark":  dict(panel_stroke="#3B372F", ink="#F3F1EC", muted="#A8A399", line="#3B372F"),
}
# rotates per card — teal, clay/amber, indigo: warm, distinct, still restrained
ACCENTS = ["#0E6E63", "#C2703D", "#5B5FD6"]
ACCENTS_DARK = ["#2DD9B5", "#E4A46F", "#9AA0F5"]

SERIF = "Georgia,'Iowan Old Style','Palatino Linotype',serif"
MONO  = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

W = 1180
CARD_W = 578
CARD_H = 186
GAP = 16
MARGIN = 2

def esc(s):
    return html.escape(str(s), quote=True)

def rel_time(iso):
    if not iso:
        return "n/a"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        d = datetime.now(timezone.utc) - dt
        if d.days > 365: return f"{d.days // 365}y ago"
        if d.days > 30:  return f"{d.days // 30}mo ago"
        if d.days > 0:   return f"{d.days}d ago"
        h = d.seconds // 3600
        return f"{h}h ago" if h else "just now"
    except Exception:
        return "n/a"

def wrap_text(s, max_chars, max_lines=2):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= max_chars:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur); cur = w
            if len(lines) == max_lines: break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(lines) == max_lines and words and " ".join(lines).count(" ") + 1 < len(words):
        lines[-1] = lines[-1][:max_chars - 1].rstrip() + "\u2026"
    return lines

def top_language(languages):
    if not languages:
        return None, 0
    total = sum(languages.values()) or 1
    lang, val = max(languages.items(), key=lambda kv: kv[1])
    return lang, val / total

def card(p, x, y, t, accent, delay):
    e = []
    a = e.append
    repo = p.get("repo", "").strip()
    repo = repo.replace("https://github.com/", "").replace("http://github.com/", "").rstrip("/")
    href = f"https://github.com/{esc(repo)}"
    line, ink, muted = t["line"], t["ink"], t["muted"]

    a(f'<a href="{href}" target="_blank">')
    # pop-in: default fully visible/in-place; animation only adds a bounce on top
    a(f'<g transform="translate({x},{y})">')
    a(f'<animateTransform attributeName="transform" type="translate" additive="sum" '
      f'from="0 10" to="0 0" dur="0.45s" begin="{delay:.2f}s" fill="freeze" '
      f'calcMode="spline" keySplines="0.25 0.1 0.25 1" keyTimes="0;1"/>')

    a(f'<rect x="0.5" y="0.5" width="{CARD_W-1}" height="{CARD_H-1}" rx="12" '
      f'fill="none" stroke="{t["panel_stroke"]}"/>')
    a(f'<text x="20" y="24" font-family="{MONO}" font-size="11" fill="{muted}">{esc(repo)}</text>')

    days = 999
    try:
        dt = datetime.fromisoformat(p.get("pushed_at", "").replace("Z", "+00:00"))
        days = (datetime.now(timezone.utc) - dt).days
    except Exception:
        pass
    if days <= 30:
        a(f'<circle cx="{CARD_W-20}" cy="20" r="3.5" fill="{accent}">'
          f'<animate attributeName="opacity" values="1;0.35;1" dur="2.2s" repeatCount="indefinite"/></circle>')
    else:
        a(f'<circle cx="{CARD_W-20}" cy="20" r="3.5" fill="none" stroke="{muted}" stroke-width="1.2"/>')

    a(f'<line x1="20" y1="36" x2="{CARD_W-20}" y2="36" stroke="{line}"/>')

    initial = esc((p.get("name") or "?")[0].upper())
    a(f'<circle cx="42" cy="70" r="20" fill="{accent}" fill-opacity="0.12" stroke="{accent}" stroke-width="1.2"/>')
    a(f'<text x="42" y="76" text-anchor="middle" font-family="{SERIF}" font-weight="700" '
      f'font-size="16" fill="{accent}">{initial}</text>')

    name = esc(p.get("name", "unnamed"))
    a(f'<text x="76" y="64" font-family="{SERIF}" font-weight="700" font-size="18" fill="{ink}">{name}</text>')
    for i, line_txt in enumerate(wrap_text(p.get("description", ""), 58)):
        a(f'<text x="76" y="{82 + i*17}" font-family="{MONO}" font-size="11" fill="{muted}">{esc(line_txt)}</text>')

    tags_y = 128
    tx = 20
    for tag in (p.get("tags") or [])[:4]:
        tw = len(tag) * 6.2 + 16
        a(f'<rect x="{tx}" y="{tags_y-13}" width="{tw:.0f}" height="18" rx="9" '
          f'fill="none" stroke="{line}"/>')
        a(f'<text x="{tx + tw/2:.0f}" y="{tags_y}" text-anchor="middle" font-family="{MONO}" '
          f'font-size="10" fill="{muted}">{esc(tag)}</text>')
        tx += tw + 8

    a(f'<line x1="20" y1="150" x2="{CARD_W-20}" y2="150" stroke="{line}"/>')

    lang, frac = top_language(p.get("languages") or {})
    if lang:
        bar_x, bar_y, bar_w = 20, 168, 120
        a(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="4" rx="2" fill="{line}"/>')
        a(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w*frac:.1f}" height="4" rx="2" fill="{accent}">'
          f'<animate attributeName="width" from="0" to="{bar_w*frac:.1f}" dur="0.6s" '
          f'begin="{delay+0.15:.2f}s" fill="freeze" calcMode="spline" keySplines="0.2 0 0.2 1" keyTimes="0;1"/></rect>')
        a(f'<text x="{bar_x+bar_w+10}" y="{bar_y+4.5}" font-family="{MONO}" font-size="10" '
          f'fill="{muted}">{esc(lang)} {frac*100:.0f}%</text>')

    stars = p.get("stars", 0)
    a(f'<text x="{CARD_W-20}" y="{168+4.5}" text-anchor="end" font-family="{MONO}" font-size="10.5" '
      f'fill="{muted}">\u2605 {stars} &#8226; updated {rel_time(p.get("pushed_at"))}</text>')

    a('</g>')
    a('</a>')
    return "".join(e)

def build(projects, theme_name):
    t = THEMES[theme_name]
    accents = ACCENTS_DARK if theme_name == "dark" else ACCENTS
    rows = math.ceil(len(projects) / 2)
    header_h = 8
    H = header_h + rows * (CARD_H + GAP)
    s = []
    a = s.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
      f'role="img" aria-label="Projects">')
    for i, p in enumerate(projects):
        x = MARGIN + (i % 2) * (CARD_W + GAP)
        y = header_h + (i // 2) * (CARD_H + GAP)
        accent = accents[i % len(accents)]
        a(card(p, x, y, t, accent, delay=i * 0.1))
    a('</svg>')
    return "".join(s)

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "merged.json"
    outdir = sys.argv[2] if len(sys.argv) > 2 else "."
    with open(src) as f:
        projects = json.load(f)
    for theme_name, suffix in (("light", ""), ("dark", "-dark")):
        svg = build(projects, theme_name)
        path = f"{outdir}/projects{suffix}.svg"
        with open(path, "w") as f:
            f.write(svg)
        print(f"wrote {path}: {len(projects)} projects, {len(svg)//1024}KB")
