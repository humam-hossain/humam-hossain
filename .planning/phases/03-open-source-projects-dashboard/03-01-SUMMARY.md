---
phase: "03"
plan: "01"
subsystem: "data-acquisition"
tags:
  - graphql
  - curation
  - offline-fallback
  - telemetry
requires:
  - "02-03"
provides:
  - "config/projects.json"
  - "tests/fixtures/graphql_projects.json"
  - "DEFAULT_PROJECT_FIXTURES in scripts/generate_projects.py"
  - "load_curated_projects, build_batched_projects_query, fetch_project_telemetry in scripts/update_profile.py"
affects:
  - "scripts/update_profile.py"
  - "tests/test_projects.py"
tech-stack:
  added: []
  patterns:
    - "Batched GraphQL queries with indexed numeric aliases (repo_0, repo_1)"
    - "Multi-tier telemetry fallback: live GraphQL -> cache -> static fixtures"
    - "Smart description resolution: custom override -> GitHub desc -> #topics -> default"
key-files:
  created:
    - "config/projects.json"
    - "tests/fixtures/graphql_projects.json"
    - "scripts/generate_projects.py"
    - "tests/test_projects.py"
  modified:
    - "scripts/update_profile.py"
key-decisions:
  - "User curation authority over repositories via dedicated config/projects.json (D-07, D-08)"
  - "Indexed numeric GraphQL aliases to safely handle hyphens and dots in single API call (D-16)"
  - "Zero unhandled exceptions offline: fallback to cache['project_metrics'] then DEFAULT_PROJECT_FIXTURES (D-18)"
requirements-completed:
  - PROJ-01
  - PROJ-02
duration: "3 min"
completed: "2026-11-08T09:23:40Z"
coverage:
  - deliverable: "Curation configuration with 4 starter pins"
    verification:
      kind: "pytest"
      ref: "tests/test_projects.py#test_curation_config_loading"
      status: "pass"
    human_judgment: false
  - deliverable: "Batched GraphQL query builder with indexed aliases"
    verification:
      kind: "pytest"
      ref: "tests/test_projects.py#test_batched_graphql_query_builder"
      status: "pass"
    human_judgment: false
  - deliverable: "Telemetry fetcher with smart description and offline fallback"
    verification:
      kind: "pytest"
      ref: "tests/test_projects.py#test_fetch_project_telemetry_with_mock_graphql"
      status: "pass"
    human_judgment: false
---

# Phase 03 Plan 01: Curated Projects Configuration & Batched GraphQL Query Engine Summary

Configured dedicated repository curation schema, batched GraphQL query builder with indexed aliases (`repo_0`..`repo_3`), and multi-tier offline fallback engine for featured projects telemetry.

## Performance & Metrics
- **Duration:** 3 min
- **Start Time:** 2026-11-08T09:18:20Z
- **End Time:** 2026-11-08T09:23:40Z
- **Tasks Executed:** 3
- **Files Modified / Created:** 5

## Accomplishments
1. **Repository Curation Configuration (`config/projects.json`)**: Established user curation schema supporting string shorthand and rich dictionary definitions with custom name, description, and tag overrides. Seeded with 4 initial starter pins (`linux_shell_scripting`, `Python`, `nn`, `antigravity-cli-statusline`).
2. **Batched GraphQL Engine & Fixtures**: Implemented `build_batched_projects_query()` generating indexed GraphQL aliases (`repo_0`, `repo_1`) to cleanly handle hyphens and dots while consuming 1 API quota point. Created `tests/fixtures/graphql_projects.json` containing mock response data for offline validation.
3. **Telemetry Fetcher & Offline Fallback**: Implemented `fetch_project_telemetry()` with smart fallback descriptions (`#topic1 #topic2` or default string) and graceful three-tier fallback (live API -> cache -> `DEFAULT_PROJECT_FIXTURES`).
4. **Unit Test Suite (`tests/test_projects.py`)**: Built 6 comprehensive offline unit tests enforcing 100% network isolation, validating schema normalizations, query syntax, mock telemetry parsing, and unauthenticated execution.

## Deviations from Plan

### [Rule 1 - Bug] Corrected repo key normalization when display name override is provided
- **Found during:** Task 03-01-03
- **Issue:** `load_curated_projects()` incorrectly formatted `"repo"` as `f"{owner}/{name}"` where `name` was the display name override rather than preserving the GitHub repository identifier.
- **Fix:** Separated `repo_name` extraction from display `name` override so `"repo"` remains `f"{owner}/{repo_name}"` and `"name"` takes the override.
- **Files modified:** `scripts/update_profile.py`
- **Verification:** `tests/test_projects.py::test_curation_config_loading` passes.

**Total deviations:** 1 auto-fixed (Rule 1).
**Impact:** Prevents corrupted repository slugs when users provide custom display names in curation config.

## Self-Check: PASSED
- `config/projects.json` exists on disk: YES
- `tests/fixtures/graphql_projects.json` exists on disk: YES
- `scripts/generate_projects.py` exists on disk: YES
- `scripts/update_profile.py` exists on disk: YES
- `tests/test_projects.py` exists on disk: YES
- Commits found:
  - `e23c3ce` feat(03-01): create repository curation config and schema loader
  - `6f59f59` feat(03-01): implement batched graphql query engine and offline fixture fallback
  - `9dd7b3b` test(03-01): create test suite foundation for curation and graphql engine
- Acceptance criteria & pytest suite: 24/24 tests PASS
