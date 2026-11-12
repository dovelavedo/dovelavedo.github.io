# Dovelavedo

Lo sport in TV oggi e dove vederlo: https://dovelavedo.github.io

## Come si aggiorna il palinsesto

L'app legge tutto da `data/events.json`. Ogni evento ha questi campi:

| Campo | Significato | Esempio |
| --- | --- | --- |
| `d` | data (AAAA-MM-GG) | `"2026-11-08"` |
| `t` | ora italiana, vuota se non confermata | `"18:00"` |
| `s` | sport: Calcio, Tennis, Motori, Basket, Pallavolo | `"Calcio"` |
| `c` | competizione | `"Serie A"` |
| `n` | evento, squadre separate da "–" | `"Inter–Como"` |
| `o` | piattaforme a pagamento (codici sotto) | `["seriea_dazn","seriea_sky","seriea_now"]` |
| `f` | canali gratis (facoltativo) | `["Rai 1"]` |
| `who` | squadre o atleti, se il nome non basta (facoltativo) | `["Leclerc","Ferrari"]` |
| `x` | nota per l'utente (facoltativo) | `"Su TV8 in differita."` |
| `l` | link diretti alla partita per piattaforma (facoltativo) | `{"DAZN":"https://www.dazn.com/..."}` |
| `chg` | cambio di programma (facoltativo) | `"Spostata dalle 15:00 alle 18:00"` |

Codici delle piattaforme: `seriea_dazn` (Serie A su DAZN, incluso MyClubPass), `seriea_sky` (Sky Calcio), `seriea_now` (NOW Sport), `dazn`, `sky_sport`, `now_sport`, `prime`, `eurosport`, `lbatv`, `vbtv`.

`chgd` (facoltativo) è la data in cui è stato segnato il cambio: dopo 3 giorni si tolgono `chg` e `chgd`.

## Dopo ogni modifica al palinsesto

```
python3 tools/build.py
```

Rigenera le pagine "Dove vedere X–Y" nella cartella `dove-vedere/` (una per evento, pensate per Google), l'elenco e `sitemap.xml`. Vanno pubblicate insieme a `data/events.json`. Le pagine degli eventi passati restano online.

## Card "Oggi in TV"

```
python3 tools/card.py [AAAA-MM-GG] [file.png]
```

Crea l'immagine con gli eventi principali del giorno (serve la libreria Pillow). Stampa il percorso del file, oppure `NESSUN_EVENTO`.

## Cosa copriamo

Serie A (con le partite anche su Sky/NOW), Serie B, Champions, Europa e Conference League delle italiane, Nazionale, Formula 1 e MotoGP (qualifiche, Sprint, gare), tennis (tornei principali e italiani, Coppa Davis), EuroLeague di Milano e Virtus, Serie A basket, SuperLega.

Se cambiano pacchetti, prezzi o codici, vanno aggiornati sia in `index.html` (PK, OFFERS, PLAT, MONTH) sia in `tools/common.py`.

`tools/build.py` crea anche pagine fisse che restano sempre online: una per competizione (es. `dove-vedere/serie-a.html`) e una per ogni squadra apparsa almeno una volta nel palinsesto (es. `dove-vedere/inter-calcio.html`). L'elenco delle squadre si accumula in `data/teams.json`: non va modificato a mano.

`w` (facoltativo) indica che la data non è ancora decisa: l'evento è messo alla domenica del weekend (o al giorno del turno) e `w` contiene il periodo da mostrare, es. "16-17 gennaio". Quando la Lega pubblica giorni e orari, si aggiorna `d`, si mette `t`, si aggiungono Sky/NOW dove servono e si toglie `w`.

## Calendari caricati

Serie A e Serie B fino all'ultima giornata, Champions/Europa/Conference fino alla fine della fase campionato, Coppa Italia (ottavi e finale), EuroLeague di Milano e Virtus fino alla fine della stagione regolare, SuperLega fino all'ultima giornata, Formula 1 e MotoGP 2027. Serie A basket solo fino a inizio dicembre: il calendario completo non era leggibile dalle fonti online.
