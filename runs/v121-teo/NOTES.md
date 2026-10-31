# v121-teo

Cambio: CAPS (suavidad en la pérdida: temporal 0.01, espacial 0.01) con `c003`, 3M, seed 42

| | v105-teo | v121-teo |
|---|---|---|
| Éxito final (100 ep.) | 100% (96–100) | 100% (96–100) |
| Éxito best (100 ep.) | 100% (96–100) | 100% (96–100) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 20.61 | 21.97 |
| Largo ep. (best) | 58.0 | 46.2 |
| Best en timestep | 3,000,000 | 2,800,000 |
| Timesteps totales | 3,000,000 | 3,000,000 |
| Final: cómo terminan | exito 100 | exito 100 |
| Final: centro, mediana / < 5 cm | 4.1 cm / 60% | 2.7 cm / 84% |
| Final: llega a tocar a (mediana, m/s) | 0.51 | 0.49 |
| Final: Δacción / Δv pedida (p95) | 0.034 / 0.063 (0.154) m/s | 0.041 / 0.063 (0.155) m/s |
| Final: inclinación RMS / jerk (m/s³) | 6.9° / 31 | 7.3° / 31 |

## Qué cambió
- **Pérdida de PPO con CAPS** (Mysore et al. 2021), en `caps.py` (`CAPSPPO`, subclase de `PPO`). Se suman dos
  términos sobre la media de la acción (la de la gaussiana, sin recortar a [−1, 1]):
  - temporal: `0.01·‖μ(s_t) − μ(s_{t+1})‖`, sobre pares de pasos consecutivos del mismo episodio del rollout;
  - espacial: `0.01·‖μ(s) − μ(s + ruido)‖`, con ruido gaussiano de desvío 0.02 en la observación normalizada.
  La recompensa no cambia. Opciones nuevas de `train.py` (`--caps_temporal`, `--caps_spatial`, `--caps_sigma`),
  apagadas por defecto. El modelo se guarda como un PPO común y se carga con `PPO.load`.
- **`caps.py` no está en `diff.patch`:** todavía no está en git (`run.json`: `git.untracked`). El código es el de
  `caps.py` en la raíz del repo, sin cambios desde que se lanzó la corrida.
- Misma recompensa (`suave_bajada_c003`), seed (42), exploración (`--log_std_init -0.5`), duración e hiperparámetros
  que v105-teo. Laboratorio S004, 3 corridas en paralelo.

## Por qué
Suavizar las acciones sin tocar la recompensa (`docs/estado-del-arte-2026-10-30.md`, sección 2). CAPS era la idea
más prometedora de la literatura (probada en un cuadricóptero real) y, como no cambia la recompensa, no puede causar
la trampa de flotar. Los pesos (0.01 y 0.01) son para que los términos queden del orden de la pérdida de la política;
no se ajustaron.

## Resultado
- 100 %, y **centra mejor**: 2.7 cm, con 84 % a menos de 5 cm (v105: 4.1 cm, 60 %). Es el mejor centrado del proyecto.
- **No es más suave:** Δv pedida 0.063 m/s, la misma que v105.
- Aprende parecido (50 % a 0.82M; v105: 0.67M).
- Términos de CAPS en TensorBoard: el temporal baja de 0.51 a 0.25 y el espacial sube de 0.08 a 0.19. Multiplicados
  por 0.01, quedan del orden de la pérdida de la política (~0.004).

## Próximo paso
- Ver v123, que junta las 3 seeds.
