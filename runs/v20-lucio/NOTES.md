# v20-lucio

Cambio: recompensa B: castigo por choque −50 (antes −10)

Se compara contra v17 (recompensa `base`, misma seed 42) **hasta 1.5M pasos**, porque estas corridas son de 1.5M. La evaluación de 100 episodios de v17 (88 %) es de su best a 3.7M, así que no es comparable directamente; la comparación justa es la curva de `rollout/success_rate`.

| | v17-lucio (`base`) | v20-lucio (`B`) |
|---|---|---|
| `rollout/success_rate` a 0.75M / 1.0M / 1.5M | 35% / 64% / 68% | 0% / 0% / 0% |
| Primer paso con ≥ 50% (entrenamiento) | 0.80M | nunca (≤ 1.5M) |
| Éxito best (100 ep.) | 88% (80–93), best a 3.7M | 0% (0–4), best a 1.2M |
| Best éxito (8 ep.) | 100% | 0% |
| Best reward | 20.63 | -31.92 |
| Largo ep. (best) | 56 pasos | 480 pasos |
| Timesteps totales | 5 001 216 | 1 503 232 (30 min) |

## Qué cambió
Variante de recompensa `B` (`--reward B`, `rewards.yaml`). El resto igual a v17:
mismo código (commit `c28c288`, sin cambios sin commitear), hiperparámetros, entorno y seed (42).
- `crash_penalty`: −10 → **−50**.
- Distancia (0.1) y progreso (0): iguales a `base`.

## Por qué
Ver `BITACORA.md` (2026-10-04, "sacar el incentivo a chocar"): en v16/v17 el dron se tiraba al piso al
principio, porque con `base` cada paso en el aire cuesta y chocar corta ese costo. La idea era sacar ese
incentivo para que aprendiera antes.

## Resultado
**Datos.**
- No aprendió a aterrizar: `rollout/success_rate` en 0 % de punta a punta (v17 a 1.5M: 68 %).
- **Evita la plataforma:** episodios de ~455 pasos de 480; en la evaluación, los 100 terminan por tiempo,
  lejos de la plataforma (distancia horizontal mediana de ~0.4 m, no encima). Ningún choque.
- `std` sube de 1.35 a 1.90 y `explained_variance` cae a 0.40 al final: la política se vuelve cada vez más
  aleatoria.

**Hipótesis.** Con −50, cualquier intento de aterrizar es demasiado arriesgado: acercarse a la plataforma
aumenta la chance de chocar. El agente prefiere mantenerse a distancia y pagar el costo por paso
(≈ −40 en el episodio), que es menor que un choque. Es la trampa inversa a la de v16.

Una sola seed, pero la diferencia con v17 es enorme (0 % contra 68 % de éxito a 1.5M en el entrenamiento),
así que es señal y no azar.

## Próximo paso
1. Volver a la recompensa `base`: en las tres variantes, sacar o encarecer la salida "fácil" (chocar) hizo que
   el agente dejara de intentar aterrizar. El incentivo a chocar de `base` probablemente **ayuda** a explorar
   (episodios cortos, muchos intentos).
2. Atacar lo que falla en v17: los choques contra el borde de la plataforma.
