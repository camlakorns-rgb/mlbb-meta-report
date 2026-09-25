# v24: integrate hmmsucks expert tiers into the engine.
# - HMM data block (133 heroes, lane-keyed, template lane names)
# - hmmVal/hmmDamp/hmmVouched/hmmBestName helpers
# - scoring: expert prior (+/-1.2, 0.9x, patch-dampened), nerfed heroes' stale measured prior x0.6
# - D-tier floor/back-sort/medal-block lifted for expert-vouched heroes (lane-aware)
# - card chips: expert BEST/GREAT (gold), situational (orange), 2.1.95a patch-stale (amber)
# - ban advisor: dampened expert threat term + why note
# - footnote + CSS
import json, re, os

TPL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template.html')
src = open(TPL, encoding='utf-8').read()
orig = src

# ---------- build HMM JS literal ----------
hmm = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'hmmsucks_tiers.json')))
LANEMAP = {'Jungler': 'Jungle', 'EXP': 'EXP', 'Mid': 'Mid', 'Gold': 'Gold', 'Roam': 'Roam'}
REN = {'Popol and Kupa': 'Popol'}  # template/STATS naming
out = {}
for h, lanes in hmm.items():
    h2 = REN.get(h, h)
    assert h2 not in out, 'dupe after rename: ' + h2
    out[h2] = {LANEMAP[k]: v for k, v in lanes.items()}
assert len(out) == 133
# ground-truth spot checks (user-validated extraction) BEFORE writing anything
assert out['Fanny'] == {'Jungle': 'BEST'}, out['Fanny']
assert out['Hanzo'] == {'Jungle': 'GREAT'}, out['Hanzo']
assert out['Lolita'] == {'Roam': 'GOOD'}, out['Lolita']
assert out['Marcel'] == {'Roam': 'BEST'}, out['Marcel']
assert out['Atlas'] == {'Roam': 'BEST'}, out['Atlas']
assert out['Miya'] == {'Gold': 'GREAT'}, out['Miya']
assert out['Grock'] == {'Roam': 'VERYGOOD', 'EXP': 'SOLID'}, out['Grock']
assert out['Gatotkaca'] == {'Roam': 'VERYGOOD', 'EXP': 'SOLID'}, out['Gatotkaca']
# names must all exist in STATS
stats = json.loads(re.search(r'var STATS = (\{.*?\});', src).group(1))
bad = [h for h in out if h not in stats]
assert not bad, 'names not in STATS: %s' % bad

def jsobj(d):
    return '{' + ','.join('"%s":%s' % (k, json.dumps(v, separators=(',', ':'), ensure_ascii=False)) for k, v in d.items()) + '}'

HMM_JS = jsobj(out)

def patch(s, old, new, tag):
    assert s.count(old) == 1, 'anchor not unique/found (%s): %r' % (tag, old[:60])
    return s.replace(old, new)

# ---------- P1: CSS ----------
src = patch(src,
  '.mb.warn{color:var(--danger-hi);}',
  '.mb.warn{color:var(--danger-hi);}\n.mb.hmm{background:rgba(245,196,81,.13);color:#f5c451;}\n.mb.situ{color:#d29a4a;}\n.mb.stale{color:#d29a4a;border-color:#d29a4a55;}',
  'P1 css')

# ---------- P2: data + helpers after the TIERSCORE IIFE ----------
anchor2 = 'var ISLUG = {'
datablock = (
'/* hmmsucks expert tiers (patch 2.1.95, Aug 23 2026) - the community gold-standard tier list, '
'lane by lane, extracted from the published grid via portrait matching (all 133 heroes). '
'Captures the high-elo/competitive read that all-ranks win rates undersell (skill-gated heroes). '
'GOOD = neutral anchor; SOLID/SITUATIONAL = below the expert bar. */\n'
'var HMM = ' + HMM_JS + ';\n'
'var HMM_T = {"BEST":1,"GREAT":0.65,"VERYGOOD":0.3,"GOOD":0,"SOLID":-0.35,"SITUATIONAL":-0.7};\n'
'/* patch 2.1.95a balance changes that postdate the expert list - expert reads on these heroes are stale. '
'(gamemarket listed Hanzo as buffed, but the MLBBHub regen-scaling nerf detail + his post-patch WR drop say nerfed.) */\n'
'var HMM95A = { nerfed:["Atlas","Hanzo","Gord","Aamon","Leomord","Sora","Yu Zhong"], '
'buffed:["Hayabusa","Obsidia","Lukas","Suyou","Miya"] };\n'
'/* expert read for this hero in this lane: lane placement if a lane is in play, else best placement anywhere. '
'No placement for the lane in play = 0 (the off-lane fit penalty handles the rest). */\n'
'function hmmVal(p, lane){\n'
'  var d = HMM[p]; if(!d) return null;\n'
'  if(lane) return d[lane] !== undefined ? HMM_T[d[lane]] : 0;\n'
'  var best = 0; for(var k in d) if(HMM_T[d[k]] > best) best = HMM_T[d[k]];\n'
'  return best;\n'
'}\n'
'/* direction-aware dampening for 2.1.95a-changed heroes: a nerf eats positive expert reads '
'(keep 25%) but makes negative ones MORE credible; a buff does the reverse. */\n'
'function hmmDamp(p, v){\n'
'  if(!v) return 1;\n'
'  if(HMM95A.nerfed.indexOf(p) >= 0) return v > 0 ? 0.25 : 1;\n'
'  if(HMM95A.buffed.indexOf(p) >= 0) return v < 0 ? 0.25 : 1;\n'
'  return 1;\n'
'}\n'
'/* expert vouch = GREAT/BEST in the lane in play (or anywhere if no lane is set) */\n'
'function hmmVouched(p){ return (hmmVal(p, myLaneNow()) || 0) >= 0.65; }\n'
'/* name of the best expert placement (for display) */\n'
'function hmmBestName(p){ var d = HMM[p]; if(!d) return null; var bn = null, bv = -2; '
'for(var k in d) if(HMM_T[d[k]] > bv){ bv = HMM_T[d[k]]; bn = d[k]; } return bn; }\n'
'\n')
src = patch(src, anchor2, datablock + anchor2, 'P2 data')

# ---------- P3a: scoring - stale-nerf shrink + vouch-lifted D floor + expert prior ----------
src = patch(src,
"""      score[p] += Math.max(-1.8, Math.min(1.8, ts * 0.55 * priorScale));
      if(TIER[p] === "D") score[p] -= 1.5; /* measured bottom tier: last resort, never a medal */
    });""",
"""      var nf = HMM95A.nerfed.indexOf(p) >= 0 ? 0.6 : 1; /* our ranked data predates the 2.1.95a nerf - shrink the stale prior */
      score[p] += Math.max(-1.8, Math.min(1.8, ts * 0.55 * priorScale * nf));
      if(TIER[p] === "D" && !hmmVouched(p)) score[p] -= 1.5; /* measured bottom tier: last resort, never a medal - unless the expert list vouches for them in this lane (skill-gated heroes) */
    });
    /* hmmsucks expert prior (patch 2.1.95 lane tiers): the high-elo read, capped so it tilts but
       never overrides measured data; 2.1.95a balance changes dampen it direction-aware */
    Object.keys(score).forEach(function(p){
      var hv = hmmVal(p, myLaneNow());
      if(!hv) return;
      score[p] += Math.max(-1.2, Math.min(1.2, hv * 0.9 * hmmDamp(p, hv)));
    });""",
 'P3a scoring')

# ---------- P3b: dFlag back-sort ----------
src = patch(src,
  'var dFlag = function(p){ return TIER[p]==="D" ? 1 : 0; };',
  'var dFlag = function(p){ return (TIER[p]==="D" && !hmmVouched(p)) ? 1 : 0; }; /* expert-vouched D-tiers compete normally */',
  'P3b dFlag')

# ---------- P3c: medal eligibility ----------
src = patch(src,
  'var mslot = TIER[pick]==="D" ? 99 : show.slice(0, idx).filter(function(x){ return TIER[x]!=="D"; }).length;',
  'var mslot = (TIER[pick]==="D" && !hmmVouched(pick)) ? 99 : show.slice(0, idx).filter(function(x){ return TIER[x]!=="D" && !hmmVouched(x); }).length;',
  'P3c mslot')

# ---------- P4: chips ----------
src = patch(src,
"""          if(TIER[pick]==="D") metaBits.push('<span class="mb warn" title="measured bottom tier this patch (mlbb.io ranked data) — a hard counter on a losing hero still loses games, so it cannot take a medal">📉 weak meta</span>');""",
"""          var _ml = myLaneNow(), _hv = hmmVal(pick, _ml), _hn = _ml && HMM[pick] ? (HMM[pick][_ml] || null) : null;
          if(_hv !== null && _hv >= 0.65) metaBits.push('<span class="mb hmm" title="hmmsucks tier list, patch 2.1.95 (community gold standard for high-elo/competitive reads): ' + (_hn ? _hn + ' in ' + _ml : 'top-tier placement') + (TIER[pick]==="D" ? ' - measured all-ranks D because the hero is skill-gated; the pilot-difficulty flag still applies' : '') + '">★ expert ' + (_hn ? _hn + ' · ' + _ml : 'top pick') + '</span>');
          else if(TIER[pick]==="D") metaBits.push('<span class="mb warn" title="measured bottom tier this patch (mlbb.io ranked data) — a hard counter on a losing hero still loses games, so it cannot take a medal">📉 weak meta</span>');
          if(_hv === HMM_T.SITUATIONAL) metaBits.push('<span class="mb situ" title="hmmsucks tier list, patch 2.1.95: situational' + (_hn ? ' in ' + _ml : ' everywhere') + ' - needs the right draft/game to pay off">⚖ expert: situational</span>');
          if(HMM95A.nerfed.indexOf(pick) >= 0) metaBits.push('<span class="mb stale" title="nerfed in patch 2.1.95a, after the expert list and our measured data were taken - expert reads keep only 25% of their positive weight and the measured prior is shrunk to 60%">⚖ 2.1.95a nerfed</span>');
          else if(HMM95A.buffed.indexOf(pick) >= 0) metaBits.push('<span class="mb stale" title="buffed in patch 2.1.95a, after the expert list was made - any negative expert read is dampened; the buffs are not in the numbers yet">⚖ 2.1.95a buffed</span>');""",
 'P4 chips')

# ---------- P5: ban advisor ----------
src = patch(src,
"""    cands.push({h:H, threat: prey.length*1.5 + (BANW[TIER[H]]||0) - cw + measT*0.45 - mHandled*0.25, prey: prey, countered: countered, mPrey: mPrey, mHandled: mHandled});""",
"""    var _hb = hmmVal(H, null) || 0;
    var _hmmT = _hb > 0 ? _hb * 1.1 * hmmDamp(H, _hb) : 0; /* expert threat (hmmsucks), dampened for 2.1.95a changes */
    cands.push({h:H, threat: prey.length*1.5 + (BANW[TIER[H]]||0) - cw + measT*0.45 - mHandled*0.25 + _hmmT, prey: prey, countered: countered, mPrey: mPrey, mHandled: mHandled, hmm:_hmmT});""",
 'P5 ban threat')
src = patch(src,
"""    if(TIER[c.h] && (TIER[c.h]==="S"||TIER[c.h]==="A") && c.threat>0) why.push(esc(TIER[c.h])+"-tier power pick");""",
"""    if(TIER[c.h] && (TIER[c.h]==="S"||TIER[c.h]==="A") && c.threat>0) why.push(esc(TIER[c.h])+"-tier power pick");
    if(c.hmm > 0.2) why.push("expert " + hmmBestName(c.h) + " (hmmsucks" + ((HMM95A.nerfed.indexOf(c.h) >= 0 || HMM95A.buffed.indexOf(c.h) >= 0) ? ", 2.1.95a-dampened" : "") + ")");""",
 'P5 ban why')

# ---------- P6: footnote ----------
src = patch(src,
'D-tier picks carry a −1.5 last-resort penalty and never take a medal; −1.2 per enemy strong against the pick ⚠️',
'D-tier picks carry a −1.5 last-resort penalty and never take a medal (lifted when the hmmsucks expert list rates the hero GREAT/BEST in your lane — skill-gated picks whose ranked WR punishes average pilots); + hmmsucks expert prior (patch 2.1.95 lane tiers, ±1.2, direction-aware: nerfed-in-2.1.95a heroes keep 25% of a positive expert read, buffed heroes keep their boost); −1.2 per enemy strong against the pick ⚠️',
 'P6 footnote prior')
src = patch(src,
'<b>✅</b> kit-verified, <b>📊</b> measured-only, <b>⚔️</b> kit-backed consensus.',
'<b>✅</b> kit-verified, <b>📊</b> measured-only, <b>⚔️</b> kit-backed consensus, <b>★ expert</b> hmmsucks top-tier read in your lane, <b>⚖ 2.1.95a</b> balance-changed after the expert list.',
 'P6 footnote legend')

# ---------- write ----------
assert src != orig
tmp = TPL + '.new'
open(tmp, 'w', encoding='utf-8').write(src)
os.replace(tmp, TPL)
print('v24 written:', len(src), 'bytes (+%d)' % (len(src) - len(orig)))
for m in ['var HMM =', 'hmmVal', 'hmmDamp', 'hmmVouched', 'hmmBestName', '2.1.95a nerfed', 'expert ']:
    print(' marker %-22s x%d' % (m, src.count(m)))
