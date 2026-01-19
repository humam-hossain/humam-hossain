#!/bin/bash
set -e

# This script automates the building of the LaTeX CV.
# It's designed for Arch Linux and uses 'pacman' for dependency management.
# It will check for required TeX Live packages and install them if they are missing.
# It then compiles the LaTeX source twice to ensure all cross-references are correct.

echo "--- Checking Dependencies ---"
PACKAGES=(
    "texlive-latexrecommended"
    "texlive-fontsextra"
    "texlive-latexextra"
)

for pkg in "${PACKAGES[@]}"; do
    if ! pacman -Q "$pkg" &>/dev/null; then
        echo "Installing $pkg..."
        sudo pacman -S --noconfirm "$pkg"
    fi
done
echo "Dependencies are satisfied."

# --- Build ---
echo "--- Building CV PDF ---"
set -x # Echo commands

mkdir -p bin
xelatex cv_humam_hossain.tex
xelatex cv_humam_hossain.tex

# --- Cleanup ---
set +x
echo "--- Moving build files to bin/ ---"
# Enable nullglob to prevent errors if no files match a pattern
shopt -s nullglob
mv -f -- *.aux *.log *.out bin/

echo "--- Build complete! ---"
