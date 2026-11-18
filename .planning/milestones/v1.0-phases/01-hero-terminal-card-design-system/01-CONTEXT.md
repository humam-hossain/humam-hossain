# Phase 1: Hero Terminal Card & Design System - Context

**Gathered:** 2026-11-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver a static dark-theme SVG terminal hero card (`assets/hero.svg`) rendered at the top of the GitHub profile README (`README.md`), featuring a stylized `H_` ASCII block monogram, `humam@workstation:~` telemetry, and a reusable design token configuration (`config/terminal_theme.json`) that establishes the design language for all subsequent profile features.
</domain>

<decisions>
## Implementation Decisions

### Theme Scope & Visual Identity
- **D-01:** **Dark Theme Only** — Single dedicated dark terminal SVG (`assets/hero.svg`). No light mode SVG or `<picture>` media query switching logic. — **Reversibility:** costly — Eliminating light mode simplifies SVG generation and downstream dashboard cards, but adding light mode later would require updating all generated SVGs and README markup.
- **D-02:** **Immediate Visual Opener** — The hero SVG card is the first element at the top of `README.md`, centered via `<div align="center">`, with no redundant text header above it.

### ASCII Monogram (`H_`)
- **D-03:** **Block-Art Typography** — Large retro Neofetch block-art `H_` (~8–10 lines tall) built using solid Unicode block characters (`█`, `▄`, `▀`).
- **D-04:** **Monogram Palette & Cursor** — Cyan (`#a5d6ff`) block characters with a static underscore (`_`) representing an authentic terminal prompt waiting for input.
- **D-05:** **Standalone Left Panel** — The monogram sits independently on the left panel (~35% width) without an enclosing sub-box, separated from telemetry by clean whitespace margin.
- **D-06:** **ANSI Diagnostic Dot Strip** — A single horizontal row of 8 circular ANSI color dots (`<circle r="6">` for Black/Gray, Red, Green, Amber, Blue, Magenta, Cyan, White) centered horizontally directly beneath the `H_` monogram art.

### Terminal Telemetry Content (Right Panel)
- **D-07:** **Prompt Header** — `humam@workstation:~` at the top of the telemetry panel followed by an authentic dashed rule divider (`-------------------`) in muted gray (`#616e7f`).
- **D-08:** **Label & Value Hierarchy** — Amber (`#ffa657`) keys/labels with high-contrast muted white (`#c9d1d9`) text values.
- **D-09:** **Exact Telemetry Fields & Wording**:
  - `OS`: `Arch Linux x86_64`
  - `Host`: `Workstation`
  - `Kernel`: `AI & Robotics`
  - `Focus`: `Autonomous Systems, IoT & Cloud`
  - `Uptime`: Realistic static placeholder (`4 yrs, 3 mos, 12 days`) prior to Phase 2 automation
  - `Shell`: `zsh 5.9`
  - `Contact`: Formatted plain text handles (`humam@...` / `in/humam-hossain`)
  - `LOC`: Realistic static placeholder (`++320,410 / --85,240`) prior to Phase 2 automation

### SVG Card Architecture & Geometry
- **D-10:** **Dimensions & Scaling** — Responsive `viewBox="0 0 850 380"` embedded with `width="100%"` inside `README.md` to cleanly fill GitHub's desktop content column while scaling down fluidly on mobile viewports.
- **D-11:** **Window Frame & Chrome** — Subtle rounded corners (`rx="10"`) with a 1px border (`#30363d`). Title bar includes colored traffic lights (🔴 `#ff5f56`, 🟡 `#ffbd2e`, 🟢 `#27c93f`) and centered title `humam@workstation:~`.
- **D-12:** **Dual-Tone Dark Background** — Header bar `#161b22` with a 1px border line (`#30363d`) over a dark console body (`#0d1117`).
- **D-13:** **Cross-Platform Monospace Font Stack** — Defined in SVG `<style>` as `ui-monospace, SFMono-Regular, Menlo, Consolas, "Fira Code", monospace` to ensure crisp rendering across all operating systems through GitHub's Camo image proxy.

### Design System Token Engine & Automation
- **D-14:** **Single Source of Truth** — Tokens defined in `config/terminal_theme.json` covering colors (backgrounds, borders, text, harmonized GitHub Dark ANSI palette), typography (font-stack, sizes, line heights), and geometry (padding, corner radii, viewBox dimensions). — **Reversibility:** costly — Downstream Python scripts in Phases 2–6 will load this config file.
- **D-15:** **Python Generator Script** — `scripts/generate_hero.py` reads `config/terminal_theme.json` and renders `assets/hero.svg`. Self-contained with zero external template package dependencies.
- **D-16:** **Design Documentation** — `docs/DESIGN_SYSTEM.md` created to document color swatches, typography rules, and aesthetic constraints for human reference.
- **D-17:** **Validation Suite** — `tests/test_tokens.py` to verify JSON token schema, valid hex codes, and well-formed SVG XML structure.

### Profile Layout (`README.md`)
- **D-18:** **Relative Image Embed** — Embedded via `<div align="center"><img src="./assets/hero.svg" alt="humam@workstation" width="100%" /></div>`.
- **D-19:** **Terminal Contact Badges** — Flat-square Shields.io badges with dark background (`#161b22`) for Email, LinkedIn, Portfolio, and Resume directly below the card. Resume badge points to local repository artifact `cv/outputs/cv_humam_hossain.pdf`.
- **D-20:** **Phase Expansion Anchors** — Structured HTML comment markers (`<!-- PROJECTS:START -->...<!-- PROJECTS:END -->`, `<!-- METRICS:START -->...`, `<!-- SKILLS:START -->...`) for seamless insertion by subsequent phase automation.
- **D-21:** **Terminal Exit Sign-Off** — Bottom terminal prompt: `<div align="center"><code>humam@workstation:~$ exit</code></div>`.

### the agent's Discretion
- Micro-spacing and exact pixel baseline offsets for telemetry lines within SVG `viewBox="0 0 850 380"`.
- Precise character width ratios for full/half-block rendering in SVG `<text>` elements.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Specifications & Requirements
- `.planning/PROJECT.md` — Core value, technical constraints, ANSI palette rules, and scope boundaries.
- `.planning/REQUIREMENTS.md` — Full requirements catalog (specifically HERO-01, HERO-02, HERO-03).
- `.planning/ROADMAP.md` — Phase 1 goals, plans breakdown, and success criteria.

### Codebase Intelligence & Assets
- `.planning/codebase/CONVENTIONS.md` — Code style, formatting, and file organization.
- `.planning/codebase/STRUCTURE.md` — Directory structure and key file locations.
- `cv/outputs/cv_humam_hossain.pdf` — Existing compiled resume referenced by the README CV badge.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `cv/outputs/cv_humam_hossain.pdf` — Pre-existing compiled resume artifact to link from the top README badge row.
- `cv/sections/summary.tex` & `cv/sections/skills.tex` — Domain keywords (`AI & Robotics`, `Autonomous Systems, IoT & Cloud`) harmonized with CV source.

### Established Patterns
- Clean component separation: `scripts/` for Python scripts, `config/` for JSON configurations, `assets/` for generated SVGs, `tests/` for validation scripts.

### Integration Points
- `README.md` — Root GitHub profile overview file to be populated with the hero card, badges, extension anchors, and exit prompt.
- `assets/hero.svg` — Target output file generated by `scripts/generate_hero.py`.
</code_context>

<specifics>
## Specific Ideas
- Authentic Neofetch CLI visual arrangement: Left panel features large `H_` monogram with a neat 8-dot ANSI diagnostic strip beneath it; right panel features `humam@workstation:~` followed by dashed divider and Amber-labeled telemetry rows.
- Pure dark aesthetic that integrates smoothly with GitHub's default dark theme.
</specifics>

<deferred>
## Deferred Ideas
- Phase 2: Live GitHub API computation for dynamic Uptime calculation and aggregate Lines of Code counters (`scripts/update_profile.py`).
- Phase 3: Open Source Projects Dashboard terminal box cards.
- Phase 4: Top Languages terminal progress bar and Git activity log stream.
- Phase 5: Categorized Skills Matrix and RSS blog slot.
- Phase 6: Daily scheduled GitHub Actions workflow.
</deferred>

---

*Phase: 1-Hero Terminal Card & Design System*
*Context gathered: 2026-11-07*
