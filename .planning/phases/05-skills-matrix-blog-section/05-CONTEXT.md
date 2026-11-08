# Phase 5: Skills Matrix & Blog Section - Context

**Gathered:** 2026-11-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver a terminal-themed categorized skills matrix and a plug-and-play blog/articles section for Muhammed Humam Hossain's GitHub Profile README. The deliverables comprise:
1. A single self-contained dark terminal SVG window (`assets/skills.svg`, 850px wide) displaying a 2x2 quadrant grid of technical competencies (AI & Data Science, Backend & Systems, SQA & Automation, Embedded & Robotics) with monospaced pill badges and subtle desktop hover highlights.
2. A dedicated JSON configuration file (`config/skills.json`) maintaining curated skills lists and ANSI color token associations, backed by a standalone generator (`scripts/generate_skills.py`).
3. A plug-and-play blog/publication reader in `scripts/update_profile.py` supporting both live RSS 2.0 / Atom 1.0 feeds and curated entries configured in `config/articles.json`, with multi-layer error fallback and caching in `data/cache.json`.
4. A terminal-styled publication log box in `README.md` (between `<!-- BLOG:START -->` and `<!-- BLOG:END -->`) rendered via a `<pre><code>` block with prompt `humam@workstation:~$ cat ~/articles.log` and clickable article links, positioned directly after Skills and before the terminal session exit prompt.

All scripts operate under pure Python standard library constraints with zero third-party pip dependencies, full XML integrity verification, and offline test fixture support.

</domain>

<decisions>
## Implementation Decisions

### Skills Matrix Presentation & SVG Window
- **D-01:** **Unified Terminal SVG Window (`assets/skills.svg`)** — Rendered as a single 850px-wide dark SVG card matching `assets/hero.svg`, `assets/projects.svg`, and `assets/metrics.svg` in corner radius (`rx="10"`), border (`#30363d`), header bar (`#161b22`), and background (`#0d1117`). — **Reversibility:** costly — Generator architecture, test fixtures, and README anchors depend on this vector card.
- **D-02:** **2x2 Quadrant Grid Layout** — Four rounded sub-panels (`rx="6"`, background `#161b22`, border `#30363d`) representing the 4 core disciplines:
  - Top-Left: AI & Data Science (Cyan `#a5d6ff`)
  - Top-Right: Backend & Systems (Amber `#ffa657`)
  - Bottom-Left: SQA & Automation (Green `#3fb950`)
  - Bottom-Right: Embedded & Robotics (Purple `#d2a8ff`)
- **D-03:** **Terminal Tag Badges / Mini-Pills** — Monospaced pill capsules with dark fill (`#21262d`), 1px border (`#30363d`), category-colored indicator dots (e.g. `● PyTorch`, `● Docker`), and crisp monospace typography (`Fira Code`, `Consolas`).
- **D-04:** **Window Chrome & Prompt** — Title bar `skills — zsh` with colored traffic lights (🔴 `#ff5f56`, 🟡 `#ffbd2e`, 🟢 `#27c93f`) and terminal prompt line: `humam@workstation:~$ neofetch --skills`.
- **D-05:** **Height Calculation with 380px Floor** — Symmetrical 2x2 grid sized with a minimum height floor of 380px (`height = max(380, calculated_height)`), matching `hero.svg` (360px) and `metrics.svg` (390px) for visual balance across the profile.
- **D-06:** **Enhanced SVG with Desktop CSS Hover Transitions** — Embedded SVG `<style>` includes subtle `:hover` brightness increase and border tint on skill pills for desktop browsers, while degrading gracefully to static shapes on mobile.

### Skills Taxonomy & Data Architecture
- **D-07:** **Dedicated Configuration File (`config/skills.json`)** — Clean, structured JSON file defining categories with `id`, `title`, `accent`, and an array of plain string skill names (e.g. `["PyTorch", "OpenCV", "Scikit-learn"]`). Avoids dead `url` fields that GitHub's SVG `<img>` embeds do not support.
- **D-08:** **Capacity Capping (5–6 Skills per Quadrant)** — Each quadrant is capped at 5–6 high-impact skills arranged across 2 rows of pill tags, guaranteeing zero overflow or border collision.
- **D-09:** **Initial Curated Inventory Seeded from CV** —
  - *AI & Data Science:* PyTorch, OpenCV, Scikit-learn, Pandas, PyBullet
  - *Backend & Systems:* Python, Node.js, Linux/Bash, MongoDB, SQLite
  - *SQA & Automation:* PyTest, Jest, CI/CD, Test Planning, Static Analysis
  - *Embedded & Robotics:* C/C++, ROS2, Arduino, ESP32, Kinematics
- **D-10:** **Standalone Generator (`scripts/generate_skills.py`)** — Standalone CLI generator callable independently and integrated into `scripts/update_profile.py`, mirroring `generate_hero.py` and `generate_metrics.py`.
- **D-11:** **Hardcoded Graceful Fallback** — If `config/skills.json` is missing or corrupted, `generate_skills.py` logs a warning and falls back to built-in default categories so CI runs never fail.
- **D-12:** **Full XML Integrity & Idempotent File Writing** — Validates markup via `xml.etree.ElementTree` before disk write, and uses byte-level comparison to prevent Git dirty churn when skills are unchanged.

### Blog & Publications Data Source
- **D-13:** **Hybrid Ingestion Architecture (RSS with Curated Fallback)** — If `rss_url` is configured in `config/articles.json`, `update_profile.py` fetches the live feed; if `rss_url` is empty, inaccessible, or times out, it falls back to `curated_articles`.
- **D-14:** **Clean Config Schema (`config/articles.json`)** —
  ```json
  {
    "rss_url": "",
    "max_display": 4,
    "curated_articles": [
      {
        "title": "Autonomous Rover Navigation with ROS2 and PyBullet",
        "url": "https://github.com/humam-hossain",
        "date": "2024-04-15",
        "platform": "Project Note"
      },
      {
        "title": "Continuous Test Automation Architecture for Linux Embedded Systems",
        "url": "https://github.com/humam-hossain",
        "date": "2024-02-10",
        "platform": "Whitepaper"
      }
    ]
  }
  ```
- **D-15:** **Resilient Stdlib Feed Fetcher** — 5-second HTTP timeout with custom User-Agent. On error, network failure, or HTTP error, falls back to `data/cache.json`, then to `curated_articles`. Never throws unhandled exceptions or halts CI.
- **D-16:** **Dual Format XML Parser (RSS 2.0 & Atom 1.0)** — Pure Python stdlib parser using `xml.etree.ElementTree` with local tag namespace stripping (`elem.tag.split('}')[-1]`), handling `<item>` (RSS) and `<entry>` (Atom).
- **D-17:** **Date & Title Normalization** — Dates parsed into ISO format `[YYYY-MM-DD]` via stdlib `datetime` and `email.utils.parsedate_to_datetime`. Titles unescaped with `html.unescape()` and capped at 55 characters with `'...'` to preserve strict 80-column alignment.
- **D-18:** **Cache Management with 12h TTL** — Cached articles persisted in `data/cache.json` under `"articles"`. Network re-fetch is skipped if cache is younger than 12 hours (unless `--refresh` is supplied), guaranteeing unit tests run 100% offline.

### Blog Section Layout in README & Streamlined Sequencing
- **D-19:** **Markdown `<pre><code>` Container** — Rendered between `<!-- BLOG:START -->` and `<!-- BLOG:END -->` as an authentic terminal code box (`<div align="left"><pre><code>...</code></pre></div>`), ensuring direct clickable `<a>` links across all GitHub web and mobile interfaces.
- **D-20:** **Terminal Prompt Command** — `humam@workstation:~$ cat ~/articles.log`.
- **D-21:** **Line Formatting Syntax** — `* [YYYY-MM-DD] <a href="url">Title</a> (Platform)` — matches the git activity stream syntax (`* [sha] (repo) message (time)`).
- **D-22:** **Streamlined Terminal Sequence (No Prompt Clutter)** — Prompts flow logically without redundant subtext lines:
  1. Projects SVG + `cd <project>`
  2. Metrics SVG + `git log --graph --oneline`
  3. Skills Matrix SVG (`neofetch --skills`)
  4. Articles Log `<pre><code>` (`cat ~/articles.log`)
  5. Terminal Session Exit (`humam@workstation:~$ exit`)

### the agent's Discretion
- Exact coordinate math, vertical margins, and pill pill horizontal spacing inside each quadrant.
- Specific default entries in `config/articles.json` seeded from CV projects.
- Regular expression patterns for RFC 822 / ISO 8601 timestamp parsing in `scripts/update_profile.py`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Specifications & Requirements
- `.planning/PROJECT.md` — Core terminal aesthetic guidelines, zero-cost GitHub Actions boundary, and ANSI palette definitions.
- `.planning/REQUIREMENTS.md` — Requirement specifications for CONTENT-01 (plug-and-play blog) and CONTENT-02 (categorized skills matrix).
- `.planning/ROADMAP.md` — Phase 5 goal, plan breakdown (05-01 Skills Matrix, 05-02 Blog Section), and acceptance criteria.

### Design System & Prior Phase Foundations
- `config/terminal_theme.json` — Color tokens (background `#161b22`/`#0d1117`, border `#30363d`, ANSI cyan `#a5d6ff`, amber `#ffa657`, green `#3fb950`, purple `#d2a8ff`) and monospace font stacks.
- `.planning/phases/01-hero-terminal-card-design-system/01-CONTEXT.md` — Terminal window chrome geometry, traffic lights, and SVG structure.
- `.planning/phases/03-open-source-projects-dashboard/03-CONTEXT.md` — Project card SVG generator reference, config pattern (`config/projects.json`), and README anchor patching.
- `.planning/phases/04-languages-streaks-metrics/04-CONTEXT.md` — Metrics card architecture, `<pre><code>` terminal stream pattern, and `data/cache.json` caching strategy.

### Codebase Assets & Integration Files
- `cv/sections/skills.tex` — Authentic resume skills inventory for initial seeding.
- `README.md` — Profile target containing `<!-- SKILLS:START -->` ... `<!-- SKILLS:END -->` and insertion point for `<!-- BLOG:START -->` ... `<!-- BLOG:END -->`.
- `scripts/update_profile.py` — Profile update coordinator; will be extended to invoke skills generation, article fetching, and README patching.
- `scripts/generate_hero.py`, `scripts/generate_projects.py`, `scripts/generate_metrics.py` — Reference implementations for pure standard-library SVG generation.
- `data/cache.json` — Telemetry cache to be extended with `"articles"` cache payload and timestamp.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `config/terminal_theme.json`: Supplies all color tokens, box radii, font stacks, and traffic light dimensions.
- `scripts/update_profile.py`: Contains `write_svg_idempotent()`, ANSI console loggers (`log_info`, `log_ok`, `log_warn`, `log_err`), and CLI argument parsing (`--refresh`, `--dry-run`).
- `tests/test_projects.py` & `tests/test_metrics.py`: Established patterns for mocking `urllib.request` and testing XML outputs offline.

### Established Patterns
- Python Standard Library Exclusively: Pure Python 3 (`urllib.request`, `xml.etree.ElementTree`, `html`, `email.utils`, `json`, `datetime`, `pathlib`).
- Idempotent File Operations: Compare buffer before disk write to avoid Git dirty state churn.
- ElementTree Verification: Parse generated SVG strings before saving to guarantee valid XML markup.
- Anchor Replacement in README: Regex replacement between `<!-- {SECTION}:START -->` and `<!-- {SECTION}:END -->`.

### Integration Points
- `config/skills.json`: New configuration file defining the 4 categories and their respective skills.
- `config/articles.json`: New configuration file with RSS feed URL and fallback curated articles.
- `scripts/generate_skills.py`: New standalone generator outputting `assets/skills.svg`.
- `scripts/update_profile.py`: Extended to call `generate_skills.py`, fetch/cache articles, and update both `<!-- SKILLS:START -->` and `<!-- BLOG:START -->` blocks in `README.md`.
- `tests/test_skills.py` & `tests/test_blog.py`: Comprehensive unit test suites verifying XML compliance, pill wrapping, RSS/Atom feed parsing, fallback behaviors, and offline fixture operation.

</code_context>

<specifics>
## Specific Ideas
- The Skills card follows the Neofetch/terminal ethos: title `skills — zsh`, prompt `humam@workstation:~$ neofetch --skills`, and 4 distinct quadrant sub-panels with ANSI header badges.
- Pill badges render with a colored circle indicator (e.g. `<circle cx="..." cy="..." r="3" fill="#a5d6ff"/>`) and monospace text inside a rounded `<rect rx="4" fill="#21262d" stroke="#30363d"/>`.
- The Blog section uses an authentic terminal command line `humam@workstation:~$ cat ~/articles.log` with clickable HTML `<a>` tags for immediate article navigation.
- If no articles are present and no feed is reachable, the section displays:
  `* [standby] feed listener active — configure rss_url in config/articles.json`
</specifics>

<deferred>
## Deferred Ideas
- Phase 6: Scheduled GitHub Actions workflow (`.github/workflows/profile-updater.yml`) running daily cron with zero cost (`AUTO-02`, `AUTO-03`).
- v2 Features: Animated contribution snake game (`EXTRA-01`) and Spotify currently playing terminal card (`EXTRA-02`).
</deferred>

---

*Phase: 5-Skills Matrix & Blog Section*
*Context gathered: 2026-11-08*
