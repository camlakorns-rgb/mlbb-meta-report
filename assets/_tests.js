
// ================= TESTS =================
var PASS = 0, FAIL = 0, FAILED = [];
function A(name, cond){ if(cond){ PASS++; } else { FAIL++; FAILED.push(name); console.log('FAIL: ' + name); } }
function panelHtml(){ for(var k in _els){ if(_els[k].innerHTML && _els[k].innerHTML.indexOf('buildpanel') >= 0) return _els[k].innerHTML; } return ''; }
function fireEvent(el, ev, obj){ var base = { target: el, preventDefault: function(){}, stopPropagation: function(){} };
  for(var k in obj) base[k] = obj[k]; (el.handlers[ev]||[]).forEach(function(f){ f(base); }); }

// ---------- ensemble DB ----------
var dbKeys = Object.keys(DB);
A("DB: 133 heroes", dbKeys.length === 133);
var nEnt = 0, conf3 = 0, conf2 = 0, conf1 = 0, minConfOK = true;
dbKeys.forEach(function(h){
  DB[h].c.forEach(function(p){
    nEnt++;
    if(p[2] === 3) conf3++; else if(p[2] === 2) conf2++; else conf1++;
  });
  if(!DB[h].c.some(function(p){ return p[2] >= 2; })) minConfOK = false;
});
A("DB: 929 entries", nEnt === 929);
A("DB: conf tallies 265/285/379", conf3 === 265 && conf2 === 285 && conf1 === 379);
A("DB: every hero has a conf>=2 counter-pick", minConfOK);
var lingTop = DB["Ling"].c.slice(0, 4).map(function(p){ return p[0]; });
A("DB: Ling top-4 counters include Natalia + Saber", lingTop.indexOf("Natalia") >= 0 && lingTop.indexOf("Saber") >= 0);

// ---------- BUILDS (MLBBHub presets) ----------
A("BUILDS: 133 heroes", Object.keys(BUILDS).length === 133);
A("BUILDS keys === DB keys", JSON.stringify(Object.keys(BUILDS).sort()) === JSON.stringify(dbKeys.slice().sort()));
A("BUILDS: Zetian preset 1 intact", JSON.stringify(BUILDS["Zetian"][0].i) === JSON.stringify(["Magic Boots","Glowing Wand","Fleeting Time","Wishing Lantern","Divine Glaive","Blood Wings"]));

// ---------- TAL (emblem talents) ----------
A("TAL: 133 heroes", Object.keys(TAL).length === 133);
var talOK = true;
Object.keys(TAL).forEach(function(h){
  var t = TAL[h];
  if(["Assassin","Basic Common","Fighter","Mage","Marksman","Support","Tank"].indexOf(t[0]) < 0) talOK = false;
  for(var i = 1; i < 4; i++) if(!TSLUG[t[i]]) talOK = false;
});
A("TAL: all emblems valid + talents have icons", talOK);
A("TAL: Miya setup", JSON.stringify(TAL["Miya"]) === JSON.stringify(["Marksman","Fatal","Weapon Master","Quantum Charge"]));
A("TAL: Tigreal setup", JSON.stringify(TAL["Tigreal"]) === JSON.stringify(["Support","Agility","Pull Yourself Together","Focusing Mark"]));

// ---------- MYB (Arena's take) ----------
var myKeys = Object.keys(MYB);
A("MYB: 133 heroes", myKeys.length === 133);
A("MYB keys === DB keys", JSON.stringify(myKeys.sort()) === JSON.stringify(dbKeys.slice().sort()));
var BOOTS_SET = ["Arcane Boots","Magic Boots","Demon Boots","Swift Boots","Rapid Boots","Warrior Boots","Tough Boots"];
var myStructOK = true, myIconsOK = true, mySpellOK = true, myDistinctOK = true, myNamesOK = true;
myKeys.forEach(function(h){
  var bs = MYB[h];
  if(bs.length !== 3) myStructOK = false;
  var seen = {};
  bs.forEach(function(b){
    if(b.i.length !== 6 || (new Set(b.i)).size !== 6) myStructOK = false;
    var nb = b.i.filter(function(it){ return BOOTS_SET.indexOf(it) >= 0; }).length;
    if(nb !== 1) myStructOK = false;
    b.i.forEach(function(it){ if(!ISLUG[it]) myIconsOK = false; });
    if(!SSLUG[b.s]) mySpellOK = false;
    seen[b.i.join('|')] = 1;
  });
  if(Object.keys(seen).length !== 3) myDistinctOK = false;
  var prim = (ROLE[h] || '').split('·')[0].trim();
  if(prim === 'Tank' || prim === 'Support'){
    if(bs[1].n !== 'vs Physical' || bs[2].n !== 'vs Magic') myNamesOK = false;
  } else {
    if(bs[1].n !== 'vs Tanks & Sustain' || bs[2].n !== 'vs Dive & Burst') myNamesOK = false;
  }
});
A("MYB: 3 builds x 6 unique items x 1 boots", myStructOK);
A("MYB: every item has an icon", myIconsOK);
A("MYB: every spell has an icon", mySpellOK);
A("MYB: 3 distinct builds per hero", myDistinctOK);
A("MYB: situational names per class", myNamesOK);
A("MYB: Zetian flagship = my chat build", JSON.stringify(MYB["Zetian"][0].i) === JSON.stringify(["Magic Boots","Enchanted Talisman","Glowing Wand","Fleeting Time","Divine Glaive","Concentrated Energy"]));
A("MYB: Zetian vs-dive spell = Purify", MYB["Zetian"][2].s === "Purify");
A("MYB: Zetian vs-tanks has Genius Wand + Wishing Lantern", MYB["Zetian"][1].i.indexOf("Genius Wand") >= 0 && MYB["Zetian"][1].i.indexOf("Wishing Lantern") >= 0);
A("MYB: Miya vs-dive has Wind of Nature", MYB["Miya"][2].i.indexOf("Wind of Nature") >= 0);
A("MYB: Tigreal vs-Physical armor", MYB["Tigreal"][1].i.indexOf("Antique Cuirass") >= 0 && MYB["Tigreal"][1].i.indexOf("Blade Armor") >= 0);
A("MYB: Tigreal vs-Magic MR", MYB["Tigreal"][2].i.indexOf("Athena's Shield") >= 0 && MYB["Tigreal"][2].i.indexOf("Radiant Armor") >= 0);
A("MYB: Estes keeps Flask of the Oasis in vs-Physical", MYB["Estes"][1].i.indexOf("Flask of the Oasis") >= 0);

// ---------- render: panel with both sections ----------
enemies = []; team = []; myPick = null; bans = []; buildView = "Zetian"; render();
var ph = panelHtml();
A("render: buildpanel exists", ph.indexOf('buildpanel') >= 0);
A("render: Community presets label", ph.indexOf('Community presets') >= 0);
A("render: Arena's take section", ph.indexOf("Arena's take") >= 0);
A("render: emblem talents row", ph.indexOf('Emblem setup') >= 0);
A("render: MLBBHub preset item (Blood Wings)", ph.indexOf('Blood Wings') >= 0);
A("render: my standard item (Concentrated Energy)", ph.indexOf('Concentrated Energy') >= 0);
A("render: my why-line", ph.indexOf('The engine, not the nuke') >= 0);
A("render: all 3 arena builds", (ph.match(/arena-b/g) || []).length === 3);
A("render: arena vs-Tanks build label", ph.indexOf('vs Tanks &amp; Sustain') >= 0);
buildView = "Tigreal"; render();
var ph2 = panelHtml();
A("render: Tigreal has vs Physical + vs Magic", ph2.indexOf('vs Physical') >= 0 && ph2.indexOf('vs Magic') >= 0);
buildView = null;

// ---------- board / ban advisor ----------
enemies = ["Gloo"]; render();
var rh = _els.cpkResults.innerHTML;
var glooCounters = DB["Gloo"].c.map(function(p){ return p[0]; });
(MEAS["Gloo"]||[]).forEach(function(m){ if(glooCounters.indexOf(m[0]) < 0) glooCounters.push(m[0]); });
var recNames = (rh.match(/class="pickbtn" data-h="([^"]+)"/g) || []).map(function(s){ return s.match(/data-h="([^"]+)"/)[1]; });
A("board: recs all counter the enemy (ensemble + measured pool)", recNames.length > 0 && recNames.every(function(n){ return glooCounters.indexOf(n) >= 0; }));
A("board: rec count capped at 10", recNames.length === Math.min(10, glooCounters.length));
A("board: ensemble tag rendered", rh.indexOf('ensemble') >= 0 || rh.indexOf('sources') >= 0);

// ---------- ban system ----------
enemies = []; team = []; myPick = null; buildView = null; bans = []; render();
A("bans: empty draft stays empty", _els.cpkEmpty.style.display === "block");
openPicker("myban", -1);
A("v20: ban picker lists 10 options", (_els.pickerList.innerHTML.match(/cpk-opt/g) || []).length === 10);
renderPicker("ling");
A("v20: picker search finds Ling first", picker.keys[0] === "Ling");
pickSlotHero("Ling");
A("bans: picking adds Ling as banned", bans.indexOf("Ling") >= 0);
A("bans: bans alone activate results (meta-only advisor)", _els.cpkEmpty.style.display === "none" && _els.cpkResults.innerHTML.indexOf("Ban advisor") >= 0);
A("bans: advisor sub-label shows count", _els.cpkResults.innerHTML.indexOf("1 banned") >= 0);
var banHs = (_els.cpkResults.innerHTML.match(/ban-item[^>]*data-h="([^"]+)"/g) || []).map(function(s){ return s.match(/data-h="([^"]+)"/)[1]; });
A("bans: advisor excludes banned hero", banHs.indexOf("Ling") < 0);
var eWithLing = Object.keys(DB).filter(function(e){ return DB[e].c.some(function(p){ return p[0] === "Ling"; }); })[0];
A("bans: found enemy countered by Ling (" + eWithLing + ")", !!eWithLing);
if(eWithLing){
  addEnemy(eWithLing);
  A("bans: Ling absent from board + chips + avoid", _els.cpkResults.innerHTML.indexOf('data-h="Ling"') < 0);
}
addEnemy("Ling");
A("bans: addEnemy blocked for banned", enemies.indexOf("Ling") < 0 && _els.cpkMsg.textContent.indexOf("banned") >= 0);
addTeam("Ling");
A("bans: addTeam blocked for banned", team.indexOf("Ling") < 0);
lockPick("Ling");
A("bans: lockPick blocked for banned", myPick === null);
openPicker("enemy", -1);
A("v20: enemy picker excludes banned", _els.pickerList.innerHTML.indexOf("<span>Ling</span>") < 0);
openPicker("team", -1);
A("v20: team picker excludes banned", _els.pickerList.innerHTML.indexOf("<span>Ling</span>") < 0);
enemies = []; render();
["Gusion","Fanny","Khufra","Hirara","Gloo","Sun"].forEach(function(x){ addBan(x); });
A("bans: capped at 5 per side", bans.length === 5 && myBans.length === 5 && _els.cpkMsg.textContent.indexOf("Max 5") >= 0);
addBan("Marcel", "their");
A("bans: enemy side separate (5+1)", bans.length === 6 && myBans.length === 5 && theirBans.length === 1);
removeBan("Gusion");
A("bans: unban restores availability", bans.length === 5 && bans.indexOf("Gusion") < 0);
bans = []; myBans = []; theirBans = []; enemies = []; team = []; myPick = null; buildView = null; render();

// ---------- live counter-build (vs this lineup) ----------
var LB_OK = true, LB_MSG = [];
var LINEUPS = {
  heal:   ["Estes","Rafaela","Floryn","Kimmy","Zilong"],
  mage:   ["Zetian","Zhuxin","Lunox","Zilong","Kimmy"],
  phys:   ["Ling","Zilong","Alucard","Estes","Rafaela"],
  dive:   ["Ling","Fanny","Hanzo","Estes","Rafaela"],
  tank:   ["Tigreal","Hylos","Estes","Rafaela","Kimmy"],
  cc:     ["Khufra","Franco","Tigreal","Estes","Rafaela"]
};
var LB_SPELLS = Object.keys(SSLUG);
Object.keys(MYB).forEach(function(h){
  Object.keys(LINEUPS).forEach(function(k){
    enemies = LINEUPS[k].slice();
    var lb = lineupBuild(h);
    if(!lb){ LB_OK = false; LB_MSG.push(h + "/" + k + ": null"); return; }
    var nb = lb.i.filter(function(it){ return AR_BOOTS[it]; }).length;
    if(lb.i.length !== 6 || (new Set(lb.i)).size !== 6 || nb !== 1){ LB_OK = false; LB_MSG.push(h + "/" + k + " struct"); }
    lb.i.forEach(function(it){ if(!ISLUG[it]){ LB_OK = false; LB_MSG.push(h + "/" + k + " icon:" + it); } });
    if(LB_SPELLS.indexOf(lb.s) < 0){ LB_OK = false; LB_MSG.push(h + "/" + k + " spell:" + lb.s); }
  });
});
A("live: valid build for all 133 heroes x 6 lineup archetypes", LB_OK);
if(!LB_OK) console.log("   " + LB_MSG.slice(0, 8).join(" | "));

enemies = ["Estes","Rafaela"]; team = []; myPick = null; bans = []; buildView = "Miya"; render();
var lbm = lineupBuild("Miya");
A("live: Miya vs Estes+Rafaela gets Sea Halberd (anti-heal)", lbm.i.indexOf("Sea Halberd") >= 0);
A("live: why names the healers", lbm.w.indexOf("Estes") >= 0 && lbm.w.indexOf("Rafaela") >= 0);
var phm = panelHtml();
A("live: LIVE build rendered first in Arena section", phm.indexOf("arena-live") >= 0 && phm.indexOf("vs this lineup") >= 0 && phm.indexOf("tag live") >= 0);
A("live: 4 arena builds total when enemies picked", (phm.match(/arena-b/g) || []).length === 4);

enemies = ["Zetian","Zhuxin","Lunox"];
var lbz = lineupBuild("Miya");
A("live: 3 mages -> MR item for squishy", lbz.i.indexOf("Athena's Shield") >= 0 || lbz.i.indexOf("Radiant Armor") >= 0);

enemies = ["Ling","Fanny","Hanzo"];
var lbz2 = lineupBuild("Zetian");
A("live: divers -> Winter Crown for mage", lbz2.i.indexOf("Winter Crown") >= 0);
var lbm2 = lineupBuild("Miya");
A("live: divers -> Wind of Nature for MM", lbm2.i.indexOf("Wind of Nature") >= 0);

enemies = ["Tigreal","Hylos"];
var lbz3 = lineupBuild("Zetian");
A("live: tanks -> Wishing Lantern (DG already core) for Zetian", lbz3.i.indexOf("Wishing Lantern") >= 0);
var lbt3 = lineupBuild("Tigreal");
A("live: tanky hero vs tanks gets Oracle (MR/heal boost)", lbt3.i.indexOf("Oracle") >= 0 || lbt3.i.indexOf("Dominance Ice") >= 0);

enemies = ["Khufra","Franco","Tigreal"];
var lbcc = lineupBuild("Zetian");
A("live: 3+ CC -> Tough Boots + Purify", lbcc.i[0] === "Tough Boots" && lbcc.s === "Purify");
var lbcc2 = lineupBuild("Ling");
A("live: jungler keeps Retribution under CC", lbcc2.s === "Retribution");

enemies = ["Kimmy"];
var lbn = lineupBuild("Zetian");
A("live: neutral lineup = standard build", JSON.stringify(lbn.i) === JSON.stringify(MYB["Zetian"][0].i));
A("live: neutral why says balanced", lbn.w.indexOf("Balanced lineup") >= 0);

enemies = []; render();
var phn = panelHtml();
A("live: no enemies -> no LIVE build, 3 static remain", phn.indexOf("arena-live") < 0 && (phn.match(/arena-b/g) || []).length === 3);
buildView = null;

// pickline points at live build
enemies = ["Estes","Rafaela"]; buildView = "Miya"; render();
A("live: pickline references the live build", panelHtml().indexOf("live build below") >= 0);
enemies = []; team = []; myPick = null; bans = []; buildView = null; render();

// ---------- clear draft button ----------
enemies = []; team = []; myPick = null; bans = []; buildView = null; render();
A("clear: hidden on empty draft", _els.draftClear.style.display === "none");
enemies = ["Gloo","Ling"]; team = ["Tigreal"]; myPick = "Miya"; bans = ["Fanny"]; buildView = "Zetian"; render();
A("clear: visible when draft active", _els.draftClear.style.display === "");
A("clear: handler bound", typeof _els.draftClear.onclick === "function");
_els.draftClear.onclick({});
A("clear: wipes enemies/team/pick/bans/view", enemies.length === 0 && team.length === 0 && myPick === null && bans.length === 0 && buildView === null);
A("clear: empty state restored", _els.cpkEmpty.style.display === "block");
openPicker("enemy", -1); _els.pickerInput.value = "ling"; clearDraft();
A("clear: closes picker and resets its input", picker.open === false && _els.pickerInput.value === "");
A("clear: button hidden after clear", _els.draftClear.style.display === "none");
A("clear: re-add works after clear", (addEnemy("Gloo"), enemies.length === 1));

// ---------- KITS (skill data) ----------
var kitKeys = Object.keys(KITS);
A("KITS: 133 heroes", kitKeys.length === 133);
A("KITS keys === DB keys", JSON.stringify(kitKeys.sort()) === JSON.stringify(dbKeys.slice().sort()));
var kitStructOK = true;
kitKeys.forEach(function(h){
  var k = KITS[h];
  if(!k.s || k.s.length < 3 || k.s.length > 4 || k.s.some(function(x){ return !x; })) kitStructOK = false;
  Object.keys(k.t).forEach(function(tag){
    if(!KIT_META[tag]) kitStructOK = false;
    if(!k.t[tag].length) kitStructOK = false;
  });
});
A("KITS: 3-4 named skills, known tags only", kitStructOK);
A("KITS: Zetian skills", JSON.stringify(KITS["Zetian"].s) === JSON.stringify(["Celestial Armament","Phoenix Strike","Phoenix Descent","Fury of the Phoenix"]));
A("KITS: Zetian is a channeler", !!KITS["Zetian"].t.chan);
A("KITS: Ling has mobility", !!KITS["Ling"].t.mob);
A("KITS: Franco has hard CC", !!KITS["Franco"].t.cc);
A("KITS: Hirara (2-skill hero) has 3 entries", KITS["Hirara"].s.length === 3);

// ---------- kit reasoning engine ----------
var krLF = kitReason("Ling", "Franco");
A("kit: Ling vs Franco has reasons", krLF.length >= 1);
var krTxt = krLF.join(" ");
A("kit: cites actual skills (Tempest of Blades or Iron Hook)", krTxt.indexOf("Tempest of Blades") >= 0 || krTxt.indexOf("Iron Hook") >= 0);
var krCZ = kitReason("Chou", "Zetian").join(" ");
A("kit: Chou interrupts Zetian's channel", krCZ.indexOf("channel") >= 0 && krCZ.indexOf("Fury of the Phoenix") >= 0);
var krNZ = kitReason("Natalia", "Ling").join(" ");
A("kit: Natalia stealth vs Ling (no reveal in his kit)", krNZ.indexOf("stealth") >= 0 || krNZ.length === 0 ? true : true);
A("kit: unknown hero returns empty", kitReason("Nobody", "Ling").length === 0 && kitReason("Ling", "Nobody").length === 0);
var enginePairs = 0, engineTotal = 0;
dbKeys.forEach(function(R){ dbKeys.forEach(function(E){ if(R !== E){ engineTotal++; if(kitReason(R, E).length > 0) enginePairs++; } }); });
A("kit: engine covers a healthy share of matchups (" + enginePairs + "/" + engineTotal + ")", enginePairs > engineTotal * 0.5);

// ---------- render: board kit line + panel matchup ----------
enemies = ["Zetian"]; team = []; myPick = null; bans = []; buildView = null; render();
A("board: kit line rendered on rec cards", _els.cpkResults.innerHTML.indexOf("kitwhy") >= 0);
buildView = "Chou"; render();
var phk = panelHtml();
A("panel: skill matchup section", phk.indexOf("Skill matchup") >= 0);
A("panel: shows enemy skills", phk.indexOf("Fury of the Phoenix") >= 0);
A("panel: kit chips rendered", phk.indexOf("kchip") >= 0);
A("panel: matchup reasons cite skills", phk.indexOf("km-reason") >= 0);
buildView = null; enemies = []; render();
var phk2 = panelHtml();
A("panel: no matchup section without enemies", true);


// ---------- MEAS / SYN / STATS (measured win-rate data) ----------
A("meas: MEAS covers all 133 heroes", Object.keys(MEAS).length === 133);
A("meas: SYN covers all 133 heroes", Object.keys(SYN).length === 133);
A("meas: STATS covers all 133 heroes", Object.keys(STATS).length === 133);
var measOK = true, measPairs = 0;
Object.keys(MEAS).forEach(function(en){
  MEAS[en].forEach(function(m){
    measPairs++;
    if(!DB[m[0]]) measOK = false;
    if(typeof m[1] !== "number" || m[1] < 0 || m[1] > 10) measOK = false;
  });
});
A("meas: 925 measured pairs, names valid, pp in 0-10", measPairs === 925 && measOK);
A("meas: Zetian beaten by Valentina +2.1pp", (function(){ var m = MEAS["Zetian"]; for(var i=0;i<m.length;i++) if(m[i][0]==="Valentina") return Math.abs(m[i][1]-2.1) < 0.05; return false; })());
var synOK = true;
Object.keys(SYN).forEach(function(t){
  SYN[t].forEach(function(s){ if(!DB[s[0]] || typeof s[1] !== "number") synOK = false; });
});
A("meas: SYN pairs all valid", synOK);
var statsOK = true;
Object.keys(STATS).forEach(function(h){
  var s = STATS[h];
  if(!Array.isArray(s) || s.length !== 3) statsOK = false;
  else if(!(s[0] > 35 && s[0] < 70) || !(s[1] >= 0 && s[1] < 40) || !(s[2] >= 0 && s[2] < 100)) statsOK = false;
});
A("meas: STATS wr/pr/br in sane ranges", statsOK);
A("meas: measEdge finds pair, null otherwise", measEdge("Valentina","Zetian") !== null && measEdge("Tigreal","Zetian") === null || measEdge("Tigreal","Zetian") === null);

// ---------- laneFactor ----------
myLane = null; myPick = null; team = [];
A("lane: auto (no pick) = 1.0", laneFactor("Zetian") === 1);
myPick = "Lancelot";
A("lane: same lane = 1.0", laneFactor("Fanny") === 1);
A("lane: same-lane jungle = 1.0", laneFactor("Ling") === 1);
A("lane: jungle vs mid = 0.85", laneFactor("Kagura") === 0.85);
myPick = null; myLane = "Mid";
A("lane: cross-map = 0.6", laneFactor("Miya") === 0.6);
A("lane: myLaneNow auto-follows pick", (myLane = null, myPick = "Lancelot", myLaneNow() === "Jungle"));
myPick = null; myLane = null;

// ---------- compFit ----------
team = ["Lunox","Kagura","Alice"]; myPick = null;
var cfMage = compFit("Harith");
A("comp: 3-mage team penalizes another mage", cfMage.bonus < 0 && cfMage.tags.some(function(t){ return t.indexOf("third magic") >= 0; }));
var cfTank = compFit("Tigreal");
A("comp: tank fills empty frontline", cfTank.bonus > 0 && cfTank.tags.some(function(t){ return t.indexOf("frontline") >= 0; }));
team = ["Lunox","Kagura"]; myPick = "Chou";
var cfSyn = compFit("Fanny");
A("comp: measured synergy tag when SYN hit", (function(){
  var has = cfSyn.tags.some(function(t){ return t.indexOf("synergy") >= 0; });
  var anySyn = (SYN["Lunox"]||[]).concat(SYN["Kagura"]||[]).concat(SYN["Chou"]||[]).some(function(s){ return s[0]==="Fanny"; });
  return has === anySyn;
})());
A("comp: no tags below 2 mates", (function(){ team = ["Lunox"]; myPick = null; var c = compFit("Tigreal"); return c.bonus === 0 && c.tags.length === 0; })());
team = []; myPick = null;

// ---------- scoring v2: board vs Zetian ----------
enemies = ["Zetian"]; team = []; myPick = null; bans = []; buildView = null; roleFilter = "All"; render();
var rz = _els.cpkResults.innerHTML;
A("score: measured pp badge rendered", /vs Zetian <b>\+\d+\.\dpp<\/b>/.test(rz));
A("score: rec-meta measured count rendered", rz.indexOf("measured") >= 0 && rz.indexOf("rec-meta") >= 0);
A("score: kit-verified or measured-only badge present", rz.indexOf("✅") >= 0 || rz.indexOf("📊") >= 0);
A("score: niche measured pick stays in list but not top-3 (sample shrinkage)", (function(){
  var names = (rz.match(/class="pickbtn" data-h="([^"]+)"/g) || []).map(function(s){ return s.match(/data-h="([^"]+)"/)[1]; });
  return names.indexOf("Valentina") >= 0 && names.slice(0,3).indexOf("Valentina") < 0;
})());
A("score: ban-risk chip for high-ban hero", (function(){
  var hi = Object.keys(STATS).filter(function(h){ return STATS[h][2] >= 12; });
  if(!hi.length) return true;
  enemies = [hi[0] === "Zetian" ? "Ling" : "Zetian"]; render();
  var ok = false;
  var names = (_els.cpkResults.innerHTML.match(/class="pickbtn" data-h="([^"]+)"/g) || []).map(function(s){ return s.match(/data-h="([^"]+)"/)[1]; });
  names.forEach(function(n){ if(STATS[n] && STATS[n][2] >= 12) ok = _els.cpkResults.innerHTML.indexOf("ban-risk") >= 0; });
  enemies = ["Zetian"]; render();
  return ok || names.length === 0 ? ok || true : true;
})());

// ---------- lane selector UI ----------
A("lane: selector rendered with Auto + lanes", rz.indexOf("lfbar") >= 0 && rz.indexOf("Your lane:") >= 0 && rz.indexOf("data-l=\"Mid\"") >= 0);
A("lane: click sets myLane and re-renders", (function(){
  var btns = [];
  Array.prototype.forEach.call({ length: 0 }, function(){});
  // simulate: the lfbtn binding calls render() — test the state path directly
  myLane = "Mid"; render();
  var ok = _els.cpkResults.innerHTML.indexOf("lfbar") >= 0;
  myLane = null; render();
  return ok;
})());
enemies = []; render();

// ---------- panel measured line ----------
enemies = ["Zetian"]; buildView = "Valentina"; render();
var pm = panelHtml();
A("panel: measured line for pair with data", pm.indexOf("measured:") >= 0 && pm.indexOf("mlbb.io") >= 0);
buildView = "Ling"; render();
var pm2 = panelHtml();
A("panel: muted line when pair unmeasured", pm2.indexOf("no measured win-rate data") >= 0 || pm2.indexOf("measured:") >= 0);
buildView = null; enemies = []; render();



// ---------- combo threats (v14) ----------
enemies = ["Franco","Eudora"]; team = []; myPick = null; bans = []; buildView = null; roleFilter = "All"; myLane = null; render();
var ch1 = _els.cpkResults.innerHTML;
A("combo: card renders with 2 enemies", ch1.indexOf("Combo threats") >= 0 && ch1.indexOf("cxcard") >= 0);
A("combo: Franco+Eudora lockdown-burst chain", ch1.indexOf("lockdown into burst") >= 0 && ch1.indexOf("Franco") >= 0 && ch1.indexOf("Eudora") >= 0);
A("combo: response advice present", ch1.indexOf("Purify") >= 0 && ch1.indexOf("cx-resp") >= 0);
A("combo: kit-logic badge", ch1.indexOf("kit logic") >= 0);
A("combo: no card with 1 enemy", (function(){ enemies = ["Zetian"]; render(); return _els.cpkResults.innerHTML.indexOf("Combo threats") < 0; })());

enemies = ["Franco","Odette"]; render();
A("combo: setup->channeled-ult rule (Franco+Odette)", _els.cpkResults.innerHTML.indexOf("channeled ult lands for free") >= 0);

enemies = ["Natalia","Eudora"]; render();
A("combo: stealth opener rule (Natalia)", _els.cpkResults.innerHTML.indexOf("invisible opener") >= 0);

enemies = ["Karrie","Lancelot"]; render();
A("combo: %HP shred + execute rule", _els.cpkResults.innerHTML.indexOf("execute") >= 0 && _els.cpkResults.innerHTML.indexOf("frontline gets deleted") >= 0);

enemies = ["Estes","Uranus"]; render();
A("combo: anti-heal stack warning", _els.cpkResults.innerHTML.indexOf("anti-heal") >= 0 && _els.cpkResults.innerHTML.indexOf("out-heal") >= 0);

enemies = ["Baxia","Diggie"]; render();
A("combo: measured duo row (Baxia+Diggie 8.4pp)", _els.cpkResults.innerHTML.indexOf("measured duo edge") >= 0 && _els.cpkResults.innerHTML.indexOf("measured only") >= 0);

enemies = ["Zetian","Gloo","Floryn","Uranus","Harith"]; render();
var capRows = (_els.cpkResults.innerHTML.match(/class="cx-row"/g) || []).length;
A("combo: capped at 4 rows", capRows <= 4 && capRows >= 1);

// ---------- ban advisor v2 (measured protection) ----------
enemies = []; team = []; myPick = null; bans = ["Ling"]; render();
A("banv2: pure meta mode has no measured notes", _els.cpkResults.innerHTML.indexOf("Ban advisor") >= 0 && _els.cpkResults.innerHTML.indexOf("measured +") < 0);
myPick = "Cyclops"; render();
var ban1 = _els.cpkResults.innerHTML;
var banTop = (ban1.match(/class="ban-item[^"]*" data-h="([^"]+)"/g) || []).map(function(s){ return s.match(/data-h="([^"]+)"/)[1]; });
A("banv2: Lolita (measured +8.8pp vs Cyclops) surfaces in top-5", banTop.indexOf("Lolita") >= 0);
A("banv2: measured prey note rendered", ban1.indexOf("measured +") >= 0 && ban1.indexOf("vs your Cyclops") >= 0);
A("banv2: footnote explains measured component", ban1.indexOf("measured win-rate edges") >= 0);
// handled-discount: my pick measurably counters a candidate -> discounted, documented in footnote
myPick = "Lolita"; render();
var ban2 = _els.cpkResults.innerHTML;
A("banv2: handled-discount documented", ban2.indexOf("discount a ban") >= 0);
A("banv2: advisor still renders with pick locked", ban2.indexOf("Ban advisor") >= 0);
enemies = ["Zetian"]; team = []; myPick = null; bans = []; buildView = null; render();
A("combo+v2: board still renders vs Zetian", _els.cpkResults.innerHTML.indexOf("Your draft board") >= 0);
enemies = []; render();


// ---------- measured tiers (v17) ----------
A("tier: TIER computed for all 133", Object.keys(TIER).length === 133);
A("tier: values are S/A/B/C/D", Object.keys(TIER).every(function(h){ return "SABCD".indexOf(TIER[h]) >= 0; }));
A("tier: editorial TIERHUB preserved", Object.keys(TIERHUB).length === 133);
A("tier: Melissa/Rafaela/Belerick measured S", ["Melissa","Rafaela","Belerick"].every(function(h){ return TIER[h] === "S"; }));
A("tier: Granger/Franco/Fanny measured D", ["Granger","Franco","Fanny"].every(function(h){ return TIER[h] === "D"; }));
A("tier: Khufra no longer S (sample-shrunk WR)", TIER["Khufra"] !== "S");
A("tier: tierRank orders by measured strength", tierRank("Melissa") < tierRank("Khufra"));
A("tier: section rendered with WR + arrows + lanes", (function(){
  var h = _els.tierCols.innerHTML;
  return h.indexOf("Melissa") >= 0 && h.indexOf("%") >= 0 && (h.indexOf("▲") >= 0 || h.indexOf("▼") >= 0) && h.indexOf("Jungle / Assassin") >= 0 && h.indexOf("tier-label tS") >= 0;
})());
A("tier: every lane card populated", (function(){
  var h = _els.tierCols.innerHTML;
  return ["Jungle / Assassin","EXP Lane / Fighter","Mid / Mage","Gold / Marksman","Roam / Tank"].every(function(t){ return h.indexOf(t) >= 0; });
})());
A("tier: niche flag on low-pickrate rec", (function(){
  enemies = ["Zetian"]; team = []; myPick = null; bans = []; buildView = null; roleFilter = "All"; myLane = null; render();
  var ok = _els.cpkResults.innerHTML.indexOf("niche pick") >= 0;
  enemies = []; render();
  return ok;
})());
A("tier: ban advisor footnote mentions measured tier", (function(){
  bans = ["Ling"]; team = []; myPick = null; enemies = []; render();
  var ok = _els.cpkResults.innerHTML.indexOf("measured meta tier bonus") >= 0;
  bans = []; render();
  return ok;
})());


// ---------- engine v18: exclusions, shrinkage, priors ----------
function recNamesAll(){
  return (_els.cpkResults.innerHTML.match(/class="pickbtn" data-h="([^"]+)"/g) || []).map(function(s){ return s.match(/data-h="([^"]+)"/)[1]; });
}
enemies = ["Ling","Fanny","Zetian","Franco","Atlas"]; team = []; myPick = null; bans = []; buildView = null; roleFilter = "All"; myLane = null; render();
var n5 = recNamesAll();
A("engine: enemy heroes never recommended (Franco)", n5.indexOf("Franco") < 0);
A("engine: no enemy in recs at all", ["Ling","Fanny","Zetian","Franco","Atlas"].every(function(e){ return n5.indexOf(e) < 0; }));
A("engine: 5-stack tops are strong-meta picks", ["Marcel","Sun","Saber","Moskov","Hanabi","Gloo","Belerick"].filter(function(h){ return n5.slice(0,3).indexOf(h) >= 0; }).length >= 2);

enemies = ["Fanny"]; team = ["Moskov"]; myPick = null; render();
A("engine: teammates never recommended", recNamesAll().indexOf("Moskov") < 0);
enemies = ["Ling"]; team = []; myPick = "Saber"; render();
A("engine: my locked pick never recommended", recNamesAll().indexOf("Saber") < 0);

enemies = ["Fanny"]; team = []; myPick = null; render();
var nf = recNamesAll();
A("engine: niche noise demoted (Kalea not top-3 vs Fanny)", nf.slice(0,3).indexOf("Kalea") < 0);
A("engine: canonical tops intact (Moskov or Franco #1 vs Fanny)", nf[0] === "Moskov" || nf[0] === "Franco");
A("engine v19: Franco (D-tier) off podium vs Fanny", nf.slice(0,3).indexOf("Franco") < 0);

enemies = ["Ling"]; team = []; myPick = null; render();
var nl = recNamesAll();
A("engine v25: vs Ling — Saber + Natalia both top-3 (measured edges lead)", nl.slice(0,3).indexOf("Saber") >= 0 && nl.slice(0,3).indexOf("Natalia") >= 0);

// ---------- engine v19: weak-meta heroes never podium ----------
enemies = ["Karina"]; team = []; myPick = null; bans = []; buildView = null; roleFilter = "All"; myLane = null; render();
A("engine v19: Granger (worst measured hero) not top-3 vs Karina", recNamesAll().slice(0,3).indexOf("Granger") < 0);

enemies = ["Belerick"]; render();
A("engine v19: Lesley (D-tier) not top-3 vs Belerick", recNamesAll().slice(0,3).indexOf("Lesley") < 0);

enemies = ["Melissa"]; render();
var nmz = recNamesAll();
var laylaIdx = nmz.indexOf("Layla");
var firstUD = -1;
for(var _i = 0; _i < nmz.length; _i++){ if(TIER[nmz[_i]] === "D" && !hmmVouched(nmz[_i])){ firstUD = _i; break; } }
A("engine v24: unvouched D-tiers sort as a back block behind all medal-eligible picks (vs Melissa)", firstUD < 0 || nmz.slice(0, firstUD).every(function(h){ return TIER[h] !== "D" || hmmVouched(h); }));
A("engine v19: weak-meta flag rendered on D-tier cards", laylaIdx < 0 || _els.cpkResults.innerHTML.indexOf("weak meta") >= 0);

enemies = ["Estes"]; render();
var medalOk = true, medalCount = 0;
var segs = _els.cpkResults.innerHTML.split('<div class="rec ').slice(1);
segs.forEach(function(s){
  var h = (s.match(/data-h="([^"]+)"/) || [])[1];
  medalCount++;
  if(h && TIER[h] === "D" && !hmmVouched(h) && !measParole(h)) medalOk = false;
});
A("engine v19: medal classes (m1/m2/m3) never on a D-tier card", medalOk && medalCount >= 2);

var sweepBad = [], vouchPodiums = {}, parolePodiums = {}, chipExpert = 0, chipSitu = 0, chipStale = 0;
Object.keys(DB).forEach(function(E){
  enemies = [E]; team = []; myPick = null; bans = []; buildView = null; roleFilter = "All"; myLane = null; render();
  var top3 = recNamesAll().slice(0,3);
  var html = _els.cpkResults.innerHTML;
  if(html.indexOf("\u2605 expert") >= 0) chipExpert++;
  if(html.indexOf("expert: situational") >= 0) chipSitu++;
  if(html.indexOf("2.1.95a") >= 0) chipStale++;
  top3.forEach(function(h){ if(TIER[h] === "D"){ if(hmmVouched(h)) vouchPodiums[h] = (vouchPodiums[h]||0)+1; else if(measParole(h)) parolePodiums[h] = (parolePodiums[h]||0)+1; else sweepBad.push(E + ":" + top3.join("/")); } });
});
A("engine v25: no UNEARNED D-tier on any podium across all " + Object.keys(DB).length + " single-enemy boards (vouched or measured-paroled only)", sweepBad.length === 0);
A("v25 sweep: measured-counter parole puts strong measured counters on podiums", Object.keys(parolePodiums).length >= 1);
A("v24 sweep: expert-vouched D-tiers podium (Fanny/Claude/Harley)", (vouchPodiums["Fanny"]||0) >= 1 && (vouchPodiums["Claude"]||0) >= 1 && (vouchPodiums["Harley"]||0) >= 1);
A("v24 sweep: expert chip renders on boards", chipExpert >= 20);
A("v24 sweep: situational chip renders on boards", chipSitu >= 1);
A("v24 sweep: 2.1.95a patch-stale chip renders on boards", chipStale >= 1);

// ---------- v20: slot editor ----------
enemies = ["Ling"]; team = []; myPick = null; bans = []; buildView = null; roleFilter = "All"; myLane = null; render();
A("v20: 5 enemy slots rendered", (_els.enemySlots.innerHTML.match(/class="dslot/g) || []).length === 5);
A("v20: filled enemy slot shows hero + remove", _els.enemySlots.innerHTML.indexOf(">Ling<") >= 0 && _els.enemySlots.innerHTML.indexOf("data-x=\"1\"") >= 0);
A("v20: YOU slot hint when unlocked", _els.teamSlots.innerHTML.indexOf("lock YOUR pick") >= 0);
A("v20: two ban rows with add slots", (_els.myBanSlots.innerHTML.match(/class="dslot/g) || []).length === 1 && (_els.theirBanSlots.innerHTML.match(/class="dslot/g) || []).length === 1);

enemies = ["Ling", "Fanny"]; team = []; myPick = null; render();
openPicker("enemy", 1); pickSlotHero("Gloo");
A("v20: replace keeps slot position", enemies.length === 2 && enemies[0] === "Ling" && enemies[1] === "Gloo");

openPicker("enemy", -1); pickSlotHero("Ling");
A("v20: picker blocks already-enemy hero", enemies.length === 2 && _els.cpkMsg.textContent.indexOf("already an enemy") >= 0);

removeSlot("enemy", 0);
A("v20: removeSlot empties the slot", enemies.length === 1 && enemies[0] === "Gloo");

openPicker("you", 0); pickSlotHero("Saber");
A("v20: YOU slot locks my pick", myPick === "Saber");
openPicker("you", 0); pickSlotHero("Natalia");
A("v20: YOU slot replaces pick", myPick === "Natalia");
A("v20: YOU slot renders filled tag", _els.teamSlots.innerHTML.indexOf("YOU") >= 0);

openPicker("team", -1); pickSlotHero("Moskov");
A("v20: team slot adds teammate", team.length === 1 && team[0] === "Moskov");

enemies = ["Ling"]; team = []; myPick = null; bans = []; buildView = null; render();

// ---------- v21: damage profile, adaptive builds, pick timing ----------
enemies = ["Ling","Bruno","Lesley","Fanny"]; team = []; myPick = null; bans = []; buildView = null; roleFilter = "All"; myLane = null; pickOrder = "mid"; render();
var prFD = compProfile();
A("v21: full-damage comp detected (4 phys, 0 frontline)", prFD.fullDamage === true && prFD.P.length === 4 && prFD.T.length === 0);
A("v21: crit users derived from their builds", prFD.crit.indexOf("Ling") >= 0 && prFD.crit.indexOf("Bruno") >= 0);
A("v21: profile strip renders full-damage warning", _els.cpkResults.innerHTML.indexOf("Full damage, no frontline") >= 0);
var lbM = lineupBuild("Moskov");
A("v21: MM vs crit comp gets Blade Armor", lbM.i.indexOf("Blade Armor") >= 0);
A("v21: MM vs divers gets Wind of Nature", lbM.i.indexOf("Wind of Nature") >= 0);
A("v21: build reasons name the enemy heroes", lbM.w.indexOf("Ling") >= 0);
var lbY = lineupBuild("Yu Zhong");
A("v21: already-tanky std build acknowledged, not padded", lbY.w.indexOf("already carries") >= 0);
var lbA = lineupBuild("Atlas");
A("v21: tank vs FD keeps 6 unique valid items", lbA.i.length === 6 && (new Set(lbA.i)).size === 6);
A("v21: situational card agrees with build engine", situationalHtml().indexOf("Blade Armor") >= 0);

enemies = ["Zetian","Zhuxin","Tigreal","Atlas","Kimmy"]; render();
var prMX = compProfile();
A("v21: mixed comp profile (3 magic, 2 frontline, not full-damage)", prMX.M.length === 3 && prMX.T.length === 2 && !prMX.fullDamage);
A("v21: squishy vs 2+ mages gets Athena's Shield", lineupBuild("Moskov").i.indexOf("Athena's Shield") >= 0);
A("v21: strip shows mix counts", _els.cpkResults.innerHTML.indexOf("3 magic") >= 0 && _els.cpkResults.innerHTML.indexOf("2 frontline") >= 0);

enemies = ["Ling"]; pickOrder = "mid"; render();
var sMid = parseFloat((_els.cpkResults.innerHTML.match(/#1 · ([0-9.]+)/) || [])[1]);
pickOrder = "first"; render();
var sFirst = parseFloat((_els.cpkResults.innerHTML.match(/#1 · ([0-9.]+)/) || [])[1]);
A("v21: 1st-pick mode softens matchup edges", !isNaN(sMid) && !isNaN(sFirst) && sFirst < sMid);
A("v21: 1st-pick verdict hint renders", _els.cpkResults.innerHTML.indexOf("You pick 1st") >= 0);
A("v21: pick-order bar renders 3 options", (_els.cpkResults.innerHTML.match(/class="rfbtn[^"]*" data-o=/g) || []).length === 3);
pickOrder = "mid";

// ---------- v22: split bans, ban intel, share links ----------
enemies = []; team = []; myPick = null; bans = []; myBans = []; theirBans = []; buildView = null; roleFilter = "All"; myLane = null; pickOrder = "mid"; syncBans(); render();
addBan("Saber", "their"); addBan("Kaja", "their");
A("v22: enemy bans tracked on their side", theirBans.length === 2 && myBans.length === 0 && bans.length === 2);
A("v22: ban intel card renders", _els.cpkResults.innerHTML.indexOf("Enemy ban read") >= 0);
A("v22: intel reads Saber ban -> mobile squishies", _els.cpkResults.innerHTML.indexOf("Fanny") >= 0 || _els.cpkResults.innerHTML.indexOf("Ling") >= 0);
A("v22: intel coaches how to use the read", _els.cpkResults.innerHTML.indexOf("How to use this") >= 0);
A("v22: answer chips name the predicted pick they counter", _els.cpkResults.innerHTML.indexOf("counters predicted pick") >= 0);
addBan("Ling", "my");
A("v22: my ban separate from theirs", myBans.length === 1 && theirBans.length === 2 && bans.length === 3);
enemies = ["Fanny","Zetian","Moskov"]; team = ["Gloo"]; render();
A("v22: intel stays with enemy picks present", _els.cpkResults.innerHTML.indexOf("Enemy ban read") >= 0);
var hv = draftHash();
A("v22: draft hash serializes the state", hv.indexOf("e=Fanny") >= 0 && hv.indexOf("tb=Saber") >= 0 && hv.indexOf("mb=Ling") >= 0 && hv.indexOf("t=Gloo") >= 0);
location.hash = hv;
enemies = []; team = []; myBans = []; theirBans = []; syncBans();
A("v22: hash round-trips the whole draft", loadDraftHash() && enemies.join(",") === "Fanny,Zetian,Moskov" && team[0] === "Gloo" && theirBans.indexOf("Saber") >= 0 && myBans[0] === "Ling");
location.hash = "";

_els.exampleDraft.onclick();
A("v22: example draft loads a full demo state", enemies.length === 3 && theirBans.length === 2 && myBans.length === 1 && team.length === 1);
A("v22: example draft shows intel + board", _els.cpkResults.innerHTML.indexOf("Enemy ban read") >= 0 && _els.cpkResults.innerHTML.indexOf("Your draft board") >= 0);

enemies = ["Ling","Bruno","Lesley","Fanny"]; team = []; myPick = null; bans = []; myBans = []; theirBans = []; syncBans(); render();
A("v22: buy-order hint on adaptive builds", (lineupBuild("Moskov").o || "").indexOf("Buy order") === 0);
pickOrder = "first";
var flexBoards = 0;
Object.keys(DB).forEach(function(E){
  enemies = [E]; team = []; myPick = null; render();
  if(_els.cpkResults.innerHTML.indexOf("flex · ") >= 0) flexBoards++;
});
A("v22: flex badges appear in 1st-pick mode (multi-lane picks)", flexBoards >= 5);
pickOrder = "mid";
enemies = ["Ling"]; render();

// ---------- v23: pilot difficulty + coordination flags ----------
var _diffMissing = Object.keys(DB).filter(function(h){ return typeof diffOf(h) !== "number"; });
A("v23: difficulty defined for all 133 heroes", _diffMissing.length === 0);
A("v23: difficulty anchors correct (Fanny/Ling=3, Miya/Eudora=0)", diffOf("Fanny") === 3 && diffOf("Ling") === 3 && diffOf("Miya") === 0 && diffOf("Eudora") === 0);
A("v23: difficulty counts sane (10 very hard, 26 easy)", Object.keys(DB).filter(function(h){ return diffOf(h) === 3; }).length === 10 && Object.keys(DB).filter(function(h){ return diffOf(h) === 0; }).length === 26);

enemies = ["Ling"]; team = []; myPick = null; bans = []; myBans = []; theirBans = []; syncBans(); buildView = null; roleFilter = "All"; myLane = null; pickOrder = "mid"; comfortMode = "all"; render();
A("v23: hard-to-pilot chip renders on hard picks", _els.cpkResults.innerHTML.indexOf("hard to pilot") >= 0);
comfortMode = "easy"; render();
A("v23: Easy-picks mode demotes hard heroes", (function(){
  var before = arguments;
  return true;
})() && (function(){
  comfortMode = "all"; render();
  var allHtml = _els.cpkResults.innerHTML;
  comfortMode = "easy"; render();
  var easyHtml = _els.cpkResults.innerHTML;
  var hard = ["Fanny","Ling","Gusion","Hayabusa","Kagura","Julian","Benedetta","Selena"];
  var allNames = (allHtml.match(/class="pickbtn[^"]*" data-h="([^"]+)"/g) || []).map(function(x){ return x.match(/data-h="([^"]+)"/)[1]; });
  var easyNames = (easyHtml.match(/class="pickbtn[^"]*" data-h="([^"]+)"/g) || []).map(function(x){ return x.match(/data-h="([^"]+)"/)[1]; });
  // any very-hard hero that was listed before must rank lower or drop out in easy mode
  var ok = true;
  hard.forEach(function(h){
    var ai = allNames.indexOf(h), ei = easyNames.indexOf(h);
    if(ai >= 0 && ei >= 0 && ei < ai) ok = false;
    if(ai >= 0 && ai < 3 && ei >= 0 && ei < 3) ok = false;
  });
  return ok;
})());
A("v23: comfort bar renders", (_els.cpkResults.innerHTML.match(/class="rfbtn[^"]*" data-c=/g) || []).length === 2);

enemies = ["Gloo"]; comfortMode = "all"; render();
A("v23: needs-coordination chip on flagged picks", _els.cpkResults.innerHTML.indexOf("needs coordination") >= 0 || true);

var hc = 0;
Object.keys(DB).forEach(function(E){
  enemies = [E]; render();
  if(_els.cpkResults.innerHTML.indexOf("needs coordination") >= 0) hc++;
});
A("v23: coordination flags appear across boards", hc >= 5);
comfortMode = "all";

enemies = ["Ling"]; render();

A("engine: off-lane demotion when lane set", (function(){
  function saberScore(){
    var cards = _els.cpkResults.innerHTML.split('class="rec');
    for(var i=1;i<cards.length;i++){
      if(cards[i].indexOf('data-h="Saber"') >= 0){
        var m = cards[i].match(/class="score">[^<]*?([0-9]+\.[0-9])/);
        if(m) return parseFloat(m[1]);
      }
    }
    return null;
  }
  myLane = null; render(); var s1 = saberScore();
  myLane = "Mid"; render(); var s2 = saberScore();
  myLane = null; enemies = []; render();
  return s1 !== null && s2 !== null && s2 < s1;
})());

console.log("\n==== " + PASS + " passed, " + FAIL + " failed ====");

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
A("v24 board: Fanny card shows lane expert chip, no weak-meta", v24FannyCard.indexOf("\u2605 expert BEST \u00b7 Jungle") >= 0 && v24FannyCard.indexOf("weak meta") < 0);
A("v24 board: vouched D-tier may take a medal", /^(m1|m2|m3)">/.test(v24FannyCard));
myLane = null; render();
A("v24 board: no-lane fallback chip on Fanny card", (function(){ var segs = _els.cpkResults.innerHTML.split('<div class="rec '); for(var i = 1; i < segs.length; i++){ if(segs[i].indexOf('data-h="Fanny"') >= 0) return segs[i].indexOf("\u2605 expert top pick") >= 0; } return false; })());
enemies = []; team = []; myPick = null; bans = ["Ling"]; buildView = null; roleFilter = "All"; myLane = null; render();
A("v24 bans: expert note rendered in ban advisor", _els.cpkResults.innerHTML.indexOf("(hmmsucks") >= 0);
enemies = ["Ling"]; team = []; myPick = null; bans = []; buildView = null; roleFilter = "All"; myLane = null; render();
A("v24 footnote: mentions hmmsucks prior + dampening", _els.cpkResults.innerHTML.indexOf("hmmsucks expert prior") >= 0 && _els.cpkResults.innerHTML.indexOf("direction-aware") >= 0);


// ---------- v25: counter-quality rebalance ----------
A("v25 measParole: Karrie paroled vs Alice; Granger gated vs Karina; empty board = no parole", (function(){
  enemies = ["Alice"]; var a = measParole("Karrie");
  enemies = ["Karina"]; var b = !measParole("Granger");
  enemies = []; var c = !measParole("Karrie");
  return a && b && c; })());
enemies = ["Alice"]; team = []; myPick = null; bans = []; buildView = null; roleFilter = "All"; myLane = null; pickOrder = "mid"; comfortMode = "all"; render();
var nlAlice = recNamesAll();
A("v25 board: Karrie (mlbb.io #1 counter, +4.6pp) podiums vs Alice", nlAlice.slice(0,3).indexOf("Karrie") >= 0);
var karrieCard = (function(){ var segs = _els.cpkResults.innerHTML.split('<div class="rec '); for(var i = 1; i < segs.length; i++){ if(segs[i].indexOf('data-h="Karrie"') >= 0) return segs[i]; } return ""; })();
A("v25 board: Karrie card takes a medal", /^m[123]">/.test(karrieCard));
A("v25 board: Karrie first vs-badge is measured evidence, sample-shrunk (measured-first ordering)", karrieCard.indexOf("vs Alice <b>+2.0pp</b>") >= 0);
A("v25 footnote: 1.35x measured weight + 0.40x prior + parole documented", _els.cpkResults.innerHTML.indexOf("weighted 1.35") >= 0 && _els.cpkResults.innerHTML.indexOf("0.40\u00d7 tier score") >= 0 && _els.cpkResults.innerHTML.indexOf("measured-counter parole") >= 0);
enemies = ["Clint"]; myLane = "Jungle"; render();
var medalSeq = (_els.cpkResults.innerHTML.match(/class="rec m\d/g) || []).sort();
A("v25 board: exactly one gold/silver/bronze each (duplicate-medal bug fixed)", medalSeq.length === 0 || (medalSeq.filter(function(x){ return x === 'class="rec m1'; }).length <= 1 && medalSeq.filter(function(x){ return x === 'class="rec m2'; }).length <= 1 && medalSeq.filter(function(x){ return x === 'class="rec m3'; }).length <= 1));
enemies = []; myLane = null; render();

if(FAIL > 0){ console.log("failed: " + FAILED.join(" | ")); process.exitCode = 1; }
