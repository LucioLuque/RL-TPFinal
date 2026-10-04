# Experimentos

Indice generado por `python -m tools.experiments_index` (no editar a mano). El detalle de cada corrida
esta en `runs/<run_id>/NOTES.md` (escrito con `/registrar-corrida`) y `runs/<run_id>/run.json`.

| Run | Autor | Fecha | Estado | Timesteps | Éxito best (100 ep.) | Best éxito (8 ep.) | Best reward | Cambio |
|---|---|---|---|---|---|---|---|---|
| [v16-lucio](runs/v16-lucio/) | lucio | 2026-10-04 | finished | 200,704 | 4% (2–10) | 0% | -9.16 | normalización fija (sin VecNormalize), dron a 0.6 m/s y contacto base-tope |
| [v17-lucio](runs/v17-lucio/) | lucio | 2026-10-04 | finished | 5,001,216 | 85% (77–91) | 100% | 20.63 | misma configuración que v16, entrenada 5M pasos en vez de 200k |
