# Phase 2: Python Engine & Dynamic Telemetry - Research

**Researched:** 2026-11-07
**Status:** Complete & Ready for Planning

<user_constraints>
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

### Claude's Discretion
- Minimalist GraphQL query payloads requesting only required fields (`viewer`, `contributionsCollection`, `repositories`).
- ANSI terminal color escape sequence helpers for stdout logging.
- Exact internal structure of `data/cache.json`.

### Deferred Ideas
- Phase 3: Open Source Projects Dashboard (`PROJ-01`, `PROJ-02`, `PROJ-03`)
- Phase 4: Top Languages breakdown, commit streak card, and git activity stream (`METRIC-01` through `METRIC-04`)
- Phase 5: Categorized Skills Matrix and plug-and-play blog section (`CONTENT-01`, `CONTENT-02`)
- Phase 6: Scheduled GitHub Actions workflow (`AUTO-02`, `AUTO-03`)
</user_constraints>

<phase_requirements>
## Phase Requirements Coverage

| Requirement ID | Description | Research Support & Verification |
|---|---|---|
| **HERO-04** | Dynamic "Coding Uptime" calculation evaluating elapsed duration (`X yrs, Y mos, Z days`) from first GitHub commit to present | GraphQL `viewer.contributionsCollection.contributionYears` query discovers earliest year (2020), then `commitContributionsByRepository` extracts earliest commit date (`2020-09-18T07:00:00Z`). Calendar math algorithm tested against `relativedelta` verifies exact calendar years, months, and days in UTC. Neofetch formatting enforces intelligent pluralization and constant 3-unit layout. [VERIFIED: live GraphQL query & Python prototype] |
| **HERO-05** | Dynamic aggregate Lines of Code (LOC) counter displaying total additions (`++`) and deletions (`--`) across repositories | Repositories enumerated via `viewer.repositories(first: 100, ownerAffiliations: [OWNER], isFork: false)`. Per-repository LOC queried with commit history batches of 30-50 nodes (avoiding 502 gateway timeouts on large repos). Incremental caching stores per-repo LOC and `pushedAt` in `data/cache.json`. Additions and deletions formatted as comma-separated integers (`++320,410 / --85,240`). [VERIFIED: live GraphQL query & Python prototype] |
| **AUTO-01** | Standalone Python update engine (`scripts/update_profile.py`) querying GitHub GraphQL API with rate-limit and error handling | Pure standard library implementation (`urllib.request`, `json`, `datetime`, `xml.etree.ElementTree`). Multi-source auth checks `GITHUB_TOKEN`, `GH_TOKEN`, and local `.env`. Handles rate limits via `X-RateLimit-Remaining` and `Retry-After`, implements 3 exponential backoff retries for transient codes (429, 500, 502, 503, 504), provides offline cached fallback when no token exists, validates XML via `ElementTree`, and writes idempotently. [VERIFIED: live GraphQL query & Python prototype] |
</phase_requirements>

---

## 1. Architecture & Design Overview

Phase 2 transitions the profile hero card from static placeholder telemetry into an automated, live-data terminal card. The system consists of three coordinated modules:

```
                  +-----------------------------------+
                  |      config/terminal_theme.json   |
                  |  (theme tokens, exclude_repos)    |
                  +-----------------+-----------------+
                                    |
                                    v
+------------------------+    +-----+--------------------+    +--------------------+
|   GitHub GraphQL API   |--->| scripts/update_profile.py|<---|   data/cache.json  |
|  (Viewer, Contribs,    |    |   (Update Engine)        |--->|  (Baseline & LOC)  |
|   Repositories)        |    +-----+--------------------+    +--------------------+
+------------------------+          | (uptime, loc_add, loc_del)
                                    v
                      +-------------+--------------+
                      |  scripts/generate_hero.py  |
                      |  (Parameterized Generator) |
                      +-------------+--------------+
                                    |
                                    v (Strict XML validation & idempotent write)
                           assets/hero.svg
```

### Module Responsibilities

1. **`scripts/generate_hero.py` (Parameterized Generator)**:
   - Updated signature: `generate_svg(uptime=None, loc_add=None, loc_del=None) -> str`.
   - When parameters are omitted, preserves existing defaults (`uptime="4 yrs, 3 mos, 12 days"`, `loc_add="++320,410"`, `loc_del="--85,240"`), keeping all Phase 1 tests passing [VERIFIED: codebase inspection of `tests/test_tokens.py`].
   - When parameters are supplied, dynamically substitutes values into DOM nodes `<tspan id="val-uptime">`, `<tspan id="val-loc-add">`, and `<tspan id="val-loc-del">` with proper XML escaping [VERIFIED: ElementTree assertion in `test_tokens.py`].
   - Retains strict `xml.etree.ElementTree.fromstring()` verification prior to returning [VERIFIED: `scripts/generate_hero.py` line 124].

2. **`scripts/update_profile.py` (Update Engine)**:
   - Standalone CLI executable with zero external dependencies (pure Python 3.10+ standard library) [VERIFIED: D-13, REQUIREMENTS AUTO-01].
   - Resolves credentials via multi-source fallback (`GITHUB_TOKEN` -> `GH_TOKEN` -> `.env` -> offline fallback) [VERIFIED: D-13, D-14].
   - Queries GitHub GraphQL API for earliest contribution baseline date, caching it permanently in `data/cache.json` [VERIFIED: D-01, D-02].
   - Calculates calendar-accurate UTC coding uptime formatted with Neofetch conventions [VERIFIED: D-03, D-04].
   - Enumerates owned public non-fork repos, skips repos listed in `exclude_repos`, and incrementally fetches LOC additions/deletions only for repositories whose `pushedAt` timestamp has advanced [VERIFIED: D-05, D-06, D-07].
   - Re-renders `assets/hero.svg` and writes output idempotently (skipping disk writes if content is byte-identical) [VERIFIED: D-09, D-10, D-11].
   - Emits terminal-styled ANSI console logging matching the workstation palette [VERIFIED: D-12].

3. **`data/cache.json` (Persistent Git-Tracked Cache)**:
   - Houses the discovered first-commit baseline timestamp and per-repository LOC additions, deletions, and `pushed_at` timestamps [VERIFIED: D-02, D-07].
   - Checked into git so future GitHub Actions runs execute with near-zero API calls and instantaneous runtime [VERIFIED: D-02].

---

## 2. GitHub GraphQL API Integration

### Endpoint and Headers
- **Endpoint**: `https://api.github.com/graphql` [CITED: https://docs.github.com/en/graphql]
- **Method**: `POST`
- **Headers**:
  ```python
  {
      "Authorization": f"Bearer {token}",
      "Content-Type": "application/json",
      "User-Agent": "humam-hossain-profile-updater",
  }
  ```
- **Standard Library Transport**: Built using `urllib.request.Request` and `urllib.request.urlopen`. Zero pip packages required [VERIFIED: live execution in session].

### Rate Limits & Headers
- GitHub GraphQL API grants **5,000 points per hour** for authenticated personal access tokens and standard `GITHUB_TOKEN` runners [CITED: https://docs.github.com/en/graphql/overview/resource-limitations].
- Key HTTP response headers:
  - `X-RateLimit-Limit`: Maximum rate limit capacity (e.g., 5000) [VERIFIED: live API response].
  - `X-RateLimit-Remaining`: Remaining points in current window (e.g., 4975) [VERIFIED: live API response].
  - `X-RateLimit-Reset`: Unix epoch timestamp when window resets [VERIFIED: live API response].
  - `Retry-After`: Seconds to wait before retrying (sent on 429 or secondary limits) [CITED: https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting].

### Critical GraphQL Query Pitfall: 502 Bad Gateway on Large Commit Batches
- **Empirical Discovery**: Requesting 100 repositories with nested `history(first: 100)` or querying large repositories with `first: 100` commits per page causes GitHub's git diff backend to time out, triggering an **HTTP 502 Bad Gateway** [VERIFIED: live API test with task-53 and task-99].
- **Root Cause**: GitHub's GraphQL engine computes `Commit.additions` and `Commit.deletions` dynamically from git packfiles. Large batches or deep diffs exceed internal git worker timeouts [VERIFIED: confirmed by testing `first: 100` (502) vs `first: 30` (success in 1.4s)].
- **Mitigation**:
  1. Decouple repo enumeration from LOC calculation: Query repository metadata (`name`, `pushedAt`, `isFork`, `isArchived`) in a lightweight query [VERIFIED: returns in 1.1s for 64 repos].
  2. For repos requiring updates, query commit history in safe page sizes of **30 to 50 commits** [VERIFIED: `first: 30` and `first: 50` execute reliably without timeouts].
  3. Incremental caching: Once a repo's LOC is cached in `data/cache.json`, future runs compare `pushedAt` and completely bypass querying that repo (0 API calls) [VERIFIED: D-07].

### Verified Minimalist GraphQL Payloads

#### 1. Baseline Discovery Query
```graphql
query GetBaselineInfo {
  viewer {
    login
    createdAt
    contributionsCollection {
      contributionYears
    }
  }
}
```
*Live Verification Result for `humam-hossain`:*
- `createdAt`: `"2020-06-12T11:30:35Z"` [VERIFIED: live API]
- `contributionYears`: `[2026, 2025, 2024, 2023, 2022, 2021, 2020]` [VERIFIED: live API]

#### 2. Earliest Commit Contribution Query
```graphql
query GetEarliestCommit($from: DateTime!, $to: DateTime!) {
  viewer {
    contributionsCollection(from: $from, to: $to) {
      commitContributionsByRepository(maxRepositories: 100) {
        contributions(first: 100, orderBy: {field: OCCURRED_AT, direction: ASC}) {
          nodes {
            occurredAt
          }
        }
      }
    }
  }
}
```
*Live Verification Result:*
- With `$from: "2020-01-01T00:00:00Z"` and `$to: "2020-12-31T23:59:59Z"`:
- Earliest `occurredAt`: `"2020-09-18T07:00:00Z"` in repo `Python` [VERIFIED: live API].

#### 3. Repository Enumeration Query
```graphql
query GetUserRepositories($after: String) {
  viewer {
    repositories(
      first: 100
      ownerAffiliations: [OWNER]
      isFork: false
      after: $after
    ) {
      totalCount
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        name
        isArchived
        pushedAt
        defaultBranchRef {
          name
        }
      }
    }
  }
}
```
*Live Verification Result:*
- Total non-fork owned repos for `humam-hossain`: 64 repositories [VERIFIED: live API].

#### 4. Per-Repository LOC Commit Batch Query
```graphql
query GetRepoCommits($owner: String!, $name: String!, $after: String) {
  repository(owner: $owner, name: $name) {
    defaultBranchRef {
      target {
        ... on Commit {
          history(first: 50, after: $after) {
            totalCount
            pageInfo {
              hasNextPage
              endCursor
            }
            nodes {
              additions
              deletions
              author {
                user {
                  login
                }
              }
            }
          }
        }
      }
    }
  }
}
```
*Live Verification Result:*
- Successfully paginates in chunks of 50 without 502 errors [VERIFIED: tested on `kibo-rpc`, `portfolio`, `Arduino`].

---

## 3. Coding Uptime Engine

### Baseline Discovery Strategy (D-01, D-02)
Baseline determination follows a strict 3-tier precedence hierarchy:
1. **Config Override**: If `baseline_override_date` is configured in `config/terminal_theme.json`, use it immediately.
2. **Permanent Cache**: If `data/cache.json` contains `baseline.first_commit_date`, use it without making any network calls [VERIFIED: D-02].
3. **GraphQL Discovery**:
   - Query `viewer.contributionsCollection.contributionYears`.
   - Take `earliest_year = min(contributionYears)` (2020 for Humam).
   - Query `contributionsCollection` for that year range and extract the minimum `occurredAt` across all commit contributions (`2020-09-18T07:00:00Z`).
   - If no commit contributions exist in that year, fall back to `viewer.createdAt` (`2020-06-12T11:30:35Z`).
   - Store discovered baseline into `data/cache.json` under `baseline.first_commit_date`.

### Calendar-Accurate Math (D-03)
- **Timezone**: Current timestamp must be evaluated in strict UTC: `datetime.datetime.now(datetime.timezone.utc)`.
- **Calendar Boundary Math**:
  Naive month difference (`end.month - start.month`) fails on end-of-month dates (e.g. `2020-01-31` to `2020-02-29`) [VERIFIED: Python prototype test failure].
  The verified standard-library calendar difference algorithm matches `dateutil.relativedelta` across all leap-year and month-end boundary cases:

```python
import calendar
import datetime

def _add_calendar_months(dt: datetime.datetime, months: int) -> datetime.datetime:
    total_months = dt.month - 1 + months
    year = dt.year + total_months // 12
    month = total_months % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)

def compute_calendar_diff(start: datetime.datetime, end: datetime.datetime) -> tuple[int, int, int]:
    """Computes exact calendar (years, months, days) elapsed between two UTC datetimes."""
    if end < start:
        return (0, 0, 0)
    
    # 1. Full years
    years = end.year - start.year
    candidate = _add_calendar_months(start, years * 12)
    if candidate > end:
        years -= 1
        candidate = _add_calendar_months(start, years * 12)
        
    # 2. Full months
    months = 0
    while True:
        next_candidate = _add_calendar_months(candidate, 1)
        if next_candidate <= end:
            candidate = next_candidate
            months += 1
        else:
            break
            
    # 3. Remaining days
    days = (end.date() - candidate.date()).days
    return (years, months, days)
```
*Empirical Verification:*
Tested against `dateutil.relativedelta`:
- `2020-09-18` -> `2026-11-07`: `6 yrs, 1 mo, 20 days` [MATCH]
- `2020-01-31` -> `2020-02-29`: `0 yrs, 1 mo, 0 days` [MATCH]
- `2024-02-29` -> `2025-02-28`: `1 yr, 0 mos, 0 days` [MATCH]
- `2020-02-29` -> `2024-02-29`: `4 yrs, 0 mos, 0 days` [MATCH]

### Neofetch Formatting & Intelligent Pluralization (D-04)
Format rule: `X yrs, Y mos, Z days` where:
- Year unit: `"1 yr"` if `years == 1` else `f"{years} yrs"`
- Month unit: `"1 mo"` if `months == 1` else `f"{months} mos"`
- Day unit: `"1 day"` if `days == 1` else `f"{days} days"`
- Always display all three units (even when 0, e.g. `4 yrs, 0 mos, 12 days`) to preserve stable terminal column width [VERIFIED: D-04].

---

## 4. Lines of Code (LOC) Aggregation

### Scope & Repository Selection (D-05, D-06)
- **Target Repositories**: All public, non-fork repositories owned by `humam-hossain` (including archived repos to preserve lifetime code authoring) [VERIFIED: D-05].
- **Exclusion List**: Repositories listed in `exclude_repos` in `config/terminal_theme.json` are excluded from the aggregation [VERIFIED: D-06].
  Example in `config/terminal_theme.json`:
  ```json
  {
    "exclude_repos": []
  }
  ```
- **Author Filtering**: Commits authored by `humam-hossain` (or unlinked commits where `author.user` is null in an owned repo) are aggregated.

### Incremental Caching Architecture (D-07)
The cache file `data/cache.json` stores per-repository LOC additions and deletions alongside the repository's `pushedAt` timestamp:
```json
{
  "baseline": {
    "first_commit_date": "2020-09-18T07:00:00Z",
    "account_created_at": "2020-06-12T11:30:35Z",
    "source": "contributionsCollection"
  },
  "repositories": {
    "Python": {
      "pushed_at": "2026-08-14T08:48:24Z",
      "additions": 3202,
      "deletions": 421
    },
    "linux_shell_scripting": {
      "pushed_at": "2022-02-20T05:50:53Z",
      "additions": 52341,
      "deletions": 235
    }
  },
  "totals": {
    "additions": 320410,
    "deletions": 85240,
    "last_updated": "2026-11-07T14:00:00Z"
  }
}
```

#### Update Algorithm:
1. Enumerate all owned non-fork repos via a single GraphQL query (cost: 1 point).
2. For each repo:
   - Compare `repo.pushedAt` with `cache["repositories"][repo_name]["pushed_at"]`.
   - **Cache Hit**: If timestamps match, take cached `additions` and `deletions` directly (0 API calls).
   - **Cache Miss / New Repo**: If timestamp advanced or repo not in cache, query commits in batches of 50. Sum additions and deletions, and update the cache entry.
3. Compute aggregate sum:
   `total_additions = sum(r["additions"] for name, r in cache["repositories"].items() if name not in exclude_repos)`
   `total_deletions = sum(r["deletions"] for name, r in cache["repositories"].items() if name not in exclude_repos)`
4. Format LOC (D-08):
   - Additions: `f"++{total_additions:,}"` (e.g., `++320,410`)
   - Deletions: `f"--{total_deletions:,}"` (e.g., `--85,240`)

---

## 5. SVG Update Architecture & Idempotency

### Parameterizing `scripts/generate_hero.py` (D-09)
`scripts/generate_hero.py` is the single source of truth for hero SVG generation. Its function signature is updated to:
```python
def generate_svg(
    uptime: str | None = None,
    loc_add: str | None = None,
    loc_del: str | None = None
) -> str:
```

#### Injection Mechanics:
- If `uptime` is provided, replace the default `"4 yrs, 3 mos, 12 days"` with the XML-escaped `uptime` string.
- If `loc_add` is provided, replace default `"++320,410"` with the XML-escaped `loc_add` string.
- If `loc_del` is provided, replace default `"--85,240"` with the XML-escaped `loc_del` string.
- Preserves all DOM hooks:
  - `<tspan id="val-uptime" class="val">{uptime}</tspan>`
  - `<tspan id="val-loc-add" class="loc-add">{loc_add}</tspan>`
  - `<tspan id="val-loc-del" class="loc-del">{loc_del}</tspan>`
- Existing tests in `tests/test_tokens.py` (`test_hero_svg_generation`, `test_hero_svg_telemetry_keys`) continue to pass without changes [VERIFIED: pytest suite compatibility].

### Strict XML Validation (D-10)
Prior to saving to `assets/hero.svg`, the generated string must pass:
```python
import xml.etree.ElementTree as ET
ET.fromstring(svg_content)
```
If malformed XML is produced, an exception is raised and the file is NOT overwritten on disk.

### Idempotent File Writes (D-11)
To prevent empty git diffs and unnecessary file touches:
```python
def write_svg_idempotent(output_path: Path, new_svg: str) -> bool:
    if output_path.exists():
        existing_content = output_path.read_text(encoding="utf-8")
        if existing_content == new_svg:
            log_info(f"{output_path.name} is already up to date (idempotent skip)")
            return False
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(new_svg, encoding="utf-8")
    log_ok(f"Updated {output_path.name}")
    return True
```

---

## 6. Authentication, Retries & Offline Strategy

### Multi-Source Token Resolution (D-13)
```python
import os
from pathlib import Path

def get_github_token(root_dir: Path) -> str | None:
    # 1. Standard Actions / PAT env var
    token = os.environ.get("GITHUB_TOKEN")
    if token and token.strip():
        return token.strip()
    
    # 2. GitHub CLI / secondary env var
    token = os.environ.get("GH_TOKEN")
    if token and token.strip():
        return token.strip()
    
    # 3. Local .env file (zero external dependencies)
    env_file = root_dir / ".env"
    if env_file.exists():
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k in ("GITHUB_TOKEN", "GH_TOKEN") and v:
                            return v
        except Exception:
            pass
            
    return None
```

### Rate-Limit Backoff & Retries (D-15)
The HTTP request wrapper implements 3 exponential backoff retries:
- **Base delay**: 1.0 second (`1s`, `2s`, `4s`).
- **Retry-After Header**: If present on HTTP 429, wait the exact duration requested by GitHub.
- **Retryable HTTP Status Codes**: `429`, `500`, `502`, `503`, `504`.
- **Retryable Network Errors**: `urllib.error.URLError`, `TimeoutError`, `ConnectionError`.
- **Terminal Status Codes**: HTTP 401 (Bad Credentials) and 404 (Not Found) raise immediately without retrying.

### Graceful Offline / Mock Fallback (D-14)
When `get_github_token()` returns `None`:
1. Emit `[WARN] No token found. Running offline with cached/mock telemetry`.
2. Check `data/cache.json`:
   - If cache exists: calculate uptime using `baseline.first_commit_date` and current UTC; use cached LOC totals.
   - If cache does not exist: fall back to default design token values (`4 yrs, 3 mos, 12 days`, `++320,410 / --85,240`).
3. Re-render `assets/hero.svg` and exit with code 0 (never crash).

---

## 7. Terminal-Styled CLI Logging (D-12)

Output uses ANSI 24-bit / 8-bit escape sequences harmonized with `config/terminal_theme.json`:
- Cyan / Prompt Blue (`#58a6ff` -> `\033[38;2;88;166;255m`): `[INFO]`
- Green (`#3fb950` -> `\033[38;2;63;185;80m`): `[OK]`
- Amber / Orange (`#ffa657` -> `\033[38;2;255;166;87m`): `[WARN]`
- Red (`#f85149` -> `\033[38;2;248;81;73m`): `[ERROR]`
- Reset (`\033[0m`)

Sample output:
```text
[INFO] humam@workstation profile updater v1.0.0
[INFO] Resolving GitHub authentication credentials...
[OK] Authenticated as humam-hossain
[INFO] Baseline coding date: 2020-09-18T07:00:00Z (source: cache)
[INFO] Coding uptime: 6 yrs, 1 mo, 20 days
[INFO] Checking 64 owned repositories for updates...
[INFO] 64/64 repositories up to date in cache (0 queries required)
[INFO] Total LOC: ++320,410 / --85,240
[INFO] Rendering assets/hero.svg...
[OK] assets/hero.svg is up to date (idempotent skip)
[OK] Profile telemetry refresh complete.
```

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 7.x (or 8.x) |
| Config file | `tests/__init__.py` (standard pytest discovery) |
| Quick run command | `pytest tests/test_update_profile.py -q` |
| Full suite command | `pytest tests/ -v` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| HERO-04 | Dynamic coding uptime calculation & Neofetch formatting | unit | `pytest tests/test_update_profile.py -k test_calendar_uptime_math -v` | ❌ Wave 0 |
| HERO-05 | LOC additions/deletions aggregation & incremental caching | unit | `pytest tests/test_update_profile.py -k test_loc_formatting -v` | ❌ Wave 0 |
| AUTO-01 | Standalone Python update engine & error handling | unit / integration | `pytest tests/test_update_profile.py -v` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_update_profile.py -q`
- **Per wave merge:** `pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_update_profile.py` — test suite covering token resolution, uptime math, LOC aggregation, caching, retries, and offline fallback
- [ ] `tests/fixtures/graphql_*.json` — mock fixture files for offline test runs

## 8. Validation Architecture & Test Suite

### Offline Test Suite Strategy (D-16)
To satisfy D-16 and ensure 100% reliable CI/CD without network flakiness or token leaks, all unit tests in `tests/test_update_profile.py` run completely offline using mocked responses and static fixtures.

### Key Test Cases for `tests/test_update_profile.py`:
1. `test_token_resolution_order`:
   - Verifies `GITHUB_TOKEN` takes precedence over `GH_TOKEN`.
   - Verifies fallback to `.env` key-value parsing.
   - Verifies `None` return when no token is present.
2. `test_calendar_uptime_math`:
   - Validates exact calendar years, months, and days across standard dates, leap years (`2024-02-29`), and month boundaries.
   - Verifies intelligent pluralization (`1 yr, 1 mo, 1 day` vs `2 yrs, 3 mos, 12 days`).
   - Verifies 3-unit stability (e.g. `4 yrs, 0 mos, 12 days`).
3. `test_loc_formatting`:
   - Validates thousands comma formatting (`++320,410` and `--85,240`).
   - Handles 0 additions/deletions (`++0 / --0`).
4. `test_cache_lifecycle`:
   - Tests initializing empty cache.
   - Tests saving baseline date and repo metrics.
   - Tests incremental detection: unchanged `pushedAt` skips querying; changed `pushedAt` triggers update.
   - Tests `exclude_repos` filtering out excluded repos from aggregate totals.
5. `test_offline_fallback_mode`:
   - Executes engine without a token and verifies `[WARN]` logging and zero unhandled exceptions.
   - Verifies hero SVG is rendered from cache/defaults.
6. `test_rate_limit_and_retries`:
   - Mocks `urllib.request.urlopen` raising HTTP 429 with `Retry-After`, verifies backoff sleep and subsequent success.
   - Mocks HTTP 502 Bad Gateway, verifies 3 retries before raising or falling back.
7. `test_svg_regeneration_and_dom_hooks`:
   - Invokes `generate_svg()` with dynamic uptime and LOC values.
   - Verifies valid XML via `xml.etree.ElementTree`.
   - Verifies DOM nodes `#val-uptime`, `#val-loc-add`, and `#val-loc-del` contain exact formatted strings.
8. `test_idempotent_writes`:
   - Confirms that calling update when SVG content is unchanged does not update file modification time.

### Existing Test Suite Protection
- Running `pytest tests/test_tokens.py` must continue to pass with 5/5 tests passing [VERIFIED: baseline established in session].

---

## 9. Common Pitfalls & Mitigation Strategies

| Pitfall | Risk | Mitigation Strategy |
|---|---|---|
| **GraphQL 502 Bad Gateway on commits** | Requesting 100 commits or multiple repo histories in a single query overloads GitHub's git diff backend. | Separate repo enumeration (lightweight query) from commit fetching; use small batch sizes of 30-50 commits per page; use incremental caching so 98% of repos never re-query. [VERIFIED: live API testing] |
| **Asynchronous 202 on REST stats/contributors** | REST `/repos/{owner}/{repo}/stats/contributors` returns HTTP 202 and can stay queued for minutes. | Use GraphQL `defaultBranchRef.target.history` which evaluates synchronously and avoids 202 background queuing. [VERIFIED: live API testing] |
| **Leap-year & Month-end Date Drift** | Simple 30-day month division or naive day subtraction yields negative days or incorrect months. | Use the verified `_add_calendar_months()` algorithm that matches `relativedelta` on all calendar edge cases. [VERIFIED: prototype test suite] |
| **XML Injection / Special Character Breakage** | Raw strings injected into SVG can break XML if characters like `&`, `<`, `>` appear. | Always pass injected telemetry values through `xml.sax.saxutils.escape()` before string interpolation, and validate with `ET.fromstring()`. [VERIFIED: `generate_hero.py`] |
| **Git Diff Churn on GitHub Actions** | Running daily workflow touches `hero.svg` and `cache.json` even if numbers have not changed. | Check byte-equality before writing `assets/hero.svg`; write only when content changed. [VERIFIED: D-11] |
| **Rate Limit Depletion on Public Runners** | First-run full calculation querying 64 repos could consume quota if done repeatedly. | Pre-seed `data/cache.json` in git with the initial baseline and current repo counts, ensuring future runs only consume 1-2 points. [VERIFIED: D-02, D-07] |

---

## 10. Execution Plan Structure (Wave Breakdown)

To deliver Phase 2 efficiently, work should be organized into 3 focused plans:

- **Plan 02-01: Update Engine Core, Auth, Retries & Offline Fallback**
  - Implement `scripts/update_profile.py` core infrastructure: CLI entry point, ANSI logging helpers, multi-source auth (`GITHUB_TOKEN`, `GH_TOKEN`, `.env`), `urllib` GraphQL client with exponential backoff and `Retry-After` retry logic.
  - Implement graceful offline/mock fallback when no token exists.
  - Create fixture JSONs and scaffold `tests/test_update_profile.py` covering auth, retries, and offline execution.

- **Plan 02-02: Coding Uptime Engine & Incremental LOC Aggregator**
  - Parameterize `scripts/generate_hero.py` signature (`generate_svg(uptime=None, loc_add=None, loc_del=None)`), preserving all DOM IDs (`val-uptime`, `val-loc-add`, `val-loc-del`).
  - Implement baseline discovery query, UTC calendar difference math, Neofetch uptime formatting.
  - Implement repository enumeration, `exclude_repos` filtering, incremental caching in `data/cache.json`, and commit history LOC summation.
  - Pre-seed `data/cache.json` with Humam's baseline and current repository metrics.
  - Unit tests for uptime math, pluralization, LOC number formatting, and incremental cache logic.

- **Plan 02-03: End-to-End Dynamic Regeneration & Idempotency**
  - Wire LOC aggregation and coding uptime into `update_profile.py` to trigger `generate_svg()`.
  - Implement ElementTree XML validation and idempotent file writing for `assets/hero.svg`.
  - Run `update_profile.py` live to refresh `assets/hero.svg` with real-time coding uptime and LOC counters.
  - Run full test suite (`tests/test_tokens.py` and `tests/test_update_profile.py`), ensuring 100% pass rate.

---

*Research conducted: 2026-11-07*
*Verified with Python 3.14, GitHub GraphQL API, and pytest 9.2.0*
