# v122-teo

Cambio: CAPS (suavidad en la pérdida: temporal 0.01, espacial 0.01) con `c003`, 3M, seed 1

| | v106-teo | v122-teo |
|---|---|---|
| Éxito final (100 ep.) | 100% (96–100) | 100% (96–100) |
| Éxito best (100 ep.) | 100% (96–100) | 100% (96–100) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 21.39 | 21.76 |
| Largo ep. (best) | 46.9 | 52.4 |
| Best en timestep | 2,900,000 | 2,900,000 |
| Timesteps totales | 3,000,000 | 3,000,000 |
| Final: cómo terminan | exito 100 | exito 100 |
| Final: centro, mediana / < 5 cm | 4.5 cm / 54% | 3.2 cm / 80% |
| Final: llega a tocar a (mediana, m/s) | 0.50 | 0.50 |
| Final: Δacción / Δv pedida (p95) | 0.050 / 0.072 (0.173) m/s | 0.039 / 0.060 (0.141) m/s |
| Final: inclinación RMS / jerk (m/s³) | 7.4° / 31 | 7.2° / 29 |

## Qué cambió
- Lo mismo que v121-teo (CAPS en la pérdida de PPO, `caps.py`), con la seed 1. Misma recompensa, seed, exploración y
  duración que v106-teo. Laboratorio S004, 3 corridas en paralelo.
- `caps.py` no está en `diff.patch` (todavía no está en git); ver v121-teo.

## Por qué
Segunda seed de CAPS (ver v121-teo).

## Resultado
- 100 %. Centra mejor que v106 (3.2 contra 4.5 cm; 80 contra 54 % a menos de 5 cm) y es algo más suave (Δv pedida
  0.060 contra 0.072 m/s).
- Aprende parecido (50 % a 0.71M; v106: 0.79M).

## Próximo paso
- Ver v123, que junta las 3 seeds.
