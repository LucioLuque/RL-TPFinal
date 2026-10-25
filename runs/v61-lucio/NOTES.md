# v61-lucio

Cambio: recompensa `base` con `--log_std_init -1.0` (desvío inicial 0.37), seed 1

| | v50-lucio | v61-lucio |
|---|---|---|
| Éxito final (100 ep.) | 79% (70–86) | 91% (84–95) |
| Éxito best (100 ep.) | 70% (60–78) | 83% (74–89) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 17.15 | 19.07 |
| Largo ep. (best) | 55.0 | 55.6 |
| Best en timestep | 1,300,000 | 1,200,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | exito 79, choque_plataforma 19, tiempo 1, choque_inclinacion 1 | exito 91, choque_plataforma 8, choque_inclinacion 1 |
| Final: centro, mediana / < 5 cm | 6.5 cm / 30% | 6.9 cm / 30% |
| Final: llega a tocar a (mediana) | 0.44 m/s | 0.44 m/s |
| Final: Δacción / Δv pedida (p95) | 0.46 / 0.216 (0.508) m/s | 0.23 / 0.188 (0.440) m/s |
| Final: inclinación RMS / jerk | 6.9° / 43 m/s³ | 7.1° / 45 m/s³ |

## Qué cambió
- Lo mismo que v60 (desvío 0.61 → 0.37 sobre `base`), con la seed 1. Se compara con v50 (`base` + desvío 0.61, seed 1).

## Por qué
Segunda seed de `base` con desvío 0.37.

## Resultado
- **91 % en el modelo final** contra 79 % de v50 (intervalos 84–95 y 70–86: casi no se pisan). Choca el borde 8 veces de
  100 (v50: 19). Centrado y suavidad parecidos.
- Aprende tarde, como v60: evals de 8 episodios por debajo de 40 % hasta 1.1M y 88–100 % desde 1.2M.
- Con dos seeds: 78 % (s42, v60: 81 % con desvío 0.61) y 91 % (s1, v50: 79 %). Falta v62.

## Próximo paso
- Seed 2 (v62).
