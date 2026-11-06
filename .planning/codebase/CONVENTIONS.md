---
last_mapped_commit: 65828da26b9a3c38688ba6b3980d5de0f182eb08
---

# Coding Conventions

**Analysis Date:** 2026-11-06

## Code Style & Formatting

**JavaScript / React:**
- **Module Syntax:** ES6 imports/exports (`import React from 'react'`).
- **Formatting:** Prettier configured (`eslint-config-prettier` 8.5.0, `prettier` 2.7.1).
- **Component Patterns:** Functional components with React arrow functions (`const Home = () => { ... }`).
- **Styling Architecture:** Styled Components defining CSS-in-JS primitives (`LayoutStyles.js`, `GlobalComponents/index.js`).
- **Component File Pairing:** Component directory mirrors component file name (e.g., `src/components/Hero/Hero.js`, `src/components/Hero/HeroStyles.js`).

**LaTeX / CV:**
- **Section Modularity:** Individual sections segregated into separate files in `cv/sections/` and brought together using `\input{sections/...}`.
- **Font & Palette Harmonization:** Centralized macros in `cv/config.tex` controlling section headings, dividing rules, and color palettes.
- **Build Isolation:** Compilation flags redirecting logs and aux files into `cv/bin/` to maintain a clean root.

## Error Handling & Validation

- Next.js default custom 404 handler implemented in `src/pages/404.js`.
- Fallbacks in place for missing project previews (e.g. `imageWebp` fallback to `image`).
- Shell script error checking in `cv/build.sh` using exit status handling.

---
*Codebase analysis: 2026-11-06*
<!-- refreshed: 2026-11-06 -->
