# MLBB Meta Report

Single-file static site: `index.html` (deployed via GitHub Pages).

## Updating the meta data (draft engine)

The draft engine's measured layers come from [mlbbhub.com](https://mlbbhub.com) hero pages
(ranked matchup stats, `advantagePp` counter edges, lane assignments, tier letters).

```bash
# 1. crawl all 133 hero pages (~90 MB, goes to /tmp/mlbbhub-crawl)
python3 tools/refresh_data.py --crawl

# 2. parse + rebuild data layers inside index.html
#    (also writes a dated snapshot to data/meta-YYYY-MM-DD.json)
python3 tools/refresh_data.py --write-html
```

What gets refreshed: `STATS` (WR/pick/ban), `MEAS` (measured counter edges),
`ROLE` (role · lanes, primary lane first), `TIERHUB` (hub tier letters),
`POP` (top-30 by pick rate), `DB` (counter lists + measured "don't pick" lists —
curated reasons and tips from previous versions are reused when a matchup persists).

What is kept (editorial, refresh manually if needed): `KITS`, `MYB` (curated builds),
`TAL`/`TSLUG` (emblems/talents), `SYN` (measured duo WR), `HMM` (hmmsucks expert tiers),
difficulty/comfort lists.

After refreshing, update the visible date/patch strings via
`TEXT_REPLACEMENTS` in `tools/refresh_data.py` (add a new pair for the new patch date).

## Notes

- Data snapshot JSONs live in `data/` (the crawl itself is disposable).
- Counter-pick weights: 3 = measured edge ≥ +2.5 pp, 2 = ≥ +1.8 pp, 1 = smaller.
- `TIER`/`TIERSCORE` are computed at runtime from `STATS`
  (`(WR−50)·pick/(pick+2) + ban·0.02`, cut at ranks 8/24/54/109 → S/A/B/C/D).
