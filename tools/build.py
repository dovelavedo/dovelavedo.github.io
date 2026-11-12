#!/usr/bin/env python3
"""Genera le pagine "Dove vedere X–Y" (una per evento), l'elenco e la sitemap.
Da lanciare dopo ogni modifica a data/events.json:  python3 tools/build.py
Le pagine degli eventi passati restano online (i link condivisi non si rompono) ma escono dalla sitemap."""
import html, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, SITE, PK, OFFERS, PLAT, load, slug, dlabel, platforms, plats_line, today_rome

OUT = os.path.join(ROOT, "dove-vedere")
esc = html.escape

CSS = """
:root{--bg:#f2f6f3;--surface:#fff;--ink:#10201a;--muted:#566a60;--line:#d9e3dd;--accent:#0b6b36;--accent-soft:#e3f2e8;--on-accent:#fff;--gold-ink:#8a6a00;--free:#0b6f7a;--free-soft:#ddf2f4;--warn:#9a5b00;--warn-soft:#fdf0d9;color-scheme:light}
@media (prefers-color-scheme:dark){:root{--bg:#0b1310;--surface:#14201b;--ink:#e7efea;--muted:#9bb0a5;--line:#26362e;--accent:#3ccf7f;--accent-soft:#163325;--on-accent:#06110b;--gold-ink:#f5c518;--free:#5ccfdb;--free-soft:#10303a;--warn:#f2b55a;--warn-soft:#352612;color-scheme:dark}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"Barlow",system-ui,-apple-system,"Segoe UI",Arial,sans-serif;font-size:16px;line-height:1.5;padding:16px max(16px,env(safe-area-inset-right,0px)) 40px max(16px,env(safe-area-inset-left,0px))}
main{max-width:620px;margin:0 auto;display:flex;flex-direction:column;gap:16px}
a{color:var(--accent)}
.top{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink)}
.top img{width:36px;height:36px;border-radius:9px}
.brand{font-family:"Lilita One","Arial Narrow",Arial,sans-serif;font-size:26px;text-transform:uppercase;line-height:1}
.brand span{color:var(--gold-ink)}
.kicker{font-size:13px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:var(--muted);margin:0}
h1{font-family:"Barlow Condensed","Arial Narrow",Arial,sans-serif;font-weight:700;font-size:34px;line-height:1.05;text-transform:uppercase;margin:0;text-wrap:balance}
h2{font-family:"Barlow Condensed","Arial Narrow",Arial,sans-serif;font-size:22px;text-transform:uppercase;margin:0}
p{margin:0}
.when{font-size:18px;font-weight:600}
.card{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:16px;display:flex;flex-direction:column;gap:12px}
.prow{display:flex;justify-content:space-between;align-items:center;gap:12px;border-top:1px solid var(--line);padding-top:12px}
.card .prow:first-of-type{border-top:0;padding-top:0}
.prow div{min-width:0}
.prow b{display:block;font-size:17px}
.prow small{color:var(--muted);font-size:14px}
.pill{font-size:12px;font-weight:700;border-radius:999px;padding:3px 9px;color:var(--free);background:var(--free-soft);margin-left:6px;vertical-align:middle}
.btn{background:var(--accent);color:var(--on-accent);font-weight:700;border-radius:10px;padding:10px 14px;text-decoration:none;white-space:nowrap;text-align:center}
.btn.big{display:block;padding:13px 16px;font-size:17px}
.btn.ghost{background:transparent;color:var(--accent);border:1px solid var(--accent)}
.note{font-size:14px;color:var(--muted)}
.alert{border:1px solid var(--warn);background:var(--warn-soft);border-radius:12px;padding:10px 12px;font-size:15px}
.cta{background:var(--accent-soft);border-color:var(--accent)}
ul.list{list-style:none;margin:0;padding:0;display:flex;flex-direction:column}
ul.list li{border-top:1px solid var(--line);padding:9px 0}
ul.list li:first-child{border-top:0}
ul.list a{font-weight:700;text-decoration:none}
ul.list small{display:block;color:var(--muted);font-size:14px}
footer{font-size:13px;color:var(--muted);display:flex;flex-direction:column;gap:4px}
"""

HEAD = """<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#0b6b36">
<link rel="icon" href="../icons/icon-192.png">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{site}/icons/icon-512.png">
<meta property="og:url" content="{canon}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lilita+One&family=Barlow+Condensed:wght@700&family=Barlow:wght@400;600;700&display=swap">
<style>{css}</style>
{extra}
</head>
<body>
<main>
<a class="top" href="../"><img src="../icons/icon-192.png" alt=""><span class="brand">Dove la <span>vedo</span></span></a>
"""
FOOT = """
<footer>
<span>Orari e canali possono cambiare: controlla sempre sulla piattaforma. Solo fonti ufficiali, niente pirateria.</span>
<span>Dovelavedo non è affiliato a DAZN, Sky, NOW, Prime Video, Rai o altre emittenti: i marchi sono dei rispettivi proprietari.</span>
<span><a href="../">Palinsesto di oggi</a> · <a href="./">Tutte le partite</a> · <a href="../chi-siamo.html">Chi siamo, privacy e contatti</a></span>
<span>Dovelavedo è gratis. <a href="https://paypal.me/madebyze" target="_blank" rel="noopener">Sostienilo con una donazione</a> · <a href="https://t.me/dovelavedo" target="_blank" rel="noopener">Canale Telegram</a></span>
</footer>
</main>
<script data-goatcounter="https://dovelavedo.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
</body>
</html>
"""


def verb(e):
    return "vederla" if e["s"] in ("Calcio", "Basket", "Pallavolo") else "vederlo"


def page(e, upd, others):
    name, comp = e["n"], e["c"]
    when = dlabel(e["d"], True) + (f", ore {e['t']}" if e.get("t") else ", orario da definire")
    if e.get("w"):
        when = f"{e['w'][0].upper()}{e['w'][1:]} {e['d'][:4]}: giorno e orario da definire" if not e["w"][0].isdigit() else f"Weekend del {e['w']} {e['d'][:4]}: giorno e orario da definire"
    line = plats_line(e)
    title = f"Dove vedere {name} in TV e streaming · {comp}, {dlabel(e['d'])}"
    desc = f"{name} ({comp}): {when}. Dove {verb(e)}: {line}. Scopri se è già nei tuoi abbonamenti."
    canon = f"{SITE}/dove-vedere/{slug(e)}.html"
    rows = []
    for c in e.get("o", []):
        if c not in OFFERS:
            continue
        p, ks = OFFERS[c]
        need = " oppure ".join(f"{PK[k][0]} ({PK[k][1]})" for k in ks)
        link = (e.get("l") or {}).get(p) or PLAT.get(p, "#")
        lab = "Vai alla partita" if (e.get("l") or {}).get(p) else f"Apri {p}"
        rows.append(f'<div class="prow"><div><b>{esc(p)}</b><small>Serve: {esc(need)}</small></div>'
                    f'<a class="btn" href="{esc(link)}" target="_blank" rel="noopener">{esc(lab)} ↗</a></div>')
    for p in e.get("f", []):
        link = (e.get("l") or {}).get(p) or PLAT.get(p)
        btn = f'<a class="btn" href="{esc(link)}" target="_blank" rel="noopener">Guarda la diretta ↗</a>' if link else ""
        rows.append(f'<div class="prow"><div><b>{esc(p)}<span class="pill">Gratis</span></b>'
                    f'<small>In chiaro, senza abbonamento</small></div>{btn}</div>')
    if not rows:
        rows.append('<p class="note">L\'emittente non è ancora stata confermata. Torna a controllare nei prossimi giorni.</p>')
    free = bool(e.get("f"))
    paid = platforms(e)
    if free and not paid:
        answer = f"{name} si vede gratis su {', '.join(e['f'])}."
    elif free:
        answer = f"{name} si vede gratis su {', '.join(e['f'])} e in abbonamento su {', '.join(paid)}."
    elif paid:
        answer = f"{name} si vede su {' e '.join([', '.join(paid[:-1]), paid[-1]]) if len(paid) > 1 else paid[0]}. Non è prevista la diretta in chiaro."
    else:
        answer = f"L'emittente di {name} non è ancora stata confermata."
    start = f"{e['d']}T{e['t']}:00+01:00" if e.get("t") else e["d"]
    ld = {"@context": "https://schema.org", "@type": "SportsEvent", "name": f"{name} · {comp}", "startDate": start,
          "sport": e["s"], "eventAttendanceMode": "https://schema.org/OnlineEventAttendanceMode",
          "location": {"@type": "VirtualLocation", "url": canon},
          "description": f"Dove {verb(e)}: {line}", "url": canon}
    teams = [t.strip() for t in name.split("–")] if "–" in name and e["s"] in ("Calcio", "Basket", "Pallavolo") else []
    if len(teams) == 2:
        ld["homeTeam"] = {"@type": "SportsTeam", "name": teams[0]}
        ld["awayTeam"] = {"@type": "SportsTeam", "name": teams[1]}
    extra = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>"
    h = HEAD.format(title=esc(title), desc=esc(desc), canon=canon, site=SITE, css=CSS, extra=extra)
    h += f'<p class="kicker">{esc(comp)} · {esc(e["s"])}</p>\n<h1>Dove vedere {esc(name)}</h1>\n'
    h += f'<p class="when" id="when">{esc(when[0].upper() + when[1:])}</p>\n'
    h += '<div class="alert" id="past" hidden>Questo evento è già passato. <a href="../">Guarda cosa c\'è oggi</a>.</div>\n'
    if e.get("chg"):
        h += f'<div class="alert"><b>Cambio di programma:</b> {esc(e["chg"])}.</div>\n'
    h += f'<p>{esc(answer)}</p>\n<div class="card"><h2>Dove {verb(e)}</h2>{"".join(rows)}</div>\n'
    if e.get("x"):
        h += f'<p class="note">{esc(e["x"])}</p>\n'
    h += ('<div class="card cta"><h2>Ce l\'hai già nei tuoi abbonamenti?</h2>'
          '<p>Dovelavedo ti dice in un colpo d\'occhio cosa puoi vedere con quello che paghi già, e cosa è gratis. '
          'È gratuito e senza registrazione.</p><a class="btn big" href="../">Apri il palinsesto di oggi</a></div>\n')
    rel = []
    ck = comp_key(comp)
    if ck:
        rel.append((f"{ck}: dove vederla, tutte le partite", COMPS[ck][0] + ".html"))
    rel += [(f"Dove vedere {t}: prossime partite", team_slug(t, e["s"]) + ".html") for t in teams_of(e)]
    if rel:
        h += '<div class="card"><h2>Vedi anche</h2><ul class="list">' + "".join(
            f'<li><a href="{u}">{esc(t)}</a></li>' for t, u in rel) + "</ul></div>\n"
    if others:
        h += '<div class="card"><h2>Lo stesso giorno</h2><ul class="list">'
        for o in others[:8]:
            h += (f'<li><a href="{slug(o)}.html">{esc(o["n"])}</a>'
                  f'<small>{esc(o["c"])} · {esc(o.get("t") or "orario da definire")} · {esc(plats_line(o))}</small></li>')
        h += "</ul></div>\n"
    h += f'<p class="note">Scheda aggiornata il {dlabel(upd, True)}.</p>\n'
    h += f'<script>if(new Date()>new Date("{e["d"]}T23:59:59+01:00"))document.getElementById("past").hidden=false</script>'
    return h + FOOT


def index(evs, upd):
    title = "Dove vedere lo sport in TV: tutte le partite dei prossimi giorni"
    desc = "Calcio, tennis, Formula 1, MotoGP, basket e pallavolo: orari e canali di tutti gli eventi in programma, piattaforma per piattaforma."
    h = HEAD.format(title=esc(title), desc=esc(desc), canon=f"{SITE}/dove-vedere/", site=SITE, css=CSS, extra="")
    h += '<p class="kicker">Tutti gli eventi in programma</p>\n<h1>Dove vedere lo sport in TV</h1>\n'
    h += f'<p class="note">Aggiornato il {dlabel(upd, True)}. Tocca un evento per vedere canali e abbonamenti.</p>\n'
    h += '<div class="card"><h2>Per competizione</h2><ul class="list">' + "".join(
        f'<li><a href="{fn}.html">{esc(k)}</a></li>' for k, (fn, _) in COMPS.items()) + "</ul></div>\n"
    import datetime as _dt
    lim = (_dt.date.fromisoformat(min(e["d"] for e in evs)) + _dt.timedelta(days=31)).isoformat() if evs else ""
    h += '<p class="note">Qui sotto i prossimi 30 giorni. Le partite più avanti le trovi nelle pagine delle competizioni e delle squadre.</p>\n'
    days = sorted({e["d"] for e in evs if e["d"] <= lim})
    for d in days:
        lab = dlabel(d, True)
        h += f'<div class="card"><h2>{esc(lab[0].upper() + lab[1:])}</h2><ul class="list">'
        for e in [x for x in evs if x["d"] == d]:
            h += (f'<li><a href="{slug(e)}.html">{esc(e["n"])}</a>'
                  f'<small>{esc(e["c"])} · {esc(e.get("t") or "orario da definire")} · {esc(plats_line(e))}</small></li>')
        h += "</ul></div>\n"
    return h + FOOT


# ---------- Pagine fisse: competizioni e squadre ----------
COMPS = {
    "Serie A": ("serie-a", "Tutte le dieci partite di ogni giornata sono su DAZN. Tre partite per giornata si vedono anche su Sky (pacchetto Sky Calcio) e su NOW (Pass Sport). Nessuna partita è in chiaro."),
    "Serie B": ("serie-b", "Tutta la Serie B è su DAZN. Le partite si vedono anche su LaB Channel, un canale a pagamento dentro Prime Video."),
    "Champions League": ("champions-league", "La Champions League è su Sky e NOW. La partita migliore del mercoledì è in esclusiva su Prime Video e non si vede su Sky."),
    "Coppa Italia": ("coppa-italia", "La Coppa Italia è in chiaro su Mediaset (Canale 5 o Italia 1) e in streaming gratuito su Mediaset Infinity."),
    "Europa League": ("europa-league", "L'Europa League è su Sky e NOW. Alcune partite vanno anche in chiaro su TV8."),
    "Conference League": ("conference-league", "La Conference League è su Sky e NOW. Alcune partite vanno anche in chiaro su TV8."),
    "Nations League": ("nations-league", "Le partite dell'Italia sono in chiaro su Rai 1 e in streaming gratuito su RaiPlay."),
    "Formula 1": ("formula-1", "Tutta la Formula 1 è in diretta su Sky e NOW. TV8 trasmette in chiaro le gare in differita e alcuni Gran Premi in diretta."),
    "MotoGP": ("motogp", "Tutta la MotoGP è in diretta su Sky e NOW. TV8 trasmette in chiaro alcune gare in diretta e le altre in differita."),
    "ATP Finals": ("atp-finals", "Le ATP Finals di Torino sono tutte su Sky e NOW. In chiaro le partite migliori, finale compresa, vanno su Mediaset."),
    "Coppa Davis": ("coppa-davis", "La Coppa Davis è in chiaro su SuperTennis. Le partite dell'Italia in semifinale e finale vanno anche sulla Rai."),
    "EuroLeague": ("eurolega", "L'EuroLeague di basket è su Sky e NOW."),
    "Serie A basket": ("serie-a-basket", "Tutte le partite della Serie A di basket sono su LBA TV. Alcune partite per giornata si vedono anche su Sky e NOW."),
    "SuperLega": ("superlega-volley", "Tutta la SuperLega è su VBTV. Alcune partite per giornata vanno anche in chiaro su Rai Sport o su DAZN."),
}
TEAMSPORTS = {"Calcio": "calcio", "Basket": "basket", "Pallavolo": "volley"}


def comp_key(c):
    for k in sorted(COMPS, key=len, reverse=True):
        if c.startswith(k):
            return k
    return None


def sl(t):
    import re, unicodedata
    t = "".join(ch for ch in unicodedata.normalize("NFD", t) if not 0x300 <= ord(ch) <= 0x36F).lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def teams_of(e):
    if e["s"] not in TEAMSPORTS or "–" not in e["n"]:
        return []
    return [t.split("·")[0].strip() for t in e["n"].split("–")][:2]


def team_slug(t, s):
    return f"{sl(t)}-{TEAMSPORTS[s]}"


def evlist(evs, withday=True):
    if not evs:
        return '<p class="note">Nessun evento in programma nei prossimi giorni. Il calendario si aggiorna ogni mattina.</p>'
    h = '<ul class="list">'
    for e in evs:
        when = (e["w"] + ", data da definire") if e.get("w") else (dlabel(e["d"]) + ", " if withday else "") + (e.get("t") or "orario da definire")
        h += (f'<li><a href="{slug(e)}.html">{esc(e["n"])}</a>'
              f'<small>{esc(e["c"])} · {esc(when)} · {esc(plats_line(e))}</small></li>')
    return h + "</ul>"


def fixed_page(fname, title, desc, kicker, h1, intro, evs, links, upd):
    h = HEAD.format(title=esc(title), desc=esc(desc), canon=f"{SITE}/dove-vedere/{fname}", site=SITE, css=CSS, extra="")
    h += f'<p class="kicker">{esc(kicker)}</p>\n<h1>{esc(h1)}</h1>\n'
    for p in intro:
        h += f"<p>{esc(p)}</p>\n"
    h += f'<div class="card"><h2>Prossimi eventi</h2>{evlist(evs)}</div>\n'
    h += ('<div class="card cta"><h2>Ce l\'hai già nei tuoi abbonamenti?</h2>'
          '<p>Scegli squadre e abbonamenti: Dovelavedo ti mostra cosa puoi vedere con quello che paghi già e cosa è gratis. '
          'Gratuito, senza registrazione.</p><a class="btn big" href="../">Apri Dovelavedo</a></div>\n')
    if links:
        h += '<div class="card"><h2>Vedi anche</h2><ul class="list">' + "".join(
            f'<li><a href="{u}">{esc(t)}</a></li>' for t, u in links) + "</ul></div>\n"
    h += f'<p class="note">Pagina aggiornata il {dlabel(upd, True)}.</p>\n'
    return h + FOOT


def fixed_pages(evs, upd):
    """Pagine che restano sempre online: una per competizione e una per squadra vista almeno una volta."""
    reg_path = os.path.join(ROOT, "data", "teams.json")
    try:
        reg = json.load(open(reg_path, encoding="utf-8"))
    except Exception:
        reg = {}
    for e in evs:
        ck = comp_key(e["c"])
        for t in teams_of(e):
            r = reg.setdefault(team_slug(t, e["s"]), {"n": t, "s": e["s"], "c": []})
            if ck and ck not in r["c"]:
                r["c"].append(ck)
    json.dump(reg, open(reg_path, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
    urls = []
    comp_links = [(f"{k}: dove vederla" if k not in ("Formula 1", "MotoGP") else f"{k}: dove vederla in TV", COMPS[k][0] + ".html") for k in COMPS]
    for k, (fn, txt) in COMPS.items():
        ce = [e for e in evs if comp_key(e["c"]) == k]
        tl = sorted({(reg[ts]["n"], ts) for ts in reg if k in reg[ts]["c"]})
        links = [(f"Dove vedere {n}", ts + ".html") for n, ts in tl][:40] + [l for l in comp_links if l[1] != fn + ".html"][:6]
        page_ = fixed_page(fn + ".html", f"{k} in TV e streaming: dove vederla, orari e canali",
                           f"{k}: {txt} Orari e canali delle prossime partite, aggiornati ogni giorno.",
                           "Guida TV", f"{k}: dove vederla in TV e streaming", [txt], ce, links, upd)
        open(os.path.join(OUT, fn + ".html"), "w", encoding="utf-8").write(page_)
        urls.append(fn + ".html")
    for ts, r in reg.items():
        te = [e for e in evs if e["s"] == r["s"] and r["n"] in teams_of(e)]
        intro = [f"Qui trovi le prossime partite di {r['n']} con orario, canale e abbonamento che serve."]
        intro += [COMPS[c][1] for c in r["c"] if c in COMPS]
        links = [(f"{c}: dove vederla", COMPS[c][0] + ".html") for c in r["c"] if c in COMPS]
        sport = {"Calcio": "calcio", "Basket": "basket", "Pallavolo": "pallavolo"}[r["s"]]
        page_ = fixed_page(ts + ".html", f"Dove vedere {r['n']} in TV e streaming: prossime partite e canali",
                           f"Le prossime partite di {r['n']} ({sport}): orari, canali TV e streaming, e quale abbonamento serve.",
                           f"Guida TV · {sport}", f"Dove vedere {r['n']}: prossime partite in TV e streaming", intro, te, links, upd)
        open(os.path.join(OUT, ts + ".html"), "w", encoding="utf-8").write(page_)
        urls.append(ts + ".html")
    return urls, reg




def main():
    upd, evs = load()
    today = today_rome()
    evs = sorted([e for e in evs if e["d"] >= today], key=lambda e: (e["d"], e.get("t") or "99", e["n"]))
    os.makedirs(OUT, exist_ok=True)
    seen = set()
    for e in evs:
        s = slug(e)
        if s in seen:
            print("ATTENZIONE: due eventi con lo stesso indirizzo:", s)
        seen.add(s)
        others = [o for o in evs if o["d"] == e["d"] and o is not e]
        with open(os.path.join(OUT, s + ".html"), "w", encoding="utf-8") as f:
            f.write(page(e, upd, others))
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(index(evs, upd))
    urls = [(SITE + "/", "daily"), (SITE + "/dove-vedere/", "daily"), (SITE + "/chi-siamo.html", "monthly")]
    fixed, reg = fixed_pages(evs, upd)
    urls += [(f"{SITE}/dove-vedere/{u}", "daily") for u in fixed]
    urls += [(f"{SITE}/dove-vedere/{slug(e)}.html", "daily") for e in evs]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"<url><loc>{u}</loc><lastmod>{upd}</lastmod><changefreq>{c}</changefreq></url>\n" for u, c in urls)
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sm + "</urlset>\n")
    print(f"{len(evs)} pagine evento, {len(fixed)} pagine fisse (competizioni e squadre), elenco e sitemap generati.")


if __name__ == "__main__":
    main()
