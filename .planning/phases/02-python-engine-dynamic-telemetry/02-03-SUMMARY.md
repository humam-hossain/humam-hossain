---
phase: "02"
plan: "03"
subsystem: "hero-svg-pipeline"
tags:
  - svg
  - dom-hooks
  - parameterization
  - idempotency
  - pipeline-integration
requires:
  - "02-02"
provides:
  - scripts/generate_hero.py
  - scripts/update_profile.py
  - assets/hero.svg
  - tests/test_update_profile.py
affects:
  - assets/hero.svg
  - README.md
tech-stack.added: []
patterns:
  - parameterized-svg
  - idempotent-file-writes
  - xml-validation-gate
  - dom-hook-retention
key-files.created: []
key-files.modified:
  - scripts/generate_hero.py
  - scripts/update_profile.py
  - assets/hero.svg
  - tests/test_update_profile.py
key-decisions:
  - "D-09: Parameterized generate_svg() signature preserving defaults and DOM hook IDs (val-uptime, val-loc-add, val-loc-del)"
  - "D-10: Strict ElementTree XML validation before writing SVG to disk"
  - "D-11: Idempotent file write comparing byte equality to prevent git diff churn"
  - "D-12: Clean terminal-styled ANSI logging for complete pipeline execution"
requirements-completed:
  - HERO-04
  - HERO-05
  - AUTO-01
coverage:
  - deliverable: "Parameterized SVG generation with DOM hook retention"
    verification:
      kind: "pytest"
      ref: "tests/test_update_profile.py#test_svg_parameterization_and_dom_hooks"
      status: "pass"
    human_judgment: false
  - deliverable: "Idempotent SVG file writing"
    verification:
      kind: "pytest"
      ref: "tests/test_update_profile.py#test_idempotent_write"
      status: "pass"
    human_judgment: false
  - deliverable: "Full pipeline offline execution"
    verification:
      kind: "pytest"
      ref: "tests/test_update_profile.py#test_full_pipeline_offline_execution"
      status: "pass"
    human_judgment: false
  - deliverable: "Refreshed hero.svg with live dynamic coding uptime and LOC metrics"
    verification:
      kind: "pytest"
      ref: "tests/test_tokens.py#test_hero_svg_generation"
      status: "pass"
    human_judgment: false
duration: "4 min"
completed: "2026-11-07"
---

# Phase 02 Plan 03: Parameterized SVG Re-rendering & Idempotent Update Integration Summary

## Executive Summary

Integrated dynamic telemetry calculation directly into the vector card generation pipeline, rendering live coding uptime and aggregate lines of code (LOC) into `assets/hero.svg`. Updated `scripts/generate_hero.py` to accept optional parameters (`uptime`, `loc_add`, `loc_del`) while preserving default workstation fallback tokens and all Phase 1 DOM hooks (`val-uptime`, `val-loc-add`, `val-loc-del`) per Requirements HERO-04 and HERO-05. Implemented strict `xml.etree.ElementTree` validation to prevent XML corruption and idempotent file writing in `scripts/update_profile.py` to prevent unnecessary git diff churn per Requirement AUTO-01.

## Accomplishments

- **Parameterized SVG Generator**: Updated `generate_svg()` signature in `scripts/generate_hero.py` with default fallback parameters, XML escaping via `xml.sax.saxutils.escape()`, and pre-validation via `ET.fromstring()`.
- **DOM Hook Retention**: Preserved exact DOM IDs (`val-uptime`, `val-loc-add`, `val-loc-del`) and viewBox geometry (`0 0 850 380`), ensuring complete backward compatibility with Phase 1 tests.
- **Idempotent File Writing**: Implemented `write_svg_idempotent()` which skips disk writes if the new content is byte-identical to `assets/hero.svg`.
- **Full Pipeline Orchestration**: Wired credential resolution, cache management, uptime calculation, LOC aggregation, SVG rendering, and idempotent saving in `main()` of `scripts/update_profile.py`.
- **End-to-End Verification**: Added 3 new tests in `tests/test_update_profile.py` (`test_svg_parameterization_and_dom_hooks`, `test_idempotent_write`, `test_full_pipeline_offline_execution`) with 100% test pass rate across all 18 test cases.

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

- `python3 scripts/update_profile.py`: Successfully refreshed `assets/hero.svg` and triggered idempotent skip on rerun.
- `pytest tests/test_tokens.py -v`: 5/5 passed.
- `pytest tests/test_update_profile.py -v`: 13/13 passed.
- `pytest tests/ -v`: 18/18 passed in 0.03s.

## Self-Check: PASSED
