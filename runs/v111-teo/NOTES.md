# v111-teo

Cambio: premio extra por tocar despacio (`suave_bajada_c003_tocar`), 3M pasos, seed 42

| | v105-teo | v111-teo |
|---|---|---|
| Éxito final (100 ep.) | 100% (96–100) | 100% (96–100) |
| Éxito best (100 ep.) | 100% (96–100) | 100% (96–100) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 20.61 | 23.19 |
| Largo ep. (best) | 58.0 | 59.8 |
| Best en timestep | 3,000,000 | 2,400,000 |
| Timesteps totales | 3,000,000 | 3,000,000 |
| Final: centro, mediana / < 5 cm | 4.1 cm / 60% | 5.3 cm / 48% |
| Final: llega a tocar a (mediana, m/s) | 0.51 (p90 0.58) | 0.43 (p90 0.56) |
| Final: Δacción / Δv pedida (p95) | 0.034 / 0.063 (0.154) m/s | 0.061 / 0.076 (0.202) m/s |
| Final: inclinación RMS / jerk (m/s³) | 6.9° / 31 | 7.0° / 30 |

## Qué cambió
- Recompensa `suave_bajada_c003` → `suave_bajada_c003_tocar`: lo mismo más `landing_vz_coef: 10`, un premio extra al
  aterrizar de `10·(1 − v_toque/0.6)`, donde `v_toque` es la velocidad de bajada relativa al tope en el paso anterior
  al primer contacto (la misma que `touchdown.vz` de `tools/evaluate.py`). Tocando a 0.5 m/s suma +1.7; a 0.1 m/s,
  +8.3. Parámetro nuevo de `env.py`, apagado por defecto (en el `diff.patch`, sin commitear todavía).
- Misma seed (42), exploración (`--log_std_init -0.5`), duración (3M) e hiperparámetros que v105-teo. Laboratorio
  S004, 3 corridas en paralelo. El `diff.patch` también trae `ground_effect` y las opciones de gSDE de `train.py`,
  apagados (no cambian esta corrida).
- Los "Best reward" no se comparan directamente: esta recompensa suma el premio extra.

## Por qué
Ninguna política frena al tocar: todas llegan a 0.41–0.51 m/s. Castigar por paso la bajada rápida cerca del
tope (`suave_bajada_flare`, v83, v86) las dejó flotando. Un premio que se paga una sola vez, al aterrizar, no encarece
acercarse, así que no debería causar la trampa de flotar (`docs/estado-del-arte-2026-10-30.md`, sección 1).

## Resultado
- 100 %. Toca a 0.43 m/s de mediana, contra 0.51 de v105: **frena un poco** (−15 %), pero el 10 % más rápido sigue
  llegando a 0.56 m/s. Algo menos suave (Δv pedida 0.076 contra 0.063) y menos centrada (5.3 contra 4.1 cm).
- Con las 3 seeds (v111–v113): 100 % de éxito y toque a **0.45 m/s de mediana, contra 0.50 de `c003`**. No cayó en
  la trampa de flotar, pero el premio casi no frena.
- **Por qué no frena (hipótesis con datos):** `s` está saturado en 1 en el 100 % de los pasos, con la media de la
  gaussiana en ~3 (`tools/action_saturation.py`: v105 3.35, v111 3.03). Con la acción `v = 0.6·s·dir/|dir|`, el dron
  va **siempre a 0.6 m/s**: para bajar más lento tiene que inclinar la dirección hacia los costados, no puede frenar.
  Y con media 3 y desvío ~0.6, la exploración casi nunca prueba `s < 1`, así que el premio no tiene cómo enseñarlo.

## Próximo paso
- Acción como velocidad (`action_mode: velocity`, `v = 0.6·(dx, dy, dz)`): `suave_bajada_c003_vel` y
  `suave_bajada_c003_vel_tocar`, en la cola de esta noche.
