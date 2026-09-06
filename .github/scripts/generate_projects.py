#!/usr/bin/env python3
"""
Generate one card SVG per project (light + dark each) instead of a single
combined panel.

Why: GitHub strips <map>/<area> tags from README HTML (not on its
sanitizer's allowlist), and links inside an SVG do nothing once it's
embedded via <img> anyway — so there is no way to make regions *inside*
one big image individually clickable on GitHub. The only pattern that
reliably works is the same one shields.io badges use: each project gets
its OWN small image, wrapped in a plain markdown/HTML link in README.md:

    [<img src="erds.svg">](https://github.com/skgpt254/Cyber_Mini-Project)

Output: out/<slug>.svg and out/<slug>-dark.svg per project, e.g.
out/erds.svg, out/erds-dark.svg, out/packetdive.svg, out/packetdive-dark.svg

Usage:
    python3 generate_projects.py merged.json out/
"""
import html
import json
import re
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

CARD_W = 578
CARD_H = 186

def esc(s):
    return html.escape(str(s), quote=True)

def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "project"

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

def card_svg(p, t, accent):
    e = []
    a = e.append
    repo = p.get("repo", "").strip()
    repo = repo.replace("https://github.com/", "").replace("http://github.com/", "").rstrip("/")
    line, ink, muted = t["line"], t["ink"], t["muted"]

    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_W}" height="{CARD_H}" '
      f'viewBox="0 0 {CARD_W} {CARD_H}" role="img" aria-label="{esc(p.get("name",""))}">')

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
          f'fill="freeze" calcMode="spline" keySplines="0.2 0 0.2 1" keyTimes="0;1"/></rect>')
        a(f'<text x="{bar_x+bar_w+10}" y="{bar_y+4.5}" font-family="{MONO}" font-size="10" '
          f'fill="{muted}">{esc(lang)} {frac*100:.0f}%</text>')

    stars = p.get("stars", 0)
    a(f'<text x="{CARD_W-20}" y="{168+4.5}" text-anchor="end" font-family="{MONO}" font-size="10.5" '
      f'fill="{muted}">\u2605 {stars} &#8226; updated {rel_time(p.get("pushed_at"))}</text>')

    a('</svg>')
    return "".join(e)

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "merged.json"
    outdir = sys.argv[2] if len(sys.argv) > 2 else "."
    with open(src) as f:
        projects = json.load(f)
    for i, p in enumerate(projects):
        slug = slugify(p.get("name", f"project-{i}"))
        for theme_name, suffix in (("light", ""), ("dark", "-dark")):
            accents = ACCENTS_DARK if theme_name == "dark" else ACCENTS
            svg = card_svg(p, THEMES[theme_name], accents[i % len(accents)])
            path = f"{outdir}/{slug}{suffix}.svg"
            with open(path, "w") as f:
                f.write(svg)
            print(f"wrote {path} ({len(svg)//1024}KB)")
