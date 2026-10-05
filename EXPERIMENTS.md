# Experimentos

Indice generado por `python -m tools.experiments_index` (no editar a mano). El detalle de cada corrida
esta en `runs/<run_id>/NOTES.md` (escrito con `/registrar-corrida`) y `runs/<run_id>/run.json`.

| Run | Autor | Fecha | Estado | Timesteps | Éxito best (100 ep.) | Best éxito (8 ep.) | Best reward | Cambio |
|---|---|---|---|---|---|---|---|---|
| [v16-lucio](runs/v16-lucio/) | lucio | 2026-10-04 | finished | 200,704 | 4% (2–10) | 0% | -9.16 | normalización fija (sin VecNormalize), dron a 0.6 m/s y contacto base-tope |
| [v17-lucio](runs/v17-lucio/) | lucio | 2026-10-04 | finished | 5,001,216 | 88% (80–93) | 100% | 20.63 | misma configuración que v16, entrenada 5M pasos en vez de 200k |
| [v18-lucio](runs/v18-lucio/) | lucio | 2026-10-04 | finished | 1,503,232 | 0% (0–4) | 0% | 3.58 | recompensa A1: progreso (k=10) en vez de castigo por distancia |
| [v19-lucio](runs/v19-lucio/) | lucio | 2026-10-04 | finished | 1,503,232 | 26% (18–35) | 38% | -10.78 | recompensa A2: progreso (k=10) además del castigo por distancia |
| [v20-lucio](runs/v20-lucio/) | lucio | 2026-10-04 | finished | 1,503,232 | 0% (0–4) | 0% | -31.92 | recompensa B: castigo por choque −50 (antes −10) |
| [v21-lucio](runs/v21-lucio/) | lucio | 2026-10-04 | finished | 1,503,232 | 65% (55–74) | 88% | 14.72 | base de referencia con el PID arreglado (1.5M pasos) |
| [v22-lucio](runs/v22-lucio/) | lucio | 2026-10-04 | finished | 1,503,232 | 35% (26–45) | 38% | -4.45 | recompensa XY: distancia horizontal pesada 3 veces más que la altura |
