---
phase: 01-hero-terminal-card-design-system
plan: 01
subsystem: design-system
tags: [terminal, design-system, tokens, pytest, svg, design-contract]

requires: []
provides:
  - Centralized terminal design token configuration in config/terminal_theme.json
  - Wave 0 test infrastructure in tests/__init__.py and tests/test_tokens.py
  - Comprehensive terminal design system specification in docs/DESIGN_SYSTEM.md
affects:
  - 01-02-PLAN.md
  - 01-03-PLAN.md
  - Phase 2-5 metrics and automation workflows

actuals:
  tokens: 1850
  tasks: 3
  commits: 3

tech-stack:
  added:
    - pytest
  patterns:
    - Centralized JSON token configuration as single source of truth
    - Schema validation and hex code regex testing in pytest
    - 60-30-10 dark terminal color architecture with ANSI 8-color palette

key-files:
  created:
    - config/terminal_theme.json
    - docs/DESIGN_SYSTEM.md
    - tests/__init__.py
    - tests/test_tokens.py
  modified: []

key-decisions:
  - "Centralized terminal design tokens in config/terminal_theme.json as the single source of truth for colors, geometry, and typography"
  - "Built Wave 0 test suite with graceful fallback imports allowing incremental testing across multi-wave execution"
  - "Authored comprehensive visual design contract in docs/DESIGN_SYSTEM.md documenting 60-30-10 color hierarchy, Camo proxy hardening, and DOM ID reservations"

patterns-established:
  - "Tokens as config: Geometry, color hexes, and font sizes defined declaratively in JSON"
  - "Schema enforcement: Pytest validates token existence, 6-digit hex format, and array lengths"

requirements-completed:
  - HERO-03

coverage:
  - id: D1
    description: "Centralized terminal theme token specification"
    requirement: "HERO-03"
    verification:
      - kind: unit
        ref: "tests/test_tokens.py::test_theme_tokens_schema"
        status: pass
  - id: D2
    description: "Wave 0 pytest validation suite"
    requirement: "HERO-03"
    verification:
      - kind: unit
        ref: "tests/test_tokens.py"
        status: pass
  - id: D3
    description: "Terminal design system documentation"
    requirement: "HERO-03"
    verification:
      - kind: manual_procedural
        ref: "docs/DESIGN_SYSTEM.md"
        status: pass
---

# Plan 01-01 Summary: Terminal Design Tokens, Test Infrastructure & Design System Documentation

## Accomplishments
- Established Wave 0 test infrastructure with `tests/__init__.py` and `tests/test_tokens.py`, implementing validation for token schema, SVG structure, and README layout.
- Created `config/terminal_theme.json` acting as the authoritative single source of truth for card geometry, traffic light coordinates, monogram coordinates, ANSI 8-color strip, 60-30-10 color hierarchy, and monospace typography stack.
- Authored `docs/DESIGN_SYSTEM.md` detailing the visual design contract, color distribution, ANSI diagnostic palette, monospace font stack, window chrome coordinate grid, GitHub Camo proxy hardening, and Phase 2 DOM update hooks (`val-uptime`, `val-loc-add`, `val-loc-del`).
- Successfully verified all token schema assertions via `pytest tests/test_tokens.py -k test_theme_tokens_schema`.

## Self-Check: PASSED
- `config/terminal_theme.json` exists and is valid JSON matching schema.
- `docs/DESIGN_SYSTEM.md` exists and exceeds 1200 bytes.
- `tests/__init__.py` and `tests/test_tokens.py` exist and pass schema verification.
- All commits follow conventional commit standards.
