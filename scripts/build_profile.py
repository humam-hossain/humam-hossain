#!/usr/bin/env python3
"""
scripts/build_profile.py
Compiles Andrew6rant-style dual-theme Neofetch profile SVGs (dark_mode.svg, light_mode.svg)
and maintains README.md. Standard library only (zero external dependencies).
"""

from __future__ import annotations

import calendar
import datetime
import html
import json
import os
from pathlib import Path
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "profile_config.json"
CACHE_PATH = ROOT_DIR / "data" / "cache.json"
DARK_SVG_PATH = ROOT_DIR / "dark_mode.svg"
LIGHT_SVG_PATH = ROOT_DIR / "light_mode.svg"
ASSETS_DIR = ROOT_DIR / "assets"
README_PATH = ROOT_DIR / "README.md"
GRAPHQL_ENDPOINT = "https://api.github.com/graphql"

TARGET_LINE_WIDTH = 60
SVG_WIDTH = 985
X_ASCII = 15
X_TEXT = 390
Y_START = 30
LINE_HEIGHT = 20

DEFAULT_ASCII_ART = [
    "                   -`                 ",
    "                  .o+`                ",
    "                 `ooo/                ",
    "                `+oooo:               ",
    "               `+oooooo:              ",
    "               -+oooooo+:             ",
    "             `/:-:++oooo+:            ",
    "            `/++++/+++++++:           ",
    "           `/++++++++++++++:          ",
    "          `/+++ooooooooooooo/`        ",
    "         ./ooosssso++osssssso+`       ",
    "        .oossssso-````/ossssss+`      ",
    "       -osssssso.      :ssssssso.     ",
    "      :osssssss/        osssso+++.    ",
    "     /ossssssss/        +ssssooo/-    ",
    "   `/ossssso+/:-        -:/+osssso+-  ",
    "  `+sso+:-`                 `.-/+oso: ",
    " `++:.                           `-/+/",
    " .`                                 `/",
    "                                      ",
    "         HUMAM HOSSAIN // WORKSTATION ",
    "         ============================ ",
    "         [AI & ROBOTICS / SYSTEMS]    ",
    "                                      ",
    "            github.com/humam-hossain  ",
]


def log_info(msg: str) -> None:
    print(f"\033[38;2;88;166;255m[INFO]\033[0m {msg}")


def log_ok(msg: str) -> None:
    print(f"\033[38;2;63;185;80m[OK]\033[0m {msg}")


def log_warn(msg: str) -> None:
    print(f"\033[38;2;255;166;87m[WARN]\033[0m {msg}")


def log_err(msg: str) -> None:
    print(f"\033[38;2;248;81;73m[ERROR]\033[0m {msg}", file=sys.stderr)


def get_token() -> str | None:
    """Finds GitHub API token from environment or .env."""
    for var in ("PROFILE_TOKEN", "GITHUB_TOKEN", "GH_TOKEN"):
        token = os.environ.get(var)
        if token and token.strip():
            return token.strip()

    env_path = ROOT_DIR / ".env"
    if env_path.is_file():
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        if k.strip() in ("PROFILE_TOKEN", "GITHUB_TOKEN", "GH_TOKEN"):
                            return v.strip().strip("'\"")
        except Exception:
            pass
    return None


def execute_graphql(query: str, variables: dict | None = None, token: str | None = None) -> dict:
    """Executes a GraphQL query."""
    if not token:
        raise ValueError("No GitHub token available.")
    payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    req = urllib.request.Request(
        GRAPHQL_ENDPOINT,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "humam-hossain-neofetch-builder",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def load_cache() -> dict:
    if CACHE_PATH.is_file():
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log_warn(f"Failed to read cache: {e}")
    return {}


def save_cache(data: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def calculate_uptime(start_date_str: str) -> str:
    """Calculates elapsed years, months, days."""
    try:
        start_date = datetime.date.fromisoformat(start_date_str.split("T")[0])
    except Exception:
        start_date = datetime.date(2020, 9, 20)

    today = datetime.date.today()
    years = today.year - start_date.year
    months = today.month - start_date.month
    days = today.day - start_date.day

    if days < 0:
        months -= 1
        prev_month = today.month - 1 or 12
        prev_year = today.year if prev_month != 12 else today.year - 1
        days += calendar.monthrange(prev_year, prev_month)[1]

    if months < 0:
        years -= 1
        months += 12

    y_str = f"{years} year" if years == 1 else f"{years} years"
    m_str = f"{months} month" if months == 1 else f"{months} months"
    d_str = f"{days} day" if days == 1 else f"{days} days"
    return f"{y_str}, {m_str}, {d_str}"


def fetch_stats(username: str, token: str | None, cache: dict) -> dict:
    """Fetches or recalls GitHub statistics."""
    stats = {
        "repos": 12,
        "contributed": 18,
        "stars": 45,
        "commits": 482,
        "followers": 15,
        "loc_total": 55543,
        "loc_add": 55543,
        "loc_del": 656,
        "uptime": "6 years, 1 month, 28 days",
    }

    # Seed from cache if present
    if "totals" in cache:
        stats["loc_add"] = cache["totals"].get("additions", stats["loc_add"])
        stats["loc_del"] = cache["totals"].get("deletions", stats["loc_del"])
        stats["loc_total"] = stats["loc_add"] + stats["loc_del"]
    if "streak_metrics" in cache:
        stats["commits"] = cache["streak_metrics"].get("total_contributions", stats["commits"])

    if not token:
        log_info("No GitHub token; using cached/baseline stats.")
        return stats

    log_info(f"Querying GitHub GraphQL API for {username}...")
    try:
        query = """
        query($login: String!) {
          user(login: $login) {
            createdAt
            followers { totalCount }
            repositories(first: 100, ownerAffiliations: [OWNER]) {
              totalCount
              nodes {
                stargazerCount
              }
            }
            repositoriesContributedTo(first: 100) {
              totalCount
            }
            contributionsCollection {
              contributionCalendar {
                totalContributions
              }
            }
          }
        }
        """
        data = execute_graphql(query, {"login": username}, token)
        user = data.get("data", {}).get("user", {})
        if user:
            repos_nodes = user.get("repositories", {}).get("nodes", [])
            stats["repos"] = user.get("repositories", {}).get("totalCount", stats["repos"])
            stats["contributed"] = user.get("repositoriesContributedTo", {}).get("totalCount", stats["contributed"])
            stats["stars"] = sum(r.get("stargazerCount", 0) for r in repos_nodes)
            stats["followers"] = user.get("followers", {}).get("totalCount", stats["followers"])
            stats["commits"] = user.get("contributionsCollection", {}).get("contributionCalendar", {}).get("totalContributions", stats["commits"])
            log_ok("Live GitHub stats fetched successfully.")
    except Exception as e:
        log_warn(f"Failed to fetch live stats: {e}. Preserving cached metrics.")

    return stats


def format_divider(title: str, total_len: int = TARGET_LINE_WIDTH) -> str:
    """
    Constructs an Andrew6rant-style section divider:
    e.g. '- Contact -——————————————————————————————————————————————-—-'
    """
    if not title:
        prefix = "- "
    else:
        prefix = f"- {title} -"
    
    suffix = "-—-"
    needed_dashes = total_len - len(prefix) - len(suffix)
    if needed_dashes < 1:
        needed_dashes = 1
    return f"{prefix}{'—' * needed_dashes}{suffix}"


def format_header_line(prompt: str, total_len: int = TARGET_LINE_WIDTH) -> str:
    """
    Formats the top prompt line:
    e.g. 'humam@workstation -———————————————————————————————————————————-—-'
    """
    prefix = f"{prompt} -"
    suffix = "-—-"
    needed_dashes = total_len - len(prefix) - len(suffix)
    if needed_dashes < 1:
        needed_dashes = 1
    return f"{prefix}{'—' * needed_dashes}{suffix}"


def justify_dot_leader(key: str, value: str, total_len: int = TARGET_LINE_WIDTH) -> tuple[str, str, str]:
    """
    Computes exact dot count so '. Key: ........ Value' equals total_len.
    Calculates on unescaped text so entities don't disrupt alignment.
    Returns (key, dots_str, value).
    """
    prefix = f". {key}:"
    raw_val = value.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    remaining = total_len - len(prefix) - len(raw_val)
    if remaining <= 2:
        dots = " " * max(1, remaining)
    else:
        dots = " " + ("." * (remaining - 2)) + " "
    return key, dots, value


def build_svg_lines(config: dict, stats: dict) -> list[dict]:
    """Generates structured line descriptors for the right column."""
    lines: list[dict] = []

    prompt = config.get("user", {}).get("prompt_header", "humam@workstation")
    lines.append({
        "type": "header",
        "text": format_header_line(prompt),
    })

    # System Info
    for item in config.get("system_info", []):
        key, dots, val = justify_dot_leader(item["key"], item["value"])
        lines.append({
            "type": "kv",
            "key": key,
            "dots": dots,
            "val": val,
        })

    # Uptime if configured
    if config.get("telemetry", {}).get("show_uptime", True):
        start_date = config.get("telemetry", {}).get("uptime_start_date", "2020-09-20")
        uptime_val = calculate_uptime(start_date)
        key, dots, val = justify_dot_leader("Uptime", uptime_val)
        lines.append({
            "type": "kv",
            "key": key,
            "dots": dots,
            "val": val,
            "id_dots": "age_data_dots",
            "id_val": "age_data",
        })

    # Blank spacer
    lines.append({"type": "spacer"})

    # Skills
    for skill in config.get("skills", []):
        key, dots, val = justify_dot_leader(skill["category"], skill["items"])
        lines.append({
            "type": "kv",
            "key": key,
            "dots": dots,
            "val": val,
        })

    # Blank spacer
    lines.append({"type": "spacer"})

    # Featured Projects
    projects = config.get("featured_projects", [])
    if projects:
        lines.append({
            "type": "divider",
            "text": format_divider("Featured Projects"),
        })
        for p in projects:
            repo_name = p.get("repo", "")
            desc = p.get("description", "")
            key, dots, val = justify_dot_leader(repo_name, desc)
            lines.append({
                "type": "kv",
                "key": key,
                "dots": dots,
                "val": val,
            })
        lines.append({"type": "spacer"})

    # Contact
    contacts = config.get("contacts", [])
    if contacts:
        lines.append({
            "type": "divider",
            "text": format_divider("Contact"),
        })
        for c in contacts:
            key, dots, val = justify_dot_leader(c["label"], c["value"])
            lines.append({
                "type": "kv",
                "key": key,
                "dots": dots,
                "val": val,
            })
        lines.append({"type": "spacer"})

    # GitHub Stats
    if config.get("telemetry", {}).get("show_github_stats", True):
        lines.append({
            "type": "divider",
            "text": format_divider("GitHub Stats"),
        })

        repos_str = f"{stats['repos']:,}"
        contrib_str = f"{stats['contributed']:,}"
        stars_str = f"{stats['stars']:,}"
        lines.append({
            "type": "stats_repos_stars",
            "repos": repos_str,
            "contrib": contrib_str,
            "stars": stars_str,
        })

        commits_str = f"{stats['commits']:,}"
        followers_str = f"{stats['followers']:,}"
        lines.append({
            "type": "stats_commits_followers",
            "commits": commits_str,
            "followers": followers_str,
        })

        if config.get("telemetry", {}).get("show_loc", True):
            loc_tot = f"{stats['loc_total']:,}"
            loc_add = f"{stats['loc_add']:,}"
            loc_del = f"{stats['loc_del']:,}"
            lines.append({
                "type": "stats_loc",
                "loc_total": loc_tot,
                "loc_add": loc_add,
                "loc_del": loc_del,
            })

    return lines


def render_svg(lines: list[dict], ascii_lines: list[str], theme: str) -> str:
    """Renders full SVG matching Andrew6rant theme specs."""
    is_dark = theme == "dark"

    bg_color = "#161b22" if is_dark else "#f6f8fa"
    main_text_color = "#c9d1d9" if is_dark else "#24292f"
    key_color = "#ffa657" if is_dark else "#953800"
    val_color = "#a5d6ff" if is_dark else "#0a3069"
    cc_color = "#616e7f" if is_dark else "#c2cfde"
    add_color = "#3fb950" if is_dark else "#1a7f37"
    del_color = "#f85149" if is_dark else "#cf222e"

    max_rows = max(len(lines), len(ascii_lines))
    height = Y_START + (max_rows * LINE_HEIGHT) + 20

    out = []
    out.append("<?xml version='1.0' encoding='UTF-8'?>")
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="{SVG_WIDTH}px" height="{height}px" font-size="16px">')
    out.append("<style>")
    out.append("@font-face {")
    out.append("src: local('Consolas'), local('Consolas Bold');")
    out.append("font-family: 'ConsolasFallback';")
    out.append("font-display: swap;")
    out.append("-webkit-size-adjust: 109%;")
    out.append("size-adjust: 109%;")
    out.append("}")
    out.append(f".key {{fill: {key_color};}}")
    out.append(f".value {{fill: {val_color};}}")
    out.append(f".addColor {{fill: {add_color};}}")
    out.append(f".delColor {{fill: {del_color};}}")
    out.append(f".cc {{fill: {cc_color};}}")
    out.append("text, tspan {white-space: pre;}")
    out.append("</style>")
    out.append(f'<rect width="{SVG_WIDTH}px" height="{height}px" fill="{bg_color}" rx="15"/>')

    # Left: ASCII Art
    out.append(f'<text x="{X_ASCII}" y="{Y_START}" fill="{main_text_color}" class="ascii">')
    for i, a_line in enumerate(ascii_lines):
        y = Y_START + (i * LINE_HEIGHT)
        escaped_a = html.escape(a_line)
        out.append(f'<tspan x="{X_ASCII}" y="{y}">{escaped_a}</tspan>')
    out.append("</text>")

    # Right: Telemetry & Content
    out.append(f'<text x="{X_TEXT}" y="{Y_START}" fill="{main_text_color}">')
    for i, row in enumerate(lines):
        y = Y_START + (i * LINE_HEIGHT)
        rtype = row.get("type")

        if rtype in ("header", "divider"):
            t = html.escape(row["text"])
            out.append(f'<tspan x="{X_TEXT}" y="{y}">{t}</tspan>')

        elif rtype == "spacer":
            out.append(f'<tspan x="{X_TEXT}" y="{y}" class="cc">. </tspan>')

        elif rtype == "kv":
            k = html.escape(row["key"])
            d = html.escape(row["dots"])
            v = html.escape(row["val"])
            id_dots = f' id="{row["id_dots"]}"' if "id_dots" in row else ""
            id_val = f' id="{row["id_val"]}"' if "id_val" in row else ""
            out.append(
                f'<tspan x="{X_TEXT}" y="{y}" class="cc">. </tspan>'
                f'<tspan class="key">{k}</tspan>:'
                f'<tspan class="cc"{id_dots}>{d}</tspan>'
                f'<tspan class="value"{id_val}>{v}</tspan>'
            )

        elif rtype == "stats_repos_stars":
            repos = row["repos"]
            contrib = row["contrib"]
            stars = row["stars"]
            raw_len = len(f". Repos:  {repos} {{Contributed: {contrib}}} | Stars:  {stars}")
            dots_total = max(4, TARGET_LINE_WIDTH - raw_len)
            d1_len = max(2, dots_total // 2)
            d2_len = max(2, dots_total - d1_len)
            d1 = " " + ("." * d1_len) + " "
            d2 = " " + ("." * d2_len) + " "

            out.append(
                f'<tspan x="{X_TEXT}" y="{y}" class="cc">. </tspan>'
                f'<tspan class="key">Repos</tspan>:<tspan class="cc" id="repo_data_dots">{d1}</tspan>'
                f'<tspan class="value" id="repo_data">{repos}</tspan> '
                f'{{<tspan class="key">Contributed</tspan>: <tspan class="value" id="contrib_data">{contrib}</tspan>}} | '
                f'<tspan class="key">Stars</tspan>:<tspan class="cc" id="star_data_dots">{d2}</tspan>'
                f'<tspan class="value" id="star_data">{stars}</tspan>'
            )

        elif rtype == "stats_commits_followers":
            commits = row["commits"]
            followers = row["followers"]
            raw_len = len(f". Commits:  {commits} | Followers:  {followers}")
            dots_total = max(4, TARGET_LINE_WIDTH - raw_len)
            d1_len = max(4, int(dots_total * 0.65))
            d2_len = max(2, dots_total - d1_len)
            d1 = " " + ("." * d1_len) + " "
            d2 = " " + ("." * d2_len) + " "

            out.append(
                f'<tspan x="{X_TEXT}" y="{y}" class="cc">. </tspan>'
                f'<tspan class="key">Commits</tspan>:<tspan class="cc" id="commit_data_dots">{d1}</tspan>'
                f'<tspan class="value" id="commit_data">{commits}</tspan> | '
                f'<tspan class="key">Followers</tspan>:<tspan class="cc" id="follower_data_dots">{d2}</tspan>'
                f'<tspan class="value" id="follower_data">{followers}</tspan>'
            )

        elif rtype == "stats_loc":
            loc_tot = row["loc_total"]
            loc_add = row["loc_add"]
            loc_del = row["loc_del"]
            raw_len = len(f". Lines of Code on GitHub: {loc_tot} ( {loc_add}++, {loc_del}-- )")
            dots_len = max(1, TARGET_LINE_WIDTH - raw_len)
            dots = "." * dots_len if dots_len > 1 else ""

            out.append(
                f'<tspan x="{X_TEXT}" y="{y}" class="cc">. </tspan>'
                f'<tspan class="key">Lines of Code on GitHub</tspan>:<tspan class="cc" id="loc_data_dots">{dots} </tspan>'
                f'<tspan class="value" id="loc_data">{loc_tot}</tspan> '
                f'( <tspan class="addColor" id="loc_add">{loc_add}++</tspan>, '
                f'<tspan class="delColor" id="loc_del">{loc_del}--</tspan> )'
            )

    out.append("</text>")
    out.append("</svg>")
    return "\n".join(out) + "\n"


def update_readme(username: str) -> None:
    """Updates README.md with the clean native <picture> tag."""
    content = f"""<a href="https://github.com/{username}">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="dark_mode.svg">
    <img alt="{username}'s GitHub Profile README" src="light_mode.svg">
  </picture>
</a>
"""
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    log_ok("README.md updated with native <picture> dual-theme embed.")


def main() -> int:
    if "--configure" in sys.argv or "--wizard" in sys.argv:
        from scripts.configure_profile import main as wizard_main
        return wizard_main()

    log_info("Starting Andrew6rant Neofetch Profile Builder...")

    if not CONFIG_PATH.is_file():
        log_err(f"Config file not found at {CONFIG_PATH}")
        return 1

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    username = config.get("user", {}).get("username", "humam-hossain")
    ascii_art = config.get("ascii_art", DEFAULT_ASCII_ART)

    cache = load_cache()
    token = get_token()
    stats = fetch_stats(username, token, cache)

    cache["totals"] = {
        "additions": stats["loc_add"],
        "deletions": stats["loc_del"],
        "last_updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    save_cache(cache)

    lines = build_svg_lines(config, stats)

    dark_svg = render_svg(lines, ascii_art, "dark")
    light_svg = render_svg(lines, ascii_art, "light")

    # Write to root
    with open(DARK_SVG_PATH, "w", encoding="utf-8") as f:
        f.write(dark_svg)
    log_ok(f"Generated {DARK_SVG_PATH} ({len(dark_svg)} bytes)")

    with open(LIGHT_SVG_PATH, "w", encoding="utf-8") as f:
        f.write(light_svg)
    log_ok(f"Generated {LIGHT_SVG_PATH} ({len(light_svg)} bytes)")

    # Mirror to assets/ for backwards compatibility
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(DARK_SVG_PATH, ASSETS_DIR / "dark_mode.svg")
    shutil.copyfile(LIGHT_SVG_PATH, ASSETS_DIR / "light_mode.svg")

    update_readme(username)

    log_ok("Profile build complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
