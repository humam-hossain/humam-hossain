set -xe

mkdir -p bin
xelatex cv_humam_hossain.tex

mv *.aux *.log *.out bin/