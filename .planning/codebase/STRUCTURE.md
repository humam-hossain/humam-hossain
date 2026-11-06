---
last_mapped_commit: 65828da26b9a3c38688ba6b3980d5de0f182eb08
---

# Directory Structure

**Analysis Date:** 2026-11-06

## Directory Layout

```
humam-hossain/
├── .planning/                  # Project management, codebase maps, specifications
│   └── codebase/              # Codebase intelligence documents
├── certs/                     # Certification images and awards documentation
├── cv/                        # LaTeX resume source files and build pipeline
│   ├── bin/                   # Build artifacts, aux, and log files
│   ├── outputs/               # Compiled PDF CVs
│   ├── sections/              # Modular LaTeX sections (skills, projects, experience)
│   ├── build.sh               # Compilation script for TeX resumes
│   ├── config.tex             # Document styling and macro configuration
│   ├── cv_humam_hossain.tex   # Master general CV
│   └── cv_humam_hossain_sqa.tex # SQA-focused CV
├── Portfolio/                 # Experimental HTML/React UI prototype canvas
│   ├── components/            # Interactive canvas components (hover, cursor glow)
│   ├── scripts/               # Canvas data definitions
│   └── index.html             # Prototype entrypoint
├── public/                    # Static web assets served by Next.js
│   ├── images/                # Screenshots, project thumbnails, webp/jpg assets
│   └── favicon.ico            # Site favicon
├── src/                       # Next.js React application source
│   ├── components/            # Reusable UI components (Hero, Projects, Header, etc.)
│   ├── constants/             # Static portfolio data definitions
│   ├── layout/                # Container layouts and framing
│   ├── pages/                 # Next.js page routes (_app, index, all-projects)
│   ├── styles/                # Global styled-components definitions
│   └── themes/                # Theme tokens and color variables
├── Note.md                    # Setup scratchpad and deployment guide
├── README.md                  # GitHub special profile README
├── package.json               # Node.js project manifest and scripts
└── yarn.lock                  # Yarn dependency lockfile
```

## Key File Locations

- `README.md` - Primary target for GitHub Profile rendering.
- `package.json` - Next.js script configurations (`dev`, `build`, `start`).
- `src/constants/constants.js` - Project list, timeline milestones, and technology lists.
- `cv/sections/skills.tex` - Categorized technical skills inventory.
- `cv/sections/summary.tex` - Professional profile summary.
- `cv/build.sh` - Automated script compiling LaTeX source to PDF outputs.

## Naming Conventions

- **JavaScript Components**: PascalCase directories and files under `src/components/` (e.g. `Projects/Projects.js`, `Header/Header.js`).
- **Pages**: Kebab-case or standard Next.js conventions (`_app.js`, `all-projects.js`, `index.js`).
- **LaTeX Partials**: Snake_case descriptive names under `cv/sections/` prefixed by domain (e.g. `project_krpc5.tex`, `exp_square_intern.tex`, `award_krpc6.tex`).

---
*Codebase analysis: 2026-11-06*
<!-- refreshed: 2026-11-06 -->
