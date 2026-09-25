#!/usr/bin/env python3
"""v22: split bans (yours/theirs), enemy ban intelligence, share links,
example draft, buy-order hints, flex badges."""
src = open('template.html', encoding='utf-8').read()
orig = len(src)
def rep(old, new, expect=1):
    global src
    n = src.count(old)
    assert n == expect, 'count %d != %d: %r' % (n, expect, old[:70])
    src = src.replace(old, new)

# ---------- 1. HTML: two ban rows + share button ----------
rep('''  <div class="pad-top">
    <div class="side-lbl grey">BANS <span class="side-note">— up to 10 · banned heroes never appear in any list</span></div>
    <button id="draftClear" class="draft-clear" style="display:none;" title="Reset the whole draft — enemies, team, your pick and bans">Clear draft</button>
  </div>
  <div class="slotrow bans" id="banSlots"></div>''',
'''  <div class="pad-top">
    <div class="side-lbl grey">BANS <span class="side-note">— 5 yours + 5 theirs · banned heroes never appear in any list. <b>Their bans are intel:</b> people ban the counters of what they plan to play</span></div>
    <span class="pad-actions"><button id="shareDraft" class="draft-clear" style="display:none;" title="Copy a link that recreates this exact draft">Share draft</button><button id="draftClear" class="draft-clear" style="display:none;" title="Reset the whole draft — enemies, team, your pick and bans">Clear draft</button></span>
  </div>
  <div class="banrow"><span class="bside-lbl">YOURS</span><div class="slotrow bans" id="myBanSlots"></div></div>
  <div class="banrow"><span class="bside-lbl theirs">THEIRS</span><div class="slotrow bans" id="theirBanSlots"></div></div>''')

# ---------- 2. example button in empty state ----------
rep('''<div class="cpk-empty" id="cpkEmpty">Draft not started — tap a slot above: enemies (right), your team (left) or bans (top). The ban advisor, counter board and builds appear here as you go. <b>Tip:</b> add <i>Ling</i> as an enemy, then tap the YOU slot and pick <i>Saber</i> — every recommended hero is searchable too.</div>''',
'''<div class="cpk-empty" id="cpkEmpty">Draft not started — tap a slot above: enemies (right), your team (left), your bans and theirs (top). Their bans feed the <b>enemy ban read</b>; enemy picks drive the <b>counter board</b>. <button id="exampleDraft" class="exbtn">Load example draft</button> — or add <i>Ling</i> as an enemy, then tap the YOU slot and pick <i>Saber</i>.</div>''')

# ---------- 3. JS: state split ----------
rep('''var bans = [];       /* up to 10 */''',
'''var myBans = [];      /* your side, up to 5 */
var theirBans = [];   /* enemy side, up to 5 — read by banIntelHtml() */
var bans = [];        /* union — every list excludes these */
function syncBans(){ bans = myBans.concat(theirBans); }''')

rep('''function addBan(name){
  if(bans.indexOf(name)>=0) return;
  if(enemies.indexOf(name)>=0){ cpkMsg(name+" is on the enemy team."); return; }
  if(team.indexOf(name)>=0){ cpkMsg(name+" is on your team."); return; }
  if(myPick===name){ cpkMsg(name+" is your locked pick."); return; }
  if(bans.length>=10){ cpkMsg("Max 10 bans (5 per side)."); return; }
  bans.push(name); cpkMsg(""); render();
}
function removeBan(name){ bans = bans.filter(function(b){return b!==name;}); render(); }''',
'''function addBan(name, side){
  side = side || "my";
  var arr = side === "their" ? theirBans : myBans;
  if(bans.indexOf(name)>=0) return;
  if(enemies.indexOf(name)>=0){ cpkMsg(name+" is on the enemy team."); return; }
  if(team.indexOf(name)>=0){ cpkMsg(name+" is on your team."); return; }
  if(myPick===name){ cpkMsg(name+" is your locked pick."); return; }
  if(arr.length>=5){ cpkMsg("Max 5 bans per side."); return; }
  arr.push(name); syncBans(); cpkMsg(""); render();
}
function removeBan(name){
  myBans = myBans.filter(function(b){return b!==name;});
  theirBans = theirBans.filter(function(b){return b!==name;});
  syncBans(); render();
}''')

# ---------- 4. slot kinds ----------
rep('''  if(kind === "ban") return bans[idx] || null;''',
'''  if(kind === "myban") return myBans[idx] || null;
  if(kind === "theirban") return theirBans[idx] || null;''')

rep('''  return kind === "enemy" ? "ADD AN ENEMY" : kind === "ban" ? "ADD A BAN"
    : kind === "you" ? "YOUR PICK — YOU" : "ADD A TEAMMATE";''',
'''  return kind === "enemy" ? "ADD AN ENEMY"
    : kind === "myban" ? "ADD YOUR BAN"
    : kind === "theirban" ? "ADD AN ENEMY BAN"
    : kind === "you" ? "YOUR PICK — YOU" : "ADD A TEAMMATE";''')

rep('''  } else if(kind === "ban"){
    if(idx >= 0 && idx < bans.length) bans[idx] = name;
    else if(bans.length < 10) bans.push(name);
  } else if(kind === "you"){''',
'''  } else if(kind === "myban" || kind === "theirban"){
    var barr = kind === "myban" ? myBans : theirBans;
    if(idx >= 0 && idx < barr.length) barr[idx] = name;
    else if(barr.length < 5) barr.push(name);
    syncBans();
  } else if(kind === "you"){''')

rep('''  else if(kind === "ban") removeBan(cur);''',
'''  else if(kind === "myban" || kind === "theirban") removeBan(cur);''')

# ---------- 5. renderSlots: two ban rows ----------
rep('''  var banEl = document.getElementById("banSlots");
  var teamEl = document.getElementById("teamSlots");
  var enEl = document.getElementById("enemySlots");
  var html, i;
  if(banEl){
    html = bans.map(function(b, i2){ return slotHtml("ban", i2, b); }).join("");
    if(bans.length < 10) html += slotHtml("ban", -1, null);
    banEl.innerHTML = html;
    wireSlots(banEl);
  }''',
'''  var myBEl = document.getElementById("myBanSlots");
  var thBEl = document.getElementById("theirBanSlots");
  var teamEl = document.getElementById("teamSlots");
  var enEl = document.getElementById("enemySlots");
  var html, i;
  if(myBEl){
    html = myBans.map(function(b, i2){ return slotHtml("myban", i2, b); }).join("");
    if(myBans.length < 5) html += slotHtml("myban", -1, null);
    myBEl.innerHTML = html;
    wireSlots(myBEl);
  }
  if(thBEl){
    html = theirBans.map(function(b, i2){ return slotHtml("theirban", i2, b); }).join("");
    if(theirBans.length < 5) html += slotHtml("theirban", -1, null);
    thBEl.innerHTML = html;
    wireSlots(thBEl);
  }''')

# ---------- 6. clearDraft + share visibility ----------
rep('''  enemies = []; team = []; myPick = null; bans = []; buildView = null;
  closePicker(); cpkMsg("");''',
'''  enemies = []; team = []; myPick = null; myBans = []; theirBans = []; bans = []; buildView = null;
  closePicker(); cpkMsg("");''')

rep('''  var _dcb = document.getElementById("draftClear");
  if(_dcb) _dcb.style.display = (enemies.length || team.length || myPick || bans.length) ? "" : "none";''',
'''  var _dcb = document.getElementById("draftClear");
  if(_dcb) _dcb.style.display = (enemies.length || team.length || myPick || bans.length) ? "" : "none";
  var _shb = document.getElementById("shareDraft");
  if(_shb) _shb.style.display = (enemies.length || team.length || myPick || bans.length) ? "" : "none";''')

# ---------- 7. ban intelligence engine + card ----------
rep('''function banAdvisorHtml(){''',
'''/* ================= ENEMY BAN INTELLIGENCE (v22) =================
   People ban the counters of what they plan to play. For each enemy ban B,
   the heroes B is a top-4 listed counter of are likely planned picks
   (3-source ensemble DB). High-ban-rate heroes are usually just meta bans. */
function banReads(){
  var reads = [];
  var excluded = enemies.concat(team, myPick ? [myPick] : [], bans);
  theirBans.forEach(function(B){
    var planned = [];
    Object.keys(DB).forEach(function(H){
      if(excluded.indexOf(H) >= 0) return;
      var c = DB[H].c || [];
      for(var i = 0; i < Math.min(c.length, 4); i++){
        if(c[i][0] === B){ planned.push({h: H, rank: i, conf: c[i][2] || 1}); break; }
      }
    });
    planned.sort(function(a, b){ return (a.rank - b.rank) || (b.conf - a.conf) || a.h.localeCompare(b.h); });
    var br = STATS[B] ? STATS[B][2] : 0;
    reads.push({b: B, banRate: br, planned: planned.slice(0, 3)});
  });
  return reads;
}
function banIntelHtml(){
  if(!theirBans.length) return '';
  var reads = banReads();
  var rows = reads.map(function(r){
    var head;
    if(r.banRate >= 20){
      head = '<b>'+esc(r.b)+'</b> — banned in '+r.banRate.toFixed(0)+'% of ranked games: standard meta ban, little draft signal.';
    } else if(r.planned.length){
      var names = r.planned.map(function(p){ return esc(p.h); }).join(", ");
      var answers = [];
      r.planned.forEach(function(p){
        (DB[p.h].c || []).slice(0, 3).forEach(function(pair){
          if(answers.length < 4 && bans.indexOf(pair[0]) < 0 && enemies.indexOf(pair[0]) < 0
            && team.indexOf(pair[0]) < 0 && pair[0] !== myPick && answers.indexOf(pair[0]) < 0 && pair[0] !== r.b) answers.push(pair[0]);
        });
      });
      head = '<b>'+esc(r.b)+'</b> — top counter of <b>'+names+'</b>: they may be planning to play them.'
        + (answers.length ? ' Available answers: ' + answers.map(function(a){ return '<span class="pchip" data-h="'+esc(a)+'" title="'+esc(a)+' — click for build">'+avatar(a)+esc(a)+'</span>'; }).join(" ") : '');
    } else {
      head = '<b>'+esc(r.b)+'</b> — no strong read from our counter data.';
    }
    return '<div class="bi-row">'+head+'</div>';
  }).join("");
  var firstNote = '';
  if(pickOrder === "first") firstNote = '<div class="bi-note">You pick 1st — you lock before seeing their picks. Treat their bans above as your scouting report, lean safe/flex picks (see board), and spend your ban on the biggest threat of the patch (advisor below).</div>';
  return '<div class="card bicard"><div class="cardhead"><b>Enemy ban read</b>'
    + '<span class="csub">what their bans tell you about their plan</span></div>'
    + rows + firstNote
    + '<div style="font-size:11.5px;color:var(--muted);margin-top:8px;">Method: people ban the counters of heroes they intend to play. For each enemy ban we list the heroes it is a top-4 counter of (3-source ensemble; banned and taken heroes excluded). Bans on 20%+ ban-rate heroes are treated as meta noise.</div></div>';
}
function banAdvisorHtml(){''')

rep('''  resEl.innerHTML = banHtml + bpHtml + boardHtml + noteHtml;''',
'''  resEl.innerHTML = banIntelHtml() + banHtml + bpHtml + boardHtml + noteHtml;''')

# ---------- 8. share links + example draft wiring ----------
rep('''  document.addEventListener("keydown", function(e){
    if(e.key === "Escape" && picker.open) closePicker();
  });
})();''',
'''  document.addEventListener("keydown", function(e){
    if(e.key === "Escape" && picker.open) closePicker();
  });
})();
/* ---- shareable draft links (v22) ---- */
function draftHash(){
  var parts = [];
  if(enemies.length) parts.push("e=" + encodeURIComponent(enemies.join(",")));
  if(team.length) parts.push("t=" + encodeURIComponent(team.join(",")));
  if(myPick) parts.push("p=" + encodeURIComponent(myPick));
  if(myBans.length) parts.push("mb=" + encodeURIComponent(myBans.join(",")));
  if(theirBans.length) parts.push("tb=" + encodeURIComponent(theirBans.join(",")));
  if(myLane) parts.push("l=" + encodeURIComponent(myLane));
  if(pickOrder !== "mid") parts.push("o=" + pickOrder);
  return parts.length ? "#d/" + parts.join("&") : "";
}
function loadDraftHash(){
  try{
    var h = (location.hash || "");
    if(h.indexOf("#d/") !== 0) return false;
    var kv = {};
    decodeURIComponent(h.slice(3)).split("&").forEach(function(seg){
      var eq = seg.indexOf("=");
      if(eq > 0) kv[seg.slice(0, eq)] = seg.slice(eq + 1);
    });
    function names(k){ return kv[k] ? kv[k].split(",").filter(function(n){ return !!DB[n]; }) : []; }
    enemies = names("e").slice(0, 5);
    team = names("t").slice(0, 4);
    myPick = DB[kv.p] ? kv.p : null;
    myBans = names("mb").slice(0, 5);
    theirBans = names("tb").slice(0, 5);
    syncBans();
    myLane = LANES.indexOf(kv.l) >= 0 ? kv.l : null;
    pickOrder = ["first","mid","last"].indexOf(kv.o) >= 0 ? kv.o : "mid";
    return true;
  }catch(e){ return false; }
}
(function(){
  var sh = document.getElementById("shareDraft");
  if(sh) sh.onclick = function(){
    var url = location.href.split("#")[0] + draftHash();
    if(typeof navigator !== "undefined" && navigator.clipboard && navigator.clipboard.writeText){
      navigator.clipboard.writeText(url).then(function(){ cpkMsg("Draft link copied to clipboard."); },
        function(){ cpkMsg("Draft link: " + url); });
    } else cpkMsg("Draft link: " + url);
  };
  var ex = document.getElementById("exampleDraft");
  if(ex) ex.onclick = function(){
    myBans = ["Ling"]; theirBans = ["Saber", "Kaja"]; syncBans();
    enemies = ["Fanny", "Zetian", "Moskov"];
    team = ["Gloo"];
    myPick = null; buildView = null; myLane = null; pickOrder = "mid";
    render();
    cpkMsg("Example draft loaded — read their bans below, then the board.");
  };
})();''')

# ---------- 9. buy-order hint in lineupBuild + render ----------
rep('''  return { n: "⚡ vs this lineup", i: items, e: std.e, s: spell,
    w: head + " " + (why.join(" · ") || "") + " Updates as the draft changes." };''',
'''  var orderHint = picks.length
    ? "Buy order: after your 2nd damage item, grab the tier-1 defense component on the way (Leather Jerkin / Steel Legplates vs physical, the magic-resist component vs magic), finish your spike, then complete the defense item."
    : "";
  return { n: "⚡ vs this lineup", i: items, e: std.e, s: spell, o: orderHint,
    w: head + " " + (why.join(" · ") || "") + " Updates as the draft changes." };''')

rep('''        + '<div class="bp-items">'+its+'</div>'
        + '<div class="bp-loadout">'+em+sp+'</div></div>';''',
'''        + '<div class="bp-items">'+its+'</div>'
        + (b.o ? '<div class="bp-order">'+esc(b.o)+'</div>' : '')
        + '<div class="bp-loadout">'+em+sp+'</div></div>';''')

# ---------- 10. flex badges in 1st-pick mode ----------
rep('''          if(TIER[pick]==="D") metaBits.push('<span class="mb warn" title="measured bottom tier this patch (mlbb.io ranked data) — a hard counter on a losing hero still loses games, so it cannot take a medal">📉 weak meta</span>');''',
'''          if(TIER[pick]==="D") metaBits.push('<span class="mb warn" title="measured bottom tier this patch (mlbb.io ranked data) — a hard counter on a losing hero still loses games, so it cannot take a medal">📉 weak meta</span>');
          if(pickOrder === "first" && laneOf(pick).length >= 2) metaBits.push('<span class="mb" title="playable in '+laneOf(pick).length+' lanes — safe to lock before you see their answer">flex · '+laneOf(pick).join("/")+'</span>');''')

# ---------- 11. hash load on start ----------
rep('''renderTierSection();
applyMeasuredChips();''',
'''loadDraftHash();
renderTierSection();
applyMeasuredChips();''')

# ---------- 12. CSS ----------
rep('''@media (max-width:720px){
  .pad-vs{flex-direction:column;gap:10px;}''',
'''.banrow{display:flex;align-items:flex-start;gap:10px;margin-bottom:6px;}
.bside-lbl{flex:none;width:52px;font-size:10px;font-weight:700;letter-spacing:.08em;color:var(--muted);padding-top:30px;}
.bside-lbl.theirs{color:#c98a6a;}
.pad-actions{display:flex;gap:6px;}
.exbtn{background:var(--card2);border:1px solid var(--line);border-radius:8px;color:var(--gold);padding:3px 10px;cursor:pointer;font:inherit;font-size:12.5px;}
.exbtn:hover{border-color:var(--gold);}
.bi-row{padding:8px 14px;border-bottom:1px solid var(--line);font-size:13px;color:var(--fg);line-height:1.5;}
.bi-row:last-of-type{border-bottom:none;}
.bi-note{padding:9px 14px;font-size:12.5px;color:var(--gold);border-top:1px solid var(--line);}
.bp-order{font-size:11.5px;color:var(--muted);padding:2px 2px 4px;}
@media (max-width:720px){
  .pad-vs{flex-direction:column;gap:10px;}''')

open('template.html', 'w', encoding='utf-8').write(src)
print('v22 patch OK:', orig, '->', len(src))
