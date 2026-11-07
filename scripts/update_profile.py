#!/usr/bin/env python3
"""
scripts/update_profile.py
Automated profile telemetry engine for Muhammed Humam Hossain (humam-hossain).
Standard library only: urllib, json, datetime, xml, calendar, pathlib.
Zero external dependencies.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config" / "terminal_theme.json"
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


def main() -> int:
    """CLI Entry point for profile update engine."""
    log_info("humam@workstation profile updater v1.0.0")
    token = get_github_token(ROOT_DIR)
    if not token:
        log_warn("No token found. Running offline with cached/mock telemetry")
        return 0

    log_ok("GitHub token resolved successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
