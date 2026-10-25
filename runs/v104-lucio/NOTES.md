# v104-lucio

Cambio: `suave_bajada_c005` + desvío 0.61 a 3M pasos, seed 3 (cortada en 2.95M; se evalúa el best)

| | v98-lucio (1.5M, final) | v104-lucio (best, 2.9M) |
|---|---|---|
| Éxito (100 ep.) | 72% (62–80) | 100% (96–100) |
| Cómo terminan | exito 72, choque_plataforma 21, tiempo 6, choque_piso 1 | exito 100 |
| Centro, mediana / < 5 cm | 13.4 cm / 6% | 4.5 cm / 54% |
| Δacción / Δv pedida (p95) | 0.03 / 0.041 (0.134) m/s | 0.02 / 0.049 (0.119) m/s |
| Inclinación RMS / jerk | 8.1° / 23 m/s³ | 7.6° / 30 m/s³ |
| Timesteps | 1,503,232 | ~2,950,000 (cortada) |

## Qué cambió
- Solo la duración: 1.5M → 3M. Misma recompensa (`suave_bajada_c005`), seed (3), exploración e hiperparámetros que
  v98, que es la comparación.

## Por qué
v98 (seed 3) aprendió tarde y a 1.5M dio 72 %; con la seed 1, entrenar 3M llevó de 61 a 100 % (v100).

## Resultado
- **La corrida se cortó** (apagado de la notebook) a ~2.95M pasos: no hay `model.zip` ni `eval_final.json`. `run.json`
  se cambió a mano de `running` a `interrupted`, con una nota. Se evaluó el best (`eval_best.json`), que según los
  evals de TensorBoard es el de 2.9M (100 %, reward 21.1).
- **Best: 100 % en 100 episodios** (v98 a 1.5M: 72 %), 4.5 cm del centro (54 % a menos de 5 cm) y **Δv pedida
  0.049 m/s (p95 0.12): la más suave de las que aterrizan siempre.**
- Igual que v100: a la seed lenta de `c005` le faltaban pasos. Con 3M, las dos seeds lentas (1 y 3) llegan a 100 %.

## Próximo paso
- Si se elige `c005` + desvío 0.61 por la suavidad, entrenar a 3M completo con varias seeds.
