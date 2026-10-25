# v96-lucio

Cambio: castigo a la acción 0.1 (`suave_bajada_c01`) con desvío inicial 0.61, seed 42: no se mueve

| | v65-lucio | v96-lucio |
|---|---|---|
| Éxito final (100 ep.) | 92% (85–96) | 0% (0–4) |
| Éxito best (100 ep.) | 89% (81–94) | 0% (0–4) |
| Best éxito (8 ep.) | 100% | 0% |
| Best reward | 18.73 | -63.64 |
| Largo ep. (best) | 59.4 | 480.0 |
| Best en timestep | 1,500,000 | 100,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | exito 92, tiempo 1, choque_plataforma 7 | tiempo 100 |
| Final: centro, mediana / < 5 cm | 5.2 cm / 42% | – |
| Final: llega a tocar a (mediana) | 0.47 m/s | – |
| Final: Δacción / Δv pedida (p95) | 0.04 / 0.059 (0.159) m/s | 0.00 / 0.000 (0.000) m/s |
| Final: inclinación RMS / jerk | 7.7° / 28 m/s³ | 0.0° / 0 m/s³ |

## Qué cambió
- Recompensa: `suave_bajada` con `reward_action_coef` 0.02 → 0.1. `--log_std_init -0.5`. Se compara con v65 (misma
  seed y exploración, castigo 0.02) y v91 (castigo 0.05: 100 %).

## Por qué
Ver hasta dónde se puede subir el castigo a la acción, después del 100 % de v91.

## Resultado
- **0 %, los 100 episodios por tiempo.** La política determinista no cambia nunca la acción (Δacción 0, inclinación
  0°): queda quieta en el aire. Evals de 8 episodios: 0 % en todos.
- Con 0.1, cambiar la acción cuesta más de lo que el agente espera ganar intentando aterrizar: otra vez la trampa de
  flotar, ahora sin moverse.

## Próximo paso
- Descartar 0.1. El límite está entre 0.05 (aprende, a veces tarde) y 0.1.
