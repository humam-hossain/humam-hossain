#!/usr/bin/env python3
"""
scripts/update_profile.py
Automated profile telemetry engine for Muhammed Humam Hossain (humam-hossain).
Standard library only: urllib, json, datetime, xml, calendar, pathlib.
Zero external dependencies.
"""

from __future__ import annotations

import calendar
import datetime
import json
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from scripts.generate_hero import generate_svg
except (ImportError, ModuleNotFoundError):
    from generate_hero import generate_svg

try:
    from scripts.generate_projects import generate_projects_svg, DEFAULT_PROJECT_FIXTURES
except (ImportError, ModuleNotFoundError):
    from generate_projects import generate_projects_svg, DEFAULT_PROJECT_FIXTURES

CONFIG_PATH = ROOT_DIR / "config" / "terminal_theme.json"
PROJECTS_CONFIG_PATH = ROOT_DIR / "config" / "projects.json"
CACHE_PATH = ROOT_DIR / "data" / "cache.json"
HERO_SVG_PATH = ROOT_DIR / "assets" / "hero.svg"
PROJECTS_SVG_PATH = ROOT_DIR / "assets" / "projects.svg"
README_PATH = ROOT_DIR / "README.md"
GRAPHQL_ENDPOINT = "https://api.github.com/graphql"

# ANSI escape codes matching workstation palette
ANSI_BLUE = "\033[38;2;88;166;255m"   # #58a6ff (Prompt Blue)
ANSI_GREEN = "\033[38;2;63;185;80m"   # #3fb950 (Additions Green)
ANSI_AMBER = "\033[38;2;255;166;87m"  # #ffa657 (Key Amber)
ANSI_RED = "\033[38;2;248;81;73m"     # #f85149 (Deletions Red)
ANSI_RESET = "\033[0m"


def log_info(msg: str) -> None:
    """Logs informational message in prompt blue."""
    print(f"{ANSI_BLUE}[INFO]{ANSI_RESET} {msg}")


def log_ok(msg: str) -> None:
    """Logs success message in additions green."""
    print(f"{ANSI_GREEN}[OK]{ANSI_RESET} {msg}")


def log_warn(msg: str) -> None:
    """Logs warning message in key amber."""
    print(f"{ANSI_AMBER}[WARN]{ANSI_RESET} {msg}")


def log_err(msg: str) -> None:
    """Logs error message in deletions red."""
    print(f"{ANSI_RED}[ERROR]{ANSI_RESET} {msg}", file=sys.stderr)


def get_github_token(root_dir: Path) -> str | None:
    """
    Resolves GitHub token in strict priority order:
    1. GITHUB_TOKEN environment variable
    2. GH_TOKEN environment variable
    3. .env file in root directory (stdlib parser)
    Returns None if no token is found.
    Never exposes or logs token values.
    """
    token = os.environ.get("GITHUB_TOKEN")
    if token and token.strip():
        return token.strip()

    token = os.environ.get("GH_TOKEN")
    if token and token.strip():
        return token.strip()

    env_path = root_dir / ".env"
    if env_path.is_file():
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k == "GITHUB_TOKEN" and v:
                            return v
                        if k == "GH_TOKEN" and v:
                            return v
        except Exception as e:
            log_warn(f"Failed to read .env file: {e}")

    return None


def execute_graphql(
    query: str,
    variables: dict | None = None,
    token: str | None = None,
    max_retries: int = 3,
) -> dict:
    """
    Executes a GitHub GraphQL query with backoff and rate-limit handling.
    Raises RuntimeError on non-retryable errors or after retries exhausted.
    """
    if not token:
        raise ValueError("Cannot execute GraphQL query without an authentication token.")

    payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    req = urllib.request.Request(
        GRAPHQL_ENDPOINT,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "humam-hossain-profile-updater",
        },
        method="POST",
    )

    delay = 1.0
    for attempt in range(max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                headers = resp.headers
                body = resp.read().decode("utf-8")
                data = json.loads(body)

                if "errors" in data and not data.get("data"):
                    raise RuntimeError(f"GraphQL Errors: {data['errors']}")

                remaining = headers.get("X-RateLimit-Remaining")
                if remaining is not None and int(remaining) < 100:
                    log_warn(f"GitHub API Rate Limit low: {remaining} requests remaining")

                return data

        except urllib.error.HTTPError as e:
            status = e.code
            retry_after = e.headers.get("Retry-After") if e.headers else None

            if status in (429, 500, 502, 503, 504) and attempt < max_retries:
                sleep_sec = float(retry_after) if retry_after else delay
                log_warn(f"HTTP {status}. Retrying in {sleep_sec:.1f}s (Attempt {attempt + 1}/{max_retries})...")
                time.sleep(sleep_sec)
                delay *= 2.0
                continue
            raise RuntimeError(f"GitHub API HTTP error {status}: {e.reason}")

        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if attempt < max_retries:
                log_warn(f"Network error: {e}. Retrying in {delay:.1f}s...")
                time.sleep(delay)
                delay *= 2.0
                continue
            raise RuntimeError(f"Network error after {max_retries} retries: {e}")

    raise RuntimeError("Max retries exceeded")


def _add_calendar_months(dt: datetime.datetime, months: int) -> datetime.datetime:
    """Adds integer calendar months to dt, clamping to the last valid day of the target month."""
    total_months = dt.month - 1 + months
    year = dt.year + total_months // 12
    month = total_months % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def compute_calendar_diff(start: datetime.datetime, end: datetime.datetime) -> tuple[int, int, int]:
    """
    Computes exact calendar (years, months, days) elapsed between two UTC datetimes.
    Matches dateutil.relativedelta behavior across leap years and month boundaries.
    """
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


def format_uptime_neofetch(years: int, months: int, days: int) -> str:
    """
    Formats elapsed duration adhering to Neofetch style:
    - Intelligent pluralization ('1 yr' vs '2 yrs', '1 mo' vs '3 mos', '1 day' vs '12 days')
    - Stable 3-unit layout (e.g. '4 yrs, 0 mos, 12 days')
    """
    yr_str = "1 yr" if years == 1 else f"{years} yrs"
    mo_str = "1 mo" if months == 1 else f"{months} mos"
    day_str = "1 day" if days == 1 else f"{days} days"
    return f"{yr_str}, {mo_str}, {day_str}"


def parse_iso_datetime(iso_str: str) -> datetime.datetime:
    """Parses ISO timestamp string into UTC timezone-aware datetime."""
    clean_str = iso_str.replace("Z", "+00:00")
    dt = datetime.datetime.fromisoformat(clean_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone.utc)


def get_baseline_date(config: dict, cache: dict, token: str | None = None) -> datetime.datetime:
    """
    Resolves baseline start date in priority order:
    1. config.telemetry.baseline_override_date
    2. cache.baseline.first_commit_date
    3. GraphQL discovery query (earliest commit contribution or createdAt)
    4. Fallback default (2020-09-18T07:00:00Z)
    """
    # 1. Config override
    override = config.get("telemetry", {}).get("baseline_override_date")
    if override:
        return parse_iso_datetime(override)

    # 2. Cached baseline
    cached_date = cache.get("baseline", {}).get("first_commit_date")
    if cached_date:
        return parse_iso_datetime(cached_date)

    # 3. GraphQL discovery
    if token:
        try:
            baseline_info_query = """
            query GetBaselineInfo {
              viewer {
                login
                createdAt
                contributionsCollection {
                  contributionYears
                }
              }
            }
            """
            data = execute_graphql(baseline_info_query, token=token)
            viewer = data.get("data", {}).get("viewer", {})
            contrib_years = viewer.get("contributionsCollection", {}).get("contributionYears", [])
            created_at_str = viewer.get("createdAt")

            if contrib_years:
                earliest_year = min(contrib_years)
                commit_query = """
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
                """
                c_vars = {
                  "from": f"{earliest_year}-01-01T00:00:00Z",
                  "to": f"{earliest_year}-12-31T23:59:59Z",
                }
                c_data = execute_graphql(commit_query, variables=c_vars, token=token)
                repos = (
                    c_data.get("data", {})
                    .get("viewer", {})
                    .get("contributionsCollection", {})
                    .get("commitContributionsByRepository", [])
                )
                occurred_dates = []
                for repo in repos:
                    for node in repo.get("contributions", {}).get("nodes", []):
                        if "occurredAt" in node:
                            occurred_dates.append(node["occurredAt"])

                if occurred_dates:
                    earliest_commit = min(occurred_dates)
                    cache.setdefault("baseline", {})["first_commit_date"] = earliest_commit
                    cache["baseline"]["source"] = "contributionsCollection"
                    if created_at_str:
                        cache["baseline"]["account_created_at"] = created_at_str
                    return parse_iso_datetime(earliest_commit)

            if created_at_str:
                cache.setdefault("baseline", {})["first_commit_date"] = created_at_str
                cache["baseline"]["account_created_at"] = created_at_str
                cache["baseline"]["source"] = "createdAt"
                return parse_iso_datetime(created_at_str)
        except Exception as e:
            log_warn(f"Failed to discover baseline via GraphQL: {e}. Falling back to default.")

    # 4. Default fallback
    return parse_iso_datetime("2020-09-18T07:00:00Z")


def format_loc_counts(additions: int, deletions: int) -> tuple[str, str]:
    """Formats LOC integers with commas and directional symbols."""
    return f"++{additions:,}", f"--{deletions:,}"


def load_cache(cache_path: Path) -> dict:
    """Safely loads cache JSON with default fallback on missing or corrupted file."""
    if cache_path.is_file():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log_warn(f"Cache corrupt or unreadable: {e}. Starting fresh.")
    return {
        "baseline": {
            "first_commit_date": "2020-09-18T07:00:00Z",
            "account_created_at": "2020-06-12T11:30:35Z",
            "source": "cache_fallback",
        },
        "repositories": {},
        "totals": {
            "additions": 320410,
            "deletions": 85240,
            "last_updated": "2026-11-07T14:00:00Z",
        },
        "project_metrics": {
            "last_updated": "2026-11-07T17:48:25Z",
            "projects": [],
        },
    }


def save_cache(cache_path: Path, data: dict) -> None:
    """Writes formatted JSON cache with 2-space indentation."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_curated_projects(config_path: Path) -> list[dict]:
    """
    Loads config/projects.json and normalizes entries to standard dicts:
    {"owner": str, "name": str, "repo": str, "description": str | None, "tag": str | None}.
    """
    if not config_path.is_file():
        log_warn(f"Projects config not found at {config_path}. Using empty list.")
        return []

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        log_warn(f"Failed to parse {config_path}: {e}")
        return []

    items = data.get("projects", [])
    normalized = []
    for item in items:
        if isinstance(item, str):
            parts = item.split("/")
            owner = parts[0] if len(parts) > 1 else "humam-hossain"
            name = parts[-1]
            normalized.append({
                "owner": owner,
                "name": name,
                "repo": f"{owner}/{name}",
                "description": None,
                "tag": None,
            })
        elif isinstance(item, dict):
            repo_str = item.get("repo", "")
            parts = repo_str.split("/") if repo_str else []
            owner = parts[0] if len(parts) > 1 else "humam-hossain"
            repo_name = parts[-1] if parts else (item.get("name") or "")
            name = item.get("name") or repo_name
            normalized.append({
                "owner": owner,
                "name": name,
                "repo": f"{owner}/{repo_name}",
                "description": item.get("description"),
                "tag": item.get("tag"),
            })
    return normalized


def build_batched_projects_query(curated_repos: list[dict]) -> str:
    """
    Constructs a consolidated GraphQL query using indexed aliases ('repo_0', 'repo_1').
    Guarantees syntax safety regardless of repository names (hyphens, dots, underscores).
    """
    fragments = []
    for idx, item in enumerate(curated_repos[:4]):
        owner = item["owner"]
        name = item["name"]
        frag = f"""
        repo_{idx}: repository(owner: "{owner}", name: "{name}") {{
          name
          owner {{ login }}
          description
          stargazerCount
          forkCount
          issues(states: OPEN) {{ totalCount }}
          pullRequests(states: OPEN) {{ totalCount }}
          primaryLanguage {{
            name
            color
          }}
          repositoryTopics(first: 5) {{
            nodes {{
              topic {{ name }}
            }}
          }}
          url
        }}"""
        fragments.append(frag)

    return "query GetFeaturedProjects {\n" + "\n".join(fragments) + "\n}"


def fetch_project_telemetry(
    curated_repos: list[dict],
    cache: dict,
    token: str | None = None,
) -> list[dict]:
    """
    Fetches project metrics via GraphQL query with indexed aliases.
    On network or token absence, falls back to cache['project_metrics'].
    If cache is empty, falls back to static fixtures.
    """
    if token and curated_repos:
        try:
            query = build_batched_projects_query(curated_repos)
            res = execute_graphql(query=query, token=token)
            data = res.get("data", {})

            projects_out = []
            for idx, c_repo in enumerate(curated_repos[:4]):
                node = data.get(f"repo_{idx}")
                if not node:
                    continue

                lang_obj = node.get("primaryLanguage") or {}
                topic_nodes = node.get("repositoryTopics", {}).get("nodes", [])
                topics = [t["topic"]["name"] for t in topic_nodes if t.get("topic")]

                # Fallback description logic (CONTEXT.md D-14)
                desc = c_repo.get("description") or node.get("description")
                if not desc:
                    desc = " ".join(f"#{t}" for t in topics) if topics else "Open-source software repository"

                projects_out.append({
                    "repo": f"{node.get('owner', {}).get('login', c_repo['owner'])}/{node.get('name', c_repo['name'])}",
                    "name": c_repo.get("name") or node.get("name"),
                    "description": desc,
                    "stars": node.get("stargazerCount", 0),
                    "forks": node.get("forkCount", 0),
                    "open_issues": node.get("issues", {}).get("totalCount", 0),
                    "open_prs": node.get("pullRequests", {}).get("totalCount", 0),
                    "language": lang_obj.get("name", "Plain Text"),
                    "language_color": lang_obj.get("color", "#8b949e"),
                    "topics": topics,
                    "url": node.get("url") or f"https://github.com/{c_repo['owner']}/{c_repo['name']}",
                })

            cache["project_metrics"] = {
                "last_updated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "projects": projects_out,
            }
            return projects_out
        except Exception as e:
            log_warn(f"Failed to fetch project telemetry via GraphQL: {e}. Falling back to cache.")

    # Cache fallback
    cached_projects = cache.get("project_metrics", {}).get("projects")
    if cached_projects:
        return cached_projects

    # Static fixture fallback
    log_warn("No cached project metrics found. Using default fixtures.")
    cache["project_metrics"] = {
        "last_updated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "projects": DEFAULT_PROJECT_FIXTURES,
    }
    return DEFAULT_PROJECT_FIXTURES


DEFAULT_LANGUAGE_FIXTURES = [
    {"name": "Python", "bytes": 65000, "color": "#3572A5", "percentage": 52.0},
    {"name": "Shell", "bytes": 42000, "color": "#89e051", "percentage": 33.6},
    {"name": "C", "bytes": 18000, "color": "#555555", "percentage": 14.4},
]


def aggregate_top_languages(
    repo_nodes: list[dict],
    ignore_list: list[str] | None = None,
) -> list[dict]:
    """
    Aggregates language byte counts across repositories, filters ignored languages,
    and returns top 5 languages + aggregated 'Other' row if remainder >= 1%.
    """
    ignore_set = set(ignore_list if ignore_list is not None else ["HTML", "CSS", "TeX", "Markdown"])
    lang_bytes: dict[str, int] = {}
    lang_colors: dict[str, str] = {}

    for repo in repo_nodes:
        if repo.get("isFork"):
            continue
        lang_conn = repo.get("languages", {})
        edges = lang_conn.get("edges", [])
        for edge in edges:
            node = edge.get("node", {})
            name = node.get("name")
            size = edge.get("size", 0)
            color = node.get("color") or "#8b949e"

            if not name or name in ignore_set:
                continue

            lang_bytes[name] = lang_bytes.get(name, 0) + size
            lang_colors[name] = color

    total_bytes = sum(lang_bytes.values())
    if total_bytes == 0:
        return []

    sorted_langs = sorted(lang_bytes.items(), key=lambda x: x[1], reverse=True)
    top_5 = sorted_langs[:5]
    remainder = sorted_langs[5:]
    remainder_bytes = sum(b for _, b in remainder)

    result = []
    for name, b in top_5:
        pct = (b / total_bytes) * 100.0
        result.append({
            "name": name,
            "bytes": b,
            "color": lang_colors.get(name, "#8b949e"),
            "percentage": round(pct, 1),
        })

    if remainder_bytes > 0:
        rem_pct = (remainder_bytes / total_bytes) * 100.0
        if rem_pct >= 1.0:
            result.append({
                "name": "Other",
                "bytes": remainder_bytes,
                "color": "#8b949e",
                "percentage": round(rem_pct, 1),
            })

    return result


def fetch_language_telemetry(config: dict, cache: dict, token: str | None = None) -> list[dict]:
    """
    Tier 1: Live GraphQL query to viewer.repositories.nodes.languages
    Tier 2: Cache fallback from cache['top_languages']
    Tier 3: DEFAULT_LANGUAGE_FIXTURES
    """
    ignore_list = config.get("telemetry", {}).get("ignore_languages")
    if token:
        try:
            query = """
            query GetTopLanguages {
              viewer {
                repositories(first: 100, isFork: false) {
                  nodes {
                    name
                    isFork
                    languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
                      edges {
                        size
                        node {
                          name
                          color
                        }
                      }
                    }
                  }
                }
              }
            }
            """
            data = execute_graphql(query, token=token)
            nodes = data.get("data", {}).get("viewer", {}).get("repositories", {}).get("nodes", [])
            languages = aggregate_top_languages(nodes, ignore_list=ignore_list)
            if languages:
                cache["top_languages"] = {
                    "last_updated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "languages": languages,
                }
                return languages
        except Exception as e:
            log_warn(f"Failed to fetch language telemetry via GraphQL: {e}. Falling back to cache.")

    cached = cache.get("top_languages", {}).get("languages")
    if cached:
        log_info("Using cached language telemetry from data/cache.json")
        return cached

    log_warn("No cached language telemetry found. Using default fixtures.")
    cache["top_languages"] = {
        "last_updated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "languages": DEFAULT_LANGUAGE_FIXTURES,
    }
    return DEFAULT_LANGUAGE_FIXTURES


DEFAULT_STREAK_FIXTURES = {
    "current_streak": 5,
    "longest_streak": 14,
    "total_contributions": 482,
    "standby": False,
}


def compute_streaks_from_calendar(
    contribution_days: list[dict],
    now_utc: datetime.datetime | None = None,
) -> tuple[int, int, int]:
    """
    Computes (current_streak, longest_streak, total_contributions) from calendar days.
    Implements GitHub today-grace-period: if user committed yesterday, streak is active
    giving until end-of-day UTC today to commit.
    """
    if now_utc is None:
        now_utc = datetime.datetime.now(datetime.timezone.utc)
    today = now_utc.date()
    yesterday = today - datetime.timedelta(days=1)

    sorted_days = sorted(contribution_days, key=lambda d: d["date"])
    day_map = {d["date"]: d.get("contributionCount", 0) for d in sorted_days}
    total_contributions = sum(day_map.values())

    # 1. Longest streak calculation
    longest_streak = 0
    curr_run = 0
    for d in sorted_days:
        if d.get("contributionCount", 0) > 0:
            curr_run += 1
            if curr_run > longest_streak:
                longest_streak = curr_run
        else:
            curr_run = 0

    # 2. Current streak with grace period
    has_today = day_map.get(today.isoformat(), 0) > 0
    has_yesterday = day_map.get(yesterday.isoformat(), 0) > 0

    if not has_today and not has_yesterday:
        return 0, longest_streak, total_contributions

    start_date = today if has_today else yesterday
    current_streak = 0
    check_date = start_date

    while True:
        if day_map.get(check_date.isoformat(), 0) > 0:
            current_streak += 1
            check_date -= datetime.timedelta(days=1)
        else:
            break

    return current_streak, max(longest_streak, current_streak), total_contributions


def fetch_streak_telemetry(cache: dict, token: str | None = None) -> dict:
    """
    Tier 1: Live GraphQL query to contributionsCollection.contributionCalendar
    Tier 2: Cache fallback from cache['streak_metrics']
    Tier 3: DEFAULT_STREAK_FIXTURES
    """
    if token:
        try:
            query = """
            query GetContributionCalendar {
              viewer {
                contributionsCollection {
                  contributionCalendar {
                    totalContributions
                    weeks {
                      contributionDays {
                        date
                        contributionCount
                        color
                      }
                    }
                  }
                }
              }
            }
            """
            data = execute_graphql(query, token=token)
            cal = (
                data.get("data", {})
                .get("viewer", {})
                .get("contributionsCollection", {})
                .get("contributionCalendar", {})
            )
            weeks = cal.get("weeks", [])
            all_days = []
            for week in weeks:
                all_days.extend(week.get("contributionDays", []))

            current, longest, total = compute_streaks_from_calendar(all_days)
            streak_result = {
                "current_streak": current,
                "longest_streak": longest,
                "total_contributions": total,
                "standby": current == 0,
            }
            cache["streak_metrics"] = {
                "last_updated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                **streak_result,
            }
            return streak_result
        except Exception as e:
            log_warn(f"Failed to fetch streak telemetry via GraphQL: {e}. Falling back to cache.")

    cached_streaks = cache.get("streak_metrics")
    if cached_streaks and "current_streak" in cached_streaks:
        log_info("Using cached streak metrics from data/cache.json")
        return cached_streaks

    log_warn("No cached streak metrics found. Using default fixtures.")
    cache["streak_metrics"] = {
        "last_updated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        **DEFAULT_STREAK_FIXTURES,
    }
    return DEFAULT_STREAK_FIXTURES


def aggregate_loc(config: dict, cache: dict, token: str | None = None) -> tuple[int, int]:
    """
    Enumerates owned non-fork repositories and aggregates LOC (additions, deletions).
    Implements incremental caching using pushedAt comparisons.
    Queries commits in batches strictly <= 50 per page.
    Filters out any repository listed in config.telemetry.exclude_repos.
    """
    exclude_repos = set(config.get("telemetry", {}).get("exclude_repos", []))

    if token:
        try:
            repos_query = """
            query GetUserRepositories($after: String) {
              viewer {
                repositories(
                  first: 100
                  ownerAffiliations: [OWNER]
                  isFork: false
                  after: $after
                ) {
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
            """
            after_cursor = None
            all_repo_nodes = []
            while True:
                data = execute_graphql(repos_query, variables={"after": after_cursor}, token=token)
                repos_data = data.get("data", {}).get("viewer", {}).get("repositories", {})
                all_repo_nodes.extend(repos_data.get("nodes", []))
                page_info = repos_data.get("pageInfo", {})
                if page_info.get("hasNextPage"):
                    after_cursor = page_info.get("endCursor")
                else:
                    break

            for node in all_repo_nodes:
                repo_name = node.get("name")
                if not repo_name or repo_name in exclude_repos:
                    continue

                pushed_at = node.get("pushedAt")
                cached = cache.setdefault("repositories", {}).get(repo_name)

                # Incremental Cache Hit
                if cached and cached.get("pushed_at") == pushed_at and "additions" in cached and "deletions" in cached:
                    continue

                # Cache Miss or Updated Repo: query commit history in batches of 50
                default_branch = node.get("defaultBranchRef")
                if not default_branch:
                    cache["repositories"][repo_name] = {
                        "pushed_at": pushed_at,
                        "additions": 0,
                        "deletions": 0,
                    }
                    continue

                commits_query = """
                query GetRepoCommits($name: String!, $after: String) {
                  viewer {
                    repository(name: $name) {
                      defaultBranchRef {
                        target {
                          ... on Commit {
                            history(first: 50, after: $after) {
                              pageInfo {
                                hasNextPage
                                endCursor
                              }
                              nodes {
                                additions
                                deletions
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
                """
                commit_after = None
                repo_adds = 0
                repo_dels = 0
                while True:
                    c_res = execute_graphql(commits_query, variables={"name": repo_name, "after": commit_after}, token=token)
                    repo_obj = c_res.get("data", {}).get("viewer", {}).get("repository")
                    if not repo_obj or not repo_obj.get("defaultBranchRef"):
                        break
                    target = repo_obj["defaultBranchRef"].get("target", {})
                    history = target.get("history", {})
                    for c_node in history.get("nodes", []):
                        repo_adds += c_node.get("additions", 0)
                        repo_dels += c_node.get("deletions", 0)

                    c_page = history.get("pageInfo", {})
                    if c_page.get("hasNextPage"):
                        commit_after = c_page.get("endCursor")
                    else:
                        break

                cache["repositories"][repo_name] = {
                    "pushed_at": pushed_at,
                    "additions": repo_adds,
                    "deletions": repo_dels,
                }
        except Exception as e:
            log_warn(f"Failed to fetch repositories/commits via GraphQL: {e}. Using cached totals.")

    # Aggregate active repositories excluding exclude_repos
    active_repos = cache.get("repositories", {})
    if active_repos:
        total_adds = sum(
            r.get("additions", 0)
            for name, r in active_repos.items()
            if name not in exclude_repos
        )
        total_dels = sum(
            r.get("deletions", 0)
            for name, r in active_repos.items()
            if name not in exclude_repos
        )
    else:
        total_adds = cache.get("totals", {}).get("additions", 320410)
        total_dels = cache.get("totals", {}).get("deletions", 85240)

    cache.setdefault("totals", {})["additions"] = total_adds
    cache["totals"]["deletions"] = total_dels
    cache["totals"]["last_updated"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return total_adds, total_dels


def write_svg_idempotent(output_path: Path, new_content: str) -> bool:
    """
    Validates XML and writes to output_path ONLY if content has changed.
    Returns True if written, False if skipped due to byte-equality.
    """
    # Strict XML validation
    ET.fromstring(new_content)

    if output_path.exists():
        existing = output_path.read_text(encoding="utf-8")
        if existing == new_content:
            log_info(f"{output_path.name} is already up to date (idempotent skip)")
            return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(new_content, encoding="utf-8")
    log_ok(f"Updated {output_path.name}")
    return True


def update_readme_projects(readme_path: Path, projects: list[dict]) -> bool:
    """
    Injects projects SVG and terminal quick-links between <!-- PROJECTS:START -->
    and <!-- PROJECTS:END --> tags idempotently.
    """
    if not readme_path.is_file():
        log_warn(f"README file not found at {readme_path}")
        return False

    content = readme_path.read_text(encoding="utf-8")
    start_tag = "<!-- PROJECTS:START -->"
    end_tag = "<!-- PROJECTS:END -->"

    if start_tag not in content or end_tag not in content:
        log_warn("README.md missing <!-- PROJECTS:START --> or <!-- PROJECTS:END --> markers.")
        return False

    start_idx = content.index(start_tag) + len(start_tag)
    end_idx = content.index(end_tag)

    links = []
    for p in projects[:4]:
        name = p.get("name") or (p.get("repo", "").split("/")[-1] if p.get("repo") else "repo")
        url = p.get("url") or f"https://github.com/{p.get('repo')}"
        links.append(f'cd <a href="{url}">{name}</a>')

    links_cmd = " | ".join(links)
    replacement = f"""
<div align="center">
  <img src="./assets/projects.svg" alt="Open Source Projects Dashboard" width="100%" />
</div>

<div align="center">
  <code>humam@workstation:~/projects$ {links_cmd}</code>
</div>
"""
    new_content = content[:start_idx] + "\n" + replacement.strip() + "\n" + content[end_idx:]
    if new_content == content:
        log_info("README.md projects section already up to date (idempotent skip)")
        return False

    readme_path.write_text(new_content, encoding="utf-8")
    log_ok("Updated README.md with projects dashboard")
    return True


VISITOR_BADGE_MARKDOWN = (
    "[![session_hits](https://komarev.com/ghpvc/?username=humam-hossain"
    "&color=3fb950&labelColor=161b22&style=flat-square&label=session_hits)]"
    "(https://github.com/humam-hossain)"
)


def update_readme_badges(readme_path: Path) -> bool:
    """
    Appends 5th session_hits visitor counter badge to top contact row idempotently.
    """
    if not readme_path.is_file():
        log_warn(f"README file not found at {readme_path}")
        return False

    content = readme_path.read_text(encoding="utf-8")
    if "session_hits" in content:
        log_info("README.md visitor badge already present (idempotent skip)")
        return False

    resume_badge_str = "[![Resume]"
    if resume_badge_str in content:
        idx = content.index(resume_badge_str)
        end_link_idx = content.find(")", idx) + 1
        new_content = content[:end_link_idx] + "\n" + VISITOR_BADGE_MARKDOWN + content[end_link_idx:]
        readme_path.write_text(new_content, encoding="utf-8")
        log_ok("Appended visitor counter badge to README.md")
        return True

    log_warn("README.md missing Resume badge; cannot append visitor badge")
    return False


def main() -> int:
    """CLI Entry point for profile update engine."""
    log_info("humam@workstation profile updater v1.0.0")

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    cache = load_cache(CACHE_PATH)
    token = get_github_token(ROOT_DIR)

    if not token:
        log_warn("No token found. Running offline with cached/mock telemetry")

    baseline_dt = get_baseline_date(config, cache, token)
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    y, m, d = compute_calendar_diff(baseline_dt, now_utc)
    uptime_str = format_uptime_neofetch(y, m, d)
    log_info(f"Coding uptime: {uptime_str} (since {baseline_dt.strftime('%Y-%m-%d')})")

    adds, dels = aggregate_loc(config, cache, token)
    add_str, del_str = format_loc_counts(adds, dels)
    log_info(f"Aggregate LOC: {add_str} / {del_str}")

    hero_svg_content = generate_svg(uptime=uptime_str, loc_add=add_str, loc_del=del_str)
    write_svg_idempotent(HERO_SVG_PATH, hero_svg_content)

    # 2. Phase 3: Projects Dashboard telemetry
    log_info("Refreshing open source projects dashboard telemetry...")
    curated = load_curated_projects(PROJECTS_CONFIG_PATH)
    projects_data = fetch_project_telemetry(curated, cache, token)
    projects_svg = generate_projects_svg(projects_data)
    write_svg_idempotent(PROJECTS_SVG_PATH, projects_svg)
    update_readme_projects(README_PATH, projects_data)

    save_cache(CACHE_PATH, cache)
    log_ok("Profile telemetry refresh complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
