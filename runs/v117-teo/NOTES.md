# v117-teo

Cambio: `suave_bajada_c003` con efecto suelo contra el tope (`ground_effect: true`), 3M, seed 2

| | v107-teo | v117-teo |
|---|---|---|
| Éxito final (100 ep.) | 100% (96–100) | 98% (93–99) |
| Éxito best (100 ep.) | 100% (96–100) | 100% (96–100) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 21.51 | 21.25 |
| Largo ep. (best) | 50.2 | 54.0 |
| Best en timestep | 2,700,000 | 2,200,000 |
| Timesteps totales | 3,000,000 | 3,000,000 |
| Final: cómo terminan | exito 100 | exito 98, tiempo 2 |
| Final: centro, mediana / < 5 cm | 3.7 cm / 65% | 4.2 cm / 57% |
| Final: llega a tocar a (mediana, m/s) | 0.49 (p90 0.58) | 0.40 (p90 0.49) |
| Final: Δacción / Δv pedida (p95) | 0.039 / 0.063 (0.145) m/s | 0.084 / 0.091 (0.217) m/s |
| Final: inclinación RMS / jerk (m/s³) | 7.3° / 30 | 7.0° / 29 |

## Qué cambió
- Física: `ground_effect: true` (variante `suave_bajada_c003_gnd`; ver v115-teo para el modelo). Misma recompensa,
  seed (2), exploración y duración que v107. Laboratorio S004, 3 corridas en paralelo.

## Por qué
El efecto suelo es lo más importante que falta modelar para el robot real (`docs/estado-del-arte-2026-10-30.md`,
sección 3). Tercera seed de la variante.

## Resultado
- **98 %**: 2 episodios se quedan sin tiempo; el best da 100 %. **Aprende tarde:** 0 % hasta 1.1M y 50 % a 1.3M
  (v107, sin efecto suelo: 100 % a 1.3M).
- Toca a 0.40 m/s (el colchón de aire frena). Menos suave que v107 (Δv pedida 0.091 contra 0.063 m/s).
- **Con las 3 seeds (v115–v117): 100 / 99 / 98 %.** Aprende igual que sin efecto suelo, pero 2 de 3 seeds tardan más.
  La prueba cruzada (v115-teo) muestra que las políticas sin efecto suelo también aterrizan con él, así que para el
  modelo de la librería no hace falta entrenar con efecto suelo.

## Próximo paso
- Medir el efecto suelo real y aleatorizar `ground_effect_scale` (`TODO.md`, punto 7).
