#!/usr/bin/env bash
set -u
set -e
set -o pipefail

echo "Running code climate analyze..."
codeclimate analyze -f html > code_climate.html

echo "Opening output in Chrome..."
google-chrome code_climate.html &

echo "Done"

