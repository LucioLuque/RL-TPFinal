# v94-lucio

Cambio: premio al aterrizar 25 − 100·d_xy (`suave_bajada_centro`) con desvío inicial 0.61, seed 42

| | v65-lucio | v94-lucio |
|---|---|---|
| Éxito final (100 ep.) | 92% (85–96) | 92% (85–96) |
| Éxito best (100 ep.) | 89% (81–94) | 92% (85–96) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 18.73 | 13.07 |
| Largo ep. (best) | 59.4 | 52.1 |
| Best en timestep | 1,500,000 | 1,500,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | exito 92, tiempo 1, choque_plataforma 7 | exito 92, choque_plataforma 5, tiempo 1, choque_inclinacion 2 |
| Final: centro, mediana / < 5 cm | 5.2 cm / 42% | 7.4 cm / 25% |
| Final: llega a tocar a (mediana) | 0.47 m/s | 0.44 m/s |
| Final: Δacción / Δv pedida (p95) | 0.04 / 0.059 (0.159) m/s | 0.04 / 0.051 (0.147) m/s |
| Final: inclinación RMS / jerk | 7.7° / 28 m/s³ | 8.2° / 28 m/s³ |

## Qué cambió
- `suave_bajada_centro` con `--log_std_init -0.5`. Se compara con v65 (`suave_bajada` + desvío 0.61, seed 42).

## Por qué
Combinar el premio al centro (v84: 96 %) con el desvío 0.61 (v65–v67: más suaves y centradas).

## Resultado
- 92 %, igual que v65. **Centra peor** (7.4 contra 5.2 cm; 25 % contra 42 % a menos de 5 cm); igual de suave.
- Aprende más tarde: los evals de 8 episodios no pasan de 50 % hasta 1.4M.

## Próximo paso
- Ver v95 (seed 1). Si no mejora, descartar `suave_bajada_centro` también con desvío 0.61.
