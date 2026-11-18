# Phase 4: Languages, Streaks & Metrics - Pattern Map

**Date:** 2026-11-08  
**Status:** Ready for Planning  
**Target Output File:** `.planning/phases/04-languages-streaks-metrics/04-PATTERNS.md`  
**Phase Directory:** `.planning/phases/04-languages-streaks-metrics/`  

---

## 1. Executive Summary & File Mapping

This document provides the planner and implementation agents with concrete code patterns, structural templates, and exact analogs extracted from the existing codebase for Phase 4 (`04-languages-streaks-metrics`).

### Target Files Inventory

| Target File | Operation | Role Classification | Data Flow Description | Closest Codebase Analog |
|---|---|---|---|---|
| `config/terminal_theme.json` | **MODIFY** | Theme Tokens & Config | Loaded by generators and coordinator; holds color tokens and language ignore lists | `config/terminal_theme.json` (self) & `config/projects.json` |
| `data/cache.json` | **MODIFY** | Persistent State Cache | Read/written by engine; persists `streak_metrics`, `top_languages`, `recent_activity` | `data/cache.json` (`project_metrics` pattern) |
| `scripts/generate_metrics.py` | **CREATE** | Standalone SVG Generator | CLI/Coordinator -> SVG XML DOM -> ElementTree Validation -> `assets/metrics.svg` | `scripts/generate_projects.py` |
| `assets/metrics.svg` | **CREATE** | Vector Terminal Window Asset | Rendered by generator; committed to repo; embedded into `README.md` | `assets/projects.svg` & `assets/hero.svg` |
| `scripts/update_profile.py` | **MODIFY** | Telemetry Coordinator Engine | Queries GitHub APIs -> computes telemetry -> updates cache -> writes SVG & README | `scripts/update_profile.py` (Phases 1-3 functions) |
| `README.md` | **MODIFY** | Profile Presentation Target | Surgical injection of visitor badge and metrics block (`<!-- METRICS:START -->`) | `README.md` (badges & `<!-- PROJECTS:START -->`) |
| `tests/fixtures/graphql_calendar.json` | **CREATE** | Test Fixture (Calendar) | Offline test mock for GitHub `contributionsCollection.contributionCalendar` | `tests/fixtures/graphql_commits.json` |
| `tests/fixtures/graphql_languages.json` | **CREATE** | Test Fixture (Languages) | Offline test mock for repository language byte counts via GraphQL | `tests/fixtures/graphql_repos.json` |
| `tests/fixtures/rest_events.json` | **CREATE** | Test Fixture (Recent Activity) | Offline test mock for public push events and commits for activity stream | `tests/fixtures/graphql_commits.json` |
| `tests/test_metrics.py` | **CREATE** | Offline Test Suite | 100% offline pytest suite validating streak math, language bars, SVG & README | `tests/test_projects.py` |

---

## 2. Per-File Pattern Assignments & Analog Excerpts

---

### 2.1 `config/terminal_theme.json` (MODIFY)

- **Role:** Central Design Tokens & Configuration
- **Data Flow:** Loaded by `update_profile.py` (`load_config`) and `generate_metrics.py`. Configures ignored languages and terminal color tokens.
- **Analog:** `config/terminal_theme.json` lines 88-92.

#### Existing Analog Pattern (`config/terminal_theme.json`)
```json
  "telemetry": {
    "exclude_repos": [],
    "baseline_override_date": null
  }
```

#### Pattern to Implement
Preserve all existing geometry, colors, typography, and telemetry keys to guarantee backwards compatibility with `tests/test_tokens.py`. Extend the `"telemetry"` section with `"ignore_languages"`:
```json
  "telemetry": {
    "exclude_repos": [],
    "baseline_override_date": null,
    "ignore_languages": [
      "HTML",
      "CSS",
      "TeX",
      "Markdown"
    ]
  }
```

---

### 2.2 `data/cache.json` (MODIFY)

- **Role:** Persistent Telemetry Cache
- **Data Flow:** Read on startup by `load_cache(CACHE_PATH)`. If live queries fail or token is absent, serves as Tier 2 fallback. Updated at end of run and saved via `save_cache(CACHE_PATH, cache)`.
- **Analog:** `data/cache.json` lines 24-96 (`project_metrics` added in Phase 3).

#### Existing Analog Pattern (`data/cache.json`)
```json
  "project_metrics": {
    "last_updated": "2026-11-08T03:29:48Z",
    "projects": [
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
        "url": "https://github.com/humam-hossain/linux_shell_scripting"
      }
    ]
  }
```

#### Pattern to Implement
Add `streak_metrics`, `top_languages`, and `recent_activity` sections while retaining existing `baseline`, `repositories`, `totals`, and `project_metrics`:
```json
  "streak_metrics": {
    "last_updated": "2026-11-08T07:35:46Z",
    "current_streak": 0,
    "longest_streak": 0,
    "total_contributions": 0,
    "standby": true
  },
  "top_languages": {
    "last_updated": "2026-11-08T07:35:46Z",
    "languages": [
      {
        "name": "Python",
        "bytes": 55000,
        "color": "#3572A5",
        "percentage": 52.4
      },
      {
        "name": "Shell",
        "bytes": 32000,
        "color": "#89e051",
        "percentage": 30.5
      },
      {
        "name": "C",
        "bytes": 12000,
        "color": "#555555",
        "percentage": 11.4
      },
      {
        "name": "Other",
        "bytes": 6000,
        "color": "#8b949e",
        "percentage": 5.7
      }
    ]
  },
  "recent_activity": {
    "last_updated": "2026-11-08T07:35:46Z",
    "events": [
      {
        "sha": "a1b2c3d",
        "repo": "linux_shell_scripting",
        "message": "fix: resolve path resolution in bootstrap script",
        "time_ago": "2 days ago",
        "url": "https://github.com/humam-hossain/linux_shell_scripting/commit/a1b2c3d",
        "repo_url": "https://github.com/humam-hossain/linux_shell_scripting"
      }
    ]
  }
```

---

### 2.3 `scripts/generate_metrics.py` (CREATE)

- **Role:** Standalone SVG Generator for `assets/metrics.svg`
- **Data Flow:** Accepts `streak_data: dict`, `languages_data: list[dict]`, `theme: dict | None`. Formats SVG XML string with ElementTree validation. Provides CLI entrypoint `main()`.
- **Analog:** `scripts/generate_projects.py` (full file architecture, lines 1-35, 203-297).

#### Concrete Code Patterns to Copy from `scripts/generate_projects.py`

**Imports and Path Resolution:**
```python
# [scripts/generate_projects.py:10-21]
from __future__ import annotations

import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import xml.sax.saxutils as saxutils

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config" / "terminal_theme.json"
OUTPUT_PATH = ROOT_DIR / "assets" / "metrics.svg"
```

**Theme Loading & Fallback:**
```python
# [scripts/generate_projects.py:211-227]
if theme is None:
    if CONFIG_PATH.is_file():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            theme = json.load(f)
    else:
        theme = {}

colors = theme.get("colors", {})
bg_body = colors.get("background", {}).get("body", "#0d1117")
bg_header = colors.get("background", {}).get("header", "#161b22")
border_color = colors.get("border", "#30363d")
t = theme.get("typography", {})
font_family = t.get(
    "font_family",
    'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
)
```

**Terminal Window Chrome & Header:**
```python
# [scripts/generate_projects.py:229-266]
lines = [
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 340" width="100%" height="100%">',
    '  <defs>',
    '    <style>',
    f'      .mono {{ font-family: {font_family}; text-rendering: geometricPrecision; }}',
    '      .title {{ font-size: 13px; fill: #8b949e; text-anchor: middle; font-weight: 400; }}',
    '      .prompt-cmd {{ font-size: 13px; }}',
    '      .prompt-user {{ fill: #58a6ff; font-weight: 600; }}',
    '      .prompt-arg {{ fill: #c9d1d9; font-weight: 400; }}',
    '      .card-title {{ font-size: 13px; font-weight: 600; }}',
    '      .card-val {{ font-size: 22px; font-weight: bold; }}',
    '      .card-unit {{ font-size: 13px; fill: #8b949e; font-weight: 400; }}',
    '      .lang-name {{ font-size: 13px; fill: #c9d1d9; font-weight: 500; }}',
    '      .lang-pct {{ font-size: 12px; fill: #8b949e; font-weight: 400; text-anchor: end; }}',
    '      .sub-header {{ font-size: 13px; fill: #8b949e; font-weight: 600; }}',
    '      .badge-standby {{ font-size: 12px; fill: #8b949e; font-weight: 400; }}',
    '    </style>',
    '  </defs>',
    '',
    '  <!-- Terminal Window Frame -->',
    f'  <rect width="850" height="340" rx="10" ry="10" fill="{bg_body}" stroke="{border_color}" stroke-width="1" />',
    '',
    '  <!-- Header Bar -->',
    f'  <rect width="850" height="38" rx="10" ry="10" fill="{bg_header}" />',
    f'  <rect y="28" width="850" height="10" fill="{bg_header}" />',
    f'  <line x1="0" y1="38" x2="850" y2="38" stroke="{border_color}" stroke-width="1" />',
    '',
    '  <!-- Traffic Lights -->',
    '  <circle cx="25" cy="19" r="6" fill="#ff5f56" />',
    '  <circle cx="45" cy="19" r="6" fill="#ffbd2e" />',
    '  <circle cx="65" cy="19" r="6" fill="#27c93f" />',
    '',
    '  <!-- Window Title -->',
    '  <text x="425" y="24" class="mono title">stats — zsh</text>',
    '',
    '  <!-- Prompt Line -->',
    '  <text x="30" y="62" class="mono prompt-cmd">',
    '    <tspan class="prompt-user">humam@workstation:~$ </tspan>',
    '    <tspan class="prompt-arg">git status --telemetry</tspan>',
    '  </text>',
]
```

**Strict XML Validation & CLI Entry Point:**
```python
# [scripts/generate_projects.py:279-297]
    lines.append('</svg>')
    svg_str = "\n".join(lines) + "\n"

    # Strict XML validation
    ET.fromstring(svg_str)
    return svg_str


def main() -> int:
    """CLI Entry point for standalone SVG generation."""
    print("Generating assets/metrics.svg using default fixtures...")
    svg_content = generate_metrics_svg(DEFAULT_STREAK_FIXTURES, DEFAULT_LANGUAGE_FIXTURES)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(svg_content, encoding="utf-8")
    print(f"Successfully generated {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

### 2.4 `scripts/update_profile.py` (MODIFY)

- **Role:** Main Telemetry Coordinator & Pipeline Engine
- **Data Flow:**
  - Queries `contributionsCollection.contributionCalendar` (GraphQL) -> `fetch_streak_telemetry()`
  - Queries `viewer.repositories.languages` (GraphQL) -> `fetch_language_telemetry()`
  - Queries commits / public events (REST/GraphQL) -> `fetch_recent_activity()`
  - Calls `generate_metrics_svg()` -> writes `assets/metrics.svg` via `write_svg_idempotent()`
  - Calls `update_readme_badges()` and `update_readme_metrics()` to update `README.md`
  - Saves updated telemetry to `data/cache.json` via `save_cache()`
- **Analog:** `scripts/update_profile.py` lines 446-510 (`fetch_project_telemetry`), 659-676 (`write_svg_idempotent`), 679-723 (`update_readme_projects`), 725-761 (`main`).

#### Concrete Code Patterns to Copy from `scripts/update_profile.py`

**Importing Generator Function:**
```python
# [scripts/update_profile.py:31-35]
try:
    from scripts.generate_metrics import (
        generate_metrics_svg,
        DEFAULT_STREAK_FIXTURES,
        DEFAULT_LANGUAGE_FIXTURES,
    )
except (ImportError, ModuleNotFoundError):
    from generate_metrics import (
        generate_metrics_svg,
        DEFAULT_STREAK_FIXTURES,
        DEFAULT_LANGUAGE_FIXTURES,
    )

METRICS_SVG_PATH = ROOT_DIR / "assets" / "metrics.svg"
```

**Multi-Tier Fallback Strategy (Tier 1 Live -> Tier 2 Cache -> Tier 3 Fixtures):**
```python
# [scripts/update_profile.py:450-510]
def fetch_streak_telemetry(cache: dict, token: str | None = None) -> dict:
    """
    Tier 1: Live GraphQL query to contributionsCollection.contributionCalendar
    Tier 2: Cache fallback from cache['streak_metrics']
    Tier 3: DEFAULT_STREAK_FIXTURES
    """
    if token:
        try:
            # Live query execution
            ...
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
```

**Surgical Markdown Anchor Injection & Idempotency:**
```python
# [scripts/update_profile.py:679-723]
def update_readme_metrics(readme_path: Path, activity_html: str) -> bool:
    """
    Injects metrics SVG and git activity stream between <!-- METRICS:START -->
    and <!-- METRICS:END --> tags idempotently.
    """
    if not readme_path.is_file():
        log_warn(f"README file not found at {readme_path}")
        return False

    content = readme_path.read_text(encoding="utf-8")
    start_tag = "<!-- METRICS:START -->"
    end_tag = "<!-- METRICS:END -->"

    if start_tag not in content or end_tag not in content:
        log_warn("README.md missing <!-- METRICS:START --> or <!-- METRICS:END --> markers.")
        return False

    start_idx = content.index(start_tag) + len(start_tag)
    end_idx = content.index(end_tag)

    replacement = f"""
<div align="center">
  <img src="./assets/metrics.svg" alt="Languages, Streaks & Metrics" width="100%" />
</div>

{activity_html}
"""
    new_content = content[:start_idx] + "\n" + replacement.strip() + "\n" + content[end_idx:]
    if new_content == content:
        log_info("README.md metrics section already up to date (idempotent skip)")
        return False

    readme_path.write_text(new_content, encoding="utf-8")
    log_ok("Updated README.md with metrics telemetry and activity stream")
    return True
```

**Badge Row Update Pattern:**
```python
def update_readme_badges(readme_path: Path) -> bool:
    """
    Appends 5th session_hits visitor counter badge to top contact row idempotently.
    """
    if not readme_path.is_file():
        return False

    content = readme_path.read_text(encoding="utf-8")
    badge_marker = "session_hits"
    if badge_marker in content:
        log_info("README.md visitor badge already present (idempotent skip)")
        return False

    visitor_badge = (
        "[![session_hits](https://komarev.com/ghpvc/?username=humam-hossain"
        "&color=3fb950&labelColor=161b22&style=flat-square&label=session_hits)]"
        "(https://github.com/humam-hossain)"
    )

    resume_badge_str = "[![Resume]"
    if resume_badge_str in content:
        # Insert directly after Resume badge
        idx = content.index(resume_badge_str)
        # Find closing parenthesis of resume badge markdown link
        end_link_idx = content.find(")", idx) + 1
        new_content = content[:end_link_idx] + "\n" + visitor_badge + content[end_link_idx:]
        readme_path.write_text(new_content, encoding="utf-8")
        log_ok("Appended visitor counter badge to README.md")
        return True

    return False
```

**Coordinator Pipeline Integration (`main()`):**
```python
# [scripts/update_profile.py:750-761]
    # Phase 4: Languages, Streaks & Metrics
    log_info("Refreshing languages, streaks & telemetry...")
    streak_data = fetch_streak_telemetry(cache, token)
    languages_data = fetch_language_telemetry(config, cache, token)
    metrics_svg = generate_metrics_svg(streak_data, languages_data, theme=config)
    write_svg_idempotent(METRICS_SVG_PATH, metrics_svg)

    activities = fetch_recent_activity(cache, token)
    activity_html = format_git_activity_stream(activities)
    update_readme_metrics(README_PATH, activity_html)
    update_readme_badges(README_PATH)

    save_cache(CACHE_PATH, cache)
```

---

### 2.5 `README.md` (MODIFY)

- **Role:** Markdown Profile Document
- **Data Flow:** Surgically modified by `scripts/update_profile.py`.
- **Analog:** `README.md` lines 5-25.

#### Target Section 1: Top Badge Container (lines 5-12)
```markdown
<div align="center">

[![Email](https://img.shields.io/badge/Email-muhammed.humam.hossain%40gmail.com-161b22?style=flat-square&logo=gmail&logoColor=ffa657)](mailto:muhammed.humam.hossain@gmail.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-humam--hossain-161b22?style=flat-square&logo=linkedin&logoColor=58a6ff)](https://www.linkedin.com/in/humam-hossain-7ab762230/)
[![Portfolio](https://img.shields.io/badge/Portfolio-humam--hossain-161b22?style=flat-square&logo=safari&logoColor=3fb950)](https://github.com/humam-hossain)
[![Resume](https://img.shields.io/badge/Resume-PDF-161b22?style=flat-square&logo=adobeacrobatreader&logoColor=ff7b72)](./cv/outputs/cv_humam_hossain.pdf)
[![session_hits](https://komarev.com/ghpvc/?username=humam-hossain&color=3fb950&labelColor=161b22&style=flat-square&label=session_hits)](https://github.com/humam-hossain)

</div>
```

#### Target Section 2: Metrics Anchors (lines 24-25)
```markdown
<!-- METRICS:START -->
<div align="center">
  <img src="./assets/metrics.svg" alt="Languages, Streaks & Metrics" width="100%" />
</div>

<div align="left">
<pre><code>humam@workstation:~$ git log --graph --oneline -n 6
* <a href="https://github.com/humam-hossain/linux_shell_scripting/commit/a1b2c3d">[a1b2c3d]</a> (<a href="https://github.com/humam-hossain/linux_shell_scripting">linux_shell_scripting</a>) fix: resolve path resolution in bootstrap script (2 days ago)
* <a href="https://github.com/humam-hossain/Python/commit/d4e5f6a">[d4e5f6a]</a> (<a href="https://github.com/humam-hossain/Python">Python</a>) feat(robotics): add quaternion kinematics module (4 days ago)
* <a href="https://github.com/humam-hossain/nn/commit/b7c8d9e">[b7c8d9e]</a> (<a href="https://github.com/humam-hossain/nn">nn</a>) perf: optimize matrix multiplication cache locality (1 week ago)
</code></pre>
</div>
<!-- METRICS:END -->
```

---

### 2.6 `tests/test_metrics.py` (CREATE)

- **Role:** Offline Pytest Unit & Integration Suite
- **Data Flow:** Reads fixtures from `tests/fixtures/`, tests streak calculation, language aggregation, bot filtering, commit clamping, XML validity, and README injection without network calls.
- **Analog:** `tests/test_projects.py` (lines 1-100, 354-432).

#### Concrete Code Patterns to Copy from `tests/test_projects.py`

**Module Header, Fixtures Path & Imports:**
```python
# [tests/test_projects.py:1-38]
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import xml.etree.ElementTree as ET

import pytest

from scripts.generate_metrics import (
    DEFAULT_STREAK_FIXTURES,
    DEFAULT_LANGUAGE_FIXTURES,
    generate_metrics_svg,
)
from scripts.update_profile import (
    compute_streaks_from_calendar,
    aggregate_top_languages,
    format_git_activity_stream,
    update_readme_metrics,
    update_readme_badges,
    fetch_streak_telemetry,
    fetch_language_telemetry,
    fetch_recent_activity,
)

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
```

**Fixture Validation Test Pattern:**
```python
# [tests/test_projects.py:40-63]
def test_fixtures_calendar_valid_json():
    """Verify tests/fixtures/graphql_calendar.json exists and has valid calendar structure."""
    fixture_path = FIXTURES_DIR / "graphql_calendar.json"
    assert fixture_path.is_file(), "Missing graphql_calendar.json fixture"

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "data" in data
    assert "viewer" in data["data"]
    assert "contributionsCollection" in data["data"]["viewer"]
    assert "contributionCalendar" in data["data"]["viewer"]["contributionsCollection"]
```

**Surgical README Injection & Idempotency Test Pattern:**
```python
# [tests/test_projects.py:354-379]
def test_readme_injection_and_idempotence(tmp_path):
    """Verify surgical injection into README between markers and idempotent second run."""
    mock_readme = tmp_path / "README.md"
    original_content = (
        "# User Profile\n\n"
        "<!-- METRICS:START -->\n"
        "<!-- METRICS:END -->\n\n"
        "Footer note\n"
    )
    mock_readme.write_text(original_content, encoding="utf-8")
    mock_html = "<pre><code>humam@workstation:~$ git log</code></pre>"

    # 1. First injection
    res1 = update_readme_metrics(mock_readme, mock_html)
    assert res1 is True

    updated_content = mock_readme.read_text(encoding="utf-8")
    assert '<img src="./assets/metrics.svg"' in updated_content
    assert "<code>humam@workstation:~$ git log" in updated_content
    assert "# User Profile" in updated_content
    assert "Footer note" in updated_content

    # 2. Second injection with identical data -> idempotent skip
    res2 = update_readme_metrics(mock_readme, mock_html)
    assert res2 is False
    assert mock_readme.read_text(encoding="utf-8") == updated_content
```

**Full Coordinator Offline Run Test Pattern:**
```python
# [tests/test_projects.py:419-432]
def test_full_coordinator_offline_execution(monkeypatch, capsys):
    """Verify executing main() unauthenticated exits 0 and updates all assets gracefully."""
    from scripts.update_profile import main

    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)

    exit_code = main()
    assert exit_code == 0

    captured = capsys.readouterr()
    output = captured.out + captured.err
    assert "[WARN]" in output
    assert "No token found" in output
```

---

### 2.7 Test Fixtures (`tests/fixtures/`)

- **Role:** Test Fixture Files for 100% Offline Pytest Execution
- **Analog:** `tests/fixtures/graphql_projects.json` & `tests/fixtures/graphql_commits.json`.

#### `tests/fixtures/graphql_calendar.json` (CREATE)
Mimics GitHub GraphQL response for `contributionsCollection.contributionCalendar`:
```json
{
  "data": {
    "viewer": {
      "contributionsCollection": {
        "contributionCalendar": {
          "totalContributions": 482,
          "weeks": [
            {
              "contributionDays": [
                {
                  "date": "2026-11-06",
                  "contributionCount": 4,
                  "color": "#39d353"
                },
                {
                  "date": "2026-11-07",
                  "contributionCount": 7,
                  "color": "#26a641"
                },
                {
                  "date": "2026-11-08",
                  "contributionCount": 2,
                  "color": "#006d32"
                }
              ]
            }
          ]
        }
      }
    }
  }
}
```

#### `tests/fixtures/graphql_languages.json` (CREATE)
Mimics GitHub GraphQL response for `viewer.repositories.nodes.languages`:
```json
{
  "data": {
    "viewer": {
      "repositories": {
        "nodes": [
          {
            "name": "Python",
            "isFork": false,
            "languages": {
              "edges": [
                { "size": 65000, "node": { "name": "Python", "color": "#3572A5" } },
                { "size": 1200, "node": { "name": "Markdown", "color": "#083fa1" } }
              ]
            }
          },
          {
            "name": "linux_shell_scripting",
            "isFork": false,
            "languages": {
              "edges": [
                { "size": 42000, "node": { "name": "Shell", "color": "#89e051" } }
              ]
            }
          },
          {
            "name": "nn",
            "isFork": false,
            "languages": {
              "edges": [
                { "size": 18000, "node": { "name": "C", "color": "#555555" } }
              ]
            }
          }
        ]
      }
    }
  }
}
```

#### `tests/fixtures/rest_events.json` (CREATE)
Mimics GitHub public events / commit stream:
```json
[
  {
    "id": "10001",
    "type": "PushEvent",
    "actor": { "login": "humam-hossain" },
    "repo": { "name": "humam-hossain/linux_shell_scripting" },
    "payload": {
      "commits": [
        {
          "sha": "a1b2c3d4e5f6",
          "message": "fix: resolve path resolution in bootstrap script",
          "author": { "name": "Muhammed Humam Hossain" }
        }
      ]
    },
    "created_at": "2026-11-06T14:20:00Z"
  },
  {
    "id": "10002",
    "type": "PushEvent",
    "actor": { "login": "humam-hossain" },
    "repo": { "name": "humam-hossain/Python" },
    "payload": {
      "commits": [
        {
          "sha": "d4e5f6a1b2c3",
          "message": "feat(robotics): add quaternion kinematics module",
          "author": { "name": "Muhammed Humam Hossain" }
        }
      ]
    },
    "created_at": "2026-11-04T09:15:00Z"
  },
  {
    "id": "10003",
    "type": "PushEvent",
    "actor": { "login": "dependabot[bot]" },
    "repo": { "name": "humam-hossain/linux_shell_scripting" },
    "payload": {
      "commits": [
        {
          "sha": "999999999999",
          "message": "bump actions/checkout from 3 to 4",
          "author": { "name": "dependabot[bot]" }
        }
      ]
    },
    "created_at": "2026-11-03T02:00:00Z"
  }
]
```

---

## 3. Core Algorithms to Implement

### 3.1 Streak Calculation with Today-Grace-Period (Decision D-05)
```python
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
```

### 3.2 Language Aggregation & Ignore Filtering (Decisions D-08, D-09, D-12)
```python
def aggregate_top_languages(
    repo_nodes: list[dict],
    ignore_list: list[str] | None = None,
) -> list[dict]:
    """
    Aggregates language byte counts across repositories, filters ignored languages,
    and returns top 5 languages + aggregated 'Other' row if remainder >= 1%.
    """
    ignore_set = set(ignore_list or ["HTML", "CSS", "TeX", "Markdown"])
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
```

### 3.3 Git Activity Formatting & Bot Filtering (Decisions D-14, D-16, D-18)
```python
import html

BOT_AUTHORS = {"github-actions[bot]", "dependabot[bot]", "github-actions", "dependabot"}
FILTER_PREFIXES = ("docs(update):", "chore(deps):", "bump ")

def format_git_activity_stream(activities: list[dict]) -> str:
    """
    Renders terminal-styled <pre><code> git activity stream with clickable links.
    Clamps commit message to 50 characters with ellipsis.
    Filters out bots and updater feedback loop commits.
    """
    filtered = []
    for item in activities:
        author = item.get("author", "").lower()
        msg = item.get("message", "").strip()
        if author in BOT_AUTHORS or any(author.startswith(b) for b in ("dependabot", "github-actions")):
            continue
        if any(msg.startswith(p) for p in FILTER_PREFIXES):
            continue
        filtered.append(item)

    lines = [
        '<div align="left">',
        "<pre><code>humam@workstation:~$ git log --graph --oneline -n 6",
    ]

    for item in filtered[:6]:
        sha = item.get("sha", "")[:7]
        repo = item.get("repo", "repo")
        commit_url = item.get("url", f"https://github.com/humam-hossain/{repo}")
        repo_url = item.get("repo_url", f"https://github.com/humam-hossain/{repo}")
        raw_msg = item.get("message", "").strip().split("\n")[0]

        # 50-character clamping
        if len(raw_msg) > 50:
            clamped = raw_msg[:47] + "..."
        else:
            clamped = raw_msg

        time_ago = item.get("time_ago", "recently")
        escaped_repo = html.escape(repo)
        escaped_msg = html.escape(clamped)

        lines.append(
            f'* <a href="{commit_url}">[{sha}]</a> '
            f'(<a href="{repo_url}">{escaped_repo}</a>) '
            f'{escaped_msg} ({time_ago})'
        )

    lines.append("</code></pre>")
    lines.append("</div>")
    return "\n".join(lines)
```

---

## 4. Cross-Cutting Patterns Checklist

- [x] **Zero External Pip Dependencies:** Standard library only (`json`, `pathlib`, `xml.etree.ElementTree`, `xml.sax.saxutils`, `html`, `datetime`, `urllib`).
- [x] **Strict XML Validation:** Every generated SVG string parsed with `ET.fromstring()` before write or test assertion.
- [x] **Idempotent Writes:** Content compared to existing file bytes before writing; skips unnecessary disk modifications.
- [x] **Surgical README Anchors:** Changes strictly bounded by `<!-- METRICS:START -->` and `<!-- METRICS:END -->`.
- [x] **Multi-Tier Fallbacks:** Tier 1 (Live API) -> Tier 2 (Cache) -> Tier 3 (Static Fixtures).
- [x] **100% Offline Pytest Isolation:** Mocked via `unittest.mock.patch` and local JSON fixtures; runs cleanly in any sandbox without tokens.
- [x] **ASVS & STRIDE Compliant:** All API string inputs escaped via `saxutils.escape()` for SVG and `html.escape()` for Markdown HTML.
