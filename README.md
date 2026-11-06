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
