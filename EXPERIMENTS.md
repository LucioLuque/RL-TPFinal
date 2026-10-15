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
| [v23-lucio](runs/v23-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 75% (66–82) | 88% | 23.60 | progreso k=3 además de la distancia (`A2_k3`), seed 42 |
| [v24-lucio](runs/v24-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 67% (57–75) | 100% | 19.65 | castigo 0.02·Σ(Δa)² por cambiar la acción (`suave_c002`), seed 42 |
| [v25-lucio](runs/v25-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 69% (59–77) | 88% | 27.83 | shaping por potencial k=10 sumado a `base` (`PBRS_k10`), seed 42 |
| [v26-lucio](runs/v26-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 66% (56–74) | 100% | 20.61 | progreso k=1 además de la distancia (`A2_k1`), seed 42 |
| [v27-lucio](runs/v27-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 35% (26–45) | 62% | 6.34 | progreso k=3 que mide solo lo que se movió el dron (`A2_k3_drone`), seed 42 |
| [v28-lucio](runs/v28-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 0% (0–4) | 0% | -12.87 | castigo por estar bajo y afuera de la plataforma (`borde_k1`), seed 42 |
| [v29-lucio](runs/v29-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 10% (6–17) | 12% | -12.78 | recompensa `base`, seed 1 |
| [v30-lucio](runs/v30-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 74% (65–82) | 100% | 19.09 | recompensa `base`, seed 2 |
| [v33-lucio](runs/v33-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 64% (54–73) | 88% | 15.92 | progreso k=3 además de la distancia (`A2_k3`), seed 1 |
| [v34-lucio](runs/v34-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 81% (72–88) | 88% | 18.05 | progreso k=3 además de la distancia (`A2_k3`), seed 2 |
| [v35-lucio](runs/v35-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 72% (62–80) | 88% | 14.51 | castigo 0.02·Σ(Δa)² por cambiar la acción (`suave_c002`), seed 1 |
| [v36-lucio](runs/v36-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 74% (65–82) | 100% | 17.62 | castigo 0.02·Σ(Δa)² por cambiar la acción (`suave_c002`), seed 2 |
| [v40-lucio](runs/v40-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 74% (65–82) | 100% | 19.65 | recompensa `base`, seed 3 |
| [v41-lucio](runs/v41-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 32% (24–42) | 38% | -9.13 | progreso k=3 además de la distancia (`A2_k3`), seed 3 |
| [v42-lucio](runs/v42-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 74% (65–82) | 88% | 15.95 | castigo 0.02·Σ(Δa)² por cambiar la acción (`suave_c002`), seed 3 |
| [v50-lucio](runs/v50-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 70% (60–78) | 100% | 17.15 | recompensa `base`, `--log_std_init -0.5` (desvío inicial 0.61), seed 1 |
| [v51-lucio](runs/v51-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 72% (62–80) | 88% | 13.85 | recompensa `base`, `--log_std_init -0.5` (desvío inicial 0.61), seed 2 |
| [v52-lucio](runs/v52-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 73% (64–81) | 88% | 16.48 | recompensa `base`, `--log_std_init -0.5` (desvío inicial 0.61), seed 42 |
| [v53-lucio](runs/v53-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 30% (22–40) | 38% | -4.03 | castigo por bajar estando afuera y cerca del tope (`bajada_k03`), seed 42 |
| [v54-lucio](runs/v54-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 89% (81–94) | 100% | 19.14 | castigo a la acción + castigo por bajar estando afuera (`suave_bajada`), seed 42 |
| [v55-lucio](runs/v55-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 77% (68–84) | 100% | 18.98 | castigo por bajar estando afuera y cerca del tope (`bajada_k03`), seed 1 |
| [v56-lucio](runs/v56-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 84% (76–90) | 100% | 18.14 | castigo a la acción + castigo por bajar estando afuera (`suave_bajada`), seed 1 |
| [v57-lucio](runs/v57-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 75% (66–82) | 100% | 20.17 | castigo 0.02·Σ(Δa)² por cambiar la acción (`suave_c002`), `--log_std_init -0.5` (desvío inicial 0.61), seed 42 |
| [v58-lucio](runs/v58-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 81% (72–88) | 100% | 20.18 | castigo 0.02·Σ(Δa)² por cambiar la acción (`suave_c002`), `--log_std_init -0.5` (desvío inicial 0.61), seed 1 |
| [v63-lucio](runs/v63-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 91% (84–95) | 100% | 19.60 | castigo a la acción + castigo por bajar estando afuera (`suave_bajada`), seed 2 |
| [v64-lucio](runs/v64-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 88% (80–93) | 100% | 18.26 | castigo a la acción + castigo por bajar estando afuera (`suave_bajada`), seed 3 |
