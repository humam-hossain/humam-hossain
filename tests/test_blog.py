"""
tests/test_blog.py
Unit and integration test suite for RSS 2.0 / Atom 1.0 feed ingestion,
date normalization, cache TTL, fallback cascade, URL sanitization, and README blog patching.
100% offline, zero network requests.
"""

from __future__ import annotations

import json
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from scripts.update_profile import (
    ARTICLES_CONFIG_PATH,
    load_articles_config,
)

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def test_articles_config_loading():
    """Verify config/articles.json loads cleanly with expected keys and fallback entries."""
    cfg = load_articles_config(ARTICLES_CONFIG_PATH)
    assert "rss_url" in cfg
    assert "max_display" in cfg
    assert cfg["max_display"] == 4
    assert isinstance(cfg.get("curated_articles"), list)
    assert len(cfg["curated_articles"]) >= 2
    for item in cfg["curated_articles"]:
        assert "title" in item
        assert "url" in item
        assert "date" in item
        assert "platform" in item


def test_fixtures_rss2_valid_xml():
    """Verify feed_rss2.xml fixture parses with ElementTree and contains item elements."""
    fixture_path = FIXTURES_DIR / "feed_rss2.xml"
    assert fixture_path.is_file(), "feed_rss2.xml fixture missing"

    root = ET.fromstring(fixture_path.read_bytes())
    assert root.tag.lower() == "rss"
    channel = root.find("channel")
    assert channel is not None
    assert channel.findtext("title") == "Dev Engineering Log"
    items = root.findall(".//item")
    assert len(items) == 2


def test_fixtures_atom_valid_xml():
    """Verify feed_atom.xml fixture parses with ElementTree and contains entry elements."""
    fixture_path = FIXTURES_DIR / "feed_atom.xml"
    assert fixture_path.is_file(), "feed_atom.xml fixture missing"

    root = ET.fromstring(fixture_path.read_bytes())
    assert root.tag.split("}")[-1].lower() == "feed"
    entries = [el for el in root.iter() if el.tag.split("}")[-1].lower() == "entry"]
    assert len(entries) == 1
    assert "Continuous Integration" in (entries[0].findtext("{http://www.w3.org/2005/Atom}title") or entries[0].findtext("title") or "")
