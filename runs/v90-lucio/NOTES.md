# v90-lucio

Cambio: premio al aterrizar 25 − 100·d_xy (`suave_bajada_centro`), seed 2

| | v63-lucio | v90-lucio |
|---|---|---|
| Éxito final (100 ep.) | 93% (86–97) | 87% (79–92) |
| Éxito best (100 ep.) | 91% (84–95) | 64% (54–73) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 19.60 | 10.59 |
| Largo ep. (best) | 54.1 | 68.4 |
| Best en timestep | 1,500,000 | 1,000,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | exito 93, tiempo 1, choque_inclinacion 2, choque_plataforma 4 | exito 87, tiempo 3, choque_plataforma 7, choque_inclinacion 3 |
| Final: centro, mediana / < 5 cm | 7.0 cm / 24% | 10.8 cm / 15% |
| Final: llega a tocar a (mediana) | 0.43 m/s | 0.41 m/s |
| Final: Δacción / Δv pedida (p95) | 0.30 / 0.152 (0.443) m/s | 0.15 / 0.092 (0.317) m/s |
| Final: inclinación RMS / jerk | 9.2° / 37 m/s³ | 10.8° / 32 m/s³ |

## Qué cambió
- Lo mismo que v84 y v87 (`landing_dxy_coef` 100), con la seed 2. Se compara con v63 (`suave_bajada`, seed 2).

## Por qué
Tercera seed de `suave_bajada_centro`.

## Resultado
- 87 % en el modelo final contra 93 % de v63 (intervalos que se pisan). **Centra peor** (10.8 contra 7.0 cm de
  mediana) y es más suave (Δv pedida 0.092 contra 0.152).
- Las 3 seeds de `suave_bajada_centro`: 96 / 83 / 87 % → 89 % de media, contra 92 / 88 / 93 % de `suave_bajada` con las
  mismas seeds; centro 8.6 / 8.0 / 10.8 cm contra 8.1 / 9.6 / 7.0. **No mejora ni el éxito ni el centrado.**

## Próximo paso
- Descartar el premio terminal al centro. Si se quiere centrar, hay que actuar antes de tocar.
