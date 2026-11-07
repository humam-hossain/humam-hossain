---
phase: "02"
slug: "python-engine-dynamic-telemetry"
status: ready
nyquist_compliant: true
wave_0_complete: false
created: "2026-11-07"
---

# Phase 02 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `tests/__init__.py` (standard pytest discovery) |
| **Quick run command** | `pytest tests/test_update_profile.py -q` |
| **Full suite command** | `pytest tests/ -v` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_update_profile.py -q`
- **After every plan wave:** Run `pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 0 | AUTO-01 | — | Offline mock fixtures and test scaffold setup | unit | `pytest tests/test_update_profile.py -v` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 1 | AUTO-01 | T-02-01 | Token resolution precedence & sanitization | unit | `pytest tests/test_update_profile.py -k test_token_resolution -v` | ❌ W0 | ⬜ pending |
| 02-01-03 | 01 | 1 | AUTO-01 | T-02-02 | HTTP retry backoff and offline fallback handling | unit | `pytest tests/test_update_profile.py -k "test_retries or test_offline" -v` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 2 | HERO-04 | — | Calendar-accurate uptime computation & Neofetch formatting | unit | `pytest tests/test_update_profile.py -k test_calendar_uptime_math -v` | ❌ W0 | ⬜ pending |
| 02-02-02 | 02 | 2 | HERO-05 | — | Repository filtering, incremental caching & LOC aggregation | unit | `pytest tests/test_update_profile.py -k "test_cache or test_loc" -v` | ❌ W0 | ⬜ pending |
| 02-03-01 | 03 | 3 | HERO-04, HERO-05 | — | Parameterized SVG rendering preserving DOM hooks | unit | `pytest tests/test_update_profile.py -k test_svg_regeneration -v` | ❌ W0 | ⬜ pending |
| 02-03-02 | 03 | 3 | AUTO-01 | — | End-to-end execution, XML validation & idempotent writes | integration | `pytest tests/ -v && python3 scripts/update_profile.py` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_update_profile.py` — unit and integration test suite
- [ ] `tests/fixtures/graphql_baseline.json` — mock response for first commit / creation date
- [ ] `tests/fixtures/graphql_repos.json` — mock response for repository list and LOC stats

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| *None* | — | — | All phase behaviors have automated verification via pytest. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 5s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved
