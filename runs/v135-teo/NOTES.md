# v135-teo

Cambio: `suave_bajada_c003` con desvío inicial 0.37 (`--log_std_init -1.0`), 3M, seed 2

| | v107-teo | v135-teo |
|---|---|---|
| Éxito final (100 ep.) | 100% (96–100) | 100% (96–100) |
| Éxito best (100 ep.) | 100% (96–100) | 100% (96–100) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 21.51 | 22.45 |
| Largo ep. (best) | 50.2 | 43.1 |
| Best en timestep | 2,700,000 | 3,000,000 |
| Timesteps totales | 3,000,000 | 3,000,000 |
| Final: cómo terminan | exito 100 | exito 100 |
| Final: centro, mediana / < 5 cm | 3.7 cm / 65% | 3.2 cm / 74% |
| Final: llega a tocar a (mediana, m/s) | 0.49 | 0.50 |
| Final: Δacción / Δv pedida (p95) | 0.039 / 0.063 (0.145) m/s | 0.025 / 0.053 (0.126) m/s |
| Final: inclinación RMS / jerk (m/s³) | 7.3° / 30 | 7.2° / 29 |

## Qué cambió
- **Exploración:** desvío inicial de la acción 0.61 → 0.37 (`--log_std_init -0.5` → `-1.0`). Misma recompensa
  (`suave_bajada_c003`), seed (2), duración (3M) e hiperparámetros que v107-teo. Laboratorio S004, 3 corridas en paralelo.

## Por qué
`TODO.md`, punto 2: con `base`, bajar el desvío de 0.61 a 0.37 subió el éxito de 79 a 85 % (v60–v62), aprendiendo
más tarde. Faltaba probarlo con la candidata `c003`.

## Resultado
- 100 %. Centra mejor que v107 (3.2 contra 3.7 cm; 74 contra 65 % a menos de 5 cm) y es algo más suave (Δv pedida
  0.053 contra 0.063 m/s).
- Aprende más tarde: 50 % recién a 1.29M (v107: 0.70M).
- **Desvío 0.37 con 3 seeds** (v133–v135, contra 0.61 en v105–v107): 100 % en las 3. **Centra mejor** (3.5 / 3.2 /
  3.2 cm, 73–76 % a menos de 5 cm, contra 4.1 / 4.5 / 3.7 y 54–65 %), con la misma suavidad (Δv pedida media 0.064
  contra 0.066). **Aprende ~0.5M pasos más tarde** (50 % a 1.1–1.3M contra 0.7–0.8M; a 1.5M, 61–84 % de éxito en
  entrenamiento). A 3M le sobra tiempo; a 1.5M sería arriesgado.
- Lo mismo que con `base` (v60–v62): menos desvío inicial, mejor resultado final y aprendizaje más tardío.

## Próximo paso
- Si se entrena a 3M, 0.37 es una opción para centrar mejor, a cambio de aprender más tarde.
