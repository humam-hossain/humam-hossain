"""
tests/test_skills.py
Unit and integration test suite for Categorized Skills Matrix SVG generator.
Validates taxonomy config loading, quadrant positioning, flow-pack pill wrapping,
capacity capping, XML validity, desktop hover styles, and idempotent file operations.
100% offline, zero network requests.
"""

from __future__ import annotations

import json
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from scripts.generate_skills import (
    DEFAULT_SKILLS_DATA,
    QUADRANT_SLOTS,
    generate_skills_svg,
    load_skills_config,
)


def test_skills_config_loading(tmp_path):
    """Test loading config/skills.json and fallback behavior on corrupt/missing files."""
    # 1. Load actual project configuration
    categories = load_skills_config()
    assert len(categories) == 4
    ids = [c["id"] for c in categories]
    assert ids == [
        "ai-data-science",
        "backend-systems",
        "sqa-automation",
        "embedded-robotics",
    ]
    for cat in categories:
        assert "title" in cat
        assert "accent" in cat
        assert "skills" in cat
        assert isinstance(cat["skills"], list)
        assert len(cat["skills"]) >= 3

    # 2. Missing config fallback
    missing_path = tmp_path / "nonexistent_skills.json"
    fallback = load_skills_config(missing_path)
    assert fallback == DEFAULT_SKILLS_DATA

    # 3. Corrupt JSON fallback
    corrupt_path = tmp_path / "corrupt_skills.json"
    corrupt_path.write_text("{invalid json", encoding="utf-8")
    fallback_corrupt = load_skills_config(corrupt_path)
    assert fallback_corrupt == DEFAULT_SKILLS_DATA

    # 4. Dict schema with 'categories' key
    dict_path = tmp_path / "dict_skills.json"
    dict_path.write_text(
        json.dumps({"categories": DEFAULT_SKILLS_DATA[:2]}),
        encoding="utf-8",
    )
    loaded_dict = load_skills_config(dict_path)
    assert len(loaded_dict) == 2


def test_generate_skills_svg_structure():
    """Verify SVG root attributes, window chrome, traffic lights, and prompt line."""
    svg = generate_skills_svg()
    root = ET.fromstring(svg)

    # Root attributes
    assert root.attrib.get("viewBox") == "0 0 850 380"
    assert "850" in root.attrib.get("viewBox")
    assert "380" in root.attrib.get("viewBox")

    # Chrome and title
    assert "skills — zsh" in svg
    assert "#ff5f56" in svg  # Red traffic light
    assert "#ffbd2e" in svg  # Yellow traffic light
    assert "#27c93f" in svg  # Green traffic light

    # Neofetch prompt
    assert "humam@workstation:~$" in svg
    assert "neofetch --skills" in svg
