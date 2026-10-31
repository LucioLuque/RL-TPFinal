# v123-teo

Cambio: CAPS (suavidad en la pérdida: temporal 0.01, espacial 0.01) con `c003`, 3M, seed 2

| | v107-teo | v123-teo |
|---|---|---|
| Éxito final (100 ep.) | 100% (96–100) | 100% (96–100) |
| Éxito best (100 ep.) | 100% (96–100) | 100% (96–100) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 21.51 | 21.93 |
| Largo ep. (best) | 50.2 | 48.9 |
| Best en timestep | 2,700,000 | 2,400,000 |
| Timesteps totales | 3,000,000 | 3,000,000 |
| Final: cómo terminan | exito 100 | exito 100 |
| Final: centro, mediana / < 5 cm | 3.7 cm / 65% | 3.8 cm / 68% |
| Final: llega a tocar a (mediana, m/s) | 0.49 | 0.51 |
| Final: Δacción / Δv pedida (p95) | 0.039 / 0.063 (0.145) m/s | 0.027 / 0.052 (0.130) m/s |
| Final: inclinación RMS / jerk (m/s³) | 7.3° / 30 | 7.3° / 28 |

## Qué cambió
- Lo mismo que v121-teo (CAPS en la pérdida de PPO, `caps.py`), con la seed 2. Misma recompensa, seed, exploración y
  duración que v107-teo. Laboratorio S004, 3 corridas en paralelo.
- `caps.py` no está en `diff.patch` (todavía no está en git); ver v121-teo.

## Por qué
Tercera seed de CAPS (ver v121-teo).

## Resultado
- 100 %. Centra igual que v107 (3.8 contra 3.7 cm) y es algo más suave (Δv pedida 0.052 contra 0.063 m/s).
- **CAPS con 3 seeds** (v121–v123, contra `c003` en v105–v107): 100 % en las 3. Centro 2.7 / 3.2 / 3.8 cm (84 / 80 /
  68 % a menos de 5 cm) contra 4.1 / 4.5 / 3.7 (60 / 54 / 65 %). Δv pedida 0.063 / 0.060 / 0.052 (media 0.058) contra
  0.066. Aprende igual (50 % a 0.7–0.8M). **Centra mejor, pero suaviza poco (~12 %), parecido a gSDE.** No era lo
  que se esperaba de la literatura.
- Hipótesis, no probada: CAPS actúa sobre la media de la gaussiana sin recortar, y esas medias están muy afuera de
  [−1, 1] (`s` ~3, `dz` ~1.1–1.5, `tools/action_saturation.py`). Gran parte del término castiga cambios de la media
  que no cambian la acción ejecutada. Eso explicaría también que el término espacial crezca durante el entrenamiento
  (0.08 → 0.2).
- Sigue tocando a ~0.5 m/s.

## Próximo paso
- Aplicar CAPS a la media recortada a [−1, 1] (o pasada por `tanh`), o subir los pesos (0.05–0.1).
- Un castigo a que la media se salga de [−1, 1] (*bounds loss*, como `bounds_loss_coef` de rl_games) atacaría la
  causa del bang-bang directamente.
