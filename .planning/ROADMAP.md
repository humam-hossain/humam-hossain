# Roadmap: Terminal-Themed GitHub Profile README

## Overview

Build a fully automated, self-updating GitHub Profile README for `humam-hossain` in vertical MVP slices. Each phase delivers a visible, working addition to the profile — starting with the core Hero terminal card, then layering on dynamic metrics, project dashboards, activity feeds, and finally the daily automation pipeline. By the end, the profile is a living terminal dashboard that refreshes itself every day via GitHub Actions at zero cost.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: Hero Terminal Card & Design System** - Static dual-theme SVG hero with ASCII monogram and system telemetry (completed 2026-11-07)
- [x] **Phase 2: Python Engine & Dynamic Telemetry** - Build the update script with coding uptime and LOC calculations (completed 2026-11-07)
- [x] **Phase 3: Open Source Projects Dashboard** - Live repo metrics table with configurable project selection (completed 2026-11-08)
- [ ] **Phase 4: Languages, Streaks & Metrics** - Top languages bar, streak stats, visitor counter, git activity stream
- [ ] **Phase 5: Skills Matrix & Blog Section** - Terminal-themed skills grid and plug-and-play blog/RSS slot
- [ ] **Phase 6: GitHub Actions Automation** - Daily scheduled workflow tying everything together

## Phase Details

### Phase 1: Hero Terminal Card & Design System

**Goal**: Deliver a static dark-theme SVG terminal hero card visible on the GitHub profile with `H_` ASCII block monogram, system telemetry, and the terminal design token system that all future phases inherit.
**Mode:** mvp
**Depends on**: Nothing (first phase)
**Requirements**: HERO-01, HERO-02, HERO-03
**Success Criteria** (what must be TRUE):

  1. Visiting `github.com/humam-hossain` displays a terminal-styled SVG hero card with `H_` ASCII block monogram on the left and `humam@workstation` system telemetry on the right
  2. The card renders as an authentic dark Unix terminal window with macOS traffic lights, 8-dot ANSI diagnostic strip, and crisp monospace typography
  3. All visual elements use the defined terminal design tokens (background `#161b22`/`#0d1117`, monospace font stack, ANSI amber/cyan/green/red colors)
  4. README.md embeds the dark hero SVG directly at the top with terminal contact badges, phase expansion anchors, and a terminal exit prompt

**Plans**: 3/3 plans executed

Plans:

- [x] 01-01-PLAN.md
- [x] 01-02-PLAN.md
- [x] 01-03-PLAN.md

**Wave 1**

- [x] 01-01: Define terminal design tokens (config/terminal_theme.json), test infrastructure (tests/test_tokens.py), and design specification (docs/DESIGN_SYSTEM.md)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 01-02: Build Python SVG generator engine (scripts/generate_hero.py) and generate dark terminal hero card (assets/hero.svg) with H_ block monogram and telemetry

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 01-03: Structure profile README.md with centered hero SVG, terminal contact badges, phase extension anchors, and exit prompt

### Phase 2: Python Engine & Dynamic Telemetry

**Goal**: Build the Python update script that queries GitHub GraphQL API for live data and patches the hero SVGs with dynamic coding uptime and lines of code counters.
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: HERO-04, HERO-05, AUTO-01
**Success Criteria** (what must be TRUE):

  1. Running `python scripts/update_profile.py` locally calculates coding uptime from user's first GitHub commit to present and injects the result into both SVGs
  2. The script calculates total LOC (additions `++` and deletions `--`) across all public repositories and injects formatted counters into the SVGs
  3. The script handles GitHub API rate limits gracefully and uses `GITHUB_TOKEN` or fine-grained PAT authentication
  4. SVGs remain valid XML after patching and render correctly on the profile

**Plans**: 3/3 plans executed

Plans:

- [x] 02-01-PLAN.md
- [x] 02-02-PLAN.md
- [x] 02-03-PLAN.md

**Wave 1**

- [x] 02-01: Scaffold `scripts/update_profile.py` with GitHub GraphQL API client, authentication, and rate-limit handling

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 02-02: Implement coding uptime calculation (first commit date → now) and LOC aggregation across all repos

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 02-03: Implement SVG patching logic to inject dynamic values into `dark_mode.svg` and `light_mode.svg`

### Phase 3: Open Source Projects Dashboard

**Goal**: Add a live open-source projects dashboard section below the hero card showing real-time Stars, Forks, Issues, and PR counts in a terminal-box format.
**Mode:** mvp
**Depends on**: Phase 2
**Requirements**: PROJ-01, PROJ-02, PROJ-03
**Success Criteria** (what must be TRUE):

  1. The README displays a terminal-styled table or SVG card listing featured repositories with live ⭐ Stars, 🍴 Forks, 🛎️ Issues, and 📬 Pull Requests counts
  2. A `config.json` or similar file allows the user to specify which repositories to feature, with automatic fallback to top-starred public repos
  3. The dashboard section strictly matches the terminal design system (monospace, dark background, ANSI colors, box-drawing characters)
  4. The Python update script fetches and injects fresh project metrics on each run

**Plans**: 3/3 plans executed

Plans:

- [x] 03-01-PLAN.md
- [x] 03-02-PLAN.md
- [x] 03-03-PLAN.md

**Wave 1**

- [x] 03-01: Add GitHub GraphQL queries for repository metrics (stars, forks, issues, PRs) with configurable repo list

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 03-02: Generate terminal-box styled project dashboard (SVG or markdown table with shields.io terminal badges)

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 03-03: Integrate dashboard generation into `update_profile.py` and inject into README.md

### Phase 4: Languages, Streaks & Metrics

**Goal**: Add top languages breakdown, commit streak stats, retro visitor counter, and recent git activity stream — all in terminal style.
**Mode:** mvp
**Depends on**: Phase 3
**Requirements**: METRIC-01, METRIC-02, METRIC-03, METRIC-04
**Success Criteria** (what must be TRUE):

  1. Top languages are displayed as a terminal-styled horizontal progress bar (e.g., `Python [████████░░] 52%`) calculated from the user's public repositories
  2. Commit streak and contribution stats are displayed in a terminal-themed card matching the profile palette
  3. A retro terminal visitor counter badge is visible on the profile
  4. Recent git activity (last 5-10 commits/PRs) is displayed formatted as `git log --graph --oneline`

**Plans**: 4 plans

Plans:
**Wave 1**

- [ ] 04-01: Implement top languages calculation and terminal progress bar rendering

**Wave 2** *(blocked on Wave 1 completion)*

- [ ] 04-02: Integrate or generate terminal-themed commit streak stats card

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 04-03: Add retro terminal visitor counter badge

**Wave 4** *(blocked on Wave 3 completion)*

- [ ] 04-04: Implement recent git activity stream (`git log` style) via GitHub API

### Phase 5: Skills Matrix & Blog Section

**Goal**: Add a terminal-themed categorized skills grid and a plug-and-play blog/article section that activates when RSS or markdown links are configured.
**Mode:** mvp
**Depends on**: Phase 4
**Requirements**: CONTENT-01, CONTENT-02
**Success Criteria** (what must be TRUE):

  1. A categorized skills matrix is visible on the profile in terminal style (AI & Data Science, Backend & Systems, SQA & Automation, Embedded/IoT)
  2. A blog/article section is present that can be populated via RSS feed URL or manual markdown entries
  3. Both sections adhere strictly to the terminal design system

**Plans**: 2 plans

Plans:

- [ ] 05-01: Build terminal-themed skills matrix section (categorized, icon-mapped)
- [ ] 05-02: Build plug-and-play blog/RSS section with terminal formatting

### Phase 6: GitHub Actions Automation

**Goal**: Wire everything into a scheduled GitHub Actions workflow that runs the Python engine daily, commits updated SVGs and README, and costs $0.
**Mode:** mvp
**Depends on**: Phase 5
**Requirements**: AUTO-02, AUTO-03
**Success Criteria** (what must be TRUE):

  1. `.github/workflows/profile-updater.yml` exists and runs on a daily cron schedule plus manual `workflow_dispatch` trigger
  2. The workflow executes `update_profile.py`, commits any changed files, and pushes to `main`
  3. The workflow uses only the standard `GITHUB_TOKEN` (or configured PAT) with no paid services
  4. The profile visibly updates within 24 hours of any GitHub activity change

**Plans**: 2 plans

Plans:

- [ ] 06-01: Create `.github/workflows/profile-updater.yml` with cron schedule, checkout, Python setup, and commit/push steps
- [ ] 06-02: End-to-end integration test — trigger workflow manually, verify profile updates, validate SVG rendering

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Hero Terminal Card & Design System | 3/3 | Complete    | 2026-11-07 |
| 2. Python Engine & Dynamic Telemetry | 3/3 | Complete    | 2026-11-07 |
| 3. Open Source Projects Dashboard | 3/3 | Complete    | 2026-11-08 |
| 4. Languages, Streaks & Metrics | 0/4 | Not started | - |
| 5. Skills Matrix & Blog Section | 0/2 | Not started | - |
| 6. GitHub Actions Automation | 0/2 | Not started | - |
