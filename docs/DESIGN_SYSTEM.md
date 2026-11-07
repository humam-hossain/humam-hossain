# Terminal Design System Contract

**Project:** Terminal-Themed GitHub Profile README (`humam-hossain`)  
**Version:** 1.0.0  
**Status:** Approved & Implemented  
**Configuration Source:** [`config/terminal_theme.json`](../config/terminal_theme.json)

---

## 1. Terminal Identity & Philosophy

The profile interface emulates a Unix workstation terminal environment inspired by the authentic Neofetch system information tool. The visual composition presents an active terminal session encased in a modern desktop window frame with macOS traffic light chrome.

- **Theme Policy:** Strict dark terminal aesthetic. Light mode is intentionally unsupported; the terminal canvas is fully opaque `#0d1117` to preserve contrast and command-line realism regardless of host client settings.
- **Composition:** Two-column split layout consisting of:
  - **Left Panel (Hero Monogram & ANSI Strip):** A retro ASCII block-art `H_` monogram with a terminal cursor, anchored below by an 8-color diagnostic ANSI dot strip.
  - **Right Panel (System Telemetry):** Neofetch-style system specifications rendered with structured key-value alignment, colorized metric counters, and GitHub activity indicators.

---

## 2. 60-30-10 Color Architecture

The visual palette strictly adheres to the 60-30-10 color rule to ensure visual hierarchy, high legibility, and terminal authenticity:

```
┌─────────────────────────────────────────────────────────────┐
│ 60% Dominant Canvas (#0d1117)                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 30% Structural Frame (#161b22, #30363d)                │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ 10% ANSI & Accent Indicators                        │ │ │
│ │ │ (#a5d6ff, #ffa657, #58a6ff, #3fb950, #f85149)      │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Color Distribution Breakdown

| Role | Color Hex | Name | Application |
|------|-----------|------|-------------|
| **60% Dominant** | `#0d1117` | GitHub Dark Canvas | Terminal console body, SVG background canvas, profile root background. |
| **30% Structural** | `#161b22` | Header Background | Terminal window header bar, Shields.io badge background surfaces. |
| **30% Structural** | `#30363d` | Frame Border | 1px outer card border, header separator line. |
| **30% Structural** | `#8b949e` | Window Title | Centered window header text (`humam@workstation:~`). |
| **30% Structural** | `#c9d1d9` | Telemetry Values | Secondary reading text for metadata values (`.val`). |
| **10% Accent** | `#a5d6ff` | Cyan (High Contrast) | Monogram block glyphs (`.mono-art`) and static prompt cursor (`_`). |
| **10% Accent** | `#ffa657` | Amber | Telemetry keys (`OS:`, `Host:`, `Kernel:`, etc.), Gmail badge logo. |
| **10% Accent** | `#58a6ff` | Blue | Telemetry prompt header (`humam@workstation:~`), LinkedIn badge logo. |
| **10% Accent** | `#616e7f` | Muted Blue-Gray | Dashed prompt divider (`-------------------`). |
| **10% Accent** | `#3fb950` | Green | Git LOC additions (`++320,410`), window zoom traffic light, Portfolio badge logo. |
| **10% Accent** | `#f85149` | Red | Git LOC deletions (`--85,240`), window close traffic light (`#ff5f56`). |

---

## 3. ANSI 8-Color Diagnostic Strip

The 8 circular dots positioned directly beneath the monogram represent the standard 8-color ANSI terminal palette:

| Slot | ANSI Code | Color Hex | Name | Representation |
|:---:|:---:|:---:|---|---|
| 0 | `30m` | `#484f58` | Black / Muted Gray | Background contrast reference |
| 1 | `31m` | `#ff7b72` | Red | Critical alerts / deletions |
| 2 | `32m` | `#3fb950` | Green | Additions / success states |
| 3 | `33m` | `#d29922` | Yellow / Amber | Warning / telemetry keys |
| 4 | `34m` | `#58a6ff` | Blue | Shell prompt / links |
| 5 | `35m` | `#bc8cff` | Magenta | System functions |
| 6 | `36m` | `#79c0ff` | Cyan | Identity / accent glyphs |
| 7 | `37m` | `#f0f6fc` | White | High-contrast foreground |

---

## 4. Typography & Monospace Font Stack

To ensure predictable character widths across all operating systems without relying on external web font downloads:

- **Font Family:** `ui-monospace, SFMono-Regular, Menlo, Consolas, "Fira Code", monospace`
- **Text Rendering:** `geometricPrecision` enabled via SVG style declarations.

### Type Scale

| Role | Font Size | Weight | Line Height | Usage |
|------|-----------|--------|-------------|-------|
| **Window Title** | 13px | 400 | N/A | Window header bar centered title (`humam@workstation:~`) |
| **Monogram Art** | 20px | 700 (bold) | 22px | 8-line Unicode block art monogram (`▄`, `█`, `▀`, `_`) |
| **Prompt Header** | 15px | 700 (bold) | 25px | Right panel terminal prompt |
| **Divider** | 14px | 400 | 25px | Dashed rule separator |
| **Telemetry Keys** | 13.5px | 600 (semi-bold) | 25px | Padded 10-character field labels (`OS:`, `Host:`, etc.) |
| **Telemetry Values** | 13.5px | 400 (normal) | 25px | Dynamic & static metadata text |

---

## 5. Window Chrome & Geometry Grid

The hero terminal card is generated as a scalable vector graphic (`assets/hero.svg`) defined within an absolute coordinate grid:

- **Dimensions & ViewBox:** `width="100%" height="100%" viewBox="0 0 850 380"`
- **Outer Corner Radius:** `rx="10" ry="10"`
- **Header Bar:** Height `38px`, background `#161b22`, separated by a `1px` horizontal border at `y=38`.
- **Traffic Light Controls:**
  - Red (Close): `cx=25, cy=19, r=6, fill="#ff5f56"`
  - Yellow (Minimize): `cx=45, cy=19, r=6, fill="#ffbd2e"`
  - Green (Zoom): `cx=65, cy=19, r=6, fill="#27c93f"`
- **Corner Bleed Isolation:** An explicit `<clipPath id="card-clip">` with `<rect width="850" height="380" rx="10" ry="10" />` encloses all background and header elements to prevent dark background pixels bleeding beyond the rounded borders.
- **Left Panel Layout:**
  - Monogram starts at `x=60`, `y=82`, with `line_height=22` spanning 8 rows down to `y=236`.
  - ANSI strip dots placed at `cy=295`, `r=6`, beginning at `x_start=62` with `spacing=22` across 8 dots (x=62 to x=216).
- **Right Panel Layout:**
  - Starts at `x=310`, `y=82`, with `line_height=25` across 9 distinct visual lines down to `y=282`.

---

## 6. GitHub Camo Proxy Hardening

GitHub routes all profile image assets through its Camo caching proxy (`camo.githubusercontent.com`). To prevent image sanitization stripping, caching corruption, or rendering crashes:

1. **Zero `<foreignObject>`:** Standard SVG `<text>`, `<tspan>`, `<rect>`, and `<circle>` elements are used exclusively.
2. **Zero External Fonts or Styles:** No `@import url(...)` or `<link>` tags. All styles are defined locally within an internal `<style>` block.
3. **XML Entity Escaping:** All dynamic or static text containing special characters (`&`, `<`, `>`, `"`) is escaped using `xml.sax.saxutils.escape()` (e.g. `AI &amp; Robotics`).
4. **Deterministic Static Dimensions:** The SVG declares both responsive sizing (`width="100%" height="100%"`) and an absolute bounding box (`viewBox="0 0 850 380"`).

---

## 7. Downstream Contract: DOM ID Hooks

Phase 2 automated update scripts patch live telemetry values directly into the SVG markup. The following element IDs are permanently reserved:

| Element ID | Tag | Expected Format / Content | Description |
|------------|-----|---------------------------|-------------|
| `val-uptime` | `<tspan>` | `X yrs, Y mos, Z days` | Real-time tenure calculated from developer start epoch |
| `val-loc-add` | `<tspan>` | `++320,410` | Cumulative Git lines of code added |
| `val-loc-del` | `<tspan>` | `--85,240` | Cumulative Git lines of code deleted |

These IDs must remain present in `assets/hero.svg` and are safeguarded by continuous regression checks in `tests/test_tokens.py`.
