#!/usr/bin/env python3
"""
scripts/generate_projects.py
Standalone SVG vector graphics generator for Open Source Projects Dashboard.
Terminal-themed 2x2 grid card display for featured repositories.
Standard library only: json, pathlib, xml.etree.ElementTree, xml.sax.saxutils.
Zero external dependencies.
"""

from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

DEFAULT_PROJECT_FIXTURES = [
    {
        "repo": "humam-hossain/linux_shell_scripting",
        "name": "linux_shell_scripting",
        "description": "Shell scripts and automation utilities for Unix systems",
        "stars": 0,
        "forks": 0,
        "open_issues": 0,
        "open_prs": 0,
        "language": "Shell",
        "language_color": "#89e051",
        "topics": ["bash", "shell", "automation"],
        "url": "https://github.com/humam-hossain/linux_shell_scripting",
    },
    {
        "repo": "humam-hossain/Python",
        "name": "Python",
        "description": "Python algorithms, utilities, and robotics tools",
        "stars": 0,
        "forks": 0,
        "open_issues": 0,
        "open_prs": 0,
        "language": "Python",
        "language_color": "#3572A5",
        "topics": ["python", "algorithms", "robotics"],
        "url": "https://github.com/humam-hossain/Python",
    },
    {
        "repo": "humam-hossain/nn",
        "name": "nn",
        "description": "C-based neural network framework for matrix operations and gradient learning",
        "stars": 0,
        "forks": 0,
        "open_issues": 0,
        "open_prs": 0,
        "language": "C",
        "language_color": "#555555",
        "topics": ["c", "machine-learning", "neural-network"],
        "url": "https://github.com/humam-hossain/nn",
    },
    {
        "repo": "humam-hossain/antigravity-cli-statusline",
        "name": "antigravity-cli-statusline",
        "description": "Advanced responsive statusline plugin for Antigravity CLI",
        "stars": 0,
        "forks": 0,
        "open_issues": 0,
        "open_prs": 0,
        "language": "Shell",
        "language_color": "#89e051",
        "topics": ["cli", "statusline", "zsh"],
        "url": "https://github.com/humam-hossain/antigravity-cli-statusline",
    },
]
