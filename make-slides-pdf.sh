#!/usr/bin/env bash
# Export the reveal.js decks to PDF locally.
#
# This drives the real slides through reveal.js's ?print-pdf stylesheet, so the
# PDF matches the web version exactly. Requires a Chromium, which decktape
# downloads on first run (~170 MB).
#
# You do not need to run this to publish: the GitHub Action in
# .github/workflows/publish.yml generates the PDF on every push.

set -euo pipefail
cd "$(dirname "$0")"

PORT=8123

command -v quarto >/dev/null || { echo "quarto not found on PATH" >&2; exit 1; }

echo "→ Rendering site…"
quarto render

echo "→ Serving _site on :$PORT…"
python3 -m http.server "$PORT" --directory _site >/dev/null 2>&1 &
SERVER_PID=$!
trap 'kill $SERVER_PID 2>/dev/null || true' EXIT

for _ in $(seq 1 30); do
  curl -sf "http://localhost:$PORT/" >/dev/null && break
  sleep 1
done

# Keep this list in step with .github/workflows/publish.yml.
for name in intro; do
  echo "→ Exporting $name…"
  npx -y decktape reveal \
    --size 1200x750 \
    --slides 1-999 \
    "http://localhost:$PORT/slides/$name.html?print-pdf" \
    "_site/slides/$name.pdf"
done

echo "✓ Done. PDFs are in _site/slides/"
