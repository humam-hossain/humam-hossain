---
last_mapped_commit: 65828da26b9a3c38688ba6b3980d5de0f182eb08
---

# External Integrations

**Analysis Date:** 2026-11-06

## APIs & External Services

**Hosting & Static Deployment:**
- Netlify - Target platform for demo deployments linked in project data (`hexcolour.netlify.app`, `secret-message-material.netlify.app`, `petapi.netlify.app`)
- GitHub Pages / Vercel - Compatible static export targets via `next export`

**External Endpoints & CDNs:**
- Google Fonts - Web font loading via `next/document` (`src/pages/_document.js`)
- Unsplash / External Images - Referenced in mock portfolio content

**Git & Version Control Services:**
- GitHub API / Repositories - Source code links referencing user repositories in `src/constants/constants.js`

## Data Storage

**Databases:**
- None active in repository. All portfolio data, project lists, timelines, and accomplishments are statically bundled in `src/constants/constants.js` and `Portfolio/scripts/data.js`.

**File Storage:**
- Local static assets stored in `public/images/`, `public/images/projects/`, and compiled CV PDFs in `cv/outputs/`.

**Caching:**
- Next.js build cache in `.next/` (git-ignored)
- LaTeX intermediate logs and aux files in `cv/bin/`

## Authentication & Security

- No client/server authentication providers (Auth0, Firebase, Supabase) are integrated. The repository serves public portfolio and CV documents.

---
*Codebase analysis: 2026-11-06*
<!-- refreshed: 2026-11-06 -->
