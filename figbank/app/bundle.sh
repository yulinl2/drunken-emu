#!/usr/bin/env bash
# figbank/app/bundle.sh — build one page app into a single self-contained HTML shell.
#
#   bash figbank/app/bundle.sh figbank/app/variable-model [OUT.html]
#
# Same mechanics as the web-artifacts-builder skill's bundle-artifact.sh (Parcel, then html-inline), with two
# differences: the bundling dependencies are installed once into the app (not on every run), and the output path is
# an argument so a consumer (MetaProof `make page`) can put the shell where its own generator reads it. The shell
# keeps the `<script id="vars" type="application/json">__JSON__</script>` data slot verbatim; the consumer fills it.
set -euo pipefail
APP="${1:?app directory}"; OUT="${2:-$APP/bundle.html}"
cd "$APP"
[ -f package.json ] && [ -f index.html ] || { echo "not an app dir: $APP" >&2; exit 64; }
command -v pnpm >/dev/null || npm install -g pnpm >/dev/null
[ -d node_modules ] || pnpm install --silent
if ! pnpm exec parcel --version >/dev/null 2>&1; then
  pnpm add -D --silent parcel @parcel/config-default parcel-resolver-tspaths html-inline
fi
[ -f .parcelrc ] || cat > .parcelrc <<'EOF'
{ "extends": "@parcel/config-default", "resolvers": ["parcel-resolver-tspaths", "..."] }
EOF
pnpm exec tsc -b
rm -rf dist .parcel-cache
pnpm exec parcel build index.html --dist-dir dist --no-source-maps --no-cache >/dev/null
pnpm exec html-inline dist/index.html > "$OUT"
grep -q '__JSON__' "$OUT" || { echo "bundle lost the __JSON__ data slot" >&2; exit 1; }
echo "shell: $OUT ($(du -h "$OUT" | cut -f1))"
