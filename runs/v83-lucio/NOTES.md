# v83-lucio

Cambio: `suave_bajada` + castigo por llegar rápido al tope (`suave_bajada_flare`), seed 42: flota

| | v54-lucio | v83-lucio |
|---|---|---|
| Éxito final (100 ep.) | 92% (85–96) | 0% (0–4) |
| Éxito best (100 ep.) | 89% (81–94) | 0% (0–4) |
| Best éxito (8 ep.) | 100% | 0% |
| Best reward | 19.14 | -12.53 |
| Largo ep. (best) | 51.1 | 25.9 |
| Best en timestep | 1,500,000 | 300,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | exito 92, choque_plataforma 5, choque_inclinacion 1, tiempo 2 | tiempo 99, choque_inclinacion 1 |
| Final: centro, mediana / < 5 cm | 8.1 cm / 24% | – |
| Final: llega a tocar a (mediana) | 0.45 m/s | -0.00 m/s |
| Final: Δacción / Δv pedida (p95) | 0.13 / 0.100 (0.288) m/s | 0.09 / 0.041 (0.262) m/s |
| Final: inclinación RMS / jerk | 8.1° / 32 m/s³ | 8.3° / 22 m/s³ |


## Qué cambió
- Recompensa: `suave_bajada` + `reward_flare_coef` 0 → 0.1: castigo `0.1·(velocidad de bajada − 0.15)₊/0.1` por paso
  estando alineado (adentro del radio) y a menos de 15 cm del tope. Término nuevo en `env.py` (commit b26acce).
- Misma seed (42), hiperparámetros y exploración que v54, que es la comparación.

## Por qué
Que llegue a la plataforma más despacio. Con la métrica corregida, todas las políticas llegan a tocar bajando a
~0.45 m/s, casi a la velocidad máxima de bajada (`BITACORA.md`, 2026-10-25).

## Resultado
- **No aprende: 0 %, 99 de 100 episodios por tiempo.** Evals de 8 episodios: 0 % en todos. En los episodios que se
  miraron (seeds 42–45), los últimos 5 s queda flotando a 5–19 cm sobre el tope y a 0.21–0.25 m del centro, justo en
  el borde (radio 0.25 m), sin bajar.
- Hipótesis (no verificada con más seeds): defecto de diseño de la variante. Con el castigo por bajar afuera
  (`reward_descent_coef`, desde 30 cm) y este adentro (desde 15 cm), bajar cerca del tope cuesta en todos lados, y es
  la misma trampa de flotar de A1, B, XY, `borde_k1` y v82: mientras el agente no sabe aterrizar, el castigo seguro de
  intentarlo pesa más que el premio raro de lograrlo.

## Próximo paso
- Ver la seed 1 (v86, ya lanzada). Si también flota, descartar la variante.
- Si se quiere castigar la velocidad de llegada, hacerlo solo después de que aprende a aterrizar (seguir entrenando
  una corrida de `suave_bajada` con `--load` y otra recompensa), o con un umbral más alto.
