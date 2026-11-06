---
last_mapped_commit: 65828da26b9a3c38688ba6b3980d5de0f182eb08
---

# Codebase Concerns & Technical Debt

**Analysis Date:** 2026-11-06

## Architectural & Repository Concerns

**1. Dual-Identity Special Repository:**
- **Context:** The repository is named `humam-hossain`, which GitHub treats as the special Profile README repository.
- **Concern:** The repo currently houses a full legacy Next.js web application, experimental HTML5 prototypes (`Portfolio/`), and LaTeX CV source code, while `README.md` only contained a placeholder.
- **Recommendation:** Maintain clear separation. The root `README.md` and associated GitHub Actions automation (SVGs, cron jobs) should form the core profile experience, while ensuring legacy application code does not interfere with profile delivery.

**2. Outdated Dependencies (Security & Maintenance):**
- Next.js is pinned to `^12.3.0` and React to `^17.0.2`. Several dependencies have known CVEs in older versions.
- If the web portfolio is maintained alongside the Profile README, an upgrade path to Next.js 14+ or decoupling into a standalone web app repo is advisable.

**3. Content Synchronization Drift:**
- `src/constants/constants.js` contains generic template placeholder projects from earlier starter code.
- Conversely, `cv/sections/` contains Humam's authentic engineering accomplishments (KRPC Robotics Competition, Homeserver & VPS infrastructure, IoT Environmental Quality Control, SQA internship).
- The new Profile README should pull exclusively from authentic engineering sources rather than legacy placeholder arrays.

## Testing & Automation Debt

- **Missing CI/CD:** There are currently no GitHub Actions workflows configured in `.github/workflows/`.
- To achieve Andrew6rant-style automated daily metric updates, a dedicated GitHub Action and authenticated GraphQL fetch script must be established.

---
*Codebase analysis: 2026-11-06*
<!-- refreshed: 2026-11-06 -->
