"""
tests/test_update_profile.py
Offline unit and integration test suite for profile update automation engine.
Enforces 100% network isolation using fixtures and mock responses.
"""

import json
import os
from pathlib import Path
import sys
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

try:
    from scripts.update_profile import (
        get_github_token,
        execute_graphql,
        main,
        log_info,
        log_ok,
        log_warn,
        log_err,
    )
except ImportError:
    get_github_token = None
    execute_graphql = None
    main = None
    log_info = None
    log_ok = None
    log_warn = None
    log_err = None

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
    if get_github_token is None:
        pytest.skip("scripts.update_profile not yet implemented")

    # Clear any ambient tokens
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
    if execute_graphql is None:
        pytest.skip("scripts.update_profile not yet implemented")

    query = "query { viewer { login } }"
    token = "test_token_xyz"

    # Case 1: 429 with Retry-After header, then success
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

    # Case 2: 502 Bad Gateway retried, then success
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

    # Case 3: 401 Unauthorized raises immediately without retry
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


def test_offline_fallback_mode(capsys, monkeypatch, tmp_path):
    """
    Validates offline fallback mode:
    When executed unauthenticated without a token, script proceeds gracefully,
    emits a warning, and exits 0 with zero unhandled exceptions.
    """
    if main is None:
        pytest.skip("scripts.update_profile not yet implemented")

    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)

    # Run main() with isolated arguments or environment
    with patch("scripts.update_profile.ROOT_DIR", tmp_path):
        exit_code = main()
        assert exit_code == 0

    captured = capsys.readouterr()
    assert "[WARN]" in captured.out or "[WARN]" in captured.err
    assert "No token found" in (captured.out + captured.err)
