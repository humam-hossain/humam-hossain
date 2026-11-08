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

import pytest

from scripts.generate_projects import DEFAULT_PROJECT_FIXTURES
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
