---
phase: "06"
slug: "github-actions-automation"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: true) (#2117)
status: draft
nyquist_compliant: true
wave_0_complete: false
created: "2026-11-15"
---

# Phase 06 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.2.0 + bash test harness |
| **Config file** | none (standard discovery) |
| **Quick run command** | `pytest tests/test_automation.py -v` |
| **Full suite command** | `pytest && bash tests/test_ci_pipeline.sh` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_automation.py -v`
- **After every plan wave:** Run `pytest && bash tests/test_ci_pipeline.sh`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 06-01-01 | 01 | 1 | AUTO-02 | T-06-01 | Workflow YAML syntax, triggers, permissions, intermediate env vars | unit | `pytest tests/test_automation.py -k "test_workflow" -v` | ❌ W0 | ⬜ pending |
| 06-01-02 | 01 | 1 | AUTO-03 | T-06-02, T-06-03 | Commit msg generator, Git Trailers, Camo cache-busting, Step Summary | unit | `pytest tests/test_automation.py -k "test_engine" -v` | ❌ W0 | ⬜ pending |
| 06-01-03 | 01 | 1 | AUTO-02, AUTO-03 | T-06-04 | Pre-commit SVG/README gates, idempotent dry-run, push retry script | integration | `bash tests/test_ci_pipeline.sh` | ❌ W0 | ⬜ pending |
| 06-02-01 | 02 | 2 | AUTO-02, AUTO-03 | — | Full suite validation & live GitHub Actions end-to-end telemetry | integration | `pytest && bash tests/test_ci_pipeline.sh` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_automation.py` — unit tests covering workflow YAML schema, commit message generator, Git trailers, Camo date-stamp cache-busting regex, and Step Summary ANSI/Markdown formatting
- [ ] `tests/test_ci_pipeline.sh` — standalone local CI pipeline simulation script covering dry-run, pre-commit SVG/README gates, and git staging idempotency

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| GitHub Actions Live Execution & UI Badges | AUTO-02, AUTO-03 | Live GitHub runners and web UI verification cannot run in offline sandbox | Run `gh workflow run profile-updater.yml` and inspect Actions UI for Neofetch ANSI summary and `github-actions[bot]` commit badge |
| Camo Proxy Image Cache Invalidation | AUTO-02 | GitHub Camo proxy CDN is hosted externally by GitHub | View `https://github.com/humam-hossain` in browser, inspect image source URLs to verify `?v=YYYYMMDD` parameter |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
