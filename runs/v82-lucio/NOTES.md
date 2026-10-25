# v82-lucio

Cambio: `suave_bajada` + castigo 0.1·|Δv pedida/0.6|² (`suave_bajada_v01`), seed 42: flota

| | v54-lucio | v82-lucio |
|---|---|---|
| Éxito final (100 ep.) | 92% (85–96) | 0% (0–4) |
| Éxito best (100 ep.) | 89% (81–94) | 0% (0–4) |
| Best éxito (8 ep.) | 100% | 0% |
| Best reward | 19.14 | -63.62 |
| Largo ep. (best) | 51.1 | 480.0 |
| Best en timestep | 1,500,000 | 100,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | exito 92, choque_plataforma 5, choque_inclinacion 1, tiempo 2 | tiempo 100 |
| Final: centro, mediana / < 5 cm | 8.1 cm / 24% | – |
| Final: toca a (mediana) | 0.31 m/s | – |
| Final: Δacción / Δv pedida (p95) | 0.13 / 0.100 (0.288) m/s | 0.00 / 0.000 (0.000) m/s |
| Final: inclinación RMS / jerk | 8.1° / 32 m/s³ | 0.0° / 0 m/s³ |


## Qué cambió
- Recompensa: `suave_bajada` + `reward_cmd_vel_coef` 0 → 0.1 (castigo `0.1·|(v_pedida − v_pedida_anterior)/0.6|²` por
  paso). Término nuevo en `env.py` (commit b26acce); con coeficiente 0 el entorno da lo mismo que el de v54.
- Misma seed (42), hiperparámetros y exploración que v54, que es la comparación.

## Por qué
Buscar un vuelo más suave castigando el salto de la velocidad que se le pide al dron (lo que se transfiere al
Crazyflie real), en vez del cambio de la acción, que tiene una dimensión redundante (`BITACORA.md`, 2026-10-24).

## Resultado
- **No aprende: 0 % y los 100 episodios terminan por tiempo.** La política pide `s = 0` en el 100 % de los pasos
  (velocidad pedida nula) y queda flotando a ~45 cm sobre el tope, a ~44 cm en horizontal. Evals de 8 episodios: 0 %
  en todos.
- No es un error del código, es un defecto de diseño del término: con `s = 0` la velocidad pedida es 0 cualquiera
  sea la dirección, así que el ruido de exploración (desvío ~0.9, `train/std`) deja de costar. Castigar la velocidad
  pedida le da al agente una salida que el castigo a la acción no tiene (ese también cobra los cambios de `s`). Es
  la misma trampa de flotar de A1, B, XY y `borde_k1`, con un atajo más.

## Próximo paso
- Descartar `suave_bajada_v01` y `_v03` (no se corren las otras seeds). Si se quiere castigar la velocidad pedida,
  hacerlo solo cuando el agente ya aterriza (curriculum) o con exploración más chica.
- Para suavidad, probar castigo a la acción más fuerte con desvío 0.61 (`suave_bajada_c005`).
