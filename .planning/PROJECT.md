# Terminal-Themed GitHub Profile README (humam-hossain)

## What This Is

An automated, self-updating GitHub Profile README for Muhammed Humam Hossain (`humam-hossain`) strictly adhering to Andrew Grant's ([Andrew6rant](https://github.com/Andrew6rant/Andrew6rant)) authentic Unix `neofetch` terminal architecture. Powered by scheduled GitHub Actions, the profile renders an authentic single-card Neofetch terminal via GitHub's native `<picture>` element with dual-theme (`dark_mode.svg` & `light_mode.svg`) support, real-time GitHub telemetry (commits, LOC, stars, repos), user-configured featured projects, categorized skills, and verified contact links.

## Core Value

Faithfully deliver Andrew6rant's clean Neofetch terminal aesthetic—zero macOS window chrome / traffic lights, native `<picture>` dark/light theme switching with zero contrast issues, full user control over featured projects and skills via `profile_config.json`, and real GitHub telemetry dynamically refreshed via free GitHub Actions.

## Current Milestone: v2.0 Andrew6rant-Style Neofetch Redesign

**Goal:** Overhaul the profile from the fragmented multi-card macOS window mockup into a faithful, authentic Andrew6rant Neofetch dual-theme architecture.

**Target features:**
- User configuration file (`profile_config.json`) to directly control featured projects, skills, contact info, and bio telemetry
- Dual-theme Neofetch SVGs (`dark_mode.svg` and `light_mode.svg`) with ASCII art monogram, dot-leader alignment, clean section dividers, and zero macOS traffic light chrome
- Live GitHub stats engine fetching real commit counts, lines of code (`++`/`--`), stars, repositories, and coding uptime
- Minimalist `README.md` using native `<picture>` media query, eliminating badge clutter, fake git commits, fake article logs, and visitor counters
- Automated GitHub Actions profile updater keeping both SVGs fresh daily at zero cost

## Requirements

### Validated

- ✓ Modular LaTeX CV generation pipeline with automated compilation scripts — existing (`cv/`)
- ✓ Next.js static portfolio foundation and component assets — existing (`src/`, `public/`)
- ✓ Initial GitHub Actions workflow architecture — Milestone v1.0

### Active

- [ ] **V2-01**: User configuration file (`profile_config.json`) defining customizable projects, skills, bio info, and contact links
- [ ] **V2-02**: Pure SVG Neofetch generator producing `dark_mode.svg` (`#161b22`) and `light_mode.svg` (`#f6f8fa`) with ASCII art and dot-leader alignment
- [ ] **V2-03**: Live GitHub GraphQL telemetry fetching authentic commits, LOC additions/deletions, stars, repos, and uptime
- [ ] **V2-04**: Simplified `README.md` containing only the native `<picture>` block, removing macOS chrome, badges, and fake logs
- [ ] **V2-05**: GitHub Actions workflow running daily to regenerate and commit both SVGs

### Out of Scope

- macOS traffic lights (red/yellow/green dots) and faux window chrome
- Fragmented multi-card SVG layout (multiple separate SVG boxes)
- Third-party visitor hit counters (like Komarev) that count the owner's own visits
- Hardcoded fake git commit hashes or fake article logs
- GitHub Trophy badges or graphical badges with non-terminal styling

## Context

- **Repository Role:** `humam-hossain/humam-hossain` is the special repository used by GitHub to render the user's public profile overview.
- **Reference Model:** Andrew Grant's ([Andrew6rant](https://github.com/Andrew6rant/Andrew6rant)) profile README.
- **Developer Background:** Muhammed Humam Hossain — Systems, SQA, Linux Administrator, AI & Robotics engineer.
- **Theme Palette:**
  - Dark: background `#161b22`, text `#c9d1d9`, keys `#ffa657`, values `#a5d6ff`, additions `#3fb950`, deletions `#f85149`, dots `#616e7f`
  - Light: background `#f6f8fa`, text `#24292f`, keys `#953800`, values `#0a3069`, additions `#1a7f37`, deletions `#cf222e`, dots `#c2cfde`

## Constraints

- **Single Embed Pattern:** Profile README must embed only the `<picture>` tag switching between `dark_mode.svg` and `light_mode.svg`.
- **Zero Cost:** $0.00 infrastructure cost — GitHub Actions free runner tier with default `GITHUB_TOKEN`.
- **Configurability:** User can edit `profile_config.json` at any time to reorder or change displayed projects, skills, and bio lines without touching code.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Andrew6rant Architecture | Eliminates all contrast/theme issues between GitHub light and dark modes and removes gaudy window chrome | Adopted in v2.0 |
| Single Config File | Gives user total ownership over featured projects and skills | Adopted in v2.0 (`profile_config.json`) |
| Real GitHub Metrics | Replaces fabricated/mocked commit and article data with genuine GraphQL telemetry | Adopted in v2.0 |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-11-18 for Milestone v2.0*
