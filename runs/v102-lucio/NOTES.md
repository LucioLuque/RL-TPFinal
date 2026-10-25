# v102-lucio

Cambio: castigo a la acción 0.03 (`suave_bajada_c003`) con desvío inicial 0.61, seed 2

| | v67-lucio | v102-lucio |
|---|---|---|
| Éxito final (100 ep.) | 89% (81–94) | 99% (95–100) |
| Éxito best (100 ep.) | 87% (79–92) | 98% (93–99) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 19.10 | 19.42 |
| Largo ep. (best) | 57.1 | 57.6 |
| Best en timestep | 1,400,000 | 1,400,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | exito 89, choque_plataforma 9, tiempo 2 | exito 99, choque_plataforma 1 |
| Final: centro, mediana / < 5 cm | 6.5 cm / 38% | 7.2 cm / 35% |
| Final: llega a tocar a (mediana) | 0.51 m/s | 0.47 m/s |
| Final: Δacción / Δv pedida (p95) | 0.10 / 0.090 (0.238) m/s | 0.08 / 0.086 (0.216) m/s |
| Final: inclinación RMS / jerk | 7.7° / 32 m/s³ | 7.5° / 33 m/s³ |

## Qué cambió
- Lo mismo que v99 y v101, con la seed 2. Se compara con v67 (`suave_bajada` + desvío 0.61, seed 2).

## Por qué
Tercera seed de `suave_bajada_c003`.

## Resultado
- **99 % en el modelo final** (v67: 89 %), 1 choque contra el borde (v67: 9). Aprende desde 0.6M.
- Igual de suave que v67 (Δv pedida 0.086 contra 0.090 m/s) y centrada parecido (7.2 contra 6.5 cm).
- **Las 3 seeds de `c003` + desvío 0.61: 99 / 95 / 99 % → 97.7 % de media**, contra 97 / 92 / 89 % → 92.7 % de
  `suave_bajada` + desvío 0.61 (castigo 0.02) con las mismas seeds. Choques contra el borde: 4 en 300 episodios contra
  18. Suavidad igual (Δv pedida 0.081 contra 0.083 m/s). Todas aprenden a tiempo (a diferencia de 0.05).

## Próximo paso
- Candidata a recompensa por defecto junto con `--log_std_init -0.5` (lo decide Lucio). Entrenarla a 3M para el
  centrado (v69: entrenar más centra).
