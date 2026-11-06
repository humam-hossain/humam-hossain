# Terminal-Themed GitHub Profile README (humam-hossain)

## What This Is

An automated, self-updating GitHub Profile README for Muhammed Humam Hossain (`humam-hossain`) that emulates a sleek, authentic Unix terminal / Neofetch interface. Powered by scheduled GitHub Actions, the profile delivers real-time repository metrics, commit uptime telemetry, dynamic lines-of-code tracking, top language distribution, and open-source project dashboards—all unified under a strict dark terminal aesthetic.

## Core Value

Every single profile component must strictly adhere to the same unified terminal design language (dark terminal background, monospace typography, terminal box borders, ANSI syntax colors) while keeping all live metrics automatically refreshed via free GitHub Actions.

## Requirements

### Validated

- ✓ Modular LaTeX CV generation pipeline with automated compilation scripts — existing (`cv/`)
- ✓ Next.js static portfolio foundation and component assets — existing (`src/`, `public/`)

### Active

- [ ] Dual-theme SVG terminal Hero Card with `H-` / `HH` stylized ASCII monogram on the left and `humam@workstation` telemetry on the right
- [ ] Automated "Coding Uptime" calculation derived from timestamp of first GitHub commit to present
- [ ] Dynamic Lines of Code (LOC) counter tracking aggregate repository additions (`++`) and deletions (`--`)
- [ ] Live Open Source Projects Dashboard displaying real-time Stars, Forks, Issues, and PR counts in a terminal box format
- [ ] Configurable repository selection for featured projects with automatic fallback to top active repos
- [ ] Top Languages distribution widget formatted as an ASCII/terminal horizontal progress bar
- [ ] Commit Streak and Contribution Stats card customized strictly to match terminal palette (`#161b22`, amber, green)
- [ ] Retro terminal session hits / visitor counter badge
- [ ] Recent Git activity stream formatted as `git log --graph --oneline`
- [ ] Plug-and-play blog post / publication section driven by RSS/markdown automation
- [ ] Scheduled GitHub Actions workflow (`.github/workflows/profile-updater.yml`) running daily with zero cost on GitHub's free public runner tier

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
| Strict Terminal Design System | Prevents disjointed appearance typical of profiles mixing random third-party cards; enforces cohesive professional identity | — Pending |
| First-Commit Coding Uptime | Personalizes uptime telemetry to reflect real GitHub engineering history rather than arbitrary biological age | — Pending |
| Dual SVG + GitHub Actions Architecture | Ensures fast profile load times without client-side lag or rate limits, while maintaining automated daily freshness | — Pending |
| Pinned + Dynamic Project Metrics | Allows highlighting key competition/portfolio repos while keeping live star, fork, issue, and PR stats accurate | — Pending |
| Exclude GitHub Trophies | User explicitly specified no trophies to maintain clean, technical minimalism | — Pending |

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
*Last updated: 2026-11-06 after initialization*
