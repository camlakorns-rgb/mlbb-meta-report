#!/usr/bin/env bash
# Run the draft-helper engine test suite against assets/template.html.
#
# The template's <script> body is extracted, unwrapped from its IIFE (so the
# tests can reach engine internals), then concatenated with a DOM shim and the
# assertion suite and executed under node.
#
# Usage: ./test.sh
set -euo pipefail
cd "$(dirname "$0")"

BUILD="${BUILD_DIR:-build}"
mkdir -p "$BUILD"

python3 - "$BUILD" <<'PY'
import os, sys
build = sys.argv[1]
src = open(os.path.join('assets', 'template.html'), encoding='utf-8').read()
i = src.find('<script>'); j = src.find('</script>', i)
assert i > 0 and j > i, 'no <script> block found in template.html'
body = src[i + 8:j]
# strip the engine IIFE wrapper so tests can reach engine vars
o = body.find('(function(){')
assert o > 0, 'IIFE opener not found'
body = body[o + len('(function(){'):].rstrip()
assert body.endswith('})();'), 'IIFE closer not at end'
body = body[:-5]
out = os.path.join(build, 'body.js')
open(out, 'w', encoding='utf-8').write(body)
print('body.js bytes:', len(body))
PY

cat assets/_stubs.js "$BUILD/body.js" assets/_tests.js > "$BUILD/run_tests.js"
node "$BUILD/run_tests.js"
