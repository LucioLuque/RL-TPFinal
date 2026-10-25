# v95-lucio

Cambio: premio al aterrizar 25 − 100·d_xy (`suave_bajada_centro`) con desvío inicial 0.61, seed 1

| | v66-lucio | v95-lucio |
|---|---|---|
| Éxito final (100 ep.) | 97% (92–99) | 94% (88–97) |
| Éxito best (100 ep.) | 96% (90–98) | 85% (77–91) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 18.13 | 12.89 |
| Largo ep. (best) | 56.8 | 56.5 |
| Best en timestep | 1,500,000 | 1,300,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | exito 97, choque_plataforma 2, tiempo 1 | exito 94, choque_plataforma 6 |
| Final: centro, mediana / < 5 cm | 7.1 cm / 28% | 7.5 cm / 30% |
| Final: llega a tocar a (mediana) | 0.46 m/s | 0.45 m/s |
| Final: Δacción / Δv pedida (p95) | 0.11 / 0.100 (0.271) m/s | 0.16 / 0.117 (0.321) m/s |
| Final: inclinación RMS / jerk | 7.8° / 32 m/s³ | 8.1° / 34 m/s³ |

## Qué cambió
- Lo mismo que v94, con la seed 1. Se compara con v66 (`suave_bajada` + desvío 0.61, seed 1).

## Por qué
Segunda seed de `suave_bajada_centro` + desvío 0.61.

## Resultado
- 94 % contra 97 % de v66 (intervalos que se pisan). Centro 7.5 contra 7.1 cm; menos suave (Δv pedida 0.117 contra
  0.100).
- Con v94: `suave_bajada_centro` + desvío 0.61 tampoco mejora a `suave_bajada` + desvío 0.61. Se descarta la variante.

## Próximo paso
- Ninguno con esta variante.
