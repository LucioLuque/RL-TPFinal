# v18-lucio

Cambio: recompensa A1: progreso (k=10) en vez de castigo por distancia

Se compara contra v17 (recompensa `base`, misma seed 42) **hasta 1.5M pasos**, porque estas corridas son de 1.5M. La evaluación de 100 episodios de v17 (88 %) es de su best a 3.7M, así que no es comparable directamente; la comparación justa es la curva de `rollout/success_rate`.

| | v17-lucio (`base`) | v18-lucio (`A1`) |
|---|---|---|
| `rollout/success_rate` a 0.75M / 1.0M / 1.5M | 35% / 64% / 68% | 0% / 0% / 0% |
| Primer paso con ≥ 50% (entrenamiento) | 0.80M | nunca (≤ 1.5M) |
| Éxito best (100 ep.) | 88% (80–93), best a 3.7M | 0% (0–4), best a 1.3M |
| Best éxito (8 ep.) | 100% | 0% |
| Best reward | 20.63 | 3.58 |
| Largo ep. (best) | 56 pasos | 463 pasos |
| Timesteps totales | 5 001 216 | 1 503 232 (28 min) |

## Qué cambió
Variante de recompensa `A1` (`--reward A1`, `rewards.yaml`). El resto igual a v17:
mismo código (commit `c28c288`, sin cambios sin commitear), hiperparámetros, entorno y seed (42).
- `reward_distance_coef`: 0.1 → **0**.
- `reward_progress_coef`: 0 → **10** (premio `10·(d_anterior − d)` por paso).
- `crash_penalty`: −10 (igual).

## Por qué
Ver `BITACORA.md` (2026-10-04, "sacar el incentivo a chocar"): en v16/v17 el dron se tiraba al piso al
principio, porque con `base` cada paso en el aire cuesta y chocar corta ese costo. La idea era sacar ese
incentivo para que aprendiera antes.

## Resultado
**Datos.**
- No aprendió a aterrizar: `rollout/success_rate` en 0 % de punta a punta (v17 a 1.5M: 68 %).
- **Dejó de chocar, pero se queda flotando:** los episodios pasan a durar ~400–440 pasos de 480 (v17: ~67).
  En la evaluación de 100 episodios, 70 terminan por tiempo, 16 contra la plataforma y 14 por inclinación.
- **En los que terminan por tiempo, está encima de la plataforma:** distancia horizontal mediana de 0.10 m al
  final. Llega, pero no se anima a bajar y quedarse quieto.
- `std` de la política sube de 1.10 a 1.49: explora cada vez más, sin encontrar el aterrizaje.

**Hipótesis.** Sin el costo por distancia, quedarse flotando cerca cuesta casi nada (solo −0.01 por paso,
≈ −4.8 en el episodio), mientras que intentar aterrizar arriesga −10. Sacar el incentivo a chocar sacó también
la presión para intentar algo. En v17, los episodios cortos (chocar rápido) daban muchos más intentos por
cada millón de pasos, y algunos terminaban en aterrizaje.

Una sola seed, pero la diferencia con v17 es enorme (0 % contra 68 % de éxito a 1.5M en el entrenamiento),
así que es señal y no azar.

## Próximo paso
1. Volver a la recompensa `base`: en las tres variantes, sacar o encarecer la salida "fácil" (chocar) hizo que
   el agente dejara de intentar aterrizar. El incentivo a chocar de `base` probablemente **ayuda** a explorar
   (episodios cortos, muchos intentos).
2. Atacar lo que falla en v17: los choques contra el borde de la plataforma.
