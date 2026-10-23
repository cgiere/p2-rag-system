#!/usr/bin/env bash
# Download the per-commodity chapter PDFs of the USGS Mineral Commodity Summaries into ../p2-raw/mcsYYYY/.
# Skips the whole volume (mcsYYYY.pdf), superseded copies (_ver, -ver, _bef_) and the appendixes.
# Usage, from the repo root: bash scripts/fetch_usgs.sh 2024 2025 2026
set -euo pipefail

for year in "$@"; do
  base="https://pubs.usgs.gov/periodicals/mcs$year"
  out="../p2-raw/mcs$year"
  mkdir -p "$out"
  curl -sfL "$base/" \
    | grep -oE "href=\"mcs$year-[a-z0-9-]+\.pdf\"" \
    | sed -e 's/^href="//' -e 's/"$//' \
    | grep -vE -- '-ver|-appendixes' \
    | sort -u \
    | while read -r name; do
        # Download to a .part file and rename when complete, so a dropped connection leaves no half PDF.
        [ -s "$out/$name" ] || { curl -sfL --retry 5 --retry-all-errors -o "$out/$name.part" "$base/$name" && mv "$out/$name.part" "$out/$name"; }
      done
  echo "mcs$year: $(ls "$out" | wc -l | tr -d ' ') chapters in $out"
done
