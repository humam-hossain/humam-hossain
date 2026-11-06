# Requirements: Terminal-Themed GitHub Profile README (humam-hossain)

**Defined:** 2026-11-06
**Core Value:** Every single profile component must strictly adhere to the same unified terminal design language (dark terminal background, monospace typography, terminal box borders, ANSI syntax colors) while keeping all live metrics automatically refreshed via free GitHub Actions.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Hero & Identity (HERO)

- [ ] **HERO-01**: Dual-theme SVG Hero card with stylized block monogram ASCII typography (`H-` / `HH`) on the left panel
- [ ] **HERO-02**: Terminal telemetry on the right panel (`humam@workstation`, OS: `Arch Linux`, Kernel: `Systems | AI & Robotics`, Focus: `Autonomous Systems & Backend`, Contact: email & LinkedIn)
- [ ] **HERO-03**: Dual theme support via `<picture>` and `(prefers-color-scheme: dark)` for seamless GitHub dark/light mode switching
- [ ] **HERO-04**: Dynamic "Coding Uptime" calculation evaluating elapsed duration (`X yrs, Y mos, Z days`) from first GitHub commit to present
- [ ] **HERO-05**: Dynamic aggregate Lines of Code (LOC) counter displaying total additions (`++`) and deletions (`--`) across repositories

### Open Source & Projects Showcase (PROJ)

- [ ] **PROJ-01**: Live Open Source Projects Dashboard displaying real-time Stars (⭐), Forks (🍴), Open Issues (🛎️), and Open Pull Requests (📬)
- [ ] **PROJ-02**: Configurable repository selection enabling user to pin specific repositories (e.g., KRPC robotics, homeserver, IoT environmental monitor) with automatic fallback to top active repos
- [ ] **PROJ-03**: Terminal-box styling (`┌───┐`, `│`, `└───┘` or terminal window card) adhering to dark terminal palette

### Metrics, Languages & Activity (METRIC)

- [ ] **METRIC-01**: Top Languages breakdown calculated from public repositories and rendered as a terminal horizontal progress bar
- [ ] **METRIC-02**: Commit Streak & Contribution Stats card customized strictly to match terminal palette (`#161b22`, amber `#ffa657`, green `#3fb950`)
- [ ] **METRIC-03**: Retro terminal session hits / visitor counter badge
- [ ] **METRIC-04**: Recent Git activity stream displaying recent commits and merged PRs formatted as `git log --graph --oneline`

### Automation & Workflows (AUTO)

- [ ] **AUTO-01**: Standalone Python update engine (`scripts/update_profile.py`) querying GitHub GraphQL API with rate-limit and error handling
- [ ] **AUTO-02**: Scheduled GitHub Actions workflow (`.github/workflows/profile-updater.yml`) running on daily cron and manual trigger (`workflow_dispatch`)
- [ ] **AUTO-03**: Automated git commit and push step within the workflow running under standard `GITHUB_TOKEN` permissions with zero hosting cost

### Skills & Content Extensibility (CONTENT)

- [ ] **CONTENT-01**: Plug-and-play blog / article section ready to pull RSS or markdown links
- [ ] **CONTENT-02**: Terminal-themed categorized skills matrix (AI & Data Science, Backend & Systems, SQA & Automation, Embedded/IoT)

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Interactive & Multimedia (EXTRA)

- **EXTRA-01**: Animated contribution snake game customized with terminal green/amber colorway
- **EXTRA-02**: Spotify / Music player terminal card showing currently playing track

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| GitHub Profile Trophies | Explicitly rejected by user to avoid visual clutter and maintain minimalist technical feel |
| Mismatched Graphical Badges | Bright pastel third-party badges violate the strict terminal aesthetic rule |
| Paid Cloud / Hosting Services | All automation must execute free of charge using GitHub Actions public runner minutes |

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| HERO-01 | Phase 1 | Pending |
| HERO-02 | Phase 1 | Pending |
| HERO-03 | Phase 1 | Pending |
| HERO-04 | Phase 2 | Pending |
| HERO-05 | Phase 2 | Pending |
| AUTO-01 | Phase 2 | Pending |
| PROJ-01 | Phase 3 | Pending |
| PROJ-02 | Phase 3 | Pending |
| PROJ-03 | Phase 3 | Pending |
| METRIC-01 | Phase 4 | Pending |
| METRIC-02 | Phase 4 | Pending |
| METRIC-03 | Phase 4 | Pending |
| METRIC-04 | Phase 4 | Pending |
| CONTENT-01 | Phase 5 | Pending |
| CONTENT-02 | Phase 5 | Pending |
| AUTO-02 | Phase 6 | Pending |
| AUTO-03 | Phase 6 | Pending |

**Coverage:**
- v1 requirements: 17 total
- Mapped to phases: 17
- Unmapped: 0

---
*Requirements defined: 2026-11-06*
*Last updated: 2026-11-06 after initialization*
