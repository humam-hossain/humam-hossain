---
phase: "02"
plan: "02"
subsystem: "telemetry-metrics"
tags:
  - uptime
  - loc-counter
  - calendar-math
  - incremental-cache
  - neofetch
requires:
  - "02-01"
provides:
  - config/terminal_theme.json
  - data/cache.json
  - scripts/update_profile.py
  - tests/test_update_profile.py
affects:
  - scripts/generate_hero.py
  - assets/hero.svg
tech-stack.added: []
patterns:
  - calendar-accurate-math
  - incremental-caching
  - repo-filtering
  - batch-safe-graphql
key-files.created:
  - data/cache.json
key-files.modified:
  - config/terminal_theme.json
  - scripts/update_profile.py
  - tests/test_update_profile.py
key-decisions:
  - "D-01: Baseline discovery precedence (override > cache > GraphQL fallback > default)"
  - "D-03: Calendar-accurate date difference in strict UTC mirroring relativedelta"
  - "D-04: Neofetch uptime format with intelligent pluralization and fixed 3-unit layout"
  - "D-06: Configurable exclude_repos in config/terminal_theme.json"
  - "D-07: Incremental caching comparing pushedAt in data/cache.json to skip unchanged repos"
  - "D-08: Thousands comma formatting for additions and deletions"
requirements-completed:
  - HERO-04
  - HERO-05
coverage:
  - deliverable: "Calendar-accurate coding uptime calculation and Neofetch formatting"
    verification:
      kind: "pytest"
      ref: "tests/test_update_profile.py#test_calendar_uptime_math"
      status: "pass"
    human_judgment: false
  - deliverable: "Baseline start date discovery and override hierarchy"
    verification:
      kind: "pytest"
      ref: "tests/test_update_profile.py#test_baseline_discovery_precedence"
      status: "pass"
    human_judgment: false
  - deliverable: "LOC thousands comma formatting"
    verification:
      kind: "pytest"
      ref: "tests/test_update_profile.py#test_loc_formatting"
      status: "pass"
    human_judgment: false
  - deliverable: "Incremental cache lifecycle and pushedAt skip"
    verification:
      kind: "pytest"
      ref: "tests/test_update_profile.py#test_incremental_cache_hit_skip"
      status: "pass"
    human_judgment: false
  - deliverable: "Configurable exclude_repos filtering"
    verification:
      kind: "pytest"
      ref: "tests/test_update_profile.py#test_exclude_repos_filtering"
      status: "pass"
    human_judgment: false
duration: "4 min"
completed: "2026-11-07"
---

# Phase 02 Plan 02: Coding Uptime Engine & Incremental LOC Aggregator Summary

## Executive Summary

Implemented dynamic metric calculations for Muhammed Humam Hossain's terminal profile: calendar-accurate coding uptime and incremental lines of code (LOC) aggregation. Coding uptime calculates elapsed duration in strict UTC using standard library calendar mathematics that mirrors `dateutil.relativedelta` across month boundaries and leap years, formatted to Neofetch conventions (`X yrs, Y mos, Z days`) with stable 3-unit layout per Requirement HERO-04. The LOC aggregator enumerates owned public non-fork repositories with commit history batching ($\le 50$) and incremental caching in `data/cache.json` indexed by `pushedAt` to bypass redundant queries per Requirement HERO-05. Introduced repository exclusion configuration in `config/terminal_theme.json`.

## Accomplishments

- **Calendar-Accurate Uptime Engine**: Implemented `compute_calendar_diff()` and `_add_calendar_months()` in `scripts/update_profile.py` verifying leap year clamping (`2024-02-29` -> `2025-02-28`), month boundaries (`2020-01-31` -> `2020-02-29`), and pluralization (`1 yr, 1 mo, 1 day`).
- **Baseline Discovery Hierarchy**: Built `get_baseline_date()` resolving config override > cache > GraphQL earliest commit discovery > account creation date > default fallback.
- **Incremental LOC Aggregator**: Implemented `aggregate_loc()` comparing repository `pushedAt` timestamps against `data/cache.json` cache entries, querying commits in batches of 50 only on cache misses, and honoring `exclude_repos`.
- **Formatting Utilities**: Implemented `format_loc_counts()` formatting LOC numbers with thousands commas (`++320,410 / --85,240`).
- **Persistent Telemetry Cache**: Created `data/cache.json` tracking baseline commit timestamp and per-repository metrics.
- **Offline Unit Test Suite**: Added 6 new unit tests in `tests/test_update_profile.py` covering calendar math, baseline precedence, LOC formatting, cache lifecycle, incremental hit skipping, and exclusion filtering.

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

- `pytest tests/test_update_profile.py -v`: 10 passed in 0.04s
- `pytest tests/ -v`: 15 passed in 0.11s
- `python3 scripts/update_profile.py`: Successfully displays uptime and LOC in terminal style

## Self-Check: PASSED
