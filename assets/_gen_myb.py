#!/usr/bin/env python3
"""Generate MYB (Arena's take builds) for all 133 heroes and inject into template.html."""
import re, json
from collections import Counter

SRC = 'template.html'
src = open(SRC, encoding='utf-8').read()
js = src.split('<script>')[-1].split('</script>')[0]

def extract_var(name):
    m = re.search(r'var %s\s*=\s*\{' % name, js)
    assert m, name
    s = js.find('{', m.start()); d = 0
    for j in range(s, len(js)):
        if js[j] == '{': d += 1
        elif js[j] == '}':
            d -= 1
            if d == 0: return json.loads(js[s:j+1])
    raise ValueError(name)

BUILDS = extract_var('BUILDS')
ROLE   = extract_var('ROLE')
ISLUG  = extract_var('ISLUG')
SSLUG  = extract_var('SSLUG')
TAL    = extract_var('TAL')

SPECIAL = {"change":"Chang'e","popol-and-kupa":"Popol","mlbb-lapu":"Lapu-Lapu","mlbb-yi-sun":"Yi Sun-shin","MLBB Lapu":"Lapu-Lapu","MLBB Yi Sun":"Yi Sun-shin","x-borg":"X.Borg"}
def name_of(slug):
    if slug in SPECIAL: return SPECIAL[slug]
    return ' '.join(w[0].upper()+w[1:] for w in slug.split('-'))

BOOTS = {'Arcane Boots','Magic Boots','Demon Boots','Swift Boots','Rapid Boots','Warrior Boots','Tough Boots'}
MAGIC_DMG = {'Clock of Destiny','Holy Crystal','Blood Wings','Lightning Truncheon','Divine Glaive','Genius Wand','Glowing Wand','Ice Queen Wand','Wishing Lantern','Concentrated Energy','Fleeting Time','Enchanted Talisman','Feather of Heaven','Demon Boots','Arcane Boots'}
PHYS_DMG = {"Berserker's Fury",'Starlium Scythe','Sky Piercer','Blade of Despair','Blade of the Heptaseas','Corrosion Scythe','Demon Hunter Sword','Endless Battle','Golden Staff',"Haas's Claws",'Hunter Strike','Malefic Gun','Malefic Roar','War Axe','Great Dragon Spear','Windtalker','Sea Halberd'}

AT_MAGIC = ['Divine Glaive','Genius Wand','Wishing Lantern','Glowing Wand','Holy Crystal','Lightning Truncheon','Blood Wings','Concentrated Energy']
AT_MM    = ['Demon Hunter Sword','Malefic Gun','Malefic Roar','Sea Halberd','Golden Staff',"Blade of Despair","Haas's Claws"]
AT_FGT   = ['War Axe','Malefic Roar','Sea Halberd','Thunder Belt','Hunter Strike','Blade of Despair']
AT_ASN   = ['Malefic Roar','Hunter Strike','Sea Halberd','Blade of Despair','Blade of the Heptaseas']

DV_MAGIC = ['Winter Crown','Immortality',"Athena's Shield",'Radiant Armor']
DV_MM    = ['Wind of Nature','Immortality','Rose Gold Meteor']
DV_FGT   = ["Queen's Wings",'Immortality','Antique Cuirass',"Athena's Shield",'Brute Force Breastplate']
DV_ASN   = ["Queen's Wings",'Immortality','Blade of Despair','Hunter Strike']

TK_PHYS  = ['Antique Cuirass','Blade Armor','Dominance Ice','Immortality','Guardian Helmet','Brute Force Breastplate']
TK_MAGIC = ["Athena's Shield",'Radiant Armor','Oracle','Immortality','Guardian Helmet']

FILL = {
 'Mage': ['Enchanted Talisman','Glowing Wand','Divine Glaive','Holy Crystal','Lightning Truncheon','Ice Queen Wand'],
 'Marksman': ['Swift Boots','Windtalker',"Berserker's Fury",'Corrosion Scythe',"Haas's Claws",'Blade of Despair'],
 'Assassin': ['Swift Boots','Blade of the Heptaseas','Endless Battle','Blade of Despair','Hunter Strike','Sea Halberd'],
 'Fighter': ['Warrior Boots','War Axe','Endless Battle','Thunder Belt',"Queen's Wings",'Blade of Despair'],
 'Tank': ['Warrior Boots','Guardian Helmet','Antique Cuirass',"Athena's Shield",'Immortality','Cursed Helmet'],
 'Support': ['Tough Boots','Flask of the Oasis','Oracle','Immortality',"Athena's Shield",'Dominance Ice'],
}

STD_WHY = {
 'Mage': 'Consensus core refined — mana/CDR engine to never stop casting, damage online by mid-game.',
 'Marksman': 'Full damage curve in power-spike order — reach for this first; defense lives in the vs-dive build.',
 'Assassin': 'Snowball damage — you are the tempo threat; convert leads before late game.',
 'Fighter': 'Bruiser balance — damage to threaten carries, sustain to hold the lane.',
 'Tank': 'Balanced frontline — HP plus both resistances with aura pressure.',
 'Support': 'Utility core — keep the heal/shield engine rolling and peel for carries.',
}

def consensus(presets):
    freq = Counter(); pos = {}
    for b in presets:
        for idx, it in enumerate(b['i']):
            freq[it] += 1; pos.setdefault(it, []).append(idx)
    avg = {it: sum(l)/len(l) for it, l in pos.items()}
    return freq, avg

def make_standard(hero, presets, primary):
    freq, avg = consensus(presets)
    order = sorted(freq, key=lambda it: (-freq[it], avg[it]))
    chosen = order[:6]
    # enforce exactly one pair of boots: keep the most frequent
    boot_items = [it for it in chosen if it in BOOTS]
    if len(boot_items) > 1:
        keep = sorted(boot_items, key=lambda it: (-freq[it], avg[it]))[0]
        chosen = [it for it in chosen if it not in BOOTS or it == keep]
    order2 = [it for it in order if it not in chosen]
    for it in order2:
        if len(chosen) >= 6: break
        if it in BOOTS and any(x in BOOTS for x in chosen): continue
        chosen.append(it)
    chosen.sort(key=lambda it: avg.get(it, 9))
    for it in FILL.get(primary, []):
        if len(chosen) >= 6: break
        if it not in chosen and not (it in BOOTS and any(x in BOOTS for x in chosen)): chosen.append(it)
    return chosen[:6]

def dmg_type(presets):
    m = p = 0
    for b in presets:
        for it in b['i']:
            if it in MAGIC_DMG: m += 1
            elif it in PHYS_DMG: p += 1
    return 'magic' if m >= p else 'phys'

def dmg_core(standard):
    core = [it for it in standard if it not in BOOTS and (it in MAGIC_DMG or it in PHYS_DMG)]
    return (core[:2] if len(core) >= 2 else [it for it in standard if it not in BOOTS][:2])

def variant(boots, core, pool, fill_primary):
    items = [boots] + core[:]
    for it in pool:
        if len(items) >= 6: break
        if it not in items: items.append(it)
    for it in FILL.get(fill_primary, []):
        if len(items) >= 6: break
        if it not in items: items.append(it)
    return items[:6]

MYB = {}
for slug, presets in BUILDS.items():
    hero = name_of(slug)
    role = ROLE.get(hero, '')
    primary = role.split('·')[0].strip()
    tanky = primary in ('Tank', 'Support')
    dmg = dmg_type(presets)
    std = make_standard(hero, presets, primary)
    std_boots = next((it for it in std if it in BOOTS), 'Warrior Boots')
    spell = Counter(b.get('s','') for b in presets).most_common(1)[0][0]
    if 'Jungle' in role and spell != 'Retribution': spell = 'Retribution'
    emblem = TAL.get(hero, [None])[0] or Counter(b.get('e','') for b in presets).most_common(1)[0][0]

    builds = []
    if not tanky:
        at_pool = AT_MAGIC if dmg == 'magic' else {'Marksman': AT_MM, 'Fighter': AT_FGT}.get(primary, AT_ASN)
        dv_pool = DV_MAGIC if dmg == 'magic' else {'Marksman': DV_MM, 'Fighter': DV_FGT}.get(primary, DV_ASN)
        core = dmg_core(std)
        at = variant(std_boots, core, at_pool, primary)
        dv = variant(std_boots, core, dv_pool, primary)
        dv_spell = 'Purify' if (spell == 'Flicker' and primary in ('Mage','Marksman')) else spell
        at_w = ('Genius Wand shreds MR while Divine Glaive/Wishing Lantern burn %HP — use vs 2+ frontliners or sustain-heavy comps.'
                if dmg=='magic' else
                ('%HP on-hit plus armor pen cuts through stacking tanks — use vs 2+ frontliners.' if primary=='Marksman' else
                 ('Pen stacks in extended trades plus anti-heal to cap their sustain — use vs tanky comps.' if primary=='Fighter' else
                  'Armor pen and anti-heal so tanks cannot ignore you in fights — use vs 2+ frontliners.')))
        dv_w = ('Winter Crown stasis and Immortality answer the dive; Purify if they chain CC — vs assassin/burst comps.'
                if dmg=='magic' else
                ('Wind of Nature phases out the physical dive, Immortality buys a second life — vs assassins and burst.' if primary=='Marksman' else
                 ('Fight through the dive — dueling survivability so their assassins cannot hunt you for free.' if primary=='Assassin' else
                  "Queen's Wings and armor let you front-line without exploding — vs dive and burst comps.")))
        builds = [
            {'n':'Arena Standard','i':std,'e':emblem,'s':spell,'w':STD_WHY[primary]},
            {'n':'vs Tanks & Sustain','i':at,'e':emblem,'s':spell,'w':at_w},
            {'n':'vs Dive & Burst','i':dv,'e':emblem,'s':dv_spell,'w':dv_w},
        ]
    else:
        core = [it for it in std if it not in BOOTS][:2]
        vp_boots = std_boots if std_boots == 'Warrior Boots' else 'Warrior Boots'
        vm_boots = std_boots if std_boots == 'Tough Boots' else 'Tough Boots'
        vp = variant(vp_boots, core, TK_PHYS, primary)
        vm = variant(vm_boots, core, TK_MAGIC, primary)
        builds = [
            {'n':'Arena Standard','i':std,'e':emblem,'s':spell,'w':STD_WHY[primary]},
            {'n':'vs Physical','i':vp,'e':emblem,'s':spell,'w':'Armor, reflect and attack-speed slow vs 3+ physical threats (fighters, jungle, marksman).'},
            {'n':'vs Magic','i':vm,'e':emblem,'s':('Purify' if spell=='Flicker' else spell),'w':'MR plus regen vs double mage or heavy magic poke; Tough Boots for the CC.'},
        ]
    MYB[hero] = builds

# ---- flagship override: my exact chat build for Zetian ----
zet = MYB['Zetian']
zet[0] = {'n':'Arena Standard','i':['Magic Boots','Enchanted Talisman','Glowing Wand','Fleeting Time','Divine Glaive','Concentrated Energy'],'e':'Mage','s':'Flicker',
          'w':'The engine, not the nuke — Talisman fixes her S1 mana, Fleeting Time snowballs the global ult, spell vamp caps the poke war.'}
MYB['Zetian'] = zet

# ---- validation ----
assert set(MYB) == set(ROLE), (set(MYB) ^ set(ROLE))
for hero, bs in MYB.items():
    assert len(bs) == 3, hero
    for b in bs:
        assert len(b['i']) == 6, (hero, b['n'], b['i'])
        assert len(set(b['i'])) == 6, (hero, b['n'], b['i'])
        assert sum(1 for it in b['i'] if it in BOOTS) == 1, (hero, b['n'], b['i'])
        for it in b['i']: assert it in ISLUG, (hero, it)
        assert b['s'] in SSLUG, (hero, b['s'])
        assert b['e'] in ('Assassin','Basic Common','Fighter','Mage','Marksman','Support','Tank'), (hero, b['e'])
    assert len({tuple(b['i']) for b in bs}) == 3, hero  # three distinct builds
    primary = ROLE[hero].split('·')[0].strip()
    if primary in ('Tank','Support'):
        assert bs[1]['n'] == 'vs Physical' and bs[2]['n'] == 'vs Magic'
    else:
        assert bs[1]['n'] == 'vs Tanks & Sustain' and bs[2]['n'] == 'vs Dive & Burst'
        if primary in ('Mage','Marksman'):
            def_items = {"Winter Crown","Immortality","Athena's Shield",'Radiant Armor','Wind of Nature','Rose Gold Meteor'}
            assert any(it in def_items for it in bs[2]['i']), hero
# Zetian flagship exact
assert MYB['Zetian'][0]['i'] == ['Magic Boots','Enchanted Talisman','Glowing Wand','Fleeting Time','Divine Glaive','Concentrated Energy']
json.dump(MYB, open('_myb.json','w'), ensure_ascii=False)
myb_js = 'var MYB = ' + json.dumps(MYB, ensure_ascii=False, separators=(',',':')) + ';\n'

# ---- inject MYB before var ISLUG ----
assert 'var MYB' not in js
marker = 'var ISLUG'
assert marker in src
src = src.replace(marker, myb_js + marker, 1)

# ---- patch buildPanelHtml: presets label + Arena section ----
old_ret = "  return head + talRow + bHtml + pickline + situationalHtml() + '</div>';"
assert src.count(old_ret) == 1
new_ret = """  var srcH = bs.length ? '<div class="bp-srch">\\U0001F4D8 Community presets — MLBBHub hero-guide builds</div>' : '';
  var my = MYB[hero] || [];
  var myHtml = '';
  if(my.length){
    myHtml = '<div class="bp-arena"><div class="bp-blabel arena-h">\\U0001F9E0 Arena\\'s take <span class="arena-sub">— our situational builds, synthesized per matchup (on top of the presets above)</span></div>' + my.map(function(b){
      var its = b.i.map(function(it, idx){
        var ic = ISLUG[it] ? '<i class="ic '+ISLUG[it]+'"></i>' : '<i class="ic noic"></i>';
        return '<span class="itemchip" title="'+esc(it)+'">'+ic+'<b>'+(idx+1)+'</b>'+esc(it)+'</span>';
      }).join('<span class="iarrow">\\u2192</span>');
      var em = b.e ? '<span class="lo-sm">'+(ESLUG[b.e]?'<i class="ic '+ESLUG[b.e]+'"></i>':'')+esc(b.e)+' emblem</span>' : '';
      var sp = b.s ? '<span class="lo-sm">'+(SSLUG[b.s]?'<i class="ic sp '+SSLUG[b.s]+'"></i>':'')+esc(b.s)+'</span>' : '';
      return '<div class="bp-build arena-b"><div class="bp-blabel">'+esc(b.n)+'</div>'
        + '<div class="bp-awhy">'+esc(b.w)+'</div>'
        + '<div class="bp-items">'+its+'</div>'
        + '<div class="bp-loadout">'+em+sp+'</div></div>';
    }).join('') + '</div>';
  }
  return head + talRow + srcH + bHtml + pickline + myHtml + situationalHtml() + '</div>';"""
src = src.replace(old_ret, new_ret, 1)

# ---- CSS before .bp-sit{ ----
css_anchor = '.bp-sit{'
assert css_anchor in src
css = """.bp-srch{font-size:11px;color:var(--muted);margin:8px 0 2px;letter-spacing:.02em;}
.bp-arena{margin-top:12px;border-top:2px dashed var(--line);padding-top:4px;}
.arena-h{color:#8f7ff0;}
.arena-sub{font-size:11px;color:var(--muted);font-weight:400;}
.bp-awhy{font-size:11px;color:var(--muted);margin:2px 0 6px;line-height:1.5;}
.arena-b .bp-blabel{color:#b0a6e8;}
"""
src = src.replace(css_anchor, css + css_anchor, 1)

# ---- update panel note ----
m = re.search(r'Builds and emblem-talent setups are MLBBHub hero-guide presets[^<]*', src)
assert m, 'note not found'
src = src.replace(m.group(0),
 "Builds: community presets (MLBBHub, 3 per hero in buy order) plus <b>Arena&#39;s take</b> — our own situational builds for every hero (a refined standard, and variants vs tanks/sustain, dive/burst, or physical/magic comps), synthesized from preset consensus + matchup itemization; not scraped from any site. Emblem-talent setups are MLBBHub defaults.")

open(SRC, 'w', encoding='utf-8').write(src)
print("MYB heroes:", len(MYB))
print("template.html bytes:", len(src.encode('utf-8')))
print("Zetian std:", MYB['Zetian'][0]['i'])
print("Tigreal:", [b['n'] for b in MYB['Tigreal']], MYB['Tigreal'][1]['i'])
print("Miya vs dive:", MYB['Miya'][2]['i'])
print("Ling vs tanks:", MYB['Ling'][1]['i'])
print("Estes vs phys:", MYB['Estes'][1]['i'])
