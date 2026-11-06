---
last_mapped_commit: 65828da26b9a3c38688ba6b3980d5de0f182eb08
---

# Architecture

**Analysis Date:** 2026-11-06

## Pattern Overview

**Overall:** Hybrid Static Portfolio & Document Generation Pipeline

**Key Characteristics:**
- **Static Next.js Web App**: Pre-rendered React application configured for static export (`next export`).
- **Decoupled Data Architecture**: Content, projects, skills, and timeline entries are maintained as plain JavaScript objects in `src/constants/constants.js`.
- **Modular LaTeX Document Engine**: Resume generation is decoupled into distinct TeX partials (`cv/sections/`) compiled via automated shell tooling (`cv/build.sh`).
- **Experimental Design Sandbox**: Isolated prototype canvas in `Portfolio/` exploring interactive animations and cursor effects.

## Layers

**Presentation Layer (`src/pages/`, `src/components/`):**
- Purpose: Render portfolio views, navigation, dynamic theme switching, project modals, and skill lists.
- Contains: Next.js page components, UI widgets (Hero, Header, Footer, Projects, Technologies, Timeline), styled-components primitives.
- Depends on: `src/layout/`, `src/styles/`, `src/themes/`, `src/constants/constants.js`.

**Layout & Styling Layer (`src/layout/`, `src/styles/`, `src/themes/`):**
- Purpose: Establish global responsive container layouts, color schemes, typography, and dark-mode themes.
- Contains: `Layout.js`, `GlobalComponents/`, `default.js` theme constants.

**Data & Constants Layer (`src/constants/`):**
- Purpose: Single source of truth for portfolio content.
- Contains: `constants.js` containing `projects`, `TimeLineData`, `AccomplishmentData`.

**Document Compilation Engine (`cv/`):**
- Purpose: Build production PDFs for general software engineering and SQA roles.
- Contains: Root TeX masters, modular section fragments, and compilation bash scripts.

## Data Flow

**Portfolio Rendering Flow:**
1. Client requests index route `/` -> `src/pages/_app.js` initializes theme and global styles.
2. `src/pages/index.js` instantiates Layout wrapper (`src/layout/Layout.js`).
3. Layout renders Header, Hero, Projects, Technologies, Timeline, and Footer sequentially.
4. Components import static items from `src/constants/constants.js` and render styled DOM elements.

**CV Build Flow:**
1. Developer runs `./cv/build.sh`.
2. Script invokes `xelatex` targeting `cv/cv_humam_hossain.tex` and `cv/cv_humam_hossain_sqa.tex`.
3. LaTeX compiler resolves includes from `cv/sections/` and styling macros from `cv/config.tex`.
4. Resulting PDFs are written to `cv/outputs/`, auxiliary build files are cleaned into `cv/bin/`.

---
*Codebase analysis: 2026-11-06*
<!-- refreshed: 2026-11-06 -->
