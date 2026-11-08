#!/usr/bin/env python3
"""
scripts/generate_metrics.py
Standalone SVG vector graphics generator for assets/metrics.svg.
Terminal-themed metrics card: streak mini-panels + language progress tracks.
Standard library only: json, pathlib, xml.etree.ElementTree, xml.sax.saxutils.
Zero external dependencies.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import xml.sax.saxutils as saxutils

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config" / "terminal_theme.json"
OUTPUT_PATH = ROOT_DIR / "assets" / "metrics.svg"

DEFAULT_STREAK_FIXTURES = {
    "current_streak": 5,
    "longest_streak": 14,
    "total_contributions": 482,
    "standby": False,
}

DEFAULT_LANGUAGE_FIXTURES = [
    {"name": "Python", "bytes": 65000, "color": "#3572A5", "percentage": 52.0},
    {"name": "Shell", "bytes": 42000, "color": "#89e051", "percentage": 33.6},
    {"name": "C", "bytes": 18000, "color": "#555555", "percentage": 14.4},
]


def generate_metrics_svg(
    streak_data: dict,
    languages_data: list[dict],
    theme: dict | None = None,
) -> str:
    """
    Generates a self-contained 850x340 SVG terminal window with:
    - macOS traffic lights, title 'stats — zsh', prompt line
    - Left panel: 3 stacked mini-panels (Current Streak, Longest Streak, Total Contributions)
    - Right panel: Top Languages breakdown with vector <rect> progress tracks
    Validates XML with ElementTree before returning.
    """
    if theme is None:
        if CONFIG_PATH.is_file():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                theme = json.load(f)
        else:
            theme = {}

    colors = theme.get("colors", {})
    bg_body = colors.get("background", {}).get("body", "#0d1117")
    bg_header = colors.get("background", {}).get("header", "#161b22")
    border_color = colors.get("border", "#30363d")
    t = theme.get("typography", {})
    font_family = t.get(
        "font_family",
        'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
    )

    current_streak = streak_data.get("current_streak", 0)
    longest_streak = streak_data.get("longest_streak", 0)
    total_contributions = streak_data.get("total_contributions", 0)

    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 340" width="100%" height="100%">',
        "  <defs>",
        "    <style>",
        f"      .mono {{ font-family: {font_family}; text-rendering: geometricPrecision; }}",
        "      .title { font-size: 13px; fill: #8b949e; text-anchor: middle; font-weight: 400; }",
        '      .prompt-cmd { font-size: 13px; }',
        "      .prompt-user { fill: #58a6ff; font-weight: 600; }",
        "      .prompt-arg { fill: #c9d1d9; font-weight: 400; }",
        "      .card-title { font-size: 13px; font-weight: 600; }",
        "      .card-val { font-size: 22px; font-weight: bold; }",
        '      .card-unit { font-size: 13px; fill: #8b949e; font-weight: 400; }',
        "      .lang-name { font-size: 13px; fill: #c9d1d9; font-weight: 500; }",
        '      .lang-pct { font-size: 12px; fill: #8b949e; font-weight: 400; text-anchor: end; }',
        '      .sub-header { font-size: 13px; fill: #8b949e; font-weight: 600; }',
        '      .badge-standby { font-size: 12px; fill: #8b949e; font-weight: 400; }',
        "    </style>",
        "  </defs>",
        "",
        "  <!-- Terminal Window Frame -->",
        f'  <rect width="850" height="340" rx="10" ry="10" fill="{bg_body}" stroke="{border_color}" stroke-width="1" />',
        "",
        "  <!-- Header Bar -->",
        f'  <rect width="850" height="38" rx="10" ry="10" fill="{bg_header}" />',
        f'  <rect y="28" width="850" height="10" fill="{bg_header}" />',
        f'  <line x1="0" y1="38" x2="850" y2="38" stroke="{border_color}" stroke-width="1" />',
        "",
        "  <!-- Traffic Lights -->",
        '  <circle cx="25" cy="19" r="6" fill="#ff5f56" />',
        '  <circle cx="45" cy="19" r="6" fill="#ffbd2e" />',
        '  <circle cx="65" cy="19" r="6" fill="#27c93f" />',
        "",
        "  <!-- Window Title -->",
        '  <text x="425" y="24" class="mono title">stats — zsh</text>',
        "",
        "  <!-- Prompt Line -->",
        '  <text x="30" y="62" class="mono prompt-cmd">',
        '    <tspan class="prompt-user">humam@workstation:~$ </tspan>',
        '    <tspan class="prompt-arg">git status --telemetry</tspan>',
        "  </text>",
    ]

    # --- Left Panel: Streak Mini-Panels (width 330, x=30) ---
    panel_x = 30
    panel_w = 330

    # Card 1: Current Streak
    card1_y = 80
    lines.append("")
    lines.append("  <!-- Left Panel: Streak Cards -->")
    lines.append(f'  <rect x="{panel_x}" y="{card1_y}" width="{panel_w}" height="70" rx="6" ry="6" fill="{bg_header}" stroke="{border_color}" stroke-width="1" />')
    lines.append(f'  <text x="{panel_x + 15}" y="{card1_y + 22}" class="mono card-title" fill="#ffa657">⚡ Current Streak</text>')
    if current_streak > 0:
        day_word = "day" if current_streak == 1 else "days"
        lines.append(f'  <text x="{panel_x + 15}" y="{card1_y + 52}" class="mono card-val" fill="#ffa657">{current_streak} <tspan class="card-unit">{day_word}</tspan></text>')
    else:
        lines.append(f'  <text x="{panel_x + 15}" y="{card1_y + 52}" class="mono card-val" fill="#ffa657">0 <tspan class="card-unit">days</tspan> <tspan class="badge-standby">[standby]</tspan></text>')

    # Card 2: Longest Streak
    card2_y = 162
    lines.append(f'  <rect x="{panel_x}" y="{card2_y}" width="{panel_w}" height="70" rx="6" ry="6" fill="{bg_header}" stroke="{border_color}" stroke-width="1" />')
    lines.append(f'  <text x="{panel_x + 15}" y="{card2_y + 22}" class="mono card-title" fill="#58a6ff">★ Longest Streak</text>')
    day_word_l = "day" if longest_streak == 1 else "days"
    lines.append(f'  <text x="{panel_x + 15}" y="{card2_y + 52}" class="mono card-val" fill="#58a6ff">{longest_streak} <tspan class="card-unit">{day_word_l}</tspan></text>')

    # Card 3: Total Contributions
    card3_y = 244
    lines.append(f'  <rect x="{panel_x}" y="{card3_y}" width="{panel_w}" height="70" rx="6" ry="6" fill="{bg_header}" stroke="{border_color}" stroke-width="1" />')
    lines.append(f'  <text x="{panel_x + 15}" y="{card3_y + 22}" class="mono card-title" fill="#3fb950">◆ Total Contributions</text>')
    lines.append(f'  <text x="{panel_x + 15}" y="{card3_y + 52}" class="mono card-val" fill="#3fb950">{total_contributions:,} <tspan class="card-unit">events</tspan></text>')

    # --- Right Panel: Language Breakdown ---
    rp_x = 380
    rp_y = 80
    rp_w = 440
    rp_h = 234
    lines.append("")
    lines.append("  <!-- Right Panel: Languages -->")
    lines.append(f'  <rect x="{rp_x}" y="{rp_y}" width="{rp_w}" height="{rp_h}" rx="6" ry="6" fill="{bg_header}" stroke="{border_color}" stroke-width="1" />')
    lines.append(f'  <text x="{rp_x + 20}" y="105" class="mono sub-header">Top Languages (by volume)</text>')
    lines.append(f'  <line x1="{rp_x + 15}" y1="115" x2="{rp_x + rp_w - 15}" y2="115" stroke="{border_color}" stroke-width="1" />')

    for i, lang in enumerate(languages_data[:6]):
        row_y = 140 + (i * 28)
        name = saxutils.escape(lang.get("name", "Unknown"))
        color = lang.get("color", "#8b949e")
        pct = lang.get("percentage", 0.0)

        # Dot + name
        lines.append(f'  <text x="{rp_x + 20}" y="{row_y}" class="mono lang-name"><tspan fill="{color}">● </tspan>{name}</text>')

        # Vector progress track
        track_x = 540
        track_w = 200
        fill_w = max(int(track_w * (pct / 100.0)), 2) if pct > 0 else 0
        lines.append(f'  <rect x="{track_x}" y="{row_y - 9}" width="{track_w}" height="8" rx="3" ry="3" fill="#21262d" />')
        if fill_w > 0:
            lines.append(f'  <rect x="{track_x}" y="{row_y - 9}" width="{fill_w}" height="8" rx="3" ry="3" fill="{color}" />')

        # Percentage readout
        lines.append(f'  <text x="{rp_x + rp_w - 20}" y="{row_y}" class="mono lang-pct">{pct:.1f}%</text>')

    lines.append("</svg>")
    svg_str = "\n".join(lines) + "\n"

    # Strict XML validation
    ET.fromstring(svg_str)
    return svg_str


def main() -> int:
    """CLI Entry point for standalone SVG generation."""
    print("Generating assets/metrics.svg using default fixtures...")
    svg_content = generate_metrics_svg(DEFAULT_STREAK_FIXTURES, DEFAULT_LANGUAGE_FIXTURES)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(svg_content, encoding="utf-8")
    print(f"Successfully generated {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
