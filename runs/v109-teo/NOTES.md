# v109-teo

Cambio: `suave_bajada_c005` + desvío 0.61 entrenada 3M pasos en vez de 1.5M, seed 2

| | v93-lucio | v109-teo |
|---|---|---|
| Éxito final (100 ep.) | 97% (92–99) | **0% (0–4)** |
| Éxito best (100 ep.) | 95% (89–98) | 0% (0–4) |
| Best éxito (8 ep.) | 100% | 0% |
| Best reward | 21.14 | -50.65 |
| Largo ep. (best) | 57.8 | 480.0 |
| Best en timestep | 1,400,000 | 1,400,000 |
| Timesteps totales | 1,500,000 | 3,000,000 |
| Final: cómo terminan | exito 97, choque_plataforma 2, tiempo 1 | tiempo 100 |
| Final: Δv pedida | 0.059 m/s | 0.000 m/s |

## Qué cambió
- Solo la duración: 1.5M → 3M pasos. Misma recompensa (`suave_bajada_c005`), seed (2), exploración
  (`--log_std_init -0.5`) e hiperparámetros que v93. Entre los commits (ec6c43e → 61c0368) solo cambiaron comentarios.
- **Otra máquina:** v93 se entrenó en la de Lucio y v109 en el laboratorio S004, con 3 corridas en paralelo.

## Por qué
`TODO.md`, punto 1: `c003` y `c005` a 3M con 3 seeds para elegir la recompensa final.

## Resultado
- **0 %: queda quieta en el aire los 480 pasos de todos los episodios.** La acción determinista es siempre
  `[−1, −1, 1, 0]`: dirección fija y **`s = 0`**, o sea velocidad pedida nula. Nunca aprende: 0 % en todos los evals
  de 8 episodios, de 0 a 3M. Al final del entrenamiento, el desvío de la acción sigue en 0.6–0.8.
- Es la misma salida que `suave_bajada_v01` (v82) y `c01` (v96): con el castigo a la acción, no cambiarla nunca no
  cuesta nada, y quedarse quieto es un óptimo local. Flotar le cuesta ~−50 por episodio (distancia acumulada), peor
  que chocar (−10), pero PPO no sale de ahí.
- **La misma seed aprendió en la máquina de Lucio** (v93: 97 % a 1.5M). Con subprocesos y otro hardware el
  entrenamiento no es reproducible, así que caer en la trampa es cuestión de azar, no de la seed.
- `c005` a 3M queda: s1 100 % (v100), s42 100 % (v108), s3 97 % (v110), s2 0 % (v109). Con 1.5M ya había 2 de 4 seeds
  lentas (v92, v98). **`c005` es frágil:** con castigo 0.05, a veces no sale de quedarse quieto.

## Próximo paso
- Una seed más de `c005` a 3M (seed 4, en la cola). Si también falla, `c005` se descarta como recompensa final.
- Si se quiere la suavidad de `c005` sin la trampa: CAPS (`caps.py`, en la cola esta noche), que suaviza en la
  pérdida y no en la recompensa.
