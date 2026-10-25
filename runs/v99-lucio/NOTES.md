# v99-lucio

Cambio: castigo a la acción 0.03 (`suave_bajada_c003`) con desvío inicial 0.61, seed 1

| | v66-lucio | v99-lucio |
|---|---|---|
| Éxito final (100 ep.) | 97% (92–99) | 99% (95–100) |
| Éxito best (100 ep.) | 96% (90–98) | 91% (84–95) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 18.13 | 20.09 |
| Largo ep. (best) | 56.8 | 44.6 |
| Best en timestep | 1,500,000 | 1,100,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | exito 97, choque_plataforma 2, tiempo 1 | exito 99, choque_inclinacion 1 |
| Final: centro, mediana / < 5 cm | 7.1 cm / 28% | 6.1 cm / 36% |
| Final: llega a tocar a (mediana) | 0.46 m/s | 0.48 m/s |
| Final: Δacción / Δv pedida (p95) | 0.11 / 0.100 (0.271) m/s | 0.07 / 0.083 (0.213) m/s |
| Final: inclinación RMS / jerk | 7.8° / 32 m/s³ | 7.6° / 31 m/s³ |

## Qué cambió
- Recompensa: `suave_bajada` con `reward_action_coef` 0.02 → 0.03. `--log_std_init -0.5`. Se compara con v66
  (`suave_bajada` + desvío 0.61, seed 1) y v92 (castigo 0.05, misma seed: 61 %).

## Por qué
Punto intermedio entre 0.02 (robusta) y 0.05 (la más suave, pero 2 de 4 seeds aprenden tarde), probado con la seed que
aprendió tarde con 0.05.

## Resultado
- **99 % en el modelo final** (v66: 97 %; v92 con 0.05: 61 %). Aprende a tiempo: evals de 8 episodios 62 % a 0.8M y
  100 % desde 1.0M.
- Más suave que v66: Δv pedida 0.083 m/s contra 0.100 (p95 0.21 contra 0.27); menos que `c005` (~0.05). Centro 6.1 cm
  (v66: 7.1), 36 % a menos de 5 cm.
- Una sola seed.

## Próximo paso
- Seeds 42 y 2 (v101, v102).
