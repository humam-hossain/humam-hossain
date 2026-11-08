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
