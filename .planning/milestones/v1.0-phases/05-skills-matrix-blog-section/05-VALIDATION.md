---
phase: "05"
slug: "skills-matrix-blog-section"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: true) (#2117)
status: draft
nyquist_compliant: true
wave_0_complete: false
created: "2026-11-08"
---

# Phase 05 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.2.0 |
| **Config file** | none (standard discovery) |
| **Quick run command** | `pytest tests/test_skills.py tests/test_blog.py -v` |
| **Full suite command** | `pytest` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_skills.py tests/test_blog.py -v`
- **After every plan wave:** Run `pytest`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 1 | CONTENT-02 | T-05-01 | Config schema, tracer SVG skeleton & test scaffold | unit | `pytest tests/test_skills.py -v` | ❌ W0 | ⬜ pending |
| 05-01-02 | 01 | 1 | CONTENT-02 | T-05-02, T-05-03 | Dynamic flow-pack layout, 2x2 grid, XML validation & CLI | unit | `python3 scripts/generate_skills.py && pytest tests/test_skills.py -v` | ❌ W0 | ⬜ pending |
| 05-01-03 | 01 | 1 | CONTENT-02 | — | update_profile skills integration & README injection | integration | `python3 scripts/update_profile.py && pytest tests/ -v` | ❌ W0 | ⬜ pending |
| 05-02-01 | 02 | 2 | CONTENT-01 | — | Articles config, mock XML fixtures (RSS 2.0 & Atom 1.0) & harness | unit | `pytest tests/test_blog.py -v` | ❌ W0 | ⬜ pending |
| 05-02-02 | 02 | 2 | CONTENT-01 | T-05-04, T-05-05, T-05-06 | Feed parser, date normalizer, 12h cache & secure log formatter | unit | `pytest tests/test_blog.py -v` | ❌ W0 | ⬜ pending |
| 05-02-03 | 02 | 2 | CONTENT-01 | — | README blog injection, streamlined sequence & full suite | integration | `python3 scripts/update_profile.py && pytest` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_skills.py` — unit and integration test suite covering CONTENT-02
- [ ] `tests/test_blog.py` — unit and integration test suite covering CONTENT-01
- [ ] `tests/fixtures/feed_rss2.xml` — mock RSS 2.0 feed fixture
- [ ] `tests/fixtures/feed_atom.xml` — mock Atom 1.0 feed fixture

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Desktop SVG hover transition | CONTENT-02 | Embedded SVG CSS hover transitions render differently across browser engines | Open `assets/skills.svg` in Chrome/Firefox, hover over skill pills, verify brightness and border tint |
| GitHub Web Markdown link clicks | CONTENT-01 | GitHub web UI renders HTML `<pre><code><a>` links in profile view | Open profile README in GitHub browser view, click article links to verify navigation |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
