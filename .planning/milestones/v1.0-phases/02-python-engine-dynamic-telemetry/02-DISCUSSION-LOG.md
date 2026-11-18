# Phase 2: Python Engine & Dynamic Telemetry - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-11-07
**Phase:** 2-Python Engine & Dynamic Telemetry
**Areas discussed:** Uptime Calculation & Baseline, LOC Aggregation & Repo Filtering, SVG Update Architecture, Local Development & Token Handling

---

## Uptime Calculation & Baseline

### Question 1: Start Date Determination
| Option | Description | Selected |
|--------|-------------|----------|
| Hybrid Discovery | Auto-query GraphQL for earliest commit with an optional config override date | ✓ |
| Pure GraphQL Discovery | Query GitHub GraphQL API contributionsCollection/commits for the true first commit timestamp | |
| Pinned Date in Config | Set a fixed starting timestamp in config (saves API calls, zero risk of rate limits) | |

**User's choice:** Hybrid: Auto-query GraphQL for earliest commit with an optional config override date (flexible, robust if history is deep).
**Notes:** Automatically extracts baseline date while allowing manual pin if desired.

### Question 2: Format & Granularity
| Option | Description | Selected |
|--------|-------------|----------|
| Full breakdown | 'X yrs, Y mos, Z days' (matches current hero.svg Neofetch format and D-09 specification) | ✓ |
| Compact | 'X yrs, Y mos' (cleaner, changes less frequently so daily git diffs only bump monthly) | |

**User's choice:** Full breakdown: 'X yrs, Y mos, Z days'.
**Notes:** Preserves authentic Unix terminal Neofetch aesthetic established in Phase 1.

### Question 3: Fallback Strategy on Empty First Commit
| Option | Description | Selected |
|--------|-------------|----------|
| Account createdAt fallback | Fallback to user account createdAt timestamp if first commit search returns empty | ✓ |
| Current placeholder fallback | Fallback to current placeholder value in hero.svg (preserves last known state) | |

**User's choice:** Fallback to user account createdAt timestamp if first commit search returns empty (graceful, fully automated).
**Notes:** Ensures automated execution without breaking on accounts with private history.

### Question 4: Time Delta Calculation
| Option | Description | Selected |
|--------|-------------|----------|
| Calendar-accurate math | Stdlib date math computing exact calendar years, months, and days from baseline to now | ✓ |
| Approximate intervals | 365 days/yr and 30 days/mo (simpler arithmetic, slightly less calendar-exact) | |

**User's choice:** Calendar-accurate calculation: Stdlib date math computing exact calendar years, months, and days from baseline to now.
**Notes:** Accurately accounts for varying month lengths and leap years.

### Question 5: Timezone Reference
| Option | Description | Selected |
|--------|-------------|----------|
| Strict UTC | Standardized across local runs and GitHub Actions runners, prevents time skew | ✓ |
| User local timezone | Configurable offset in config (e.g. UTC+6) | |

**User's choice:** Strict UTC (`datetime.timezone.utc`).
**Notes:** Prevents daily git diff jitter caused by runner timezone differences.

### Question 6: Baseline Caching
| Option | Description | Selected |
|--------|-------------|----------|
| Local JSON cache | Cache baseline date in a local JSON cache file (avoids redundant historical API queries) | ✓ |
| Query every run | Stateless, but consumes extra GraphQL rate limit points | |

**User's choice:** Cache baseline date in a local JSON cache file (`data/cache.json`).
**Notes:** Since first commit date is permanent, caching saves unnecessary API calls.

### Question 7: Unit Pluralization
| Option | Description | Selected |
|--------|-------------|----------|
| Intelligent singular/plural | '1 yr' / '2 yrs', '1 mo' / '3 mos', '1 day' / '12 days' | ✓ |
| Fixed abbreviations | Always 'yrs', 'mos', 'days' regardless of count | |

**User's choice:** Intelligent singular/plural: '1 yr' / '2 yrs', '1 mo' / '3 mos', '1 day' / '12 days'.
**Notes:** Clean typographical polish.

### Question 8: Zero-Value Handling
| Option | Description | Selected |
|--------|-------------|----------|
| Display all three units | '4 yrs, 0 mos, 12 days' — maintains stable terminal text alignment and layout width | ✓ |
| Omit zero units | '4 yrs, 12 days' — more natural reading, but variable text width | |

**User's choice:** Always display all three units (e.g., '4 yrs, 0 mos, 12 days').
**Notes:** Prevents telemetry text column width jitter in SVG.

---

## LOC Aggregation & Repo Filtering

### Question 1: Repository Scope
| Option | Description | Selected |
|--------|-------------|----------|
| Owned public non-fork | Pure personal contributions, avoids counting upstream codebase lines | ✓ |
| Owned + contributing forks | More comprehensive, but requires branch commit filtering | |
| All public and private | Accurate total, but requires private repo token scope | |

**User's choice:** Owned public non-fork repositories only.
**Notes:** Reflects pure personal authored projects without polluting stats with upstream forks.

### Question 2: Archived Repositories
| Option | Description | Selected |
|--------|-------------|----------|
| Include archived | Reflects true lifetime authored code volume across entire GitHub history | ✓ |
| Exclude archived | Only count active, non-archived projects | |

**User's choice:** Include archived repositories.
**Notes:** Author's historical LOC represents total lifetime contribution.

### Question 3: Outlier & Exclusion Handling
| Option | Description | Selected |
|--------|-------------|----------|
| Configurable exclude list | Supports an optional 'exclude_repos' array for dataset/vendor repos (default empty) | ✓ |
| No exclusion list | Sum all qualifying repos directly without custom filters | |
| Auto-clamp commits | Exclude commits exceeding 50,000 LOC | |

**User's choice:** Configurable exclude list in config (`exclude_repos` array).
**Notes:** Gives developer full control over any dataset/vendor outliers.

### Question 4: LOC Formatting
| Option | Description | Selected |
|--------|-------------|----------|
| Full comma-separated integers | '++320,410 / --85,240' (exact counts, strictly matches current SVG format) | ✓ |
| Metric abbreviation | '++320.4k / --85.2k' (compact) | |

**User's choice:** Full comma-separated integer: '++320,410 / --85,240'.
**Notes:** Strictly matches terminal Neofetch aesthetic and Phase 1 card.

---

## SVG Update Architecture

### Question 1: SVG Update Strategy
| Option | Description | Selected |
|--------|-------------|----------|
| Generator re-render | update_profile.py imports and calls generate_hero.py with dynamic values | ✓ |
| In-place XML patching | Directly parse assets/hero.svg and replace inner text of DOM IDs | |

**User's choice:** Generator re-render: `update_profile.py` imports and calls `generate_hero.py` with dynamic values.
**Notes:** Avoids fragile regex/DOM string manipulation. `generate_hero.py` remains single source of truth for SVG template while preserving DOM IDs (`val-uptime`, etc.).

### Question 2: Pre-Write SVG Validation
| Option | Description | Selected |
|--------|-------------|----------|
| Strict ElementTree parse | Validate well-formedness with xml.etree.ElementTree before writing to disk | ✓ |
| Basic string assertions | Verify closing tags and viewBox | |

**User's choice:** Strict ElementTree XML parse check before writing to disk.
**Notes:** Prevents corrupt or invalid XML from ever reaching git.

### Question 3: Idempotent File Writing
| Option | Description | Selected |
|--------|-------------|----------|
| Idempotent check | If generated content is identical to existing SVG, skip file write | ✓ |
| Always overwrite | Always write to assets/hero.svg on every script invocation | |

**User's choice:** Idempotent check: If generated content is identical to existing SVG, skip file write.
**Notes:** Eliminates empty git diffs and useless commits when metrics haven't changed.

### Question 4: Console Output & Logging
| Option | Description | Selected |
|--------|-------------|----------|
| Terminal-styled console output | Clean ANSI status lines ([OK], [INFO], metrics summary) matching terminal theme | ✓ |
| Minimal quiet output | Single-line confirmation or silent exit | |

**User's choice:** Terminal-styled console output: Clean ANSI status lines matching workstation terminal theme.
**Notes:** Consistent CLI developer experience.

---

## Local Development & Token Handling

### Question 1: Credential Resolution
| Option | Description | Selected |
|--------|-------------|----------|
| Multi-source | GITHUB_TOKEN or GH_TOKEN env vars, with fallback to local gitignored .env file | ✓ |
| Strict env var | GITHUB_TOKEN environment variable only | |
| CLI flag | Support --token flag | |

**User's choice:** Multi-source: `GITHUB_TOKEN` or `GH_TOKEN` env vars, with fallback to local gitignored `.env` file.
**Notes:** Seamless both in local development and GitHub Actions runner environments.

### Question 2: Behavior on Missing Token
| Option | Description | Selected |
|--------|-------------|----------|
| Dry-run / mock fallback | Warn on missing token and fall back to cached data or offline test fixtures | ✓ |
| Strict error exit | Exit with non-zero code | |

**User's choice:** Dry-run / mock fallback: Warn on missing token and fall back to cached data or offline test fixtures without crashing.
**Notes:** Offline testing and local verification work out-of-the-box.

### Question 3: Rate Limiting & Transient Retries
| Option | Description | Selected |
|--------|-------------|----------|
| Exponential backoff | Check X-RateLimit-Remaining and Retry-After headers, retry up to 3 times | ✓ |
| Single retry | Fixed 5s delay | |

**User's choice:** Exponential backoff with RateLimit inspection (up to 3 retries).
**Notes:** High reliability in CI against API throttling.

### Question 4: Test Suite Validation
| Option | Description | Selected |
|--------|-------------|----------|
| Pure offline mock fixtures | Pytest suite uses fixture JSONs simulating GitHub GraphQL responses | ✓ |
| Hybrid live test | Mock tests + live test when token is available | |

**User's choice:** Pure offline mock fixtures: Pytest suite uses fixture JSONs simulating GitHub GraphQL responses.
**Notes:** 100% deterministic, zero API rate limits burned in tests.

---

## the agent's Discretion

- Simplification of baseline discovery to query `contributionsCollection.contributionYears` and earliest year contribution before falling back to `createdAt`.
- Tracking `data/cache.json` in git so daily GitHub Actions runners retain persistent baseline without re-querying.
- Incremental sync checking `pushedAt` on repositories to only fetch commit additions/deletions on changed repos.
- Pure standard library `.env` parsing (no external pip dependencies).

## Deferred Ideas

- Phase 3: Live open source projects dashboard with PR/Issue counts.
- Phase 4: Top languages distribution progress bar and git activity log stream.
- Phase 5: Categorized Skills Matrix and plug-and-play blog section.
- Phase 6: Daily scheduled GitHub Actions workflow.
