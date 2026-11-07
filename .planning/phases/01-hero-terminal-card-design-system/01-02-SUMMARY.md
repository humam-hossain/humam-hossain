---
phase: 01-hero-terminal-card-design-system
plan: 02
subsystem: ui-component
tags: [terminal, hero-card, svg, python, monogram, telemetry, xml]

requires:
  - phase: 01-01
    provides: "Terminal design tokens in config/terminal_theme.json and test suite in tests/test_tokens.py"
provides:
  - Deterministic Python SVG generator in scripts/generate_hero.py
  - Production terminal hero vector asset in assets/hero.svg
affects:
  - 01-03-PLAN.md
  - Phase 2-5 dynamic SVG updater scripts

actuals:
  tokens: 1420
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - Pure standard library Python SVG generator (json, xml.sax.saxutils, xml.etree.ElementTree)
    - ClipPath bounding box protection preventing corner pixel bleeding
    - Dedicated DOM ID reservation for downstream dynamic metrics updating (val-uptime, val-loc-add, val-loc-del)

key-files:
  created:
    - scripts/generate_hero.py
    - assets/hero.svg
  modified: []

key-decisions:
  - "Built generator with zero external runtime dependencies using Python standard library exclusively"
  - "Wrapped window body and header in SVG clipPath to guarantee clean rounded corners without pixel bleed"
  - "Applied saxutils.escape() to all telemetry values to ensure 100% well-formed XML for GitHub Camo proxy delivery"
  - "Embedded DOM IDs val-uptime, val-loc-add, and val-loc-del to enable Phase 2 dynamic patching"

patterns-established:
  - "Deterministic vector generation: scripts/generate_hero.py compiles tokens into production assets/hero.svg"
  - "DOM-addressable SVG hooks: Element IDs permanently reserved for workflow updaters"

requirements-completed:
  - HERO-01
  - HERO-02

coverage:
  - id: D1
    description: "Pure Python SVG hero generator script"
    requirement: "HERO-01"
    verification:
      - kind: unit
        ref: "tests/test_tokens.py::test_hero_svg_generation"
        status: pass
  - id: D2
    description: "Neofetch H_ block monogram and 8-dot ANSI diagnostic strip"
    requirement: "HERO-01"
    verification:
      - kind: unit
        ref: "tests/test_tokens.py::test_hero_svg_monogram_and_ansi"
        status: pass
  - id: D3
    description: "System telemetry panel with XML-escaped ampersands and DOM IDs"
    requirement: "HERO-02"
    verification:
      - kind: unit
        ref: "tests/test_tokens.py::test_hero_svg_telemetry_keys"
        status: pass
  - id: D4
    description: "Production assets/hero.svg vector asset"
    requirement: "HERO-01"
    verification:
      - kind: unit
        ref: "assets/hero.svg"
        status: pass
---

# Plan 01-02 Summary: Python Hero SVG Generator & Production Terminal Vector Asset

## Accomplishments
- Implemented `scripts/generate_hero.py` utilizing Python standard library modules (`json`, `xml.sax.saxutils`, `xml.etree.ElementTree`).
- Rendered macOS window chrome with 3 traffic light circles, title bar, and `<clipPath id="card-clip">` corner isolation.
- Rendered the Neofetch `H_` block monogram in Cyan (`#a5d6ff`) using solid/half block glyphs (`█`, `▄`, `▀`, `_`) and 8-dot ANSI color strip.
- Rendered right-panel system telemetry with Amber keys (`#ffa657`), XML-escaped text (`AI &amp; Robotics`, `Autonomous Systems, IoT &amp; Cloud`), and reserved DOM IDs (`val-uptime`, `val-loc-add`, `val-loc-del`).
- Generated and verified `assets/hero.svg` (>3000 bytes, `viewBox="0 0 850 380"`, 11 circles, valid XML).
- Verified unit test suite: `test_hero_svg_generation`, `test_hero_svg_monogram_and_ansi`, and `test_hero_svg_telemetry_keys` all PASSED.

## Self-Check: PASSED
- `scripts/generate_hero.py` exists, is executable, and produces `assets/hero.svg`.
- `assets/hero.svg` is valid XML with correct `viewBox` and DOM hooks.
- All SVG unit tests in `tests/test_tokens.py` pass.
- Commits follow conventional commit standards.
