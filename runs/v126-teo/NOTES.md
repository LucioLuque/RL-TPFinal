# v126-teo

Cambio: acción como velocidad (`action_mode: velocity`, `suave_bajada_c003_vel`), 3M, seed 2

| | v107-teo | v126-teo |
|---|---|---|
| Éxito final (100 ep.) | 100% (96–100) | 100% (96–100) |
| Éxito best (100 ep.) | 100% (96–100) | 100% (96–100) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 21.51 | 21.02 |
| Largo ep. (best) | 50.2 | 50.9 |
| Best en timestep | 2,700,000 | 2,800,000 |
| Timesteps totales | 3,000,000 | 3,000,000 |
| Final: cómo terminan | exito 100 | exito 100 |
| Final: centro, mediana / < 5 cm | 3.7 cm / 65% | 5.1 cm / 46% |
| Final: llega a tocar a (mediana, m/s) | 0.49 | 0.50 |
| Final: Δacción / Δv pedida (p95) | 0.039 / 0.063 (0.145) m/s | 0.140 / 0.096 (0.230) m/s |
| Final: inclinación RMS / jerk (m/s³) | 7.3° / 30 | 7.0° / 34 |

## Qué cambió
- Lo mismo que v124-teo (acción como velocidad), con la seed 2. Mismo resto que v107-teo. Laboratorio S004, 3 corridas en paralelo.

## Por qué
Tercera seed de `suave_bajada_c003_vel` (ver v124-teo).

## Resultado
- 100 %, pero menos suave (Δv pedida 0.096 contra 0.063 m/s) y menos centrada (5.1 contra 3.7 cm) que v107. Llega a
  8 de 8 de forma estable recién a 2.6M.
- **Acción como velocidad con 3 seeds** (v124–v126, contra `c003` en v105–v107): 100 / 91 / 100 %. **Aprende antes**
  (50 % a ~0.5M contra ~0.7M), pero es **menos suave** (Δv pedida 0.068 / 0.096 / 0.096, media 0.087, contra 0.066) y
  centra algo peor (3.7 / 4.8 / 5.1 cm contra 4.1 / 4.5 / 3.7).
- **No frena:** toca a 0.51 / 0.48 / 0.50 m/s. Sin un término que lo pida, la política sigue pidiendo la máxima
  velocidad de bajada (`dz` saturado en el 78–86 % de los pasos).

## Próximo paso
- Ver v127–v129: la misma acción con premio por tocar despacio.
