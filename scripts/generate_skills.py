#!/usr/bin/env python3
"""
scripts/generate_skills.py
Standalone SVG vector graphics generator for Categorized Skills Matrix.
Terminal-themed 2x2 quadrant display (850x380) with Neofetch prompt and monospaced badges.
Standard library only: json, pathlib, sys, xml.etree.ElementTree, xml.sax.saxutils.
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
SKILLS_CONFIG_PATH = ROOT_DIR / "config" / "skills.json"
OUTPUT_PATH = ROOT_DIR / "assets" / "skills.svg"

QUADRANT_SLOTS = [
    {"x": 30, "y": 80, "width": 380, "height": 135},   # Top-Left: AI & Data Science
    {"x": 440, "y": 80, "width": 380, "height": 135},  # Top-Right: Backend & Systems
    {"x": 30, "y": 230, "width": 380, "height": 135},  # Bottom-Left: SQA & Automation
    {"x": 440, "y": 230, "width": 380, "height": 135}, # Bottom-Right: Embedded & Robotics
]

DEFAULT_SKILLS_DATA = [
    {
        "id": "ai-data-science",
        "title": "AI & Data Science",
        "accent": "#a5d6ff",
        "skills": ["PyTorch", "OpenCV", "Scikit-learn", "Pandas", "PyBullet"],
    },
    {
        "id": "backend-systems",
        "title": "Backend & Systems",
        "accent": "#ffa657",
        "skills": ["Python", "Node.js", "Linux/Bash", "MongoDB", "SQLite"],
    },
    {
        "id": "sqa-automation",
        "title": "SQA & Automation",
        "accent": "#3fb950",
        "skills": ["PyTest", "Jest", "CI/CD", "Test Planning", "Static Analysis"],
    },
    {
        "id": "embedded-robotics",
        "title": "Embedded & Robotics",
        "accent": "#d2a8ff",
        "skills": ["C/C++", "ROS2", "Arduino", "ESP32", "Kinematics"],
    },
]


def log_warn(msg: str) -> None:
    """Logs warning message to stderr."""
    print(f"\033[38;2;255;166;87m[WARN]\033[0m {msg}", file=sys.stderr)


def load_skills_config(config_path: Path | None = None) -> list[dict]:
    """
    Loads category and skills taxonomy from config/skills.json.
    Falls back gracefully to DEFAULT_SKILLS_DATA on missing or corrupted file.
    Supports either a list of category dicts or a dict with a 'categories' list.
    """
    path = config_path or SKILLS_CONFIG_PATH
    if not path.is_file():
        log_warn(f"Skills config not found at {path}, falling back to defaults")
        return DEFAULT_SKILLS_DATA

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "categories" in data and isinstance(data["categories"], list):
            return data["categories"]
        else:
            log_warn(f"Unexpected schema in {path}, falling back to defaults")
            return DEFAULT_SKILLS_DATA
    except Exception as e:
        log_warn(f"Failed to read skills config ({e}), falling back to defaults")
        return DEFAULT_SKILLS_DATA


def generate_skills_svg(skills_data: list[dict] | None = None, theme: dict | None = None) -> str:
    """
    Generates an 850x380 SVG card rendering a 2x2 skills quadrant inside
    a terminal window with Neofetch prompt and macOS traffic lights.
    Strictly validates XML output before returning.
    """
    if skills_data is None:
        skills_data = load_skills_config()

    if theme is None:
        if CONFIG_PATH.is_file():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    theme = json.load(f)
            except Exception:
                theme = {}
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

    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 380" width="100%" height="100%">',
        '  <defs>',
        '    <style>',
        f'      .mono {{ font-family: {font_family}; text-rendering: geometricPrecision; }}',
        '      .title { font-size: 13px; fill: #8b949e; text-anchor: middle; font-weight: 400; }',
        '      .prompt-cmd { font-size: 13px; }',
        '      .prompt-user { fill: #58a6ff; font-weight: 600; }',
        '      .prompt-arg { fill: #c9d1d9; font-weight: 400; }',
        '      .cat-title { font-size: 13px; font-weight: 600; }',
        '      .pill-text { font-size: 11px; fill: #c9d1d9; font-weight: 500; }',
        '      .skill-pill { transition: transform 0.15s ease-in-out; }',
        '      .skill-pill:hover .pill-bg { fill: #282e37; stroke: #8b949e; }',
        '      .skill-pill:hover .pill-text { fill: #f0f6fc; }',
        '    </style>',
        '  </defs>',
        '',
        '  <!-- Terminal Window Frame -->',
        f'  <rect width="850" height="380" rx="10" ry="10" fill="{bg_body}" stroke="{border_color}" stroke-width="1" />',
        '',
        '  <!-- Header Bar -->',
        f'  <rect width="850" height="38" rx="10" ry="10" fill="{bg_header}" />',
        f'  <rect y="28" width="850" height="10" fill="{bg_header}" />',
        f'  <line x1="0" y1="38" x2="850" y2="38" stroke="{border_color}" stroke-width="1" />',
        '',
        '  <!-- Traffic Lights -->',
        '  <circle cx="25" cy="19" r="6" fill="#ff5f56" />',
        '  <circle cx="45" cy="19" r="6" fill="#ffbd2e" />',
        '  <circle cx="65" cy="19" r="6" fill="#27c93f" />',
        '',
        '  <!-- Window Title -->',
        '  <text x="425" y="24" class="mono title">skills — zsh</text>',
        '',
        '  <!-- Prompt Line -->',
        '  <text x="30" y="62" class="mono prompt-cmd">',
        '    <tspan class="prompt-user">humam@workstation:~$ </tspan>',
        '    <tspan class="prompt-arg">neofetch --skills</tspan>',
        '  </text>',
        '',
        '  <!-- 2x2 Quadrant Grid -->',
    ]

    for idx, slot in enumerate(QUADRANT_SLOTS):
        if idx >= len(skills_data):
            break
        cat = skills_data[idx]
        title = saxutils.escape(cat.get("title", f"Category {idx+1}"))
        accent = cat.get("accent", "#58a6ff")
        skills = cat.get("skills", [])[:6]

        px, py, pw, ph = slot["x"], slot["y"], slot["width"], slot["height"]

        lines.append(f'  <g id="quadrant-{cat.get("id", idx)}">')
        lines.append(f'    <rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="6" fill="#161b22" stroke="{border_color}" stroke-width="1" />')
        lines.append(f'    <text x="{px + 16}" y="{py + 25}" fill="{accent}" class="mono cat-title">{title}</text>')

        cur_x = px + 16
        cur_y = py + 44
        max_x = px + pw - 16
        pill_h = 26
        row_gap = 10
        col_gap = 8

        for skill in skills:
            escaped_skill = saxutils.escape(skill)
            pill_w = round(32 + len(skill) * 6.8)
            if cur_x + pill_w > max_x and cur_x > px + 16:
                cur_x = px + 16
                cur_y += pill_h + row_gap

            lines.append(
                f'    <g class="skill-pill">'
                f'<rect x="{cur_x}" y="{cur_y}" width="{pill_w}" height="{pill_h}" rx="4" class="pill-bg" fill="#21262d" stroke="{border_color}" stroke-width="1" />'
                f'<circle cx="{cur_x + 12}" cy="{cur_y + 13}" r="3" fill="{accent}" />'
                f'<text x="{cur_x + 22}" y="{cur_y + 17}" class="mono pill-text">{escaped_skill}</text>'
                f'</g>'
            )
            cur_x += pill_w + col_gap

        lines.append('  </g>')

    lines.append('</svg>\n')
    svg_text = "\n".join(lines)

    # Validate strict XML integrity
    ET.fromstring(svg_text)
    return svg_text
