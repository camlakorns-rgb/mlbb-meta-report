# v25: counter-system quality rebalance (user feedback: recommendations "not good vs mlbb.io")
# 1. measured edges (mlbb.io) weighted 1.35x - real matchup data leads the board
# 2. meta prior 0.55x -> 0.40x - hero quality matters but can't beat a big real edge
# 3. measured-counter parole: D-tier with >=+3.5pp measured edge vs a board enemy
#    (and ts >= -1.2, i.e. not a ranked feeder) gets floor -0.5 + normal sort + medal eligibility
# 4. fix v24 duplicate-medal bug (vouched-D ahead didn't consume a medal slot)
# 5. fix 11 dropped "Popol and Kupa" measured edges (name mismatch)
# 6. card vs-badges + top reasoning sorted measured-first
# 7. footnote update
import json, re, os

TPL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template.html')
src = open(TPL, encoding='utf-8').read()
orig = src

def patch(s, old, new, tag):
    assert s.count(old) == 1, 'anchor not unique/found (%s): %r' % (tag, old[:70])
    return s.replace(old, new)

# ---------- P2: measParole helper after hmmBestName ----------
anchor = "/* name of the best expert placement (for display) */"
helper = (
"/* measured-counter parole: a bottom-tier hero with a STRONG measured edge (+3.5pp+) vs an enemy\n"
"   on this board - and whose overall tier score isn't catastrophic - competes nearly normally.\n"
"   The matchup data earned it; this is how mlbb.io's own counter lists behave. */\n"
"function measParole(p){\n"
"  if(TIERSCORE[p] && TIERSCORE[p].v < -1.2) return false;\n"
"  for(var i = 0; i < enemies.length; i++){\n"
"    var e = measEdge(p, enemies[i]);\n"
"    if(e !== null && e >= 3.5) return true;\n"
"  }\n"
"  return false;\n"
"}\n")
src = patch(src, anchor, helper + anchor, 'P2 parole')

# ---------- P3: measured edge weight 1.35x (DB loop) ----------
src = patch(src,
"        if(mp !== null){ pts += Math.min(mp, 2.5) * edgeScale; measCnt[pick] = (measCnt[pick]||0)+1; }",
"        if(mp !== null){ pts += Math.min(mp, 2.5) * edgeScale * 1.35; measCnt[pick] = (measCnt[pick]||0)+1; } /* measured edges (mlbb.io) are the strongest signal - weighted up */",
'P3 dbloop')

# ---------- P4: measured edge weight 1.35x (MEAS loop) ----------
src = patch(src,
"        score[pick] += Math.min(eff, 2.5) * lf * edgeScale;",
"        score[pick] += Math.min(eff, 2.5) * lf * edgeScale * 1.35;",
'P4 measloop')

# ---------- P5: prior 0.55 -> 0.40 ----------
src = patch(src,
"      score[p] += Math.max(-1.8, Math.min(1.8, ts * 0.55 * priorScale * nf));",
"      score[p] += Math.max(-1.8, Math.min(1.8, ts * 0.40 * priorScale * nf)); /* hero quality matters, but a big real edge beats it */",
'P5 prior')

# ---------- P6: D-floor with parole ----------
src = patch(src,
'      if(TIER[p] === "D" && !hmmVouched(p)) score[p] -= 1.5; /* measured bottom tier: last resort, never a medal - unless the expert list vouches for them in this lane (skill-gated heroes) */',
'      if(TIER[p] === "D" && !hmmVouched(p)) score[p] -= (measParole(p) ? 0.5 : 1.5); /* measured bottom tier: last resort - unless expert-vouched in this lane, or paroled by a strong measured counter edge */',
'P6 dfloor')

# ---------- P7: dFlag ----------
src = patch(src,
'    var dFlag = function(p){ return (TIER[p]==="D" && !hmmVouched(p)) ? 1 : 0; }; /* expert-vouched D-tiers compete normally */',
'    var dFlag = function(p){ return (TIER[p]==="D" && !hmmVouched(p) && !measParole(p)) ? 1 : 0; }; /* expert-vouched or measured-paroled D-tiers compete normally */',
'P7 dflag')

# ---------- P8: mslot - medal eligibility + duplicate-medal fix ----------
src = patch(src,
'          var mslot = (TIER[pick]==="D" && !hmmVouched(pick)) ? 99 : show.slice(0, idx).filter(function(x){ return TIER[x]!=="D" && !hmmVouched(x); }).length;',
'          var mslot = (TIER[pick]==="D" && !hmmVouched(pick) && !measParole(pick)) ? 99 : show.slice(0, idx).filter(function(x){ return TIER[x]!=="D" || hmmVouched(x) || measParole(x); }).length; /* medal slots consumed by every medal-eligible pick ahead */',
'P8 mslot')

# ---------- P9: measured-first badges ----------
src = patch(src,
'          var vs = reasons[pick].map(function(r){',
'          var rs = reasons[pick].slice().sort(function(a,b){ return (b.pp===undefined?-99:b.pp) - (a.pp===undefined?-99:a.pp); }); /* measured evidence leads */\n          var vs = rs.map(function(r){',
'P9 vs')
src = patch(src,
'          var topWhy = reasons[pick].slice(0,2).map(function(r){return "vs "+r.vs+": "+r.why;}).join(" · ");',
'          var topWhy = rs.slice(0,2).map(function(r){return "vs "+r.vs+": "+r.why;}).join(" · ");',
'P9 topwhy')

# ---------- P10: footnote ----------
src = patch(src,
'measured win-rate edges (mlbb.io ranked data, Aug 2026, <b>shrunk by sample size</b>) + confidence-weighted',
'measured win-rate edges (mlbb.io ranked data, Aug 2026, <b>shrunk by sample size, weighted 1.35×</b> — real matchup data leads the board) + confidence-weighted',
'P10 fn1')
src = patch(src,
'measured meta-strength prior (0.55× tier score, ±1.8 — strong enough that counter edges cannot carry a weak hero)',
'measured meta-strength prior (0.40× tier score, ±1.8 — hero quality matters, but a big real edge beats it)',
'P10 fn2')
src = patch(src,
'D-tier picks carry a −1.5 last-resort penalty and never take a medal (lifted when the hmmsucks expert list rates the hero GREAT/BEST in your lane — skill-gated picks whose ranked WR punishes average pilots)',
'D-tier picks carry a −1.5 last-resort penalty and never take a medal — lifted for expert-vouched heroes (hmmsucks GREAT/BEST in your lane) and reduced to −0.5 by measured-counter parole (a +3.5pp+ measured edge vs an enemy on this board, on a hero that isn\'t a ranked feeder — that\'s mlbb.io\'s own counter logic showing through)',
'P10 fn3')

assert src != orig
tmp = TPL + '.new'
open(tmp, 'w', encoding='utf-8').write(src)
os.replace(tmp, TPL)
print('v25 written:', len(src), 'bytes (+%d)' % (len(src) - len(orig)))
for mk in ['measParole', '1.35', 'ts * 0.40', 'measured evidence leads']:
    print(' marker %-26s x%d' % (mk, src.count(mk)))
