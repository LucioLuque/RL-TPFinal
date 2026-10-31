# v134-teo

Cambio: `suave_bajada_c003` con desvío inicial 0.37 (`--log_std_init -1.0`), 3M, seed 1

| | v106-teo | v134-teo |
|---|---|---|
| Éxito final (100 ep.) | 100% (96–100) | 100% (96–100) |
| Éxito best (100 ep.) | 100% (96–100) | 100% (96–100) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 21.39 | 21.23 |
| Largo ep. (best) | 46.9 | 47.5 |
| Best en timestep | 2,900,000 | 2,400,000 |
| Timesteps totales | 3,000,000 | 3,000,000 |
| Final: cómo terminan | exito 100 | exito 100 |
| Final: centro, mediana / < 5 cm | 4.5 cm / 54% | 3.2 cm / 76% |
| Final: llega a tocar a (mediana, m/s) | 0.50 | 0.52 |
| Final: Δacción / Δv pedida (p95) | 0.050 / 0.072 (0.173) m/s | 0.045 / 0.071 (0.180) m/s |
| Final: inclinación RMS / jerk (m/s³) | 7.4° / 31 | 7.4° / 31 |

## Qué cambió
- **Exploración:** desvío inicial de la acción 0.61 → 0.37 (`--log_std_init -0.5` → `-1.0`). Misma recompensa
  (`suave_bajada_c003`), seed (1), duración (3M) e hiperparámetros que v106-teo. Laboratorio S004, 3 corridas en paralelo.

## Por qué
`TODO.md`, punto 2: con `base`, bajar el desvío de 0.61 a 0.37 subió el éxito de 79 a 85 % (v60–v62), aprendiendo
más tarde. Faltaba probarlo con la candidata `c003`.

## Resultado
- 100 %. Centra mejor que v106 (3.2 contra 4.5 cm; 76 contra 54 % a menos de 5 cm), con la misma suavidad (Δv pedida
  0.071 contra 0.072 m/s).
- Aprende más tarde: 50 % recién a 1.33M (v106: 0.79M).

## Próximo paso
- Ver v135, que junta las 3 seeds.
