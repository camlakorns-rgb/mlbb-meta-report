#!/usr/bin/env python3
"""v21 part A: enemy damage-profile engine + lineupBuild v2 + situationalHtml v2."""
src = open('template.html', encoding='utf-8').read()
orig = len(src)

NEW = '''/* ================= ENEMY DAMAGE PROFILE (v21) =================
   Damage types derived from what each hero actually builds (standard preset):
   2+ magic items = magic dealer; Berserker Fury/Windtalker = crit threat;
   DHS/Golden Staff/Windtalker/Corrosive Scythe = attack-speed threat.
   Tanks count as frontline, not damage. Itemization rules follow ONE Esports
   + MLBB wiki + community consensus (Athena vs Radiant, Blade vs Antique). */
function buildOf(h){ return (MYB[h] || [])[0] || null; }
function dmgTypeOf(h){
  if(TANKS.indexOf(h) >= 0) return "T";
  if((ROLE[h] || "").indexOf("Mage") >= 0) return "M";
  var b = buildOf(h);
  if(b){
    var mag = 0;
    for(var k = 0; k < b.i.length; k++) if(AR_MAG[b.i[k]]) mag++;
    if(mag >= 2) return "M";
  }
  return "P";
}
function critUser(h){
  var b = buildOf(h);
  return !!b && (b.i.indexOf("Berserker's Fury") >= 0 || b.i.indexOf("Windtalker") >= 0);
}
function aspdUser(h){
  var b = buildOf(h);
  return !!b && (b.i.indexOf("Demon Hunter Sword") >= 0 || b.i.indexOf("Golden Staff") >= 0 || b.i.indexOf("Windtalker") >= 0 || b.i.indexOf("Corrosive Scythe") >= 0);
}
function compProfile(){
  var P = [], M = [], T = [], crit = [], aspd = [], heal = [], div = [], sust = [], ccN = 0;
  enemies.forEach(function(e){
    var d = dmgTypeOf(e);
    if(d === "M") M.push(e); else if(d === "P") P.push(e); else T.push(e);
    if(critUser(e)) crit.push(e);
    if(aspdUser(e)) aspd.push(e);
    if(HEALERS.indexOf(e) >= 0) heal.push(e);
    if(DIVERS.indexOf(e) >= 0) div.push(e);
    if(AR_SUSMAGE.indexOf(e) >= 0) sust.push(e);
    if(CCLIST.indexOf(e) >= 0) ccN++;
  });
  var dmg = P.length + M.length;
  return {
    P: P, M: M, T: T, crit: crit, aspd: aspd, heal: heal, div: div, sust: sust, ccN: ccN,
    dmg: dmg,
    fullDamage: enemies.length >= 4 && T.length === 0 && dmg >= 4,
    heavyPhys: P.length >= 3,
    heavyMagic: M.length >= 2
  };
}
function lineupBuild(hero){
  var std = buildOf(hero);
  if(!std || !enemies.length) return null;
  var pr = compProfile();
  var prim = (ROLE[hero] || "").split("·")[0].trim();
  var tanky = prim === "Tank" || prim === "Support";
  var fighter = prim === "Fighter";
  var squishy = !tanky && !fighter;
  var backline = prim === "Marksman" || prim === "Mage";
  var magic = std.i.some(function(it){ return AR_MAG[it]; });

  function antiHealItem(){ return tanky ? "Dominance Ice" : (magic ? "Glowing Wand" : "Sea Halberd"); }
  function magicItem(){ return squishy ? "Athena's Shield" : (pr.sust.length ? "Radiant Armor" : "Athena's Shield"); }
  function diveItem(){
    if(prim === "Marksman" && !magic) return "Wind of Nature";
    if(magic || prim === "Mage") return "Winter Crown";
    return tanky ? "Immortality" : "Queen's Wings";
  }
  function physItem(){ return pr.crit.length ? "Blade Armor" : "Antique Cuirass"; }

  /* ordered defensive answers; backliners threatened by divers answer the dive first */
  var order = (backline && pr.div.length >= 2)
    ? ["dive", "heal", "magic", "phys", "aspd", "imm"]
    : ["heal", "magic", "phys", "aspd", "dive", "imm"];
  var table = {
    heal:  pr.heal.length >= 2 ? [antiHealItem(), "anti-heal vs " + pr.heal.slice(0,2).join(" + ")] : null,
    magic: pr.heavyMagic ? [magicItem(), "magic damage from " + pr.M.slice(0,2).join(", ") + (squishy ? " — Athena's Shield stops the one-combo delete" : (pr.sust.length ? " — sustained ticks stack Radiant Armor" : ""))] : null,
    phys:  (pr.crit.length && (pr.P.length >= 2 || pr.crit.length >= 2))
             ? ["Blade Armor", "crit carries (" + pr.crit.slice(0,2).join(", ") + ") — the only crit-damage reduction in the game"]
             : (pr.P.length >= 3 ? ["Antique Cuirass", "physical skill damage from " + pr.P.slice(0,3).join(", ") + " — Deter stacks cut their burst"]
               : (pr.P.length >= 2 && (squishy || pr.fullDamage) ? ["Antique Cuirass", "physical threats (" + pr.P.slice(0,2).join(", ") + ") — cuts their attack on every skill hit"] : null)),
    aspd:  (pr.aspd.length && (tanky || pr.heal.length)) ? ["Dominance Ice", "attack-speed slow vs " + pr.aspd.slice(0,2).join(", ") + (pr.heal.length ? " + cuts their healing" : "")] : null,
    dive:  pr.div.length >= 2 ? [diveItem(), "they dive you (" + pr.div.slice(0,2).join(", ") + ")"] : null,
    imm:   (pr.fullDamage && !tanky) ? ["Immortality", "zero frontline, " + pr.dmg + " damage threats — they win the damage race unless you get a second life"] : null
  };
  var picks = [];
  order.forEach(function(key){ if(table[key]) picks.push(table[key]); });

  /* penetration vs a double-tank front line is an offense flex, not defense budget */
  var flex = null;
  if(pr.T.length >= 2){
    flex = magic ? (std.i.indexOf("Divine Glaive") >= 0 ? "Wishing Lantern" : "Divine Glaive")
                 : (prim === "Marksman" ? "Demon Hunter Sword" : "Malefic Roar");
  }

  /* how many flex slots convert to survival (std defense items already count) */
  function isDef(it){
    return PHYSDEF.indexOf(it) >= 0 || MAGICDEF.indexOf(it) >= 0 || it === "Immortality"
      || it === "Queen's Wings" || it === "Wind of Nature" || it === "Winter Crown";
  }
  var already = std.i.filter(isDef).length;
  var budget = tanky ? 2
    : (pr.fullDamage || (pr.heavyPhys && pr.heavyMagic)) ? 2
    : (pr.dmg >= 3 ? (squishy ? 2 : 1) : (pr.dmg >= 2 ? 1 : 0));
  budget = Math.max(0, budget - already);

  var boot = "Tough Boots";
  for(var b0 = 0; b0 < std.i.length; b0++) if(AR_BOOTS[std.i[b0]]) boot = std.i[b0];
  var items = [boot].concat(std.i.filter(function(it){ return !AR_BOOTS[it]; }).slice(0, 2));
  var why = [];
  picks = picks.filter(function(nd){ return items.indexOf(nd[0]) < 0; }).slice(0, budget);
  picks.forEach(function(nd){ items.push(nd[0]); why.push(nd[1]); });
  if(flex && items.indexOf(flex) < 0 && items.length < 6){
    items.push(flex);
    why.push("shred the " + pr.T.slice(0,2).join(" + ") + " front line");
  }
  std.i.forEach(function(it){ if(items.length < 6 && items.indexOf(it) < 0 && !AR_BOOTS[it]) items.push(it); });

  var spell = std.s;
  if(pr.ccN >= 3){
    if(items[0] !== "Tough Boots") items[0] = "Tough Boots";
    if(spell === "Flicker") spell = "Purify";
    why.push("Tough Boots" + (spell === "Purify" ? " + Purify" : "") + " vs their CC chain");
  }

  var head;
  if(pr.fullDamage) head = "Full-damage comp — " + pr.dmg + " damage threats, no frontline to absorb anything. This build keeps your core and inserts " + Math.max(picks.length, 0) + " survival item" + (picks.length === 1 ? "" : "s") + ": trade a little damage for not dying in their opener.";
  else if(!picks.length && already >= 2) head = "Balanced lineup — and your standard build already carries " + already + " defensive items. That IS the answer.";
  else if(!picks.length) head = "Balanced lineup — " + pr.dmg + " damage threat" + (pr.dmg === 1 ? "" : "s") + ", " + pr.T.length + " frontline; no forced swaps, the standard build holds up.";
  else head = "Adapted to their damage mix (" + pr.P.length + " physical · " + pr.M.length + " magic · " + pr.T.length + " frontline).";

  return { n: "⚡ vs this lineup", i: items, e: std.e, s: spell,
    w: head + " " + (why.join(" · ") || "") + " Updates as the draft changes." };
}
function situationalHtml(){
  if(!enemies.length) return '';
  var pr = compProfile();
  var recs = [];
  if(pr.heal.length >= 2) recs.push(["Sea Halberd", "anti-heal is near-mandatory — sustain: " + pr.heal.map(esc).join(", ") + " (Dominance Ice for tanks, Necklace of Durance for mages)"]);
  if(pr.heavyMagic) recs.push(["Athena's Shield", "heavy magic damage (" + pr.M.map(esc).join(", ") + ")" + (pr.sust.length ? " — Radiant Armor instead if you are the frontline vs sustained ticks (" + pr.sust.slice(0,2).map(esc).join(", ") + ")" : "")]);
  if(pr.crit.length && (pr.P.length >= 2 || pr.crit.length >= 2)) recs.push(["Blade Armor", "crit carries (" + pr.crit.map(esc).join(", ") + ") — the only crit-damage reduction in the game"]);
  if(pr.heavyPhys && !pr.crit.length) recs.push(["Antique Cuirass", "physical skill threats (" + pr.P.map(esc).join(", ") + ") — Deter cuts their attack per skill hit"]);
  if(pr.aspd.length >= 2) recs.push(["Dominance Ice", "attack-speed threats (" + pr.aspd.map(esc).join(", ") + ") — the aura slows their basic attacks"]);
  if(pr.T.length >= 2) recs.push(["Demon Hunter Sword", "tanky front line (" + pr.T.map(esc).join(", ") + ") — %HP damage; Malefic Roar for fighters, Genius Wand/Glowing Wand for mages"]);
  if(pr.div.length >= 2) recs.push(["Wind of Nature", "diver-heavy comp (" + pr.div.map(esc).join(", ") + ") — Wind of Nature for marksmen, Winter Truncheon for mages"]);
  if(pr.ccN >= 3) recs.push(["Tough Boots", "heavy CC — Tough Boots + consider Purify over your default spell"]);
  if(!recs.length) return '';
  var chips = recs.map(function(r){
    var ic = ISLUG[r[0]] ? '<i class="ic ' + ISLUG[r[0]] + '"></i>' : '';
    return '<div class="sitrow">' + ic + '<b>' + esc(r[0]) + '</b><span>' + r[1] + '</span></div>';
  }).join("");
  var prof = "Enemy profile: " + pr.P.length + " physical · " + pr.M.length + " magic · " + pr.T.length + " frontline" + (pr.heal.length ? " · " + pr.heal.length + " sustain" : "") + (pr.ccN ? " · " + pr.ccN + " CC" : "") + ".";
  return '<div class="bp-sit"><div class="bp-blabel">🎯 vs this enemy team — ' + esc(prof) + '</div>' + chips
    + '<div style="font-size:11px;color:var(--muted);margin-top:6px;">Damage types are derived from what each hero actually builds. Swap into flex slots (usually items 5–6); boots stay.</div></div>';
}
'''
i = src.find('function lineupBuild(hero){')
j = src.find('/* ---- build fit: which of the hero\'s presets suits this matchup ---- */')
assert 0 < i < j, 'lineupBuild span not found'
src = src[:i] + NEW + src[j:]
open('template.html', 'w', encoding='utf-8').write(src)
print('part A OK:', orig, '->', len(src))
