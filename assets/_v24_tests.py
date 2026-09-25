# v24 tests: update v19 D-tier invariants to expert-vouch semantics + add v24 block
import re, os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_tests.js')
s = open(P, encoding='utf-8').read()
orig = s

def rep(old, new, tag):
    global s
    assert s.count(old) == 1, 'anchor fail (%s): %r' % (tag, old[:70])
    s = s.replace(old, new)

# 1. "D behind non-D" -> "unvouched D behind medal-eligible"
rep('A("engine v19: D-tier listed only behind non-D picks (vs Melissa)", laylaIdx < 0 || nmz.slice(0, laylaIdx).every(function(h){ return TIER[h] !== "D"; }));',
    'A("engine v24: non-vouched D-tier listed only behind medal-eligible picks (vs Melissa)", laylaIdx < 0 || nmz.slice(0, laylaIdx).every(function(h){ return TIER[h] !== "D" || hmmVouched(h); }));',
    't1')

# 2. medal test: vouched D may medal
rep('  if(h && TIER[h] === "D") medalOk = false;',
    '  if(h && TIER[h] === "D" && !hmmVouched(h)) medalOk = false;',
    't2')

# 3. sweep: unvouched D never podiums; vouched D expected to podium; count chips in same sweep
rep('''var sweepBad = [];
Object.keys(DB).forEach(function(E){
  enemies = [E]; team = []; myPick = null; bans = []; buildView = null; roleFilter = "All"; myLane = null; render();
  var top3 = recNamesAll().slice(0,3);
  if(top3.some(function(h){ return TIER[h] === "D"; })) sweepBad.push(E + ":" + top3.join("/"));
});
A("engine v19: no D-tier on any podium across all " + Object.keys(DB).length + " single-enemy boards", sweepBad.length === 0);''',
'''var sweepBad = [], vouchPodiums = {}, chipExpert = 0, chipSitu = 0, chipStale = 0;
Object.keys(DB).forEach(function(E){
  enemies = [E]; team = []; myPick = null; bans = []; buildView = null; roleFilter = "All"; myLane = null; render();
  var top3 = recNamesAll().slice(0,3);
  var html = _els.cpkResults.innerHTML;
  if(html.indexOf("\\u2605 expert") >= 0) chipExpert++;
  if(html.indexOf("expert: situational") >= 0) chipSitu++;
  if(html.indexOf("2.1.95a") >= 0) chipStale++;
  top3.forEach(function(h){ if(TIER[h] === "D"){ if(hmmVouched(h)) vouchPodiums[h] = (vouchPodiums[h]||0)+1; else sweepBad.push(E + ":" + top3.join("/")); } });
});
A("engine v24: no UNVOUCHED D-tier on any podium across all " + Object.keys(DB).length + " single-enemy boards", sweepBad.length === 0);
A("v24 sweep: expert-vouched D-tiers podium (Fanny/Claude/Harley)", (vouchPodiums["Fanny"]||0) >= 1 && (vouchPodiums["Claude"]||0) >= 1 && (vouchPodiums["Harley"]||0) >= 1);
A("v24 sweep: expert chip renders on boards", chipExpert >= 20);
A("v24 sweep: situational chip renders on boards", chipSitu >= 1);
A("v24 sweep: 2.1.95a patch-stale chip renders on boards", chipStale >= 1);''',
    't3')

# 4. append v24 block before final summary
V24 = '''
// ---------- v24: hmmsucks expert tiers ----------
A("v24 HMM: 133 heroes, all known to the engine", Object.keys(HMM).length === 133 && Object.keys(HMM).every(function(h){ return !!DB[h]; }));
var v24LaneOK = true, v24TierOK = true;
Object.keys(HMM).forEach(function(h){ Object.keys(HMM[h]).forEach(function(l){ if(LANES.indexOf(l) < 0) v24LaneOK = false; if(!(HMM[h][l] in HMM_T)) v24TierOK = false; }); });
A("v24 HMM: lane keys valid (Jungle/EXP/Mid/Gold/Roam)", v24LaneOK);
A("v24 HMM: tier values valid", v24TierOK);
A("v24 HMM: anchors Fanny/Hanzo/Lolita/Marcel/Miya", JSON.stringify(HMM["Fanny"]) === '{"Jungle":"BEST"}' && JSON.stringify(HMM["Hanzo"]) === '{"Jungle":"GREAT"}' && JSON.stringify(HMM["Lolita"]) === '{"Roam":"GOOD"}' && JSON.stringify(HMM["Marcel"]) === '{"Roam":"BEST"}' && JSON.stringify(HMM["Miya"]) === '{"Gold":"GREAT"}');
A("v24 HMM: stone twins flex Roam VERYGOOD + EXP SOLID", JSON.stringify(HMM["Grock"]) === '{"Roam":"VERYGOOD","EXP":"SOLID"}' && JSON.stringify(HMM["Gatotkaca"]) === '{"Roam":"VERYGOOD","EXP":"SOLID"}');
A("v24 HMM95A: lists valid + disjoint", HMM95A.nerfed.every(function(h){ return !!DB[h]; }) && HMM95A.buffed.every(function(h){ return !!DB[h]; }) && HMM95A.nerfed.every(function(h){ return HMM95A.buffed.indexOf(h) < 0; }));
A("v24 hmmVal: lane staked / missing lane / no lane / neutral", hmmVal("Fanny","Jungle") === 1 && hmmVal("Fanny","Mid") === 0 && hmmVal("Fanny",null) === 1 && hmmVal("Lolita",null) === 0 && hmmVal("Lolita","Roam") === 0 && hmmVal("Grock",null) === 0.3 && hmmVal("Miya","Gold") === 0.65);
A("v24 hmmVal: Aldous demoted everywhere (best -0.7)", hmmVal("Aldous",null) === -0.7 && hmmBestName("Aldous") === "SITUATIONAL");
A("v24 hmmDamp: nerfed positive x0.25, buffed positive full", hmmDamp("Hanzo",0.65) === 0.25 && hmmDamp("Atlas",1) === 0.25 && hmmDamp("Miya",0.65) === 1 && hmmDamp("Lukas",0.65) === 1);
A("v24 hmmDamp: nerfed negative full, buffed negative x0.25, others 1", hmmDamp("Leomord",-0.35) === 1 && hmmDamp("Suyou",-0.35) === 0.25 && hmmDamp("Layla",1) === 1 && hmmDamp("Hanzo",0) === 1);
A("v24 vouch: lane-aware (Fanny Jungle yes / Mid no; Selena fallback yes; Layla never)", (function(){ myLane = "Jungle"; var a = hmmVouched("Fanny"); myLane = "Mid"; var b = !hmmVouched("Fanny"); myLane = "Gold"; var c = hmmVouched("Claude"); myLane = null; return a && b && c && hmmVouched("Selena") && !hmmVouched("Layla"); })());
enemies = ["Clint"]; team = []; myPick = null; bans = []; buildView = null; roleFilter = "All"; myLane = "Jungle"; pickOrder = "mid"; render();
A("v24 board: expert-vouched Fanny podiums vs Clint (Jungle)", recNamesAll().slice(0,3).indexOf("Fanny") >= 0);
var v24FannyCard = (function(){ var segs = _els.cpkResults.innerHTML.split('<div class="rec '); for(var i = 1; i < segs.length; i++){ if(segs[i].indexOf('data-h="Fanny"') >= 0) return segs[i]; } return ""; })();
A("v24 board: Fanny card shows lane expert chip, no weak-meta", v24FannyCard.indexOf("\\u2605 expert BEST \\u00b7 Jungle") >= 0 && v24FannyCard.indexOf("weak meta") < 0);
A("v24 board: vouched D-tier may take a medal", /^(m1|m2|m3)">/.test(v24FannyCard));
myLane = null; render();
A("v24 board: no-lane fallback chip on Fanny card", (function(){ var segs = _els.cpkResults.innerHTML.split('<div class="rec '); for(var i = 1; i < segs.length; i++){ if(segs[i].indexOf('data-h="Fanny"') >= 0) return segs[i].indexOf("\\u2605 expert top pick") >= 0; } return false; })());
enemies = []; team = []; myPick = null; bans = []; buildView = null; roleFilter = "All"; myLane = null; render();
A("v24 bans: expert note rendered in ban advisor", _els.cpkResults.innerHTML.indexOf("(hmmsucks") >= 0);
A("v24 footnote: mentions hmmsucks prior + dampening", document.body.innerHTML.indexOf("hmmsucks expert prior") >= 0 && document.body.innerHTML.indexOf("direction-aware") >= 0);

'''
rep('if(FAIL > 0){ console.log("failed: " + FAILED.join(" | ")); process.exitCode = 1; }',
    V24 + 'if(FAIL > 0){ console.log("failed: " + FAILED.join(" | ")); process.exitCode = 1; }',
    't4')

assert s != orig
open(P, 'w', encoding='utf-8').write(s)
print('tests patched, lines:', s.count('\\n'))
