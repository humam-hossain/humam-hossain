# Phase 3: Open Source Projects Dashboard - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-11-07
**Phase:** 3-Open Source Projects Dashboard
**Areas discussed:** Display Format & Layout, Repository Selection & Pinning, Repository Metrics & Metadata Detail, Caching & Offline Fallback Strategy

---

## Display Format & Layout

| Option | Description | Selected |
|--------|-------------|----------|
| Standalone Terminal SVG Window | Single window with traffic lights, prompt (`humam@workstation:~/projects$ ls -la`), clean monospace grid, and clickable repository links | ✓ |
| Markdown Unicode Box Table | Injected directly into `README.md` using Unicode box characters (`┌───┬───┐`). Pure markdown without generating an extra SVG asset | |
| Grid of Mini Terminal SVG Cards | 2-column grid of individual repository terminal cards (similar to GitHub's native pinned cards but styled as mini terminal windows) | |

**User's choice:** Standalone Terminal SVG Window (`assets/projects.svg`)
**Notes:** Provides pixel-perfect terminal styling matching Hero card without markdown parser formatting quirks.

| Option | Description | Selected |
|--------|-------------|----------|
| 2-Column Grid of Project Sub-Panels | 2 columns x 2 rows; each repo gets a terminal sub-box with title, description, language dot, and metric counters | ✓ |
| CLI Tabular List (`ls -la` / `ps` style) | Single unified table where each row is a repo with columns for Name, Primary Language, Stars, Forks, Issues, and PRs | |
| Full-Width Stacked Rows | 1 project per row across full card width, leaving maximum room for longer project descriptions and tech stacks | |

**User's choice:** 2-Column Grid of Project Sub-Panels
**Notes:** Displays 4 featured projects cleanly with dedicated sub-boxes.

| Option | Description | Selected |
|--------|-------------|----------|
| Window Chrome with Traffic Lights + CLI Command Prompt | Title bar with traffic lights and 'projects — zsh', plus a prompt line in the body: 'humam@workstation:~/projects$ gh repo list' | ✓ |
| Hero Window Mirror (No Command Line) | Title bar with traffic lights and title 'humam@workstation:~/projects', stepping directly into the project grid without extra CLI commands | |
| Pure Unix Frame (No Traffic Lights) | Minimalist box-drawing border with embedded prompt header '┌── humam@workstation:~/projects ────────────────────────────┐' | |

**User's choice:** Window Chrome with Traffic Lights + CLI Command Prompt
**Notes:** Mirrors authentic terminal window feel established in Phase 1.

| Option | Description | Selected |
|--------|-------------|----------|
| 4 Projects (2x2 Grid, viewBox '0 0 850 340') | Matches Hero card width (850px); compact, balanced height without cluttering the profile | ✓ |
| 6 Projects (3x2 Grid, viewBox '0 0 850 480') | Shows 6 featured repositories for a deeper showcase of works, with matching 850px width | |
| Dynamic Height | Auto-sized based on repo count in config | |

**User's choice:** 4 Projects (2x2 Grid, viewBox '0 0 850 340')
**Notes:** Exact 850px width maintains visual column alignment with the Hero card.

| Option | Description | Selected |
|--------|-------------|----------|
| Subtle Rounded Sub-Box (`rx="6"`, `stroke="#30363d"`, `fill="#161b22"`) | Clean dark container against `#0d1117` console background, matching GitHub Dark UI | ✓ |
| ASCII-Style Dashed Frame (`stroke-dasharray="4 3"`) | Retro terminal wireframe appearance | |
| Minimalist Open Cards (No sub-borders) | Rely on indentation and clean whitespace without inner box borders | |

**User's choice:** Subtle Rounded Sub-Box (`rx="6"`, `stroke="#30363d"`, `fill="#161b22"`)
**Notes:** Gives distinct container elevation for each project.

| Option | Description | Selected |
|--------|-------------|----------|
| SVG Card + Terminal Quick-Links | SVG renders pixel-perfect terminal window; an authentic terminal command line directly below it in README (e.g., `cd humam-hossain/<repo>`) provides direct clickable markdown links | ✓ |
| Wrap SVG in Link to All Repositories | Clicking the SVG card opens `https://github.com/humam-hossain?tab=repositories` | |
| Standalone SVG Card Only | Pure visual showcase card without additional link lines below it | |

**User's choice:** SVG Card + Terminal Quick-Links
**Notes:** Overcomes GitHub Camo proxy stripping inline SVG hyperlinks while keeping the terminal metaphor intact.

| Option | Description | Selected |
|--------|-------------|----------|
| Clean Whitespace Margin (`<br />`) | No redundant text header; let the SVG window's own title bar and prompt introduce the section | ✓ |
| Terminal Prompt Header | Subtle terminal command banner above the card (e.g., `humam@workstation:~$ ./show_projects.sh`) | |
| Standard Markdown Heading | Markdown header (`## 🛠️ Open Source Projects`) for native GitHub table of contents navigation | |

**User's choice:** Clean Whitespace Margin (`<br />`)
**Notes:** Avoids redundant text above the terminal window card.

| Option | Description | Selected |
|--------|-------------|----------|
| Harmonized ANSI Syntax Palette | Cyan (`#a5d6ff`) repo name, Muted gray (`#8b949e`) description, and ANSI-colored metric icons/counters (Yellow stars, Blue forks, Amber issues, Purple PRs) | ✓ |
| High-Contrast Minimalist | White (`#c9d1d9`) repo title, Muted gray (`#616e7f`) description, and uniform Prompt Blue (`#58a6ff`) for all metric numbers | |
| Full Monogram Match | Cyan (`#a5d6ff`) headers and Amber (`#ffa657`) metric numbers strictly matching the hero monogram and telemetry keys | |

**User's choice:** Harmonized ANSI Syntax Palette
**Notes:** Consistent with the design system defined in `docs/DESIGN_SYSTEM.md`.

---

## Repository Selection & Pinning

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated `config/projects.json` File | Dedicated, easy-to-edit file for project curation with strict explicit user control over which repos and features appear | ✓ |
| Centralized in `config/terminal_theme.json` | Add a 'projects' key with pinned repo names and fallback rules | |
| Pure CLI / Script Argument | Pass pinned repos via environment variables or CLI flags | |

**User's choice:** Dedicated `config/projects.json` File (User explicit input)
**Notes:** User emphasized having a dedicated file where they personally curate the exact projects and features shown, rejecting automatic backfilling of unwanted public repos.

| Option | Description | Selected |
|--------|-------------|----------|
| Hybrid Format (String or Object with Optional Overrides) | Supports `"repo-name"` or `{"repo": "owner/repo", "name": "display-name", "description": "Custom summary", "tag": "Robotics"}`; falls back to GitHub API description if omitted | ✓ |
| Strict String List | 100% of descriptions, names, and topics derived automatically from GitHub API with no manual overrides | |
| Rich Configuration Objects Mandatory | Every repo item in config must define explicit title, description, and custom category tags | |

**User's choice:** Hybrid Format (String or Object with Optional Overrides)
**Notes:** Maximum flexibility for clean curation.

| Option | Description | Selected |
|--------|-------------|----------|
| Support Both Own Repos & Org Repos | Support `'repo-name'` (defaults to `humam-hossain/repo`) or `'owner/repo'` for collaborative/organization projects | ✓ |
| Strictly User-Owned Repos Only | Only allow repositories under github.com/humam-hossain; reject or ignore external org references | |

**User's choice:** Support Both Own Repos & Org Repos
**Notes:** Allows showcasing high-impact collaborative open source contributions.

| Option | Description | Selected |
|--------|-------------|----------|
| Curated Starter List | Seed `config/projects.json` with detected active repositories (`linux_shell_scripting`, `Python`) | ✓ |
| Empty Pinned List (`[]`) | 100% dynamic discovery on first run | |

**User's choice:** Curated Starter List in `config/projects.json`

| Option | Description | Selected |
|--------|-------------|----------|
| Clean Short Name with CLI Prefix (`📁 repo-name`) | Maximizes readable space inside the sub-panel, while full namespace `humam-hossain/repo` is shown in README quick-links | ✓ |
| Full Namespaced Path (`humam-hossain/repo-name`) | Shows explicit owner and repository name directly inside SVG header | |
| Executable Style (`./repo-name`) | Formatted as an executable script or terminal binary name | |

**User's choice:** Clean Short Name with CLI Prefix (`📁 repo-name`)

| Option | Description | Selected |
|--------|-------------|----------|
| Smart Fallback Description | Display topics/tags (e.g., `#python #automation`) or default fallback phrase (e.g., 'Open-source software repository') so panel layout stays vertically balanced | ✓ |
| Topics Tags First, then Generic Fallback | If description is empty, pull repository topics; if no topics, use generic terminal fallback | |
| Collapse Space (Empty line) | Do not render description text if absent | |

**User's choice:** Smart Fallback Description

---

## Repository Metrics & Metadata Detail

| Option | Description | Selected |
|--------|-------------|----------|
| Horizontal Metric Row at Bottom of Sub-Box | Clean row of icons + numbers (`★ 12   ⌥ 4   ⊙ 2   ⑂ 1`) along the bottom of the card in ANSI colors | ✓ |
| Two-Column Metric Grid | Compact 2x2 cluster (Stars & Forks on left, Issues & PRs on right) at bottom right of each panel | |
| Terminal Tag Pills | Small rectangular terminal pill containers around each metric with colored text | |

**User's choice:** Horizontal Metric Row at Bottom of Sub-Box

| Option | Description | Selected |
|--------|-------------|----------|
| Top-Right Header Corner (`● Python`) | Language dot with official GitHub/ANSI color and language name aligned opposite repository title | ✓ |
| Bottom Metrics Row Prefix | Placed at far left of bottom metric row (`● Python   ★ 12   ⌥ 4   ⊙ 1   ⑂ 0`) | |
| Omit Language from SVG | Keep sub-box focused only on title, description, and 4 metrics | |

**User's choice:** Top-Right Header Corner (`● Python`)

| Option | Description | Selected |
|--------|-------------|----------|
| Fixed 2-Line Truncation (~80-85 chars with ellipsis) | Allows 2 lines of description text, truncating longer summaries with '...' to keep all 4 boxes identical in height | ✓ |
| Strict 1-Line Truncation (~42 chars with ellipsis) | Maximum vertical compactness; shows a punchy one-line snippet | |
| Full Word-Wrap (Variable Height) | Allow descriptions to wrap up to 3 lines without truncation | |

**User's choice:** Fixed 2-Line Truncation (~80-85 chars with ellipsis)

| Option | Description | Selected |
|--------|-------------|----------|
| Always Show All 4 Metrics (Mute zeros in `#616e7f`) | Keep all 4 metric slots visible for layout consistency; render 0 in muted gray while non-zero values use vibrant ANSI accents | ✓ |
| Hide Zero-Value Metrics | Only display metrics that have a value > 0 to emphasize positive counts | |
| Show All with Identical Color | Always show all 4 metrics with uniform color regardless of value | |

**User's choice:** Always Show All 4 Metrics (Mute zeros in `#616e7f`)

---

## Caching & Offline Fallback Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated 'project_metrics' key in `data/cache.json` | Store per-repo metrics (stars, forks, issues, prs, language, description, fetched_at) alongside existing telemetry cache in `data/cache.json` | ✓ |
| Merge into existing 'repositories' key in `data/cache.json` | Add new metric fields directly onto existing LOC repository objects | |
| Separate `data/projects_cache.json` | Create an isolated cache file specifically for repository showcase data | |

**User's choice:** Dedicated 'project_metrics' key in `data/cache.json`

| Option | Description | Selected |
|--------|-------------|----------|
| Cache Fallback with Static Mock Fallback | If cached metrics exist, use them with a [WARN] log; if cache is empty (fresh clone/tests), fall back to built-in fixture metrics so tests pass 100% offline | ✓ |
| Freeze Existing Files | Skip generating projects.svg and leaving README.md untouched when no token is available | |
| Strict Failure | Exit with non-zero status if GitHub API cannot be reached | |

**User's choice:** Cache Fallback with Static Mock Fallback

| Option | Description | Selected |
|--------|-------------|----------|
| Single Consolidated GraphQL Query | Fetch all featured repos (stars, forks, open issues, open PRs, language, description) in a single batched GraphQL query (1 API call) | ✓ |
| REST API Multi-Endpoint Requests | Fetch each repository individually via GitHub REST v3 endpoints | |
| Incremental Timestamp Check | Only query metrics for repositories whose pushedAt has changed since last run | |

**User's choice:** Single Consolidated GraphQL Query

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated Generator `scripts/generate_projects.py` + `update_profile.py` Coordinator | `generate_projects.py` handles SVG rendering & validation, while `update_profile.py` orchestrates API fetching, cache persistence, and README anchor injection | ✓ |
| Monolithic Single Script | Put all project SVG template building and README replacement directly into `scripts/update_profile.py` | |
| Independent `scripts/update_projects.py` | Completely separate script run independently from the telemetry engine | |

**User's choice:** Dedicated Generator `scripts/generate_projects.py` + `update_profile.py` Coordinator

---

## the agent's Discretion

- Coordinate calculations and line spacing inside `viewBox="0 0 850 340"`.
- Precise vector glyph paths for stars, forks, issues, and PR icons.
- Exact internal layout of `project_metrics` dictionary in `data/cache.json`.

## Deferred Ideas

- None — all topics discussed stayed strictly within Phase 3 scope.
