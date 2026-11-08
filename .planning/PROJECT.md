# Terminal-Themed GitHub Profile README (humam-hossain)

## What This Is

An automated, self-updating GitHub Profile README for Muhammed Humam Hossain (`humam-hossain`) that emulates a sleek, authentic Unix terminal / Neofetch interface. Powered by scheduled GitHub Actions, the profile delivers real-time repository metrics, commit uptime telemetry, dynamic lines-of-code tracking, top language distribution, and open-source project dashboards—all unified under a strict dark terminal aesthetic.

## Core Value

Every single profile component must strictly adhere to the same unified terminal design language (dark terminal background, monospace typography, terminal box borders, ANSI syntax colors) while keeping all live metrics automatically refreshed via free GitHub Actions.

## Requirements

### Validated

- ✓ Modular LaTeX CV generation pipeline with automated compilation scripts — existing (`cv/`)
- ✓ Next.js static portfolio foundation and component assets — existing (`src/`, `public/`)
- ✓ SVG terminal Hero Card with `H_` stylized ASCII monogram, 8-dot ANSI strip, `humam@workstation` telemetry, and Shields.io terminal contact badges — Phase 1
- ✓ Automated "Coding Uptime" calculation from first commit and aggregate Lines of Code (LOC) counter — Phase 2
- ✓ Live Open Source Projects Dashboard displaying real-time Stars, Forks, Issues, and PR counts with configurable repo selection — Phase 3
- ✓ Top Languages distribution widget formatted as horizontal vector tracks — Phase 4
- ✓ Commit Streak & Contribution Stats card customized strictly to match terminal palette — Phase 4
- ✓ Retro terminal session hits / visitor counter badge — Phase 4
- ✓ Recent Git activity stream formatted as `git log --graph --oneline` with automated bot filtering — Phase 4
- ✓ Terminal-themed categorized skills matrix (AI & Data Science, Backend & Systems, SQA & Automation, Embedded & Robotics) with flow-pack pills — Phase 5
- ✓ Plug-and-play blog / article section (`cat ~/articles.log`) with RSS 2.0 / Atom 1.0 parsing, 12h caching, and fallback cascade — Phase 5

### Active

- [ ] Scheduled GitHub Actions workflow (`.github/workflows/profile-updater.yml`) running daily with zero cost on GitHub's free public runner tier (Phase 6)
- [ ] Automated git commit and push step within the workflow running under standard `GITHUB_TOKEN` permissions with zero hosting cost (Phase 6)

### Out of Scope

- GitHub Trophy badges — explicitly rejected by user ("I don't think we're gonna add trophy there")
- Mismatched graphical third-party badges (bright gradients, pastel cards) — violates strict terminal design rule
- Paid cloud functions or external hosting — all updates must execute free of charge using native GitHub Actions

## Context

- **Repository Role:** `humam-hossain/humam-hossain` is the special repository used by GitHub to render the user's public profile overview.
- **Reference Model:** Inspired by Andrew Grant's ([Andrew6rant](https://github.com/Andrew6rant/Andrew6rant)) terminal profile, but tailored with custom typography, coding uptime calculation, live project PR/issue counters, and curated system telemetry.
- **Developer Background:** Muhammed Humam Hossain — Systems, SQA, Linux Homeserver/VPS administrator, AI & Robotics engineer (KRPC competition, autonomous rover, IoT environmental quality control).
- **Existing Assets:** Pre-mapped codebase contains authentic CV project descriptions (`cv/sections/`) that can seed the featured project highlights.

## Constraints

- **Design Consistency**: Every visual element must match the terminal aesthetic: background `#161b22`/`#0d1117`, monospace fonts (`Consolas`, `Fira Code`), ANSI colors (Amber `#ffa657`, Cyan `#a5d6ff`, Green `#3fb950`, Red `#f85149`, Muted `#616e7f`).
- **Cost**: $0.00 infrastructure cost — must leverage GitHub Actions free unlimited tier for public repositories.
- **Authentication**: Python scripts querying GitHub GraphQL API must utilize the default `GITHUB_TOKEN` provided by the workflow runner or a fine-grained PAT.
- **Theme Support**: Hero SVGs should support both dark and light modes via GitHub's native `<picture>` media queries.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Strict Terminal Design System | Prevents disjointed appearance typical of profiles mixing random third-party cards; enforces cohesive professional identity | ✓ Shipped in Phase 1 (config/terminal_theme.json, docs/DESIGN_SYSTEM.md) |
| Deterministic Standard Library Generator | Pure Python stdlib (xml.sax, xml.etree) guarantees zero external dependencies and fast GitHub Actions runtime | ✓ Shipped in Phase 1 (scripts/generate_hero.py) |
| First-Commit Coding Uptime | Personalizes uptime telemetry to reflect real GitHub engineering history rather than arbitrary biological age | ✓ Shipped in Phase 2 (scripts/update_profile.py) |
| Dual SVG + GitHub Actions Architecture | Ensures fast profile load times without client-side lag or rate limits, while maintaining automated daily freshness | ✓ Shipped in Phase 1-5, automation in Phase 6 |
| Pinned + Dynamic Project Metrics | Allows highlighting key competition/portfolio repos while keeping live star, fork, issue, and PR stats accurate | ✓ Shipped in Phase 3 (assets/projects.svg) |
| Exclude GitHub Trophies | User explicitly specified no trophies to maintain clean, technical minimalism | ✓ Enforced |
| Flow-Pack Monospace Skills Layout | monospaced width math (`32 + len * 6.8`) with 6-skill capacity cap guarantees zero boundary overflow | ✓ Shipped in Phase 5 (assets/skills.svg) |
| Multi-Layer Article Fallback Cascade | Live feed -> Cache (12h TTL) -> Curated articles -> Standby message guarantees zero CI failure risk | ✓ Shipped in Phase 5 (scripts/update_profile.py) |

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
*Last updated: 2026-11-09 after Phase 5*
