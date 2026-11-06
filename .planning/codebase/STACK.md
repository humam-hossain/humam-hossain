---
last_mapped_commit: 65828da26b9a3c38688ba6b3980d5de0f182eb08
---

# Technology Stack

**Analysis Date:** 2026-11-06

## Languages

**Primary:**
- JavaScript (ES6+) - Next.js portfolio application code (`src/pages/`, `src/components/`, `src/styles/`)
- LaTeX - Curated CV and resume build artifacts (`cv/`, `cv/sections/`)

**Secondary:**
- Bash / Shell - Build automation scripts (`cv/build.sh`)
- HTML5 / CSS3 - Static templates and canvas prototypes (`Portfolio/`, `public/`)

## Runtime

**Environment:**
- Node.js 16.x - 18.x compatible runtime (inferred from Next.js 12.3.0 / React 17.0.2 dependencies)
- TeX Live / XeLaTeX environment for CV compilation

**Package Manager:**
- Yarn (v1 classic)
- Lockfile: `yarn.lock` present and committed

## Frameworks

**Core:**
- Next.js 12.3.0 - Static site generator and React SSR/SSG framework (`package.json`)
- React 17.0.2 - Component library (`package.json`)
- Styled Components 5.3.5 - CSS-in-JS styling system (`src/styles/`)
- Framer Motion 6.5.1 - Animation library (`src/components/`)

**Utilities & Plugins:**
- `next-dark-mode` 3.0.0 - Theme toggling support
- `next-seo` 5.5.0 - Meta tag and SEO configuration
- `react-icons` 4.4.0 - Icon set library
- `react-image-gallery` 1.2.9 - Lightbox/gallery modal components
- `react-modal` 3.15.1 - Accessible modal dialogs

**Build/Dev:**
- Prettier 2.7.1 - Code formatting
- ESLint Config Prettier 8.5.0 - Lint rule harmonization

## Key Dependencies

- `next` (12.3.0) - Core React framework with `next dev`, `next build`, `next export` workflows
- `styled-components` (5.3.5) - Theme provider and scoped styling
- `framer-motion` (6.5.1) - Micro-interactions and transition animations
- `react-icons` (4.4.0) - Vector icon sets (Fa, Fi, Ai icons)

---
*Codebase analysis: 2026-11-06*
<!-- refreshed: 2026-11-06 -->
