# v119-teo

Cambio: exploración gSDE (`--use_sde --sde_sample_freq 4 --log_std_init -2`) con `suave_bajada_c003`, 3M, seed 1

| | v106-teo | v119-teo |
|---|---|---|
| Éxito final (100 ep.) | 100% (96–100) | 100% (96–100) |
| Éxito best (100 ep.) | 100% (96–100) | 100% (96–100) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 21.39 | 21.65 |
| Largo ep. (best) | 46.9 | 50.1 |
| Best en timestep | 2,900,000 | 2,700,000 |
| Timesteps totales | 3,000,000 | 3,000,000 |
| Final: centro, mediana / < 5 cm | 4.5 cm / 54% | 3.3 cm / 81% |
| Final: llega a tocar a (mediana, m/s) | 0.50 | 0.51 |
| Final: Δacción / Δv pedida (p95) | 0.050 / 0.072 (0.173) m/s | 0.018 / 0.046 (0.109) m/s |
| Final: inclinación RMS / jerk (m/s³) | 7.4° / 31 | 7.4° / 29 |

## Qué cambió
- **Exploración:** gSDE (Raffin et al. 2021) en vez del ruido gaussiano independiente en cada paso. El ruido depende
  del estado (`ruido = ε · features(s)`, con la matriz ε sorteada cada 4 pasos), así que la acción explorada no salta
  de un paso al siguiente. Opciones nuevas de `train.py` (`--use_sde`, `--sde_sample_freq`), apagadas por defecto.
  `--log_std_init -2` y `--sde_sample_freq 4` son valores típicos de rl-baselines3-zoo para PyBullet, sin ajustar.
- Misma recompensa (`suave_bajada_c003`), seed (1), duración e hiperparámetros que v106-teo. Laboratorio S004, 3
  corridas en paralelo.

## Por qué
Suavizar las acciones sin tocar la recompensa: más castigo a la acción en la recompensa aprende más lento y a veces
deja al dron flotando (`c005`, v109; `c01`). gSDE suaviza la exploración y no cambia los retornos
(`docs/estado-del-arte-2026-10-30.md`, sección 2).

## Resultado
- **100 %, y de las más suaves y centradas del proyecto:** Δv pedida **0.046 m/s** (p95 0.109) contra 0.072 de v106, y
  **3.3 cm con 81 % a menos de 5 cm** (v106: 4.5 cm, 54 %). Lo mismo que la mejor seed de `c005` (v108: 0.043 m/s,
  80 %), sin el castigo más fuerte que a veces la deja flotando.
- Aprende parecido a `c003` (evals de 8 episodios: 75 % a 0.9M, 100 % desde 1.1M y estable hasta el final).
- Sigue tocando a ~0.5 m/s (gSDE no cambia la acción, y `s` sigue saturado).

## Próximo paso
- La seed 2 (v120) para ver si la mejora de v119 se repite. Si se repite, gSDE es candidata a exploración por
  defecto, junto con el desvío 0.61.
