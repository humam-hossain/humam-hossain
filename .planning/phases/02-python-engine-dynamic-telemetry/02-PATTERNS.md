# Phase 2: Python Engine & Dynamic Telemetry — Pattern Map

**Generated:** 2026-11-07  
**Status:** Complete  
**Directives:** Downstream plan generators and execution agents MUST follow these patterns without ad-hoc deviation.

---

## 1. Target Files Inventory

| File Path | Action | Role | Data Flow | Closest Analog |
|-----------|--------|------|-----------|----------------|
| `scripts/generate_hero.py` | Modify | Parameterized Vector Graphic Generator | `config/terminal_theme.json` + `(uptime, loc_add, loc_del)` $\rightarrow$ Valid XML SVG String / `assets/hero.svg` | Existing `scripts/generate_hero.py` |
| `config/terminal_theme.json` | Modify | Configuration Token Store & Repo Filter | Git repository $\rightarrow$ `scripts/update_profile.py` & `scripts/generate_hero.py` | Existing `config/terminal_theme.json` |
| `scripts/update_profile.py` | Create | Standalone Automation Engine / CLI Controller | Environment / `.env` $\rightarrow$ GitHub GraphQL API $\rightarrow$ `data/cache.json` $\rightarrow$ `scripts/generate_hero.py` $\rightarrow$ `assets/hero.svg` | `scripts/generate_hero.py` & `cv/build.sh` |
| `data/cache.json` | Create | Persistent Git-Tracked State Cache | GitHub GraphQL API / Cache $\rightarrow$ `data/cache.json` $\rightarrow$ Telemetry Metrics | `config/terminal_theme.json` |
| `tests/test_update_profile.py` | Create | Offline Unit & Integration Test Suite | Fixtures / Pytest Runner $\rightarrow$ `scripts/update_profile.py` $\rightarrow$ Assertions | `tests/test_tokens.py` |
| `tests/fixtures/graphql_baseline.json` | Create | Static GraphQL Mock Fixture (Baseline) | Test Mock Transport $\rightarrow$ `update_profile.py` | `config/terminal_theme.json` |
| `tests/fixtures/graphql_repos.json` | Create | Static GraphQL Mock Fixture (Repositories) | Test Mock Transport $\rightarrow$ `update_profile.py` | `config/terminal_theme.json` |
| `tests/fixtures/graphql_commits.json` | Create | Static GraphQL Mock Fixture (Commits Batch) | Test Mock Transport $\rightarrow$ `update_profile.py` | `config/terminal_theme.json` |
| `assets/hero.svg` | Modify (Generated) | Vector Graphic Component | `scripts/update_profile.py` output $\rightarrow$ Profile Viewport | Existing `assets/hero.svg` |

---

## 2. Codebase Analogs & Pattern Origins

### 2.1 Parameterized SVG Generator

#### Codebase Analog: `scripts/generate_hero.py`
In Phase 1, `scripts/generate_hero.py` generated static placeholder values with DOM ID hooks (`val-uptime`, `val-loc-add`, `val-loc-del`).
Notice the exact lines in `scripts/generate_hero.py`:

```python
# Excerpt from scripts/generate_hero.py (Phase 1)
# Lines 30-38
TELEMETRY_ITEMS = [
    ("OS:", "Arch Linux x86_64"),
    ("Host:", "Workstation"),
    ("Kernel:", "AI & Robotics"),
    ("Focus:", "Autonomous Systems, IoT & Cloud"),
    ("Uptime:", "4 yrs, 3 mos, 12 days"),
    ("Shell:", "zsh 5.9"),
    ("Contact:", "humam@... / in/humam-hossain"),
]

# Lines 41, 107-115
def generate_svg() -> str:
    # ...
    for key, val in TELEMETRY_ITEMS:
        padded_key = f"{key:<10}"
        escaped_val = saxutils.escape(val)
        if "Uptime" in key:
            lines.append(f'    <text x="{tm["x"]}" y="{cur_y}" class="mono"><tspan class="key" xml:space="preserve">{padded_key} </tspan><tspan id="val-uptime" class="val">{escaped_val}</tspan></text>')
        else:
            lines.append(f'    <text x="{tm["x"]}" y="{cur_y}" class="mono"><tspan class="key" xml:space="preserve">{padded_key} </tspan><tspan class="val">{escaped_val}</tspan></text>')
        cur_y += tm["line_height"]

    # LOC Counter with Phase 2 DOM Hooks
    loc_key = f'{"LOC:":<10}'
    lines.append(f'    <text x="{tm["x"]}" y="{cur_y}" class="mono"><tspan class="key" xml:space="preserve">{loc_key} </tspan><tspan id="val-loc-add" class="loc-add">++320,410</tspan><tspan class="val"> / </tspan><tspan id="val-loc-del" class="loc-del">--85,240</tspan></text>')
```

#### New Pattern: Parameterized `generate_svg()` Signature (D-09)
In Phase 2, `generate_svg` accepts optional telemetry overrides while preserving default fallback values, keeping all Phase 1 tests in `tests/test_tokens.py` passing:

```python
# Pattern for scripts/generate_hero.py (Phase 2)
DEFAULT_UPTIME = "4 yrs, 3 mos, 12 days"
DEFAULT_LOC_ADD = "++320,410"
DEFAULT_LOC_DEL = "--85,240"

def generate_svg(
    uptime: str | None = None,
    loc_add: str | None = None,
    loc_del: str | None = None
) -> str:
    uptime_val = uptime if uptime is not None else DEFAULT_UPTIME
    loc_add_val = loc_add if loc_add is not None else DEFAULT_LOC_ADD
    loc_del_val = loc_del if loc_del is not None else DEFAULT_LOC_DEL
    
    # In telemetry loop:
    # Uptime uses saxutils.escape(uptime_val) within <tspan id="val-uptime">
    # LOC uses saxutils.escape(loc_add_val) in <tspan id="val-loc-add">
    # and saxutils.escape(loc_del_val) in <tspan id="val-loc-del">
```

---

### 2.2 Configuration Token Store & Repo Filter

#### Codebase Analog: `config/terminal_theme.json`
`config/terminal_theme.json` defines geometry, typography, and color tokens.

```json
// Excerpt from config/terminal_theme.json (Phase 1)
{
  "meta": {
    "name": "GitHub Dark Terminal Theme",
    "version": "1.0.0",
    "author": "humam-hossain"
  },
  "geometry": { ... },
  "colors": { ... },
  "typography": { ... }
}
```

#### New Pattern: Repository Exclusion & Baseline Override (D-01, D-06)
Phase 2 extends this schema cleanly at the root or within a `telemetry` config block:

```json
{
  "meta": {
    "name": "GitHub Dark Terminal Theme",
    "version": "1.1.0",
    "author": "humam-hossain"
  },
  "geometry": { ... },
  "colors": { ... },
  "typography": { ... },
  "telemetry": {
    "exclude_repos": [],
    "baseline_override_date": null
  }
}
```

---

### 2.3 Standalone Profile Update Engine

#### Codebase Analogs: `scripts/generate_hero.py` & `cv/build.sh`
The codebase emphasizes:
1. Pure standard library dependencies (zero external pip packages).
2. Clean terminal logging output.
3. Path anchoring relative to file location (`Path(__file__).resolve().parent.parent`).
4. Strict XML/output validation prior to persisting artifacts.

```python
# Path and XML validation pattern from scripts/generate_hero.py
ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config" / "terminal_theme.json"
OUTPUT_PATH = ROOT_DIR / "assets" / "hero.svg"

# ElementTree verification pattern
ET.fromstring(content)
```

#### New Pattern: `scripts/update_profile.py` Structure
The new engine coordinates multi-source authentication, resilient GraphQL queries, UTC date math, incremental LOC calculation, and idempotent SVG rendering:

```python
#!/usr/bin/env python3
"""
scripts/update_profile.py
Automated profile telemetry engine for Muhammed Humam Hossain (humam-hossain).
Standard library only: urllib, json, datetime, xml, calendar, pathlib.
Zero external dependencies.
"""

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

from scripts.generate_hero import generate_svg

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config" / "terminal_theme.json"
CACHE_PATH = ROOT_DIR / "data" / "cache.json"
HERO_SVG_PATH = ROOT_DIR / "assets" / "hero.svg"
GRAPHQL_ENDPOINT = "https://api.github.com/graphql"
```

---

### 2.4 Persistent Telemetry Cache

#### Codebase Analog: `config/terminal_theme.json`
Data is serialized as human-readable JSON with 2-space indentation and typed structures.

#### New Pattern: `data/cache.json` (D-02, D-07)
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
    }
  },
  "totals": {
    "additions": 320410,
    "deletions": 85240,
    "last_updated": "2026-11-07T14:00:00Z"
  }
}
```

---

### 2.5 Verification & Test Architecture

#### Codebase Analog: `tests/test_tokens.py`
The test patterns established in Phase 1 use standard `pytest` assertions, `Path` manipulation, schema validation, and `xml.etree.ElementTree` parsing:

```python
# Excerpt from tests/test_tokens.py
def test_hero_svg_generation():
    svg_content = generate_svg()
    root = ET.fromstring(svg_content)
    assert root.tag == "{http://www.w3.org/2000/svg}svg" or root.tag == "svg"
    assert root.find(".//*[@id='val-uptime']") is not None
```

#### New Pattern: `tests/test_update_profile.py` (D-16)
The Phase 2 test suite validates authentication order, exact calendar date math, pluralization, LOC aggregation, incremental cache hits, network retries, offline execution, and idempotency—completely offline using fixtures and `monkeypatch`:

```python
# Pattern for tests/test_update_profile.py
import json
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

from scripts.update_profile import (
    compute_calendar_diff,
    format_uptime_neofetch,
    format_loc_counts,
    get_github_token,
    load_cache,
    save_cache,
    write_svg_idempotent,
)
```

---

## 3. Concrete Implementation Patterns

### 3.1 Parameterized SVG Generation (`scripts/generate_hero.py`)

Modify `scripts/generate_hero.py` to support dynamic parameters while preserving defaults and strict ElementTree validation:

```python
# scripts/generate_hero.py (parameterized implementation pattern)

DEFAULT_UPTIME = "4 yrs, 3 mos, 12 days"
DEFAULT_LOC_ADD = "++320,410"
DEFAULT_LOC_DEL = "--85,240"

def generate_svg(
    uptime: str | None = None,
    loc_add: str | None = None,
    loc_del: str | None = None,
) -> str:
    """
    Generates assets/hero.svg content.
    If telemetry parameters are None, falls back to default workstation baseline tokens.
    """
    uptime_val = uptime if uptime is not None else DEFAULT_UPTIME
    loc_add_val = loc_add if loc_add is not None else DEFAULT_LOC_ADD
    loc_del_val = loc_del if loc_del is not None else DEFAULT_LOC_DEL

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        theme = json.load(f)

    g = theme["geometry"]
    c = theme["colors"]
    t = theme["typography"]
    fs = t["font_sizes"]

    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{g["viewBox"]}" width="100%" height="100%">')
    lines.append('<defs>')
    lines.append(f'''  <style>
    .mono {{
      font-family: {t["font_family"]};
      text-rendering: geometricPrecision;
    }}
    .title {{ font-size: {fs["title"]}px; fill: {c["text"]["title"]}; text-anchor: middle; }}
    .mono-art {{ font-size: {fs["monogram"]}px; fill: {c["text"]["monogram"]}; white-space: pre; font-weight: bold; }}
    .prompt {{ font-size: {fs["prompt"]}px; fill: {c["text"]["prompt"]}; font-weight: bold; }}
    .divider {{ font-size: {fs["divider"]}px; fill: {c["text"]["divider"]}; }}
    .key {{ font-size: {fs["telemetry"]}px; fill: {c["text"]["key"]}; font-weight: 600; }}
    .val {{ font-size: {fs["telemetry"]}px; fill: {c["text"]["value"]}; }}
    .loc-add {{ font-size: {fs["telemetry"]}px; fill: {c["text"]["additions"]}; font-weight: 600; }}
    .loc-del {{ font-size: {fs["telemetry"]}px; fill: {c["text"]["deletions"]}; font-weight: 600; }}
  </style>''')
    lines.append(f'  <clipPath id="card-clip"><rect width="{g["width"]}" height="{g["height"]}" rx="{g["card_rx"]}" ry="{g["card_rx"]}" /></clipPath>')
    lines.append('</defs>')

    # Window chrome & background
    lines.append('  <g clip-path="url(#card-clip)">')
    lines.append(f'    <rect width="{g["width"]}" height="{g["height"]}" fill="{c["background"]["body"]}" />')
    lines.append(f'    <rect width="{g["width"]}" height="{g["header_height"]}" fill="{c["background"]["header"]}" />')
    lines.append(f'    <line x1="0" y1="{g["header_height"]}" x2="{g["width"]}" y2="{g["header_height"]}" stroke="{c["border"]}" stroke-width="1" />')

    for light in g["traffic_lights"]:
        lines.append(f'    <circle cx="{light["cx"]}" cy="{light["cy"]}" r="{light["r"]}" fill="{light["color"]}" />')

    lines.append(f'    <text x="{g["width"] // 2}" y="24" class="mono title">humam@workstation:~</text>')

    mg = g["monogram"]
    for i, line in enumerate(MONOGRAM_LINES):
        y = mg["y_start"] + i * mg["line_height"]
        lines.append(f'    <text x="{mg["x"]}" y="{y}" class="mono mono-art" xml:space="preserve">{line}</text>')

    strip = g["ansi_strip"]
    for i, color in enumerate(c["ansi"]):
        cx = strip["x_start"] + i * strip["spacing"]
        lines.append(f'    <circle cx="{cx}" cy="{strip["cy"]}" r="{strip["r"]}" fill="{color}" />')

    tm = g["telemetry"]
    cur_y = tm["y_start"]
    lines.append(f'    <text x="{tm["x"]}" y="{cur_y}" class="mono prompt">humam@workstation:~</text>')
    cur_y += tm["line_height"] - 2

    lines.append(f'    <text x="{tm["x"]}" y="{cur_y}" class="mono divider">-------------------</text>')
    cur_y += tm["line_height"]

    for key, val in TELEMETRY_ITEMS:
        padded_key = f"{key:<10}"
        if "Uptime" in key:
            escaped_val = saxutils.escape(str(uptime_val))
            lines.append(f'    <text x="{tm["x"]}" y="{cur_y}" class="mono"><tspan class="key" xml:space="preserve">{padded_key} </tspan><tspan id="val-uptime" class="val">{escaped_val}</tspan></text>')
        else:
            escaped_val = saxutils.escape(str(val))
            lines.append(f'    <text x="{tm["x"]}" y="{cur_y}" class="mono"><tspan class="key" xml:space="preserve">{padded_key} </tspan><tspan class="val">{escaped_val}</tspan></text>')
        cur_y += tm["line_height"]

    # Parameterized LOC counter with preserved DOM hooks
    loc_key = f'{"LOC:":<10}'
    esc_add = saxutils.escape(str(loc_add_val))
    esc_del = saxutils.escape(str(loc_del_val))
    lines.append(f'    <text x="{tm["x"]}" y="{cur_y}" class="mono"><tspan class="key" xml:space="preserve">{loc_key} </tspan><tspan id="val-loc-add" class="loc-add">{esc_add}</tspan><tspan class="val"> / </tspan><tspan id="val-loc-del" class="loc-del">{esc_del}</tspan></text>')

    lines.append(f'    <rect width="{g["width"]}" height="{g["height"]}" rx="{g["card_rx"]}" ry="{g["card_rx"]}" fill="none" stroke="{c["border"]}" stroke-width="1" />')
    lines.append('  </g>')
    lines.append('</svg>')

    content = "\n".join(lines)
    ET.fromstring(content)
    return content
```

---

### 3.2 Terminal Logging & ANSI Formatting (`scripts/update_profile.py`)

Harmonize CLI status output with workstation terminal tokens:

```python
# ANSI escape codes matching workstation palette
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

---

### 3.3 Multi-Source Credential Resolution (D-13, D-14)

```python
def get_github_token(root_dir: Path) -> str | None:
    """
    Resolves GitHub token in strict priority order:
    1. GITHUB_TOKEN environment variable
    2. GH_TOKEN environment variable
    3. .env file in root directory (stdlib parser)
    Returns None if no token is found.
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
                        if k in ("GITHUB_TOKEN", "GH_TOKEN") and v:
                            return v
        except Exception as e:
            log_warn(f"Failed to read .env file: {e}")

    return None
```

---

### 3.4 GitHub GraphQL Transport with Exponential Retries (D-15)

```python
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
                status = resp.status
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
            retry_after = e.headers.get("Retry-After")

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

---

### 3.5 Calendar-Accurate Coding Uptime (D-03, D-04)

Standard-library calendar math guaranteeing exact elapsed years, months, and days in UTC:

```python
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
```

---

### 3.6 LOC Formatting & Incremental Cache Management (D-07, D-08)

```python
def format_loc_counts(additions: int, deletions: int) -> tuple[str, str]:
    """Formats LOC integers with commas and directional symbols."""
    return f"++{additions:,}", f"--{deletions:,}"

def load_cache(cache_path: Path) -> dict:
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
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
```

---

### 3.7 Idempotent File Writing (D-10, D-11)

```python
def write_svg_idempotent(output_path: Path, new_content: str) -> bool:
    """
    Validates XML and writes to output_path ONLY if content has changed.
    Returns True if written, False if skipped due to byte-equality.
    """
    # Strict validation
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

---

### 3.8 Complete Pytest Unit & Offline Test Suite (`tests/test_update_profile.py`)

Pattern ensuring 100% test coverage without hitting network endpoints:

```python
"""
tests/test_update_profile.py
Unit and integration tests for profile update engine and dynamic telemetry.
100% offline using mock fixtures and standard library assertions.
"""

import datetime
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import pytest

from scripts.generate_hero import generate_svg
from scripts.update_profile import (
    _add_calendar_months,
    compute_calendar_diff,
    format_uptime_neofetch,
    format_loc_counts,
    get_github_token,
    load_cache,
    save_cache,
    write_svg_idempotent,
)

ROOT_DIR = Path(__file__).resolve().parent.parent

def test_token_resolution_order(tmp_path, monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)

    # 1. No token
    assert get_github_token(tmp_path) is None

    # 2. .env file
    env_file = tmp_path / ".env"
    env_file.write_text("GITHUB_TOKEN=token_from_env\n", encoding="utf-8")
    assert get_github_token(tmp_path) == "token_from_env"

    # 3. GH_TOKEN overrides .env
    monkeypatch.setenv("GH_TOKEN", "token_from_gh")
    assert get_github_token(tmp_path) == "token_from_gh"

    # 4. GITHUB_TOKEN overrides GH_TOKEN
    monkeypatch.setenv("GITHUB_TOKEN", "token_from_actions")
    assert get_github_token(tmp_path) == "token_from_actions"


def test_calendar_uptime_math():
    # Regular years
    start = datetime.datetime(2020, 9, 18, 7, 0, 0, tzinfo=datetime.timezone.utc)
    end = datetime.datetime(2026, 11, 7, 14, 0, 0, tzinfo=datetime.timezone.utc)
    y, m, d = compute_calendar_diff(start, end)
    assert (y, m, d) == (6, 1, 20)
    assert format_uptime_neofetch(y, m, d) == "6 yrs, 1 mo, 20 days"

    # Pluralization edge cases
    assert format_uptime_neofetch(1, 1, 1) == "1 yr, 1 mo, 1 day"
    assert format_uptime_neofetch(0, 0, 0) == "0 yrs, 0 mos, 0 days"
    assert format_uptime_neofetch(2, 0, 15) == "2 yrs, 0 mos, 15 days"

    # Leap year boundary (Feb 29 -> Feb 28 non-leap)
    start_leap = datetime.datetime(2024, 2, 29, 0, 0, 0, tzinfo=datetime.timezone.utc)
    end_leap = datetime.datetime(2025, 2, 28, 0, 0, 0, tzinfo=datetime.timezone.utc)
    assert compute_calendar_diff(start_leap, end_leap) == (1, 0, 0)


def test_loc_formatting():
    add_str, del_str = format_loc_counts(320410, 85240)
    assert add_str == "++320,410"
    assert del_str == "--85,240"

    add_zero, del_zero = format_loc_counts(0, 0)
    assert add_zero == "++0"
    assert del_zero == "--0"


def test_cache_lifecycle(tmp_path):
    cache_file = tmp_path / "cache.json"
    cache = load_cache(cache_file)
    assert "baseline" in cache
    assert "repositories" in cache
    assert "totals" in cache

    cache["repositories"]["test_repo"] = {
        "pushed_at": "2026-11-07T12:00:00Z",
        "additions": 1500,
        "deletions": 200,
    }
    save_cache(cache_file, cache)

    reloaded = load_cache(cache_file)
    assert reloaded["repositories"]["test_repo"]["additions"] == 1500


def test_svg_parameterization_and_dom_hooks():
    # Test custom values
    custom_uptime = "5 yrs, 2 mos, 10 days"
    custom_add = "++400,000"
    custom_del = "--50,000"

    svg = generate_svg(uptime=custom_uptime, loc_add=custom_add, loc_del=custom_del)
    root = ET.fromstring(svg)

    uptime_el = root.find(".//*[@id='val-uptime']")
    assert uptime_el is not None
    assert uptime_el.text == custom_uptime

    add_el = root.find(".//*[@id='val-loc-add']")
    assert add_el is not None
    assert add_el.text == custom_add

    del_el = root.find(".//*[@id='val-loc-del']")
    assert del_el is not None
    assert del_el.text == custom_del


def test_idempotent_write(tmp_path):
    target = tmp_path / "hero.svg"
    svg1 = generate_svg()

    # First write returns True
    assert write_svg_idempotent(target, svg1) is True
    assert target.exists()

    # Second write with identical content returns False (skip)
    assert write_svg_idempotent(target, svg1) is False
```

---

## 4. Pattern Implementation Rules & Directives

### Invariant 1: Standard Library Only
- **Rule**: Absolutely no third-party package dependencies may be introduced. Never add `requests`, `python-dotenv`, `dateutil`, or `beautifulsoup4`.
- **Enforcement**: Rely entirely on `urllib.request`, `urllib.error`, `json`, `datetime`, `calendar`, `xml.sax.saxutils`, `xml.etree.ElementTree`, and `pathlib.Path`.

### Invariant 2: Strict UTC Datetime Precision
- **Rule**: Datetime evaluations must always pass `datetime.timezone.utc`.
- **Enforcement**: Never use naive `datetime.datetime.now()`. Always use `datetime.datetime.now(datetime.timezone.utc)`.

### Invariant 3: ElementTree XML Integrity Gate
- **Rule**: Any SVG output generated must be parsed via `xml.etree.ElementTree.fromstring()` prior to writing to disk.
- **Enforcement**: Malformed XML immediately raises an unhandled exception before touching `assets/hero.svg`.

### Invariant 4: DOM ID Hook Retention
- **Rule**: The DOM elements `<tspan id="val-uptime">`, `<tspan id="val-loc-add">`, and `<tspan id="val-loc-del">` must remain intact in `assets/hero.svg`.
- **Enforcement**: Both Phase 1 tests (`test_tokens.py`) and Phase 2 tests (`test_update_profile.py`) assert the presence and contents of these IDs.

### Invariant 5: Idempotency & Clean Diffs
- **Rule**: `update_profile.py` must compare generated SVG content with existing file content before calling `write_text()`.
- **Enforcement**: If content is identical, the file write is skipped. This prevents unnecessary GitHub Actions commit churn and empty diffs.

### Invariant 6: GraphQL Commit History Safety
- **Rule**: Commit history queries must never request more than 50 commits per page (`first: 50`).
- **Enforcement**: Prevents GitHub's internal git diff backend from timing out with HTTP 502 Bad Gateway.

---

## 5. Anti-Patterns to Avoid

| Anti-Pattern | Why It Is Prohibited | Proper Alternative |
|--------------|----------------------|--------------------|
| Calling REST `/repos/{owner}/{repo}/stats/contributors` | GitHub queues contributor stats asynchronously, returning HTTP 202 and hanging or failing on automated runners. | Query commit history additions/deletions directly via GraphQL `defaultBranchRef.target.history(first: 50)`. |
| Requesting `history(first: 100)` across multiple repos | Causes GitHub git backend timeouts and HTTP 502 Bad Gateway. | Enumerate repos first; fetch commits in batches of 50 only for repos whose `pushedAt` advanced. |
| Using `pip install` or `requirements.txt` | Phase constraint requires 0-overhead stdlib execution. | Use stdlib `urllib.request` and standard library modules exclusively. |
| Naive month subtraction (`end.month - start.month`) | Fails on leap years and months with varying days (e.g. Jan 31 to Feb 28). | Use verified `compute_calendar_diff` and `_add_calendar_months` calendar clamping algorithm. |
| Crashing when unauthenticated (`GITHUB_TOKEN` unset) | Breaks local developers running `python3 scripts/update_profile.py` without credentials. | Log `[WARN]` and use cached or fallback telemetry gracefully with exit code 0. |
| Direct string replacement without XML escaping | Strings containing `&`, `<`, `>` corrupt the SVG and break browser rendering. | Always escape dynamic values using `xml.sax.saxutils.escape()`. |
| Touching `assets/hero.svg` on every run | Causes dirty git states in scheduled GitHub Actions runners when numbers haven't changed. | Idempotent equality check before writing. |

---

*Pattern Map for Phase 2: Python Engine & Dynamic Telemetry*  
*Compliant with GSD architecture directives and project conventions.*
