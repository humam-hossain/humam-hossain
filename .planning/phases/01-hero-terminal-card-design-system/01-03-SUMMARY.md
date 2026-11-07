---
phase: 01-hero-terminal-card-design-system
plan: 03
subsystem: profile-readme
tags: [readme, terminal, badges, shields-io, exit-prompt, anchors]

requires:
  - phase: 01-01
    provides: "Design tokens in config/terminal_theme.json and test suite in tests/test_tokens.py"
  - phase: 01-02
    provides: "Vector asset in assets/hero.svg"
provides:
  - Terminal-themed profile landing page in README.md
  - Shields.io flat-square dark contact badges
  - Downstream phase comment anchors (PROJECTS, METRICS, SKILLS)
  - Centered terminal exit prompt sign-off
affects:
  - Phase 2 (Live Telemetry & Activity Metrics)
  - Phase 3 (Language Distribution & Repository Cards)
  - Phase 4 (Open-Source Project Showcase)
  - Phase 5 (Technical Skills Grid)

actuals:
  tokens: 1250
  tasks: 2
  commits: 1

tech-stack:
  added: []
  patterns:
    - Centered vector image embed with 100% width for GitHub Camo delivery
    - Shields.io flat-square badges styled with structural #161b22 background
    - HTML comment expansion anchors for automated workflow templating
    - Terminal session exit sign-off pattern

key-files:
  created: []
  modified:
    - README.md

key-decisions:
  - "Embedded assets/hero.svg centered at 100% width as the immediate visual opener"
  - "Rendered flat-square Shields.io badges with #161b22 background for Email, LinkedIn, Portfolio, and local resume PDF"
  - "Structured comment extension anchors for PROJECTS, METRICS, and SKILLS to enable zero-collision automated insertions in Phases 2-5"
  - "Added terminal exit prompt humam@workstation:~$ exit to cleanly conclude profile session"

patterns-established:
  - "Profile Layout: Hero embed -> Contact badge row -> Automation anchors -> Exit prompt"
  - "Full Pytest E2E: Validates all Phase 1 deliverables simultaneously in 0.02s"

requirements-completed:
  - HERO-01
  - HERO-02
  - HERO-03

coverage:
  - id: D1
    description: "README.md hero SVG embed and layout"
    requirement: "HERO-01"
    verification:
      - kind: unit
        ref: "tests/test_tokens.py::test_readme_structure"
        status: pass
  - id: D2
    description: "Flat-square terminal Shields.io contact badges"
    requirement: "HERO-03"
    verification:
      - kind: unit
        ref: "tests/test_tokens.py::test_readme_structure"
        status: pass
  - id: D3
    description: "Phase automation comment anchors and terminal exit prompt"
    requirement: "HERO-02"
    verification:
      - kind: unit
        ref: "tests/test_tokens.py::test_readme_structure"
        status: pass
  - id: D4
    description: "Full Phase 1 test suite passing 100%"
    requirement: "HERO-03"
    verification:
      - kind: unit
        ref: "tests/test_tokens.py"
        status: pass
---

# Plan 01-03 Summary: Profile README Integration, Terminal Badges & End-to-End Validation

## Accomplishments
- Replaced placeholder `README.md` with authentic Unix terminal profile landing page.
- Embedded `assets/hero.svg` centered as the immediate visual opener (`width="100%"`).
- Styled and embedded flat-square Shields.io contact badges with `#161b22` background for Email, LinkedIn, Portfolio, and local tracked resume PDF (`./cv/outputs/cv_humam_hossain.pdf`).
- Planted comment delimiters (`<!-- PROJECTS:START -->`, `<!-- METRICS:START -->`, `<!-- SKILLS:START -->`) for Phase 2-5 script insertions.
- Added centered terminal exit prompt `humam@workstation:~$ exit`.
- Executed full automated test suite `pytest tests/test_tokens.py -v`, passing 5/5 tests in 0.02s with 100% success rate.

## Self-Check: PASSED
- `README.md` exists and contains hero card, badges, anchors, and exit prompt.
- Full pytest test suite passes without errors or warnings.
- All commits follow conventional commit standards.
