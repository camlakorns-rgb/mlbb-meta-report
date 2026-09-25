#!/usr/bin/env python3
"""v20 JS rework: replace enemy/team/ban input systems with the slot editor."""
src = open('template.html', encoding='utf-8').read()
orig = len(src)
def rep(old, new, expect=1):
    global src
    n = src.count(old)
    assert n == expect, 'count %d != %d: %r' % (n, expect, old[:70])
    src = src.replace(old, new)
def span_replace(startmark, endmark, new):
    global src
    i = src.find(startmark); j = src.find(endmark, i + 1)
    assert i > 0 and j > i, 'span not found: %r .. %r' % (startmark[:50], endmark[:50])
    src = src[:i] + new + src[j:]

# --- 1. drop dead enemy-input vars (keep quickEl/emptyEl/resEl) ---
rep('''var input = document.getElementById("cpkInput");
var drop = document.getElementById("cpkDrop");
var chipsEl = document.getElementById("enemyChips");
var quickEl''', '''var quickEl''')

# --- 2. dropKeys line (popRank right after survives) ---
rep('''var dropKeys = [], selIdx = 0;
function popRank''', '''function popRank''')

# --- 3. remove enemy dropdown system ---
span_replace('function showDrop(q){', '/* ---- add/remove enemies ---- */',
             '/* hero picker lives in the slot editor below (v20) */\n')

# --- 4. addEnemy: strip old input DOM lines ---
rep('''  enemies.push(name);
  input.value = "";
  drop.style.display = "none";
  cpkMsg("");
  render();''',
'''  enemies.push(name);
  cpkMsg("");
  render();''')

# --- 5. replace team+ban input systems with the slot editor ---
NEWBLOCK = '''/* ================= SLOT EDITOR (v20) ================= */
var bans = [];       /* up to 10 */
function addTeam(name){
  if(team.indexOf(name)>=0) return;
  if(enemies.indexOf(name)>=0){ cpkMsg(name+" is on the enemy team."); return; }
  if(myPick===name){ cpkMsg(name+" is already your pick."); return; }
  if(bans.indexOf(name)>=0){ cpkMsg(name+" is banned in this draft."); return; }
  if(team.length>=4){ cpkMsg("Max 4 teammates — you are the 5th."); return; }
  team.push(name); cpkMsg(""); render();
}
function removeTeam(name){ team = team.filter(function(t){return t!==name;}); render(); }
function addBan(name){
  if(bans.indexOf(name)>=0) return;
  if(enemies.indexOf(name)>=0){ cpkMsg(name+" is on the enemy team."); return; }
  if(team.indexOf(name)>=0){ cpkMsg(name+" is on your team."); return; }
  if(myPick===name){ cpkMsg(name+" is your locked pick."); return; }
  if(bans.length>=10){ cpkMsg("Max 10 bans (5 per side)."); return; }
  bans.push(name); cpkMsg(""); render();
}
function removeBan(name){ bans = bans.filter(function(b){return b!==name;}); render(); }

var picker = { open:false, kind:null, idx:-1, keys:[], sel:0 };
function slotOccupant(kind, idx){
  if(kind === "enemy") return enemies[idx] || null;
  if(kind === "ban") return bans[idx] || null;
  if(kind === "you") return myPick;
  if(kind === "team") return team[idx] || null;
  return null;
}
function pickerTitleFor(kind){
  return kind === "enemy" ? "ADD AN ENEMY" : kind === "ban" ? "ADD A BAN"
    : kind === "you" ? "YOUR PICK — YOU" : "ADD A TEAMMATE";
}
function openPicker(kind, idx){
  picker.open = true; picker.kind = kind; picker.idx = (typeof idx === "number") ? idx : -1;
  cpkMsg("");
  var pt = document.getElementById("pickerTitle");
  if(pt) pt.textContent = pickerTitleFor(kind);
  var pi = document.getElementById("pickerInput");
  if(pi){ pi.value = ""; if(pi.focus) pi.focus(); }
  var pk = document.getElementById("slotPicker");
  if(pk) pk.classList.add("open");
  renderPicker("");
  placePicker();
}
function closePicker(){
  picker.open = false;
  var pk = document.getElementById("slotPicker");
  if(pk) pk.classList.remove("open");
}
function placePicker(){
  var pk = document.getElementById("slotPicker");
  if(!pk || !pk.classList.contains("open") || !document.querySelector) return;
  var slot = document.querySelector('.dslot[data-k="'+picker.kind+'"][data-i="'+picker.idx+'"]');
  if(!slot || !slot.getBoundingClientRect) return;
  var r = slot.getBoundingClientRect();
  var vw = (window && window.innerWidth) ? window.innerWidth : 1280;
  var w = 308;
  pk.style.left = Math.max(8, Math.min(r.left, vw - w - 8)) + "px";
  pk.style.top = (r.bottom + 6) + "px";
}
function renderPicker(q){
  q = (q || "").toLowerCase().trim();
  var listEl = document.getElementById("pickerList");
  if(!listEl) return;
  var cur = slotOccupant(picker.kind, picker.idx);
  var taken = enemies.concat(team, myPick ? [myPick] : [], bans);
  if(cur) taken = taken.filter(function(h){ return h !== cur; });
  var keys = Object.keys(DB).filter(function(k){
    return taken.indexOf(k) < 0 && (q === "" || k.toLowerCase().indexOf(q) >= 0);
  });
  keys.sort(function(a, b){
    var qa = q === "" ? 0 : (a.toLowerCase().indexOf(q) === 0 ? 0 : 1);
    var qb = q === "" ? 0 : (b.toLowerCase().indexOf(q) === 0 ? 0 : 1);
    return (qa - qb) || (popRank(a) - popRank(b)) || a.localeCompare(b);
  });
  picker.keys = keys.slice(0, 10);
  picker.sel = 0;
  var html = "";
  if(cur){
    html += '<div class="cur-row"><button class="cbtn" data-act="view" data-h="'+esc(cur)+'">View '+esc(cur)+' build</button><button class="cbtn" data-act="remove" data-h="'+esc(cur)+'">Remove</button></div>';
  }
  html += picker.keys.map(function(k, i){
    var label = esc(k);
    if(q){
      var pos = k.toLowerCase().indexOf(q);
      if(pos >= 0) label = esc(k.slice(0, pos))+"<b>"+esc(k.slice(pos, pos+q.length))+"</b>"+esc(k.slice(pos+q.length));
    }
    var tb = TIER[k] ? '<span class="tb tb-'+TIER[k]+'">'+TIER[k]+'</span>' : '';
    return '<div class="cpk-opt" data-pi="'+i+'" data-h="'+esc(k)+'">'+avatar(k)+'<span>'+label+'</span><span class="ro">'+(ROLE[k] || "")+'</span>'+tb+'</div>';
  }).join("");
  if(!picker.keys.length && !cur) html = '<div class="cpk-empty" style="margin:10px 12px;">No heroes match — check the spelling.</div>';
  listEl.innerHTML = html;
  paintPickerSel();
}
function paintPickerSel(){
  var listEl = document.getElementById("pickerList");
  if(!listEl || !listEl.querySelectorAll) return;
  Array.prototype.forEach.call(listEl.querySelectorAll(".cpk-opt"), function(el){
    if(parseInt(el.getAttribute("data-pi"), 10) === picker.sel) el.classList.add("sel");
    else el.classList.remove("sel");
  });
}
function pickSlotHero(name){
  var kind = picker.kind, idx = picker.idx;
  var cur = slotOccupant(kind, idx);
  closePicker();
  if(cur === name){ render(); return; }
  if(bans.indexOf(name) >= 0){ cpkMsg(name+" is banned in this draft."); return; }
  if(enemies.indexOf(name) >= 0){ cpkMsg(name+" is already an enemy pick."); return; }
  if(team.indexOf(name) >= 0){ cpkMsg(name+" is already on your team."); return; }
  if(myPick === name){ cpkMsg(name+" is your locked pick."); return; }
  if(kind === "enemy"){
    if(idx >= 0 && idx < enemies.length) enemies[idx] = name;
    else if(enemies.length < 5) enemies.push(name);
  } else if(kind === "ban"){
    if(idx >= 0 && idx < bans.length) bans[idx] = name;
    else if(bans.length < 10) bans.push(name);
  } else if(kind === "you"){
    myPick = name; buildView = null;
  } else {
    if(idx >= 0 && idx < team.length) team[idx] = name;
    else if(team.length < 4) team.push(name);
  }
  cpkMsg("");
  render();
}
function removeSlot(kind, idx){
  var cur = slotOccupant(kind, idx);
  if(cur === null || cur === undefined) return;
  if(kind === "enemy") removeEnemy(cur);
  else if(kind === "ban") removeBan(cur);
  else if(kind === "you"){ myPick = null; render(); }
  else removeTeam(cur);
}
function slotHtml(kind, idx, h){
  if(h){
    var tag = kind === "you" ? '<span class="stag">YOU</span>' : '<span class="srole">'+esc(kind === "ban" ? "ban" : (ROLE[h] || ""))+'</span>';
    return '<button class="dslot filled '+kind+'" data-k="'+kind+'" data-i="'+idx+'" title="'+esc(h)+' — click to replace or view its build">'
      + avatar(h) + '<span class="sname">'+esc(h)+'</span>' + tag
      + '<span class="sx" data-x="1" title="Remove '+esc(h)+'">✕</span></button>';
  }
  var hint = kind === "you" ? "lock YOUR pick" : kind === "ban" ? "add ban" : kind === "enemy" ? "add enemy" : "add teammate";
  return '<button class="dslot empty '+kind+'" data-k="'+kind+'" data-i="'+idx+'" title="'+hint+'"><span class="plus">+</span><span class="shint">'+hint+'</span></button>';
}
function wireSlots(containerEl){
  if(!containerEl || !containerEl.querySelectorAll) return;
  Array.prototype.forEach.call(containerEl.querySelectorAll(".dslot"), function(el){
    el.onclick = function(ev){
      var kind = el.getAttribute("data-k");
      var idx = parseInt(el.getAttribute("data-i"), 10);
      if(ev && ev.target && ev.target.getAttribute && ev.target.getAttribute("data-x")){ removeSlot(kind, idx); return; }
      openPicker(kind, idx);
    };
  });
}
function renderSlots(){
  var banEl = document.getElementById("banSlots");
  var teamEl = document.getElementById("teamSlots");
  var enEl = document.getElementById("enemySlots");
  var html, i;
  if(banEl){
    html = bans.map(function(b, i2){ return slotHtml("ban", i2, b); }).join("");
    if(bans.length < 10) html += slotHtml("ban", -1, null);
    banEl.innerHTML = html;
    wireSlots(banEl);
  }
  if(teamEl){
    html = slotHtml("you", 0, myPick);
    for(i = 0; i < team.length; i++) html += slotHtml("team", i, team[i]);
    if(team.length < 4) html += slotHtml("team", team.length, null);
    teamEl.innerHTML = html;
    wireSlots(teamEl);
  }
  if(enEl){
    html = "";
    for(i = 0; i < 5; i++) html += slotHtml("enemy", i, enemies[i] || null);
    enEl.innerHTML = html;
    wireSlots(enEl);
  }
  if(quickEl && quickEl.querySelectorAll){
    Array.prototype.forEach.call(quickEl.querySelectorAll("button"), function(b){
      var qh = b.getAttribute("data-h");
      if(!qh) return;
      if(enemies.indexOf(qh) >= 0) b.classList.add("on"); else b.classList.remove("on");
      if(bans.indexOf(qh) >= 0) b.classList.add("banned"); else b.classList.remove("banned");
    });
  }
}
(function(){
  var pi = document.getElementById("pickerInput");
  if(pi){
    pi.addEventListener("input", function(){ renderPicker(pi.value); });
    pi.addEventListener("keydown", function(e){
      if(e.key === "ArrowDown"){ if(picker.keys.length){ picker.sel = Math.min(picker.sel + 1, picker.keys.length - 1); paintPickerSel(); } e.preventDefault(); }
      else if(e.key === "ArrowUp"){ picker.sel = Math.max(picker.sel - 1, 0); paintPickerSel(); e.preventDefault(); }
      else if(e.key === "Enter"){ if(picker.keys[picker.sel]) pickSlotHero(picker.keys[picker.sel]); e.preventDefault(); }
      else if(e.key === "Escape"){ closePicker(); }
    });
  }
  var pc = document.getElementById("pickerClose");
  if(pc) pc.onclick = function(){ closePicker(); };
  var pl = document.getElementById("pickerList");
  if(pl){
    pl.addEventListener("click", function(e){
      var t = e.target;
      if(!t || !t.closest) return;
      var opt = t.closest(".cpk-opt");
      if(opt){ pickSlotHero(opt.getAttribute("data-h")); return; }
      var cb = t.closest(".cbtn");
      if(cb){
        var act = cb.getAttribute("data-act");
        var kind = picker.kind, idx = picker.idx;
        closePicker();
        if(act === "view"){ buildView = cb.getAttribute("data-h"); render(); }
        else if(act === "remove"){ removeSlot(kind, idx); }
      }
    });
  }
  document.addEventListener("click", function(e){
    if(!picker.open) return;
    var t = e.target;
    if(t && t.closest && !t.closest("#slotPicker") && !t.closest(".dslot")) closePicker();
  });
})();

'''
span_replace('var teamInput = document.getElementById("teamInput");', 'function lockPick(name){', NEWBLOCK)

# --- 6. clearDraft strip FIRST (contains a teamMsg call) ---
rep('''  enemies = []; team = []; myPick = null; bans = []; buildView = null;
  input.value = ""; drop.style.display = "none"; cpkMsg("");
  if(teamInput){ teamInput.value = ""; teamDrop.style.display = "none"; teamMsg(""); }
  if(banInput){ banInput.value = ""; banDrop.style.display = "none"; banMsgEl.textContent = ""; banMsgEl.style.display = "none"; }
  render();''',
'''  enemies = []; team = []; myPick = null; bans = []; buildView = null;
  closePicker(); cpkMsg("");
  render();''')

# --- 7. lockPick: teamMsg -> cpkMsg (exactly 3 remain) ---
n = src.count('teamMsg(')
assert n == 3, 'lockPick teamMsg count %d' % n
src = src.replace('teamMsg(', 'cpkMsg(')

# --- 8. render(): chip rendering -> slot rendering ---
span_replace('  /* team chips: teammates + your locked pick */', '  var draftStarted',
'''  /* draft slots (v20) */
  renderSlots();

''')

open('template.html', 'w', encoding='utf-8').write(src)
print('JS rework OK:', orig, '->', len(src), 'bytes')
