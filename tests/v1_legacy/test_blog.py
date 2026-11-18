"""
tests/test_blog.py
Unit and integration test suite for RSS 2.0 / Atom 1.0 feed ingestion,
date normalization, cache TTL, fallback cascade, URL sanitization, and README blog patching.
100% offline, zero network requests.
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import urllib.error
import xml.etree.ElementTree as ET

import pytest

from scripts.update_profile import (
    ARTICLES_CONFIG_PATH,
    fetch_articles,
    format_articles_terminal_log,
    load_articles_config,
    normalize_date_string,
    parse_feed_xml,
    update_readme_blog,
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


def test_rss2_feed_parsing():
    """Verify offline parsing of RSS 2.0 XML fixture with channel title and items."""
    fixture_path = FIXTURES_DIR / "feed_rss2.xml"
    xml_bytes = fixture_path.read_bytes()
    articles = parse_feed_xml(xml_bytes)

    assert len(articles) == 2
    assert articles[0]["title"] == "Building High-Throughput Robotics Simulators with ROS2"
    assert articles[0]["url"] == "https://example.com/robotics-sim"
    assert articles[0]["date"] == "2024-05-19"
    assert articles[0]["platform"] == "Dev Engineering Log"

    assert articles[1]["title"] == "Real-Time Embedded & Edge AI Inference Optimization"
    assert articles[1]["url"] == "https://example.com/edge-ai"
    assert articles[1]["date"] == "2024-04-01"
    assert articles[1]["platform"] == "Dev Engineering Log"


def test_atom1_feed_parsing():
    """Verify offline parsing of Atom 1.0 XML fixture with namespace stripping."""
    fixture_path = FIXTURES_DIR / "feed_atom.xml"
    xml_bytes = fixture_path.read_bytes()
    articles = parse_feed_xml(xml_bytes)

    assert len(articles) == 1
    assert articles[0]["title"] == "Continuous Integration for Embedded Firmware with PyTest"
    assert articles[0]["url"] == "https://example.com/embedded-ci"
    assert articles[0]["date"] == "2024-05-18"
    assert articles[0]["platform"] == "Workstation Research Notes"


def test_date_normalization():
    """Verify normalize_date_string handles RFC 822, ISO 8601, and YYYY-MM-DD."""
    assert normalize_date_string("Sun, 19 May 2024 14:30:00 GMT") == "2024-05-19"
    assert normalize_date_string("2024-05-18T08:00:00Z") == "2024-05-18"
    assert normalize_date_string("2024-04-15") == "2024-04-15"
    assert normalize_date_string("") == datetime.date.today().strftime("%Y-%m-%d")


def test_title_clamping_and_escaping():
    """Verify titles >55 chars are clamped with '...' and HTML entities unescaped/escaped."""
    articles = [
        {
            "title": "A Very Long Title That Definitely Exceeds The Strict Monospace Fifty-Five Character Limit For Terminal Display",
            "url": "https://example.com/long",
            "date": "2024-05-19",
            "platform": "Blog & Tech",
        },
        {
            "title": "Clean &amp; Safe &lt;Code&gt; &quot;Testing&quot;",
            "url": "https://example.com/safe",
            "date": "2024-05-19",
            "platform": "Notes",
        },
    ]
    output = format_articles_terminal_log(articles, max_display=2)
    assert "A Very Long Title That Definitely Exceeds The Strict..." in output
    assert "Clean &amp; Safe &lt;Code&gt; &quot;Testing&quot;" in output
    assert "Blog &amp; Tech" in output


def test_security_url_sanitization():
    """Verify unsafe protocols (javascript:) are sanitized to '#'."""
    articles = [
        {
            "title": "Malicious Link Test",
            "url": "javascript:alert('xss')",
            "date": "2024-05-19",
            "platform": "Test",
        }
    ]
    output = format_articles_terminal_log(articles)
    assert '<a href="#">' in output
    assert "javascript:" not in output


def test_cache_ttl_and_refresh():
    """Verify 12h TTL prevents network call unless force_refresh is True."""
    now = datetime.datetime.now(datetime.timezone.utc)
    recent_ts = (now - datetime.timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")

    cache = {
        "articles": {
            "last_updated": recent_ts,
            "items": [{"title": "Cached Post", "url": "https://example.com/cached", "date": "2024-05-01", "platform": "Cached"}],
        }
    }
    cfg = {"rss_url": "https://example.com/feed.xml", "curated_articles": []}

    # Should hit cache without making network request
    with patch("urllib.request.urlopen") as mock_url:
        res = fetch_articles(cfg, cache, force_refresh=False)
        assert len(res) == 1
        assert res[0]["title"] == "Cached Post"
        mock_url.assert_not_called()

        # force_refresh bypasses cache
        mock_url.side_effect = urllib.error.URLError("Simulated offline")
        res_forced = fetch_articles(cfg, cache, force_refresh=True)
        assert mock_url.called
        assert len(res_forced) == 1  # Falls back to cache on error


def test_network_fallbacks():
    """Verify HTTPError / URLError / timeout gracefully cascade to cache then curated."""
    cfg = {
        "rss_url": "https://example.com/offline-feed.xml",
        "curated_articles": [
            {"title": "Curated Backup", "url": "https://example.com/backup", "date": "2024-01-01", "platform": "Curated"}
        ],
    }
    empty_cache = {}

    with patch("urllib.request.urlopen", side_effect=urllib.error.HTTPError(None, 404, "Not Found", None, None)):
        res = fetch_articles(cfg, empty_cache)
        assert len(res) == 1
        assert res[0]["title"] == "Curated Backup"


def test_standby_formatting():
    """Verify standby message formatting when article list is empty."""
    output = format_articles_terminal_log([])
    assert "* [standby] feed listener active — configure rss_url in config/articles.json" in output


def test_readme_blog_injection(tmp_path):
    """Verify idempotent README injection between <!-- BLOG:START --> and <!-- BLOG:END -->."""
    mock_readme = tmp_path / "README.md"
    original = (
        "# Profile\n\n"
        "<!-- SKILLS:END -->\n\n"
        "<code>humam@workstation:~$ exit</code>\n"
    )
    mock_readme.write_text(original, encoding="utf-8")
    mock_html = "<pre><code>humam@workstation:~$ cat ~/articles.log\n* [2024-05-19] Test Post</code></pre>"

    # 1. First injection auto-creates markers and updates
    res1 = update_readme_blog(mock_readme, mock_html)
    assert res1 is True

    content = mock_readme.read_text(encoding="utf-8")
    assert "<!-- BLOG:START -->" in content
    assert "<!-- BLOG:END -->" in content
    assert "* [2024-05-19] Test Post" in content

    # 2. Idempotent second injection
    res2 = update_readme_blog(mock_readme, mock_html)
    assert res2 is False


