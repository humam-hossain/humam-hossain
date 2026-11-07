# Phase 1: Hero Terminal Card & Design System — Pattern Map

**Generated:** 2026-11-07  
**Status:** Complete  
**Directives:** Downstream plan generators and execution agents MUST follow these patterns without ad-hoc deviation.

---

## 1. Target Files Inventory

| File Path | Action | Role | Data Flow | Closest Analog |
|-----------|--------|------|-----------|----------------|
| `config/terminal_theme.json` | Create | Design Token Single Source of Truth | Config $\rightarrow$ Generator & Tests | `src/themes/default.js` |
| `scripts/generate_hero.py` | Create | Deterministic SVG Generator | `config/terminal_theme.json` $\rightarrow$ `assets/hero.svg` | `cv/build.sh` |
| `assets/hero.svg` | Create (Generated) | Vector Graphic Component | Generator output $\rightarrow$ Profile Viewport | `cv/outputs/cv_humam_hossain.pdf` |
| `docs/DESIGN_SYSTEM.md` | Create | Visual Reference Manual | Static Architectural Contract | `cv/README.md` & `codebase/CONVENTIONS.md` |
| `tests/test_tokens.py` | Create | Schema & Asset Verification Suite | Inputs $\rightarrow$ ElementTree Validation $\rightarrow$ Assertions | `cv/test_doc.tex` |
| `tests/__init__.py` | Create | Package Init Marker | Python Discovery Hook | Standard empty init marker |
| `README.md` | Modify | GitHub Profile Landing Page | Embeds `assets/hero.svg`, badges, anchors | Existing `README.md` |

---

## 2. Codebase Analogs & Pattern Origins

### 2.1 Theme & Design System Tokens

#### Codebase Analog: `src/themes/default.js` & `cv/config.tex`
In the existing codebase, visual constants and style tokens are centralized rather than scattered inline:

```javascript
// Excerpt from src/themes/default.js
const defaultTheme = {
  fonts: {
    title: "Space Grotesk, sans-serif",
    main: "system-ui, sans-serif"
  },
  breakpoints: {
    xs: 'screen and (max-width: 480px)',
    sm: 'screen and (max-width: 640px)',
    md: 'screen and (max-width: 768px)',
  },
}

const dark = {
  colors: {
    primary1: "#EEEDF0",
    background1: "#17181F",
    accent1: "#6C72CB",
    // ...
  }
}
```

```latex
% Excerpt from cv/config.tex
% font
\usepackage{fontspec}
\setmainfont{Courier 10 Pitch}

% margins
\usepackage[
    top=0.75in,
    left=0.75in,
    bottom=0.75in,
    right=0.75in,
]{geometry}
```

#### New Pattern: `config/terminal_theme.json`
For the automated terminal system, tokens must be accessible across Python CLI scripts, test harnesses, and GitHub Actions. A declarative JSON format is used as the single source of truth:

```json
{
  "meta": {
    "name": "GitHub Dark Terminal Theme",
    "version": "1.0.0",
    "author": "humam-hossain"
  },
  "geometry": {
    "viewBox": "0 0 850 380",
    "width": 850,
    "height": 380,
    "card_rx": 10,
    "header_height": 38,
    "traffic_lights": [
      {"cx": 25, "cy": 19, "r": 6, "color": "#ff5f56"},
      {"cx": 45, "cy": 19, "r": 6, "color": "#ffbd2e"},
      {"cx": 65, "cy": 19, "r": 6, "color": "#27c93f"}
    ],
    "monogram": {
      "x": 60,
      "y_start": 82,
      "line_height": 22
    },
    "ansi_strip": {
      "cy": 295,
      "r": 6,
      "x_start": 62,
      "spacing": 22
    },
    "telemetry": {
      "x": 310,
      "y_start": 82,
      "line_height": 25
    }
  },
  "colors": {
    "background": {
      "header": "#161b22",
      "body": "#0d1117"
    },
    "border": "#30363d",
    "text": {
      "title": "#8b949e",
      "monogram": "#a5d6ff",
      "cursor": "#a5d6ff",
      "prompt": "#58a6ff",
      "divider": "#616e7f",
      "key": "#ffa657",
      "value": "#c9d1d9",
      "additions": "#3fb950",
      "deletions": "#f85149"
    },
    "ansi": [
      "#484f58",
      "#ff7b72",
      "#3fb950",
      "#d29922",
      "#58a6ff",
      "#bc8cff",
      "#79c0ff",
      "#f0f6fc"
    ]
  },
  "typography": {
    "font_family": "ui-monospace, SFMono-Regular, Menlo, Consolas, \"Fira Code\", monospace",
    "font_sizes": {
      "title": 13,
      "monogram": 20,
      "prompt": 15,
      "divider": 14,
      "telemetry": 13.5
    }
  }
}
```

---

### 2.2 Automation Script & Generation Pipeline

#### Codebase Analog: `cv/build.sh`
The existing build script handles directories deterministically, compiles artifacts, and isolates output files:

```bash
# Excerpt from cv/build.sh
mkdir -p bin outputs
xelatex "${TARGET}.tex"
mv -f "${TARGET}.pdf" outputs/
echo "--- Build complete: outputs/${TARGET}.pdf ---"
```

#### New Pattern: `scripts/generate_hero.py`
The Python generator follows the same deterministic output isolation principle, using pure standard library modules (`json`, `pathlib.Path`, `xml.sax.saxutils`, `xml.etree.ElementTree`) without external dependencies:

```python
#!/usr/bin/env python3
"""
scripts/generate_hero.py
Generates assets/hero.svg using tokens defined in config/terminal_theme.json.
Standard library only (zero external dependencies).
"""

import json
from pathlib import Path
import xml.sax.saxutils as saxutils
import xml.etree.ElementTree as ET

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config" / "terminal_theme.json"
OUTPUT_PATH = ROOT_DIR / "assets" / "hero.svg"

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

def generate_svg() -> str:
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
        escaped_val = saxutils.escape(val)
        if "Uptime" in key:
            lines.append(f'    <text x="{tm["x"]}" y="{cur_y}" class="mono"><tspan class="key" xml:space="preserve">{padded_key} </tspan><tspan id="val-uptime" class="val">{escaped_val}</tspan></text>')
        else:
            lines.append(f'    <text x="{tm["x"]}" y="{cur_y}" class="mono"><tspan class="key" xml:space="preserve">{padded_key} </tspan><tspan class="val">{escaped_val}</tspan></text>')
        cur_y += tm["line_height"]

    # LOC Counter with Phase 2 DOM Hooks
    loc_key = f'{"LOC:":<10}'
    lines.append(f'    <text x="{tm["x"]}" y="{cur_y}" class="mono"><tspan class="key" xml:space="preserve">{loc_key} </tspan><tspan id="val-loc-add" class="loc-add">++320,410</tspan><tspan class="val"> / </tspan><tspan id="val-loc-del" class="loc-del">--85,240</tspan></text>')

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
```

---

### 2.3 Verification & Test Architecture

#### Codebase Analog: `cv/test_doc.tex`
The codebase previously used `test_doc.tex` to compile a test document before running production LaTeX builds:

```latex
% Excerpt from cv/test_doc.tex
\documentclass{article}
\usepackage{fontspec}
\setmainfont{Courier 10 Pitch}
\begin{document}
Test document for verifying TeX packages and fonts.
\end{document}
```

#### New Pattern: `tests/test_tokens.py`
The terminal system implements a clean, automated `pytest` suite ensuring schema compliance, 6-digit hex validity, well-formed SVG XML, DOM ID retention, and README structure:

```python
"""
tests/test_tokens.py
Pytest suite validating terminal theme tokens, SVG generator output, and README layout.
"""

import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import pytest

from scripts.generate_hero import generate_svg

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config" / "terminal_theme.json"
HERO_SVG_PATH = ROOT_DIR / "assets" / "hero.svg"
README_PATH = ROOT_DIR / "README.md"

HEX_REGEX = re.compile(r"^#[0-9a-fA-F]{6}$")

def test_theme_tokens_schema():
    assert CONFIG_PATH.exists(), "config/terminal_theme.json must exist"
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        theme = json.load(f)

    # Required top-level sections
    assert "geometry" in theme
    assert "colors" in theme
    assert "typography" in theme

    # Verify colors are valid hex codes
    c = theme["colors"]
    assert HEX_REGEX.match(c["background"]["header"])
    assert HEX_REGEX.match(c["background"]["body"])
    assert HEX_REGEX.match(c["border"])
    for key, hex_code in c["text"].items():
        assert HEX_REGEX.match(hex_code), f"Invalid hex for text.{key}: {hex_code}"
    for hex_code in c["ansi"]:
        assert HEX_REGEX.match(hex_code), f"Invalid ANSI hex: {hex_code}"
    assert len(c["ansi"]) == 8, "ANSI palette must contain exactly 8 diagnostic colors"

def test_hero_svg_generation():
    svg_content = generate_svg()
    root = ET.fromstring(svg_content)
    assert root.tag == "{http://www.w3.org/2000/svg}svg" or root.tag == "svg"
    assert root.attrib.get("viewBox") == "0 0 850 380"

def test_hero_svg_monogram_and_ansi():
    if not HERO_SVG_PATH.exists():
        svg_content = generate_svg()
    else:
        with open(HERO_SVG_PATH, "r", encoding="utf-8") as f:
            svg_content = f.read()

    root = ET.fromstring(svg_content)
    # Check block glyphs in monogram
    assert "█" in svg_content
    assert "▄" in svg_content
    assert "▀" in svg_content
    assert "_" in svg_content

    # Check ANSI circle count
    circles = root.findall(".//{http://www.w3.org/2000/svg}circle")
    if not circles:
        circles = root.findall(".//circle")
    # 3 traffic lights + 8 ANSI dots = 11 circles
    assert len(circles) >= 11

def test_hero_svg_telemetry_keys():
    if not HERO_SVG_PATH.exists():
        svg_content = generate_svg()
    else:
        with open(HERO_SVG_PATH, "r", encoding="utf-8") as f:
            svg_content = f.read()

    root = ET.fromstring(svg_content)
    # Assert telemetry keys
    for key in ["OS:", "Host:", "Kernel:", "Focus:", "Uptime:", "Shell:", "Contact:", "LOC:"]:
        assert key in svg_content, f"Missing telemetry key: {key}"

    # Verify XML escaped ampersand
    assert "AI &amp; Robotics" in svg_content
    assert "Autonomous Systems, IoT &amp; Cloud" in svg_content

    # Verify Phase 2 DOM update IDs
    assert root.find(".//*[@id='val-uptime']") is not None
    assert root.find(".//*[@id='val-loc-add']") is not None
    assert root.find(".//*[@id='val-loc-del']") is not None

def test_readme_structure():
    assert README_PATH.exists(), "README.md must exist"
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Image embed
    assert '<img src="./assets/hero.svg"' in content
    assert 'alt="humam@workstation"' in content

    # Flat-square Shields.io badges
    assert "img.shields.io/badge" in content
    assert "style=flat-square" in content
    assert "161b22" in content
    assert "./cv/outputs/cv_humam_hossain.pdf" in content

    # Phase anchors
    assert "<!-- PROJECTS:START -->" in content
    assert "<!-- PROJECTS:END -->" in content
    assert "<!-- METRICS:START -->" in content
    assert "<!-- METRICS:END -->" in content
    assert "<!-- SKILLS:START -->" in content
    assert "<!-- SKILLS:END -->" in content

    # Exit prompt
    assert "humam@workstation:~$ exit" in content
```

---

### 2.4 Profile Landing Page (`README.md`)

#### Codebase Analog: Existing `README.md`
The existing repository `README.md` was a minimal placeholder:
```markdown
## Muhammed Humam Hossain

I'm a programmer
```

#### New Pattern: Profile README Structure
The new profile README serves as an authentic terminal session with centered hero card, contact badges, phase anchors, and terminal exit prompt:

```markdown
<div align="center">
  <img src="./assets/hero.svg" alt="humam@workstation" width="100%" />
</div>

<div align="center">

[![Email](https://img.shields.io/badge/Email-muhammed.humam.hossain%40gmail.com-161b22?style=flat-square&logo=gmail&logoColor=ffa657)](mailto:muhammed.humam.hossain@gmail.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-humam--hossain-161b22?style=flat-square&logo=linkedin&logoColor=58a6ff)](https://www.linkedin.com/in/humam-hossain-7ab762230/)
[![Portfolio](https://img.shields.io/badge/Portfolio-humam--hossain-161b22?style=flat-square&logo=safari&logoColor=3fb950)](https://github.com/humam-hossain)
[![Resume](https://img.shields.io/badge/Resume-PDF-161b22?style=flat-square&logo=adobeacrobatreader&logoColor=ff7b72)](./cv/outputs/cv_humam_hossain.pdf)

</div>

<!-- PROJECTS:START -->
<!-- PROJECTS:END -->

<!-- METRICS:START -->
<!-- METRICS:END -->

<!-- SKILLS:START -->
<!-- SKILLS:END -->

<br />

<div align="center">
  <code>humam@workstation:~$ exit</code>
</div>
```

---

## 3. Detailed Component & Implementation Rules

### 3.1 Security & GitHub Camo Proxy Compatibility
GitHub sanitizes all README images through `camo.githubusercontent.com`. The following patterns MUST be strictly observed:
1. **No `<foreignObject>`:** Stripped by GitHub Camo. All layouts must use native SVG primitives (`<rect>`, `<text>`, `<tspan>`, `<circle>`, `<line>`).
2. **No `<script>` or Event Attributes:** Event handlers (`onload`, `onclick`) trigger Camo sanitization blocks.
3. **No External `@import` Fonts:** Camo blocks external network font fetches. Only the cross-platform system font stack may be declared:
   `ui-monospace, SFMono-Regular, Menlo, Consolas, "Fira Code", monospace`.
4. **Mandatory XML Entity Escaping:** Ampersands (`&`) in telemetry (`AI & Robotics`, `Autonomous Systems, IoT & Cloud`) MUST be escaped using `xml.sax.saxutils.escape()` to yield `&amp;`. Raw ampersands cause XML parser crashes.
5. **ClipPath for Corner Bleed Prevention:** Window title bar (`#161b22`) must be enclosed within a `<g clip-path="url(#card-clip)">` so its 90-degree rectangle corners do not protrude outside the rounded card (`rx="10"`).

### 3.2 Monogram Typography & Alignment
- **Dimensions:** 8 lines tall.
- **Glyphs:** Unicode Full Block (`█` `U+2588`), Lower Half Block (`▄` `U+2584`), Upper Half Block (`▀` `U+2580`), and underscore (`_`).
- **Color:** Cyan (`#a5d6ff`).
- **Font Properties:** `font-size: 20px`, `font-weight: bold`, `white-space: pre`, `xml:space="preserve"`.
- **Diagnostic Strip Alignment:** 8 circular dots (`r="6"`) spanning horizontally from `x=62` to `x=216` with center-to-center spacing of 22px (`62 + 7 * 22 = 216`), precisely matching the visual boundary of the monogram art above.

### 3.3 Downstream Contract (Phase 2 Integration)
To enable Phase 2 (`update_profile.py`) to update live GitHub metrics without regex scraping or brittle string substitution, the SVG generator guarantees the presence of explicit DOM `id` attributes:
- `id="val-uptime"` on the Uptime value `<tspan>`.
- `id="val-loc-add"` on the LOC additions value `<tspan>`.
- `id="val-loc-del"` on the LOC deletions value `<tspan>`.

---

## 4. Phase 1 Dependency & Execution Waves

```
Wave 0: Test Scaffold & Schema
├── tests/__init__.py
├── config/terminal_theme.json
└── tests/test_tokens.py (schema & initial assertions)

Wave 1: Generator Implementation & Vector Asset
├── scripts/generate_hero.py
├── assets/hero.svg (executed by script)
└── docs/DESIGN_SYSTEM.md

Wave 2: Profile Markdown Integration & Verification
├── README.md (embedded hero card, badges, anchors, exit prompt)
└── pytest tests/test_tokens.py (full green validation pass)
```

---

## PATTERN MAPPING COMPLETE
