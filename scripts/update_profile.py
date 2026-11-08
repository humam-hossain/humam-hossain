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
    from scripts.generate_projects import DEFAULT_PROJECT_FIXTURES
except (ImportError, ModuleNotFoundError):
    from generate_projects import DEFAULT_PROJECT_FIXTURES

CONFIG_PATH = ROOT_DIR / "config" / "terminal_theme.json"
PROJECTS_CONFIG_PATH = ROOT_DIR / "config" / "projects.json"
CACHE_PATH = ROOT_DIR / "data" / "cache.json"
HERO_SVG_PATH = ROOT_DIR / "assets" / "hero.svg"
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
    return DEFAULT_PROJECT_FIXTURES


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

    svg_content = generate_svg(uptime=uptime_str, loc_add=add_str, loc_del=del_str)
    write_svg_idempotent(HERO_SVG_PATH, svg_content)

    save_cache(CACHE_PATH, cache)
    log_ok("Profile telemetry refresh complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
