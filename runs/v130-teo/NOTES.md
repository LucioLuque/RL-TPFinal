# v130-teo

Cambio: `suave_bajada` + desvío 0.61 entrenada 3M en vez de 1.5M, seed 42 (control de `c003`)

| | v65-lucio | v130-teo |
|---|---|---|
| Éxito final (100 ep.) | 92% (85–96) | 100% (96–100) |
| Éxito best (100 ep.) | 89% (81–94) | 100% (96–100) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 18.73 | 21.42 |
| Largo ep. (best) | 59.4 | 48.2 |
| Best en timestep | 1,500,000 | 2,200,000 |
| Timesteps totales | 1,500,000 | 3,000,000 |
| Final: cómo terminan | exito 92, tiempo 1, choque_plataforma 7 | exito 100 |
| Final: centro, mediana / < 5 cm | 5.2 cm / 42% | 4.6 cm / 59% |
| Final: llega a tocar a (mediana, m/s) | 0.47 | 0.49 |
| Final: Δacción / Δv pedida (p95) | 0.037 / 0.059 (0.159) m/s | 0.049 / 0.071 (0.176) m/s |
| Final: inclinación RMS / jerk (m/s³) | 7.7° / 28 | 7.3° / 31 |

## Qué cambió
- Solo la duración: 1.5M → 3M pasos. Misma recompensa (`suave_bajada`, la de por defecto: castigo a la acción 0.02),
  seed (42), exploración (`--log_std_init -0.5`) e hiperparámetros que v65-lucio. Corre con el código de esta noche
  (61c0368 + `diff.patch`), cuyas opciones nuevas están todas apagadas por defecto. Laboratorio S004, 3 corridas en paralelo.

## Por qué
Control de las candidatas a recompensa final. `c003` y `c005` a 3M dan 100 %, pero no se sabía cuánto de eso es la
recompensa y cuánto el entrenamiento más largo. Es la misma exploración y duración, con la recompensa por defecto.

## Resultado
- 100 % (v65 a 1.5M: 92 %). Centra mejor (4.6 contra 5.2 cm) y es algo menos suave (Δv pedida 0.071 contra
  0.059 m/s).
- Contra `c003` a 3M con la misma seed (v105: 100 %, 4.1 cm, 0.063 m/s): muy parecida.

## Próximo paso
- Ver v132, que junta las 3 seeds.
