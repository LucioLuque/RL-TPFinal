# v59-lucio

Cambio: `suave_c002` con `--log_std_init -0.5` (desvío inicial 0.61), seed 2

| | v36-lucio | v59-lucio |
|---|---|---|
| Éxito final (100 ep.) | 75% (66–82) | 100% (96–100) |
| Éxito best (100 ep.) | 74% (65–82) | 99% (95–100) |
| Best éxito (8 ep.) | 100% | 100% |
| Best reward | 17.62 | 20.61 |
| Largo ep. (best) | 58.1 | 49.2 |
| Best en timestep | 1,400,000 | 1,500,000 |
| Timesteps totales | 1,503,232 | 1,503,232 |
| Final: cómo terminan | exito 75, choque_plataforma 21, choque_piso 2, tiempo 2 | exito 100 |
| Final: centro, mediana / < 5 cm | 10.5 cm / 12% | 5.3 cm / 45% |
| Final: llega a tocar a (mediana) | 0.43 m/s | 0.48 m/s |
| Final: Δacción / Δv pedida (p95) | 0.10 / 0.076 (0.233) m/s | 0.17 / 0.126 (0.337) m/s |
| Final: inclinación RMS / jerk | 8.0° / 29 m/s³ | 7.4° / 35 m/s³ |

## Qué cambió
- Exploración: `log_std_init` 0 → −0.5 (desvío 1 → 0.61). Misma recompensa (`suave_c002`: `base` + castigo 0.02 a la
  acción), seed (2) e hiperparámetros que v36, que es la comparación.
- Tercera seed de `suave_c002` + desvío 0.61 (v57: s42, v58: s1). Número reservado desde el 2026-10-15.

## Por qué
La conclusión "el castigo a la acción y el menor ruido de exploración se suman" se apoyaba en 2 seeds (93 y 85 %).

## Resultado
- **100 % en el modelo final** (v36, con desvío 1: 75 %), sin choques. 5.3 cm del centro (45 % a menos de 5 cm).
- Menos suave que las otras dos seeds: Δv pedida 0.126 m/s (v57: 0.088; v58: 0.079).
- **Las 3 seeds de `suave_c002` + desvío 0.61: 93 / 85 / 100 % → 92.7 %**, contra 74 % de `suave_c002` con desvío 1 (4
  seeds). Confirma que las dos cosas se suman.
- **Igual que `suave_bajada` + desvío 0.61 con las mismas seeds** (92 / 97 / 89 → 92.7 %): mismos choques contra el
  borde (16 contra 18 en 300 episodios), misma suavidad (Δv pedida 0.097 contra 0.083 m/s) y mismo centrado (6.1 contra
  6.3 cm). Con menos ruido de exploración, el castigo por bajar estando afuera (`reward_descent_coef`) no suma.

## Próximo paso
- Tenerlo en cuenta al elegir la recompensa final (TODO.md, punto 1): el término de bajada quizás sobra con desvío 0.61.
