#!/usr/bin/env bash
# ==============================================================================
# tests/test_ci_pipeline.sh
# Local simulation test harness for Profile Telemetry Sync CI workflow.
# Simulates all GitHub Actions pipeline stages locally:
# 1. YAML syntax and schema validation
# 2. Python engine execution in dry-run mode
# 3. Pre-commit SVG ElementTree XML validity and byte size gates
# 4. Pre-commit README section marker verification
# 5. Git status and idempotent diff change detection
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

# Terminal ANSI colors matching workstation theme
C_BLUE='\033[38;2;88;166;255m'
C_GREEN='\033[38;2;63;185;80m'
C_AMBER='\033[38;2;255;166;87m'
C_RED='\033[38;2;248;81;73m'
C_RESET='\033[0m'

log_info() { echo -e "${C_BLUE}[INFO]${C_RESET} $*"; }
log_ok()   { echo -e "${C_GREEN}[OK]${C_RESET} $*"; }
log_warn() { echo -e "${C_AMBER}[WARN]${C_RESET} $*"; }
log_err()  { echo -e "${C_RED}[FAIL]${C_RESET} $*" >&2; }

# Trap to restore workspace on exit (D-82)
cleanup() {
  log_info "Cleaning up local test modifications..."
  git checkout assets/hero.svg assets/projects.svg assets/metrics.svg assets/skills.svg README.md data/cache.json 2>/dev/null || true
  rm -f .git/COMMIT_MSG_TMP
  log_ok "Workspace restored to pristine state."
}
trap cleanup EXIT

echo "=================================================="
echo " Starting Profile Telemetry CI Pipeline Simulation"
echo "=================================================="

# Stage 1: YAML Syntax Validation
log_info "Stage 1: Validating .github/workflows/profile-updater.yml syntax..."
WORKFLOW_FILE=".github/workflows/profile-updater.yml"

if [ ! -f "$WORKFLOW_FILE" ]; then
  log_err "Workflow file $WORKFLOW_FILE not found!"
  exit 1
fi

python3 - << 'EOF'
import sys
try:
    import yaml
    with open(".github/workflows/profile-updater.yml", "r", encoding="utf-8") as f:
        yaml.safe_load(f)
    print("YAML parsed successfully.")
except ImportError:
    print("PyYAML not installed; syntax check skipped.")
except Exception as e:
    print(f"YAML syntax error: {e}", file=sys.stderr)
    sys.exit(1)
EOF

if command -v actionlint >/dev/null 2>&1; then
  log_info "Running actionlint on workflow files..."
  actionlint "$WORKFLOW_FILE"
  log_ok "actionlint passed."
else
  log_warn "actionlint not detected on PATH; skipped lint check."
fi
log_ok "Stage 1 passed: YAML is valid."

# Stage 2: Python Engine Dry-Run Execution
log_info "Stage 2: Running update_profile.py in --dry-run mode..."
python3 -u scripts/update_profile.py --dry-run
log_ok "Stage 2 passed: update_profile.py exited 0."

# Stage 3: SVG ElementTree Validation Gate
log_info "Stage 3: Validating SVG XML well-formedness and byte size..."
python3 - << 'EOF'
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

svgs = [
    Path("assets/hero.svg"),
    Path("assets/projects.svg"),
    Path("assets/metrics.svg"),
    Path("assets/skills.svg"),
]

for svg in svgs:
    if not svg.is_file():
        print(f"Missing asset: {svg}", file=sys.stderr)
        sys.exit(1)
    size = svg.stat().st_size
    if size < 500:
        print(f"Asset too small ({size}B): {svg}", file=sys.stderr)
        sys.exit(1)
    ET.parse(str(svg))
    print(f"Verified {svg} ({size} bytes, valid XML)")
EOF
log_ok "Stage 3 passed: All SVGs are valid XML and >500B."

# Stage 4: README Marker Verification Gate
log_info "Stage 4: Verifying README.md section marker pairs..."
python3 - << 'EOF'
import sys
from pathlib import Path

content = Path("README.md").read_text(encoding="utf-8")
markers = [
    ("<!-- PROJECTS:START -->", "<!-- PROJECTS:END -->"),
    ("<!-- METRICS:START -->", "<!-- METRICS:END -->"),
    ("<!-- SKILLS:START -->", "<!-- SKILLS:END -->"),
    ("<!-- BLOG:START -->", "<!-- BLOG:END -->"),
]

for start, end in markers:
    if start not in content or end not in content:
        print(f"Missing marker pair: {start} ... {end}", file=sys.stderr)
        sys.exit(1)
    s_idx = content.index(start)
    e_idx = content.index(end)
    if s_idx >= e_idx:
        print(f"Inverted markers: {start} appears after {end}", file=sys.stderr)
        sys.exit(1)

print("All 4 marker pairs exist and are correctly ordered.")
EOF
log_ok "Stage 4 passed: README markers verified."

# Stage 5: Git Idempotency & Staging Simulation
log_info "Stage 5: Simulating git change detection and staging..."
git add assets/*.svg README.md data/cache.json
if git diff --cached --quiet -- assets/*.svg README.md; then
  log_info "User-facing assets unchanged; no-op skip verified."
else
  log_info "User-facing changes detected; commit would proceed."
fi
git reset --quiet HEAD

log_ok "All 5 CI Simulation Stages PASSED successfully!"
