# v19-lucio

Cambio: recompensa A2: progreso (k=10) además del castigo por distancia

Se compara contra v17 (recompensa `base`, misma seed 42) **hasta 1.5M pasos**, porque estas corridas son de 1.5M. La evaluación de 100 episodios de v17 (88 %) es de su best a 3.7M, así que no es comparable directamente; la comparación justa es la curva de `rollout/success_rate`.

| | v17-lucio (`base`) | v19-lucio (`A2`) |
|---|---|---|
| `rollout/success_rate` a 0.75M / 1.0M / 1.5M | 35% / 64% / 68% | 0% / 0% / 0% |
| Primer paso con ≥ 50% (entrenamiento) | 0.80M | nunca (≤ 1.5M) |
| Éxito best (100 ep.) | 88% (80–93), best a 3.7M | 26% (18–35), best a 0.2M |
| Best éxito (8 ep.) | 100% | 37.5% |
| Best reward | 20.63 | -10.78 |
| Largo ep. (best) | 56 pasos | 222 pasos |
| Timesteps totales | 5 001 216 | 1 503 232 (30 min) |

## Qué cambió
Variante de recompensa `A2` (`--reward A2`, `rewards.yaml`). El resto igual a v17:
mismo código (commit `c28c288`, sin cambios sin commitear), hiperparámetros, entorno y seed (42).
- `reward_progress_coef`: 0 → **10**, sumado al castigo por distancia (0.1, igual).
- `crash_penalty`: −10 (igual).

## Por qué
Ver `BITACORA.md` (2026-10-04, "sacar el incentivo a chocar"): en v16/v17 el dron se tiraba al piso al
principio, porque con `base` cada paso en el aire cuesta y chocar corta ese costo. La idea era sacar ese
incentivo para que aprendiera antes.

## Resultado
**Datos.**
- **Aprendió algo muy al principio y lo perdió:** su best es de los 200k pasos (37.5 % en 8 episodios; 26 % en
  100 episodios, IC 18–35 %). Después, `rollout/success_rate` cae a 0 % y no vuelve (v17 a 1.5M: 68 %).
- Episodios largos: ~290–380 pasos (v17: ~67).
- Evaluación del best (200k): 26 éxitos, 61 choques contra la plataforma, 7 por tiempo, 3 contra el piso
  y 3 por inclinación.
  La posición relativa se recorta en 1.4–3.5 % de los pasos: a veces se aleja más de 1.5 m.
- `explained_variance` más baja que en las otras (~0.70): el crítico predice peor con dos términos densos.

**Hipótesis.** Con k = 10, el progreso domina la recompensa por paso y genera mucho ruido (la plataforma se
mueve, así que `d` cambia aunque el dron no haga nada). Eso puede haber desestabilizado lo que había
aprendido al principio. Que el best sea de 200k sugiere que no es que no pueda aprender, sino que el
aprendizaje no fue estable.

Una sola seed, pero la diferencia con v17 es enorme (0 % contra 68 % de éxito a 1.5M en el entrenamiento),
así que es señal y no azar.

## Próximo paso
1. Volver a la recompensa `base`: en las tres variantes, sacar o encarecer la salida "fácil" (chocar) hizo que
   el agente dejara de intentar aterrizar. El incentivo a chocar de `base` probablemente **ayuda** a explorar
   (episodios cortos, muchos intentos).
2. Atacar lo que falla en v17: los choques contra el borde de la plataforma.
