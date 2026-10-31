# v116-teo

Cambio: `suave_bajada_c003` con efecto suelo contra el tope (`ground_effect: true`), 3M, seed 1

| | v106-teo | v116-teo |
|---|---|---|
| Éxito final (100 ep.) | 100% (96–100) | 99% (95–100) |
| Éxito best (100 ep.) | 100% (96–100) | 99% (95–100) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 21.39 | 21.63 |
| Largo ep. (best) | 46.9 | 52.1 |
| Best en timestep | 2,900,000 | 1,700,000 |
| Timesteps totales | 3,000,000 | 3,000,000 |
| Final: centro, mediana / < 5 cm | 4.5 cm / 54% | 4.3 cm / 57% |
| Final: llega a tocar a (mediana, m/s) | 0.50 (p90 0.57) | 0.38 (p90 0.50) |
| Final: Δacción / Δv pedida (p95) | 0.050 / 0.072 (0.173) m/s | 0.057 / 0.079 (0.197) m/s |
| Final: inclinación RMS / jerk (m/s³) | 7.4° / 31 | 7.0° / 28 |

## Qué cambió
- **Física, no recompensa:** `ground_effect: true` (variante `suave_bajada_c003_gnd`) usa `Physics.PYB_GND` con
  `_groundEffect` de `env.py`: el modelo de gym-pybullet-drones (Shi et al. 2019) con la altura de cada hélice medida
  contra el tope si está encima de la plataforma y contra el piso si no. En hover empuja +4 % del peso a 10 cm, +15 % a
  5 cm y +27 % desde 3.8 cm; en el borde solo empujan las hélices de adentro (efecto suelo parcial). Antes el entorno
  usaba `Physics.PYB`, sin efecto suelo.
- La recompensa es la misma que v106-teo (`suave_bajada_c003`), con la misma seed (1), exploración y duración.
  Laboratorio S004, 3 corridas en paralelo. Es ~15 % más lenta de entrenar (~37 min contra ~32).

## Por qué
El efecto suelo es lo más importante que falta modelar para el robot real (pedido de Teo, 2026-10-30). Primero, ver si
la política aprende igual con él. Detalle y fuentes en `docs/estado-del-arte-2026-10-30.md`, sección 3.

## Resultado
- **99 %** (1 choque contra la plataforma). Aprende al mismo ritmo que v106 (100 % desde 1.3M).
- **Toca más despacio sin que la política frene:** 0.38–0.41 m/s contra ~0.50. Es el colchón de aire, no el control
  (la política de v101, entrenada sin efecto suelo, también toca a 0.40 en este entorno).
- Centrado y suavidad parecidos a `c003` sin efecto suelo. Jerk un poco menor (28 contra 31 m/s³).
- **La magnitud del modelo es dudosa:** a 4.6 cm da ~18 %, y lo medido en un Crazyflie 2.0 es ~5 %. Esto muestra
  que la política se adapta a un efecto suelo fuerte, no que el real sea así.

- **Prueba cruzada** (50 episodios, seeds 1000–1049, sin guardar en archivo): v105, v106 (sin efecto suelo) y v115,
  v116 (con efecto suelo) aterrizan **50/50 sin choques** con el efecto suelo multiplicado por 0, 0.3, 1 y 1.5. Solo
  cambia la velocidad de toque (0.49–0.50 m/s sin efecto, 0.41–0.42 con ×1, 0.32–0.37 con ×1.5). Con este modelo, el
  efecto suelo amortigua el toque y no hace falta entrenar con él para aterrizar.

## Próximo paso
- Medir el efecto suelo en el laboratorio y ajustar `ground_effect_scale`; mientras tanto, aleatorizarlo por episodio
  (`TODO.md`, punto 7).
- Lo que el modelo no tiene: efecto no estacionario, rebote del aire en una plataforma chica y el controlador del
  Crazyflie a ~500 Hz. Eso solo se ve en el laboratorio.
