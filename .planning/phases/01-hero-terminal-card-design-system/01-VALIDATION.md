---
phase: "01"
slug: "hero-terminal-card-design-system"
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-11-07"
---

# Phase 01 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.2.0 |
| **Config file** | none — standard discovery in `tests/` |
| **Quick run command** | `pytest tests/test_tokens.py -q` |
| **Full suite command** | `pytest tests/test_tokens.py -v` |
| **Estimated runtime** | ~1 second |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_tokens.py -q`
- **After every plan wave:** Run `pytest tests/test_tokens.py -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 2 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | HERO-03 | — | JSON theme tokens conform to valid schema and hex values | unit | `pytest tests/test_tokens.py -k test_theme_tokens_schema` | ❌ W0 | ⬜ pending |
| 01-02-01 | 02 | 1 | HERO-01 | — | Generated SVG contains valid block monogram and ANSI circles | unit / integration | `pytest tests/test_tokens.py -k test_hero_svg_monogram_and_ansi` | ❌ W0 | ⬜ pending |
| 01-02-02 | 02 | 1 | HERO-02 | T-01-01 | XML entities escaped via `saxutils.escape()`, valid ElementTree parse, DOM IDs present | unit / integration | `pytest tests/test_tokens.py -k test_hero_svg_telemetry_keys` | ❌ W0 | ⬜ pending |
| 01-03-01 | 03 | 2 | README | T-01-02 | README embeds dark hero SVG, Shields.io badges, and expansion anchors | unit / integration | `pytest tests/test_tokens.py -k test_readme_structure` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_tokens.py` — validation suite covering schema, XML well-formedness, telemetry, and README structure
- [ ] `tests/__init__.py` — test package initialization marker

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| GitHub Profile Appearance | HERO-01 | Render visual check | Inspect `README.md` preview in GitHub or browser to confirm `width="100%"` scaling and contrast |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 2s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
