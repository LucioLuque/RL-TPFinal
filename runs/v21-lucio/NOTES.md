# v21-lucio

Cambio: base de referencia con el PID arreglado (1.5M pasos)

Se compara contra v17 (misma recompensa `base` y seed 42, pero entrenada con el error del PID) **hasta 1.5M
pasos**. La evaluación de 100 episodios de v17 (88 %) es de su best a 3.7M, así que no es directamente
comparable con la de esta corrida (best a 0.9M).

| | v17-lucio | v21-lucio |
|---|---|---|
| `rollout/success_rate` a 0.75M / 1.0M / 1.5M | 35% / 64% / 68% | 31% / 62% / 72% |
| Primer paso con ≥ 50% (entrenamiento) | 0.80M | 0.86M |
| Éxito best (100 ep.) | 88% (80–93), best a 3.7M | 65% (55–74), best a 0.9M |
| Best éxito (8 ep.) | 100% | 87.5% |
| Largo ep. a 1.5M (entrenamiento) | 68 pasos | 78 pasos |
| Timesteps totales | 5 001 216 | 1 503 232 (36 min) |

## Qué cambió
- El PID del dron se reinicia en cada episodio (commit `8b26a8e`). Antes arrastraba el estado del episodio
  anterior. Recompensa (`base`), hiperparámetros, entorno y seed: iguales a v17.
- Además, 1.5M pasos en vez de 5M.

## Por qué
Las corridas hasta v20 se entrenaron con el error del PID (`BITACORA.md`, 2026-10-04). Hacía falta una
`base` entrenada en las mismas condiciones que las variantes nuevas, empezando por `XY` (v22).

## Resultado
**Datos.**
- **El arreglo del PID no cambió el aprendizaje:** la curva de éxito es casi igual a la de v17 (72 % contra
  68 % a 1.5M; cruza el 50 % a 0.86M contra 0.80M). Con una sola seed, esa diferencia es ruido.
- **Evaluación del best (0.9M), 100 episodios:** 65 % (IC 55–74 %). Fallos: 31 choques contra la
  plataforma, 3 contra el piso y 1 por tiempo.
- **Los 31 choques contra la plataforma tienen el mismo patrón que en v17:** medio segundo antes, el dron
  está afuera (mediana 0.43 m del centro; radio 0.25) y bajo (8 cm sobre el tope), bajando en diagonal. El
  100 % cumple "afuera y bajo". Es el modo de fallo de `base`, no algo de v17.

**Hipótesis.** Con más entrenamiento, el best mejora (v17 pasó de ~65 % a 88 % entre 1M y 3.7M), pero el
patrón de bajar en diagonal se mantiene, porque `−0.1·d` lo premia.

## Próximo paso
- Es la referencia para comparar variantes de recompensa de 1.5M pasos con el PID arreglado (ver v22).
