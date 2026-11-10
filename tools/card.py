#!/usr/bin/env python3
"""Crea la card "Oggi in TV" (immagine 1080x1350) dagli eventi del giorno.
Uso:  python3 tools/card.py [AAAA-MM-GG] [file.png]
Stampa il percorso dell'immagine, oppure NESSUN_EVENTO se quel giorno non c'è nulla."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont
from common import ROOT, load, dlabel, plats_line, today_rome

W, H, M = 1080, 1350, 64
GREEN, DARK, GOLD, WHITE, SOFT = (11, 107, 54), (6, 62, 32), (245, 197, 24), (255, 255, 255), (203, 232, 214)
FD = os.path.join(ROOT, "tools", "fonts")
font = lambda n, s: ImageFont.truetype(os.path.join(FD, n), s)
LIL, COND, BODY = "LilitaOne.ttf", "BarlowCondensed-Bold.ttf", "Barlow-SemiBold.ttf"
MAXROWS = 7
LINE = (56, 140, 92)


def weight(e):
    """Più basso = più importante: decide cosa entra nella card quando gli eventi sono tanti."""
    c, who = e["c"], e.get("who") or []
    n = e["n"]
    if "Italia" in n.split("–") or "Italia" in who or n.startswith("Italia"):
        return 0
    for k, w in (("Champions", 1), ("Serie A basket", 7), ("Serie A", 2), ("Formula 1", 3), ("MotoGP", 3),
                 ("ATP Finals", 3), ("Europa League", 3), ("Coppa Davis", 4), ("Conference", 4), ("EuroLeague", 5),
                 ("SuperLega", 6), ("Serie B", 8)):
        if k in c:
            return w - (1 if "sky_sport" in e.get("o", []) and k == "Serie A basket" else 0)
    return 6


def fit(draw, text, name, size, maxw, minsize=30):
    f = font(name, size)
    while draw.textlength(text, font=f) > maxw and size > minsize:
        size -= 2
        f = font(name, size)
    if draw.textlength(text, font=f) > maxw:
        while len(text) > 4 and draw.textlength(text + "…", font=f) > maxw:
            text = text[:-1]
        text = text.rstrip(" ·,") + "…"
    return text, f


def main():
    day = sys.argv[1] if len(sys.argv) > 1 else today_rome()
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "card.png")
    _, evs = load()
    evs = [e for e in evs if e["d"] == day]
    if not evs:
        print("NESSUN_EVENTO")
        return
    top = sorted(sorted(evs, key=lambda e: (weight(e), e.get("t") or "99"))[:MAXROWS], key=lambda e: (e.get("t") or "99", e["n"]))
    rest = len(evs) - len(top)

    img = Image.new("RGB", (W, H), GREEN)
    px = img.load()
    for y in range(H):  # sfumatura verticale
        t = y / H
        col = tuple(int(GREEN[i] * (1 - t) + DARK[i] * t) for i in range(3))
        for x in range(W):
            px[x, y] = col
    d = ImageDraw.Draw(img)

    # testata
    try:
        logo = Image.open(os.path.join(ROOT, "icons", "icon-192.png")).convert("RGBA").resize((104, 104))
        mask = Image.new("L", (104, 104), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, 103, 103), 24, fill=255)
        img.paste(logo, (M, M), mask)
    except Exception:
        pass
    f = font(LIL, 66)
    x = M + 128
    d.text((x, M + 14), "DOVE LA ", font=f, fill=WHITE)
    d.text((x + d.textlength("DOVE LA ", font=f), M + 14), "VEDO", font=f, fill=GOLD)

    lab = dlabel(day)
    d.text((M, 214), "OGGI IN TV", font=font(COND, 120), fill=GOLD)
    d.text((M, 344), lab.upper(), font=font(COND, 50), fill=WHITE)

    # righe: più grandi quando gli eventi sono pochi
    y0, y1 = 436, H - 196
    rh = min(150, (y1 - y0) // len(top))
    k = min(1.3, rh / 103)
    z = lambda v: int(v * k)
    for i, e in enumerate(top):
        y = y0 + i * rh
        d.line((M, y, W - M, y), fill=LINE, width=2)
        d.text((M, y + z(18)), e.get("t") or "—", font=font(COND, z(54)), fill=GOLD)
        tx, maxw = M + z(165), W - M - (M + z(165))
        if e.get("f"):
            pf = font(COND, z(28))
            pw = d.textlength("GRATIS", font=pf) + z(26)
            d.rounded_rectangle((W - M - pw, y + z(16), W - M, y + z(54)), z(19), fill=GOLD)
            d.text((W - M - pw + z(13), y + z(18)), "GRATIS", font=pf, fill=DARK)
            maxw -= pw + 16
        name, nf = fit(d, e["n"], COND, z(44), maxw)
        d.text((tx, y + z(8)), name, font=nf, fill=WHITE)
        sub, sf = fit(d, f"{e['c']} · {plats_line(e)}", BODY, z(25), W - M - tx, 20)
        d.text((tx, y + z(60)), sub, font=sf, fill=SOFT)
    yb = y0 + len(top) * rh
    d.line((M, yb, W - M, yb), fill=LINE, width=2)
    if rest > 0:
        d.text((M, yb + 14), f"+ {rest} {'altro evento' if rest == 1 else 'altri eventi'} nell'app", font=font(BODY, 30), fill=SOFT)

    # piede
    d.rounded_rectangle((M, H - 118, W - M, H - M + 6), 26, fill=GOLD)
    txt = "dovelavedo.github.io"
    ff = font(LIL, 44)
    d.text(((W - d.textlength(txt, font=ff)) / 2, H - 108), txt, font=ff, fill=DARK)
    img.save(out, optimize=True)
    print(out)


if __name__ == "__main__":
    main()
