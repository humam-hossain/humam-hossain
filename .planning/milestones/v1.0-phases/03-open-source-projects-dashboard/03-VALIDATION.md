---
phase: "3"
slug: "open-source-projects-dashboard"
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-11-07"
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x / 8.x |
| **Config file** | none (standard root tests/ discovery) |
| **Quick run command** | `pytest tests/test_projects.py -q` |
| **Full suite command** | `pytest tests/ -v` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_projects.py -q`
- **After every plan wave:** Run `pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | PROJ-02 | — | Validates config parsing, schema defaults, and fallback handling | unit | `pytest tests/test_projects.py -k "test_curation" -v` | ❌ W0 | ⬜ pending |
| 03-01-02 | 01 | 1 | PROJ-01 | — | Verifies batched GraphQL query builder and alias parsing | unit | `pytest tests/test_projects.py -k "test_graphql" -v` | ❌ W0 | ⬜ pending |
| 03-02-01 | 02 | 2 | PROJ-03 | — | Verifies XML ElementTree validation, viewBox 850x340, and ANSI tokens | unit | `pytest tests/test_projects.py -k "test_svg_xml_validity or test_geometry" -v` | ❌ W0 | ⬜ pending |
| 03-02-02 | 02 | 2 | PROJ-01, PROJ-03 | — | Verifies 2-line description clamping, XML escaping, and muted zeroes | unit | `pytest tests/test_projects.py -k "test_description or test_zero_count" -v` | ❌ W0 | ⬜ pending |
| 03-03-01 | 03 | 3 | AUTO-01 | — | Tests coordinator cache persistence, offline fallback, and CLI logging | unit / integration | `pytest tests/test_projects.py -k "test_cache or test_offline" -v` | ❌ W0 | ⬜ pending |
| 03-03-02 | 03 | 3 | PROJ-01, AUTO-01 | — | Tests idempotent README injection between markers and quick-links | unit / integration | `pytest tests/test_projects.py -k "test_readme" -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_projects.py` — test suite covering PROJ-01, PROJ-02, PROJ-03, and AUTO-01
- [ ] Shared fixtures in `tests/test_projects.py` or `tests/conftest.py` — sample GraphQL responses, mock projects configuration

*If none: "Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Visual aesthetic & GitHub dark theme contrast | PROJ-03 | GitHub Camo proxy image display and browser contrast cannot be fully tested headlessly | Open `assets/projects.svg` in browser or view `README.md` on GitHub to confirm visual alignment with `assets/hero.svg` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
