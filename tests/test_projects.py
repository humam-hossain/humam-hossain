"""
tests/test_projects.py
Unit and integration test suite for the Open Source Projects Dashboard.
Tests curation config loading, batched GraphQL query construction,
smart description fallbacks, and offline fixture handling.
Enforces 100% network isolation with zero external API calls.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch
import xml.etree.ElementTree as ET

import pytest

from scripts.generate_projects import (
    DEFAULT_PROJECT_FIXTURES,
    GRID_SLOTS,
    OCTICONS,
    generate_projects_svg,
    wrap_and_clamp_description,
)
from scripts.update_profile import (
    PROJECTS_CONFIG_PATH,
    build_batched_projects_query,
    fetch_project_telemetry,
    load_curated_projects,
)

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def test_fixtures_projects_valid_json():
    """Verify tests/fixtures/graphql_projects.json exists and contains repo_0 through repo_3."""
    fixture_path = FIXTURES_DIR / "graphql_projects.json"
    assert fixture_path.is_file(), "Missing graphql_projects.json fixture"

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "data" in data, "Fixture missing top-level 'data' key"
    for idx in range(4):
        key = f"repo_{idx}"
        assert key in data["data"], f"Missing {key} in fixture"
        repo = data["data"][key]
        assert "name" in repo
        assert "owner" in repo
        assert "stargazerCount" in repo
        assert "forkCount" in repo
        assert "issues" in repo
        assert "pullRequests" in repo
        assert "primaryLanguage" in repo
        assert "repositoryTopics" in repo
        assert "url" in repo


def test_curation_config_loading(tmp_path):
    """Test loading config/projects.json and schema normalization (string & dict)."""
    # 1. Existing config/projects.json
    res = load_curated_projects(PROJECTS_CONFIG_PATH)
    assert len(res) == 4
    assert res[0]["name"] == "linux_shell_scripting"
    assert res[0]["owner"] == "humam-hossain"
    assert res[0]["repo"] == "humam-hossain/linux_shell_scripting"
    assert res[0]["tag"] == "DevOps"

    # 2. String shorthand normalization
    test_config = tmp_path / "projects_test.json"
    test_config.write_text(
        json.dumps({
            "projects": [
                "custom-owner/foo-repo",
                "bare-repo",
                {
                    "repo": "another-owner/bar",
                    "name": "CustomBar",
                    "description": "Custom description",
                    "tag": "Utilities",
                },
            ]
        }),
        encoding="utf-8",
    )
    loaded = load_curated_projects(test_config)
    assert len(loaded) == 3
    assert loaded[0] == {
        "owner": "custom-owner",
        "name": "foo-repo",
        "repo": "custom-owner/foo-repo",
        "description": None,
        "tag": None,
    }
    assert loaded[1] == {
        "owner": "humam-hossain",
        "name": "bare-repo",
        "repo": "humam-hossain/bare-repo",
        "description": None,
        "tag": None,
    }
    assert loaded[2] == {
        "owner": "another-owner",
        "name": "CustomBar",
        "repo": "another-owner/bar",
        "description": "Custom description",
        "tag": "Utilities",
    }

    # 3. Missing file and corrupt JSON fallback
    missing = load_curated_projects(tmp_path / "nonexistent.json")
    assert missing == []

    corrupt_config = tmp_path / "corrupt.json"
    corrupt_config.write_text("{invalid json", encoding="utf-8")
    assert load_curated_projects(corrupt_config) == []


def test_batched_graphql_query_builder():
    """Verify indexed GraphQL aliases and requested fields."""
    curated = [
        {"owner": "humam-hossain", "name": "linux-shell-scripting"},
        {"owner": "humam-hossain", "name": "Python.algo"},
    ]
    query = build_batched_projects_query(curated)

    assert "query GetFeaturedProjects {" in query
    assert "repo_0: repository(owner: \"humam-hossain\", name: \"linux-shell-scripting\")" in query
    assert "repo_1: repository(owner: \"humam-hossain\", name: \"Python.algo\")" in query
    assert "stargazerCount" in query
    assert "forkCount" in query
    assert "issues(states: OPEN)" in query
    assert "pullRequests(states: OPEN)" in query
    assert "primaryLanguage" in query
    assert "repositoryTopics(first: 5)" in query
    assert "url" in query


def test_fetch_project_telemetry_with_mock_graphql():
    """Verify telemetry parsing and cache population using fixture response."""
    fixture_path = FIXTURES_DIR / "graphql_projects.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        mock_response = json.load(f)

    curated = load_curated_projects(PROJECTS_CONFIG_PATH)
    cache = {}

    with patch("scripts.update_profile.execute_graphql", return_value=mock_response):
        projects = fetch_project_telemetry(curated, cache, token="mock-token-xyz")

    assert len(projects) == 4
    repo_0 = projects[0]
    assert repo_0["name"] == "linux_shell_scripting"
    assert repo_0["stars"] == 12
    assert repo_0["forks"] == 3
    assert repo_0["open_issues"] == 1
    assert repo_0["open_prs"] == 0
    assert repo_0["language"] == "Shell"
    assert repo_0["language_color"] == "#89e051"
    assert repo_0["topics"] == ["bash", "shell", "automation"]
    assert repo_0["url"] == "https://github.com/humam-hossain/linux_shell_scripting"

    # Verify cache is populated
    assert "project_metrics" in cache
    assert "last_updated" in cache["project_metrics"]
    assert len(cache["project_metrics"]["projects"]) == 4


def test_smart_description_fallback():
    """Verify custom description priority -> GitHub description -> #topics -> default fallback."""
    # 1. Custom description takes priority
    curated_custom = [{"owner": "humam-hossain", "name": "repo1", "description": "Custom override"}]
    mock_resp_1 = {
        "data": {
            "repo_0": {
                "name": "repo1",
                "owner": {"login": "humam-hossain"},
                "description": "GitHub description",
                "stargazerCount": 0,
                "forkCount": 0,
                "issues": {"totalCount": 0},
                "pullRequests": {"totalCount": 0},
                "primaryLanguage": {"name": "Python", "color": "#3572A5"},
                "repositoryTopics": {"nodes": []},
                "url": "https://github.com/humam-hossain/repo1",
            }
        }
    }
    with patch("scripts.update_profile.execute_graphql", return_value=mock_resp_1):
        res1 = fetch_project_telemetry(curated_custom, {}, token="token")
    assert res1[0]["description"] == "Custom override"

    # 2. Missing description falls back to #topics
    curated_topics = [{"owner": "humam-hossain", "name": "repo2", "description": None}]
    mock_resp_2 = {
        "data": {
            "repo_0": {
                "name": "repo2",
                "owner": {"login": "humam-hossain"},
                "description": None,
                "stargazerCount": 0,
                "forkCount": 0,
                "issues": {"totalCount": 0},
                "pullRequests": {"totalCount": 0},
                "primaryLanguage": None,
                "repositoryTopics": {
                    "nodes": [{"topic": {"name": "ros2"}}, {"topic": {"name": "robotics"}}]
                },
                "url": "https://github.com/humam-hossain/repo2",
            }
        }
    }
    with patch("scripts.update_profile.execute_graphql", return_value=mock_resp_2):
        res2 = fetch_project_telemetry(curated_topics, {}, token="token")
    assert res2[0]["description"] == "#ros2 #robotics"

    # 3. Empty topics fall back to generic string
    mock_resp_3 = {
        "data": {
            "repo_0": {
                "name": "repo3",
                "owner": {"login": "humam-hossain"},
                "description": "",
                "stargazerCount": 0,
                "forkCount": 0,
                "issues": {"totalCount": 0},
                "pullRequests": {"totalCount": 0},
                "primaryLanguage": None,
                "repositoryTopics": {"nodes": []},
                "url": "https://github.com/humam-hossain/repo3",
            }
        }
    }
    with patch("scripts.update_profile.execute_graphql", return_value=mock_resp_3):
        res3 = fetch_project_telemetry([{"owner": "humam-hossain", "name": "repo3", "description": None}], {}, token="token")
    assert res3[0]["description"] == "Open-source software repository"


def test_offline_fallback_when_unauthenticated():
    """Verify offline fallback returns DEFAULT_PROJECT_FIXTURES when no token & empty cache."""
    cache = {}
    res = fetch_project_telemetry([], cache, token=None)
    assert res == DEFAULT_PROJECT_FIXTURES
    assert len(res) == 4

    # When cache exists, returns cached projects
    cached_data = [{"name": "cached-repo", "stars": 99}]
    cache = {"project_metrics": {"projects": cached_data}}
    res_cached = fetch_project_telemetry([], cache, token=None)
    assert res_cached == cached_data


def test_description_clamping_and_escaping():
    """Verify word wrapping at 42/40 characters, ellipsis, and XML entity escaping."""
    # 1. Short text
    l1, l2 = wrap_and_clamp_description("Short text")
    assert l1 == "Short text"
    assert l2 == ""

    # 2. Text with XML entities (e.g. &)
    l1_ent, l2_ent = wrap_and_clamp_description("Robotics & AI Framework tools for autonomous vehicles")
    assert "&amp;" in l1_ent
    # Verify no broken entities like &am...
    assert "&am" not in l1_ent.replace("&amp;", "")

    # 3. Very long text requiring 2 lines and ellipsis truncation
    long_text = (
        "This is an extremely detailed and exceptionally lengthy project description "
        "designed specifically to test the two-line word wrapping and ellipsis truncation "
        "algorithm in the terminal SVG generator."
    )
    l1_long, l2_long = wrap_and_clamp_description(long_text, max_line1=42, max_line2=40)
    assert len(l1_long) <= 50  # Allows for safe entities
    assert l2_long.endswith("...")


def test_projects_svg_xml_validity():
    """Verify generated SVG parses cleanly with ElementTree and has viewBox 0 0 850 340."""
    svg_str = generate_projects_svg(DEFAULT_PROJECT_FIXTURES)
    root = ET.fromstring(svg_str)

    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    assert root.attrib.get("viewBox") == "0 0 850 340"
    assert root.attrib.get("width") == "100%"
    assert root.attrib.get("height") == "100%"


def test_projects_svg_chrome_and_tokens():
    """Verify workstation header bar, traffic lights, window title, and prompt command."""
    svg_str = generate_projects_svg(DEFAULT_PROJECT_FIXTURES)

    # Traffic lights
    assert 'fill="#ff5f56"' in svg_str  # Close
    assert 'fill="#ffbd2e"' in svg_str  # Minimize
    assert 'fill="#27c93f"' in svg_str  # Zoom

    # Window title
    assert "projects — zsh" in svg_str

    # CLI Prompt line
    assert "humam@workstation:~/projects$" in svg_str
    assert "gh repo list" in svg_str


def test_subpanel_grid_positions():
    """Verify subpanels are rendered at exact (30,80), (440,80), (30,207), (440,207) coordinates."""
    svg_str = generate_projects_svg(DEFAULT_PROJECT_FIXTURES)

    for gx, gy in GRID_SLOTS:
        pattern = f'x="{gx}" y="{gy}" width="380" height="115"'
        assert pattern in svg_str, f"Missing subpanel at ({gx}, {gy})"


def test_zero_count_muted_rendering():
    """Verify metric counters use ANSI accent for > 0 and muted #616e7f for == 0."""
    sample_projects = [
        {
            "name": "sample-repo",
            "repo": "humam-hossain/sample-repo",
            "description": "Test repo",
            "stars": 15,
            "forks": 0,
            "open_issues": 3,
            "open_prs": 0,
            "language": "Python",
            "language_color": "#3572A5",
        }
    ]
    svg_str = generate_projects_svg(sample_projects)

    # Star > 0 -> #f1e05a
    assert 'fill="#f1e05a"' in svg_str
    # Issue > 0 -> #ffa657
    assert 'fill="#ffa657"' in svg_str
    # Fork == 0 and PR == 0 -> #616e7f
    assert 'fill="#616e7f"' in svg_str


def test_partial_grid_slots():
    """Verify empty grid slots render dashed border and [ available slot ] placeholder."""
    two_projects = DEFAULT_PROJECT_FIXTURES[:2]
    svg_str = generate_projects_svg(two_projects)

    # 2 empty slots -> 2 dashed rectangles
    assert svg_str.count('stroke-dasharray="4,4"') == 2
    assert svg_str.count("[ available slot ]") == 2

