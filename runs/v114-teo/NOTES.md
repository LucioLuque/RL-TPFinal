# v114-teo

Cambio: `suave_bajada_c005` + desvío 0.61 a 3M, seed 4 (quinta seed, por la falla de v109)

| | v108-teo | v114-teo |
|---|---|---|
| Éxito final (100 ep.) | 100% (96–100) | 100% (96–100) |
| Éxito best (100 ep.) | 100% (96–100) | 100% (96–100) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 22.38 | 21.04 |
| Largo ep. (best) | 51.5 | 52.1 |
| Best en timestep | 2,900,000 | 2,400,000 |
| Timesteps totales | 3,000,000 | 3,000,000 |
| Final: centro, mediana / < 5 cm | 3.3 cm / 80% | 3.3 cm / 77% |
| Final: llega a tocar a (mediana) | 0.52 m/s | 0.51 m/s |
| Final: Δacción / Δv pedida (p95) | 0.020 / 0.043 (0.104) m/s | 0.052 / 0.066 (0.157) m/s |
| Final: inclinación RMS / jerk | 7.5° / 28 m/s³ | 7.1° / 31 m/s³ |

## Qué cambió
- Solo la seed: 42 → 4. Misma recompensa (`suave_bajada_c005`), exploración (`--log_std_init -0.5`), duración (3M) e
  hiperparámetros. Laboratorio S004, 3 corridas en paralelo. El `diff.patch` trae opciones nuevas de `env.py` y
  `train.py` (efecto suelo, premio por tocar, gSDE, CAPS), todas apagadas en esta corrida.

## Por qué
Con 3 seeds a 3M, `c005` dio 100 / 0 / 97 % (v108, v109, v110): falló una sola, quedándose quieta con `s = 0`.
Criterio acordado con Teo: si fallan todas menos una, se prueba otra seed; si fallan varias, no se confía en la
variante aunque la siguiente ande.

## Resultado
- **100 %**, 3.3 cm del centro y 77 % a menos de 5 cm. Aprende a ~1.1M (evals de 8 episodios: 100 % desde 1.5M).
- Δv pedida 0.066 m/s, menos suave que v108 (0.043) y parecida a v100 y v110 (0.059–0.072).
- **`c005` a 3M con 5 seeds: 4 aprenden (97–100 %) y 1 queda flotando (v109).** `c003` a 3M: 3 de 3 al 100 %. Entre
  las que aprenden, `c005` es apenas más suave (Δv pedida 0.060 contra 0.066 m/s) y más centrada (3.7 contra 4.1 cm,
  71 contra 60 % a menos de 5 cm). Las dos tocan a ~0.5 m/s.

## Próximo paso
- Decidir la recompensa final (`TODO.md`, punto 1): `c003` es la segura; `c005` gana poco y tiene una trampa.
