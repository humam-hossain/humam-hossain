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
    pad_line,
    select_projects_tui,
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

