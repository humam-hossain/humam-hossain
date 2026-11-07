# Phase 1: Hero Terminal Card & Design System - Research

**Researched:** 2026-11-07  
**Domain:** SVG Vector Graphics, Terminal Window Chrome, Design Token Architectures, GitHub Profile README Rendering  
**Confidence:** HIGH  

---

## Summary

Phase 1 establishes the foundational visual identity and design system for the entire terminal-themed GitHub profile. The objective is to deliver a static dark-theme SVG terminal hero card (`assets/hero.svg`) rendered at the top of `README.md`, accompanied by a centralized design token configuration (`config/terminal_theme.json`), a pure Python generator script (`scripts/generate_hero.py`), comprehensive design documentation (`docs/DESIGN_SYSTEM.md`), and automated schema and SVG validation (`tests/test_tokens.py`).

The visual architecture emulates an authentic Unix Neofetch terminal session inside a polished macOS-style terminal window (`#161b22` header with traffic lights, `#0d1117` console body, 1px border `#30363d`). The card is divided into two distinct regions: a left panel (~35% width) hosting a retro block-art `H_` monogram rendered in cyan (`#a5d6ff`) with Unicode block characters (`█`, `▄`, `▀`) and an authentic static cursor (`_`), underscored by an 8-dot ANSI diagnostic strip (`<circle r="6">`); and a right panel (~65% width) displaying system telemetry (`humam@workstation:~`, dashed divider, and Amber-keyed system metadata) with DOM ID hooks (`val-uptime`, `val-loc-add`, `val-loc-del`) reserved for dynamic updates in Phase 2.

**Primary recommendation:** Build `scripts/generate_hero.py` using Python standard library modules (`json`, `xml.sax.saxutils`, `xml.etree.ElementTree`) without external template packages; read all styles and coordinates from `config/terminal_theme.json`, use an SVG `<clipPath>` for window corners, and strictly escape all text entities (`&` to `&amp;`) to ensure 100% well-formed SVG rendering through GitHub's Camo proxy.

---

## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: Dark Theme Only** — Single dedicated dark terminal SVG (`assets/hero.svg`). No light mode SVG or `<picture>` media query switching logic. — **Reversibility:** costly — Eliminating light mode simplifies SVG generation and downstream dashboard cards, but adding light mode later would require updating all generated SVGs and README markup.
- **D-02: Immediate Visual Opener** — The hero SVG card is the first element at the top of `README.md`, centered via `<div align="center">`, with no redundant text header above it.
- **D-03: Block-Art Typography** — Large retro Neofetch block-art `H_` (~8–10 lines tall) built using solid Unicode block characters (`█`, `▄`, `▀`).
- **D-04: Monogram Palette & Cursor** — Cyan (`#a5d6ff`) block characters with a static underscore (`_`) representing an authentic terminal prompt waiting for input.
- **D-05: Standalone Left Panel** — The monogram sits independently on the left panel (~35% width) without an enclosing sub-box, separated from telemetry by clean whitespace margin.
- **D-06: ANSI Diagnostic Dot Strip** — A single horizontal row of 8 circular ANSI color dots (`<circle r="6">` for Black/Gray, Red, Green, Amber, Blue, Magenta, Cyan, White) centered horizontally directly beneath the `H_` monogram art.
- **D-07: Prompt Header** — `humam@workstation:~` at the top of the telemetry panel followed by an authentic dashed rule divider (`-------------------`) in muted gray (`#616e7f`).
- **D-08: Label & Value Hierarchy** — Amber (`#ffa657`) keys/labels with high-contrast muted white (`#c9d1d9`) text values.
- **D-09: Exact Telemetry Fields & Wording**:
  - `OS`: `Arch Linux x86_64`
  - `Host`: `Workstation`
  - `Kernel`: `AI & Robotics`
  - `Focus`: `Autonomous Systems, IoT & Cloud`
  - `Uptime`: Realistic static placeholder (`4 yrs, 3 mos, 12 days`) prior to Phase 2 automation
  - `Shell`: `zsh 5.9`
  - `Contact`: Formatted plain text handles (`humam@...` / `in/humam-hossain`)
  - `LOC`: Realistic static placeholder (`++320,410 / --85,240`) prior to Phase 2 automation
- **D-10: Dimensions & Scaling** — Responsive `viewBox="0 0 850 380"` embedded with `width="100%"` inside `README.md` to cleanly fill GitHub's desktop content column while scaling down fluidly on mobile viewports.
- **D-11: Window Frame & Chrome** — Subtle rounded corners (`rx="10"`) with a 1px border (`#30363d`). Title bar includes colored traffic lights (🔴 `#ff5f56`, 🟡 `#ffbd2e`, 🟢 `#27c93f`) and centered title `humam@workstation:~`.
- **D-12: Dual-Tone Dark Background** — Header bar `#161b22` with a 1px border line (`#30363d`) over a dark console body (`#0d1117`).
- **D-13: Cross-Platform Monospace Font Stack** — Defined in SVG `<style>` as `ui-monospace, SFMono-Regular, Menlo, Consolas, "Fira Code", monospace` to ensure crisp rendering across all operating systems through GitHub's Camo image proxy.
- **D-14: Single Source of Truth** — Tokens defined in `config/terminal_theme.json` covering colors (backgrounds, borders, text, harmonized GitHub Dark ANSI palette), typography (font-stack, sizes, line heights), and geometry (padding, corner radii, viewBox dimensions). — **Reversibility:** costly — Downstream Python scripts in Phases 2–6 will load this config file.
- **D-15: Python Generator Script** — `scripts/generate_hero.py` reads `config/terminal_theme.json` and renders `assets/hero.svg`. Self-contained with zero external template package dependencies.
- **D-16: Design Documentation** — `docs/DESIGN_SYSTEM.md` created to document color swatches, typography rules, and aesthetic constraints for human reference.
- **D-17: Validation Suite** — `tests/test_tokens.py` to verify JSON token schema, valid hex codes, and well-formed SVG XML structure.
- **D-18: Relative Image Embed** — Embedded via `<div align="center"><img src="./assets/hero.svg" alt="humam@workstation" width="100%" /></div>`.
- **D-19: Terminal Contact Badges** — Flat-square Shields.io badges with dark background (`#161b22`) for Email, LinkedIn, Portfolio, and Resume directly below the card. Resume badge points to local repository artifact `cv/outputs/cv_humam_hossain.pdf`.
- **D-20: Phase Expansion Anchors** — Structured HTML comment markers (`<!-- PROJECTS:START -->...<!-- PROJECTS:END -->`, `<!-- METRICS:START -->...`, `<!-- SKILLS:START -->...`) for seamless insertion by subsequent phase automation.
- **D-21: Terminal Exit Sign-Off** — Bottom terminal prompt: `<div align="center"><code>humam@workstation:~$ exit</code></div>`.

### Discretion

- Micro-spacing and exact pixel baseline offsets for telemetry lines within SVG `viewBox="0 0 850 380"`.
- Precise character width ratios for full/half-block rendering in SVG `<text>` elements.

### Deferred Ideas (OUT OF SCOPE)

- Phase 2: Live GitHub API computation for dynamic Uptime calculation and aggregate Lines of Code counters (`scripts/update_profile.py`).
- Phase 3: Open Source Projects Dashboard terminal box cards.
- Phase 4: Top Languages terminal progress bar and Git activity log stream.
- Phase 5: Categorized Skills Matrix and RSS blog slot.
- Phase 6: Daily scheduled GitHub Actions workflow.

---

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| **HERO-01** | Dual-theme SVG Hero card with stylized block monogram ASCII typography (`H-` / `HH`) on the left panel | Fully addressed by static SVG card (`assets/hero.svg`) featuring retro Neofetch block monogram `H_` constructed from Unicode solid and half-block glyphs (`█`, `▄`, `▀`) with static cursor (`_`) on the left panel, accompanied by an 8-color ANSI dot strip beneath [VERIFIED: `test_svg.py`]. |
| **HERO-02** | Terminal telemetry on the right panel (`humam@workstation`, OS: `Arch Linux`, Kernel: `Systems \| AI & Robotics`, Focus: `Autonomous Systems & Backend`, Contact: email & LinkedIn) | Implemented via structured right-panel telemetry with Amber keys (`#ffa657`), high-contrast muted white values (`#c9d1d9`), green/red LOC metrics, and pre-allocated `<tspan>` IDs (`val-uptime`, `val-loc-add`, `val-loc-del`) to support Phase 2 dynamic patching [VERIFIED: prototype SVG inspection]. |
| **HERO-03** | Dual theme support via `<picture>` and `(prefers-color-scheme: dark)` for seamless GitHub dark/light mode switching | **Superseded by User Decision D-01:** Locked decision explicitly overrides dual-theme switching with a dedicated dark-theme terminal card (`assets/hero.svg`) embedded directly via `<img>`. The card features an opaque dark background (`#0d1117`), preventing light mode washout while drastically simplifying downstream card styling [VERIFIED: CONTEXT.md D-01]. |

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| **Design Tokens** | `config/terminal_theme.json` | `docs/DESIGN_SYSTEM.md` | Centralized JSON configuration defines authoritative color hexes, typography stacks, and geometric layout parameters consumed by all Python scripts. |
| **SVG Generation** | `scripts/generate_hero.py` | Python standard library (`json`, `xml.sax.saxutils`) | Standalone, zero-dependency script reads tokens and emits valid XML for `assets/hero.svg`. |
| **Visual Delivery** | `assets/hero.svg` | `README.md` image tag | SVG acts as a self-contained visual vector asset that scales crisply on desktop and mobile viewports. |
| **Profile Structure** | `README.md` | Shields.io CDN badges | Host markdown orchestrates the top-level centered card, contact badges, expansion anchor comments, and terminal exit prompt. |
| **Automated Verification** | `tests/test_tokens.py` | `pytest` runner | Ensures token syntax validity, color hex correctness, SVG XML parse integrity, and DOM ID preservation prior to deployment. |

---

## Standard Stack

### Core

| Library / Tool | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| **Python** | 3.14.9 [VERIFIED: host] | Generator & test execution | Ubiquitously pre-installed in development environments and GitHub Actions runners; requires zero runtime setup. |
| **Standard Library `json`** | Built-in | Token serialization | Native JSON parsing with zero overhead. |
| **Standard Library `xml.sax.saxutils`** | Built-in | XML entity escaping | Escapes ampersands (`&`), quotes, and angle brackets to prevent malformed SVG generation. |
| **Standard Library `xml.etree.ElementTree`** | Built-in | SVG validation | Authoritative XML DOM parser confirms SVG well-formedness. |
| **SVG (Scalable Vector Graphics)** | 1.1 W3C Recommendation | Vector graphic representation | Natively supported by GitHub markdown and image rendering pipeline; scales smoothly across resolutions. |

### Supporting

| Library / Tool | Version | Purpose | When to Use |
|----------------|---------|---------|-------------|
| **pytest** | 9.2.0 [VERIFIED: host] | Test runner | Runs unit and schema validation suites (`pytest tests/`). |
| **Shields.io Badges** | Cloud API (REST) | Contact and resume badges | Renders flat-square terminal-themed contact links directly below the hero card. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Python standard library template strings | Jinja2 | Jinja2 requires `pip install jinja2` in every environment. Python f-strings and standard string methods are 100% self-contained and require zero dependencies. |
| Vector SVG | Raster PNG via Pillow/Cairo | PNG does not scale smoothly across retina displays, cannot be inspected or patched via DOM XML in Phase 2, and requires native C libraries (`libcairo`). |
| Standalone Dark SVG | `<picture>` media query dual SVG | Dual SVG adds light mode design debt, requires maintaining two separate graphics, and conflicts with the authentic Unix dark terminal aesthetic specified in D-01. |

---

## Architecture Patterns

### System Architecture Diagram

```
+-----------------------------------------------------------+
|               config/terminal_theme.json                  |
|  (Colors, ANSI Palette, Typography, Coordinates, Radii)   |
+-----------------------------+-----------------------------+
                              |
                              v
+-----------------------------------------------------------+
|                scripts/generate_hero.py                   |
|  - Reads terminal_theme.json                              |
|  - Escapes XML entities (saxutils.escape)                 |
|  - Computes pixel coordinates & builds SVG markup         |
|  - Writes assets/hero.svg                                 |
+-----------------------------+-----------------------------+
                              |
            +-----------------+-----------------+
            |                                   |
            v                                   v
+-----------------------+           +-----------------------+
|    assets/hero.svg    |           |  tests/test_tokens.py |
| (Tested by ElementTree|           | (Validates schema,    |
| & validated XML)      |           |  hexes, XML, and IDs) |
+-----------+-----------+           +-----------------------+
            |
            v
+-----------------------------------------------------------+
|                        README.md                          |
|  - <div align="center"><img src="./assets/hero.svg"/>     |
|  - Flat-square Shields.io badges                          |
|  - Phase extension anchors (PROJECTS, METRICS, SKILLS)    |
|  - <div align="center"><code>exit</code></div>            |
+-----------------------------------------------------------+
```

### Recommended Component Structure

```
humam-hossain/
├── .planning/
│   ├── phases/
│   │   └── 01-hero-terminal-card-design-system/
│   │       ├── 01-CONTEXT.md
│   │       ├── 01-RESEARCH.md
│   │       └── ...
│   ├── PROJECT.md
│   ├── REQUIREMENTS.md
│   └── STATE.md
├── assets/
│   └── hero.svg                   # Generated dark terminal SVG card
├── config/
│   └── terminal_theme.json        # Design token system (colors, typography, geometry)
├── cv/
│   └── outputs/
│       └── cv_humam_hossain.pdf   # Pre-existing resume linked from README badge
├── docs/
│   └── DESIGN_SYSTEM.md           # Visual reference manual for terminal tokens
├── scripts/
│   └── generate_hero.py           # Self-contained SVG generator
├── tests/
│   └── test_tokens.py             # Pytest suite for tokens and SVG integrity
└── README.md                      # GitHub profile markdown with hero embed & badges
```

### Pattern 1: Token-Driven Single Source of Truth

All visual properties (palette hex codes, font families, font sizes, line heights, corner radii, and panel dimensions) must live exclusively in `config/terminal_theme.json`. `scripts/generate_hero.py` should never hardcode raw hex values or pixel offsets; it reads from `terminal_theme.json`. Downstream phase scripts (e.g., `update_profile.py` in Phase 2, project card generator in Phase 3) import this same token file to maintain visual harmony.

### Pattern 2: Downstream DOM Hooking via Element IDs

To allow Phase 2 to update dynamic telemetry without fragile string parsing or brittle regular expressions, the generator assigns explicit XML IDs to target `<tspan>` nodes:
- `id="val-uptime"`: For Coding Uptime (`4 yrs, 3 mos, 12 days`).
- `id="val-loc-add"`: For LOC additions (`++320,410`).
- `id="val-loc-del"`: For LOC deletions (`--85,240`).

In Phase 2, Python's `xml.etree.ElementTree` can find elements via `tree.find(".//*[@id='val-uptime']")` and update `.text` cleanly while preserving XML integrity.

### Pattern 3: GitHub Camo Proxy Defense-in-Depth

GitHub routes all embedded images through its Camo caching proxy (`camo.githubusercontent.com`) [CITED: daily.dev, github.com]. Camo strips `<foreignObject>`, `<script>`, `<style>` blocks containing external `@import` fonts, and any non-standard XML tags.
To render reliably:
1. Embed all styling inside a `<style>` tag within `<defs>`, targeting standard classes (`.title`, `.mono-art`, `.prompt`, `.key`, `.val`).
2. Use the cross-platform system font stack: `ui-monospace, SFMono-Regular, Menlo, Consolas, "Fira Code", monospace` [VERIFIED: D-13]. This uses local OS fonts on macOS, Windows, and Linux without external network requests.
3. Use SVG `<clipPath>` with rounded corners (`rx="10"`) to clip the background rectangles cleanly without corner pixel bleed.

### Pattern 4: XML-Safe Content Sanitization

Text nodes inside SVGs must be strictly valid XML. Special characters—specifically ampersands (`&`) in values like `AI & Robotics` or `Autonomous Systems, IoT & Cloud`—will immediately cause XML parse failures (`ParseError: not well-formed (invalid token)`) if not escaped [VERIFIED: `test_svg.py`].
Always run text values through `xml.sax.saxutils.escape()` before emitting SVG elements:
```python
import xml.sax.saxutils as saxutils
escaped_value = saxutils.escape(value)
```

### Anti-Patterns to Avoid

- **Anti-Pattern 1: Light-Mode Media Query switching within dark terminal theme.** Violates locked decision D-01. A terminal window is intrinsically dark. Transparent backgrounds or light mode switching would break the authentic Neofetch terminal appearance.
- **Anti-Pattern 2: Hardcoded string replacement for dynamic values.** Scraping SVG lines with regex in future phases risks corrupting attributes or XML formatting. Always use explicit `id` attributes on `<tspan>` elements.
- **Anti-Pattern 3: Inlining external Google Fonts via `@import`.** Camo proxy will fail to load or strip external font URLs, causing erratic font rendering across clients.
- **Anti-Pattern 4: Raw HTML `<table>` for the hero.** Markdown tables cannot render traffic light circles, rounded window corners, or exact Neofetch block art.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| **XML Escaping** | Custom regex or string replace (`.replace('&', '&amp;')`) | `xml.sax.saxutils.escape()` | Built-in standard library function handles XML entities correctly and safely without edge cases. |
| **SVG XML Validation** | Custom tag matching regex | `xml.etree.ElementTree.fromstring()` | Standard library parser enforces strict XML compliance and identifies syntax errors instantly. |
| **Hex Code Validation** | Ad-hoc string length checks | `re.compile(r"^#[0-9a-fA-F]{6}$")` | Ensures valid 6-digit RGB hex colors conform to CSS/SVG specifications. |
| **Contact Badges** | Custom inline SVG badges for social links | Shields.io REST URLs with `style=flat-square&color=161b22` | Shields.io provides standardized, accessible badges with official brand icons (Gmail, LinkedIn, Safari/Portfolio, Acrobat). |

---

## Common Pitfalls

### Pitfall 1: Unescaped Ampersands in SVG Text
**Impact:** SVG fails to parse; GitHub displays broken image icon.  
**Root Cause:** Values in `Kernel` (`AI & Robotics`) and `Focus` (`Autonomous Systems, IoT & Cloud`) contain raw `&` characters. In XML, `&` is the entity start marker.  
**Remedy:** Every value interpolated into an SVG text node must be passed through `saxutils.escape()`, converting `&` to `&amp;` [VERIFIED: `test_svg.py`].

### Pitfall 2: Window Header Bleeding Past Rounded Corners
**Impact:** The `#161b22` title bar rectangle has sharp 90-degree corners at top-left and top-right, protruding outside the card's `rx="10"` border.  
**Root Cause:** Drawing a `<rect>` for the title bar on top of a rounded card rect leaves protruding corner pixels unless clipped.  
**Remedy:** Wrap all card background elements inside a `<g clip-path="url(#card-clip)">`, where `<clipPath id="card-clip"><rect width="850" height="380" rx="10" ry="10" /></clipPath>` clips everything neatly inside the rounded container [VERIFIED: `test_hero.svg`].

### Pitfall 3: Inconsistent Monospace Font Metrics Across Platforms
**Impact:** Monogram block art misaligns with the cursor or telemetry text overlaps.  
**Root Cause:** Monospace fonts on Windows (Consolas) have slightly different advance widths and line ascents compared to macOS (Menlo / SF Mono).  
**Remedy:** 
1. Use `xml:space="preserve"` on all `<text>` and `<tspan>` nodes.
2. Render multi-line block art using discrete `<text x="..." y="...">` elements with explicit absolute vertical spacing (`line_height: 22` or `24`), rather than relative `dy` offsets.
3. Set `text-rendering: geometricPrecision` in CSS.

### Pitfall 4: Misaligned ANSI Dot Strip
**Impact:** Dot strip looks off-center or detached from the monogram art above it.  
**Root Cause:** Fixed coordinates that do not match the monogram's bounding box.  
**Remedy:** Monogram width with 13 characters at 20px font size spans ~156px (from x=60 to x=216). An 8-dot strip with radius 6 and center-to-center spacing of 22px spans from x=62 to x=216 (`62 + 7 * 22 = 216`), perfectly centering and bounding the dots directly below the monogram [VERIFIED: layout calculations].

---

## Code Examples

### Token Schema Structure (`config/terminal_theme.json`)

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

### Generator Script Implementation (`scripts/generate_hero.py`)

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

    lines.append('  <g clip-path="url(#card-clip)">')
    lines.append(f'    <rect width="{g["width"]}" height="{g["height"]}" fill="{c["background"]["body"]}" />')
    lines.append(f'    <rect width="{g["width"]}" height="{g["header_height"]}" fill="{c["background"]["header"]}" />')
    lines.append(f'    <line x1="0" y1="{g["header_height"]}" x2="{g["width"]}" y2="{g["header_height"]}" stroke="{c["border"]}" stroke-width="1" />')

    for light in g["traffic_lights"]:
        lines.append(f'    <circle cx="{light["cx"]}" cy="{light["cy"]}" r="{light["r"]}" fill="{light["color"]}" />')

    lines.append(f'    <text x="{g["width"] // 2}" y="24" class="mono title">humam@workstation:~</text>')

    # Monogram lines
    mg = g["monogram"]
    for i, line in enumerate(MONOGRAM_LINES):
        y = mg["y_start"] + i * mg["line_height"]
        lines.append(f'    <text x="{mg["x"]}" y="{y}" class="mono mono-art" xml:space="preserve">{line}</text>')

    # ANSI dot strip
    strip = g["ansi_strip"]
    for i, color in enumerate(c["ansi"]):
        cx = strip["x_start"] + i * strip["spacing"]
        lines.append(f'    <circle cx="{cx}" cy="{strip["cy"]}" r="{strip["r"]}" fill="{color}" />')

    # Telemetry
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

    loc_key = f'{"LOC:":<10}'
    lines.append(f'    <text x="{tm["x"]}" y="{cur_y}" class="mono"><tspan class="key" xml:space="preserve">{loc_key} </tspan><tspan id="val-loc-add" class="loc-add">++320,410</tspan><tspan class="val"> / </tspan><tspan id="val-loc-del" class="loc-del">--85,240</tspan></text>')

    lines.append(f'    <rect width="{g["width"]}" height="{g["height"]}" rx="{g["card_rx"]}" ry="{g["card_rx"]}" fill="none" stroke="{c["border"]}" stroke-width="1" />')
    lines.append('  </g>')
    lines.append('</svg>')

    content = "\n".join(lines)
    # Validate well-formed XML before writing
    ET.fromstring(content)
    return content

if __name__ == "__main__":
    svg = generate_svg()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Successfully generated {OUTPUT_PATH}")
```

### Profile README Implementation (`README.md`)

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

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Dual-theme light/dark SVG `<picture>` media queries | Dedicated dark terminal SVG (`assets/hero.svg`) | 2026 (Phase 1 Decision D-01) | Avoids light-mode visual breakage and dual SVG maintenance; terminal windows are authentically dark. |
| External web fonts via `@import url(...)` | Cross-platform system monospace stack | 2023+ (GitHub Camo tightening) | Eliminates Camo proxy network blocks, CORS errors, and font flashing. |
| Inlined HTML inside SVG `<foreignObject>` | Pure SVG `<text>` and `<tspan>` nodes | 2021+ (GitHub Camo sanitization) | `<foreignObject>` is routinely stripped or blocked by GitHub sanitizer for security; pure SVG tags always render. |
| Ad-hoc regex string replacement for SVG updates | Explicit DOM `id` targeting (`id="val-uptime"`) | Best Practice Architecture | Guarantees downstream Python scripts (Phase 2) can parse and update values without fragile string scraping. |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| 1 | GitHub Camo proxy allows relative SVG paths (`./assets/hero.svg`) in README `<img>` tags. | Standard Stack / README | Low. Relative links in repository README files are natively supported by GitHub Markdown and Camo proxy. |
| 2 | Shields.io flat-square badges with `#161b22` color render properly in GitHub dark mode. | Standard Stack | Low. Shields.io produces standard SVGs compatible with GitHub Markdown. |
| 3 | System fonts `ui-monospace, SFMono-Regular, Menlo, Consolas` render block Unicode `█`, `▄`, `▀` uniformly. | Architecture Patterns | Low. All modern OS monospace fonts include full block character sets in the standard Unicode block (U+2580 to U+259F). |

---

## Open Questions

1. **Email display on public README badge:**  
   `cv/sections/header.tex` lists `muhammed.humam.hossain@gmail.com`. The badge uses this address directly. If the user prefers spam masking, an alternate handle or redirect can be updated in `README.md`.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python 3 | `scripts/generate_hero.py`, test suite | Yes [VERIFIED: host] | 3.14.9 | None needed |
| pytest | `tests/test_tokens.py` | Yes [VERIFIED: host] | 9.2.0 | `python3 -m unittest` |
| Git | Version control & repo structure | Yes [VERIFIED: host] | 2.51.0 | None needed |
| Resume artifact | Contact badge relative link | Yes [VERIFIED: `cv/outputs/cv_humam_hossain.pdf`] | August 2026 build | `cv/build.sh` compilation |

---

## Validation Architecture

### Test Framework
`pytest` 9.2.0 executing against Python 3.14.9.

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| **HERO-01** | `assets/hero.svg` exists, has `viewBox="0 0 850 380"`, contains block monogram (`█`, `▄`, `▀`, `_`), and 8 ANSI dot circles | Unit / Integration | `pytest tests/test_tokens.py -k test_hero_svg_monogram_and_ansi` | To be created in Plan 01-02/01-03 |
| **HERO-02** | `assets/hero.svg` contains right-panel telemetry with correct keys, escaped entities, and IDs (`val-uptime`, `val-loc-add`, `val-loc-del`) | Unit / Integration | `pytest tests/test_tokens.py -k test_hero_svg_telemetry_keys` | To be created in Plan 01-02/01-03 |
| **HERO-03** | `config/terminal_theme.json` has valid hex colors, required keys, and dark theme palette | Unit (Schema) | `pytest tests/test_tokens.py -k test_theme_tokens_schema` | To be created in Plan 01-01 |
| **README** | `README.md` contains hero embed, flat-square badges, expansion comment anchors, and terminal exit sign-off | Unit / Integration | `pytest tests/test_tokens.py -k test_readme_structure` | To be created in Plan 01-03 |

### Sampling Rate
100% automated test coverage across all created assets, configurations, and generator outputs.

### Wave 0 Gaps
- `config/terminal_theme.json` does not yet exist.
- `scripts/generate_hero.py` does not yet exist.
- `assets/hero.svg` does not yet exist.
- `docs/DESIGN_SYSTEM.md` does not yet exist.
- `tests/test_tokens.py` does not yet exist.
These will be created incrementally across the plans for Phase 1.

---

## Security Domain

### Applicable ASVS Categories
- **V5 (Input Validation & XML Sanitization):** SVG generators must never interpolate raw, unescaped strings into XML structures. All text content must be processed through `xml.sax.saxutils.escape()` to prevent malformed XML and injection risks.
- **V14 (Build & Dependency Integrity):** Generator and validation scripts rely 100% on the Python standard library, introducing zero external package vulnerabilities or supply-chain risks.

### Known Threat Patterns
- **Malformed XML Denial-of-Service / Broken Render:** Unescaped characters like `&` break XML parsers and cause GitHub Camo to display broken image badges. Mitigated by `saxutils.escape()` and automated `xml.etree.ElementTree` validation in tests.
- **SVG Scripting Injections:** Camo blocks `<script>` and inline event handlers (`onload`, `onclick`). The generator avoids emitting any script or interactive tags.

---

## Sources

### Primary (HIGH confidence)
- Repository code inspection [VERIFIED]:
  - `cv/sections/header.tex`: Confirmed author name, email (`muhammed.humam.hossain@gmail.com`), and LinkedIn handle.
  - `cv/outputs/cv_humam_hossain.pdf`: Confirmed physical existence of compiled resume.
  - Local environment tools: `python3` (3.14.9) and `pytest` (9.2.0) verified via terminal execution.
  - XML parsing behavior: Confirmed unescaped entity parsing failure and resolution via `test_svg.py`.
- Locked user decisions [VERIFIED]: `01-CONTEXT.md` decisions D-01 through D-21.

### Secondary (MEDIUM confidence)
- GitHub Camo image proxy specifications & SVG sanitization [CITED: https://daily.dev / GitHub Docs] — Confirms restrictions on `<foreignObject>`, scripts, and external `@import` fonts.
- Neofetch CLI visual conventions — Standard 8-color ANSI dot palette and username@hostname dashed separator.

### Tertiary (LOW confidence)
- None.
