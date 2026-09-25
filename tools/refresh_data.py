#!/usr/bin/env python3
"""
refresh_data.py — MLBB Meta Report data refresh pipeline.

Crawls MLBBHub (mlbbhub.com) hero pages, parses the embedded RSC/flight data,
and rebuilds the draft-engine data layers inside index.html:

  STATS   [winRate, pickRate%, banRate%]            (from hero page current stats)
  MEAS    enemy -> [[counter, edge_pp], ...]         (from countersThisHero.advantagePp)
  ROLE    "Role · Lane1, Lane2"                      (from role[] + lane[], primary lane first)
  TIERHUB hub tier letters                           (from hero.tier, for disagreement arrows)
  POP     top-30 most-picked hero names              (from pickRate)
  DB      enemy -> {c:[[pick, reason, w], ...],      (rebuilt from measured edges;
            avoid:[prey...], tip:"..."}              curated reasons/tips preserved & reused)

Kept as-is (not refreshed here): KITS, MYB (curated builds), TAL/TSLUG, SYN (measured
duo WR from the 2.1.95 crawl — the hub's synergyScore is a constant editorial 8),
HMM (hmmsucks expert tiers), DIFF*/comfort lists.

Usage:
  python3 tools/refresh_data.py --crawl  [--crawl-dir DIR]   # fetch hero pages (~90 MB)
  python3 tools/refresh_data.py --build  [--crawl-dir DIR]   # parse -> data/meta-*.json
  python3 tools/refresh_data.py --write-html [--crawl-dir DIR] [--index PATH]
                                                           # splice fresh layers into index.html
  --crawl implies --build; --write-html implies --build.
"""
import argparse, json, os, re, sys, time, urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
HEROES_INDEX = "https://mlbbhub.com/heroes"
HERO_URL = "https://mlbbhub.com/heroes/{slug}"

# site slug -> display name overrides (everything else uses the site's own name)
NAME_MAP = {"popol-and-kupa": "Popol"}

# layer var names we refresh inside index.html
LAYERS = ["STATS", "MEAS", "ROLE", "TIERHUB", "POP", "DB"]


# --------------------------------------------------------------------------- io
def fetch(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def balanced(s, i):
    """Return the balanced {...} / [...] substring of s starting at s[i]."""
    depth = 0; instr = False; esc = False
    for j in range(i, len(s)):
        ch = s[j]
        if instr:
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == '"': instr = False
        else:
            if ch == '"': instr = True
            elif ch in "{[": depth += 1
            elif ch in "}]":
                depth -= 1
                if depth == 0: return s[i:j + 1]
    raise ValueError("unbalanced structure at offset %d" % i)


# ------------------------------------------------------------------------ crawl
def get_slugs():
    html = fetch(HEROES_INDEX).decode("utf-8", "replace")
    slugs = sorted(set(re.findall(r'href="/heroes/([a-z0-9-]+)"', html)))
    return [s for s in slugs if s not in ("tier-list-maker",)]


def cmd_crawl(crawl_dir):
    os.makedirs(crawl_dir, exist_ok=True)
    slugs = get_slugs()
    print("hero slugs:", len(slugs))
    n = 0
    for i, slug in enumerate(slugs):
        out = os.path.join(crawl_dir, slug + ".html")
        if os.path.exists(out) and os.path.getsize(out) > 50000:
            n += 1
            continue
        try:
            data = fetch(HERO_URL.format(slug=slug))
            with open(out, "wb") as f:
                f.write(data)
            n += 1
        except Exception as e:
            print("  FAIL %s: %s" % (slug, e))
        if (i + 1) % 20 == 0:
            print("  %d/%d" % (i + 1, len(slugs)))
        time.sleep(0.2)
    print("crawled %d/%d pages -> %s" % (n, len(slugs), crawl_dir))


# ------------------------------------------------------------------------ parse
def flight_payload(path):
    html = open(path, encoding="utf-8", errors="replace").read()
    chunks = re.findall(r'self\.__next_f\.push\(\[1,\s*"((?:[^"\\]|\\.)*)"\]\)', html)
    return "".join(json.loads('"%s"' % c) for c in chunks)


def parse_page(path):
    joined = flight_payload(path)
    m = re.search(r'"hero":\{"id":', joined)
    if not m:
        raise ValueError("no hero object")
    hero = json.loads(balanced(joined, joined.index("{", m.start())))
    out = {
        "name": NAME_MAP.get(hero["slug"], hero["name"]),
        "slug": hero["slug"],
        "role": hero.get("role", []),
        "lanes": hero.get("lane", []),
        "tier": hero.get("tier"),
        "difficulty": hero.get("difficulty"),
        "winRate": hero.get("winRate"),
        "pickRate": hero.get("pickRate"),
        "banRate": hero.get("banRate"),
    }
    mh = re.search(r'"statsHistory":\[\{', joined)
    if mh:
        hist = json.loads(balanced(joined, joined.index("[", mh.start())))
        out["stats_date"] = hist[-1]["date"] if hist else None
    mc = re.search(r'"countersThisHero":\[\{', joined)
    arr = json.loads(balanced(joined, joined.index("[", mc.start()))) if mc else []
    out["counters"] = [{"name": NAME_MAP.get(x["heroSlug"], x["heroName"]),
                        "pp": round(x["advantagePp"], 2)} for x in arr]
    return out


def cmd_build(crawl_dir, snapshot_out):
    pages = sorted(f for f in os.listdir(crawl_dir) if f.endswith(".html"))
    parsed = {}
    for f in pages:
        try:
            parsed[f[:-5]] = parse_page(os.path.join(crawl_dir, f))
        except Exception as e:
            print("  parse FAIL %s: %s" % (f, e))
    print("parsed %d heroes" % len(parsed))
    if len(parsed) < 100:
        sys.exit("too few heroes parsed — aborting")

    dates = [v.get("stats_date") for v in parsed.values() if v.get("stats_date")]
    stats_date = max(dates) if dates else None
    snapshot = {"source": "mlbbhub.com hero pages",
                "crawled_at": time.strftime("%Y-%m-%d"),
                "stats_date": stats_date,
                "heroes": parsed}
    os.makedirs(os.path.dirname(snapshot_out), exist_ok=True)
    with open(snapshot_out, "w") as f:
        json.dump(snapshot, f, separators=(",", ":"))
    print("wrote %s (%d KB), stats_date=%s" %
          (snapshot_out, os.path.getsize(snapshot_out) // 1024, stats_date))
    return snapshot


# ------------------------------------------------------------- layer generation
def js_str(s):
    return json.dumps(s, ensure_ascii=False)


def gen_layers(snapshot, old):
    """Return {LAYER: js_literal_string} using old layers for curation reuse."""
    heroes = snapshot["heroes"]
    names = {v["name"] for v in heroes.values()}
    db_names = set(old["db"].keys())
    missing = db_names - names
    if missing:
        print("  WARN: heroes in DB but not in fresh crawl:", sorted(missing))

    # STATS
    stats = {v["name"]: [round(v["winRate"], 2), round(v["pickRate"], 2), round(v["banRate"], 2)]
             for v in heroes.values() if v["name"] in db_names}
    layer_stats = json.dumps(stats, separators=(",", ":"), ensure_ascii=False)

    # MEAS — enemy -> [[counter, pp]] (top 8, pp >= 1.0, keep >=5)
    meas = {}
    for v in heroes.values():
        h = v["name"]
        if h not in db_names:
            continue
        cs = [c for c in v["counters"] if c["name"] in db_names]
        keep = [c for c in cs if c["pp"] >= 1.0][:8]
        if len(keep) < 5:
            keep = cs[:5]
        meas[h] = [[c["name"], round(c["pp"], 1)] for c in keep]
    layer_meas = json.dumps(meas, separators=(",", ":"), ensure_ascii=False)

    # ROLE — "Role · Lane1, Lane2" (primary first)
    role = {}
    for v in heroes.values():
        h = v["name"]
        if h not in db_names or not v["lanes"] or not v["role"]:
            continue
        role[h] = "%s · %s" % (v["role"][0], ", ".join(v["lanes"]))
    layer_role = json.dumps(role, separators=(",", ":"), ensure_ascii=False)

    # TIERHUB
    tierhub = {v["name"]: v["tier"] for v in heroes.values() if v["name"] in db_names}
    layer_tierhub = "{\n" + ",\n".join(' "%s":"%s"' % (k, tierhub[k]) for k in sorted(tierhub, key=str.lower)) + "\n}"

    # POP — top 30 by pick rate
    by_pick = sorted((v for v in heroes.values() if v["name"] in db_names),
                     key=lambda v: -v["pickRate"])
    layer_pop = json.dumps([v["name"] for v in by_pick[:30]], ensure_ascii=False)

    # DB — counters with reasons + avoid (measured prey) + old tips
    # reverse index: hero -> [(enemy_that_they_counter... wait: rev[x] = [(h, pp)] means x counters h
    rev = {}
    for h, edges in meas.items():
        for cname, pp in edges:
            rev.setdefault(cname, []).append([h, pp])   # cname counters h with edge pp
    role_lookup = {v["name"]: (v["role"][0] if v["role"] else "", v["lanes"]) for v in heroes.values()}

    ROLE_LABEL = {"Fighter": "fighter-class", "Tank": "tank", "Marksman": "marksman",
                  "Assassin": "assassin", "Mage": "mage", "Support": "support"}

    def fresh_reason(counter, enemy, pp):
        cr, clanes = role_lookup.get(counter, ("", []))
        elanes = role_lookup.get(enemy, ("", []))[1]
        if elanes and clanes and clanes[0] == elanes[0]:
            head = "Same-lane answer"
        elif cr:
            head = "Best %s answer" % ROLE_LABEL.get(cr, cr.lower())
        else:
            head = "Ranked answer"
        return "%s — measured +%.1f pp WR edge" % (head, pp)

    db_out = {}
    old_db = old["db"]
    for h in sorted(db_names, key=str.lower):
        edges = meas.get(h, [])
        old_entry = old_db.get(h, {})
        old_c = {row[0]: row[1] for row in old_entry.get("c", [])}
        c_list = []
        for cname, pp in edges:
            reason = old_c.get(cname) or fresh_reason(cname, h, pp)
            w = 3 if pp >= 2.5 else (2 if pp >= 1.8 else 1)
            c_list.append([cname, reason, w])
        # avoid = measured prey (heroes this enemy counters), old avoid as fallback filler
        prey = sorted(rev.get(h, []), key=lambda x: -x[1])
        avoid, seen = [], set()
        for cname, pp in prey:
            if pp >= 1.0 and cname not in seen:
                avoid.append(cname); seen.add(cname)
            if len(avoid) >= 5:
                break
        for a in old_entry.get("avoid", []):
            if len(avoid) >= 6:
                break
            if a in db_names and a not in seen:
                avoid.append(a); seen.add(a)
        entry = {"c": c_list, "avoid": avoid}
        if old_entry.get("tip"):
            entry["tip"] = old_entry["tip"]
        db_out[h] = entry

    # serialize DB in old style: quoted keys, unquoted c/avoid/tip identifiers
    parts = []
    for h, e in db_out.items():
        c_js = ",".join("[%s,%s,%d]" % (js_str(p), js_str(r), w) for p, r, w in e["c"])
        av_js = ",".join(js_str(a) for a in e["avoid"])
        tip_js = (',"tip":%s' % js_str(e["tip"])) if e.get("tip") else ""
        parts.append('%s:{c:[%s],avoid:[%s]%s}' % (js_str(h), c_js, av_js, tip_js))
    layer_db = "{" + ",".join(parts) + "}"

    return {"STATS": layer_stats, "MEAS": layer_meas, "ROLE": layer_role,
            "TIERHUB": layer_tierhub, "POP": layer_pop, "DB": layer_db}


# ------------------------------------------------------------------ html splice
def grab_span(js, name):
    """Locate 'var NAME = <literal>' in js; return (start_of_literal, end_index_inclusive)."""
    m = re.search(r'var %s = ' % re.escape(name), js)
    if not m:
        raise ValueError("var %s not found" % name)
    i = m.end()
    opener = js[i]
    if opener not in "{[":
        raise ValueError("var %s does not start a literal" % name)
    lit = balanced(js, i)
    end = i + len(lit)
    if end < len(js) and js[end] == ";":
        end += 1
    return i, end


def parse_old_layers(index_path):
    js = open(index_path, encoding="utf-8").read()
    def grab_obj(name):
        i, e = grab_span(js, name)
        lit = js[i:e].rstrip(";")
        return lit
    # old DB / others: parse with a tolerant JSON-ish loader (unquoted c/avoid/tip keys)
    def tolerant(text):
        t = re.sub(r'(?<=[{,])(c|avoid|tip):', r'"\1":', text)
        return json.loads(t)
    old = {
        "db": tolerant(grab_obj("DB")),
    }
    return old


TEXT_REPLACEMENTS = [
    # (old, new) — self-referential date/patch/version strings only (source citations untouched)
    ("<title>MLBB Meta Report — August 2026</title>",
     "<title>MLBB Meta Report — September 2026</title>"),
    ("Snapshot accurate as of Aug 28, 2026.",
     "Rank-stats snapshot through Sep 16, 2026 (Season 42 launch day, patch 2.2.16)."),
    ("Season 41 ranked data (patch 2.1.95)",
     "Season 42 ranked data (patch 2.2.16)"),
    ("Compiled Aug 28, 2026 · Patch 2.1.95 · Season 41 \"Scarlet Embers\"",
     "Compiled Sep 25, 2026 · Patch 2.2.16 · Season 42 \"Starward Decade\""),
    ("ensemble of three independent matchup trackers</b> (MLBBHub ranked stats, mlbb.io, mlcounters — crawled Aug 29, 2026, patch 2.1.95) and community guide consensus (Zathong, BitTopup, Reddit). No single site\\'s list is trusted alone:",
     "MLBBHub ranked matchup stats</b> (crawled Sep 25, 2026, patch 2.2.16 — stats through the Sep 16 Season 42 launch), merged with the curated guide + kit reasoning kept from the v25 three-tracker ensemble. No single site\\'s list is trusted alone:"),
    ("Moonton ships balance patches roughly every 2 weeks (Advance Server is testing 2.2.10), so expect drift",
     "Season 42 (Sep 16, 2026) shipped 8 hero revamps — Masha (full rework), Bruno, Brody, Kadita, Badang, Clint, Paquito, Luo Yi — so expect drift as the patch settles"),
    ("mlbb.io ranked data, Aug 2026",
     "MLBBHub ranked data, Sep 2026"),
    ("measured win-rate edges from mlbb.io ranked data (crawled",
     "measured win-rate edges from MLBBHub ranked data (crawled"),
]


def cmd_write_html(snapshot, crawl_dir, index_path):
    old = parse_old_layers(index_path)
    layers = gen_layers(snapshot, old)
    js = open(index_path, encoding="utf-8").read()

    for name in LAYERS:
        i, e = grab_span(js, name)
        js = js[:i] + layers[name] + js[e:]
        print("  spliced %-8s (%6d chars)" % (name, len(layers[name])))

    applied = 0
    for old_t, new_t in TEXT_REPLACEMENTS:
        if old_t in js:
            js = js.replace(old_t, new_t)
            applied += 1
        else:
            print("  WARN text not found: %r..." % old_t[:60])
    print("  text replacements applied: %d/%d" % (applied, len(TEXT_REPLACEMENTS)))

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(js)
    print("wrote %s (%d KB)" % (index_path, len(js) // 1024))


# ------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--crawl", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--write-html", action="store_true")
    ap.add_argument("--crawl-dir", default="/tmp/mlbbhub-crawl")
    ap.add_argument("--index", default=os.path.join(os.path.dirname(__file__), "..", "index.html"))
    ap.add_argument("--snapshot-dir", default=os.path.join(os.path.dirname(__file__), "..", "data"))
    a = ap.parse_args()
    if not (a.crawl or a.build or a.write_html):
        ap.error("nothing to do: pass --crawl and/or --build and/or --write-html")

    if a.crawl:
        cmd_crawl(a.crawl_dir)
    snapshot_path = os.path.join(a.snapshot_dir, "meta-%s.json" % time.strftime("%Y-%m-%d"))
    if a.crawl or a.build or a.write_html:
        if os.path.exists(snapshot_path) and not a.crawl and not a.build:
            snapshot = json.load(open(snapshot_path))
            print("loaded existing snapshot", snapshot_path)
        else:
            if not os.path.isdir(a.crawl_dir) or not os.listdir(a.crawl_dir):
                sys.exit("crawl dir empty — run with --crawl first")
            snapshot = cmd_build(a.crawl_dir, snapshot_path)
    if a.write_html:
        cmd_write_html(snapshot, a.crawl_dir, os.path.abspath(a.index))


if __name__ == "__main__":
    main()
