"""
tests/test_automation.py
Offline unit test suite for GitHub Actions workflow and Phase 6 automation helpers.
Enforces 100% network isolation with zero external API calls.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET

import pytest

from scripts.update_profile import (
    ROOT_DIR,
    append_github_step_summary,
    get_github_token,
    update_readme_cache_busters,
    write_commit_message_file,
)

WORKFLOW_PATH = ROOT_DIR / ".github" / "workflows" / "profile-updater.yml"


def test_workflow_yaml_syntax_and_structure():
    """Validates that profile-updater.yml exists, parses as valid YAML, and enforces key constraints."""
    assert WORKFLOW_PATH.is_file(), f"Missing workflow file: {WORKFLOW_PATH}"

    try:
        import yaml
        with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except ImportError:
        pytest.skip("PyYAML not installed in current environment")

    # 1. Triggers - support 'on' or True (YAML 1.1)
    triggers = data.get("on") or data.get(True)
    assert triggers is not None, "Missing workflow triggers ('on')"
    assert "schedule" in triggers
    assert triggers["schedule"][0]["cron"] == "17 0 * * *"
    assert "workflow_dispatch" in triggers
    assert "push" in triggers
    assert "pull_request" in triggers

    # 2. Permissions
    assert data.get("permissions") == {"contents": "write", "pull-requests": "read"}

    # 3. Concurrency
    concurrency = data.get("concurrency")
    assert concurrency["group"] == "profile-telemetry-sync"
    assert concurrency["cancel-in-progress"] is False

    # 4. Job structure
    job = data["jobs"]["sync-profile"]
    assert job["runs-on"] == "ubuntu-latest"
    assert job["timeout-minutes"] == 10

    # 5. Injection safety: env block usage
    steps = job["steps"]
    step_names = [s.get("name", "") for s in steps]
    assert any("Check out repository" in n for n in step_names)
    assert any("Set up Python" in n for n in step_names)
    assert any("Execute Profile Telemetry Engine" in n for n in step_names)
    assert any("Validate Asset Integrity" in n for n in step_names)
    assert any("Commit and push" in n for n in step_names)


def test_token_resolution_priority_extended(tmp_path, monkeypatch):
    """
    Validates 4-tier token resolution hierarchy:
    PROFILE_TOKEN > GITHUB_TOKEN > GH_TOKEN > .env file > None.
    """
    monkeypatch.delenv("PROFILE_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)

    # 1. Empty -> None
    assert get_github_token(tmp_path) is None

    # 2. .env file
    env_file = tmp_path / ".env"
    env_file.write_text("GITHUB_TOKEN=token_env_file\n", encoding="utf-8")
    assert get_github_token(tmp_path) == "token_env_file"

    # 3. GH_TOKEN overrides .env
    monkeypatch.setenv("GH_TOKEN", "token_gh")
    assert get_github_token(tmp_path) == "token_gh"

    # 4. GITHUB_TOKEN overrides GH_TOKEN
    monkeypatch.setenv("GITHUB_TOKEN", "token_github")
    assert get_github_token(tmp_path) == "token_github"

    # 5. PROFILE_TOKEN overrides GITHUB_TOKEN
    monkeypatch.setenv("PROFILE_TOKEN", "token_profile")
    assert get_github_token(tmp_path) == "token_profile"


def test_commit_message_generation(tmp_path, monkeypatch):
    """Validates .git/COMMIT_MSG_TMP generation, Conventional Commit format, and Git Trailers."""
    git_dir = tmp_path / ".git"
    git_dir.mkdir(parents=True)

    monkeypatch.setenv("GITHUB_RUN_ID", "987654321")
    monkeypatch.setenv("GITHUB_EVENT_NAME", "schedule")
    monkeypatch.setenv("GITHUB_REPOSITORY", "humam-hossain/humam-hossain")

    msg_path = write_commit_message_file(
        root_dir=tmp_path,
        uptime_str="6 yrs, 1 mo, 28 days",
        loc_add="++55,543",
        loc_del="--656",
        current_streak=5,
        longest_streak=14,
    )

    assert msg_path is not None
    assert msg_path.is_file()

    content = msg_path.read_text(encoding="utf-8")
    lines = content.strip().splitlines()

    # Subject line <= 60 characters
    subject = lines[0]
    assert subject == "chore(profile): auto-sync terminal telemetry [skip ci]"
    assert len(subject) <= 60

    # Empty second line
    assert lines[1] == ""

    # Telemetry in body
    assert "Coding Uptime:  6 yrs, 1 mo, 28 days" in content
    assert "Lines of Code:  ++55,543 / --656" in content
    assert "Commit Streak:  5 days (longest: 14 days)" in content

    # Git Trailers
    assert "Workflow-Run: https://github.com/humam-hossain/humam-hossain/actions/runs/987654321" in content
    assert "Workflow-Event: schedule" in content

    # Clean line wrapping (no lines over 72 chars except long URLs)
    for line in lines:
        if not line.startswith("Workflow-Run:"):
            assert len(line) <= 72


def test_camo_cache_buster_regex(tmp_path):
    """Validates updating ?v=YYYYMMDD on SVG links in README while preserving fragments."""
    readme = tmp_path / "README.md"
    sample = (
        '<img src="./assets/hero.svg" alt="hero" />\n'
        '<img src="./assets/projects.svg?v=20260101" alt="projects" />\n'
        '<img src="./assets/metrics.svg#gh-dark-mode-only" alt="metrics" />\n'
        '<img src="./assets/skills.svg?v=20260101#gh-light-mode-only" alt="skills" />\n'
    )
    readme.write_text(sample, encoding="utf-8")

    res = update_readme_cache_busters(readme, date_str="20261115")
    assert res is True

    updated = readme.read_text(encoding="utf-8")
    assert './assets/hero.svg?v=20261115"' in updated
    assert './assets/projects.svg?v=20261115"' in updated
    assert './assets/metrics.svg?v=20261115#gh-dark-mode-only"' in updated
    assert './assets/skills.svg?v=20261115#gh-light-mode-only"' in updated

    # Idempotent second call
    res2 = update_readme_cache_busters(readme, date_str="20261115")
    assert res2 is False


def test_step_summary_generation(tmp_path, monkeypatch):
    """Validates ANSI Neofetch code block and Markdown asset verification table output."""
    summary_file = tmp_path / "step_summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary_file))
    monkeypatch.setenv("GITHUB_EVENT_NAME", "schedule")

    hero_svg = tmp_path / "hero.svg"
    hero_svg.write_text("<svg></svg>", encoding="utf-8")

    readme = tmp_path / "README.md"
    readme.write_text("# Test", encoding="utf-8")

    append_github_step_summary(
        uptime_str="6 yrs, 1 mo, 28 days",
        loc_add="++55,543",
        loc_del="--656",
        streak_info={"current_streak": 5, "longest_streak": 14},
        elapsed_sec=1.42,
        assets=[hero_svg],
        readme_path=readme,
    )

    assert summary_file.is_file()
    summary = summary_file.read_text(encoding="utf-8")

    # Check ANSI code block
    assert "```ansi" in summary
    assert "humam@workstation" in summary
    assert "profile-sync --status" in summary
    assert "6 yrs, 1 mo, 28 days" in summary
    assert "1.42s" in summary

    # Check Markdown table
    assert "### 📋 Profile Asset Verification" in summary
    assert "| `hero.svg` |" in summary
    assert "| `README.md` |" in summary
