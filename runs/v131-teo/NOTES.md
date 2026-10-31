# v131-teo

Cambio: `suave_bajada` + desvío 0.61 entrenada 3M en vez de 1.5M, seed 1 (control de `c003`)

| | v66-lucio | v131-teo |
|---|---|---|
| Éxito final (100 ep.) | 97% (92–99) | 100% (96–100) |
| Éxito best (100 ep.) | 96% (90–98) | 100% (96–100) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 18.13 | 21.94 |
| Largo ep. (best) | 56.8 | 55.0 |
| Best en timestep | 1,500,000 | 2,800,000 |
| Timesteps totales | 1,500,000 | 3,000,000 |
| Final: cómo terminan | exito 97, choque_plataforma 2, tiempo 1 | exito 100 |
| Final: centro, mediana / < 5 cm | 7.1 cm / 28% | 3.3 cm / 78% |
| Final: llega a tocar a (mediana, m/s) | 0.46 | 0.52 |
| Final: Δacción / Δv pedida (p95) | 0.111 / 0.100 (0.271) m/s | 0.056 / 0.069 (0.180) m/s |
| Final: inclinación RMS / jerk (m/s³) | 7.8° / 32 | 7.4° / 31 |

## Qué cambió
- Solo la duración: 1.5M → 3M pasos. Misma recompensa (`suave_bajada`, la de por defecto: castigo a la acción 0.02),
  seed (1), exploración (`--log_std_init -0.5`) e hiperparámetros que v66-lucio. Corre con el código de esta noche
  (61c0368 + `diff.patch`), cuyas opciones nuevas están todas apagadas por defecto. Laboratorio S004, 3 corridas en paralelo.

## Por qué
Control de las candidatas a recompensa final. `c003` y `c005` a 3M dan 100 %, pero no se sabía cuánto de eso es la
recompensa y cuánto el entrenamiento más largo. Es la misma exploración y duración, con la recompensa por defecto.

## Resultado
- 100 % (v66 a 1.5M: 97 %). Centra mucho mejor (3.3 contra 7.1 cm; 78 % a menos de 5 cm) y es más suave (Δv pedida
  0.069 contra 0.100 m/s).
- Contra `c003` a 3M con la misma seed (v106: 100 %, 4.5 cm, 0.072 m/s): igual o mejor.

## Próximo paso
- Ver v132, que junta las 3 seeds.
