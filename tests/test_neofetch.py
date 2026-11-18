"""
tests/test_neofetch.py
Unit and integration tests for Andrew6rant-style Neofetch profile architecture (v2.0).
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import pytest

from scripts.build_profile import (
    CONFIG_PATH,
    DARK_SVG_PATH,
    LIGHT_SVG_PATH,
    README_PATH,
    TARGET_LINE_WIDTH,
    calculate_uptime,
    format_divider,
    format_header_line,
    justify_dot_leader,
    main as build_main,
)


def test_profile_config_structure():
    """Verify profile_config.json contains all required fields."""
    assert CONFIG_PATH.is_file(), "profile_config.json must exist"
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    assert "user" in config
    assert "username" in config["user"]
    assert "system_info" in config
    assert "skills" in config
    assert "featured_projects" in config
    assert "contacts" in config
    assert "telemetry" in config


def test_dot_leader_calculation():
    """Verify dot leader calculation yields exact target line width."""
    key = "OS"
    val = "Arch Linux x86_64, Ubuntu"
    k, dots, v = justify_dot_leader(key, val, TARGET_LINE_WIDTH)
    line = f". {k}:{dots}{v}"
    assert len(line) == TARGET_LINE_WIDTH


def test_divider_formatting():
    """Verify section dividers reach exactly target line width."""
    divider = format_divider("Featured Projects", TARGET_LINE_WIDTH)
    assert len(divider) == TARGET_LINE_WIDTH
    assert divider.startswith("- Featured Projects -")
    assert divider.endswith("-—-")


def test_header_line_formatting():
    """Verify top header line reaches exactly target line width."""
    header = format_header_line("humam@workstation", TARGET_LINE_WIDTH)
    assert len(header) == TARGET_LINE_WIDTH
    assert header.startswith("humam@workstation -")


def test_uptime_calculation():
    """Verify uptime calculation returns formatted string."""
    uptime = calculate_uptime("2020-09-20")
    assert "year" in uptime
    assert "month" in uptime
    assert "day" in uptime


def test_build_execution_and_xml_validity():
    """Verify build script executes with exit code 0 and produces valid SVGs."""
    exit_code = build_main()
    assert exit_code == 0

    assert DARK_SVG_PATH.is_file()
    assert LIGHT_SVG_PATH.is_file()

    # XML validity
    dark_tree = ET.parse(DARK_SVG_PATH)
    light_tree = ET.parse(LIGHT_SVG_PATH)

    assert dark_tree.getroot().tag.endswith("svg")
    assert light_tree.getroot().tag.endswith("svg")

    dark_content = DARK_SVG_PATH.read_text(encoding="utf-8")
    light_content = LIGHT_SVG_PATH.read_text(encoding="utf-8")

    # Dark mode colors
    assert 'fill="#161b22"' in dark_content
    assert ".key {fill: #ffa657;}" in dark_content
    assert ".value {fill: #a5d6ff;}" in dark_content

    # Light mode colors
    assert 'fill="#f6f8fa"' in light_content
    assert ".key {fill: #953800;}" in light_content
    assert ".value {fill: #0a3069;}" in light_content

    # No macOS traffic lights
    assert "traffic_lights" not in dark_content
    assert "#ff5f56" not in dark_content  # Red dot
    assert "#ffbd2e" not in dark_content  # Yellow dot
    assert "#27c93f" not in dark_content  # Green dot


def test_readme_picture_tag():
    """Verify README contains only native <picture> tag without badges or fake logs."""
    content = README_PATH.read_text(encoding="utf-8")
    assert "<picture>" in content
    assert '<source media="(prefers-color-scheme: dark)" srcset="dark_mode.svg">' in content
    assert '<img alt="humam-hossain\'s GitHub Profile README" src="light_mode.svg">' in content

    # Purged elements
    assert "komarev.com/ghpvc" not in content
    assert "shields.io" not in content
    assert "cat ~/articles.log" not in content
    assert "git log --graph" not in content
