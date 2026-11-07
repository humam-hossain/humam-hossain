"""
tests/test_tokens.py
Pytest suite validating terminal theme tokens, SVG generator output, and README layout.
"""

import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import pytest

try:
    from scripts.generate_hero import generate_svg
except (ImportError, ModuleNotFoundError):
    generate_svg = None

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config" / "terminal_theme.json"
HERO_SVG_PATH = ROOT_DIR / "assets" / "hero.svg"
README_PATH = ROOT_DIR / "README.md"

HEX_REGEX = re.compile(r"^#[0-9a-fA-F]{6}$")


def test_theme_tokens_schema():
    assert CONFIG_PATH.exists(), "config/terminal_theme.json must exist"
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        theme = json.load(f)

    # Required top-level sections
    assert "geometry" in theme, "Missing 'geometry' section in theme"
    assert "colors" in theme, "Missing 'colors' section in theme"
    assert "typography" in theme, "Missing 'typography' section in theme"

    # Verify colors are valid hex codes
    c = theme["colors"]
    assert HEX_REGEX.match(c["background"]["header"]), f"Invalid header bg hex: {c['background']['header']}"
    assert HEX_REGEX.match(c["background"]["body"]), f"Invalid body bg hex: {c['background']['body']}"
    assert HEX_REGEX.match(c["border"]), f"Invalid border hex: {c['border']}"
    for key, hex_code in c["text"].items():
        assert HEX_REGEX.match(hex_code), f"Invalid hex for text.{key}: {hex_code}"
    for hex_code in c["ansi"]:
        assert HEX_REGEX.match(hex_code), f"Invalid ANSI hex: {hex_code}"
    assert len(c["ansi"]) == 8, "ANSI palette must contain exactly 8 diagnostic colors"


def test_hero_svg_generation():
    if generate_svg is None and not HERO_SVG_PATH.exists():
        pytest.skip("scripts/generate_hero.py not yet implemented and assets/hero.svg does not exist")
    svg_content = generate_svg() if generate_svg is not None else HERO_SVG_PATH.read_text(encoding="utf-8")
    root = ET.fromstring(svg_content)
    assert root.tag == "{http://www.w3.org/2000/svg}svg" or root.tag == "svg"
    assert root.attrib.get("viewBox") == "0 0 850 380"


def test_hero_svg_monogram_and_ansi():
    if not HERO_SVG_PATH.exists():
        if generate_svg is None:
            pytest.skip("scripts/generate_hero.py not yet implemented and assets/hero.svg does not exist")
        svg_content = generate_svg()
    else:
        with open(HERO_SVG_PATH, "r", encoding="utf-8") as f:
            svg_content = f.read()

    root = ET.fromstring(svg_content)
    # Check block glyphs in monogram
    assert "█" in svg_content
    assert "▄" in svg_content
    assert "▀" in svg_content
    assert "_" in svg_content

    # Check ANSI circle count
    circles = root.findall(".//{http://www.w3.org/2000/svg}circle")
    if not circles:
        circles = root.findall(".//circle")
    # 3 traffic lights + 8 ANSI dots = 11 circles
    assert len(circles) >= 11


def test_hero_svg_telemetry_keys():
    if not HERO_SVG_PATH.exists():
        if generate_svg is None:
            pytest.skip("scripts/generate_hero.py not yet implemented and assets/hero.svg does not exist")
        svg_content = generate_svg()
    else:
        with open(HERO_SVG_PATH, "r", encoding="utf-8") as f:
            svg_content = f.read()

    root = ET.fromstring(svg_content)
    # Assert telemetry keys
    for key in ["OS:", "Host:", "Kernel:", "Focus:", "Uptime:", "Shell:", "Contact:", "LOC:"]:
        assert key in svg_content, f"Missing telemetry key: {key}"

    # Verify XML escaped ampersand
    assert "AI &amp; Robotics" in svg_content
    assert "Autonomous Systems, IoT &amp; Cloud" in svg_content

    # Verify Phase 2 DOM update IDs
    assert root.find(".//*[@id='val-uptime']") is not None
    assert root.find(".//*[@id='val-loc-add']") is not None
    assert root.find(".//*[@id='val-loc-del']") is not None


def test_readme_structure():
    assert README_PATH.exists(), "README.md must exist"
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Image embed
    assert '<img src="./assets/hero.svg"' in content
    assert 'alt="humam@workstation"' in content

    # Flat-square Shields.io badges
    assert "img.shields.io/badge" in content
    assert "style=flat-square" in content
    assert "161b22" in content
    assert "./cv/outputs/cv_humam_hossain.pdf" in content

    # Phase anchors
    assert "<!-- PROJECTS:START -->" in content
    assert "<!-- PROJECTS:END -->" in content
    assert "<!-- METRICS:START -->" in content
    assert "<!-- METRICS:END -->" in content
    assert "<!-- SKILLS:START -->" in content
    assert "<!-- SKILLS:END -->" in content

    # Exit prompt
    assert "humam@workstation:~$ exit" in content
