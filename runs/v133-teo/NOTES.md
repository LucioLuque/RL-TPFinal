# v133-teo

Cambio: `suave_bajada_c003` con desvío inicial 0.37 (`--log_std_init -1.0`), 3M, seed 42

| | v105-teo | v133-teo |
|---|---|---|
| Éxito final (100 ep.) | 100% (96–100) | 100% (96–100) |
| Éxito best (100 ep.) | 100% (96–100) | 100% (96–100) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 20.61 | 21.52 |
| Largo ep. (best) | 58.0 | 46.1 |
| Best en timestep | 3,000,000 | 2,600,000 |
| Timesteps totales | 3,000,000 | 3,000,000 |
| Final: cómo terminan | exito 100 | exito 100 |
| Final: centro, mediana / < 5 cm | 4.1 cm / 60% | 3.5 cm / 73% |
| Final: llega a tocar a (mediana, m/s) | 0.51 | 0.52 |
| Final: Δacción / Δv pedida (p95) | 0.034 / 0.063 (0.154) m/s | 0.042 / 0.067 (0.167) m/s |
| Final: inclinación RMS / jerk (m/s³) | 6.9° / 31 | 7.0° / 30 |

## Qué cambió
- **Exploración:** desvío inicial de la acción 0.61 → 0.37 (`--log_std_init -0.5` → `-1.0`). Misma recompensa
  (`suave_bajada_c003`), seed (42), duración (3M) e hiperparámetros que v105-teo. Laboratorio S004, 3 corridas en paralelo.

## Por qué
`TODO.md`, punto 2: con `base`, bajar el desvío de 0.61 a 0.37 subió el éxito de 79 a 85 % (v60–v62), aprendiendo
más tarde. Faltaba probarlo con la candidata `c003`.

## Resultado
- 100 %. Centra mejor que v105 (3.5 contra 4.1 cm; 73 contra 60 % a menos de 5 cm), con la misma suavidad (Δv pedida
  0.067 contra 0.063 m/s).
- **Aprende más tarde:** 0 de 8 en todos los evals hasta 1M y 50 % recién a 1.10M (v105: 0.67M).

## Próximo paso
- Ver v135, que junta las 3 seeds.
