# Phase 3: Open Source Projects Dashboard - Context

**Gathered:** 2026-11-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver a live Open Source Projects Dashboard section below the hero card in `README.md` (between `<!-- PROJECTS:START -->` and `<!-- PROJECTS:END -->`), rendered as a dedicated dark terminal SVG window (`assets/projects.svg`) displaying real-time repository metrics (⭐ Stars, 🍴 Forks, 🛎️ Open Issues, 📬 Open PRs, Primary Language) for user-curated repositories configured in `config/projects.json`, backed by consolidated GraphQL queries, cached persistence, and offline test resilience in `scripts/update_profile.py`.

</domain>

<decisions>
## Implementation Decisions

### Visual Presentation & Window Architecture
- **D-01:** **Standalone Terminal SVG Window** — Single dedicated dark terminal SVG (`assets/projects.svg`) styled as a workstation terminal window with subtle rounded frame (`rx="10"`, border `#30363d`), header bar (`#161b22`), macOS traffic lights (🔴 `#ff5f56`, 🟡 `#ffbd2e`, 🟢 `#27c93f`), title bar `projects — zsh`, and console prompt line: `humam@workstation:~/projects$ gh repo list`. — **Reversibility:** costly — Eliminates HTML/markdown table parsing inconsistencies and ensures Camo-proxy rendering fidelity, but dictates downstream generator structure.
- **D-02:** **Dimensions & Capacity** — Responsive `viewBox="0 0 850 340"` with `width="100%"` in `README.md`, perfectly aligning with the 850px width of `assets/hero.svg`. Accommodates a 2-column by 2-row grid of 4 featured projects.
- **D-03:** **2-Column Grid of Project Sub-Panels** — Inside the console body (`#0d1117`), repositories are arranged in a 2x2 grid. Each repository sits inside a distinct sub-panel container with subtle rounded corners (`rx="6"`, border `1px solid #30363d`, background `#161b22`).
- **D-04:** **Section Transition & Heading** — Clean whitespace margin (`<br />`) between the top contact badges and the Projects Dashboard; no redundant markdown heading so the terminal card's own title bar and prompt introduce the section organically.

### Repository Navigation & GitHub Interaction
- **D-05:** **Terminal Quick-Links in README** — Because GitHub's image proxy strips interactive `<a href="...">` hyperlinks inside embedded SVGs, `README.md` includes an authentic terminal command line directly below `assets/projects.svg` between `<!-- PROJECTS:START -->` and `<!-- PROJECTS:END -->` (e.g. `<code>humam@workstation:~/projects$ cd humam-hossain/<repo></code>`) providing direct clickable markdown links to each featured repository.
- **D-06:** **Sub-Panel Header & Titles** — Clean short repository name with CLI folder prefix (`📁 repo-name` or `~/repo-name`) in Cyan (`#a5d6ff`) on the top-left; primary language with color dot (`● Python`) on the top-right opposite the repo title.

### Project Curation & Configuration
- **D-07:** **Dedicated Curation File (`config/projects.json`)** — Pinned repositories and their custom attributes are maintained in an independent, human-editable configuration file (`config/projects.json`) rather than mixing content curation into `config/terminal_theme.json`. — **Reversibility:** costly — Downstream scripts and workflows will read this configuration schema.
- **D-08:** **Strict User Curation (No Auto-Fill / Surprise Repos)** — Only repositories explicitly declared in `config/projects.json` are rendered in the dashboard. The system does not automatically backfill unpinned or unwanted public repositories, giving the user 100% curation authority over their profile showcase.
- **D-09:** **Flexible Project Schema with Overrides** — Entries in `config/projects.json` support simple strings (`"repo-name"`) or rich objects (`{"repo": "owner/repo", "name": "display-name", "description": "Custom summary", "tag": "Robotics"}`). Supports both user-owned repositories (defaults to `humam-hossain/`) and external organization/collaborative repositories.
- **D-10:** **Initial Starter Pins** — Starter list in `config/projects.json` seeded with user's detected active repositories (`linux_shell_scripting`, `Python`), ready for immediate customization.

### Metrics, Formatting & Typography
- **D-11:** **Harmonized ANSI Syntax Palette** — Repository titles in Cyan (`#a5d6ff`), descriptions in Muted Gray (`#8b949e`), and ANSI-colored metric icons/counters: Star Yellow (`#f1e05a`), Fork Blue (`#58a6ff`), Issue Amber (`#ffa657`), PR Purple (`#a371f7`).
- **D-12:** **Horizontal Bottom Metrics Row** — Real-time metrics arranged cleanly along the bottom baseline of each sub-panel: `★ Stars   ⌥ Forks   ⊙ Issues   ⑂ PRs`. Non-zero values use vibrant ANSI accents; zero counts (`0`) are rendered in muted gray (`#616e7f`) to preserve layout stability without visual noise.
- **D-13:** **2-Line Description Clamping** — Descriptions are clamped to 2 lines (~80–85 characters max) with ellipsis (`...`) truncation to keep all 4 sub-box heights uniform.
- **D-14:** **Smart Fallback Description** — If a repository has no description on GitHub and no custom override in `config/projects.json`, display repository topics (e.g., `#python #automation`) or fallback phrase (`Open-source software repository`) to prevent empty vertical gaps.

### Engine Architecture, Caching & Testing
- **D-15:** **Modular Codebase Architecture** — Standalone generator `scripts/generate_projects.py` handles SVG rendering, typography styling, and ElementTree XML validation; `scripts/update_profile.py` serves as the coordinator, querying GraphQL, updating cache, calling the generator, writing `assets/projects.svg`, and injecting README markdown quick-links. — **Reversibility:** costly
- **D-16:** **Consolidated Batched GraphQL Query** — Metrics for all featured repositories (stars, forks, open issues, open PRs, primary language, topics, and description) are fetched in a single consolidated GraphQL query, consuming only 1 API quota point.
- **D-17:** **Telemetry Cache Persistence (`data/cache.json`)** — Fetched repository metrics are saved under a dedicated `project_metrics` key in `data/cache.json` alongside a `last_updated` UTC timestamp.
- **D-18:** **Offline & Mock Fallback Resilience** — When running without `GITHUB_TOKEN` or offline, `update_profile.py` renders using cached `project_metrics`. If the cache is empty (fresh clone/CI testing), it falls back to built-in static fixture metrics with `[WARN]` logging, ensuring 100% test pass rate without network.
- **D-19:** **Idempotent Output Writes** — Both `assets/projects.svg` and `README.md` are updated only if their contents change, preventing unnecessary git diff churn.

### the agent's Discretion
- Micro-spacing, padding, and exact coordinate layout within the `viewBox="0 0 850 340"` SVG grid.
- Precise SVG path icons for star, fork, issue, and pull request glyphs.
- Internal schema formatting for `project_metrics` in `data/cache.json`.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Specifications & Requirements
- `.planning/PROJECT.md` — Terminal design language, ANSI palette constraints, and zero-cost automation boundary.
- `.planning/REQUIREMENTS.md` — PROJ-01, PROJ-02, PROJ-03 specification and traceability.
- `.planning/ROADMAP.md` — Phase 3 goals, plan breakdown, and success criteria.

### Prior Phase Foundations
- `.planning/phases/01-hero-terminal-card-design-system/01-CONTEXT.md` — Design token system and SVG generation patterns.
- `.planning/phases/02-python-engine-dynamic-telemetry/02-CONTEXT.md` — Python engine architecture, GraphQL client, and caching strategy.
- `config/terminal_theme.json` — Color tokens, typography rules, and frame geometry.
- `scripts/update_profile.py` — Existing telemetry engine to be extended with project query and coordinator logic.
- `scripts/generate_hero.py` — Reference implementation for standard library XML/SVG generation.
- `README.md` — Profile target containing `<!-- PROJECTS:START -->` and `<!-- PROJECTS:END -->` anchor markers.
- `data/cache.json` — Existing cache file to be extended with `project_metrics`.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `config/terminal_theme.json`: Contains official color tokens (backgrounds, borders, text, ANSI syntax palette) and typography font stack (`ui-monospace, SFMono-Regular, Menlo, Consolas, "Fira Code", monospace`).
- `scripts/update_profile.py`: Contains `execute_graphql_query()`, token resolution, rate-limit backoff, ANSI logging (`log_info`, `log_ok`, `log_warn`, `log_err`), and `write_svg_idempotent()`.
- `tests/test_update_profile.py`: Mocking patterns and offline test fixtures using `unittest.mock`.

### Established Patterns
- Python Standard Library Only: Zero external packages (`urllib.request`, `xml.etree.ElementTree`, `json`, `pathlib`).
- Idempotent file writes: Comparing byte contents before disk write.
- ElementTree XML validation before writing SVG files to disk.
- HTML anchor comment tags in `README.md` for surgical text replacement.

### Integration Points
- `config/projects.json`: New configuration file to define featured repositories and custom overrides.
- `scripts/generate_projects.py`: New standalone generator script for the Projects Dashboard SVG.
- `scripts/update_profile.py`: Extend `main()` to query project metrics, update cache, invoke `generate_projects_svg()`, and patch `README.md`.
- `assets/projects.svg`: New generated SVG asset embedded in `README.md`.
- `README.md`: Anchor block `<!-- PROJECTS:START -->` to `<!-- PROJECTS:END -->` updated with SVG embed and terminal quick-links.
- `tests/test_projects.py`: New test suite validating project config parsing, SVG validity, and offline fallback.

</code_context>

<specifics>
## Specific Ideas
- Authentic Neofetch CLI directory listing feel: window title `projects — zsh` and prompt `humam@workstation:~/projects$ gh repo list` at the top of the SVG window.
- Direct quick-links line in README: `<div align="center"><code>humam@workstation:~/projects$ cd <a href="...">repo-1</a> | cd <a href="...">repo-2</a></code></div>` providing seamless 1-click navigation without breaking terminal immersion.
- Exact 850px width matching `assets/hero.svg` for a clean visual column on GitHub desktop profile views.
</specifics>

<deferred>
## Deferred Ideas
- Phase 4: Top Languages horizontal progress bar, commit streak stats card, retro visitor counter, and git activity stream (`METRIC-01` through `METRIC-04`).
- Phase 5: Categorized Skills Matrix and plug-and-play RSS blog section (`CONTENT-01`, `CONTENT-02`).
- Phase 6: Daily scheduled GitHub Actions workflow (`AUTO-02`, `AUTO-03`).
</deferred>

---

*Phase: 3-Open Source Projects Dashboard*
*Context gathered: 2026-11-07*
