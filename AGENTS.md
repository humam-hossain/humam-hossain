<!-- GSD:project-start source:PROJECT.md -->

## Project

**Terminal-Themed GitHub Profile README (humam-hossain)**

An automated, self-updating GitHub Profile README for Muhammed Humam Hossain (`humam-hossain`) that emulates a sleek, authentic Unix terminal / Neofetch interface. Powered by scheduled GitHub Actions, the profile delivers real-time repository metrics, commit uptime telemetry, dynamic lines-of-code tracking, top language distribution, and open-source project dashboards—all unified under a strict dark terminal aesthetic.

**Core Value:** Every single profile component must strictly adhere to the same unified terminal design language (dark terminal background, monospace typography, terminal box borders, ANSI syntax colors) while keeping all live metrics automatically refreshed via free GitHub Actions.

### Constraints

- **Design Consistency**: Every visual element must match the terminal aesthetic: background `#161b22`/`#0d1117`, monospace fonts (`Consolas`, `Fira Code`), ANSI colors (Amber `#ffa657`, Cyan `#a5d6ff`, Green `#3fb950`, Red `#f85149`, Muted `#616e7f`).
- **Cost**: $0.00 infrastructure cost — must leverage GitHub Actions free unlimited tier for public repositories.
- **Authentication**: Python scripts querying GitHub GraphQL API must utilize the default `GITHUB_TOKEN` provided by the workflow runner or a fine-grained PAT.
- **Theme Support**: Hero SVGs should support both dark and light modes via GitHub's native `<picture>` media queries.

<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->

## Technology Stack

## Languages

- JavaScript (ES6+) - Next.js portfolio application code (`src/pages/`, `src/components/`, `src/styles/`)
- LaTeX - Curated CV and resume build artifacts (`cv/`, `cv/sections/`)
- Bash / Shell - Build automation scripts (`cv/build.sh`)
- HTML5 / CSS3 - Static templates and canvas prototypes (`Portfolio/`, `public/`)

## Runtime

- Node.js 16.x - 18.x compatible runtime (inferred from Next.js 12.3.0 / React 17.0.2 dependencies)
- TeX Live / XeLaTeX environment for CV compilation
- Yarn (v1 classic)
- Lockfile: `yarn.lock` present and committed

## Frameworks

- Next.js 12.3.0 - Static site generator and React SSR/SSG framework (`package.json`)
- React 17.0.2 - Component library (`package.json`)
- Styled Components 5.3.5 - CSS-in-JS styling system (`src/styles/`)
- Framer Motion 6.5.1 - Animation library (`src/components/`)
- `next-dark-mode` 3.0.0 - Theme toggling support
- `next-seo` 5.5.0 - Meta tag and SEO configuration
- `react-icons` 4.4.0 - Icon set library
- `react-image-gallery` 1.2.9 - Lightbox/gallery modal components
- `react-modal` 3.15.1 - Accessible modal dialogs
- Prettier 2.7.1 - Code formatting
- ESLint Config Prettier 8.5.0 - Lint rule harmonization

## Key Dependencies

- `next` (12.3.0) - Core React framework with `next dev`, `next build`, `next export` workflows
- `styled-components` (5.3.5) - Theme provider and scoped styling
- `framer-motion` (6.5.1) - Micro-interactions and transition animations
- `react-icons` (4.4.0) - Vector icon sets (Fa, Fi, Ai icons)

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

## Code Style & Formatting

- **Module Syntax:** ES6 imports/exports (`import React from 'react'`).
- **Formatting:** Prettier configured (`eslint-config-prettier` 8.5.0, `prettier` 2.7.1).
- **Component Patterns:** Functional components with React arrow functions (`const Home = () => { ... }`).
- **Styling Architecture:** Styled Components defining CSS-in-JS primitives (`LayoutStyles.js`, `GlobalComponents/index.js`).
- **Component File Pairing:** Component directory mirrors component file name (e.g., `src/components/Hero/Hero.js`, `src/components/Hero/HeroStyles.js`).
- **Section Modularity:** Individual sections segregated into separate files in `cv/sections/` and brought together using `\input{sections/...}`.
- **Font & Palette Harmonization:** Centralized macros in `cv/config.tex` controlling section headings, dividing rules, and color palettes.
- **Build Isolation:** Compilation flags redirecting logs and aux files into `cv/bin/` to maintain a clean root.

## Error Handling & Validation

- Next.js default custom 404 handler implemented in `src/pages/404.js`.
- Fallbacks in place for missing project previews (e.g. `imageWebp` fallback to `image`).
- Shell script error checking in `cv/build.sh` using exit status handling.

<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

## Pattern Overview

- **Static Next.js Web App**: Pre-rendered React application configured for static export (`next export`).
- **Decoupled Data Architecture**: Content, projects, skills, and timeline entries are maintained as plain JavaScript objects in `src/constants/constants.js`.
- **Modular LaTeX Document Engine**: Resume generation is decoupled into distinct TeX partials (`cv/sections/`) compiled via automated shell tooling (`cv/build.sh`).
- **Experimental Design Sandbox**: Isolated prototype canvas in `Portfolio/` exploring interactive animations and cursor effects.

## Layers

- Purpose: Render portfolio views, navigation, dynamic theme switching, project modals, and skill lists.
- Contains: Next.js page components, UI widgets (Hero, Header, Footer, Projects, Technologies, Timeline), styled-components primitives.
- Depends on: `src/layout/`, `src/styles/`, `src/themes/`, `src/constants/constants.js`.
- Purpose: Establish global responsive container layouts, color schemes, typography, and dark-mode themes.
- Contains: `Layout.js`, `GlobalComponents/`, `default.js` theme constants.
- Purpose: Single source of truth for portfolio content.
- Contains: `constants.js` containing `projects`, `TimeLineData`, `AccomplishmentData`.
- Purpose: Build production PDFs for general software engineering and SQA roles.
- Contains: Root TeX masters, modular section fragments, and compilation bash scripts.

## Data Flow

<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.agents/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
