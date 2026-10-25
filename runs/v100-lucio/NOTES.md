# v100-lucio

Cambio: `suave_bajada_c005` + desvío 0.61 entrenada 3M pasos en vez de 1.5M, seed 1

| | v92-lucio | v100-lucio |
|---|---|---|
| Éxito final (100 ep.) | 61% (51–70) | 100% (96–100) |
| Éxito best (100 ep.) | 42% (33–52) | 100% (96–100) |
| Best éxito (8 ep.) | 62% | 100% |
| Best reward | 8.84 | 21.68 |
| Largo ep. (best) | 121.5 | 47.9 |
| Best en timestep | 1,400,000 | 2,600,000 |
| Timesteps totales | 1,503,232 | 3,002,368 |
| Final: cómo terminan | choque_plataforma 29, exito 61, tiempo 6, choque_inclinacion 4 | exito 100 |
| Final: centro, mediana / < 5 cm | 12.3 cm / 10% | 3.3 cm / 71% |
| Final: llega a tocar a (mediana) | 0.40 m/s | 0.50 m/s |
| Final: Δacción / Δv pedida (p95) | 0.04 / 0.044 (0.152) m/s | 0.05 / 0.072 (0.190) m/s |
| Final: inclinación RMS / jerk | 8.6° / 24 m/s³ | 7.3° / 32 m/s³ |

## Qué cambió
- Solo la duración: 1.5M → 3M. Misma recompensa (`suave_bajada_c005`), seed (1), exploración (`--log_std_init -0.5`)
  e hiperparámetros que v92, que es la comparación. Hasta 1.5M es la misma corrida (los evals de 8 episodios coinciden
  con los de v92).

## Por qué
v92 (seed 1) y v98 (seed 3) aprendieron tarde con `c005` y a 1.5M no habían terminado (61 % y 72 %). ¿Les faltaban
pasos o no aprenden?

## Resultado
- **100 % en el modelo final** (v92 a 1.5M: 61 %), sin choques. En 200 episodios extra (seeds 1000–1199, no guardados
  en archivo): **200/200**.
- **La más centrada del proyecto:** 3.3 cm de mediana, 71 % a menos de 5 cm (en los 200 extra: 3.6 cm, 65 % a menos de
  5 cm y 96 % a menos de 10 cm).
- Termina de aprender entre 1.5M y 1.8M (evals de 8 episodios: 50 % a 1.5M, 100 % desde 1.8M).
- Δv pedida 0.072 m/s: menos suave que v91 y v93 (las seeds rápidas de `c005`, ~0.055), más suave que `suave_bajada`
  sola a 3M (v69: 0.119).
- **La seed lenta no era un fracaso: le faltaban pasos.** Una sola seed a 3M.

## Próximo paso
- Las otras seeds de `c005` + desvío 0.61 a 3M (sobre todo la 3, v98: 72 % a 1.5M) y `c003` a 3M (v103, corriendo).
