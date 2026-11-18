"""
tests/test_metrics.py
Unit and integration test suite for Languages, Streaks & Metrics Telemetry Engine.
Enforces 100% network isolation with zero external API calls.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import xml.etree.ElementTree as ET

import pytest

import datetime

from scripts.generate_metrics import (
    DEFAULT_STREAK_FIXTURES as GEN_STREAK_FIXTURES,
    DEFAULT_LANGUAGE_FIXTURES as GEN_LANG_FIXTURES,
    generate_metrics_svg,
)
from scripts.update_profile import (
    BOT_AUTHORS,
    DEFAULT_ACTIVITY_FIXTURES,
    DEFAULT_LANGUAGE_FIXTURES,
    DEFAULT_STREAK_FIXTURES,
    FILTER_PREFIXES,
    VISITOR_BADGE_MARKDOWN,
    aggregate_top_languages,
    compute_relative_time_str,
    compute_streaks_from_calendar,
    fetch_language_telemetry,
    fetch_recent_activity,
    fetch_streak_telemetry,
    format_git_activity_stream,
    main as update_profile_main,
    update_readme_badges,
    update_readme_metrics,
)

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def test_fixtures_calendar_valid_json():
    """Verify tests/fixtures/graphql_calendar.json exists and has valid calendar structure."""
    fixture_path = FIXTURES_DIR / "graphql_calendar.json"
    assert fixture_path.is_file(), "Missing graphql_calendar.json fixture"

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "data" in data
    assert "viewer" in data["data"]
    assert "contributionsCollection" in data["data"]["viewer"]
    calendar = data["data"]["viewer"]["contributionsCollection"]["contributionCalendar"]
    assert "totalContributions" in calendar
    assert "weeks" in calendar
    assert isinstance(calendar["weeks"], list)
    assert len(calendar["weeks"]) > 0


def test_fixtures_languages_valid_json():
    """Verify tests/fixtures/graphql_languages.json exists and contains repository language nodes."""
    fixture_path = FIXTURES_DIR / "graphql_languages.json"
    assert fixture_path.is_file(), "Missing graphql_languages.json fixture"

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "data" in data
    assert "viewer" in data["data"]
    assert "repositories" in data["data"]["viewer"]
    nodes = data["data"]["viewer"]["repositories"]["nodes"]
    assert isinstance(nodes, list)
    assert len(nodes) > 0
    first_repo = nodes[0]
    assert "name" in first_repo
    assert "isFork" in first_repo
    assert "languages" in first_repo
    assert "edges" in first_repo["languages"]


def test_fixtures_events_valid_json():
    """Verify tests/fixtures/rest_events.json exists, loads valid JSON array, and contains PushEvents."""
    fixture_path = FIXTURES_DIR / "rest_events.json"
    assert fixture_path.is_file(), "Missing rest_events.json fixture"

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) > 0
    push_events = [e for e in data if e.get("type") == "PushEvent"]
    assert len(push_events) >= 2
    for event in push_events:
        assert "actor" in event
        assert "repo" in event
        assert "payload" in event
        assert "commits" in event["payload"]


def test_language_aggregation_percentages():
    """Verify aggregate_top_languages accurately calculates percentages on fixture data."""
    fixture_path = FIXTURES_DIR / "graphql_languages.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    nodes = data["data"]["viewer"]["repositories"]["nodes"]

    languages = aggregate_top_languages(nodes)
    assert len(languages) == 3
    names = [l["name"] for l in languages]
    assert names == ["Python", "Shell", "C"]

    # Verify Markdown was excluded
    assert "Markdown" not in names

    # Percentages check: 65k / 125k = 52.0%, 42k / 125k = 33.6%, 18k / 125k = 14.4%
    total_pct = sum(l["percentage"] for l in languages)
    assert pytest.approx(total_pct, 0.1) == 100.0
    assert languages[0]["percentage"] == 52.0
    assert languages[1]["percentage"] == 33.6
    assert languages[2]["percentage"] == 14.4


def test_language_ignore_list_filtering():
    """Verify that ignored languages (HTML, CSS, TeX, Markdown) are filtered out."""
    nodes = [
        {
            "name": "web-app",
            "isFork": False,
            "languages": {
                "edges": [
                    {"size": 10000, "node": {"name": "JavaScript", "color": "#f1e05a"}},
                    {"size": 8000, "node": {"name": "HTML", "color": "#e34c26"}},
                    {"size": 6000, "node": {"name": "CSS", "color": "#563d7c"}},
                    {"size": 4000, "node": {"name": "TeX", "color": "#3D6117"}},
                    {"size": 2000, "node": {"name": "Markdown", "color": "#083fa1"}},
                ]
            },
        }
    ]

    languages = aggregate_top_languages(nodes, ignore_list=["HTML", "CSS", "TeX", "Markdown"])
    assert len(languages) == 1
    assert languages[0]["name"] == "JavaScript"
    assert languages[0]["percentage"] == 100.0


def test_language_other_row_roll_up():
    """Verify that languages beyond top 5 roll up into 'Other' if remainder >= 1%."""
    nodes = [
        {
            "name": "multi-lang-repo",
            "isFork": False,
            "languages": {
                "edges": [
                    {"size": 50000, "node": {"name": "Lang1", "color": "#111111"}},
                    {"size": 20000, "node": {"name": "Lang2", "color": "#222222"}},
                    {"size": 15000, "node": {"name": "Lang3", "color": "#333333"}},
                    {"size": 10000, "node": {"name": "Lang4", "color": "#444444"}},
                    {"size": 5000, "node": {"name": "Lang5", "color": "#555555"}},
                    {"size": 3000, "node": {"name": "Lang6", "color": "#666666"}},
                    {"size": 2000, "node": {"name": "Lang7", "color": "#777777"}},
                ]
            },
        }
    ]

    # Total: 105,000 bytes. Top 5: 100,000. Remainder: 5,000 (~4.8%).
    languages = aggregate_top_languages(nodes, ignore_list=[])
    assert len(languages) == 6
    assert [l["name"] for l in languages[:5]] == ["Lang1", "Lang2", "Lang3", "Lang4", "Lang5"]
    assert languages[5]["name"] == "Other"
    assert languages[5]["color"] == "#8b949e"
    assert languages[5]["percentage"] == 4.8

    # Case where remainder < 1%: 100,000 + 100 bytes -> remainder is < 0.1%
    nodes_small_rem = [
        {
            "name": "small-rem-repo",
            "isFork": False,
            "languages": {
                "edges": [
                    {"size": 50000, "node": {"name": "Lang1", "color": "#111111"}},
                    {"size": 20000, "node": {"name": "Lang2", "color": "#222222"}},
                    {"size": 15000, "node": {"name": "Lang3", "color": "#333333"}},
                    {"size": 10000, "node": {"name": "Lang4", "color": "#444444"}},
                    {"size": 5000, "node": {"name": "Lang5", "color": "#555555"}},
                    {"size": 50, "node": {"name": "Lang6", "color": "#666666"}},
                ]
            },
        }
    ]
    languages_no_other = aggregate_top_languages(nodes_small_rem, ignore_list=[])
    assert len(languages_no_other) == 5
    assert "Other" not in [l["name"] for l in languages_no_other]


def test_language_zero_bytes_safety():
    """Verify empty nodes or 0-byte repositories return empty list without ZeroDivisionError."""
    assert aggregate_top_languages([]) == []
    empty_nodes = [
        {"name": "fork-repo", "isFork": True, "languages": {"edges": [{"size": 1000, "node": {"name": "Python"}}]}},
        {"name": "empty-repo", "isFork": False, "languages": {"edges": []}},
    ]
    assert aggregate_top_languages(empty_nodes) == []


def test_fetch_language_telemetry_cache_fallback():
    """Verify fetch_language_telemetry fallback behavior across tiers."""
    config = {"telemetry": {"ignore_languages": ["HTML", "CSS", "TeX", "Markdown"]}}

    # 1. Tier 2: Cache hit
    cache_with_langs = {
        "top_languages": {
            "last_updated": "2026-11-08T00:00:00Z",
            "languages": [{"name": "Python", "bytes": 1000, "color": "#3572A5", "percentage": 100.0}],
        }
    }
    result = fetch_language_telemetry(config, cache_with_langs, token=None)
    assert len(result) == 1
    assert result[0]["name"] == "Python"

    # 2. Tier 3: Fixture fallback
    empty_cache = {}
    result_fixtures = fetch_language_telemetry(config, empty_cache, token=None)
    assert result_fixtures == DEFAULT_LANGUAGE_FIXTURES
    assert "top_languages" in empty_cache

    # 3. Network error fallback
    with patch("scripts.update_profile.execute_graphql", side_effect=RuntimeError("API error")):
        error_cache = {}
        result_err = fetch_language_telemetry(config, error_cache, token="fake_token")
        assert result_err == DEFAULT_LANGUAGE_FIXTURES



def test_streak_calculation_active_today():
    """Verify streak includes today when today has contributions."""
    now = datetime.datetime(2026, 11, 8, 12, 0, 0, tzinfo=datetime.timezone.utc)
    days = [
        {"date": "2026-11-06", "contributionCount": 4},
        {"date": "2026-11-07", "contributionCount": 7},
        {"date": "2026-11-08", "contributionCount": 2},
    ]
    current, longest, total = compute_streaks_from_calendar(days, now_utc=now)
    assert current == 3
    assert longest == 3
    assert total == 13


def test_streak_calculation_today_grace_period():
    """Verify streak does not break if yesterday has contributions and today has 0."""
    now = datetime.datetime(2026, 11, 8, 12, 0, 0, tzinfo=datetime.timezone.utc)
    days = [
        {"date": "2026-11-06", "contributionCount": 4},
        {"date": "2026-11-07", "contributionCount": 7},
        {"date": "2026-11-08", "contributionCount": 0},
    ]
    current, longest, total = compute_streaks_from_calendar(days, now_utc=now)
    assert current == 2  # Yesterday + day before
    assert longest == 2
    assert total == 11


def test_streak_calculation_inactive_standby():
    """Verify streak resets to 0 if both today and yesterday have 0 contributions."""
    now = datetime.datetime(2026, 11, 8, 12, 0, 0, tzinfo=datetime.timezone.utc)
    days = [
        {"date": "2026-11-06", "contributionCount": 4},
        {"date": "2026-11-07", "contributionCount": 0},
        {"date": "2026-11-08", "contributionCount": 0},
    ]
    current, longest, total = compute_streaks_from_calendar(days, now_utc=now)
    assert current == 0
    assert longest == 1
    assert total == 4


def test_longest_streak_historical_carry():
    """Verify longest streak carries historical maximum even after current streak breaks."""
    now = datetime.datetime(2026, 11, 8, 12, 0, 0, tzinfo=datetime.timezone.utc)
    days = [
        {"date": "2026-11-01", "contributionCount": 1},
        {"date": "2026-11-02", "contributionCount": 1},
        {"date": "2026-11-03", "contributionCount": 1},
        {"date": "2026-11-04", "contributionCount": 1},
        {"date": "2026-11-05", "contributionCount": 0},  # Break
        {"date": "2026-11-06", "contributionCount": 1},
        {"date": "2026-11-07", "contributionCount": 1},
        {"date": "2026-11-08", "contributionCount": 1},
    ]
    current, longest, total = compute_streaks_from_calendar(days, now_utc=now)
    assert current == 3
    assert longest == 4  # Historical max from Nov 1-4
    assert total == 7


def test_fetch_streak_telemetry_offline_fallback():
    """Verify fetch_streak_telemetry fallback behavior across tiers."""
    # Tier 2: cached
    cache_with_streaks = {
        "streak_metrics": {
            "last_updated": "2026-11-08T00:00:00Z",
            "current_streak": 10,
            "longest_streak": 20,
            "total_contributions": 500,
            "standby": False,
        }
    }
    result = fetch_streak_telemetry(cache_with_streaks, token=None)
    assert result["current_streak"] == 10
    assert result["longest_streak"] == 20

    # Tier 3: default fixtures
    empty_cache: dict = {}
    result_fix = fetch_streak_telemetry(empty_cache, token=None)
    assert result_fix == DEFAULT_STREAK_FIXTURES
    assert "streak_metrics" in empty_cache


def test_metrics_svg_valid_xml():
    """Verify generated SVG is valid XML parseable by ElementTree."""
    svg = generate_metrics_svg(DEFAULT_STREAK_FIXTURES, DEFAULT_LANGUAGE_FIXTURES)
    root = ET.fromstring(svg)
    assert root.tag == "{http://www.w3.org/2000/svg}svg"


def test_metrics_svg_viewbox_and_dimensions():
    """Verify viewBox is '0 0 850 340'."""
    svg = generate_metrics_svg(DEFAULT_STREAK_FIXTURES, DEFAULT_LANGUAGE_FIXTURES)
    root = ET.fromstring(svg)
    assert root.attrib["viewBox"] == "0 0 850 340"


def test_metrics_svg_palette_tokens():
    """Verify terminal palette tokens are present in SVG output."""
    svg = generate_metrics_svg(DEFAULT_STREAK_FIXTURES, DEFAULT_LANGUAGE_FIXTURES)
    for token in ["#161b22", "#0d1117", "#ffa657", "#58a6ff", "#3fb950"]:
        assert token in svg, f"Missing palette token {token}"


def test_metrics_svg_standby_badge_rendering():
    """Verify [standby] text is rendered when current_streak == 0."""
    standby_data = {
        "current_streak": 0,
        "longest_streak": 14,
        "total_contributions": 482,
        "standby": True,
    }
    svg = generate_metrics_svg(standby_data, DEFAULT_LANGUAGE_FIXTURES)
    assert "[standby]" in svg

    # Non-standby should NOT contain [standby]
    active_data = {
        "current_streak": 5,
        "longest_streak": 14,
        "total_contributions": 482,
        "standby": False,
    }
    svg_active = generate_metrics_svg(active_data, DEFAULT_LANGUAGE_FIXTURES)
    assert "[standby]" not in svg_active


def test_vector_progress_track_width_calc():
    """Verify vector track <rect> width handles 0% and 100% correctly."""
    # 100% single language
    langs_100 = [{"name": "Python", "bytes": 100, "color": "#3572A5", "percentage": 100.0}]
    svg_100 = generate_metrics_svg(DEFAULT_STREAK_FIXTURES, langs_100)
    root = ET.fromstring(svg_100)
    # Should have a filled rect with width=200 (max track width)
    assert 'width="200"' in svg_100

    # Empty languages - should still produce valid SVG
    svg_empty = generate_metrics_svg(DEFAULT_STREAK_FIXTURES, [])
    ET.fromstring(svg_empty)  # Must not crash


def test_visitor_badge_url_parameters():
    """Verify visitor counter badge Markdown has exact required parameters per D-19, D-20."""
    assert "username=humam-hossain" in VISITOR_BADGE_MARKDOWN
    assert "color=3fb950" in VISITOR_BADGE_MARKDOWN
    assert "labelColor=161b22" in VISITOR_BADGE_MARKDOWN
    assert "style=flat-square" in VISITOR_BADGE_MARKDOWN
    assert "label=session_hits" in VISITOR_BADGE_MARKDOWN


def test_update_readme_badges_insertion(tmp_path):
    """Verify update_readme_badges appends session_hits badge after Resume badge."""
    mock_readme = tmp_path / "README.md"
    content = (
        "<div align=\"center\">\n\n"
        "[![Email](https://img.shields.io/badge/Email-test-161b22)](mailto:test@example.com)\n"
        "[![LinkedIn](https://img.shields.io/badge/LinkedIn-test-161b22)](https://linkedin.com)\n"
        "[![Portfolio](https://img.shields.io/badge/Portfolio-test-161b22)](https://github.com)\n"
        "[![Resume](https://img.shields.io/badge/Resume-PDF-161b22)](./cv/test.pdf)\n\n"
        "</div>\n"
    )
    mock_readme.write_text(content, encoding="utf-8")

    res = update_readme_badges(mock_readme)
    assert res is True

    new_content = mock_readme.read_text(encoding="utf-8")
    assert "session_hits" in new_content
    # Assert it appears after Resume badge
    resume_pos = new_content.index("[![Resume]")
    session_pos = new_content.index("[![session_hits]")
    assert session_pos > resume_pos


def test_update_readme_badges_idempotence(tmp_path):
    """Verify update_readme_badges is strictly idempotent on repeated calls."""
    mock_readme = tmp_path / "README.md"
    content = (
        "<div align=\"center\">\n\n"
        "[![Resume](https://img.shields.io/badge/Resume-PDF-161b22)](./cv/test.pdf)\n\n"
        "</div>\n"
    )
    mock_readme.write_text(content, encoding="utf-8")

    res1 = update_readme_badges(mock_readme)
    assert res1 is True
    first_pass_content = mock_readme.read_text(encoding="utf-8")

    # Second pass: should skip write and return False
    res2 = update_readme_badges(mock_readme)
    assert res2 is False
    assert mock_readme.read_text(encoding="utf-8") == first_pass_content


def test_git_activity_formatting_output():
    """Verify format_git_activity_stream produces terminal <pre><code> block with links."""
    output = format_git_activity_stream(DEFAULT_ACTIVITY_FIXTURES)
    assert '<div align="left">' in output
    assert '<pre><code>humam@workstation:~$ git log --graph --oneline -n 6' in output
    assert "linux_shell_scripting" in output
    assert "Python" in output
    assert "nn" in output
    assert "* <a href=" in output
    assert "</code></pre>" in output
    assert "</div>" in output


def test_git_activity_message_clamping_50_chars():
    """Verify commit messages > 50 characters are clamped to 50 chars with ellipsis."""
    long_msg = "feat(telemetry): implement super advanced multi-threaded hyper-speed commit stream analyzer"
    activities = [
        {
            "sha": "1234567",
            "repo": "test-repo",
            "message": long_msg,
            "author": "humam-hossain",
            "time_ago": "1 day ago",
        }
    ]
    output = format_git_activity_stream(activities)
    expected_clamped = long_msg[:47] + "..."
    assert expected_clamped in output
    assert long_msg not in output


def test_bot_filtering_github_actions_and_dependabot():
    """Verify commits authored by bots are excluded from activity stream."""
    activities = [
        {
            "sha": "aaaaaaa",
            "repo": "test-repo",
            "message": "valid human commit",
            "author": "humam-hossain",
            "time_ago": "1 day ago",
        },
        {
            "sha": "bbbbbbb",
            "repo": "test-repo",
            "message": "bot commit 1",
            "author": "dependabot[bot]",
            "time_ago": "1 day ago",
        },
        {
            "sha": "ccccccc",
            "repo": "test-repo",
            "message": "bot commit 2",
            "author": "github-actions[bot]",
            "time_ago": "1 day ago",
        },
    ]
    output = format_git_activity_stream(activities)
    assert "valid human commit" in output
    assert "bot commit 1" not in output
    assert "bot commit 2" not in output


def test_updater_commit_prefix_filtering():
    """Verify commits starting with updater/chore prefixes are filtered out."""
    activities = [
        {
            "sha": "1111111",
            "repo": "test-repo",
            "message": "docs(update): refresh profile telemetry",
            "author": "humam-hossain",
            "time_ago": "1 hour ago",
        },
        {
            "sha": "2222222",
            "repo": "test-repo",
            "message": "chore(deps): update actions",
            "author": "humam-hossain",
            "time_ago": "1 hour ago",
        },
        {
            "sha": "3333333",
            "repo": "test-repo",
            "message": "bump version to 1.0.1",
            "author": "humam-hossain",
            "time_ago": "1 hour ago",
        },
        {
            "sha": "4444444",
            "repo": "test-repo",
            "message": "feat: genuine feature commit",
            "author": "humam-hossain",
            "time_ago": "1 hour ago",
        },
    ]
    output = format_git_activity_stream(activities)
    assert "feat: genuine feature commit" in output
    assert "docs(update):" not in output
    assert "chore(deps):" not in output
    assert "bump version" not in output


def test_html_escaping_in_commit_messages():
    """Verify HTML special characters in messages and repo names are escaped."""
    activities = [
        {
            "sha": "5555555",
            "repo": "repo<>&",
            "message": "fix: sanitize <script>alert(1)</script> & enjoy",
            "author": "humam-hossain",
            "time_ago": "1 day ago",
        }
    ]
    output = format_git_activity_stream(activities)
    assert "&lt;script&gt;" in output
    assert "<script>" not in output
    assert "repo&lt;&gt;&amp;" in output


def test_relative_time_formatting():
    """Verify compute_relative_time_str produces human-friendly relative time strings."""
    now = datetime.datetime(2026, 11, 8, 12, 0, 0, tzinfo=datetime.timezone.utc)

    t_just_now = now - datetime.timedelta(minutes=15)
    assert compute_relative_time_str(t_just_now, now_utc=now) == "just now"

    t_1_hr = now - datetime.timedelta(hours=1)
    assert compute_relative_time_str(t_1_hr, now_utc=now) == "1 hour ago"

    t_5_hrs = now - datetime.timedelta(hours=5)
    assert compute_relative_time_str(t_5_hrs, now_utc=now) == "5 hours ago"

    t_1_day = now - datetime.timedelta(days=1)
    assert compute_relative_time_str(t_1_day, now_utc=now) == "1 day ago"

    t_4_days = now - datetime.timedelta(days=4)
    assert compute_relative_time_str(t_4_days, now_utc=now) == "4 days ago"

    t_2_weeks = now - datetime.timedelta(days=14)
    assert compute_relative_time_str(t_2_weeks, now_utc=now) == "2 weeks ago"

    t_2_months = now - datetime.timedelta(days=65)
    assert compute_relative_time_str(t_2_months, now_utc=now) == "2 months ago"


def test_readme_metrics_injection_and_idempotence(tmp_path):
    """Verify surgical injection into README between markers and idempotent second run."""
    mock_readme = tmp_path / "README.md"
    original_content = (
        "# User Profile\n\n"
        "<!-- METRICS:START -->\n"
        "<!-- METRICS:END -->\n\n"
        "Footer note\n"
    )
    mock_readme.write_text(original_content, encoding="utf-8")
    mock_html = "<pre><code>humam@workstation:~$ git log</code></pre>"

    # 1. First injection
    res1 = update_readme_metrics(mock_readme, mock_html)
    assert res1 is True

    updated_content = mock_readme.read_text(encoding="utf-8")
    assert '<img src="./assets/metrics.svg"' in updated_content
    assert "<code>humam@workstation:~$ git log" in updated_content
    assert "# User Profile" in updated_content
    assert "Footer note" in updated_content

    # 2. Second injection with identical data -> idempotent skip
    res2 = update_readme_metrics(mock_readme, mock_html)
    assert res2 is False
    assert mock_readme.read_text(encoding="utf-8") == updated_content


def test_cache_persistence_keys():
    """Verify data/cache.json retains all required telemetry sections."""
    cache_path = Path(__file__).resolve().parent.parent / "data" / "cache.json"
    assert cache_path.is_file()
    with open(cache_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    required_keys = [
        "baseline",
        "repositories",
        "totals",
        "project_metrics",
        "streak_metrics",
        "top_languages",
        "recent_activity",
    ]
    for k in required_keys:
        assert k in data, f"Missing key {k} in data/cache.json"


def test_full_coordinator_offline_execution(monkeypatch, capsys):
    """Verify executing update_profile main() unauthenticated exits 0 and updates all assets."""
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)

    exit_code = update_profile_main()
    assert exit_code == 0

    captured = capsys.readouterr()
    output = captured.out + captured.err
    assert "[WARN]" in output
    assert "No token found" in output
