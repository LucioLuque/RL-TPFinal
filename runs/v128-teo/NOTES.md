# v128-teo

Cambio: acción como velocidad + premio por tocar despacio (`suave_bajada_c003_vel_tocar`), seed 1

| | v125-teo | v128-teo |
|---|---|---|
| Éxito final (100 ep.) | 91% (84–95) | 100% (96–100) |
| Éxito best (100 ep.) | 89% (81–94) | 100% (96–100) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 21.60 | 22.51 |
| Largo ep. (best) | 52.0 | 52.8 |
| Best en timestep | 1,800,000 | 3,000,000 |
| Timesteps totales | 3,000,000 | 3,000,000 |
| Final: cómo terminan | choque_plataforma 9, exito 91 | exito 100 |
| Final: centro, mediana / < 5 cm | 4.8 cm / 50% | 5.2 cm / 47% |
| Final: llega a tocar a (mediana, m/s) | 0.48 | 0.45 |
| Final: Δacción / Δv pedida (p95) | 0.223 / 0.096 (0.263) m/s | 0.124 / 0.067 (0.171) m/s |
| Final: inclinación RMS / jerk (m/s³) | 7.2° / 32 | 7.0° / 29 |

## Qué cambió
- Lo mismo que v127-teo (acción como velocidad + `landing_vz_coef: 10`), con la seed 1. Mismo resto que v125-teo.
  Laboratorio S004, 3 corridas en paralelo.

## Por qué
Segunda seed de `suave_bajada_c003_vel_tocar` (ver v127-teo).

## Resultado
- 100 % (v125, sin el premio: 91 %). Más suave que v125 (Δv pedida 0.067 contra 0.096 m/s).
- **Casi no frena:** toca a 0.45 m/s (p90 0.57), contra 0.48 de v125. `dz` saturado en el 80 % de los pasos.

## Próximo paso
- Ver v129, que junta las 3 seeds.
