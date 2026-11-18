---
phase: "04"
slug: "languages-streaks-metrics"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-11-08"
---

# Phase 04 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.2.0 |
| **Config file** | none (standard discovery) |
| **Quick run command** | `pytest tests/test_metrics.py -v` |
| **Full suite command** | `pytest` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_metrics.py -v`
- **After every plan wave:** Run `pytest`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 0 | METRIC-01..04 | — | Fixtures and test harness scaffolded | unit | `pytest tests/test_metrics.py -v` | ❌ W0 | ⬜ pending |
| 04-01-02 | 01 | 1 | METRIC-01 | T-04-02 | Sanitized language percentages & vector tracks | unit | `pytest tests/test_metrics.py -k "test_language" -v` | ❌ W0 | ⬜ pending |
| 04-02-01 | 02 | 1 | METRIC-02 | T-04-01 | Verified streak math & SVG XML structure | unit | `pytest tests/test_metrics.py -k "test_streak or test_metrics_svg" -v` | ❌ W0 | ⬜ pending |
| 04-03-01 | 03 | 1 | METRIC-03 | T-04-04 | Validated visitor badge URL parameters | unit | `pytest tests/test_metrics.py -k "test_visitor_badge" -v` | ❌ W0 | ⬜ pending |
| 04-04-01 | 04 | 1 | METRIC-04 | T-04-01 | HTML-escaped clickable git activity stream | unit | `pytest tests/test_metrics.py -k "test_git_activity" -v` | ❌ W0 | ⬜ pending |
| 04-04-02 | 04 | 2 | METRIC-01..04 | — | Full update_profile integration & README injection | integration | `pytest && python3 scripts/update_profile.py` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_metrics.py` — unit and integration test suite covering METRIC-01, METRIC-02, METRIC-03, and METRIC-04
- [ ] `tests/fixtures/graphql_calendar.json` — mock contribution calendar response
- [ ] `tests/fixtures/graphql_languages.json` — mock language byte counts across repositories
- [ ] `tests/fixtures/rest_events.json` — mock GitHub public activity events

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| GitHub Camo Visitor Counter rendering | METRIC-03 | Badge service relies on external URL proxy rendering in GitHub web UI | Load profile preview in browser, inspect `session_hits` badge visual style |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
