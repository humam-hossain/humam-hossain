# Requirements: Milestone v2.0 Andrew6rant-Style Neofetch Redesign

## Overview

Overhaul the profile repository to adhere to Andrew6rant's proven, single-card Neofetch terminal architecture with native dual-theme support, user-driven configuration, and real GitHub telemetry.

## Requirements

### Configuration & Data Control

- [ ] **CONF-01**: User configuration file `profile_config.json` created with clear schema for:
  - System info (`os`, `uptime_mode`, `host`, `kernel`, `ide`)
  - Categorized skills (`Languages.Code`, `Languages.Tools`, etc.)
  - Featured projects list with user-specified project names, descriptions, and metrics
  - Contact links (`Email`, `LinkedIn`, `Portfolio`)
  - Telemetry overrides and display toggles
- [ ] **CONF-02**: Python script `scripts/build_profile.py` that reads `profile_config.json` and compiles both theme SVGs cleanly.

### Dual-Theme Neofetch Vector Engine

- [ ] **NEO-01**: `dark_mode.svg` generated matching Andrew6rant's exact dimensions, typography (`Consolas`, monospace), and color palette:
  - Background `#161b22`, border radius `15px`
  - Zero traffic lights / window chrome
  - Left column: crisp monospace ASCII art monogram / terminal art
  - Right column: `humam@workstation` header line, dot-leader aligned key-values (`. Key: ........ Value`)
  - Section dividers (`- Section -————————————————————`)
  - Key fill `#ffa657`, value fill `#a5d6ff`, dot fill `#616e7f`
- [ ] **NEO-02**: `light_mode.svg` generated matching GitHub light theme:
  - Background `#f6f8fa`, border radius `15px`
  - Zero traffic lights / window chrome
  - Left column: matching ASCII art in dark text `#24292f`
  - Right column: matching dot-leader layout
  - Key fill `#953800`, value fill `#0a3069`, dot fill `#c2cfde`, text `#24292f`

### Dynamic Telemetry & Live Stats

- [ ] **STAT-01**: GitHub GraphQL integration to query live statistics:
  - Total public repositories and contributed repositories
  - Total stars accumulated across user repositories
  - Total commits
  - Total followers
  - Total lines of code additions `++` and deletions `--`
  - Dynamic uptime calculation
- [ ] **STAT-02**: Dynamic injection into SVG text nodes with automatic dot-leader justification (preserving fixed character width across varying number lengths).

### README & Clean Up

- [ ] **DOC-01**: `README.md` simplified to a single `<picture>` block with `(prefers-color-scheme: dark)` pointing to `dark_mode.svg` and `light_mode.svg`, linked to the user's profile.
- [ ] **DOC-02**: Completely remove all fake commit graphs, fake article logs, visitor counters, and fragmented SVG cards.

### CI/CD Automation

- [ ] **AUTO-01**: GitHub Actions workflow `.github/workflows/profile-updater.yml` updated to execute `scripts/build_profile.py` daily and commit updated SVGs and README when stats change.

## Out of Scope

- Faux macOS title bars and traffic light buttons
- Multiple SVG cards
- Third-party hit counters (like Komarev)
- Fabricated commit or article feeds

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CONF-01 | Phase 7 | Pending |
| CONF-02 | Phase 7 | Pending |
| NEO-01 | Phase 8 | Pending |
| NEO-02 | Phase 8 | Pending |
| STAT-01 | Phase 9 | Pending |
| STAT-02 | Phase 9 | Pending |
| DOC-01 | Phase 10 | Pending |
| DOC-02 | Phase 10 | Pending |
| AUTO-01 | Phase 11 | Pending |
