# v125-teo

Cambio: acción como velocidad (`action_mode: velocity`, `suave_bajada_c003_vel`), 3M, seed 1

| | v106-teo | v125-teo |
|---|---|---|
| Éxito final (100 ep.) | 100% (96–100) | 91% (84–95) |
| Éxito best (100 ep.) | 100% (96–100) | 89% (81–94) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 21.39 | 21.60 |
| Largo ep. (best) | 46.9 | 52.0 |
| Best en timestep | 2,900,000 | 1,800,000 |
| Timesteps totales | 3,000,000 | 3,000,000 |
| Final: cómo terminan | exito 100 | choque_plataforma 9, exito 91 |
| Final: centro, mediana / < 5 cm | 4.5 cm / 54% | 4.8 cm / 50% |
| Final: llega a tocar a (mediana, m/s) | 0.50 | 0.48 |
| Final: Δacción / Δv pedida (p95) | 0.050 / 0.072 (0.173) m/s | 0.223 / 0.096 (0.263) m/s |
| Final: inclinación RMS / jerk (m/s³) | 7.4° / 31 | 7.2° / 32 |

## Qué cambió
- Lo mismo que v124-teo (acción como velocidad), con la seed 1. Mismo resto que v106-teo. Laboratorio S004, 3 corridas en paralelo.

## Por qué
Segunda seed de `suave_bajada_c003_vel` (ver v124-teo).

## Resultado
- **91 %** (9 choques contra la plataforma); el best da 89 %. Los evals de 8 episodios siguen oscilando entre 6 y 8 de
  8 hasta el final: no termina de estabilizarse.
- Aprende antes (50 % a 0.54M; v106: 0.79M), pero es **menos suave**: Δv pedida 0.096 contra 0.072 m/s. `dz`
  saturado en el 86 % de los pasos, y las 3 direcciones a la vez en el 27 % (v107: 6 %).
- Toca a 0.48 m/s.

## Próximo paso
- Ver v126 (3 seeds).
