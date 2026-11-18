# Phase 3: Open Source Projects Dashboard — Pattern Map

**Generated:** 2026-11-07  
**Domain:** GitHub GraphQL API v4, SVG 1.1 Vector Graphics Generation, Python Automation Engine, Monospace Terminal Design Systems  
**Status:** Complete  
**Directives:** Downstream plan generators and execution agents MUST follow these patterns without ad-hoc deviation.

---

## 1. Target Files Inventory

| File Path | Action | Role | Data Flow | Closest Analog |
|-----------|--------|------|-----------|----------------|
| `config/projects.json` | Create | Project Curation & Metadata Overrides | Human/Curator Config $\rightarrow$ `scripts/update_profile.py` & `scripts/generate_projects.py` | `config/terminal_theme.json` |
| `scripts/generate_projects.py` | Create | Standalone Projects SVG Generator | `config/terminal_theme.json` + `project_metrics` $\rightarrow$ XML Validation $\rightarrow$ `assets/projects.svg` | `scripts/generate_hero.py` |
| `scripts/update_profile.py` | Modify | Telemetry Engine & Coordinator | `config/projects.json` + GitHub GraphQL API $\rightarrow$ `data/cache.json` $\rightarrow$ `assets/projects.svg` & `README.md` | Existing `scripts/update_profile.py` |
| `assets/projects.svg` | Create (Generated) | Rendered Projects Terminal Window SVG | Generator Output $\rightarrow$ `assets/projects.svg` $\rightarrow$ `README.md` Viewport | `assets/hero.svg` |
| `data/cache.json` | Modify (Runtime/Persisted) | Git-Tracked State Cache | GraphQL API / Snapshot $\rightarrow$ `cache.project_metrics` $\rightarrow$ Offline Fallback | Existing `data/cache.json` |
| `README.md` | Modify | Root Profile Presentation Target | `scripts/update_profile.py` $\rightarrow$ Anchor Replacement `<!-- PROJECTS:START/END -->` | Existing `README.md` |
| `tests/fixtures/graphql_projects.json` | Create | Mock GraphQL Response Fixture | Test Mock HTTP Transport $\rightarrow$ `scripts/update_profile.py` | `tests/fixtures/graphql_repos.json` |
| `tests/test_projects.py` | Create | Offline Unit & Integration Test Suite | Fixtures / Pytest Runner $\rightarrow$ `scripts/generate_projects.py` & `scripts/update_profile.py` | `tests/test_update_profile.py` |

---

## 2. Codebase Analogs & Pattern Origins

### 2.1 SVG Generation & XML Validation Pattern

#### Codebase Analog: `scripts/generate_hero.py`
In Phases 1 and 2, SVG generation is strictly encapsulated in a standalone script adhering to standard library imports (`xml.etree.ElementTree`, `xml.sax.saxutils`, `json`, `pathlib`), consuming configuration tokens and performing strict validation prior to disk emission.

```python
# [scripts/generate_hero.py:L8-L17]
from __future__ import annotations

import json
from pathlib import Path
import xml.sax.saxutils as saxutils
import xml.etree.ElementTree as ET

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config" / "terminal_theme.json"
OUTPUT_PATH = ROOT_DIR / "assets" / "hero.svg"
```

```python
# [scripts/generate_hero.py:L144-L156]
    content = "\n".join(lines)
    # Strict validation before emission
    ET.fromstring(content)
    return content


if __name__ == "__main__":
    svg = generate_svg()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Successfully generated {OUTPUT_PATH}")
```

#### Application to `scripts/generate_projects.py`:
- Use the exact same standard-library import signature.
- Accept a `projects: list[dict]` parameter and an optional `theme: dict | None = None`.
- Construct the terminal window chrome: outer `<rect>` with `rx="10" ry="10"`, header bar (`#161b22`, height 38), macOS traffic light circles (`#ff5f56`, `#ffbd2e`, `#27c93f`), header title `projects — zsh` at `x=425, y=24`, and console prompt line at `y=62`.
- Validate with `ET.fromstring(content)` before returning or writing to disk.

---

### 2.2 GraphQL Execution, Rate Limiting & Error Handling

#### Codebase Analog: `scripts/update_profile.py`
In Phase 2, `scripts/update_profile.py` established a resilient HTTP client using `urllib.request` with exponential backoff for HTTP 429/5xx status codes, JSON payload encoding, rate-limit header monitoring, and strict error reporting.

```python
# [scripts/update_profile.py:L103-L165]
def execute_graphql(
    query: str,
    variables: dict | None = None,
    token: str | None = None,
    max_retries: int = 3,
) -> dict:
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
```

#### Application to Project Telemetry:
- `scripts/update_profile.py` reuses `execute_graphql()` directly without modification or duplication.
- Batched repository telemetry is fetched through a single consolidated query using field aliases (`repo_0`, `repo_1`, ...), consuming exactly 1 API quota point.

---

### 2.3 Idempotent Disk Writing & Logging Pattern

#### Codebase Analog: `scripts/update_profile.py`
`write_svg_idempotent()` verifies XML syntax and compares byte content against the existing file before executing disk writes, preventing spurious git diffs and commits.

```python
# [scripts/update_profile.py:L500-L518]
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
```

ANSI terminal logging helpers:
```python
# [scripts/update_profile.py:L37-L62]
ANSI_BLUE = "\033[38;2;88;166;255m"   # #58a6ff (Prompt Blue)
ANSI_GREEN = "\033[38;2;63;185;80m"   # #3fb950 (Additions Green)
ANSI_AMBER = "\033[38;2;255;166;87m"  # #ffa657 (Key Amber)
ANSI_RED = "\033[38;2;248;81;73m"     # #f85149 (Deletions Red)
ANSI_RESET = "\033[0m"

def log_info(msg: str) -> None:
    print(f"{ANSI_BLUE}[INFO]{ANSI_RESET} {msg}")

def log_ok(msg: str) -> None:
    print(f"{ANSI_GREEN}[OK]{ANSI_RESET} {msg}")

def log_warn(msg: str) -> None:
    print(f"{ANSI_AMBER}[WARN]{ANSI_RESET} {msg}")

def log_err(msg: str) -> None:
    print(f"{ANSI_RED}[ERROR]{ANSI_RESET} {msg}", file=sys.stderr)
```

#### Application:
- `write_svg_idempotent()` writes `assets/projects.svg`.
- An analog `update_readme_projects()` function uses the same equality check to update `README.md` idempotently between `<!-- PROJECTS:START -->` and `<!-- PROJECTS:END -->`.

---

### 2.4 Cache Lifecycle & Offline Fallback Pattern

#### Codebase Analog: `scripts/update_profile.py`
In Phase 2, `load_cache()` and `save_cache()` handle cache state persistence, corrupted file recovery, and graceful defaults.

```python
# [scripts/update_profile.py:L324-L352]
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
```

#### Application to Project Metrics:
Extend cache structure with a dedicated `project_metrics` key:
```json
{
  "baseline": { ... },
  "repositories": { ... },
  "totals": { ... },
  "project_metrics": {
    "last_updated": "2026-11-07T17:48:25Z",
    "projects": [ ... ]
  }
}
```
When running offline or without `GITHUB_TOKEN`, `update_profile.py` reads `cache.get("project_metrics", {}).get("projects", [])`. If that list is empty, it falls back to built-in static fixture data with `log_warn()`.

---

### 2.5 Pytest Structure & Offline Network Isolation Pattern

#### Codebase Analog: `tests/test_update_profile.py` & `tests/test_tokens.py`
`tests/test_update_profile.py` demonstrates standard fixture loading, `monkeypatch` environment isolation, `unittest.mock.patch` for `urlopen` and `execute_graphql`, and ElementTree XML assertions.

```python
# [tests/test_update_profile.py:L38-L63]
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

def test_fixtures_valid_json():
    """Verify that all GraphQL mock fixtures exist and parse as valid JSON."""
    baseline = FIXTURES_DIR / "graphql_baseline.json"
    repos = FIXTURES_DIR / "graphql_repos.json"
    commits = FIXTURES_DIR / "graphql_commits.json"

    assert baseline.is_file(), "Missing graphql_baseline.json fixture"
    assert repos.is_file(), "Missing graphql_repos.json fixture"
    assert commits.is_file(), "Missing graphql_commits.json fixture"
    # ...
```

```python
# [tests/test_update_profile.py:L387-L402]
def test_offline_fallback_mode(capsys, monkeypatch, tmp_path):
    """
    Validates offline fallback mode:
    When executed unauthenticated without a token, script proceeds gracefully,
    emits a warning, and exits 0 with zero unhandled exceptions.
    """
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)

    exit_code = main()
    assert exit_code == 0

    captured = capsys.readouterr()
    assert "[WARN]" in captured.out or "[WARN]" in captured.err
    assert "No token found" in (captured.out + captured.err)
```

---

## 3. Per-File Pattern Assignments & Implementation Blueprints

---

### 3.1 `config/projects.json`

**Role:** Curation layer defining featured repositories and custom display overrides.  
**Analog:** `config/terminal_theme.json`

#### Schema Requirements (CONTEXT.md D-07, D-08, D-09, D-10):
- Array of entries under the key `"projects"`.
- Supports both string shorthand (`"repo-name"`) and rich configuration objects.
- Rich configuration fields:
  - `repo`: Required string (`"owner/name"` or `"name"`).
  - `name`: Optional display override. Defaults to repo name.
  - `description`: Optional custom summary override.
  - `tag`: Optional categorical tag.
- Initial starter pins: `humam-hossain/linux_shell_scripting`, `humam-hossain/Python`, `humam-hossain/nn`, `humam-hossain/antigravity-cli-statusline`.

#### Concrete Blueprint:
```json
{
  "projects": [
    {
      "repo": "humam-hossain/linux_shell_scripting",
      "name": "linux_shell_scripting",
      "description": "Shell scripts and automation utilities for Unix systems",
      "tag": "DevOps"
    },
    {
      "repo": "humam-hossain/Python",
      "name": "Python",
      "description": "Python algorithms, utilities, and robotics tools",
      "tag": "Robotics & AI"
    },
    {
      "repo": "humam-hossain/nn",
      "name": "nn",
      "description": "C-based neural network framework for matrix operations and gradient learning",
      "tag": "Machine Learning"
    },
    {
      "repo": "humam-hossain/antigravity-cli-statusline",
      "name": "antigravity-cli-statusline",
      "description": "Advanced responsive statusline plugin for Antigravity CLI",
      "tag": "CLI Tooling"
    }
  ]
}
```

---

### 3.2 `scripts/generate_projects.py`

**Role:** Standalone SVG 1.1 vector graphics generator for `assets/projects.svg`.  
**Analog:** `scripts/generate_hero.py`

#### Key Constraints:
- Zero external dependencies: `json`, `pathlib`, `xml.etree.ElementTree`, `xml.sax.saxutils`.
- Root geometry: `viewBox="0 0 850 340"`, `width="100%"`, `height="100%"`.
- Top header: Height 38px, background `#161b22`, border `#30363d`, traffic lights (`#ff5f56`, `#ffbd2e`, `#27c93f`), window title `projects — zsh` at `(425, 24)`.
- Terminal prompt line at `y=62`: `humam@workstation:~/projects$` in `#58a6ff` (font-weight 600) + `gh repo list` in `#c9d1d9`.
- Sub-panel 2x2 grid slots:
  - Dimensions: 380px x 115px, `rx="6" ry="6"`, background `#161b22`, border `#30363d`.
  - Slot 1: `(30, 80)`
  - Slot 2: `(440, 80)`
  - Slot 3: `(30, 207)`
  - Slot 4: `(440, 207)`
- Sub-panel elements:
  - Header: Repo title `📁 {name}` at `(16, 24)` (14px, weight 600, fill `#a5d6ff`); Language indicator `● {lang}` at `(364, 24)` (`text-anchor="end"`, fill `#8b949e`, dot fill `language_color` or `#8b949e`).
  - Separator: `<line x1="16" y1="34" x2="364" y2="34" stroke="#21262d" stroke-width="1" />`.
  - Body: 2-line clamped description at `y=52` and `y=68` (12px, fill `#8b949e`).
  - Metric Counter Strip at `y=96`:
    - Star: `x=16` (`#f1e05a` if > 0 else `#616e7f`)
    - Fork: `x=100` (`#58a6ff` if > 0 else `#616e7f`)
    - Issue: `x=184` (`#ffa657` if > 0 else `#616e7f`)
    - PR: `x=274` (`#a371f7` if > 0 else `#616e7f`)
- Unoccupied slots (< 4 repos): Dashed border `<rect stroke-dasharray="4,4" .../>` with centered text `[ available slot ]`.
- Octicon SVG path glyphs: Inline paths scaled and translated into place.

#### Word-Wrapping & Clamping Pattern (Entity-Safe):
```python
def wrap_and_clamp_description(text: str, max_line1: int = 42, max_line2: int = 40) -> tuple[str, str]:
    """
    Wraps text into 2 lines with ellipsis truncation before escaping XML.
    Prevents splitting entities like '&amp;' across lines or at the truncation point.
    """
    clean = " ".join((text or "").split())
    if not clean:
        return "", ""

    words = clean.split()
    line1_words = []
    curr_len = 0
    idx = 0

    while idx < len(words):
        w = words[idx]
        add_len = len(w) + (1 if curr_len > 0 else 0)
        if curr_len + add_len <= max_line1:
            line1_words.append(w)
            curr_len += add_len
            idx += 1
        else:
            break

    line1 = " ".join(line1_words)
    rem_words = words[idx:]
    if not rem_words:
        return saxutils.escape(line1), ""

    line2_words = []
    curr_len = 0
    truncated = False
    for w in rem_words:
        add_len = len(w) + (1 if curr_len > 0 else 0)
        if curr_len + add_len <= max_line2:
            line2_words.append(w)
            curr_len += add_len
        else:
            truncated = True
            break

    line2 = " ".join(line2_words)
    if truncated or idx + len(line2_words) < len(words):
        line2 = line2.rstrip(".,;:!?") + "..."

    return saxutils.escape(line1), saxutils.escape(line2)
```

#### SVG Octicons & Glyph Rendering:
```python
OCTICONS = {
    "star": "M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z",
    "fork": "M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a2.25 2.25 0 1 1 1.5 0v.878a2.25 2.25 0 0 1-2.25 2.25h-1.5v2.128a2.251 2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3 6.25v-.878a2.25 2.25 0 1 1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm-3 8.75a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z",
    "issue": "M8 9.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3ZM8 0a8 8 0 1 1 0 16A8 8 0 0 1 8 0ZM1.5 8a6.5 6.5 0 1 0 13 0 6.5 6.5 0 0 0-13 0Z",
    "pr": "M1.5 3.25a2.25 2.25 0 1 1 3 2.122v5.256a2.251 2.251 0 1 1-1.5 0V5.372A2.25 2.25 0 0 1 1.5 3.25Zm5.677-.177L9.5 5.396V10.75a2.25 2.25 0 1 0 1.5 0V5.396l2.323-2.323a.75.75 0 0 0-1.06-1.06L11 3.28V1.5a.75.75 0 0 0-1.5 0v1.78L8.243 2.013a.75.75 0 0 0-1.066 1.06Z",
}
```

---

### 3.3 `scripts/update_profile.py` Extension

**Role:** Automation Engine coordinator fetching telemetry, invoking generators, and writing outputs.  
**Analog:** Existing functions in `scripts/update_profile.py`.

#### Required New Functions:

##### 1. Config Loader & Normalizer:
```python
PROJECTS_CONFIG_PATH = ROOT_DIR / "config" / "projects.json"
PROJECTS_SVG_PATH = ROOT_DIR / "assets" / "projects.svg"
README_PATH = ROOT_DIR / "README.md"

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
            name = item.get("name") or (parts[-1] if parts else "")
            normalized.append({
                "owner": owner,
                "name": name,
                "repo": f"{owner}/{name}",
                "description": item.get("description"),
                "tag": item.get("tag"),
            })
    return normalized
```

##### 2. Batched GraphQL Query Builder:
```python
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
```

##### 3. Telemetry Fetcher & Parser:
```python
DEFAULT_PROJECT_FIXTURES = [
    {
        "repo": "humam-hossain/linux_shell_scripting",
        "name": "linux_shell_scripting",
        "description": "Shell scripts and automation utilities for Unix systems",
        "stars": 0,
        "forks": 0,
        "open_issues": 0,
        "open_prs": 0,
        "language": "Shell",
        "language_color": "#89e051",
        "topics": ["bash", "shell", "automation"],
        "url": "https://github.com/humam-hossain/linux_shell_scripting",
    },
    {
        "repo": "humam-hossain/Python",
        "name": "Python",
        "description": "Python algorithms, utilities, and robotics tools",
        "stars": 0,
        "forks": 0,
        "open_issues": 0,
        "open_prs": 0,
        "language": "Python",
        "language_color": "#3572A5",
        "topics": ["python", "algorithms", "robotics"],
        "url": "https://github.com/humam-hossain/Python",
    },
    {
        "repo": "humam-hossain/nn",
        "name": "nn",
        "description": "C-based neural network framework for matrix operations and gradient learning",
        "stars": 0,
        "forks": 0,
        "open_issues": 0,
        "open_prs": 0,
        "language": "C",
        "language_color": "#555555",
        "topics": ["c", "machine-learning", "neural-network"],
        "url": "https://github.com/humam-hossain/nn",
    },
    {
        "repo": "humam-hossain/antigravity-cli-statusline",
        "name": "antigravity-cli-statusline",
        "description": "Advanced responsive statusline plugin for Antigravity CLI",
        "stars": 0,
        "forks": 0,
        "open_issues": 0,
        "open_prs": 0,
        "language": "Shell",
        "language_color": "#89e051",
        "topics": ["cli", "statusline", "zsh"],
        "url": "https://github.com/humam-hossain/antigravity-cli-statusline",
    },
]

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
```

##### 4. Idempotent README Section Injection:
```python
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
        name = p.get("name") or p.get("repo", "").split("/")[-1]
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
    new_content = content[:start_idx] + replacement + content[end_idx:]
    if new_content == content:
        log_info("README.md projects section already up to date (idempotent skip)")
        return False

    readme_path.write_text(new_content, encoding="utf-8")
    log_ok("Updated README.md with projects dashboard")
    return True
```

##### 5. Updated `main()` Pipeline Coordinator:
```python
def main() -> int:
    """CLI Entry point for profile update engine."""
    log_info("humam@workstation profile updater v1.0.0")

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    cache = load_cache(CACHE_PATH)
    token = get_github_token(ROOT_DIR)

    if not token:
        log_warn("No token found. Running offline with cached/mock telemetry")

    # 1. Hero telemetry
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
    curated = load_curated_projects(PROJECTS_CONFIG_PATH)
    projects_data = fetch_project_telemetry(curated, cache, token)
    projects_svg_content = generate_projects_svg(projects_data)
    write_svg_idempotent(PROJECTS_SVG_PATH, projects_svg_content)
    update_readme_projects(README_PATH, projects_data)

    # 3. Save cache
    save_cache(CACHE_PATH, cache)
    log_ok("Profile telemetry refresh complete.")
    return 0
```

---

### 3.4 `tests/fixtures/graphql_projects.json`

**Role:** Mock GraphQL response payload for 4 repositories.  
**Analog:** `tests/fixtures/graphql_repos.json`

```json
{
  "data": {
    "repo_0": {
      "name": "linux_shell_scripting",
      "owner": {
        "login": "humam-hossain"
      },
      "description": "Shell scripts and automation utilities for Unix systems",
      "stargazerCount": 12,
      "forkCount": 3,
      "issues": {
        "totalCount": 1
      },
      "pullRequests": {
        "totalCount": 0
      },
      "primaryLanguage": {
        "name": "Shell",
        "color": "#89e051"
      },
      "repositoryTopics": {
        "nodes": [
          { "topic": { "name": "bash" } },
          { "topic": { "name": "shell" } },
          { "topic": { "name": "automation" } }
        ]
      },
      "url": "https://github.com/humam-hossain/linux_shell_scripting"
    },
    "repo_1": {
      "name": "Python",
      "owner": {
        "login": "humam-hossain"
      },
      "description": "Python algorithms, utilities, and robotics tools",
      "stargazerCount": 24,
      "forkCount": 5,
      "issues": {
        "totalCount": 0
      },
      "pullRequests": {
        "totalCount": 2
      },
      "primaryLanguage": {
        "name": "Python",
        "color": "#3572A5"
      },
      "repositoryTopics": {
        "nodes": [
          { "topic": { "name": "python" } },
          { "topic": { "name": "robotics" } }
        ]
      },
      "url": "https://github.com/humam-hossain/Python"
    },
    "repo_2": {
      "name": "nn",
      "owner": {
        "login": "humam-hossain"
      },
      "description": "C-based neural network framework for matrix operations and gradient learning",
      "stargazerCount": 8,
      "forkCount": 1,
      "issues": {
        "totalCount": 0
      },
      "pullRequests": {
        "totalCount": 0
      },
      "primaryLanguage": {
        "name": "C",
        "color": "#555555"
      },
      "repositoryTopics": {
        "nodes": [
          { "topic": { "name": "c" } },
          { "topic": { "name": "machine-learning" } }
        ]
      },
      "url": "https://github.com/humam-hossain/nn"
    },
    "repo_3": {
      "name": "antigravity-cli-statusline",
      "owner": {
        "login": "humam-hossain"
      },
      "description": "Advanced responsive statusline plugin for Antigravity CLI",
      "stargazerCount": 5,
      "forkCount": 0,
      "issues": {
        "totalCount": 2
      },
      "pullRequests": {
        "totalCount": 1
      },
      "primaryLanguage": {
        "name": "Shell",
        "color": "#89e051"
      },
      "repositoryTopics": {
        "nodes": [
          { "topic": { "name": "cli" } },
          { "topic": { "name": "zsh" } }
        ]
      },
      "url": "https://github.com/humam-hossain/antigravity-cli-statusline"
    }
  }
}
```

---

### 3.5 `tests/test_projects.py`

**Role:** Comprehensive unit and integration test suite enforcing 100% network isolation.  
**Analog:** `tests/test_update_profile.py` & `tests/test_tokens.py`

#### Test Coverage Requirements:
1. `test_curation_config_loading`: Verifies `config/projects.json` structure, 4 starter pins, and string vs dictionary schema normalizations.
2. `test_batched_graphql_query_builder`: Asserts indexed aliases (`repo_0`, `repo_1`) and verifies requested fields (`stargazerCount`, `forkCount`, `issues`, `pullRequests`, `primaryLanguage`, `repositoryTopics`).
3. `test_description_wrapping_and_entity_escaping`: Asserts word wrapping at 42/40 characters, ellipsis addition, and safety of XML entities (`&amp;` not sliced).
4. `test_smart_description_fallback`: Verifies fallback to `#topics` or `"Open-source software repository"` when description is null or empty.
5. `test_projects_svg_xml_validity_and_geometry`: Strictly validates with `ET.fromstring`, verifies `viewBox="0 0 850 340"`, traffic lights, window title `projects — zsh`, prompt text `gh repo list`.
6. `test_subpanel_grid_positions`: Confirms sub-panel rect coordinates `(30, 80)`, `(440, 80)`, `(30, 207)`, `(440, 207)` with width 380 and height 115.
7. `test_zero_count_muted_accent`: Verifies non-zero counts use ANSI accents (`#f1e05a`, `#58a6ff`, `#ffa657`, `#a371f7`) while 0 counts use muted `#616e7f`.
8. `test_partial_grid_slots`: Validates dashed borders (`stroke-dasharray="4,4"`) and `[ available slot ]` placeholder when fewer than 4 repositories are declared.
9. `test_readme_injection_and_idempotence`: Verifies surgical replacement between `<!-- PROJECTS:START -->` and `<!-- PROJECTS:END -->`, verifies identical second run returns `False`.
10. `test_offline_fallback_mode`: Verifies pipeline runs without `GITHUB_TOKEN` and unhandled exceptions, using cache or fixtures.
11. `test_cache_lifecycle_for_projects`: Verifies `project_metrics` key and timestamp structure in `data/cache.json`.

---

## 4. Anti-Patterns & Critical Pitfalls Checklist

| Pitfall / Anti-Pattern | Bad Example | Correct Pattern | Reason / Consequence |
|------------------------|-------------|-----------------|----------------------|
| **Hyphenated GraphQL Aliases** | `linux-shell-scripting: repository(...)` | `repo_0: repository(...)` | GraphQL syntax error (`400 Bad Request`); alias names must follow identifier syntax `/[_A-Za-z][_0-9A-Za-z]*/`. |
| **Slicing XML-Escaped Strings** | `escaped[:80] + "..."` | `saxutils.escape(clamp(plain, 80))` | Slicing an entity like `&amp;` produces invalid XML (`&am...`), crashing `ET.fromstring()` with `ParseError`. |
| **Using `<foreignObject>` in SVG** | `<foreignObject width="380"><div>...</div></foreignObject>` | Native `<text>` with calculated `<tspan x="..." y="...">` | GitHub Camo proxy strips `<foreignObject>` tags entirely for security, resulting in blank panels. |
| **Unicode Glyphs for Metric Icons** | `★`, `⌥`, `⊙`, `⑂` in font text | Compact inline SVG `<path d="..." />` | Unicode glyphs render as missing character tofu boxes (`□`) across divergent client operating systems and fonts. |
| **Non-idempotent README Injection** | `content.replace(start_tag, start_tag + new_body)` | Locate `start_idx` and `end_idx`, slice cleanly, check `new_content == content` | Replaces or appends repeatedly, corrupting README markdown on subsequent runs. |
| **Unrounded Float Coordinates** | `x="30.00000001" y="80.33333"` | Explicit integer pixel coordinates (`x="30" y="80"`) | Float precision fluctuations trigger spurious git diffs and commits on CI runners. |
| **External Dependencies** | `import requests`, `from gql import Client` | Python Standard Library: `urllib.request`, `xml.etree.ElementTree`, `json` | Project-wide constraint strictly mandates zero external dependencies. |

---

## 5. Traceability Matrix

| Requirement | Architectural Role | Assigned Files | Verification Pattern |
|-------------|-------------------|----------------|----------------------|
| **PROJ-01** | Real-time Stars, Forks, Issues, PRs metrics display | `scripts/update_profile.py`, `scripts/generate_projects.py` | `test_batched_graphql_query_builder`, `test_zero_count_muted_accent` |
| **PROJ-02** | User-curated repositories via configuration with fallback | `config/projects.json`, `scripts/update_profile.py` | `test_curation_config_loading`, `test_smart_description_fallback` |
| **PROJ-03** | Dark terminal window styling (`850x340`), Cyan titles, traffic lights | `scripts/generate_projects.py`, `assets/projects.svg` | `test_projects_svg_xml_validity_and_geometry`, `test_subpanel_grid_positions` |
| **AUTO-01** | Standard library automation, idempotent file writes, caching | `scripts/update_profile.py`, `data/cache.json`, `README.md` | `test_readme_injection_and_idempotence`, `test_offline_fallback_mode` |

---

*Pattern mapping completed for Phase 3.*
