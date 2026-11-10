"""Dati condivisi dagli script di Dovelavedo. Tenere allineato con index.html (PK, OFFERS, PLAT)."""
import json, os, re, unicodedata, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://dovelavedo.github.io"

PK = {
    "daznfull": ("DAZN Full, Family o Full Mobile", "da 46,99 €/mese o 379 € l'anno"),
    "daznclub": ("DAZN MyClubPass", "29,99 €/mese con 12 rate, solo la tua squadra"),
    "skycalcio": ("Sky TV + Sky Calcio", "circa 14,90 €/mese in promozione"),
    "skysport": ("Sky TV + Sky Sport", "24,99 €/mese per 18 mesi"),
    "nowsport": ("NOW Pass Sport", "24,99 €/mese con vincolo di 12 mesi"),
    "prime": ("Amazon Prime", "4,99 €/mese"),
    "eurosport": ("Eurosport", "tramite HBO Max, discovery+, DAZN o TIMVISION"),
    "lbatv": ("LBA TV", "99 € a stagione"),
    "vbtv": ("VBTV", "piattaforma di Volleyball World"),
}
OFFERS = {
    "seriea_dazn": ("DAZN", ["daznfull", "daznclub"]), "seriea_sky": ("Sky", ["skycalcio"]),
    "seriea_now": ("NOW", ["nowsport"]), "dazn": ("DAZN", ["daznfull"]),
    "sky_sport": ("Sky", ["skysport"]), "now_sport": ("NOW", ["nowsport"]),
    "prime": ("Prime Video", ["prime"]), "eurosport": ("Eurosport", ["eurosport"]),
    "lbatv": ("LBA TV", ["lbatv"]), "vbtv": ("VBTV", ["vbtv"]),
}
PLAT = {
    "DAZN": "https://www.dazn.com/it-IT/home", "Sky": "https://www.sky.it", "NOW": "https://www.nowtv.it",
    "Prime Video": "https://www.primevideo.com", "Eurosport": "https://www.eurosport.it",
    "LBA TV": "https://www.legabasket.it", "VBTV": "https://volleyballworld.tv",
    "Rai 1": "https://www.raiplay.it/dirette/rai1", "Rai 2": "https://www.raiplay.it/dirette/rai2",
    "Rai Sport": "https://www.raiplay.it/dirette/raisport", "Rai": "https://www.raiplay.it/dirette",
    "RaiPlay": "https://www.raiplay.it/dirette", "Mediaset": "https://mediasetinfinity.mediaset.it/dirette",
    "TV8": "https://www.tv8.it/streaming", "SuperTennis": "https://www.supertennis.tv",
}
WDL = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
MO = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre",
      "ottobre", "novembre", "dicembre"]


def load():
    with open(os.path.join(ROOT, "data", "events.json"), encoding="utf-8") as f:
        d = json.load(f)
    return d.get("updated", ""), [e for e in d["events"] if e.get("d") and e.get("n")]


def slug(e):
    """Stesso calcolo di slug() in index.html."""
    s = unicodedata.normalize("NFD", e["n"] + " " + e["c"])
    s = "".join(ch for ch in s if not 0x300 <= ord(ch) <= 0x36F).lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") + "-" + e["d"]


def dlabel(iso, year=False):
    x = datetime.date.fromisoformat(iso)
    return f"{WDL[x.weekday()]} {x.day} {MO[x.month - 1]}" + (f" {x.year}" if year else "")


def platforms(e):
    """Piattaforme a pagamento, senza doppioni, nell'ordine del file."""
    out = []
    for c in e.get("o", []):
        if c in OFFERS and OFFERS[c][0] not in out:
            out.append(OFFERS[c][0])
    return out


def plats_line(e):
    ps, fr = platforms(e), e.get("f", [])
    line = " · ".join(ps)
    if fr:
        line += (" · gratis: " if ps else "Gratis: ") + ", ".join(fr)
    return line or "Emittente da confermare"


def today_rome():
    try:
        from zoneinfo import ZoneInfo
        return datetime.datetime.now(ZoneInfo("Europe/Rome")).date().isoformat()
    except Exception:
        return (datetime.datetime.utcnow() + datetime.timedelta(hours=1)).date().isoformat()
