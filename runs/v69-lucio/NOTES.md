# v69-lucio

Cambio: `suave_bajada` entrenada 3M pasos en vez de 1.5M, seed 42

| | v54-lucio | v69-lucio |
|---|---|---|
| Éxito final (100 ep.) | 92% (85–96) | 99% (95–100) |
| Éxito best (100 ep.) | 89% (81–94) | 99% (95–100) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 19.14 | 21.07 |
| Largo ep. (best) | 51.1 | 45.8 |
| Best en timestep | 1,500,000 | 2,800,000 |
| Timesteps totales | 1,503,232 | 3,002,368 |
| Final: cómo terminan | exito 92, choque_plataforma 5, choque_inclinacion 1, tiempo 2 | exito 99, choque_plataforma 1 |
| Final: centro, mediana / < 5 cm | 8.1 cm / 24% | 3.7 cm / 60% |
| Final: llega a tocar a (mediana) | 0.45 m/s | 0.49 m/s |
| Final: Δacción / Δv pedida (p95) | 0.13 / 0.100 (0.288) m/s | 0.15 / 0.119 (0.309) m/s |
| Final: inclinación RMS / jerk | 8.1° / 32 m/s³ | 7.0° / 35 m/s³ |

## Qué cambió
- Solo la duración: 1.5M → 3M pasos. Misma recompensa (`suave_bajada`), seed (42), exploración (desvío 1) e
  hiperparámetros que v54, que es la comparación. `env.py` con los términos de 2026-10-24 apagados (mismo entorno).

## Por qué
Prioridad 3 de `cola_pendiente.txt`: las curvas de `suave_bajada` seguían subiendo a 1.5M, y v17 (`base`, 5M) da 99 %
con el modelo final (reevaluado el 2026-10-24).

## Resultado
- **99 % en el modelo final** (IC 95–100 %; v54: 92 %), 1 choque contra el borde. En 200 episodios extra (seeds
  1000–1199, no guardados en archivo): **199/200**.
- **La más centrada del proyecto:** 3.7 cm de mediana y 60 % a menos de 5 cm (v54: 8.1 cm y 24 %). En los 200 extra:
  4.2 cm y 59 %. El premio al centro no había logrado esto (`suave_bajada_centro`); entrenar más sí.
- **No es más suave:** Δv pedida 0.119 m/s (v54: 0.100), y llega a tocar igual de rápido (0.49 m/s).
- Evals de 8 episodios: 100 % casi siempre desde 1.3M; el best (2.8M) da lo mismo que el final.
- Una sola seed.

## Próximo paso
- Más seeds a 3M. Y entrenar 3M las variantes más suaves (`suave_bajada` + desvío 0.61, `c005` + desvío 0.61), cuyas
  seeds lentas no terminan de aprender a 1.5M.
