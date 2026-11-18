#!/usr/bin/env python3
"""
scripts/update_profile.py
Wrapper delegating to scripts/build_profile.py for backward compatibility.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from scripts.build_profile import main
except ImportError:
    from build_profile import main

if __name__ == "__main__":
    sys.exit(main())
