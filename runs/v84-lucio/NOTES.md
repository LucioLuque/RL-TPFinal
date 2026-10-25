# v84-lucio

Cambio: premio al aterrizar 25 − 100·d_xy en vez de 25 − 50·d_xy (`suave_bajada_centro`), seed 42

| | v54-lucio | v84-lucio |
|---|---|---|
| Éxito final (100 ep.) | 92% (85–96) | 96% (90–98) |
| Éxito best (100 ep.) | 89% (81–94) | 83% (74–89) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 19.14 | 12.82 |
| Largo ep. (best) | 51.1 | 59.5 |
| Best en timestep | 1,500,000 | 1,300,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | exito 92, choque_plataforma 5, choque_inclinacion 1, tiempo 2 | exito 96, tiempo 3, choque_plataforma 1 |
| Final: centro, mediana / < 5 cm | 8.1 cm / 24% | 8.6 cm / 16% |
| Final: llega a tocar a (mediana) | 0.45 m/s | 0.42 m/s |
| Final: Δacción / Δv pedida (p95) | 0.13 / 0.100 (0.288) m/s | 0.05 / 0.060 (0.179) m/s |
| Final: inclinación RMS / jerk | 8.1° / 32 m/s³ | 8.4° / 28 m/s³ |


## Qué cambió
- Recompensa: `suave_bajada` con `landing_dxy_coef` 50 → 100 (premio al aterrizar entre 5 y 25 en vez de entre 15 y
  25, con d_xy < 0.2). Parámetro nuevo en `env.py` (commit b26acce; con 50 da lo mismo que antes).
- Misma seed (42), hiperparámetros y exploración que v54, que es la comparación.

## Por qué
Que aterrice más cerca del centro: v54 aterriza a 8.1 cm (mediana) y solo 24 % a menos de 5 cm (`BITACORA.md`,
2026-10-24, métricas nuevas).

## Resultado
- **No centra mejor**, que era el objetivo: 8.6 cm de mediana y 16 % a menos de 5 cm (v54: 8.1 cm y 24 %).
- En cambio, **96 % de éxito final** (v54: 92 %; los intervalos 90–98 y 85–96 se pisan) y **1 solo choque contra el
  borde** de 100 (v54: 5). Más suave: Δv pedida 0.060 m/s contra 0.100 (p95 0.18 contra 0.29).
- Evals de 8 episodios: aprende desde 0.6M como v54. El best (1.3M, 83 %) es peor que el final: otra vez el best de 8
  episodios engaña.
- Hipótesis de por qué no centra: el premio se cobra al terminar, 10 pasos después de tocar, y una vez apoyado el dron
  casi no se desplaza sobre la plataforma; el centrado se decide antes de tocar, y la señal llega tarde y ruidosa.
  Una sola seed: no sacar conclusiones del éxito.

## Próximo paso
- Seeds 1 y 2 (v87, v90) para ver si el éxito y la suavidad se sostienen.
- Para centrar, probar un término por paso con la distancia horizontal cerca del tope (en vez del premio terminal).
