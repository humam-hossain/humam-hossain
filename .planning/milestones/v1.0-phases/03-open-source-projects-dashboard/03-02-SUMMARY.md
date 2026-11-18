---
phase: "03"
plan: "02"
subsystem: "ui-vector-graphics"
tags:
  - svg
  - terminal-ui
  - octicons
  - elementtree
requires:
  - "03-01"
provides:
  - "scripts/generate_projects.py"
  - "assets/projects.svg"
affects:
  - "scripts/generate_projects.py"
  - "tests/test_projects.py"
tech-stack:
  added: []
  patterns:
    - "Standalone SVG generation with ElementTree XML validation"
    - "Entity-safe 2-line plain-text word wrapping before XML escaping"
    - "Font-independent inline Octicon vector paths with ANSI syntax coloring"
    - "Muted zero-count styling (#616e7f) and dashed placeholder slots"
key-files:
  created:
    - "assets/projects.svg"
  modified:
    - "scripts/generate_projects.py"
    - "tests/test_projects.py"
key-decisions:
  - "Dedicated dark terminal SVG window (viewBox 0 0 850 340) matching hero.svg width (D-01, D-02)"
  - "2x2 grid layout of 380x115px project cards at exact integer coordinates (D-03)"
  - "Inline GitHub Octicons with vibrant ANSI accents for non-zero counts and muted #616e7f for zeros (D-11, D-12)"
  - "Plain-text word wrapping and ellipsis truncation before saxutils.escape() to prevent broken entities (D-13)"
requirements-completed:
  - PROJ-01
  - PROJ-03
duration: "4 min"
completed: "2026-11-08T09:27:30Z"
coverage:
  - deliverable: "Standalone terminal SVG generator with ElementTree validation"
    verification:
      kind: "pytest"
      ref: "tests/test_projects.py#test_projects_svg_xml_validity"
      status: "pass"
    human_judgment: false
  - deliverable: "Entity-safe 2-line description word wrapping and clamping"
    verification:
      kind: "pytest"
      ref: "tests/test_projects.py#test_description_clamping_and_escaping"
      status: "pass"
    human_judgment: false
  - deliverable: "Muted zero counts and ANSI accent metrics rendering"
    verification:
      kind: "pytest"
      ref: "tests/test_projects.py#test_zero_count_muted_rendering"
      status: "pass"
    human_judgment: false
  - deliverable: "2x2 grid subpanel coordinates and placeholder slots"
    verification:
      kind: "pytest"
      ref: "tests/test_projects.py#test_subpanel_grid_positions"
      status: "pass"
    human_judgment: false
---

# Phase 03 Plan 02: Terminal Projects SVG Generator & Visual Contract Summary

Implemented the standalone terminal SVG vector graphics generator (`scripts/generate_projects.py`), producing `assets/projects.svg` adhering strictly to the workstation dark terminal visual contract.

## Performance & Metrics
- **Duration:** 4 min
- **Start Time:** 2026-11-08T09:24:00Z
- **End Time:** 2026-11-08T09:27:30Z
- **Tasks Executed:** 3
- **Files Modified / Created:** 3

## Accomplishments
1. **Terminal Window Frame & Chrome (`assets/projects.svg`)**: Created a dedicated `850x340` SVG canvas (`viewBox="0 0 850 340"`) featuring workstation header bar (`#161b22`), macOS traffic lights (`#ff5f56`, `#ffbd2e`, `#27c93f`), window title `projects — zsh`, and CLI command prompt `humam@workstation:~/projects$ gh repo list`.
2. **2x2 Sub-Panel Grid Layout**: Positioned four `380x115px` card subpanels (`#161b22`, border `#30363d`) at exact integer coordinates `(30,80)`, `(440,80)`, `(30,207)`, `(440,207)`. Unfilled slots render with dashed borders (`stroke-dasharray="4,4"`) and centered `[ available slot ]` placeholder text.
3. **Entity-Safe 2-Line Word Wrapping (`wrap_and_clamp_description`)**: Solved entity corruption by performing word splitting and ellipsis truncation on raw unicode text before escaping with `saxutils.escape()`, completely preventing split entities such as `&am...`.
4. **Font-Independent Octicon Glyphs & Muted Zero Counters**: Integrated inline SVG paths for Star, Fork, Issue, and PR Octicons. Implemented semantic telemetry highlighting with ANSI accents for non-zero counts (`#f1e05a`, `#58a6ff`, `#ffa657`, `#a371f7`) and muted gray (`#616e7f`) for inactive/zero counts.
5. **Comprehensive SVG Test Suite**: Extended `tests/test_projects.py` with 6 dedicated test cases validating XML well-formedness, viewBox geometry, window chrome tokens, subpanel grid coordinates, and muted zero rendering.

## Deviations from Plan
None — plan executed exactly as written.

## Self-Check: PASSED
- `scripts/generate_projects.py` exists on disk: YES
- `assets/projects.svg` exists on disk: YES
- `tests/test_projects.py` exists on disk: YES
- Commits found:
  - `664fb28` feat(03-02): implement standalone terminal projects svg generator and render projects.svg
  - `ad09c37` test(03-02): extend test suite for svg geometry, xml integrity, and ui tokens
- Acceptance criteria & pytest suite: 30/30 tests PASS
