#!/usr/bin/env python3
"""
scripts/generate_hero.py
Generates assets/hero.svg using tokens defined in config/terminal_theme.json.
Standard library only (zero external dependencies).
"""

from __future__ import annotations

import json
from pathlib import Path
import xml.sax.saxutils as saxutils
import xml.etree.ElementTree as ET

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config" / "terminal_theme.json"
OUTPUT_PATH = ROOT_DIR / "assets" / "hero.svg"

# Default baseline fallback values (Phase 1 tokens)
DEFAULT_UPTIME = "4 yrs, 3 mos, 12 days"
DEFAULT_LOC_ADD = "++320,410"
DEFAULT_LOC_DEL = "--85,240"

# ASCII Monogram lines using solid and half-blocks
MONOGRAM_LINES = [
    "▄▄     ▄▄",
    "██     ██",
    "██     ██",
    "█████████",
    "█████████",
    "██     ██",
    "██     ██",
    "▀▀     ▀▀  _"
]

# Telemetry items harmonized with CV and decisions
TELEMETRY_ITEMS = [
    ("OS:", "Arch Linux x86_64"),
    ("Host:", "Workstation"),
    ("Kernel:", "AI & Robotics"),
    ("Focus:", "Autonomous Systems, IoT & Cloud"),
    ("Uptime:", "4 yrs, 3 mos, 12 days"),
    ("Shell:", "zsh 5.9"),
    ("Contact:", "humam@... / in/humam-hossain"),
]


def generate_svg(
    uptime: str | None = None,
    loc_add: str | None = None,
    loc_del: str | None = None,
) -> str:
    """
    Generates assets/hero.svg vector graphic content.
    If telemetry parameters are None, falls back to default workstation baseline tokens.
    """
    uptime_val = uptime if uptime is not None else DEFAULT_UPTIME
    loc_add_val = loc_add if loc_add is not None else DEFAULT_LOC_ADD
    loc_del_val = loc_del if loc_del is not None else DEFAULT_LOC_DEL

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        theme = json.load(f)

    g = theme["geometry"]
    c = theme["colors"]
    t = theme["typography"]
    fs = t["font_sizes"]

    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{g["viewBox"]}" width="100%" height="100%">')
    lines.append('<defs>')
    lines.append(f'''  <style>
    .mono {{
      font-family: {t["font_family"]};
      text-rendering: geometricPrecision;
    }}
    .title {{ font-size: {fs["title"]}px; fill: {c["text"]["title"]}; text-anchor: middle; }}
    .mono-art {{ font-size: {fs["monogram"]}px; fill: {c["text"]["monogram"]}; white-space: pre; font-weight: bold; }}
    .prompt {{ font-size: {fs["prompt"]}px; fill: {c["text"]["prompt"]}; font-weight: bold; }}
    .divider {{ font-size: {fs["divider"]}px; fill: {c["text"]["divider"]}; }}
    .key {{ font-size: {fs["telemetry"]}px; fill: {c["text"]["key"]}; font-weight: 600; }}
    .val {{ font-size: {fs["telemetry"]}px; fill: {c["text"]["value"]}; }}
    .loc-add {{ font-size: {fs["telemetry"]}px; fill: {c["text"]["additions"]}; font-weight: 600; }}
    .loc-del {{ font-size: {fs["telemetry"]}px; fill: {c["text"]["deletions"]}; font-weight: 600; }}
  </style>''')
    lines.append(f'  <clipPath id="card-clip"><rect width="{g["width"]}" height="{g["height"]}" rx="{g["card_rx"]}" ry="{g["card_rx"]}" /></clipPath>')
    lines.append('</defs>')

    # Card Window & Chrome with ClipPath
    lines.append('  <g clip-path="url(#card-clip)">')
    lines.append(f'    <rect width="{g["width"]}" height="{g["height"]}" fill="{c["background"]["body"]}" />')
    lines.append(f'    <rect width="{g["width"]}" height="{g["header_height"]}" fill="{c["background"]["header"]}" />')
    lines.append(f'    <line x1="0" y1="{g["header_height"]}" x2="{g["width"]}" y2="{g["header_height"]}" stroke="{c["border"]}" stroke-width="1" />')

    # macOS Traffic Lights
    for light in g["traffic_lights"]:
        lines.append(f'    <circle cx="{light["cx"]}" cy="{light["cy"]}" r="{light["r"]}" fill="{light["color"]}" />')

    # Centered Header Title
    lines.append(f'    <text x="{g["width"] // 2}" y="24" class="mono title">humam@workstation:~</text>')

    # Left Panel: Monogram lines
    mg = g["monogram"]
    for i, line in enumerate(MONOGRAM_LINES):
        y = mg["y_start"] + i * mg["line_height"]
        lines.append(f'    <text x="{mg["x"]}" y="{y}" class="mono mono-art" xml:space="preserve">{line}</text>')

    # Left Panel: ANSI dot strip
    strip = g["ansi_strip"]
    for i, color in enumerate(c["ansi"]):
        cx = strip["x_start"] + i * strip["spacing"]
        lines.append(f'    <circle cx="{cx}" cy="{strip["cy"]}" r="{strip["r"]}" fill="{color}" />')

    # Right Panel: Telemetry
    tm = g["telemetry"]
    cur_y = tm["y_start"]
    lines.append(f'    <text x="{tm["x"]}" y="{cur_y}" class="mono prompt">humam@workstation:~</text>')
    cur_y += tm["line_height"] - 2

    lines.append(f'    <text x="{tm["x"]}" y="{cur_y}" class="mono divider">-------------------</text>')
    cur_y += tm["line_height"]

    for key, val in TELEMETRY_ITEMS:
        padded_key = f"{key:<10}"
        if "Uptime" in key:
            escaped_val = saxutils.escape(str(uptime_val))
            lines.append(f'    <text x="{tm["x"]}" y="{cur_y}" class="mono"><tspan class="key" xml:space="preserve">{padded_key} </tspan><tspan id="val-uptime" class="val">{escaped_val}</tspan></text>')
        else:
            escaped_val = saxutils.escape(str(val))
            lines.append(f'    <text x="{tm["x"]}" y="{cur_y}" class="mono"><tspan class="key" xml:space="preserve">{padded_key} </tspan><tspan class="val">{escaped_val}</tspan></text>')
        cur_y += tm["line_height"]

    # Parameterized LOC Counter with Phase 2 DOM Hooks
    loc_key = f'{"LOC:":<10}'
    esc_add = saxutils.escape(str(loc_add_val))
    esc_del = saxutils.escape(str(loc_del_val))
    lines.append(f'    <text x="{tm["x"]}" y="{cur_y}" class="mono"><tspan class="key" xml:space="preserve">{loc_key} </tspan><tspan id="val-loc-add" class="loc-add">{esc_add}</tspan><tspan class="val"> / </tspan><tspan id="val-loc-del" class="loc-del">{esc_del}</tspan></text>')

    # Window Outer Border
    lines.append(f'    <rect width="{g["width"]}" height="{g["height"]}" rx="{g["card_rx"]}" ry="{g["card_rx"]}" fill="none" stroke="{c["border"]}" stroke-width="1" />')
    lines.append('  </g>')
    lines.append('</svg>')

    content = "\n".join(lines)
    # Strict validation before emission
    ET.fromstring(content)
    return content


if __name__ == "__main__":
    svg = generate_svg()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Successfully generated {OUTPUT_PATH}")
