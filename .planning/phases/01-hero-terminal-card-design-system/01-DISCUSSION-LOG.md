# Phase 1: Hero Terminal Card & Design System - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-11-07
**Phase:** 1-Hero Terminal Card & Design System
**Areas discussed:** ASCII monogram style, Terminal telemetry content, SVG card frame & layout, Dark vs Light theme delta, Design system token file, README.md profile structure, SVG asset location & file naming, ANSI color strip shape & layout

---

## ASCII Monogram Style

| Option | Description | Selected |
|--------|-------------|----------|
| Large block-art H- | Unicode full-block/half-block elements (█▄▀) — retro Neofetch vibe, ~8-10 lines tall | ✓ |
| Compact H- | Box-drawing characters (│─┌┐) — cleaner, ~4-5 lines tall | |
| Figlet HH | ASCII characters (#, =, \|) | |
| Minimal H | Typography over art with blinking cursor | |

| Option | Description | Selected |
|--------|-------------|----------|
| Amber (#ffa657) | Warm classic terminal amber | |
| Green (#3fb950) | Classic Matrix hacker aesthetic | |
| Cyan (#a5d6ff) | Cooler tone, modern terminal feel | ✓ |
| Multi-color gradient | Gradient transition | |

| Option | Description | Selected |
|--------|-------------|----------|
| H- | Stylized dash as design element | |
| HH | Double initial monogram | |
| H_ | Underscore cursor simulating terminal prompt waiting for input | ✓ |

| Option | Description | Selected |
|--------|-------------|----------|
| Standalone monogram block | Clean separation, art piece on its own | ✓ |
| Monogram in info box | Neofetch-style framed sub-box | |
| Monogram with prompt line | Terminal prompt line directly below | |

| Option | Description | Selected |
|--------|-------------|----------|
| ~8-10 lines tall | Matches Neofetch scale, fills left panel | ✓ |
| ~5-6 lines tall | Medium size | |
| ~12+ lines tall | Oversized | |

| Option | Description | Selected |
|--------|-------------|----------|
| Solid block fill (█▄▀) | Bold standard Neofetch ASCII art style | ✓ |
| Outlined letters (│─) | Refined hollow edges | |
| Dotted/pixelated (▓▒░) | CRT / pixel-art texture | |

| Option | Description | Selected |
|--------|-------------|----------|
| Static underscore | Always visible, simple and reliable in SVG | ✓ |
| Animated blinking cursor | CSS keyframes pulse | |
| No cursor element | Single letter only | |

| Option | Description | Selected |
|--------|-------------|----------|
| ANSI color strip below | 8 ANSI color blocks/dots classic Neofetch style | ✓ |
| No color strip | Clean panel with monogram only | |
| Shell prompt below | e.g. status: online | |

---

## Terminal Telemetry Content

| Option | Description | Selected |
|--------|-------------|----------|
| humam@workstation | Modern developer workstation with prompt separator | ✓ |
| humam@archlinux | Arch Linux enthusiast identity in hostname | |
| humam@homeserver | Homeserver/sysadmin focus | |

| Option | Description | Selected |
|--------|-------------|----------|
| Full Neofetch-style set | OS, Host, Kernel, Focus, Uptime, Shell, Contact, LOC | ✓ |
| Minimal set | OS, Focus, Uptime, Contact | |
| Engineering focus set | Stack, Uptime, LOC, Projects, Contact | |

| Option | Description | Selected |
|--------|-------------|----------|
| Amber labels (#ffa657) + white values | High contrast, warm terminal hierarchy | ✓ |
| Cyan labels (#a5d6ff) + white values | Unified cyan palette | |
| Green labels (#3fb950) + white values | Classic Unix green prompt | |

| Option | Description | Selected |
|--------|-------------|----------|
| Formatted text values | Text in SVG; clickable badges below card in README | ✓ |
| Short handles only | Compact single line | |
| Omit from SVG card | Exclusively markdown links | |

| Option | Description | Selected |
|--------|-------------|----------|
| Dashed rule (-------------------) | Authentic Neofetch divider in muted gray (#616e7f) | ✓ |
| Unicode solid line (───) | Solid line in accent color | |
| No separator line | Direct transition | |

| Option | Description | Selected |
|--------|-------------|----------|
| Realistic static values | Looks finished in Phase 1 before Phase 2 activates | ✓ |
| Explicit placeholder tags | [syncing...] / [calculating...] | |
| Omit rows until Phase 2 | Added only when automated | |

| Option | Description | Selected |
|--------|-------------|----------|
| Arch Linux x86_64, zsh 5.9, Workstation | Standard modern Linux power-user setup | ✓ |
| Arch Linux, bash 5.2, Homeserver | Server hosting background | |
| Arch Linux x86_64, fish 3.7, ThinkPad | Interactive shell setup | |

**Custom Wording:** User specified `Kernel: AI & Robotics, Focus: Autonomous Systems, IoT & Cloud`.

---

## SVG Card Frame & Layout

| Option | Description | Selected |
|--------|-------------|----------|
| Window title bar with colored traffic lights | 🔴 🟡 🟢 dots + centered title "humam@workstation:~" | ✓ |
| Monochrome control dots | Minimalist title bar | |
| ASCII window controls | [x] [-] [+] | |
| Frameless card | No title bar | |

| Option | Description | Selected |
|--------|-------------|----------|
| Modern terminal window | rx="10" rounded corners, 1px border (#30363d) | ✓ |
| Sharp corners | rx="0" rectangular box | |
| Glow/shadow effect | Cyberpunk ambient depth | |

| Option | Description | Selected |
|--------|-------------|----------|
| Standard profile width | viewBox="0 0 850 380" (width="100%") | ✓ |
| Wider cinematic ratio | viewBox="0 0 920 360" | |
| Compact card | viewBox="0 0 750 350" | |

| Option | Description | Selected |
|--------|-------------|----------|
| Clean whitespace gap | ~35% monogram, ~65% telemetry, no artificial divider line | ✓ |
| Vertical separator line | 1px dashed/solid border | |
| 40/60 split with box border | Box-drawing column border | |

| Option | Description | Selected |
|--------|-------------|----------|
| Dual-tone dark window | Header #161b22 with 1px border over #0d1117 console body | ✓ |
| Flat dark background | #0d1117 throughout | |
| OLED black | #000000 background | |

| Option | Description | Selected |
|--------|-------------|----------|
| Cross-platform system monospace | ui-monospace, SFMono-Regular, Menlo, Consolas, Fira Code, monospace | ✓ |
| Strict Fira Code priority | Fira Code, Consolas, monospace | |
| Classic Courier stack | Courier New, monospace | |

---

## Dark vs Light Theme Delta

| Option | Description | Selected |
|--------|-------------|----------|
| One theme only: Dark theme | Build exclusively for Dark mode. Skip light mode SVG and picture media queries | ✓ |
| Dual theme (Dark + Light) | Separate dark_mode.svg and light_mode.svg via `<picture>` | |

**User statement:** "one theme only dark theme. no need to think about light theme"

---

## Design System Token File

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated JSON config | config/terminal_theme.json accessible to Python and templates | ✓ |
| Python theme module | scripts/theme.py dataclass | |
| Inline SVG styling | Tokens in SVG only | |

| Option | Description | Selected |
|--------|-------------|----------|
| Comprehensive token schema | Colors, typography, dimensions, padding, radii | ✓ |
| Minimal colors & fonts only | Hex values and font strings | |
| Full schema + template metadata | Positions and coordinates | |

| Option | Description | Selected |
|--------|-------------|----------|
| Create docs/DESIGN_SYSTEM.md | Human-readable specification with swatches and guidelines | ✓ |
| No extra markdown doc | JSON only | |

| Option | Description | Selected |
|--------|-------------|----------|
| Python generator script | scripts/generate_hero.py reading config/terminal_theme.json | ✓ |
| Handcrafted static SVG | Manual SVG authoring | |
| Jinja2 template | External pip dependency | |

| Option | Description | Selected |
|--------|-------------|----------|
| Harmonized GitHub Dark ANSI | Matches GitHub Dark UI with Amber, Cyan, Green accents | ✓ |
| Alacritty / Arch default | Distribution default ANSI | |
| Strict minimal 6-color | Only used colors | |

| Option | Description | Selected |
|--------|-------------|----------|
| Lightweight Python test script | tests/test_tokens.py validating hex codes, schema, SVG XML | ✓ |
| Inline assertions | Script assertions only | |
| No test script | Visual inspection only | |

---

## README.md Profile Structure

| Option | Description | Selected |
|--------|-------------|----------|
| Centered alignment | `<div align="center">` balances card across all screens | ✓ |
| Left-aligned markdown | `![Terminal Hero](...)` left justification | |

| Option | Description | Selected |
|--------|-------------|----------|
| Immediate visual opener | Card starts directly at the top with no redundant header | ✓ |
| Terminal prompt heading | `<h3 align="center"><code>$ whoami</code></h3>` | |
| Formal heading | `<h1>Muhammed Humam Hossain</h1>` | |

| Option | Description | Selected |
|--------|-------------|----------|
| Dark terminal badges | Shields.io flat-square with #161b22 bg for Email, LinkedIn, Portfolio, Resume | ✓ |
| Monospace text links | `[email] • [linkedin] • [portfolio] • [cv]` | |
| One-liner bio + badges | Short bio between card and badges | |

| Option | Description | Selected |
|--------|-------------|----------|
| Structured comment markers | `<!-- PROJECTS:START -->`, `<!-- METRICS:START -->`, etc. | ✓ |
| Minimal Phase 1 only | Add markers incrementally | |

| Option | Description | Selected |
|--------|-------------|----------|
| Terminal exit prompt footer | `<div align="center"><code>humam@workstation:~$ exit</code></div>` | ✓ |
| Copyright/built-with | Text footer | |
| No footer | Clean end | |

| Option | Description | Selected |
|--------|-------------|----------|
| Link to repo PDF | `cv/outputs/cv_humam_hossain.pdf` self-contained link | ✓ |
| Hosted link / Drive | External URL | |
| Omit CV badge | Email, LinkedIn, Portfolio only | |

---

## SVG Asset Location & File Naming

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated assets/ folder | assets/hero.svg | ✓ |
| public/images/ | Inside Next.js static asset folder | |
| Repository root | hero.svg | |

| Option | Description | Selected |
|--------|-------------|----------|
| Relative HTML image tag | `<img src="./assets/hero.svg" alt="humam@workstation" width="100%" />` | ✓ |
| Markdown image syntax | `![humam@workstation](./assets/hero.svg)` | |
| Raw GitHub URL | With cache-busting query parameter | |

| Option | Description | Selected |
|--------|-------------|----------|
| Standardize assets/ | Uniform location for all profile SVGs across phases | ✓ |
| Per-phase decisions | Varying locations | |

| Option | Description | Selected |
|--------|-------------|----------|
| Pure Python generator | Structured SVG builder in scripts/generate_hero.py with zero extra packages | ✓ |
| External template file | templates/hero.svg.template | |
| Jinja2 template | Requires jinja2 package | |

---

## ANSI Color Strip Shape & Layout

| Option | Description | Selected |
|--------|-------------|----------|
| Circular color dots | `<circle r="6">` with smooth spacing | ✓ |
| Rounded pills | `<rect width="18" height="10" rx="3">` | |
| Square solid blocks | `<rect width="14" height="14">` | |

| Option | Description | Selected |
|--------|-------------|----------|
| Single row of 8 dots | Compact, elegant balance beneath monogram | ✓ |
| Dual row of 16 dots | 8 standard + 8 bright variants | |

| Option | Description | Selected |
|--------|-------------|----------|
| Centered horizontally | Directly beneath H_ monogram block | ✓ |
| Left-aligned | Aligned with monogram left edge | |

---

## the agent's Discretion

- Precise micro-typography baseline offsets for telemetry text rows inside `viewBox="0 0 850 380"`.
- Character width spacing of Unicode block elements (`█▄▀`) in SVG `<text>`.

## Deferred Ideas

- None for Phase 1 scope.
