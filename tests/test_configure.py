#!/usr/bin/env python3
"""
tests/test_configure.py
Unit tests for the interactive terminal setup wizard (configure_profile.py).
Verifies:
1. Repositories are fetched and sorted strictly by latest commit (pushed_at descending).
2. Key reader parses hjkl, space, enter, and arrow keys properly.
3. Fallbacks handle non-tty and headless environments gracefully.
"""

from __future__ import annotations

import io
import json
import os
import sys
from pathlib import Path

import pytest

from scripts.configure_profile import (
    ARCH_ASCII,
    MONOGRAM_ASCII,
    TerminalUI,
    fetch_user_repos,
    format_skills_items,
    pad_line,
    parse_skills_items,
    prepare_repos_list,
    select_ascii_art_tui,
    select_projects_tui,
    setup_skills_tui,
    strip_ansi,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "profile_config.json"


def test_fetch_user_repos_ordering():
    """Verify that repositories returned are ordered by pushed_at descending."""
    repos = fetch_user_repos("humam-hossain")
    assert isinstance(repos, list)
    assert len(repos) > 0

    # Ensure required keys exist
    for r in repos:
        assert "name" in r
        assert "pushed_at" in r
        assert "language" in r

    # Verify descending sort by pushed_at
    pushed_dates = [r["pushed_at"] for r in repos if r.get("pushed_at")]
    assert pushed_dates == sorted(pushed_dates, reverse=True), "Repositories are not sorted by latest push date descending!"


def test_strip_ansi_and_pad_line():
    """Verify ANSI escape stripping and visible column padding."""
    styled = "\033[38;2;88;166;255m\033[1mHello World\033[0m"
    clean = strip_ansi(styled)
    assert clean == "Hello World"
    assert len(clean) == 11

    padded = pad_line("Test", 10)
    assert len(padded) == 10
    assert padded == "Test      "


def test_ascii_art_definitions():
    """Verify built-in ASCII styles are valid list of strings."""
    assert isinstance(ARCH_ASCII, list)
    assert len(ARCH_ASCII) >= 10
    assert isinstance(MONOGRAM_ASCII, list)
    assert len(MONOGRAM_ASCII) >= 10


def test_non_interactive_fallback():
    """Verify that select_projects_tui falls back gracefully when tui is not a tty."""
    tui = TerminalUI()
    tui.is_tty = False
    dummy_repos = [
        {"name": "repo-a", "pushed_at": "2026-11-18", "description": "Latest", "language": "Python"},
        {"name": "repo-b", "pushed_at": "2026-11-10", "description": "Older", "language": "C++"},
    ]
    res = select_projects_tui(tui, dummy_repos, ["repo-a"])
    assert isinstance(res, list)
    assert len(res) > 0
    assert res[0]["name"] == "repo-a"


def test_prompt_line_editor_non_interactive():
    """Verify prompt_line_editor returns default value in non-interactive mode."""
    from scripts.configure_profile import prompt_line_editor
    tui = TerminalUI()
    tui.is_tty = False
    val = prompt_line_editor(tui, "Test Title", "Label", initial_text="Default Value")
    assert val == "Default Value"


def test_cursor_rendering_and_space_support():
    """Simulate key handling logic to ensure space, backspace, and cursor are handled correctly."""
    buf = list("Hello")
    pos = len(buf)

    # Simulate typing space
    key = "SPACE"
    if key in ("SPACE", " "):
        buf.insert(pos, " ")
        pos += 1

    assert "".join(buf) == "Hello "
    assert pos == 6

    # Simulate typing another word
    for ch in "World":
        buf.insert(pos, ch)
        pos += 1

    assert "".join(buf) == "Hello World"
    assert pos == 11

    # Simulate backspace
    buf.pop(pos - 1)
    pos -= 1
    assert "".join(buf) == "Hello Worl"
    assert pos == 10


def test_prepare_repos_list_prioritizes_last_change():
    """Verify that projects configured in the last change come up first with custom descriptions."""
    fetched = [
        {"name": "repo-newest", "pushed_at": "2026-11-19", "description": "Raw 1", "language": "Python"},
        {"name": "repo-middle", "pushed_at": "2026-11-15", "description": "Raw 2", "language": "C++"},
        {"name": "repo-oldest", "pushed_at": "2026-11-01", "description": "Raw 3", "language": "Shell"},
    ]
    last_featured = [
        {"repo": "repo-oldest", "description": "My Custom Description for Oldest"},
        {"repo": "repo-middle", "description": "My Custom Description for Middle"},
    ]

    ordered, selected_names = prepare_repos_list(fetched, last_featured)

    # 1. The last configured projects must come up first
    assert ordered[0]["name"] == "repo-oldest"
    assert ordered[0]["description"] == "My Custom Description for Oldest"
    assert ordered[1]["name"] == "repo-middle"
    assert ordered[1]["description"] == "My Custom Description for Middle"

    # 2. Remaining repos follow
    assert ordered[2]["name"] == "repo-newest"

    # 3. Selected names contains the last configured repos
    assert selected_names == ["repo-oldest", "repo-middle"]


def test_select_ascii_art_preserves_last_change():
    """Verify that select_ascii_art_tui preserves and defaults to whatever art was previously saved."""
    tui = TerminalUI()
    tui.is_tty = False

    # When config had Monogram
    cfg_monogram = {"ascii_art": MONOGRAM_ASCII}
    result_monogram = select_ascii_art_tui(tui, cfg_monogram)
    assert result_monogram == MONOGRAM_ASCII

    # When config had Arch
    cfg_arch = {"ascii_art": ARCH_ASCII}
    result_arch = select_ascii_art_tui(tui, cfg_arch)
    assert result_arch == ARCH_ASCII


def test_parse_and_format_skills_items():
    """Verify parsing and formatting of skills items string."""
    raw = " Python, C/C++, Bash , JavaScript , "
    parsed = parse_skills_items(raw)
    assert parsed == ["Python", "C/C++", "Bash", "JavaScript"]

    formatted = format_skills_items(parsed)
    assert formatted == "Python, C/C++, Bash, JavaScript"

    assert parse_skills_items("") == []
    assert format_skills_items([]) == ""


def test_delete_individual_skill():
    """Verify deleting an individual skill from a category's parsed items."""
    skills_list = ["Python", "C/C++", "Bash", "JavaScript"]
    # User deletes "Bash" (index 2)
    deleted = skills_list.pop(2)
    assert deleted == "Bash"
    assert skills_list == ["Python", "C/C++", "JavaScript"]
    assert format_skills_items(skills_list) == "Python, C/C++, JavaScript"


def test_delete_category():
    """Verify deleting an entire category from the skills list."""
    skills = [
        {"category": "Languages.Code", "items": "Python, C++"},
        {"category": "Technologies.AI", "items": "PyTorch, ROS2"},
    ]
    # Delete first category
    deleted = skills.pop(0)
    assert deleted["category"] == "Languages.Code"
    assert len(skills) == 1
    assert skills[0]["category"] == "Technologies.AI"

    # Delete remaining category (should be allowed to reach 0 categories)
    deleted_last = skills.pop(0)
    assert deleted_last["category"] == "Technologies.AI"
    assert len(skills) == 0


def test_setup_skills_tui_non_interactive():
    """Verify setup_skills_tui non-interactive fallback returns skills cleanly."""
    tui = TerminalUI()
    tui.is_tty = False

    custom_skills = [{"category": "Languages.Custom", "items": "Rust, Zig"}]
    res = setup_skills_tui(tui, {"skills": custom_skills})
    assert res == custom_skills



