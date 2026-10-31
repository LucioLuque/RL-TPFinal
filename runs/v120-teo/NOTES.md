# v120-teo

Cambio: exploración gSDE (`--use_sde --sde_sample_freq 4 --log_std_init -2`) con `suave_bajada_c003`, 3M, seed 2

| | v107-teo | v120-teo |
|---|---|---|
| Éxito final (100 ep.) | 100% (96–100) | 100% (96–100) |
| Éxito best (100 ep.) | 100% (96–100) | 100% (96–100) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 21.51 | 21.63 |
| Largo ep. (best) | 50.2 | 49.2 |
| Best en timestep | 2,700,000 | 2,300,000 |
| Timesteps totales | 3,000,000 | 3,000,000 |
| Final: cómo terminan | exito 100 | exito 100 |
| Final: centro, mediana / < 5 cm | 3.7 cm / 65% | 3.2 cm / 72% |
| Final: llega a tocar a (mediana, m/s) | 0.49 | 0.48 |
| Final: Δacción / Δv pedida (p95) | 0.039 / 0.063 (0.145) m/s | 0.035 / 0.060 (0.153) m/s |
| Final: inclinación RMS / jerk (m/s³) | 7.3° / 30 | 8.1° / 30 |

## Qué cambió
- Lo mismo que v118 y v119: gSDE en vez del ruido gaussiano independiente en cada paso, ahora con la seed 2. Misma
  recompensa (`suave_bajada_c003`), seed, duración e hiperparámetros que v107-teo. Laboratorio S004, 3 corridas en paralelo.

## Por qué
Tercera seed de gSDE: v119 había salido la más suave y centrada del proyecto, y faltaba ver si se repetía.

## Resultado
- 100 %. Centra algo mejor que v107 (3.2 contra 3.7 cm; 72 contra 65 % a menos de 5 cm), con la misma suavidad
  (Δv pedida 0.060 contra 0.063 m/s).
- Aprende antes: 94 % de éxito en entrenamiento a 1M (v107: 73 %).
- **gSDE con 3 seeds** (v118–v120, contra `c003` en v105–v107): 100 % en las 3. Δv pedida 0.061 / 0.046 / 0.060
  (media 0.056) contra 0.063 / 0.072 / 0.063 (0.066). Centro 4.2 / 3.3 / 3.2 cm contra 4.1 / 4.5 / 3.7. **Mejora la
  suavidad (~15 %) y el centrado, pero menos de lo que hacía pensar v119.** Aprende parecido (50 % a 0.7–0.9M).
- Sigue tocando a ~0.5 m/s (gSDE no cambia la acción, y `s` sigue saturado).

## Próximo paso
- gSDE no cambia ni la recompensa ni el entorno: se puede combinar con lo que se elija para tocar suave.
- Si se quiere ajustar: `--sde_sample_freq` 8 o 16 (ruido que cambia más lento).
