# Phase 5: Skills Matrix & Blog Section - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-11-08
**Phase:** 5-Skills Matrix & Blog Section
**Areas discussed:** Skills Matrix Presentation, Skills Taxonomy & Data Architecture, Blog & Publications Data Source, Blog Section Layout in README

---

## Skills Matrix Presentation

| Option | Description | Selected |
|--------|-------------|----------|
| Single Unified SVG Terminal Card (`assets/skills.svg`) | Matches hero.svg, projects.svg, and metrics.svg with dark frame, traffic lights, and pixel-crisp alignment across all platforms | ✓ |
| Terminal Markdown `<pre><code>` Block | ASCII-bordered box with monospaced text directly in README.md | |
| Curated Terminal Shields Badges | Category headers with flat-square badges in README markdown | |
| You decide | Whichever best preserves visual harmony | |

**User's choice:** Single Unified SVG Terminal Card (`assets/skills.svg`).
**Notes:** 2x2 quadrant grid layout selected with distinct ANSI color accents (Cyan, Amber, Green, Purple). Sized with a 380px height floor for visual balance. Skill items styled as terminal tag badges / mini-pills with colored indicator dots and subtle desktop CSS hover transitions. Title bar `skills — zsh` with prompt `humam@workstation:~$ neofetch --skills`. Redundant subtext below the SVG removed during critical review to streamline prompt flow.

---

## Skills Taxonomy & Data Architecture

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated `config/skills.json` | Mirrors config/projects.json with structured category objects, display names, and color tokens, easy to update anytime | ✓ |
| Auto-Parsing `cv/sections/skills.tex` with JSON override | Directly extracts skills from LaTeX CV source | |
| Integrated into `config/terminal_theme.json` | Keep all profile static metadata in one file | |
| You decide | Cleanest to maintain and test | |

**User's choice:** Dedicated `config/skills.json`.
**Notes:** Simplified to clean string arrays per category (e.g. `["PyTorch", "OpenCV", "Scikit-learn"]`), dropping unnecessary `url` properties that cannot be clicked inside SVG `<img>` embeds. Capped to 5–6 skills per category across 2 rows to ensure zero overflow. Initial inventory seeded from authentic CV projects across AI, Backend, SQA, and Embedded/Robotics. Generator implemented as standalone `scripts/generate_skills.py` integrated into `scripts/update_profile.py`, protected by ElementTree validation, idempotent writing, and graceful hardcoded fallbacks for offline test resilience.

---

## Blog & Publications Data Source

| Option | Description | Selected |
|--------|-------------|----------|
| Hybrid Mode (RSS with Curated Fallback) | If an RSS/Atom feed URL is configured in config/articles.json, fetch latest live articles; otherwise fall back to curated manual entries | ✓ |
| Curated Manual Articles Only | Define articles directly in config/articles.json with zero network dependency | |
| Live RSS/Atom Feed Only | Strictly pull from external RSS feed via Python stdlib | |
| You decide | Maximum flexibility with zero dependencies | |

**User's choice:** Hybrid Mode (RSS with Curated Fallback).
**Notes:** Configured via `config/articles.json` (`rss_url`, `max_display: 4`, `curated_articles`). Standard library feed reader in `scripts/update_profile.py` with 5s timeout, namespace-stripping for dual RSS 2.0 and Atom 1.0 support, ISO date formatting `[YYYY-MM-DD]`, HTML entity unescaping, 55-char title truncation, 12h cache TTL in `data/cache.json`, and multi-layer fallback so CI workflows never fail. Seeded with authentic project writeups/notes from CV.

---

## Blog Section Layout in README

| Option | Description | Selected |
|--------|-------------|----------|
| Markdown `<pre><code>` Terminal Box | `<div align="left"><pre><code>` block with prompt, enabling direct clickable HTML `<a>` links across web and mobile | ✓ |
| Dedicated SVG Terminal Window (`assets/blog.svg`) | Visual SVG card (links non-clickable on mobile) | |
| Clean Markdown Table with Terminal Borders | Markdown table with box-drawing characters | |
| You decide | Best interactivity and authentic styling | |

**User's choice:** Markdown `<pre><code>` Terminal Box.
**Notes:** Positioned between `<!-- BLOG:START -->` and `<!-- BLOG:END -->` directly after the Skills Matrix and before the terminal session exit prompt (`humam@workstation:~$ exit`). Uses command prompt `humam@workstation:~$ cat ~/articles.log` and entry syntax `* [YYYY-MM-DD] <a href="url">Title</a> (Platform)` matching the git activity stream.

---

## the agent's Discretion

- Coordinate spacing, pill width calculation, and horizontal margins inside each quadrant.
- Specific default curated entries seeded from CV project descriptions.
- Regular expression parsing helpers for XML date strings.

## Deferred Ideas

- Phase 6: Scheduled GitHub Actions workflow (`.github/workflows/profile-updater.yml`) running daily cron (`AUTO-02`, `AUTO-03`).
- v2 Features: Animated contribution snake game (`EXTRA-01`) and Spotify currently playing terminal card (`EXTRA-02`).
