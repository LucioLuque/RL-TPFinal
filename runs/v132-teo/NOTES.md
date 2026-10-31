# v132-teo

Cambio: `suave_bajada` + desvío 0.61 entrenada 3M en vez de 1.5M, seed 2 (control de `c003`)

| | v67-lucio | v132-teo |
|---|---|---|
| Éxito final (100 ep.) | 89% (81–94) | 100% (96–100) |
| Éxito best (100 ep.) | 87% (79–92) | 87% (79–92) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 19.10 | 20.47 |
| Largo ep. (best) | 57.1 | 48.2 |
| Best en timestep | 1,400,000 | 1,600,000 |
| Timesteps totales | 1,500,000 | 3,000,000 |
| Final: cómo terminan | exito 89, choque_plataforma 9, tiempo 2 | exito 100 |
| Final: centro, mediana / < 5 cm | 6.5 cm / 38% | 4.7 cm / 59% |
| Final: llega a tocar a (mediana, m/s) | 0.51 | 0.50 |
| Final: Δacción / Δv pedida (p95) | 0.096 / 0.090 (0.238) m/s | 0.100 / 0.098 (0.255) m/s |
| Final: inclinación RMS / jerk (m/s³) | 7.7° / 32 | 6.8° / 34 |

## Qué cambió
- Solo la duración: 1.5M → 3M pasos. Misma recompensa (`suave_bajada`, la de por defecto: castigo a la acción 0.02),
  seed (2), exploración (`--log_std_init -0.5`) e hiperparámetros que v67-lucio. Corre con el código de esta noche
  (61c0368 + `diff.patch`), cuyas opciones nuevas están todas apagadas por defecto. Laboratorio S004, 3 corridas en paralelo.

## Por qué
Control de las candidatas a recompensa final. `c003` y `c005` a 3M dan 100 %, pero no se sabía cuánto de eso es la
recompensa y cuánto el entrenamiento más largo. Es la misma exploración y duración, con la recompensa por defecto.

## Resultado
- 100 % (v67 a 1.5M: 89 %). El best (elegido a 1.6M con 8 episodios) da 87 % en 100: otra vez el final es mejor que
  el best. Centra mejor (4.7 contra 6.5 cm), con la misma suavidad (Δv pedida 0.098 contra 0.090 m/s).
- **`suave_bajada` a 3M con 3 seeds** (v130–v132, contra `c003` en v105–v107): 100 % en las 3, igual que `c003`.
  Δv pedida 0.071 / 0.069 / 0.098 (media 0.079) contra 0.063 / 0.072 / 0.063 (0.066). Centro 4.6 / 3.3 / 4.7 cm
  contra 4.1 / 4.5 / 3.7. Aprende igual (50 % a 0.6–0.85M).
- **La mejora de 1.5M a 3M se debe sobre todo al entrenamiento más largo** (las 3 seeds de `suave_bajada` pasan de
  89–97 % a 100 % y centran mejor). `c003` es algo más suave en promedio (~15 %), pero las seeds se superponen
  (v131, de `suave_bajada`, es más suave que v106, de `c003`).

## Próximo paso
- Para decidir la recompensa final (`TODO.md`, punto 1): entre `suave_bajada` y `c003` la diferencia es chica; `c003`
  es algo más suave y no tuvo fallas en 3 seeds.
