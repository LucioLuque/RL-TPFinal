# Experimentos

Indice generado por `python -m tools.experiments_index` (no editar a mano). El detalle de cada corrida
esta en `runs/<run_id>/NOTES.md` (escrito con `/registrar-corrida`) y `runs/<run_id>/run.json`.

Columnas del modelo final (100 ep.): centro = mediana de la distancia al centro de la plataforma en los
aterrizajes; Δv pedida = cambio medio por paso de la velocidad pedida; inclinación = RMS de roll y pitch en vuelo.

| Run | Autor | Fecha | Estado | Timesteps | Éxito final (100 ep.) | Éxito best (100 ep.) | Best éxito (8 ep.) | Best reward | Centro final (cm) | Δv pedida final (m/s) | Inclinación final (°) | Cambio |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| [v16-lucio](runs/v16-lucio/) | lucio | 2026-10-04 | finished | 200,704 | 4% (2–10) | 4% (2–10) | 0% | -9.16 | 12.7 | 0.087 | 7.6 | normalización fija (sin VecNormalize), dron a 0.6 m/s y contacto base-tope |
| [v17-lucio](runs/v17-lucio/) | lucio | 2026-10-04 | finished | 5,001,216 | 99% (95–100) | 88% (80–93) | 100% | 20.63 | 6.5 | 0.418 | 7.5 | misma configuración que v16, entrenada 5M pasos en vez de 200k |
| [v18-lucio](runs/v18-lucio/) | lucio | 2026-10-04 | finished | 1,503,232 | 0% (0–4) | 0% (0–4) | 0% | 3.58 | - | 0.418 | 9.1 | recompensa A1: progreso (k=10) en vez de castigo por distancia |
| [v19-lucio](runs/v19-lucio/) | lucio | 2026-10-04 | finished | 1,503,232 | 1% (0–5) | 26% (18–35) | 38% | -10.78 | 2.6 | 0.343 | 10.8 | recompensa A2: progreso (k=10) además del castigo por distancia |
| [v20-lucio](runs/v20-lucio/) | lucio | 2026-10-04 | finished | 1,503,232 | 0% (0–4) | 0% (0–4) | 0% | -31.92 | - | 0.232 | 9.3 | recompensa B: castigo por choque −50 (antes −10) |
| [v21-lucio](runs/v21-lucio/) | lucio | 2026-10-04 | finished | 1,503,232 | 72% (62–80) | 65% (55–74) | 88% | 14.72 | 7.9 | 0.259 | 7.4 | base de referencia con el PID arreglado (1.5M pasos) |
| [v22-lucio](runs/v22-lucio/) | lucio | 2026-10-04 | finished | 1,503,232 | 35% (26–45) | 35% (26–45) | 38% | -4.45 | 9.6 | 0.474 | 8.6 | recompensa XY: distancia horizontal pesada 3 veces más que la altura |
| [v23-lucio](runs/v23-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 64% (54–73) | 75% (66–82) | 88% | 23.60 | 4.1 | 0.267 | 7.2 | progreso k=3 además de la distancia (`A2_k3`), seed 42 |
| [v24-lucio](runs/v24-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 72% (62–80) | 67% (57–75) | 100% | 19.65 | 8.3 | 0.133 | 7.3 | castigo 0.02·Σ(Δa)² por cambiar la acción (`suave_c002`), seed 42 |
| [v25-lucio](runs/v25-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 72% (62–80) | 69% (59–77) | 88% | 27.83 | 8.6 | 0.358 | 6.7 | shaping por potencial k=10 sumado a `base` (`PBRS_k10`), seed 42 |
| [v26-lucio](runs/v26-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 74% (65–82) | 66% (56–74) | 100% | 20.61 | 5.6 | 0.296 | 6.7 | progreso k=1 además de la distancia (`A2_k1`), seed 42 |
| [v27-lucio](runs/v27-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 2% (1–7) | 35% (26–45) | 62% | 6.34 | 6.5 | 0.555 | 6.8 | progreso k=3 que mide solo lo que se movió el dron (`A2_k3_drone`), seed 42 |
| [v28-lucio](runs/v28-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 0% (0–4) | 0% (0–4) | 0% | -12.87 | - | 0.500 | 9.6 | castigo por estar bajo y afuera de la plataforma (`borde_k1`), seed 42 |
| [v29-lucio](runs/v29-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 0% (0–4) | 10% (6–17) | 12% | -12.78 | - | 0.334 | 10.0 | recompensa `base`, seed 1 |
| [v30-lucio](runs/v30-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 76% (67–83) | 74% (65–82) | 100% | 19.09 | 7.2 | 0.183 | 7.5 | recompensa `base`, seed 2 |
| [v33-lucio](runs/v33-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 64% (54–73) | 64% (54–73) | 88% | 15.92 | 8.1 | 0.352 | 6.6 | progreso k=3 además de la distancia (`A2_k3`), seed 1 |
| [v34-lucio](runs/v34-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 80% (71–87) | 81% (72–88) | 88% | 18.05 | 6.8 | 0.253 | 7.0 | progreso k=3 además de la distancia (`A2_k3`), seed 2 |
| [v35-lucio](runs/v35-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 76% (67–83) | 72% (62–80) | 88% | 14.51 | 6.5 | 0.144 | 7.5 | castigo 0.02·Σ(Δa)² por cambiar la acción (`suave_c002`), seed 1 |
| [v36-lucio](runs/v36-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 75% (66–82) | 74% (65–82) | 100% | 17.62 | 10.5 | 0.076 | 8.0 | castigo 0.02·Σ(Δa)² por cambiar la acción (`suave_c002`), seed 2 |
| [v40-lucio](runs/v40-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 70% (60–78) | 74% (65–82) | 100% | 19.65 | 5.6 | 0.240 | 6.9 | recompensa `base`, seed 3 |
| [v41-lucio](runs/v41-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 55% (45–64) | 32% (24–42) | 38% | -9.13 | 11.8 | 0.265 | 8.4 | progreso k=3 además de la distancia (`A2_k3`), seed 3 |
| [v42-lucio](runs/v42-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 71% (62–79) | 74% (65–82) | 88% | 15.95 | 8.9 | 0.093 | 7.8 | castigo 0.02·Σ(Δa)² por cambiar la acción (`suave_c002`), seed 3 |
| [v50-lucio](runs/v50-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 79% (70–86) | 70% (60–78) | 100% | 17.15 | 6.5 | 0.216 | 6.9 | recompensa `base`, `--log_std_init -0.5` (desvío inicial 0.61), seed 1 |
| [v51-lucio](runs/v51-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 76% (67–83) | 72% (62–80) | 88% | 13.85 | 9.6 | 0.179 | 6.7 | recompensa `base`, `--log_std_init -0.5` (desvío inicial 0.61), seed 2 |
| [v52-lucio](runs/v52-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 81% (72–88) | 73% (64–81) | 88% | 16.48 | 4.7 | 0.186 | 7.4 | recompensa `base`, `--log_std_init -0.5` (desvío inicial 0.61), seed 42 |
| [v53-lucio](runs/v53-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 26% (18–35) | 30% (22–40) | 38% | -4.03 | 7.6 | 0.284 | 9.2 | castigo por bajar estando afuera y cerca del tope (`bajada_k03`), seed 42 |
| [v54-lucio](runs/v54-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 92% (85–96) | 89% (81–94) | 100% | 19.14 | 8.1 | 0.100 | 8.1 | castigo a la acción + castigo por bajar estando afuera (`suave_bajada`), seed 42 |
| [v55-lucio](runs/v55-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 81% (72–88) | 77% (68–84) | 100% | 18.98 | 9.3 | 0.186 | 8.3 | castigo por bajar estando afuera y cerca del tope (`bajada_k03`), seed 1 |
| [v56-lucio](runs/v56-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 88% (80–93) | 84% (76–90) | 100% | 18.14 | 9.6 | 0.091 | 8.1 | castigo a la acción + castigo por bajar estando afuera (`suave_bajada`), seed 1 |
| [v57-lucio](runs/v57-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 93% (86–97) | 75% (66–82) | 100% | 20.17 | 6.0 | 0.088 | 7.2 | castigo 0.02·Σ(Δa)² por cambiar la acción (`suave_c002`), `--log_std_init -0.5` (desvío inicial 0.61), seed 42 |
| [v58-lucio](runs/v58-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 85% (77–91) | 81% (72–88) | 100% | 20.18 | 6.9 | 0.079 | 7.0 | castigo 0.02·Σ(Δa)² por cambiar la acción (`suave_c002`), `--log_std_init -0.5` (desvío inicial 0.61), seed 1 |
| [v59-lucio](runs/v59-lucio/) | lucio | 2026-10-25 | finished | 1,503,232 | 100% (96–100) | 99% (95–100) | 100% | 20.61 | 5.3 | 0.126 | 7.4 | `suave_c002` con `--log_std_init -0.5` (desvío inicial 0.61), seed 2 |
| [v60-lucio](runs/v60-lucio/) | lucio | 2026-10-25 | finished | 1,503,232 | 78% (69–85) | 79% (70–86) | 100% | 17.84 | 8.3 | 0.170 | 8.1 | recompensa `base` con `--log_std_init -1.0` (desvío inicial 0.37), seed 42 |
| [v61-lucio](runs/v61-lucio/) | lucio | 2026-10-25 | running | - | - | - | - | - | - | - | - | _sin registrar_ |
| [v62-lucio](runs/v62-lucio/) | lucio | 2026-10-25 | running | - | - | - | - | - | - | - | - | _sin registrar_ |
| [v63-lucio](runs/v63-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 93% (86–97) | 91% (84–95) | 100% | 19.60 | 7.0 | 0.152 | 9.2 | castigo a la acción + castigo por bajar estando afuera (`suave_bajada`), seed 2 |
| [v64-lucio](runs/v64-lucio/) | lucio | 2026-10-15 | finished | 1,503,232 | 95% (89–98) | 88% (80–93) | 100% | 18.26 | 8.3 | 0.204 | 8.9 | castigo a la acción + castigo por bajar estando afuera (`suave_bajada`), seed 3 |
| [v65-lucio](runs/v65-lucio/) | lucio | 2026-10-24 | finished | 1,503,232 | 92% (85–96) | 89% (81–94) | 100% | 18.73 | 5.2 | 0.059 | 7.7 | `suave_bajada` con `--log_std_init -0.5` (desvío inicial 0.61), seed 42 |
| [v66-lucio](runs/v66-lucio/) | lucio | 2026-10-24 | finished | 1,503,232 | 97% (92–99) | 96% (90–98) | 100% | 18.13 | 7.1 | 0.100 | 7.8 | `suave_bajada` con `--log_std_init -0.5` (desvío inicial 0.61), seed 1 |
| [v67-lucio](runs/v67-lucio/) | lucio | 2026-10-24 | finished | 1,503,232 | 89% (81–94) | 87% (79–92) | 100% | 19.10 | 6.5 | 0.090 | 7.7 | `suave_bajada` con `--log_std_init -0.5` (desvío inicial 0.61), seed 2 |
| [v69-lucio](runs/v69-lucio/) | lucio | 2026-10-25 | finished | 3,002,368 | 99% (95–100) | 99% (95–100) | 100% | 21.07 | 3.7 | 0.119 | 7.0 | `suave_bajada` entrenada 3M pasos en vez de 1.5M, seed 42 |
| [v82-lucio](runs/v82-lucio/) | lucio | 2026-10-24 | finished | 1,503,232 | 0% (0–4) | 0% (0–4) | 0% | -63.62 | - | 0.000 | 0.0 | `suave_bajada` + castigo 0.1·\|Δv pedida/0.6\|² (`suave_bajada_v01`), seed 42: flota |
| [v83-lucio](runs/v83-lucio/) | lucio | 2026-10-25 | finished | 1,503,232 | 0% (0–4) | 0% (0–4) | 0% | -12.53 | - | 0.041 | 8.3 | `suave_bajada` + castigo por llegar rápido al tope (`suave_bajada_flare`), seed 42: flota |
| [v84-lucio](runs/v84-lucio/) | lucio | 2026-10-25 | finished | 1,503,232 | 96% (90–98) | 83% (74–89) | 100% | 12.82 | 8.6 | 0.060 | 8.4 | premio al aterrizar 25 − 100·d_xy en vez de 25 − 50·d_xy (`suave_bajada_centro`), seed 42 |
| [v86-lucio](runs/v86-lucio/) | lucio | 2026-10-25 | finished | 1,503,232 | 0% (0–4) | 0% (0–4) | 0% | -13.50 | - | 0.030 | 7.7 | `suave_bajada` + castigo por llegar rápido al tope (`suave_bajada_flare`), seed 1: flota |
| [v87-lucio](runs/v87-lucio/) | lucio | 2026-10-25 | finished | 1,503,232 | 83% (74–89) | 85% (77–91) | 100% | 15.98 | 8.0 | 0.109 | 9.1 | premio al aterrizar 25 − 100·d_xy (`suave_bajada_centro`), seed 1 |
| [v90-lucio](runs/v90-lucio/) | lucio | 2026-10-25 | finished | 1,503,232 | 87% (79–92) | 64% (54–73) | 100% | 10.59 | 10.8 | 0.092 | 10.8 | premio al aterrizar 25 − 100·d_xy (`suave_bajada_centro`), seed 2 |
| [v91-lucio](runs/v91-lucio/) | lucio | 2026-10-25 | finished | 1,503,232 | 100% (96–100) | 97% (92–99) | 100% | 20.80 | 5.1 | 0.051 | 7.5 | castigo a la acción 0.05 en vez de 0.02 (`suave_bajada_c005`) con desvío inicial 0.61, seed 42 |
| [v92-lucio](runs/v92-lucio/) | lucio | 2026-10-25 | finished | 1,503,232 | 61% (51–70) | 42% (33–52) | 62% | 8.84 | 12.3 | 0.044 | 8.6 | castigo a la acción 0.05 (`suave_bajada_c005`) con desvío inicial 0.61, seed 1 |
| [v93-lucio](runs/v93-lucio/) | lucio | 2026-10-25 | finished | 1,503,232 | 97% (92–99) | 95% (89–98) | 100% | 21.14 | 6.3 | 0.059 | 7.6 | castigo a la acción 0.05 (`suave_bajada_c005`) con desvío inicial 0.61, seed 2 |
| [v94-lucio](runs/v94-lucio/) | lucio | 2026-10-25 | finished | 1,503,232 | 92% (85–96) | 92% (85–96) | 100% | 13.07 | 7.4 | 0.051 | 8.2 | premio al aterrizar 25 − 100·d_xy (`suave_bajada_centro`) con desvío inicial 0.61, seed 42 |
| [v95-lucio](runs/v95-lucio/) | lucio | 2026-10-25 | finished | 1,503,232 | 94% (88–97) | 85% (77–91) | 100% | 12.89 | 7.5 | 0.117 | 8.1 | premio al aterrizar 25 − 100·d_xy (`suave_bajada_centro`) con desvío inicial 0.61, seed 1 |
| [v96-lucio](runs/v96-lucio/) | lucio | 2026-10-25 | finished | 1,503,232 | 0% (0–4) | 0% (0–4) | 0% | -63.64 | - | 0.000 | 0.0 | castigo a la acción 0.1 (`suave_bajada_c01`) con desvío inicial 0.61, seed 42: no se mueve |
| [v97-lucio](runs/v97-lucio/) | lucio | 2026-10-25 | finished | 1,503,232 | 42% (33–52) | 40% (31–50) | 50% | -0.50 | 13.8 | 0.031 | 8.3 | castigo a la acción 0.1 (`suave_bajada_c01`) con desvío inicial 0.61, seed 1 |
| [v98-lucio](runs/v98-lucio/) | lucio | 2026-10-25 | finished | 1,503,232 | 72% (62–80) | 78% (69–85) | 88% | 17.05 | 13.4 | 0.041 | 8.1 | castigo a la acción 0.05 (`suave_bajada_c005`) con desvío inicial 0.61, seed 3 |
| [v99-lucio](runs/v99-lucio/) | lucio | 2026-10-25 | finished | 1,503,232 | 99% (95–100) | 91% (84–95) | 100% | 20.09 | 6.1 | 0.083 | 7.6 | castigo a la acción 0.03 (`suave_bajada_c003`) con desvío inicial 0.61, seed 1 |
| [v100-lucio](runs/v100-lucio/) | lucio | 2026-10-25 | finished | 3,002,368 | 100% (96–100) | 100% (96–100) | 100% | 21.68 | 3.3 | 0.072 | 7.3 | `suave_bajada_c005` + desvío 0.61 entrenada 3M pasos en vez de 1.5M, seed 1 |
| [v101-lucio](runs/v101-lucio/) | lucio | 2026-10-25 | finished | 1,503,232 | 95% (89–98) | 96% (90–98) | 100% | 19.87 | 5.4 | 0.073 | 7.5 | castigo a la acción 0.03 (`suave_bajada_c003`) con desvío inicial 0.61, seed 42 |
| [v102-lucio](runs/v102-lucio/) | lucio | 2026-10-25 | finished | 1,503,232 | 99% (95–100) | 98% (93–99) | 100% | 19.42 | 7.2 | 0.086 | 7.5 | castigo a la acción 0.03 (`suave_bajada_c003`) con desvío inicial 0.61, seed 2 |
| [v103-lucio](runs/v103-lucio/) | lucio | 2026-10-25 | interrupted | - | - | 100% (96–100) | - | - | - | - | - | `suave_bajada_c003` + desvío 0.61 a 3M pasos, seed 42 (cortada en 2.8M; se evalúa el best) |
| [v104-lucio](runs/v104-lucio/) | lucio | 2026-10-25 | interrupted | - | - | 100% (96–100) | - | - | - | - | - | `suave_bajada_c005` + desvío 0.61 a 3M pasos, seed 3 (cortada en 2.95M; se evalúa el best) |
