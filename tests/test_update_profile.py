"""
tests/test_update_profile.py
Offline unit and integration test suite for profile update automation engine.
Enforces 100% network isolation using fixtures and mock responses.
"""

import datetime
import json
import os
from pathlib import Path
import sys
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from scripts.update_profile import (
    _add_calendar_months,
    compute_calendar_diff,
    format_uptime_neofetch,
    get_baseline_date,
    format_loc_counts,
    load_cache,
    save_cache,
    aggregate_loc,
    write_svg_idempotent,
    get_github_token,
    execute_graphql,
    main,
    log_info,
    log_ok,
    log_warn,
    log_err,
)

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def test_fixtures_valid_json():
    """Verify that all GraphQL mock fixtures exist and parse as valid JSON."""
    baseline = FIXTURES_DIR / "graphql_baseline.json"
    repos = FIXTURES_DIR / "graphql_repos.json"
    commits = FIXTURES_DIR / "graphql_commits.json"

    assert baseline.is_file(), "Missing graphql_baseline.json fixture"
    assert repos.is_file(), "Missing graphql_repos.json fixture"
    assert commits.is_file(), "Missing graphql_commits.json fixture"

    with open(baseline, "r", encoding="utf-8") as f:
        data_baseline = json.load(f)
    assert data_baseline["data"]["viewer"]["login"] == "humam-hossain"
    assert len(data_baseline["data"]["viewer"]["contributionsCollection"]["contributionYears"]) > 0

    with open(repos, "r", encoding="utf-8") as f:
        data_repos = json.load(f)
    assert len(data_repos["data"]["viewer"]["repositories"]["nodes"]) == 2

    with open(commits, "r", encoding="utf-8") as f:
        data_commits = json.load(f)
    assert len(data_commits["data"]["repository"]["defaultBranchRef"]["target"]["history"]["nodes"]) == 2


def test_token_resolution_order(tmp_path, monkeypatch):
    """
    Validates token resolution hierarchy:
    GITHUB_TOKEN > GH_TOKEN > .env file > None.
    """
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)

    # 1. No token in env or .env -> None
    assert get_github_token(tmp_path) is None

    # 2. .env file provided
    env_file = tmp_path / ".env"
    env_file.write_text("GITHUB_TOKEN=token_from_env_file\n", encoding="utf-8")
    assert get_github_token(tmp_path) == "token_from_env_file"

    # 3. GH_TOKEN overrides .env
    monkeypatch.setenv("GH_TOKEN", "token_from_gh_env")
    assert get_github_token(tmp_path) == "token_from_gh_env"

    # 4. GITHUB_TOKEN overrides GH_TOKEN
    monkeypatch.setenv("GITHUB_TOKEN", "token_from_github_env")
    assert get_github_token(tmp_path) == "token_from_github_env"


def test_rate_limit_and_retries():
    """
    Validates exponential backoff and retry handling:
    1. HTTP 429 backoff with Retry-After header.
    2. HTTP 502 Bad Gateway retry.
    3. Fatal error raised after retries exhausted or on non-retryable 401.
    """
    query = "query { viewer { login } }"
    token = "test_token_xyz"

    resp_429 = urllib.error.HTTPError(
        url="https://api.github.com/graphql",
        code=429,
        msg="Too Many Requests",
        hdrs={"Retry-After": "0.1"},
        fp=None,
    )
    success_resp = MagicMock()
    success_resp.status = 200
    success_resp.headers = {"X-RateLimit-Remaining": "4900"}
    success_resp.read.return_value = json.dumps({"data": {"viewer": {"login": "humam-hossain"}}}).encode("utf-8")
    success_resp.__enter__.return_value = success_resp
    success_resp.__exit__.return_value = None

    with patch("urllib.request.urlopen", side_effect=[resp_429, success_resp]) as mock_urlopen:
        with patch("time.sleep") as mock_sleep:
            res = execute_graphql(query=query, token=token, max_retries=2)
            assert res["data"]["viewer"]["login"] == "humam-hossain"
            assert mock_urlopen.call_count == 2
            mock_sleep.assert_called_with(0.1)

    resp_502 = urllib.error.HTTPError(
        url="https://api.github.com/graphql",
        code=502,
        msg="Bad Gateway",
        hdrs={},
        fp=None,
    )
    with patch("urllib.request.urlopen", side_effect=[resp_502, success_resp]) as mock_urlopen:
        with patch("time.sleep") as mock_sleep:
            res = execute_graphql(query=query, token=token, max_retries=2)
            assert res["data"]["viewer"]["login"] == "humam-hossain"
            assert mock_urlopen.call_count == 2
            mock_sleep.assert_called_with(1.0)

    resp_401 = urllib.error.HTTPError(
        url="https://api.github.com/graphql",
        code=401,
        msg="Unauthorized",
        hdrs={},
        fp=None,
    )
    with patch("urllib.request.urlopen", side_effect=resp_401) as mock_urlopen:
        with pytest.raises(RuntimeError, match="401"):
            execute_graphql(query=query, token=token, max_retries=2)
        assert mock_urlopen.call_count == 1


def test_calendar_uptime_math():
    """
    Validates calendar-accurate UTC date differences and Neofetch formatting:
    - Standard differences
    - Pluralization rules (1 vs multiple, 0 values)
    - Leap year boundaries (Feb 29 -> Feb 28)
    - Month boundary clamping (Jan 31 -> Feb 29)
    """
    # Standard differences
    start = datetime.datetime(2020, 9, 18, 7, 0, 0, tzinfo=datetime.timezone.utc)
    end = datetime.datetime(2026, 11, 7, 14, 0, 0, tzinfo=datetime.timezone.utc)
    y, m, d = compute_calendar_diff(start, end)
    assert (y, m, d) == (6, 1, 20)
    assert format_uptime_neofetch(y, m, d) == "6 yrs, 1 mo, 20 days"

    # Pluralization edge cases
    assert format_uptime_neofetch(1, 1, 1) == "1 yr, 1 mo, 1 day"
    assert format_uptime_neofetch(0, 0, 0) == "0 yrs, 0 mos, 0 days"
    assert format_uptime_neofetch(2, 0, 15) == "2 yrs, 0 mos, 15 days"

    # Leap year boundary (Feb 29 -> Feb 28 non-leap)
    start_leap = datetime.datetime(2024, 2, 29, 0, 0, 0, tzinfo=datetime.timezone.utc)
    end_non_leap = datetime.datetime(2025, 2, 28, 0, 0, 0, tzinfo=datetime.timezone.utc)
    assert compute_calendar_diff(start_leap, end_non_leap) == (1, 0, 0)

    # Month end clamping (Jan 31 in leap year -> Feb 29)
    start_jan = datetime.datetime(2020, 1, 31, 0, 0, 0, tzinfo=datetime.timezone.utc)
    end_feb = datetime.datetime(2020, 2, 29, 0, 0, 0, tzinfo=datetime.timezone.utc)
    assert compute_calendar_diff(start_jan, end_feb) == (0, 1, 0)

    # Inverted dates return (0, 0, 0)
    assert compute_calendar_diff(end, start) == (0, 0, 0)


def test_baseline_discovery_precedence():
    """Verifies baseline discovery hierarchy: override > cache > GraphQL fallback > default."""
    config_override = {
        "telemetry": {
            "baseline_override_date": "2019-01-01T00:00:00Z"
        }
    }
    cache_entry = {
        "baseline": {
            "first_commit_date": "2020-05-10T10:00:00Z"
        }
    }

    # 1. Override takes precedence over cache and GraphQL
    dt_override = get_baseline_date(config_override, cache_entry, token="fake_token")
    assert dt_override == datetime.datetime(2019, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)

    # 2. Cached takes precedence when no override
    dt_cached = get_baseline_date({}, cache_entry, token="fake_token")
    assert dt_cached == datetime.datetime(2020, 5, 10, 10, 0, 0, tzinfo=datetime.timezone.utc)

    # 3. GraphQL discovery when no override and no cache
    mock_info = {
        "data": {
            "viewer": {
                "login": "humam-hossain",
                "createdAt": "2020-06-12T11:30:35Z",
                "contributionsCollection": {
                    "contributionYears": [2020]
                }
            }
        }
    }
    mock_commit = {
        "data": {
            "viewer": {
                "contributionsCollection": {
                    "commitContributionsByRepository": [
                        {
                            "contributions": {
                                "nodes": [
                                    {"occurredAt": "2020-09-18T07:00:00Z"}
                                ]
                            }
                        }
                    ]
                }
            }
        }
    }

    empty_cache = {}
    with patch("scripts.update_profile.execute_graphql", side_effect=[mock_info, mock_commit]):
        dt_gql = get_baseline_date({}, empty_cache, token="valid_token")
        assert dt_gql == datetime.datetime(2020, 9, 18, 7, 0, 0, tzinfo=datetime.timezone.utc)
        assert empty_cache["baseline"]["first_commit_date"] == "2020-09-18T07:00:00Z"

    # 4. Fallback default when no token and no cache
    dt_default = get_baseline_date({}, {}, token=None)
    assert dt_default == datetime.datetime(2020, 9, 18, 7, 0, 0, tzinfo=datetime.timezone.utc)


def test_loc_formatting():
    """Verifies comma-separated LOC strings with directional prefix."""
    add_str, del_str = format_loc_counts(320410, 85240)
    assert add_str == "++320,410"
    assert del_str == "--85,240"

    add_zero, del_zero = format_loc_counts(0, 0)
    assert add_zero == "++0"
    assert del_zero == "--0"


def test_cache_lifecycle(tmp_path):
    """Verifies loading, updating, saving, and reloading cache."""
    cache_file = tmp_path / "cache.json"
    cache = load_cache(cache_file)
    assert "baseline" in cache
    assert "repositories" in cache
    assert "totals" in cache

    cache["repositories"]["test_repo"] = {
        "pushed_at": "2026-11-07T12:00:00Z",
        "additions": 1500,
        "deletions": 200,
    }
    save_cache(cache_file, cache)

    reloaded = load_cache(cache_file)
    assert reloaded["repositories"]["test_repo"]["additions"] == 1500
    assert reloaded["repositories"]["test_repo"]["deletions"] == 200


def test_incremental_cache_hit_skip():
    """
    Verifies that when a repository's pushedAt matches cache, no commit history GraphQL
    queries are made (incremental cache hit). When pushedAt changes, query is triggered.
    """
    config = {"telemetry": {"exclude_repos": []}}
    cache = {
        "repositories": {
            "cached_repo": {
                "pushed_at": "2026-11-01T00:00:00Z",
                "additions": 500,
                "deletions": 100,
            }
        },
        "totals": {}
    }

    # Mock repository listing with matching pushedAt
    mock_repos_hit = {
        "data": {
            "viewer": {
                "repositories": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "nodes": [
                        {
                            "name": "cached_repo",
                            "isArchived": False,
                            "pushedAt": "2026-11-01T00:00:00Z",
                            "defaultBranchRef": {"name": "main"}
                        }
                    ]
                }
            }
        }
    }

    with patch("scripts.update_profile.execute_graphql", return_value=mock_repos_hit) as mock_exec:
        adds, dels = aggregate_loc(config, cache, token="test_token")
        assert (adds, dels) == (500, 100)
        # execute_graphql was called only once for repo enumeration, 0 times for commits!
        assert mock_exec.call_count == 1

    # Now simulate pushed_at advance (cache miss)
    mock_repos_miss = {
        "data": {
            "viewer": {
                "repositories": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "nodes": [
                        {
                            "name": "cached_repo",
                            "isArchived": False,
                            "pushedAt": "2026-11-07T12:00:00Z",  # Advanced timestamp
                            "defaultBranchRef": {"name": "main"}
                        }
                    ]
                }
            }
        }
    }
    mock_commits = {
        "data": {
            "viewer": {
                "repository": {
                    "defaultBranchRef": {
                        "target": {
                            "history": {
                                "pageInfo": {"hasNextPage": False, "endCursor": None},
                                "nodes": [
                                    {"additions": 800, "deletions": 150}
                                ]
                            }
                        }
                    }
                }
            }
        }
    }
    with patch("scripts.update_profile.execute_graphql", side_effect=[mock_repos_miss, mock_commits]) as mock_exec:
        adds, dels = aggregate_loc(config, cache, token="test_token")
        assert (adds, dels) == (800, 150)
        assert mock_exec.call_count == 2
        assert cache["repositories"]["cached_repo"]["additions"] == 800


def test_exclude_repos_filtering():
    """Verifies that repositories listed in exclude_repos are excluded from LOC aggregation."""
    config = {
        "telemetry": {
            "exclude_repos": ["excluded_dataset_repo"]
        }
    }
    cache = {
        "repositories": {
            "included_repo": {
                "pushed_at": "2026-11-01T00:00:00Z",
                "additions": 1000,
                "deletions": 200,
            },
            "excluded_dataset_repo": {
                "pushed_at": "2026-11-01T00:00:00Z",
                "additions": 900000,
                "deletions": 50000,
            }
        },
        "totals": {}
    }

    adds, dels = aggregate_loc(config, cache, token=None)
    assert (adds, dels) == (1000, 200)


def test_offline_fallback_mode(capsys, monkeypatch, tmp_path):
    """
    Validates offline fallback mode:
    When executed unauthenticated without a token, script proceeds gracefully,
    emits a warning, and exits 0 with zero unhandled exceptions.
    """
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)

    exit_code = main()
    assert exit_code == 0

    captured = capsys.readouterr()
    assert "[WARN]" in captured.out or "[WARN]" in captured.err
    assert "No token found" in (captured.out + captured.err)
