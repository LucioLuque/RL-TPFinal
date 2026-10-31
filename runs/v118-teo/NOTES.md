# v118-teo

Cambio: exploración gSDE (`--use_sde --sde_sample_freq 4 --log_std_init -2`) con `suave_bajada_c003`, 3M, seed 42

| | v105-teo | v118-teo |
|---|---|---|
| Éxito final (100 ep.) | 100% (96–100) | 100% (96–100) |
| Éxito best (100 ep.) | 100% (96–100) | 100% (96–100) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 20.61 | 21.41 |
| Largo ep. (best) | 58.0 | 54.9 |
| Best en timestep | 3,000,000 | 2,700,000 |
| Timesteps totales | 3,000,000 | 3,000,000 |
| Final: centro, mediana / < 5 cm | 4.1 cm / 60% | 4.2 cm / 60% |
| Final: llega a tocar a (mediana, m/s) | 0.51 | 0.52 |
| Final: Δacción / Δv pedida (p95) | 0.034 / 0.063 (0.154) m/s | 0.043 / 0.062 (0.161) m/s |
| Final: inclinación RMS / jerk (m/s³) | 6.9° / 31 | 8.2° / 30 |

## Qué cambió
- **Exploración:** gSDE (Raffin et al. 2021) en vez del ruido gaussiano independiente en cada paso. El ruido depende
  del estado (`ruido = ε · features(s)`, con la matriz ε sorteada cada 4 pasos), así que la acción explorada no salta
  de un paso al siguiente. Opciones nuevas de `train.py` (`--use_sde`, `--sde_sample_freq`), apagadas por defecto.
  `--log_std_init -2` y `--sde_sample_freq 4` son valores típicos de rl-baselines3-zoo para PyBullet, sin ajustar.
- Misma recompensa (`suave_bajada_c003`), seed (42), duración e hiperparámetros que v105-teo. Laboratorio S004, 3
  corridas en paralelo.

## Por qué
Suavizar las acciones sin tocar la recompensa: más castigo a la acción en la recompensa aprende más lento y a veces
deja al dron flotando (`c005`, v109; `c01`). gSDE suaviza la exploración y no cambia los retornos
(`docs/estado-del-arte-2026-10-30.md`, sección 2).

## Resultado
- **100 %**, igual que v105. Suavidad y centrado iguales (Δv pedida 0.062 contra 0.063; 4.2 contra 4.1 cm). Inclinación
  RMS algo mayor (8.2° contra 6.9°).
- Aprende parecido a `c003` (evals de 8 episodios: 75 % a 0.9M, 100 % desde 1.1M y estable hasta el final).
- Sigue tocando a ~0.5 m/s (gSDE no cambia la acción, y `s` sigue saturado).

## Próximo paso
- La seed 2 (v120) para ver si la mejora de v119 se repite. Si se repite, gSDE es candidata a exploración por
  defecto, junto con el desvío 0.61.
