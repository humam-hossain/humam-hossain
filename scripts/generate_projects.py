#!/usr/bin/env python3
"""
scripts/generate_projects.py
Standalone SVG vector graphics generator for Open Source Projects Dashboard.
Terminal-themed 2x2 grid card display for featured repositories.
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
OUTPUT_PATH = ROOT_DIR / "assets" / "projects.svg"

GRID_SLOTS = [
    (30, 80),
    (440, 80),
    (30, 207),
    (440, 207),
]

OCTICONS = {
    "star": "M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z",
    "fork": "M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a2.25 2.25 0 1 1 1.5 0v.878a2.25 2.25 0 0 1-2.25 2.25h-1.5v2.128a2.251 2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3 6.25v-.878a2.25 2.25 0 1 1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm-3 8.75a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z",
    "issue": "M8 9.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3ZM8 0a8 8 0 1 1 0 16A8 8 0 0 1 8 0ZM1.5 8a6.5 6.5 0 1 0 13 0 6.5 6.5 0 0 0-13 0Z",
    "pr": "M1.5 3.25a2.25 2.25 0 1 1 3 2.122v5.256a2.251 2.251 0 1 1-1.5 0V5.372A2.25 2.25 0 0 1 1.5 3.25Zm5.677-.177L9.5 5.396V10.75a2.25 2.25 0 1 0 1.5 0V5.396l2.323-2.323a.75.75 0 0 0-1.06-1.06L11 3.28V1.5a.75.75 0 0 0-1.5 0v1.78L8.243 2.013a.75.75 0 0 0-1.066 1.06Z",
}

DEFAULT_PROJECT_FIXTURES = [
    {
        "repo": "humam-hossain/linux_shell_scripting",
        "name": "linux_shell_scripting",
        "description": "Shell scripts and automation utilities for Unix systems",
        "stars": 0,
        "forks": 0,
        "open_issues": 0,
        "open_prs": 0,
        "language": "Shell",
        "language_color": "#89e051",
        "topics": ["bash", "shell", "automation"],
        "url": "https://github.com/humam-hossain/linux_shell_scripting",
    },
    {
        "repo": "humam-hossain/Python",
        "name": "Python",
        "description": "Python algorithms, utilities, and robotics tools",
        "stars": 0,
        "forks": 0,
        "open_issues": 0,
        "open_prs": 0,
        "language": "Python",
        "language_color": "#3572A5",
        "topics": ["python", "algorithms", "robotics"],
        "url": "https://github.com/humam-hossain/Python",
    },
    {
        "repo": "humam-hossain/nn",
        "name": "nn",
        "description": "C-based neural network framework for matrix operations and gradient learning",
        "stars": 0,
        "forks": 0,
        "open_issues": 0,
        "open_prs": 0,
        "language": "C",
        "language_color": "#555555",
        "topics": ["c", "machine-learning", "neural-network"],
        "url": "https://github.com/humam-hossain/nn",
    },
    {
        "repo": "humam-hossain/antigravity-cli-statusline",
        "name": "antigravity-cli-statusline",
        "description": "Advanced responsive statusline plugin for Antigravity CLI",
        "stars": 0,
        "forks": 0,
        "open_issues": 0,
        "open_prs": 0,
        "language": "Shell",
        "language_color": "#89e051",
        "topics": ["cli", "statusline", "zsh"],
        "url": "https://github.com/humam-hossain/antigravity-cli-statusline",
    },
]


def wrap_and_clamp_description(
    text: str, max_line1: int = 42, max_line2: int = 40
) -> tuple[str, str]:
    """
    Wraps text into 2 lines with ellipsis truncation before escaping XML.
    Prevents splitting entities like '&amp;' across lines or at the truncation point.
    """
    clean = " ".join((text or "").split())
    if not clean:
        return "", ""

    words = clean.split()
    line1_words = []
    curr_len = 0
    idx = 0

    while idx < len(words):
        w = words[idx]
        add_len = len(w) + (1 if curr_len > 0 else 0)
        if curr_len + add_len <= max_line1 or not line1_words:
            line1_words.append(w)
            curr_len += add_len
            idx += 1
        else:
            break

    line1 = " ".join(line1_words)
    rem_words = words[idx:]
    if not rem_words:
        return saxutils.escape(line1), ""

    line2_words = []
    curr_len = 0
    truncated = False
    for w in rem_words:
        add_len = len(w) + (1 if curr_len > 0 else 0)
        if curr_len + add_len <= max_line2 or not line2_words:
            line2_words.append(w)
            curr_len += add_len
        else:
            truncated = True
            break

    line2 = " ".join(line2_words)
    if truncated or (idx + len(line2_words) < len(words)):
        line2 = line2.rstrip(".,;:!?") + "..."

    return saxutils.escape(line1), saxutils.escape(line2)


def _render_subpanel(gx: int, gy: int, p: dict, border_color: str) -> list[str]:
    """Renders a single 380x115px project card subpanel at (gx, gy)."""
    lines = []
    lines.append(f'    <rect x="{gx}" y="{gy}" width="380" height="115" rx="6" fill="#161b22" stroke="{border_color}" stroke-width="1" />')

    # Repo title: 📁 {name}
    name_raw = p.get("name") or (p.get("repo", "").split("/")[-1] if p.get("repo") else "repo")
    title_escaped = saxutils.escape(name_raw[:28])
    lines.append(f'    <text x="{gx + 16}" y="{gy + 24}" class="mono repo-title"><tspan>&#128193; {title_escaped}</tspan></text>')

    # Primary language: ● {lang}
    lang = saxutils.escape(p.get("language") or "Plain Text")
    lang_color = p.get("language_color") or "#8b949e"
    lines.append(f'    <text x="{gx + 364}" y="{gy + 24}" class="mono lang-text" text-anchor="end"><tspan fill="{lang_color}">&#9679; </tspan><tspan fill="#8b949e">{lang}</tspan></text>')

    # Divider line
    lines.append(f'    <line x1="{gx + 16}" y1="{gy + 34}" x2="{gx + 364}" y2="{gy + 34}" stroke="#21262d" stroke-width="1" />')

    # Description (2 lines clamped)
    desc_l1, desc_l2 = wrap_and_clamp_description(p.get("description", ""))
    if desc_l1:
        lines.append(f'    <text x="{gx + 16}" y="{gy + 52}" class="mono desc-text">{desc_l1}</text>')
    if desc_l2:
        lines.append(f'    <text x="{gx + 16}" y="{gy + 68}" class="mono desc-text">{desc_l2}</text>')

    # Metric counter row at y = gy + 96
    # 1. Star
    stars = p.get("stars", 0)
    star_color = "#f1e05a" if stars > 0 else "#616e7f"
    lines.append(f'    <g transform="translate({gx + 16}, {gy + 84}) scale(0.75)">')
    lines.append(f'      <path d="{OCTICONS["star"]}" fill="{star_color}" />')
    lines.append(f'    </g>')
    lines.append(f'    <text x="{gx + 32}" y="{gy + 96}" class="mono metric-text" fill="{star_color}">{stars}</text>')

    # 2. Fork
    forks = p.get("forks", 0)
    fork_color = "#58a6ff" if forks > 0 else "#616e7f"
    lines.append(f'    <g transform="translate({gx + 100}, {gy + 84}) scale(0.75)">')
    lines.append(f'      <path d="{OCTICONS["fork"]}" fill="{fork_color}" />')
    lines.append(f'    </g>')
    lines.append(f'    <text x="{gx + 116}" y="{gy + 96}" class="mono metric-text" fill="{fork_color}">{forks}</text>')

    # 3. Issue
    issues = p.get("open_issues", 0)
    issue_color = "#ffa657" if issues > 0 else "#616e7f"
    lines.append(f'    <g transform="translate({gx + 184}, {gy + 84}) scale(0.75)">')
    lines.append(f'      <path d="{OCTICONS["issue"]}" fill="{issue_color}" />')
    lines.append(f'    </g>')
    lines.append(f'    <text x="{gx + 200}" y="{gy + 96}" class="mono metric-text" fill="{issue_color}">{issues}</text>')

    # 4. PR
    prs = p.get("open_prs", 0)
    pr_color = "#a371f7" if prs > 0 else "#616e7f"
    lines.append(f'    <g transform="translate({gx + 274}, {gy + 84}) scale(0.75)">')
    lines.append(f'      <path d="{OCTICONS["pr"]}" fill="{pr_color}" />')
    lines.append(f'    </g>')
    lines.append(f'    <text x="{gx + 290}" y="{gy + 96}" class="mono metric-text" fill="{pr_color}">{prs}</text>')

    return lines


def generate_projects_svg(
    projects: list[dict],
    theme: dict | None = None,
) -> str:
    """
    Renders the dark terminal projects dashboard SVG (850x340).
    Strictly validates XML using xml.etree.ElementTree before returning.
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

    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 340" width="100%" height="100%">',
        '  <defs>',
        '    <style>',
        f'      .mono {{ font-family: {font_family}; text-rendering: geometricPrecision; }}',
        '      .title {{ font-size: 13px; fill: #8b949e; text-anchor: middle; font-weight: 400; }}',
        '      .prompt-cmd {{ font-size: 13px; }}',
        '      .prompt-user {{ fill: #58a6ff; font-weight: 600; }}',
        '      .prompt-arg {{ fill: #c9d1d9; font-weight: 400; }}',
        '      .repo-title {{ font-size: 14px; fill: #a5d6ff; font-weight: 600; }}',
        '      .lang-text {{ font-size: 12px; font-weight: 400; }}',
        '      .desc-text {{ font-size: 12px; fill: #8b949e; font-weight: 400; }}',
        '      .metric-text {{ font-size: 12px; font-weight: 400; }}',
        '      .slot-placeholder {{ font-size: 13px; fill: #616e7f; text-anchor: middle; font-weight: 400; }}',
        '    </style>',
        '  </defs>',
        '',
        f'  <!-- Terminal Window Frame -->',
        f'  <rect width="850" height="340" rx="10" ry="10" fill="{bg_body}" stroke="{border_color}" stroke-width="1" />',
        '',
        f'  <!-- Header Bar -->',
        f'  <rect width="850" height="38" rx="10" ry="10" fill="{bg_header}" />',
        f'  <rect y="28" width="850" height="10" fill="{bg_header}" />',
        f'  <line x1="0" y1="38" x2="850" y2="38" stroke="{border_color}" stroke-width="1" />',
        '',
        '  <!-- macOS Traffic Lights -->',
        '  <circle cx="25" cy="19" r="6" fill="#ff5f56" />',
        '  <circle cx="45" cy="19" r="6" fill="#ffbd2e" />',
        '  <circle cx="65" cy="19" r="6" fill="#27c93f" />',
        '',
        '  <!-- Window Title -->',
        '  <text x="425" y="24" class="mono title">projects — zsh</text>',
        '',
        '  <!-- Prompt Line -->',
        '  <text x="30" y="62" class="mono prompt-cmd">',
        '    <tspan class="prompt-user">humam@workstation:~/projects$ </tspan>',
        '    <tspan class="prompt-arg">gh repo list</tspan>',
        '  </text>',
        '',
        '  <!-- 2x2 Project Cards Grid -->',
    ]

    for idx, (gx, gy) in enumerate(GRID_SLOTS):
        if idx < len(projects):
            lines.extend(_render_subpanel(gx, gy, projects[idx], border_color))
        else:
            # Empty / Available slot placeholder
            lines.append(f'    <rect x="{gx}" y="{gy}" width="380" height="115" rx="6" fill="none" stroke="{border_color}" stroke-dasharray="4,4" stroke-width="1" />')
            lines.append(f'    <text x="{gx + 190}" y="{gy + 62}" class="mono slot-placeholder">[ available slot ]</text>')

    lines.append('</svg>')
    svg_str = "\n".join(lines) + "\n"

    # Strict XML validation
    ET.fromstring(svg_str)
    return svg_str


def main() -> int:
    """CLI Entry point for standalone SVG generation."""
    print("Generating assets/projects.svg using default fixtures...")
    svg_content = generate_projects_svg(DEFAULT_PROJECT_FIXTURES)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(svg_content, encoding="utf-8")
    print(f"Successfully generated {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
