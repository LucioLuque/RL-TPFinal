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
| [v23-lucio](runs/v23-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 75% (66–82) | 88% | 23.60 | _sin registrar_ |
| [v24-lucio](runs/v24-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 67% (57–75) | 100% | 19.65 | _sin registrar_ |
| [v25-lucio](runs/v25-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 69% (59–77) | 88% | 27.83 | _sin registrar_ |
| [v26-lucio](runs/v26-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 66% (56–74) | 100% | 20.61 | _sin registrar_ |
| [v27-lucio](runs/v27-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 35% (26–45) | 62% | 6.34 | _sin registrar_ |
| [v28-lucio](runs/v28-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 0% (0–4) | 0% | -12.87 | _sin registrar_ |
| [v29-lucio](runs/v29-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 10% (6–17) | 12% | -12.78 | _sin registrar_ |
| [v30-lucio](runs/v30-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 74% (65–82) | 100% | 19.09 | _sin registrar_ |
| [v33-lucio](runs/v33-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 64% (54–73) | 88% | 15.92 | _sin registrar_ |
| [v34-lucio](runs/v34-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 81% (72–88) | 88% | 18.05 | _sin registrar_ |
| [v35-lucio](runs/v35-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 72% (62–80) | 88% | 14.51 | _sin registrar_ |
| [v36-lucio](runs/v36-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 74% (65–82) | 100% | 17.62 | _sin registrar_ |
| [v40-lucio](runs/v40-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 74% (65–82) | 100% | 19.65 | _sin registrar_ |
| [v41-lucio](runs/v41-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 32% (24–42) | 38% | -9.13 | _sin registrar_ |
| [v42-lucio](runs/v42-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 74% (65–82) | 88% | 15.95 | _sin registrar_ |
| [v50-lucio](runs/v50-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 70% (60–78) | 100% | 17.15 | _sin registrar_ |
| [v51-lucio](runs/v51-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 72% (62–80) | 88% | 13.85 | _sin registrar_ |
| [v52-lucio](runs/v52-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 73% (64–81) | 88% | 16.48 | _sin registrar_ |
| [v53-lucio](runs/v53-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 30% (22–40) | 38% | -4.03 | _sin registrar_ |
| [v54-lucio](runs/v54-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 89% (81–94) | 100% | 19.14 | _sin registrar_ |
| [v55-lucio](runs/v55-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 77% (68–84) | 100% | 18.98 | _sin registrar_ |
| [v56-lucio](runs/v56-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 84% (76–90) | 100% | 18.14 | _sin registrar_ |
| [v57-lucio](runs/v57-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 75% (66–82) | 100% | 20.17 | _sin registrar_ |
| [v58-lucio](runs/v58-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 81% (72–88) | 100% | 20.18 | _sin registrar_ |
| [v63-lucio](runs/v63-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 91% (84–95) | 100% | 19.60 | _sin registrar_ |
| [v64-lucio](runs/v64-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 88% (80–93) | 100% | 18.26 | _sin registrar_ |
