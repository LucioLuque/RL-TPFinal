# v62-lucio

Cambio: recompensa `base` con `--log_std_init -1.0` (desvío inicial 0.37), seed 2

| | v51-lucio | v62-lucio |
|---|---|---|
| Éxito final (100 ep.) | 76% (67–83) | 87% (79–92) |
| Éxito best (100 ep.) | 72% (62–80) | 86% (78–92) |
| Best éxito (8 ep.) | 88% | 100% |
| Best reward | 13.85 | 18.42 |
| Largo ep. (best) | 52.1 | 46.5 |
| Best en timestep | 1,200,000 | 1,500,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | exito 76, tiempo 1, choque_plataforma 23 | exito 87, choque_plataforma 11, choque_inclinacion 2 |
| Final: centro, mediana / < 5 cm | 9.6 cm / 16% | 7.2 cm / 22% |
| Final: llega a tocar a (mediana) | 0.41 m/s | 0.42 m/s |
| Final: Δacción / Δv pedida (p95) | 0.36 / 0.179 (0.436) m/s | 0.14 / 0.130 (0.306) m/s |
| Final: inclinación RMS / jerk | 6.7° / 38 m/s³ | 7.3° / 36 m/s³ |

## Qué cambió
- Lo mismo que v60 y v61 (desvío 0.61 → 0.37 sobre `base`), con la seed 2. Se compara con v51 (`base` + desvío 0.61, seed 2).

## Por qué
Tercera seed de `base` con desvío 0.37.

## Resultado
- **87 % en el modelo final** contra 76 % de v51 (intervalos que se pisan). Choca el borde 11 veces de 100 (v51: 23), más
  suave (Δv pedida 0.130 contra 0.179 m/s) y algo más centrada (7.2 contra 9.6 cm).
- Aprende tarde: evals de 8 episodios irregulares (0 % entre 0.8M y 0.9M) y 88–100 % desde 1.0M.
- **Las 3 seeds de `base` + desvío 0.37: 78 / 91 / 87 % → 85 %**, contra 79 % con desvío 0.61 (v50–v52) y 49 % con
  desvío 1 (v21, v29, v30). Menos ruido de exploración sigue ayudando, pero de 0.61 a 0.37 la mejora es chica (mejor en
  2 de 3 seeds, intervalos que se pisan) y aprende más tarde.

## Próximo paso
- Probar el desvío 0.37 con las recompensas candidatas (`suave_bajada_c003`), no solo con `base` (TODO.md, punto 2).
