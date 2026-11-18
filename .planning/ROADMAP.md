# Roadmap: Milestone v2.0 Andrew6rant-Style Neofetch Redesign

## Overview

Overhaul the profile repository to adhere to Andrew6rant's proven, single-card Neofetch terminal architecture with native dual-theme support, user-driven configuration, and real GitHub telemetry.

## Phases

- [x] **Phase 7: User Configuration & Project Selection** - Create `profile_config.json` enabling the user to specify custom featured projects, skills, system info, and contacts. (completed 2026-11-18)
- [x] **Phase 8: Dual-Theme Neofetch SVG Engine** - Implement pure vector SVG builder generating `dark_mode.svg` and `light_mode.svg` matching Andrew6rant's clean layout without window chrome. (completed 2026-11-18)
- [x] **Phase 9: Real GitHub GraphQL Telemetry** - Wire live GitHub stats (commits, LOC ++/--, stars, repos, uptime) with dot-leader justification. (completed 2026-11-18)
- [x] **Phase 10: README Consolidation & Purge** - Simplify `README.md` to a single `<picture>` tag and remove visitor hit counters, fake commits, and fake articles. (completed 2026-11-18)
- [x] **Phase 11: GitHub Actions Automation & Verification** - Ensure scheduled workflow runs daily with zero cost, commits updated SVGs, and verified end-to-end. (completed 2026-11-18)

## Phase Details

### Phase 7: User Configuration & Project Selection

**Goal:** Establish `profile_config.json` as the single source of truth for all profile content, allowing the user to pick exact featured projects, skills, system telemetry, and contact methods.
**Requirements:** CONF-01, CONF-02
**Success Criteria:**
1. `profile_config.json` exists with intuitive schema for system telemetry, categorized skills, featured projects, and contact info. ✓
2. A verification parser validates the config format and provides sensible defaults. ✓

### Phase 8: Dual-Theme Neofetch SVG Engine

**Goal:** Generate `dark_mode.svg` and `light_mode.svg` strictly following Andrew6rant's design specifications.
**Requirements:** NEO-01, NEO-02
**Success Criteria:**
1. Zero macOS window chrome (no traffic light dots, no fake window title bars). ✓
2. Monospace typography with ASCII art on the left and dot-leader aligned rows on the right. ✓
3. `dark_mode.svg` uses GitHub dark palette (`#161b22`, amber keys, cyan values). ✓
4. `light_mode.svg` uses GitHub light palette (`#f6f8fa`, dark text, rust-brown keys, navy values). ✓
5. Both SVGs render crisply across devices. ✓

### Phase 9: Real GitHub GraphQL Telemetry

**Goal:** Integrate authentic GitHub statistics and dynamic uptime calculation with dot-justified layout preservation.
**Requirements:** STAT-01, STAT-02
**Success Criteria:**
1. Queries GitHub GraphQL API for authentic repo counts, stars, commits, followers, and lines of code (additions `++` and deletions `--`). ✓
2. Calculates coding uptime dynamically from user's creation/first-commit date. ✓
3. Dynamically updates SVG text nodes and adjusts dot leaders so column alignment is strictly maintained regardless of number digit length. ✓

### Phase 10: README Consolidation & Purge

**Goal:** Clean `README.md` down to a single `<picture>` block and remove all obsolete cards, shields, and fake logs.
**Requirements:** DOC-01, DOC-02
**Success Criteria:**
1. `README.md` contains only the native `<picture>` block linking `dark_mode.svg` and `light_mode.svg`. ✓
2. Removal of the `komarev` visitor counter badge that counts self-hits. ✓
3. Removal of fake git log graph and fake article log. ✓
4. Old fragmented SVGs (`hero.svg`, `projects.svg`, `metrics.svg`, `skills.svg`) retired. ✓

### Phase 11: GitHub Actions Automation & Verification

**Goal:** Update the daily GitHub Actions workflow to run the new pipeline and verify end-to-end execution.
**Requirements:** AUTO-01
**Success Criteria:**
1. `.github/workflows/profile-updater.yml` executes the build script and pushes SVG updates on main. ✓
2. End-to-end test run passes locally with zero errors. ✓

## Progress

| Phase | Status | Completed |
|-------|--------|-----------|
| 7. User Configuration & Project Selection | Complete | 2026-11-18 |
| 8. Dual-Theme Neofetch SVG Engine | Complete | 2026-11-18 |
| 9. Real GitHub GraphQL Telemetry | Complete | 2026-11-18 |
| 10. README Consolidation & Purge | Complete | 2026-11-18 |
| 11. GitHub Actions Automation & Verification | Complete | 2026-11-18 |
