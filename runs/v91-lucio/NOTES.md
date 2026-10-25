# v91-lucio

Cambio: castigo a la acción 0.05 en vez de 0.02 (`suave_bajada_c005`) con desvío inicial 0.61, seed 42

| | v65-lucio | v91-lucio |
|---|---|---|
| Éxito final (100 ep.) | 92% (85–96) | 100% (96–100) |
| Éxito best (100 ep.) | 89% (81–94) | 97% (92–99) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 18.73 | 20.80 |
| Largo ep. (best) | 59.4 | 54.2 |
| Best en timestep | 1,500,000 | 1,100,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | exito 92, tiempo 1, choque_plataforma 7 | exito 100 |
| Final: centro, mediana / < 5 cm | 5.2 cm / 42% | 5.1 cm / 49% |
| Final: llega a tocar a (mediana) | 0.47 m/s | 0.50 m/s |
| Final: Δacción / Δv pedida (p95) | 0.04 / 0.059 (0.159) m/s | 0.02 / 0.051 (0.123) m/s |
| Final: inclinación RMS / jerk | 7.7° / 28 m/s³ | 7.5° / 29 m/s³ |


## Qué cambió
- Recompensa: `suave_bajada` con `reward_action_coef` 0.02 → 0.05 (`suave_bajada_c005`). `--log_std_init -0.5`.
- Se compara con v65 (`suave_bajada` + desvío 0.61, seed 42): misma seed, exploración e hiperparámetros.

## Por qué
Buscar más suavidad: con desvío 0.61, el castigo a la acción ya había dado las políticas más suaves (v57, v58, v65) y,
a diferencia del castigo a la velocidad pedida (v82), no tiene una salida que deje al dron flotando.

## Resultado
- **100 % de éxito en el modelo final** (IC 96–100 %), 0 choques; v65: 92 %. **Evaluación extra en 200 episodios
  distintos** (seeds 1000–1199, no guardada en archivo): **200/200** (IC 98–100 %), contra 189/200 de v65.
- La más suave del proyecto: Δv pedida 0.051 m/s por paso (p95 0.12) contra 0.059 (0.16) de v65 y 0.100 (0.29) de v54.
- La más centrada: 5.1 cm de mediana y 49 % a menos de 5 cm (v65: 5.2 cm y 42 %; v54: 8.1 cm y 24 %). En los 200
  episodios extra: 4.8 cm y 53 %.
- Aprende antes que v65: 50 % en el eval de 8 episodios a 0.6M, y 100 % desde 1.1M.
- Llega a tocar igual de rápido que todas (0.50 m/s) y la inclinación RMS no cambia (7.5°; ver el PID a 24 Hz en
  `BITACORA.md`).
- **Una sola seed.** Faltan v92 (s1) y v93 (s2).

## Próximo paso
- Seeds 1 y 2 (v92, v93). Si se sostiene, es candidata a recompensa por defecto (lo decide Lucio).
- Probar un castigo a la acción todavía más fuerte (0.1) con desvío 0.61, para ver dónde empieza a costar éxito.
