# v103-lucio

Cambio: `suave_bajada_c003` + desvío 0.61 a 3M pasos, seed 42 (cortada en 2.8M; se evalúa el best)

| | v101-lucio (1.5M, final) | v103-lucio (best, 2.4M) |
|---|---|---|
| Éxito (100 ep.) | 95% (89–98) | 100% (96–100) |
| Cómo terminan | choque_plataforma 3, tiempo 2, exito 95 | exito 100 |
| Centro, mediana / < 5 cm | 5.4 cm / 42% | 4.0 cm / 61% |
| Δacción / Δv pedida (p95) | 0.06 / 0.073 (0.182) m/s | 0.04 / 0.064 (0.151) m/s |
| Inclinación RMS / jerk | 7.5° / 31 m/s³ | 7.1° / 30 m/s³ |
| Timesteps | 1,503,232 | ~2,810,000 (cortada) |

## Qué cambió
- Solo la duración: 1.5M → 3M. Misma recompensa (`suave_bajada_c003`), seed (42), exploración (`--log_std_init -0.5`)
  e hiperparámetros que v101, que es la comparación (v101 es su modelo final a 1.5M).

## Por qué
`c003` + desvío 0.61 fue la más robusta a 1.5M (97.7 % con 3 seeds), y entrenar 3M centró mucho más con
`suave_bajada` (v69) y `c005` (v100).

## Resultado
- **La corrida se cortó** (apagado de la notebook) a ~2.81M pasos: no hay `model.zip` ni `eval_final.json`. `run.json`
  quedó con estado `running`; se cambió a mano a `interrupted`, con una nota. Se evaluó el best (`eval_best.json`), que
  según los evals de TensorBoard es el de 2.4M (100 % y el reward más alto, 22.0).
- **Best: 100 % en 100 episodios**, 4.0 cm del centro (61 % a menos de 5 cm, 94 % a menos de 10) y Δv pedida 0.064 m/s:
  más centrada y algo más suave que la misma corrida a 1.5M (v101).
- Evals de 8 episodios: 100 % en todos desde 1.7M.

## Próximo paso
- Si se elige `c003` + desvío 0.61, entrenarla de nuevo a 3M completo (y más seeds) para tener el modelo final.
