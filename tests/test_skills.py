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
    write_svg_idempotent,
)
from scripts.update_profile import update_readme_skills


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


def test_skills_quadrants_and_accents():
    """Assert all 4 quadrant IDs and ANSI accents are present in generated SVG."""
    svg = generate_skills_svg()

    # All 4 quadrant IDs
    assert 'id="quadrant-ai-data-science"' in svg
    assert 'id="quadrant-backend-systems"' in svg
    assert 'id="quadrant-sqa-automation"' in svg
    assert 'id="quadrant-embedded-robotics"' in svg

    # All 4 ANSI accent colors
    assert "#a5d6ff" in svg  # Cyan (AI & Data Science)
    assert "#ffa657" in svg  # Amber (Backend & Systems)
    assert "#3fb950" in svg  # Green (SQA & Automation)
    assert "#d2a8ff" in svg  # Purple (Embedded & Robotics)


def test_skills_pill_wrapping_and_capping():
    """Verify flow-pack pill wrapping and hard capacity capping at 6 skills."""
    test_data = [
        {
            "id": "test-overflow",
            "title": "Overflow Test",
            "accent": "#58a6ff",
            "skills": [
                "SkillOne",
                "SkillTwo",
                "SkillThree",
                "SkillFour",
                "SkillFive",
                "SkillSix",
                "SkillSevenOverflow",
            ],
        }
    ]
    svg = generate_skills_svg(test_data)

    # Skills 1 through 6 should be rendered
    assert "SkillOne" in svg
    assert "SkillSix" in svg

    # Skill 7 must be capped (excluded) to guarantee zero boundary overflow
    assert "SkillSevenOverflow" not in svg

    # XML must still parse cleanly
    root = ET.fromstring(svg)
    pills = root.findall(".//{http://www.w3.org/2000/svg}g[@class='skill-pill']")
    if not pills:
        # Without namespace or local
        pills = [el for el in root.iter() if el.attrib.get("class") == "skill-pill"]
    assert len(pills) == 6


def test_skills_hover_css_and_xml_validity():
    """Verify embedded CSS hover transitions and clean ElementTree parsing."""
    svg = generate_skills_svg()
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")

    # CSS hover styles
    assert ".skill-pill:hover .pill-bg" in svg
    assert ".skill-pill:hover .pill-text" in svg
    assert "transition: transform" in svg


def test_skills_idempotent_write(tmp_path):
    """Verify write_svg_idempotent returns True on new content and False on identical content."""
    test_svg_path = tmp_path / "test_skills.svg"
    content = generate_skills_svg()

    # First write -> True
    assert write_svg_idempotent(test_svg_path, content) is True
    assert test_svg_path.is_file()

    # Second write with identical content -> False (idempotent skip)
    assert write_svg_idempotent(test_svg_path, content) is False


def test_update_readme_skills(tmp_path):
    """Verify README patching between SKILLS markers and idempotent skip."""
    mock_readme = tmp_path / "README.md"
    mock_readme.write_text(
        "# Profile\n\n<!-- SKILLS:START -->\n<!-- SKILLS:END -->\n\nexit\n",
        encoding="utf-8",
    )

    # First run: should patch and return True
    assert update_readme_skills(mock_readme) is True
    content = mock_readme.read_text(encoding="utf-8")
    assert '<img src="./assets/skills.svg"' in content
    assert 'alt="Categorized Skills Matrix"' in content

    # Second run: content is identical, should return False (idempotent)
    assert update_readme_skills(mock_readme) is False


