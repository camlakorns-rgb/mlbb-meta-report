# MLBB Meta Report — August 2026

A single-file, self-contained **Mobile Legends: Bang Bang** meta report with a
live draft-helper engine. Every image is inlined as a WebP data-URI, so
`index.html` works offline with zero network requests.

## Sections

| # | Section | Notes |
|---|---------|-------|
| 01 | **Draft Helper** | Live tool — bans, counters & builds |
| 02 | TL;DR — The 10 Heroes Defining the Meta | |
| 03 | While You Were Away | patch deltas |
| 04 | Tier Lists by Role | Jungle / EXP / Mid / Gold / Roam |
| 05 | The Builds | 17 meta heroes |
| 06 | Emblem Cheat Sheet | |
| 07 | Situational Item Swaps | |
| 08 | What to Ban | live ban rates |
| 09 | Sources & Method | |

## Layout

```
index.html                     shipped artifact (generated — do not hand-edit)
MLBB-Meta-Report-August-2026.md  the report in prose/markdown form
hmmsucks_tiers.json            expert tier data (lane → VERYGOOD/GREAT/GOOD/SOLID/SITUATIONAL)
hmmsucks_extracted.html        raw scrape those tiers came from
test.sh                        engine test runner
assets/
  template.html                ← SOURCE OF TRUTH (HTML + CSS + engine JS)
  assemble.py                  build: template + images → index.html
  _stubs.js                    DOM shim for running the engine under node
  _tests.js                    224 engine assertions
  _split.py                    legacy extract-the-<script>-body helper
  _kits.json _meas.json _meas_matrix.json _myb.json _skills_raw.json
                               hero data (kits, mlbb.io matchups, builds, skills)
  _gen_myb.py                  generates _myb.json
  _v20_js.py … _v25.py         historical version patchers (changelog-in-code)
  heroes/ heroes_extra/ items/ emblems/ spells/ talents/ banner.jpg
                               image inputs (1.94 MB) — required by the build
artifacts/                     dev-only: QA screenshots, superseded sources (gitignored)
```

## Build

Requires Python 3 + Pillow, and node for tests.

```bash
python3 -m venv .venv && ./.venv/bin/pip install Pillow   # once

./.venv/bin/python assets/assemble.py            # → index.html
./.venv/bin/python assets/assemble.py /tmp/x.html  # → alternate destination
```

`assemble.py` resizes each image to its largest displayed size (retina 2×),
re-encodes to WebP, and emits one CSS class per icon at the `/*__IMAGES__*/`
marker inside `template.html`. Already-WebP inputs are embedded byte-for-byte
without re-encoding. It finishes by cross-checking every `h-`/`i-`/`e-`/`s-`
class token referenced by the markup and JS against the classes it defined, and
exits non-zero if anything is missing.

## Test

```bash
./test.sh        # → "==== 224 passed, 0 failed ===="
```

The runner extracts the `<script>` body from `template.html`, strips its IIFE
wrapper so tests can reach engine internals, concatenates `_stubs.js` + body +
`_tests.js`, and executes under node.

## Editing the engine

Work in `assets/template.html`, never in `index.html` — the latter is a build
product and will be overwritten. The `assets/_v*.py` scripts are the historical
record of how each version's engine changes were applied; they are kept as
reference and are no longer re-run as part of the build.
