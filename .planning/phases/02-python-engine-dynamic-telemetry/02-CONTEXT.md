# Phase 2: Python Engine & Dynamic Telemetry - Context

**Gathered:** 2026-11-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the standalone Python update engine (`scripts/update_profile.py`) that queries the GitHub GraphQL API for user contribution data and repository metrics, calculates real-time coding uptime and aggregate lines of code (LOC: additions `++` and deletions `--`), and updates the dark terminal hero card (`assets/hero.svg`) via parameterized re-rendering.
</domain>

<decisions>
## Implementation Decisions

### Uptime Calculation & Baseline
- **D-01:** **Hybrid Baseline Start Date** — Query GitHub GraphQL API for the earliest commit contribution (using `contributionsCollection.contributionYears`), falling back to user account `createdAt` timestamp if commit history is empty or private, with support for an explicit override timestamp in config. — **Reversibility:** reversible
- **D-02:** **Permanent Baseline Caching** — Discovered first-commit baseline timestamp is stored in `data/cache.json` (tracked in git), ensuring daily GitHub Actions runners execute with zero historical API queries. — **Reversibility:** costly — Downstream automation and actions workflows rely on this cache file location.
- **D-03:** **Strict UTC & Calendar-Accurate Math** — Current timestamp evaluated in strict UTC (`datetime.timezone.utc`) using standard library date math calculating exact calendar years, months, and days.
- **D-04:** **Neofetch Uptime Format & Layout Stability** — Format as `X yrs, Y mos, Z days` with intelligent pluralization (`1 yr` / `2 yrs`, `1 mo` / `3 mos`, `1 day` / `12 days`) while always displaying all three units (e.g., `4 yrs, 0 mos, 12 days`) to preserve stable terminal layout width.

### LOC Aggregation & Repo Filtering
- **D-05:** **Owned Public Non-Fork Repositories** — Aggregate LOC additions (`++`) and deletions (`--`) across all public non-fork repositories owned by `humam-hossain`, including archived repositories to capture full lifetime code authoring. — **Reversibility:** reversible
- **D-06:** **Configurable Exclude List** — Support an optional `exclude_repos` array in `config/terminal_theme.json` (default empty) to filter out dataset, vendor, or bulk machine-generated repositories.
- **D-07:** **Incremental Repo Caching** — Cache per-repository LOC totals alongside their `pushedAt` timestamp in `data/cache.json`. `update_profile.py` only re-queries repositories whose `pushedAt` timestamp has changed, minimizing GraphQL API consumption. — **Reversibility:** costly
- **D-08:** **LOC Number Formatting** — Format additions and deletions as comma-separated integers (`++320,410 / --85,240`), preserving exact Neofetch counts and terminal aesthetic.

### SVG Update Architecture
- **D-09:** **Generator Re-rendering with DOM Hooks Preserved** — Parameterize `generate_svg(uptime=None, loc_add=None, loc_del=None)` in `scripts/generate_hero.py`. `update_profile.py` imports and calls `generate_svg()` with fresh metrics. The generated SVG preserves DOM IDs (`id="val-uptime"`, `id="val-loc-add"`, `id="val-loc-del"`), keeping existing test suites passing while guaranteeing valid XML. — **Reversibility:** costly — Generator signature is the single source of truth for SVG creation.
- **D-10:** **Strict XML Validation** — Prior to writing to `assets/hero.svg`, validate output using `xml.etree.ElementTree.fromstring()` to ensure well-formedness.
- **D-11:** **Idempotent File Writes** — If the freshly generated SVG content is byte-identical to `assets/hero.svg`, skip disk write to prevent unnecessary file touches and git diff churn.
- **D-12:** **Terminal-Styled CLI Logging** — Script emits clean ANSI-formatted console status lines (`[INFO]`, `[OK]`, telemetry summary) matching the workstation terminal theme tokens.

### Credentials & Local Development
- **D-13:** **Multi-Source Authentication** — Token resolved from `GITHUB_TOKEN` environment variable, falling back to `GH_TOKEN`, falling back to local `.env` via a lightweight stdlib key-value parser (zero external pip packages).
- **D-14:** **Graceful Offline / Mock Fallback** — When executed without a token (local development or offline testing), emit a warning (`[WARN] No token found. Running offline with cached/mock telemetry`) and proceed without raising unhandled exceptions.
- **D-15:** **Rate-Limit Backoff & Retries** — Check `X-RateLimit-Remaining` and `Retry-After` headers on GitHub API responses; implement exponential backoff with up to 3 retries for transient HTTP/network errors.
- **D-16:** **Offline Test Suite** — Build `tests/test_update_profile.py` using fixture JSON files to mock GraphQL responses, achieving 100% test coverage without hitting live network endpoints or requiring tokens.

### the agent's Discretion
- Minimalist GraphQL query payloads requesting only required fields (`viewer`, `contributionsCollection`, `repositories`).
- ANSI terminal color escape sequence helpers for stdout logging.
- Exact internal structure of `data/cache.json`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Specifications & Requirements
- `.planning/PROJECT.md` — Core value, ANSI palette rules, and scope boundaries.
- `.planning/REQUIREMENTS.md` — Requirements catalog (specifically HERO-04, HERO-05, AUTO-01).
- `.planning/ROADMAP.md` — Phase 2 goals, plans, and success criteria.

### Phase 1 Foundations
- `.planning/phases/01-hero-terminal-card-design-system/01-CONTEXT.md` — Established terminal design tokens and DOM hooks.
- `config/terminal_theme.json` — Color tokens, typography, and geometry specifications.
- `scripts/generate_hero.py` — Existing SVG generator to be parameterized.
- `assets/hero.svg` — Target terminal card output.
- `tests/test_tokens.py` — Existing token validation and DOM ID assertions.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/generate_hero.py`: Contains `generate_svg()` and `TELEMETRY_ITEMS`. Can be extended with default parameters `uptime=None`, `loc_add=None`, `loc_del=None` while keeping DOM IDs intact.
- `config/terminal_theme.json`: Can house optional configuration additions such as `exclude_repos` and `baseline_override_date`.

### Established Patterns
- Python Standard Library Only: Zero external packages (no `requests`, no `python-dotenv`), relying entirely on `urllib.request`, `xml.etree.ElementTree`, `json`, and `datetime`.
- Strict ElementTree validation before file writing.
- Pytest suite in `tests/` with assertions for structure, styling, and schema.

### Integration Points
- `scripts/update_profile.py`: New standalone update engine to be created.
- `data/cache.json`: Persistent telemetry cache file storing baseline commit date and per-repo LOC metrics.
- `assets/hero.svg`: Regenerated output file.
- `tests/test_update_profile.py`: New unit and integration test suite.

</code_context>

<specifics>
## Specific Ideas
- Incremental caching strategy where repository LOC is only recalculated when a repository's `pushedAt` timestamp advances, reducing daily GitHub Actions runtime to seconds and conserving API quotas.
- Clean Neofetch-style telemetry formatting with stable column widths.
</specifics>

<deferred>
## Deferred Ideas
- Phase 3: Open Source Projects Dashboard (`PROJ-01`, `PROJ-02`, `PROJ-03`)
- Phase 4: Top Languages breakdown, commit streak card, and git activity stream (`METRIC-01` through `METRIC-04`)
- Phase 5: Categorized Skills Matrix and plug-and-play blog section (`CONTENT-01`, `CONTENT-02`)
- Phase 6: Scheduled GitHub Actions workflow (`AUTO-02`, `AUTO-03`)
</deferred>

---

*Phase: 2-Python Engine & Dynamic Telemetry*
*Context gathered: 2026-11-07*
