# v86-lucio

Cambio: `suave_bajada` + castigo por llegar rápido al tope (`suave_bajada_flare`), seed 1: flota

| | v56-lucio | v86-lucio |
|---|---|---|
| Éxito final (100 ep.) | 88% (80–93) | 0% (0–4) |
| Éxito best (100 ep.) | 84% (76–90) | 0% (0–4) |
| Best éxito (8 ep.) | 100% | 0% |
| Best reward | 18.14 | -13.50 |
| Largo ep. (best) | 61.1 | 34.4 |
| Best en timestep | 1,500,000 | 200,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | choque_plataforma 9, choque_piso 1, exito 88, tiempo 2 | tiempo 100 |
| Final: centro, mediana / < 5 cm | 9.6 cm / 18% | – |
| Final: llega a tocar a (mediana) | 0.42 m/s | 0.32 m/s |
| Final: Δacción / Δv pedida (p95) | 0.13 / 0.091 (0.280) m/s | 0.06 / 0.030 (0.207) m/s |
| Final: inclinación RMS / jerk | 8.1° / 30 m/s³ | 7.7° / 19 m/s³ |


## Qué cambió
- Lo mismo que v83 (`reward_flare_coef` 0.1), con la seed 1. Se compara con v56 (`suave_bajada`, seed 1).

## Por qué
Segunda seed de `suave_bajada_flare`, después de que v83 (seed 42) quedó flotando.

## Resultado
- **Tampoco aprende: 0 %, los 100 episodios por tiempo**, 0 % en todos los evals de 8 episodios. Con 2 de 2 seeds
  flotando (v83, v86), la variante se descarta: castigar la velocidad de llegada desde el principio del entrenamiento
  cae en la trampa de flotar.

## Próximo paso
- No correr la seed 2 (v89). Si se retoma la idea, castigar la llegada recién cuando ya aterriza (curriculum).
